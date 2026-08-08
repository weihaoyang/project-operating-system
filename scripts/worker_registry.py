#!/usr/bin/env python3
"""Register and release disjoint project workers in an append-only JSONL registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def objective_key(task: str) -> str:
    return hashlib.sha256(task.strip().lower().encode("utf-8")).hexdigest()[:16]


def ownership_key(task: str, paths: list[str]) -> str:
    raw = task.strip().lower() + "\0" + "\0".join(sorted(p.replace("\\", "/").lower() for p in paths))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def latest(path: Path) -> dict[str, dict]:
    result: dict[str, dict] = {}
    if not path.exists():
        return result
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("worker"):
            result[str(item["worker"])] = item
    return result


def append(path: Path, item: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, ensure_ascii=False) + "\n")


def max_workers(root: Path) -> int:
    contract = root / "docs/TASK_CONTRACT.md"
    if not contract.exists():
        return 3
    match = re.search(r"^\s*max_workers:\s*(\d+)", contract.read_text(encoding="utf-8", errors="replace"), re.MULTILINE)
    return max(1, int(match.group(1))) if match else 3


def with_lock(path: Path):
    lock = path.with_suffix(path.suffix + ".lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise SystemExit(f"REGISTRY_BUSY {lock}") from exc
    os.close(descriptor)
    return lock


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start")
    start.add_argument("--project-root", default=".")
    start.add_argument("--worker", required=True)
    start.add_argument("--task", required=True)
    start.add_argument("--paths", nargs="*", default=[])
    start.add_argument("--thread-id", default="")
    start.add_argument("--host-id", default="local")
    start.add_argument("--sync-mode", choices=("verified", "degraded"), default="verified")
    release = sub.add_parser("release")
    release.add_argument("--project-root", default=".")
    release.add_argument("--worker", required=True)
    release.add_argument("--status", choices=("complete", "blocked", "cancelled"), default="complete")
    show = sub.add_parser("status")
    show.add_argument("--project-root", default=".")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    registry = root / "docs/ACTIVE_WORK.jsonl"
    lock = with_lock(registry)
    try:
        records = latest(registry)
        if args.command == "status":
            for item in records.values():
                if item.get("status") == "running":
                    print(json.dumps(item, ensure_ascii=False))
            return 0
        if args.command == "release":
            if args.worker not in records:
                print(f"WARN unknown worker {args.worker}")
            append(registry, {"worker": args.worker, "status": args.status, "updated": now()})
            print(f"RELEASED {args.worker} {args.status}")
            return 0

        objective = objective_key(args.task)
        ownership = ownership_key(args.task, args.paths)
        incoming = {p.replace("\\", "/").lower() for p in args.paths}
        active = [item for item in records.values() if item.get("status") == "running"]
        if len(active) >= max_workers(root):
            print(f"BLOCK worker budget exhausted active={len(active)} max={max_workers(root)}")
            return 2
        for item in records.values():
            if item.get("status") != "running":
                continue
            existing_objective = item.get("objective_key") or objective_key(str(item.get("task", "")))
            if existing_objective == objective:
                print(f"BLOCK duplicate task owned by {item.get('worker')}")
                return 2
            existing = {p.replace("\\", "/").lower() for p in item.get("paths", [])}
            if incoming.intersection(existing):
                print(f"BLOCK overlapping paths owned by {item.get('worker')}")
                return 2
        append(registry, {"worker": args.worker, "thread_id": args.thread_id, "host_id": args.host_id, "sync_mode": args.sync_mode, "objective_key": objective, "ownership_key": ownership, "task": args.task, "paths": args.paths, "status": "running", "started": now()})
        print(f"STARTED {args.worker} objective={objective} ownership={ownership}")
        return 0
    finally:
        try:
            lock.unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
