---
name: sdd-implement
description: Implement one or more requirements (REQ-NNN) from scope.md using RAG retrieval. Use whenever the user asks to build, implement, fix or extend a feature in this project.
---

# Implement requirements from scope.md (RAG + spec-driven)

Run commands from the project root. `RAG` below means
`python .agents/skills/sdd-implement/scripts/rag.py`.

## 1. Find the requirement
- If the user named REQ IDs, use them.
- Otherwise run `RAG list` and pick the approved REQ(s) that match the request.
  If none match, stop: tell the user to add the requirement with /sdd-change.

## 2. Retrieve (never skip)
Run `RAG ask "Implement REQ-NNN <short title>"`, then read `.rag/prompt_out.md`.
It contains: Overview, Out of scope, Glossary, all approved decisions, the requirement,
and the existing code and tests linked to it. Use only this as project knowledge.
If you need a file the retriever didn't return, open it and name it in "Context used".

## 3. Implementation Plan (wait for approval)
Write the Implementation Plan in the format given in `.rag/prompt_out.md`:
Context used, Changes, Coverage table (acceptance bullet → function → test), Open questions.
If there are open questions, stop here and ask.

## 4. Task list
One task per acceptance bullet, then "Run tests" and "Run check".

## 5. Build
Follow the rules in `.rag/prompt_out.md`: edit in place, tag `# Implements:` and
`# Tests:`, one test per acceptance bullet, follow every approved DEC-*.

## 6. Verify
```
python -m pytest -q
python .agents/skills/sdd-implement/scripts/rag.py check
```
Fix anything that fails. `check` must show 0 problems for these REQs.

## 7. Walkthrough
Changed files, pytest output, `check` output and the final coverage table.
