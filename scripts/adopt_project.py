#!/usr/bin/env python3
"""Adopt an existing project without resetting its state or pretending it is complete."""

from __future__ import annotations

import argparse
import json
import re
import sys
import subprocess
from datetime import date
from pathlib import Path


SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", ".cache", "__pycache__"}
HIGH_RISK_MARKERS = {"clinical", "medical", "trading", "finance", "payment", "production", "deploy", "training", "migration", "sql", "qmt", "pinn"}
MANIFESTS = {"package.json", "pyproject.toml", "requirements.txt", "cargo.toml", "go.mod", "pom.xml", "build.gradle", "dockerfile", "docker-compose.yml", "pnpm-lock.yaml", "package-lock.json"}
WORKFLOW_FILES = (
    "AGENTS.md",
    "docs/PROJECT_STATUS.yaml",
    "docs/TASK_CONTRACT.md",
    "docs/KNOWLEDGE_BASE.md",
    "docs/ARCHITECTURE_DECISIONS.md",
    "docs/EVIDENCE_INDEX.jsonl",
    "docs/ACTIVE_WORK.jsonl",
    "docs/TECH_DEBT.yaml",
    "docs/research/INDEX.yaml",
    "docs/PROJECT_INVENTORY.json",
)


def run(root: Path, command: list[str]) -> str:
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def git_inventory(root: Path) -> dict:
    inside = run(root, ["git", "rev-parse", "--is-inside-work-tree"]) == "true"
    if not inside:
        return {"is_git": False, "branch": "", "dirty_files": 0, "recent_commits": [], "tracked_files": 0}
    branch = run(root, ["git", "branch", "--show-current"])
    dirty = run(root, ["git", "status", "--short"])
    log = run(root, ["git", "log", "-8", "--date=iso-strict", "--format=%H%x09%ad%x09%s"])
    tracked = run(root, ["git", "ls-files"])
    commits = []
    for line in log.splitlines():
        commit, _, rest = line.partition("\t")
        timestamp, _, subject = rest.partition("\t")
        commits.append({"commit": commit, "timestamp": timestamp, "subject": subject})
    return {"is_git": True, "branch": branch, "dirty_files": len(dirty.splitlines()) if dirty else 0, "recent_commits": commits, "tracked_files": len(tracked.splitlines()) if tracked else 0}


def project_inventory(root: Path) -> dict:
    top_level = sorted(item.name for item in root.iterdir() if item.name not in SKIP_DIRS)
    lower_top = {item.lower() for item in top_level}
    manifests = sorted(item for item in top_level if item.lower() in MANIFESTS)
    source_dirs = sorted(item for item in top_level if item.lower() in {"src", "app", "apps", "lib", "server", "frontend", "backend", "scripts", "tests", "test", "docs"})
    signal_text = " ".join((root.name, *top_level)).lower()
    signal_tokens = {token for token in re.split(r"[^a-z0-9]+", signal_text) if token}
    high_risk = bool(signal_tokens & HIGH_RISK_MARKERS)
    git = git_inventory(root)
    if high_risk:
        recommended = "high-risk"
    elif git["tracked_files"] > 0 or manifests or source_dirs:
        recommended = "standard"
    else:
        recommended = "lite"
    return {
        "inventory_version": 1,
        "adopted_at": date.today().isoformat(),
        "root": str(root),
        "top_level": top_level[:200],
        "manifests": manifests,
        "source_dirs": source_dirs,
        "git": git,
        "existing_workflow_files": [item for item in WORKFLOW_FILES if (root / item).exists()],
        "recommended_profile": recommended,
        "limitations": ["Inventory is structural evidence only; it does not infer feature completeness or project intent."],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--project-name", default="")
    parser.add_argument("--profile", choices=("auto", "lite", "standard", "high-risk"), default="auto")
    parser.add_argument("--refresh-inventory", action="store_true")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    if not root.is_dir():
        raise SystemExit(f"Project root does not exist: {root}")
    inventory = project_inventory(root)
    profile = inventory["recommended_profile"] if args.profile == "auto" else args.profile
    bootstrap = Path(__file__).with_name("bootstrap_project.py")
    result = subprocess.run([sys.executable, "-X", "utf8", str(bootstrap), "--project-root", str(root), "--project-name", args.project_name or root.name, "--profile", profile, "--mode", "adopt"], capture_output=True, text=True, check=False)
    print(result.stdout, end="")
    if result.returncode != 0:
        print(result.stderr, end="")
        return result.returncode
    target = root / "docs/PROJECT_INVENTORY.json"
    if target.exists() and not args.refresh_inventory:
        print(f"EXISTS {target} (use --refresh-inventory to replace generated inventory)")
    else:
        inventory["existing_workflow_files"] = sorted(
            set(inventory["existing_workflow_files"]) | {"docs/PROJECT_INVENTORY.json"}
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"CREATED {target}")
    print(f"ADOPTED profile={profile} phase=adopting status=needs_reconciliation")
    print("NEXT read PROJECT_INVENTORY, existing status/commits/tests, then update TASK_CONTRACT before implementation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
