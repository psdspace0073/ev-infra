# EV Infra Map India: Project Rules

## Mission
Build an auditable, reproducible EV infrastructure decision-support
prototype for the EV Infra & Green Mobility AI Challenge.

## Scope
- Begin with Karnataka as the pilot / proof-of-work geography
  (docs/decisions/ADR-001-geography.md).
- Design a repeatable pipeline that can later expand state by state.
- Support EV demand analysis, charging infrastructure gap analysis,
  and candidate-site prioritisation.
- Follow the official problem statement, final research report,
  final changelog and submission checklist in docs/reference/.

## Data integrity
- Never invent dataset values, source URLs, licences or test results.
- Preserve downloaded raw source files unchanged.
- Record publisher, source URL, retrieval date, geography, time period,
  licence, transformations and limitations for each dataset.
- Distinguish observed, officially reported, planned, inferred and
  synthetic data.
- Do not assume installed chargers are operational.
- Do not treat RTO-level registrations as exact vehicle locations.
- Document conflicting source counts instead of silently reconciling them.

## Engineering
- Keep reusable application logic in src/evinfra/.
- Add tests for important transformations and calculations.
- Prefer reproducible scripts over manual-only notebook workflows.
- Explain new dependencies before adding them.
- Never commit secrets or local environment files.
- Never overwrite raw data.
- Never claim a test passed unless it was actually run.

## Shared-agent protocol
- Only one agent may modify the shared working tree at a time.
- Read this file and check git status before each task.
- Inspect existing code before editing.
- Do not overwrite uncommitted work from another agent.
- Report changed files, commands run, actual test results and remaining issues.
- Do not commit changes without user review.
- Do not run destructive Git cleanup or reset commands without permission.

## Definition of done
1. Requested changes exist.
2. Relevant tests or validation commands have been run.
3. Results and limitations are reported honestly.
4. No unrelated changes are included.
5. The next step is documented.
