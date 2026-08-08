#!/usr/bin/env python3
"""Create the smallest suitable project workflow profile without overwriting files."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path


def write_if_missing(path: Path, content: str) -> str:
    if path.exists():
        return f"EXISTS {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return f"CREATED {path}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--project-name", default="Project")
    parser.add_argument("--profile", choices=("lite", "standard", "high-risk"), default="standard")
    parser.add_argument("--mode", choices=("start", "adopt"), default="start")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    if not root.is_dir():
        raise SystemExit(f"Project root does not exist: {root}")

    today = date.today().isoformat()
    phase = "adopting" if args.mode == "adopt" else "intake"
    status = "needs_reconciliation" if args.mode == "adopt" else "needs_confirmation"
    files: dict[Path, str] = {
        root / "AGENTS.md": f"""# {args.project_name} project rules

This project uses the `project-operating-system` workflow with the `{args.profile}` profile.

## Core principles

- Start from the user outcome and the smallest invariant that must be true.
- Prefer the simplest design that satisfies that invariant; remove layers that buy no reliability.
- Every task has one owner, one bounded scope, and one acceptance gate.
- Every gate must name the concrete failure it catches. Do not add ritual tests.

## Coordination

- Keep one canonical main task for this project.
- Before implementation, read `docs/PROJECT_STATUS.yaml` and `docs/TASK_CONTRACT.md`.
- Maximum normal concurrency: three disjoint workers; use one owner for schema, migrations, public interfaces, lockfiles, and central configuration.
- Before spawning, follow `references/thread-sync.md`: reconcile `list_threads` with the local active-work registry and store thread/host IDs. If unavailable, use degraded single-worker mode.
- Workers return compact evidence; the main task integrates and closes out.

## Research gate

For a new product or major feature, complete a read-only GitHub comparison and obtain user confirmation before creating implementation files. Record the proposal and sources. Explicit user permission to skip research must be recorded in the task contract.

For an existing project, run `adopt_project.py --profile auto` first. Preserve existing history and files, read the generated inventory, reconcile status and evidence, and start from the highest-value unresolved gap.

## Verification

- Use the minimum sufficient check: focused test for isolated code, boundary smoke for contract changes, real counts/hashes/checkpoints for data or runtime changes.
- Reuse unchanged evidence. Full suites, long matrices, and full rebuilds require a concrete risk or release reason.
- Long-running jobs require one-instance lock, environment preflight, heartbeat, checkpoint, status, and resume.
- Do not call mocks, placeholders, or existence checks a completed capability.

## Knowledge and debt

- Record verified difficult solutions in `docs/KNOWLEDGE_BASE.md` with source and verification.
- Record consequential architecture choices in `docs/ARCHITECTURE_DECISIONS.md`.
- Record only actionable debt with severity, owner, impact, and repayment condition in `docs/TECH_DEBT.yaml`.

## Scope

Do not perform unrelated cleanup or speculative refactoring. Preserve existing user changes.
""",
        root / "docs" / "PROJECT_STATUS.yaml": f"""project: {args.project_name!r}
profile: {args.profile!r}
updated: {today!r}
objective: ""
success_condition: ""
phase: {phase!r}
status: {status!r}
current_blocker: ""
next_action: ""
active_workers: []
recent_evidence: []
closed_routes: []
last_commit: ""
remote_state: "unknown"
adoption:
  mode: {args.mode!r}
  inventory: "docs/PROJECT_INVENTORY.json"
  requires_reconciliation: {str(args.mode == "adopt").lower()}
""",
        root / "docs" / "TASK_CONTRACT.md": """# Current task contract

```yaml
task: ""
objective_key: ""
ownership_key: ""
owner: "main"
mode: "research_only"
scope:
  include: []
  exclude: []
acceptance: []
verification:
  commands: []
  evidence: []
  reason_for_each_gate: []
budget:
  max_workers: 3
  max_full_scans: 1
  max_retries: 2
  max_expensive_checks: 1
stop_conditions: []
file_ownership: []
status: "planned"
next_action: ""
""",
    }
    standard_files = {
        root / "docs" / "EVIDENCE_INDEX.jsonl": "",
        root / "docs" / "KNOWLEDGE_BASE.md": """# Local project knowledge base

Use one entry per verified problem or external finding. Keep secrets and unnecessary logs out.

## Entry format

### YYYY-MM-DD — short title

- Problem:
- Environment:
- Root cause / confidence:
- Solution:
- Verification:
- Source:
- Source type:
- Verified at:
- Recheck after:
- Tags:
""",
        root / "docs" / "ARCHITECTURE_DECISIONS.md": """# Architecture decisions

Record only decisions that affect boundaries, data contracts, dependencies, deployment, safety, or reversibility.

## Format

### ADR-001 — title

- Date:
- Status: proposed | accepted | rejected | superseded
- Context:
- Decision:
- Alternatives:
- Consequences:
- Evidence:
""",
    }
    high_risk_files = {
        root / "docs" / "ACTIVE_WORK.jsonl": "",
        root / "docs" / "TECH_DEBT.yaml": """# Only actionable debt belongs here.
items: []
""",
        root / "docs" / "research" / "INDEX.yaml": """reports: []
""",
    }
    if args.profile in {"standard", "high-risk"}:
        files.update(standard_files)
    if args.profile == "high-risk":
        files.update(high_risk_files)
    for path, content in files.items():
        print(write_if_missing(path, content))
    print(f"PROFILE {args.profile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
