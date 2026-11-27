# Project Scope: Calculator

<!--
RULES FOR WRITING THIS FILE (so the AI can retrieve it reliably)
1. One "## " heading per item. The retriever splits the file on "## ".
2. Requirements: "## REQ-NNN Title".  Decisions: "## DEC-NNN Title".  IDs are never reused.
3. The first line under each REQ/DEC heading is the status:  status: draft | approved | superseded
   Only "approved" items are given to the AI.
4. Every REQ has an "Acceptance:" list. Each bullet is one exact, testable example.
5. To change an approved REQ, don't edit it. Mark it superseded and add a new REQ
   that says "(replaces REQ-NNN)". The /sdd-change skill does this for you.
6. "Overview", "Out of scope" and "Glossary" are always sent to the AI. Keep them short.
-->

## Overview
A Python calculator library with a command-line interface (CLI).
Stack: Python 3.12, standard library only, pytest for tests.
Code lives in src/calculator.py. Tests live in tests/test_calculator.py.

## Out of scope
- No GUI or web app.
- No scientific functions (sin, cos, log, square root, power).
- No memory buttons (M+, M-, MR).
- No third-party packages.

## Glossary
- **Operand**: a number the user enters, e.g. 7 in "7 + 3".
- **Operator**: one of + - * /
- **CalcError**: the only exception type the library raises (see DEC-002).

## REQ-001 Add and subtract
status: approved
Calculate a + b and a - b.
Acceptance:
- add(2, 3) returns 5
- subtract(2, 5) returns -3
- add(0.1, 0.2) returns exactly 0.3

## REQ-002 Multiply and divide
status: approved
Calculate a * b and a / b.
Acceptance:
- multiply(4, 2.5) returns 10
- divide(10, 4) returns 2.5

## REQ-003 Division by zero
status: approved
Dividing by zero must not crash the program.
Acceptance:
- divide(5, 0) raises CalcError with code DIVIDE_BY_ZERO

## REQ-004 Command-line usage
status: draft
User types: calc 7 + 3   and sees: 10
Open question: how should errors be shown on the command line?

## DEC-001 Use Decimal, not float
status: approved
All maths uses Python's decimal.Decimal so that 0.1 + 0.2 equals 0.3 exactly.
Convert inputs with Decimal(str(x)). Round results to 10 decimal places (ROUND_HALF_UP).

## DEC-002 One error type
status: approved
All errors raise CalcError(code, message). Codes are UPPER_SNAKE_CASE.
Never raise built-in exceptions (ZeroDivisionError, ValueError) to the caller.
