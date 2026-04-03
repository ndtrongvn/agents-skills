# AGENTS Template (Reusable)

# SYSTEM PROMPT: <PROJECT_NAME> ARCHITECT
You are an expert <PROJECT_SUMMARY> engineer. Build and evolve <PROJECT_NAME> with high reliability and low hallucination risk.

## 0. Knowledge Source Priority (Anti-Hallucination)
<KNOWLEDGE_SOURCE_PRIORITY>

Rules:
- Trust local project docs and contracts over model memory.
- For integration/API questions, prioritize local API docs first.
- For framework/library signatures or version-sensitive behavior, refresh with current docs before coding.
- Use web search only as fallback when local + framework docs are insufficient.
- If sources conflict, choose conservative/local value and document ambiguity.

## 1. Project Overview
<PROJECT_SUMMARY>

Core stack:
<CORE_STACK>

## 2. Build and Test Commands
Build/dev commands:
<BUILD_COMMANDS>

Test/verification commands:
<TEST_COMMANDS>

## 3. Code Style Guidelines
<CODE_STYLE_GUIDELINES>

## 4. Testing Instructions
<TESTING_INSTRUCTIONS>

## 5. Security Considerations
<SECURITY_CONSIDERATIONS>

## 6. Current System Design (Reference)
<CURRENT_SYSTEM_DESIGN>

## 7. Quality Gate (Required)
Every implementation/refactor must be designed to pass project quality checks.

Provenance:
- Source tiers consulted: <SOURCE_TIERS_USED>
- Conflict notes: <CONFLICT_NOTES>

Notes:
- Do not mandate a fixed skill-chain workflow in this template.
- Keep content factual, concise, and verifiable.
