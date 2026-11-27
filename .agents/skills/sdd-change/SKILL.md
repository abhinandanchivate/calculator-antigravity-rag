---
name: sdd-change
description: Add a new requirement or decision to scope.md, or change an existing one by superseding it. Use when the user wants new behavior, changed behavior, or a new technical decision.
---

# Add or change requirements in scope.md

Never write code in this skill. It only edits `scope.md`.

## Add a new requirement
1. Run `python .agents/skills/sdd-implement/scripts/rag.py list` to find the next free number.
   IDs are never reused.
2. Check the request against "Out of scope" and the existing approved REQs and DECs.
   If it conflicts with any of them, tell the user which ones and ask what to do.
3. Add a section in this exact format:
   ```
   ## REQ-NNN Short title
   status: draft
   One or two sentences: what the user can do.
   Acceptance:
   - exact example input -> exact expected result
   - error case -> CalcError with code UPPER_SNAKE_CASE
   ```
4. Show it to the user. Change it to `status: approved` only when the user says so.

## Change an approved requirement
1. Do NOT edit it. Change its status line to `status: superseded`.
2. Add a new REQ with the next number and "(replaces REQ-OLD)" in the title, in the format above.
3. Run `rag.py check`. It lists the code still tagged with the old ID.
   Tell the user to run /sdd-implement for the new REQ.

## Add a decision
Same format with `## DEC-NNN Title` and no Acceptance list. Decisions apply to every task.
