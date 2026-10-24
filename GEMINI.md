# Antigravity Workspace Instructions — EV Infra Map India

Treat `PROJECT_RULES.md` as the shared project source of truth. Read `PROJECT_RULES.md` before doing any work on any task.
Read the authoritative reference documents in `docs/reference/` relevant to the task.

## At the start of each task:
1. Always read `PROJECT_RULES.md` before starting work.
2. Run `git status --short` to inspect working tree state before editing.
3. Inspect relevant existing code and files before making edits.
4. Limit changes strictly to assigned files; do not modify files outside the assigned task.
5. Only one agent may modify the shared working tree at a time; never overwrite uncommitted work from another agent.

## During and after execution:
1. Follow data integrity guidelines: never invent dataset values, source URLs, licences, or test results; preserve raw source files unchanged.
2. Engineering standards: keep reusable logic in `src/evinfra/`, add tests for transformations/calculations, and prefer reproducible scripts.
3. Report actual test results: run relevant tests or validation commands and report real test output honestly. Never claim a test passed unless it was actually run.
4. Summarise changed files, commands run, real test results, and any unresolved assumptions or limitations.
5. Do not commit changes without explicit user review.
6. Do not run destructive Git cleanup or reset commands without permission.
