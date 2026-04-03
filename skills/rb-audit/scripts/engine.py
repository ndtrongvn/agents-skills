#!/usr/bin/env python3
"""rb-audit analysis engine.

Builds a compact anti-hallucination project capsule, writes it to
.agents/docs/rb-audit-latest.json, and prints the same JSON to stdout.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List

VERSION = "1.2.0"
TOP_FINDINGS_LIMIT = 12
TARGET_DEPS = ("next", "@solana/kit", "@supabase/supabase-js")
CAPSULE_TTL_HOURS = 6
CAPSULE_PATH = Path(".agents/docs/rb-audit-latest.json")

SEV_WEIGHT = {"C": 0, "H": 1, "M": 2, "L": 3}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def to_rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def line_no(text: str, needle: str) -> int:
    idx = text.find(needle)
    if idx < 0:
        return 1
    return text.count("\n", 0, idx) + 1


def iso_utc(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def gather_files(root: Path) -> Dict[str, List[Path]]:
    groups: Dict[str, List[Path]] = {}
    for folder in ("app", "components", "lib", "supabase", "tests"):
        base = root / folder
        if not base.exists():
            groups[folder] = []
            continue
        groups[folder] = sorted([p for p in base.rglob("*") if p.is_file()])
    return groups


def parse_dep_tree(node: object, acc: Dict[str, str]) -> None:
    if isinstance(node, dict):
        name = node.get("name")
        version = node.get("version")
        if isinstance(name, str) and isinstance(version, str) and name in TARGET_DEPS:
            acc[name] = version
        deps = node.get("dependencies")
        if isinstance(deps, dict):
            for dep_name, dep_node in deps.items():
                if dep_name in TARGET_DEPS and isinstance(dep_node, dict):
                    dep_ver = dep_node.get("version")
                    if isinstance(dep_ver, str):
                        acc[dep_name] = dep_ver
                parse_dep_tree(dep_node, acc)
        elif isinstance(deps, list):
            for dep_node in deps:
                parse_dep_tree(dep_node, acc)
    elif isinstance(node, list):
        for item in node:
            parse_dep_tree(item, acc)


def get_dependencies(root: Path) -> Dict[str, str]:
    versions: Dict[str, str] = {}
    try:
        run = subprocess.run(
            ["pnpm", "list", "--json", "--depth", "3"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=False,
        )
        if run.returncode == 0 and run.stdout.strip():
            payload = json.loads(run.stdout)
            parse_dep_tree(payload, versions)
    except Exception:
        pass

    if len(versions) < len(TARGET_DEPS):
        package_json = root / "package.json"
        if package_json.exists():
            pkg = json.loads(read_text(package_json))
            merged = {}
            merged.update(pkg.get("dependencies", {}))
            merged.update(pkg.get("devDependencies", {}))
            for dep in TARGET_DEPS:
                if dep not in versions and dep in merged:
                    versions[dep] = str(merged[dep])

    for dep in TARGET_DEPS:
        versions.setdefault(dep, "unknown")

    return {k: versions[k] for k in TARGET_DEPS}


def collect_contracts(root: Path, app_files: List[Path]) -> Dict[str, object]:
    route_entries: List[Dict[str, object]] = []
    for path in app_files:
        if path.name != "route.ts":
            continue
        rel = to_rel(path, root)
        text = read_text(path)
        methods = sorted(set(re.findall(r"export\s+async\s+function\s+(GET|POST|PUT|PATCH|DELETE)", text)))
        route_entries.append({"r": rel, "m": methods})

    contract_file = root / "lib" / "contracts" / "client-api.ts"
    contract_summary = {}
    if contract_file.exists():
        text = read_text(contract_file)
        schema_exports = len(re.findall(r"export\s+const\s+\w+Schema\s*=\s*z\.object", text))
        type_exports = len(re.findall(r"export\s+type\s+", text))
        contract_summary = {
            "file": to_rel(contract_file, root),
            "schema_exports": schema_exports,
            "type_exports": type_exports,
        }

    return {
        "api_routes": route_entries,
        "client_contracts": contract_summary,
    }


def finding(fid: str, sev: str, cat: str, loc: str, rule: str, fix: str) -> Dict[str, str]:
    return {"id": fid, "sev": sev, "cat": cat, "loc": loc, "rule": rule, "fix": fix}


def has_route_or_action_sibling(page_path: Path) -> bool:
    folder = page_path.parent
    for name in ("route.ts", "actions.ts", "action.ts"):
        if (folder / name).exists():
            return True
    return False


def run_audits(root: Path, files: Dict[str, List[Path]]) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []

    app_files = files["app"]
    component_files = files["components"]
    lib_files = files["lib"]
    supabase_files = files["supabase"]
    test_files = files["tests"]

    ts_like = [
        p
        for p in (app_files + component_files + lib_files)
        if p.suffix in {".ts", ".tsx", ".js", ".mjs"}
    ]

    client_files: List[Path] = []
    for path in ts_like:
        text = read_text(path)
        header = "\n".join(text.splitlines()[:5])
        if '"use client"' in header or "'use client'" in header:
            client_files.append(path)

    for path in client_files:
        text = read_text(path)
        if "lib/supabase/admin" in text or "SUPABASE_SERVICE_ROLE_KEY" in text:
            rel = to_rel(path, root)
            findings.append(
                finding(
                    "next-client-admin",
                    "H",
                    "boundary",
                    f"{rel}:{line_no(text, 'lib/supabase/admin')}",
                    "client_imports_admin_surface",
                    "move_admin_calls_to_server_route",
                )
            )

    for page in [p for p in app_files if p.name == "page.tsx"]:
        text = read_text(page)
        if "<form" in text or "submit" in text.lower() or "onSubmit" in text:
            if not has_route_or_action_sibling(page):
                rel = to_rel(page, root)
                findings.append(
                    finding(
                        "missing-link",
                        "L",
                        "contract",
                        f"{rel}:{line_no(text, '<form')}",
                        "interactive_page_without_local_route_or_action",
                        "add_route_or_server_action_mapping",
                    )
                )

    private_literal_re = re.compile(r"['\"]([1-9A-HJ-NP-Za-km-z]{64,120})['\"]")
    context_re = re.compile(r"private|secret|mint_private_key|keypair", re.IGNORECASE)
    for path in ts_like + supabase_files:
        text = read_text(path)
        if context_re.search(text):
            for match in private_literal_re.finditer(text):
                rel = to_rel(path, root)
                findings.append(
                    finding(
                        "secret-literal",
                        "H",
                        "security",
                        f"{rel}:{line_no(text, match.group(0))}",
                        "possible_private_key_literal",
                        "remove_literal_use_env_or_vault",
                    )
                )
                break

    for path in ts_like:
        text = read_text(path)
        if "http://" in text and ("RPC" in text or "rpc" in text or "SOLANA" in text):
            rel = to_rel(path, root)
            findings.append(
                finding(
                    "rpc-insecure-http",
                    "M",
                    "web3",
                    f"{rel}:{line_no(text, 'http://')}",
                    "non_tls_rpc_endpoint",
                    "enforce_https_rpc",
                )
            )

    solana_path = root / "lib" / "solana.ts"
    if solana_path.exists():
        solana_text = read_text(solana_path)
        if "simulateTransaction" not in solana_text:
            findings.append(
                finding(
                    "solana-no-sim",
                    "M",
                    "web3",
                    f"lib/solana.ts:{line_no(solana_text, 'sendTransaction')}",
                    "broadcast_without_explicit_simulation_guard",
                    "add_simulation_or_guardrail",
                )
            )

    pre_mint_sql = root / "supabase" / "migrations" / "0003_pre_mint_pool.sql"
    if pre_mint_sql.exists():
        sql = read_text(pre_mint_sql)
        if "mint_private_key text not null" in sql and "for select" in sql and "to authenticated" in sql and "using (true)" in sql:
            findings.append(
                finding(
                    "pre-mint-key-exposure",
                    "C",
                    "security",
                    f"supabase/migrations/0003_pre_mint_pool.sql:{line_no(sql, 'mint_private_key text not null')}",
                    "sensitive_key_column_readable_by_authenticated",
                    "remove_select_policy_mask_or_server_only_access",
                )
            )

    ingest_sql = root / "supabase" / "migrations" / "0005_search_ingest_and_cron.sql"
    if ingest_sql.exists():
        sql = read_text(ingest_sql)
        if "search_ingest_settings_update_authenticated" in sql and "using (true)" in sql and "with check (true)" in sql:
            findings.append(
                finding(
                    "ingest-global-update",
                    "H",
                    "authz",
                    f"supabase/migrations/0005_search_ingest_and_cron.sql:{line_no(sql, 'search_ingest_settings_update_authenticated')}",
                    "global_settings_writable_by_any_authenticated",
                    "scope_updates_to_owner_or_admin",
                )
            )

    for path in [root / "lib" / "search-ingest-settings.ts", root / "lib" / "pre-mint-pool.ts"]:
        if not path.exists():
            continue
        text = read_text(path)
        if "createAdminSupabase(" in text:
            findings.append(
                finding(
                    "service-role-surface",
                    "M",
                    "authz",
                    f"{to_rel(path, root)}:{line_no(text, 'createAdminSupabase(')}",
                    "service_role_used_in_user_driven_flow",
                    "review_least_privilege_and_rls_path",
                )
            )

    external_dir = root / "lib" / "external"
    if external_dir.exists():
        for path in external_dir.glob("*.ts"):
            text = read_text(path)
            if re.search(r"response\.json\(\)\)\s+as\s+\{", text):
                findings.append(
                    finding(
                        "api-unsafe-cast",
                        "M",
                        "contract",
                        f"{to_rel(path, root)}:{line_no(text, 'response.json()')}",
                        "external_payload_cast_without_runtime_validation",
                        "add_zod_schema_parse",
                    )
                )

    job_store = root / "lib" / "job-store.ts"
    if job_store.exists():
        text = read_text(job_store)
        if "globalThis" in text and "Map<string, LaunchJob>" in text and "JOB_TTL_MS" in text:
            findings.append(
                finding(
                    "job-memory-ttl",
                    "H",
                    "reliability",
                    f"lib/job-store.ts:{line_no(text, 'JOB_TTL_MS')}",
                    "in_memory_job_store_with_ttl",
                    "persist_jobs_or_add_durable_queue",
                )
            )

    status_route = root / "app" / "api" / "launch" / "status" / "route.ts"
    if status_route.exists():
        text = read_text(status_route)
        needle = "Job not found or expired."
        if needle in text:
            findings.append(
                finding(
                    "job-expired-ux",
                    "M",
                    "reliability",
                    f"app/api/launch/status/route.ts:{line_no(text, needle)}",
                    "status_fallback_returns_expired_error",
                    "provide_terminal_snapshot_or_store_result",
                )
            )

    orch = root / "lib" / "launch" / "orchestrator.ts"
    if orch.exists():
        text = read_text(orch)
        if "imageDataUrl:" in text and "toString(\"base64\")" in text:
            findings.append(
                finding(
                    "sse-large-payload",
                    "M",
                    "reliability",
                    f"lib/launch/orchestrator.ts:{line_no(text, 'imageDataUrl:')}",
                    "base64_preview_sent_in_stream_snapshot",
                    "send_preview_url_or_truncated_payload",
                )
            )

    for relp in (
        "supabase/functions/search-ingest-runner/index.ts",
        "supabase/functions/cleanup-icons-runner/index.ts",
    ):
        path = root / relp
        if not path.exists():
            continue
        text_lower = read_text(path).lower()
        has_inbound_auth_check = (
            "request.headers.get(\"authorization\")" in text_lower
            or "request.headers.get('authorization')" in text_lower
            or "req.headers.get(\"authorization\")" in text_lower
            or "req.headers.get('authorization')" in text_lower
        )
        if not has_inbound_auth_check:
            findings.append(
                finding(
                    "edge-auth-verify",
                    "M",
                    "security",
                    f"{relp}:1",
                    "edge_runner_missing_caller_verification",
                    "verify_cron_caller_or_shared_secret",
                )
            )

    critical_targets = [
        "lib/launch/orchestrator.ts",
        "lib/metrics.ts",
        "lib/pre-mint-pool.ts",
        "app/api/launch/route.ts",
        "app/api/metrics/route.ts",
        "supabase/functions/search-ingest-runner/index.ts",
        "supabase/functions/cleanup-icons-runner/index.ts",
    ]
    test_blob = "\n".join(read_text(p) for p in test_files if p.suffix in {".ts", ".tsx", ".js"}).lower()
    for target in critical_targets:
        stem = Path(target).stem.lower().replace("-", "_")
        if stem not in test_blob and Path(target).name.lower() not in test_blob:
            findings.append(
                finding(
                    "coverage-gap",
                    "M",
                    "coverage",
                    f"{target}:1",
                    "critical_surface_without_direct_tests",
                    "add_targeted_unit_or_contract_tests",
                )
            )

    seen = set()
    deduped = []
    for f in findings:
        key = (f["id"], f["loc"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(f)

    return deduped


def score(findings: List[Dict[str, str]]) -> Dict[str, int]:
    arch = 10
    halluc = 10
    web3 = 10

    for f in findings:
        sev = f["sev"]
        cat = f["cat"]
        penalty = 0
        if sev == "C":
            penalty = 3
        elif sev == "H":
            penalty = 2
        elif sev == "M":
            penalty = 1

        if cat in {"authz", "boundary", "reliability"}:
            arch -= penalty
        if cat in {"contract", "coverage", "reliability"}:
            halluc -= penalty
        if cat in {"web3", "security"}:
            web3 -= penalty

    arch = max(1, arch)
    halluc = max(1, halluc)
    web3 = max(1, web3)
    overall = max(1, round((arch + halluc + web3) / 3))

    return {
        "architectural_alignment": arch,
        "hallucination_risk": halluc,
        "web3_safety": web3,
        "overall": overall,
    }


def risk_counts(findings: List[Dict[str, str]]) -> Dict[str, Dict[str, int]]:
    by_sev = Counter(f["sev"] for f in findings)
    by_cat = Counter(f["cat"] for f in findings)
    return {
        "sev": {k: by_sev.get(k, 0) for k in ("C", "H", "M", "L")},
        "cat": dict(sorted(by_cat.items())),
        "total": len(findings),
    }


def top_findings(findings: List[Dict[str, str]]) -> List[Dict[str, str]]:
    ordered = sorted(findings, key=lambda f: (SEV_WEIGHT[f["sev"]], f["cat"], f["rule"], f["loc"]))
    return ordered[:TOP_FINDINGS_LIMIT]


def build_action_queue(findings: List[Dict[str, str]]) -> Dict[str, List[str]]:
    p0: List[str] = []
    p1: List[str] = []
    seen0 = set()
    seen1 = set()

    for f in sorted(findings, key=lambda x: (SEV_WEIGHT[x["sev"]], x["cat"])):
        code = f["fix"]
        if f["sev"] in {"C", "H"}:
            if code not in seen0:
                seen0.add(code)
                p0.append(code)
        else:
            if code not in seen1:
                seen1.add(code)
                p1.append(code)

    return {"p0": p0[:8], "p1": p1[:8]}


def build_project_brief(root: Path, files: Dict[str, List[Path]], deps: Dict[str, str]) -> Dict[str, object]:
    ts_like = [
        p
        for p in (files["app"] + files["components"] + files["lib"])
        if p.suffix in {".ts", ".tsx", ".js", ".mjs"}
    ]
    client_count = 0
    for path in ts_like:
        text = read_text(path)
        head = "\n".join(text.splitlines()[:5])
        if '"use client"' in head or "'use client'" in head:
            client_count += 1

    route_count = sum(1 for p in files["app"] if p.name == "route.ts")
    page_count = sum(1 for p in files["app"] if p.name == "page.tsx")
    migrations_count = len([p for p in files["supabase"] if "migrations" in to_rel(p, root)])

    return {
        "stack": {
            "next": deps["next"],
            "solana_kit": deps["@solana/kit"],
            "supabase_js": deps["@supabase/supabase-js"],
        },
        "shape": {
            "app_router": (root / "app").exists(),
            "pages": page_count,
            "api_routes": route_count,
            "client_files": client_count,
            "migrations": migrations_count,
        },
        "truths": [
            "nextjs_app_router_project",
            "launch_flow_uses_in_memory_job_store",
            "supabase_service_role_used_on_server",
        ],
    }


def build_capsule(root: Path) -> Dict[str, object]:
    files = gather_files(root)
    deps = get_dependencies(root)
    findings = run_audits(root, files)
    top = top_findings(findings)

    generated = datetime.now(timezone.utc)
    expires = generated + timedelta(hours=CAPSULE_TTL_HOURS)

    return {
        "v": VERSION,
        "generated_at": iso_utc(generated),
        "expires_at": iso_utc(expires),
        "project_brief": build_project_brief(root, files, deps),
        "contracts_brief": collect_contracts(root, files["app"]),
        "risk_brief": {
            "counts": risk_counts(findings),
            "top": top,
        },
        "rb_score": score(findings),
        "action_queue": build_action_queue(top),
    }


def write_capsule(root: Path, payload: Dict[str, object]) -> None:
    out_path = root / CAPSULE_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, separators=(",", ":"), sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    root = Path(__file__).resolve().parents[4]
    payload = build_capsule(root)

    write_capsule(root, payload)
    sys.stdout.write(json.dumps(payload, separators=(",", ":"), sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
