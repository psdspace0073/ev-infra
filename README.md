# EV Infra Map India

A reproducible, evidence-backed EV infrastructure decision-support prototype.
Pilot geography: Karnataka. Telangana is a future expansion geography
(see docs/decisions/ADR-001-geography.md).

## Development

Create and activate a Python virtual environment, then install development tools:

    python -m pip install -e ".[dev]"

Run tests:

    python -m pytest

Run lint checks:

    python -m ruff check src tests

See PROJECT_RULES.md and docs/reference/ for project constraints.
