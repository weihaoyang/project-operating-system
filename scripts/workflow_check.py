#!/usr/bin/env python3
"""Print a compact, read-only health check for the project workflow."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


BASE_REQUIRED = (
    "AGENTS.md",
    "docs/PROJECT_STATUS.yaml",
    "docs/TASK_CONTRACT.md",
)
STANDARD_REQUIRED = (
    "docs/KNOWLEDGE_BASE.md",
    "docs/ARCHITECTURE_DECISIONS.md",
    "docs/EVIDENCE_INDEX.jsonl",
)
HIGH_RISK_REQUIRED = (
    "docs/ACTIVE_WORK.jsonl",
    "docs/TECH_DEBT.yaml",
    "docs/research/INDEX.yaml",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    print(f"PROJECT {root}")
    status_path = root / "docs/PROJECT_STATUS.yaml"
    status_text = status_path.read_text(encoding="utf-8", errors="replace") if status_path.exists() else ""
    profile = "high-risk" if "profile: 'high-risk'" in status_text or 'profile: "high-risk"' in status_text else "standard" if "profile: 'standard'" in status_text or 'profile: "standard"' in status_text else "lite"
    required = BASE_REQUIRED + (STANDARD_REQUIRED if profile in {"standard", "high-risk"} else ()) + (HIGH_RISK_REQUIRED if profile == "high-risk" else ())
    print(f"PROFILE {profile}")
    missing = [item for item in required if not (root / item).exists()]
    print("WORKFLOW_FILES " + ("OK" if not missing else "MISSING " + ", ".join(missing)))

    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        print(f"GIT unavailable: {exc}")
        return 0
    if result.returncode != 0:
        print("GIT status unavailable")
    else:
        lines = result.stdout.splitlines()
        print(f"GIT_CHANGES {len(lines)}")
        for line in lines[:20]:
            print(line)
        if len(lines) > 20:
            print(f"... {len(lines) - 20} more")

    contract = root / "docs/TASK_CONTRACT.md"
    if contract.exists():
        text = contract.read_text(encoding="utf-8", errors="replace")
        for key in ("task:", "owner:", "mode:", "status:", "next_action:"):
            value = next((line.strip() for line in text.splitlines() if line.strip().startswith(key)), "")
            print(f"CONTRACT_{key[:-1].upper()} {value}")
    registry = root / "docs/ACTIVE_WORK.jsonl"
    if registry.exists():
        latest = {}
        for line in registry.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                item = json.loads(line)
            except ValueError:
                continue
            if item.get("worker"):
                latest[item["worker"]] = item
        running = sum(1 for item in latest.values() if item.get("status") == "running")
        print(f"ACTIVE_WORK_RECORDS {running}")
    debt = root / "docs/TECH_DEBT.yaml"
    if debt.exists():
        print(f"TECH_DEBT_LINES {len(debt.read_text(encoding='utf-8', errors='replace').splitlines())}")
    inventory = root / "docs/PROJECT_INVENTORY.json"
    if inventory.exists():
        print("ADOPTION_INVENTORY OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
