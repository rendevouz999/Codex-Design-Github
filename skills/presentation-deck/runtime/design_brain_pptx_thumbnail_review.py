#!/usr/bin/env python
"""Review available PPTX slide thumbnails for readability risks."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a thumbnail-readability review checklist.")
    parser.add_argument("--thumbnail-dir", default="", help="Directory containing rendered slide thumbnails.")
    parser.add_argument("--notes", default="", help="Optional observation notes.")
    parser.add_argument("--output", default="", help="Optional report path.")
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def collect_images(path_value: str) -> tuple[str, list[str], str]:
    if not path_value:
        return "not provided", [], "No thumbnail directory was provided."
    path = Path(path_value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    if not path.exists():
        return str(path.resolve()), [], "Thumbnail directory does not exist."
    images = sorted(str(item.resolve()) for item in path.iterdir() if item.is_file() and item.suffix.lower() in IMAGE_SUFFIXES)
    return str(path.resolve()), images, ""


def build_review(args: argparse.Namespace) -> dict[str, Any]:
    directory, images, error = collect_images(args.thumbnail_dir)
    findings: list[dict[str, str]] = []
    if error:
        findings.append(
            {
                "severity": "WARN",
                "area": "input",
                "message": error,
                "requiredFix": "Render slide thumbnails first, then rerun this review with --thumbnail-dir.",
            }
        )
    elif not images:
        findings.append(
            {
                "severity": "WARN",
                "area": "input",
                "message": "No thumbnail images were found.",
                "requiredFix": "Export slide thumbnails as PNG/JPG/WebP before visual review.",
            }
        )

    return {
        "generatedAt": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z"),
        "thumbnailDir": directory,
        "thumbnailCount": len(images),
        "thumbnails": images,
        "notes": args.notes,
        "verdict": "NEEDS_VISUAL_REVIEW" if findings else "READY_FOR_VISUAL_REVIEW",
        "findings": findings,
        "checklist": [
            "Can the title be read at 160px wide?",
            "Is there one dominant idea or number per slide?",
            "Do section dividers remain distinct from content slides?",
            "Are charts/tables readable without zooming?",
            "Do footer/page numbers stay consistent and unobtrusive?",
            "Do slide crops preserve faces, product screenshots, and key labels?",
            "Does the deck form a coherent rhythm when scanned as thumbnails?",
        ],
    }


def markdown_report(data: dict[str, Any]) -> str:
    thumbnails = "\n".join(f"- {item}" for item in data["thumbnails"]) or "- None"
    findings = []
    for finding in data["findings"]:
        findings.extend(
            [
                f"### {finding['severity']} - {finding['area']}",
                "",
                f"- Issue: {finding['message']}",
                f"- Required fix: {finding['requiredFix']}",
                "",
            ]
        )
    if not findings:
        findings = ["- No input findings. Inspect the thumbnails visually against the checklist.", ""]
    return "\n".join(
        [
            "# PPTX Thumbnail Review",
            "",
            f"- Generated: {data['generatedAt']}",
            f"- Thumbnail directory: {data['thumbnailDir']}",
            f"- Thumbnail count: {data['thumbnailCount']}",
            f"- Verdict: {data['verdict']}",
            f"- Notes: {data['notes'] or 'None'}",
            "",
            "## Thumbnails",
            "",
            thumbnails,
            "",
            "## Findings",
            "",
            *findings,
            "## Thumbnail Readability Checklist",
            "",
            "\n".join(f"- {item}" for item in data["checklist"]),
            "",
        ]
    )


def output_path(args: argparse.Namespace) -> Path:
    if args.output:
        path = Path(args.output).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.resolve()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return repo_root() / ".design-brain" / "reviews" / f"{stamp}-pptx-thumbnail-review.md"


def main() -> int:
    args = parse_args()
    data = build_review(args)
    text = json.dumps(data, indent=2, ensure_ascii=False) if args.json else markdown_report(data)
    if args.dry_run:
        print(text)
        return 0
    path = output_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"PPTX thumbnail review written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
