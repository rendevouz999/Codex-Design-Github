#!/usr/bin/env python
"""Append controlled design reflection lessons to REFLECTION_LOG.md.

This utility supports local Codex Design Brain memory. It does not train a
model, rewrite core design memory, or change preference weights. It only
formats and appends a reusable lesson to .design-brain/REFLECTION_LOG.md.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path


LOG_HEADER = """# Reflection Log

Save reusable lessons from user feedback here. Keep entries concise and practical.

"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append a controlled Codex Design Brain reflection lesson."
    )
    parser.add_argument("--task", required=True, help="Task or design work being reviewed.")
    parser.add_argument("--feedback", required=True, help="User feedback to preserve.")
    parser.add_argument(
        "--went-wrong",
        required=True,
        help="What went wrong in the design decision or output.",
    )
    parser.add_argument("--lesson", required=True, help="Reusable design lesson extracted.")
    parser.add_argument("--rule", required=True, help="Rule to reuse next time.")
    parser.add_argument(
        "--source-report",
        default="None",
        help="Optional path to a related review report. Defaults to None.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the reflection entry without modifying REFLECTION_LOG.md.",
    )
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def warn_if_vague(name: str, value: str, warnings: list[str]) -> None:
    stripped = " ".join(value.split())
    vague_values = {"n/a", "none", "test", "good", "bad", "fix it", "improve", "better"}
    if len(stripped) < 12:
        warnings.append(f"{name} may be too short to be reusable.")
    if stripped.lower() in vague_values:
        warnings.append(f"{name} is vague; use a concrete design observation.")


def normalize_block(value: str) -> str:
    return value.strip().replace("\r\n", "\n").replace("\r", "\n")


def build_entry(args: argparse.Namespace) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    source_report = normalize_block(args.source_report) or "None"
    return f"""## {timestamp} - {normalize_block(args.task)}

### User Feedback

{normalize_block(args.feedback)}

### What Went Wrong

{normalize_block(args.went_wrong)}

### Design Lesson

{normalize_block(args.lesson)}

### Rule To Reuse Next Time

{normalize_block(args.rule)}

### Source Report

{source_report}

---
"""


def ensure_log_file(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text(LOG_HEADER, encoding="utf-8")


def append_entry(log_path: Path, entry: str) -> None:
    existing = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    separator = "" if not existing or existing.endswith("\n") else "\n"
    with log_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(separator)
        handle.write(entry)


def main() -> int:
    args = parse_args()
    warnings: list[str] = []

    warn_if_vague("task", args.task, warnings)
    warn_if_vague("feedback", args.feedback, warnings)
    warn_if_vague("went-wrong", args.went_wrong, warnings)
    warn_if_vague("lesson", args.lesson, warnings)
    warn_if_vague("rule", args.rule, warnings)

    root = repo_root()
    log_path = root / ".design-brain" / "REFLECTION_LOG.md"
    entry = build_entry(args)

    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)

    if args.dry_run:
        print(entry, end="")
        return 0

    try:
        ensure_log_file(log_path)
        append_entry(log_path, entry)
    except OSError as exc:
        print(f"ERROR: Could not update {log_path}: {exc}", file=sys.stderr)
        return 1

    print(f"Reflection lesson appended to: {log_path}")
    print("Core design memory and preference weights were not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
