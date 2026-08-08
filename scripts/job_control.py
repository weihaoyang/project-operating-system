#!/usr/bin/env python3
"""Track generic long-running jobs with one-instance records and resumable metadata."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start")
    start.add_argument("--project-root", default=".")
    start.add_argument("--job-id", required=True)
    start.add_argument("--command", required=True)
    start.add_argument("--cwd", default=".")
    status = sub.add_parser("status")
    status.add_argument("--project-root", default=".")
    status.add_argument("--job-id", required=True)
    stop = sub.add_parser("stop")
    stop.add_argument("--project-root", default=".")
    stop.add_argument("--job-id", required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    jobs = root / "docs/jobs"
    jobs.mkdir(parents=True, exist_ok=True)
    record_path = jobs / f"{args.job_id}.json"
    if args.command == "status":
        if not record_path.exists():
            print(f"UNKNOWN {args.job_id}")
            return 1
        print(record_path.read_text(encoding="utf-8"))
        return 0
    record = json.loads(record_path.read_text(encoding="utf-8")) if record_path.exists() else {}
    if args.command == "start":
        if record.get("status") == "running":
            print(f"BLOCK job already running pid={record.get('pid')}")
            return 2
        log_path = jobs / f"{args.job_id}.log"
        handle = log_path.open("a", encoding="utf-8")
        flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
        requested_cwd = Path(args.cwd)
        job_cwd = requested_cwd if requested_cwd.is_absolute() else root / requested_cwd
        process = subprocess.Popen(args.command, cwd=job_cwd.resolve(), shell=True, stdout=handle, stderr=subprocess.STDOUT, creationflags=flags)
        handle.close()
        record = {"job_id": args.job_id, "command": args.command, "cwd": str(job_cwd.resolve()), "pid": process.pid, "status": "running", "started": now(), "heartbeat": "", "checkpoint": "", "log": str(log_path)}
        record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"STARTED {args.job_id} pid={process.pid}")
        return 0
    pid = int(record.get("pid", 0))
    if not pid:
        print(f"UNKNOWN pid for {args.job_id}")
        return 1
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    record["status"] = "stopped"
    record["stopped"] = now()
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"STOPPED {args.job_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
