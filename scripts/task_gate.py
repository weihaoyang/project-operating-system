#!/usr/bin/env python3
"""Check a task before implementation or delegation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def value(text: str, key: str, default: str = "") -> str:
    match = re.search(rf"^\s*{re.escape(key)}:\s*[\"']?([^\"'\n]*)", text, re.MULTILINE)
    return match.group(1).strip() if match else default


def normalize(path: str) -> str:
    return path.replace("\\", "/").strip("./").lower()


def objective_key(task: str) -> str:
    raw = task.strip().lower()
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def ownership_key(task: str, paths: list[str]) -> str:
    raw = task.strip().lower() + "\0" + "\0".join(sorted(normalize(p) for p in paths))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def active_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    latest: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        worker = str(item.get("worker", ""))
        if worker:
            latest[worker] = item
    return [item for item in latest.values() if item.get("status") == "running"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--task", required=True)
    parser.add_argument("--mode", choices=("research_only", "awaiting_confirmation", "implementation", "verification", "operations"), default="implementation")
    parser.add_argument("--paths", nargs="*", default=[])
    parser.add_argument("--confirmed", action="store_true")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    status = root / "docs/PROJECT_STATUS.yaml"
    contract = root / "docs/TASK_CONTRACT.md"
    registry = root / "docs/ACTIVE_WORK.jsonl"
    current_phase = value(status.read_text(encoding="utf-8", errors="replace"), "phase") if status.exists() else "unknown"
    objective = objective_key(args.task)
    ownership = ownership_key(args.task, args.paths)
    print(f"OBJECTIVE_KEY {objective}")
    print(f"OWNERSHIP_KEY {ownership}")
    print(f"PHASE {current_phase}")

    if args.mode in {"implementation", "verification", "operations"} and current_phase in {"adopting", "needs_reconciliation"}:
        print("BLOCK existing project reconciliation is required before implementation")
        return 2
    if args.mode in {"implementation", "verification", "operations"} and current_phase in {"intake", "needs_confirmation", "awaiting_confirmation", "researching"} and not args.confirmed:
        print("BLOCK confirmation is required before implementation")
        return 2
    if not contract.exists():
        print("WARN missing docs/TASK_CONTRACT.md; bootstrap the project before delegation")

    contract_text = contract.read_text(encoding="utf-8", errors="replace") if contract.exists() else ""
    budget_text = value(contract_text, "max_workers", "3")
    try:
        max_workers = max(1, int(budget_text))
    except ValueError:
        max_workers = 3
    incoming = {normalize(p) for p in args.paths}
    active = active_records(registry)
    if len(active) >= max_workers:
        print(f"BLOCK worker budget exhausted active={len(active)} max={max_workers}")
        return 2
    for record in active:
        existing_objective = str(record.get("objective_key", "")) or objective_key(str(record.get("task", "")))
        existing_paths = {normalize(p) for p in record.get("paths", [])}
        if existing_objective == objective:
            print(f"BLOCK duplicate active task owned by {record.get('worker', 'unknown')}")
            return 2
        if incoming and existing_paths and incoming.intersection(existing_paths):
            print(f"BLOCK overlapping active paths owned by {record.get('worker', 'unknown')}")
            return 2
    print("PASS task is eligible")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
