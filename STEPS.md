# Calculator in Google Antigravity: spec-driven development + RAG, step by step

## What's in the folder
```
scope.md                          WHAT to build (REQ-NNN requirements, DEC-NNN decisions)
prompt.md                         HOW the agent works (rules + output format); rag.py fills it
.agents/rules/sdd-rag.md          always-on rule: "retrieve with rag.py before planning"
.agents/skills/sdd-implement/     /sdd-implement: retrieve → plan → tasks → code → verify
    SKILL.md
    scripts/rag.py                the retriever (standard-library Python, no installs)
.agents/skills/sdd-change/        /sdd-change: add or replace requirements in scope.md
```

## Step 1: Open the project
Antigravity → Open Folder → `calculator-antigravity`. The agent loads the rule and both
skills automatically. Check under Customizations, or type `/` to see `/sdd-implement`.
Select **Review-driven** (or Agent-assisted) mode, so you approve each plan.
You need Python 3.10+ and `pip install pytest`.

## Step 2: See where you stand
Ask the agent: **"Run rag.py list and check"**, or run it yourself in the terminal:
```
python .agents/skills/sdd-implement/scripts/rag.py check
REQ-001  approved  CODE 0  TESTS 0  <- missing code and tests
REQ-002  approved  CODE 0  TESTS 0  <- missing code and tests
REQ-003  approved  CODE 0  TESTS 0  <- missing code and tests
REQ-004  draft     CODE 0  TESTS 0       (draft: will not be built)
```

## Step 3: Build REQ-001 and REQ-002
Type: **`/sdd-implement REQ-001 and REQ-002`**

The agent runs:
```
rag.py ask "Implement REQ-001 and REQ-002 basic arithmetic"
  [always] Overview, Out of scope, Glossary, DEC-001 Decimal, DEC-002 CalcError
  [search] REQ-001 Add and subtract
  [search] REQ-002 Multiply and divide
```
Then it writes an **Implementation Plan** that starts with
`Context used: REQ-001, REQ-002, DEC-001, DEC-002` and a coverage table.
→ Review it and click **Proceed**.

It creates `src/calculator.py` (using Decimal, tagged `# Implements: REQ-001`) and
`tests/test_calculator.py`, then runs pytest and `check`. The **Walkthrough** shows:
REQ-001 and REQ-002 covered, REQ-003 still missing.

## Step 4: Build REQ-003, which builds on existing code
Type: **`/sdd-implement REQ-003`**
```
  [search] REQ-003 Division by zero
  [linked] src/calculator.py :: divide       ← existing code is retrieved
  [linked] src/calculator.py :: CalcError    ← so it is reused, not rewritten
```
The agent edits `divide()` in place and adds `test_divide_by_zero`. `check`: **0 problems**.

## Step 5: Test the guard rails
- "Add a square root button" → refused: it's under Out of scope.
- "/sdd-implement REQ-004" → stops: REQ-004 is draft, and it asks the open question.
- "Make divide return 0 instead of an error" → points out that this conflicts with REQ-003
  and DEC-002 and suggests /sdd-change.

## Step 6: Change a requirement
Type: **`/sdd-change add should accept any number of values`**

The agent marks REQ-001 `superseded` and adds a draft **REQ-005 Add many numbers
(replaces REQ-001)** with acceptance examples. Review it and say "approve REQ-005".
```
rag.py check
REQ-001  superseded  CODE 2  TESTS 3  <- code refers to a superseded requirement
REQ-005  approved    CODE 0  TESTS 0  <- missing code and tests
```

## Step 7: Implement the change
Type: **`/sdd-implement REQ-005`**. The retriever brings back the old `add()` and its tests.
The agent updates them and re-tags them REQ-005. `check`: **0 problems**.

## The loop
```
/sdd-change  →  approve in scope.md  →  /sdd-implement REQ-NNN
   →  RAG retrieves context  →  Plan (you approve)  →  Tasks  →  Code + tests
   →  pytest + rag.py check  →  Walkthrough
```

## Why the results stay consistent
- The same script always retrieves the same context for the same scope and code.
- The agent sees only approved requirements plus all decisions, never drafts or old versions.
- The prompt template fixes the rules and the output format.
- Tagging code with REQ IDs lets every later task find the code it builds on.
- `check` catches anything missing or stale.

## Use it for your own project
Replace the content of `scope.md` (keep the format) and the Role line in `prompt.md`.
Keep the `.agents/` folder as it is.
