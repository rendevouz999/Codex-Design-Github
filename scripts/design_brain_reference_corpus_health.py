#!/usr/bin/env python
"""Check Design Brain local reference corpus availability.

This is intentionally a health check, not a selector. It reports whether a
reference-led workflow has local files to study before Codex claims that local
reference selection happened.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REFERENCE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".fig"}
DEFAULT_CORPUS_FOLDERS = [
    "Template Website",
    "references/Template Website",
    "references/template-website",
    ".design-brain/reference-corpus/template-website",
    ".design-brain/evidence/fig-extracts",
]
EXCLUDED_NAME_PARTS = {
    "captcha",
    "license",
    "readme",
    "font",
    "documentation",
    "changelog",
    "support",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check local Design Brain reference corpus health.")
    parser.add_argument("--source", default="", help="Optional corpus folder. Relative paths resolve from repo root.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of markdown.")
    return parser.parse_args()


def resolve(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def checked_paths(root: Path, source: str = "") -> list[Path]:
    values = [source] if source else DEFAULT_CORPUS_FOLDERS
    if source:
        values.extend(item for item in DEFAULT_CORPUS_FOLDERS if item != source)

    result: list[Path] = []
    seen: set[str] = set()
    for value in values:
        path = resolve(root, value)
        key = str(path).lower()
        if key not in seen:
            result.append(path)
            seen.add(key)
    return result


def is_reference_candidate(path: Path) -> bool:
    if not path.is_file() or path.suffix.lower() not in REFERENCE_EXTENSIONS:
        return False
    name = path.name.lower()
    return not any(part in name for part in EXCLUDED_NAME_PARTS)


def path_summary(path: Path) -> dict[str, Any]:
    exists = path.exists()
    candidates = 0
    excluded = 0
    if exists:
        for item in path.rglob("*"):
            if not item.is_file() or item.suffix.lower() not in REFERENCE_EXTENSIONS:
                continue
            if is_reference_candidate(item):
                candidates += 1
            else:
                excluded += 1
    return {
        "path": str(path).replace("\\", "/"),
        "exists": exists,
        "candidateCount": candidates,
        "excludedCount": excluded,
    }


def build_report(root: Path, source: str = "") -> dict[str, Any]:
    rows = [path_summary(path) for path in checked_paths(root, source)]
    total_candidates = sum(int(row["candidateCount"]) for row in rows)
    total_excluded = sum(int(row["excludedCount"]) for row in rows)
    return {
        "status": "ok" if total_candidates > 0 else "warning",
        "message": (
            "Reference corpus is available."
            if total_candidates > 0
            else "No local reference candidates found in the checked folders."
        ),
        "candidateCount": total_candidates,
        "excludedCount": total_excluded,
        "checkedPaths": rows,
        "rule": "Do not claim local-reference-led selection happened when candidateCount is 0.",
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Reference Corpus Health",
        "",
        f"- Status: {report['status'].upper()}",
        f"- Message: {report['message']}",
        f"- Candidate files: {report['candidateCount']}",
        f"- Excluded files: {report['excludedCount']}",
        f"- Rule: {report['rule']}",
        "",
        "## Checked Paths",
        "",
    ]
    for row in report["checkedPaths"]:
        exists = "yes" if row["exists"] else "no"
        lines.append(
            f"- `{row['path']}` | exists: {exists} | candidates: {row['candidateCount']} | excluded: {row['excludedCount']}"
        )
    if report["candidateCount"] == 0:
        lines.extend(
            [
                "",
                "## Required Action",
                "",
                "- Configure `.design-brain/REFERENCE_CORPUS_CONFIG.md`, pass `--source`, or provide a reference image/link.",
                "- Continue only with explicit limitation notes if no local corpus is available.",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    report = build_report(repo_root(), args.source)
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
