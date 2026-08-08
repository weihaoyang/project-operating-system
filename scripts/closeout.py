#!/usr/bin/env python3
"""Run explicitly selected, proportional closeout checks."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--evidence", nargs="*", default=[])
    parser.add_argument("--test-command", action="append", default=[])
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    failed = False
    for item in args.evidence:
        path = root / item
        if path.exists():
            print(f"EVIDENCE OK {item}")
        else:
            print(f"EVIDENCE MISSING {item}")
            failed = True

    diff = subprocess.run(["git", "diff", "--check"], cwd=root, capture_output=True, text=True, check=False)
    if diff.returncode == 0:
        print("DIFF_CHECK OK")
    else:
        print(diff.stdout or diff.stderr)
        failed = True

    if len(args.test_command) > 3:
        print("BLOCK more than three explicit checks; justify a larger release gate separately")
        return 2
    for command in args.test_command:
        result = subprocess.run(command, cwd=root, shell=True, capture_output=True, text=True, check=False)
        print(f"CHECK {'PASS' if result.returncode == 0 else 'FAIL'} {command}")
        if result.returncode != 0:
            print((result.stdout + result.stderr)[-2000:])
            failed = True
    status = subprocess.run(["git", "status", "--short"], cwd=root, capture_output=True, text=True, check=False)
    print(f"GIT_CHANGES {len(status.stdout.splitlines())}")
    print("CLOSEOUT_BLOCKED" if failed else "CLOSEOUT_READY")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
