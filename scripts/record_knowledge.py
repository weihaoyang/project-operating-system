#!/usr/bin/env python3
"""Append a compact, deduplicated verified solution to a project's knowledge base."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--title", required=True)
    parser.add_argument("--problem", required=True)
    parser.add_argument("--solution", required=True)
    parser.add_argument("--verification", required=True)
    parser.add_argument("--source", required=True, help="URL, commit, issue, or local file")
    parser.add_argument("--environment", default="")
    parser.add_argument("--confidence", default="confirmed")
    parser.add_argument("--source-type", default="experiment", choices=("official", "github_issue", "code", "experiment", "community"))
    parser.add_argument("--verified-at", default=date.today().isoformat())
    parser.add_argument("--recheck-after", default="")
    parser.add_argument("--tags", default="")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    target = root / "docs" / "KNOWLEDGE_BASE.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_text("# Local project knowledge base\n\n", encoding="utf-8")
    existing = target.read_text(encoding="utf-8")
    marker = f"### {date.today().isoformat()} — {args.title}"
    if marker in existing:
        print(f"SKIPPED duplicate {marker}")
        return 0

    entry = f"""
{marker}

- Problem: {args.problem}
- Environment: {args.environment}
- Root cause / confidence: {args.confidence}
- Solution: {args.solution}
- Verification: {args.verification}
- Source: {args.source}
- Source type: {args.source_type}
- Verified at: {args.verified_at}
- Recheck after: {args.recheck_after}
- Tags: {args.tags}
"""
    with target.open("a", encoding="utf-8") as handle:
        handle.write(entry.rstrip() + "\n")
    print(f"RECORDED {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
