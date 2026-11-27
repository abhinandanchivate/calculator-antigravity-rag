---
trigger: always_on
description: Spec-driven development with RAG. scope.md is the source of truth; retrieve context with rag.py before planning any code change.
---

# Spec-driven development with RAG

This project is built only from `scope.md`. `prompt.md` is the prompt template.

## Before you plan ANY code change
1. Run the retriever. Never plan from memory:
   `python .agents/skills/sdd-implement/scripts/rag.py ask "<task in one line>"`
2. Read `.rag/prompt_out.md` and follow it. It contains the rules, the retrieved context
   and the required output format.
3. Start the Implementation Plan with "Context used:" and the REQ/DEC IDs and files retrieved.

## Always
- Only REQ/DEC items with `status: approved` may be built. Draft, superseded and
  "Out of scope" items are never built.
- Tag code `# Implements: REQ-NNN` and tests `# Tests: REQ-NNN`.
- Don't guess. If scope.md doesn't answer something, ask in "Open questions" and wait.
- Never edit an approved requirement. Use the /sdd-change skill to replace it.

## Before you finish
Run `python -m pytest -q` and `python .agents/skills/sdd-implement/scripts/rag.py check`.
Put both results in the Walkthrough. The task is not done until check shows 0 problems
for the requirements you worked on.
