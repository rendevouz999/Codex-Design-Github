#!/usr/bin/env python
"""Create a per-slide precision audit report for PPTX/Figma deck templates.

The script does not visually analyze screenshots by itself. It creates a
structured review surface so Codex can inspect each slide frame manually and
avoid accepting "premium-looking" decks with local overlap, tangent spacing,
or title/content clearance errors.
"""

from __future__ import annotations

import argparse
import re
import struct
import sys
from datetime import datetime
from pathlib import Path


JPEG_SOF_MARKERS = {
    0xC0,
    0xC1,
    0xC2,
    0xC3,
    0xC5,
    0xC6,
    0xC7,
    0xC9,
    0xCA,
    0xCB,
    0xCD,
    0xCE,
    0xCF,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate PPTX frame precision review report.")
    parser.add_argument("--task", required=True, help="Review task name.")
    parser.add_argument("--target", required=True, help="Deck, Figma page, or slide frame target.")
    parser.add_argument("--screenshot", default="", help="Optional contact sheet or slide screenshot path.")
    parser.add_argument("--slide-count", type=int, default=0, help="Number of slides to list.")
    parser.add_argument(
        "--slide-names",
        default="",
        help="Optional pipe-separated slide names. Overrides generated slide labels.",
    )
    parser.add_argument("--notes", default="", help="Optional manual observations or context.")
    parser.add_argument("--output", default="", help="Optional output markdown path.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    return slug[:72] or "pptx-frame-precision-review"


def resolve_path(root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return root / path


def display_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def png_dimensions(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", header[16:24])
    return int(width), int(height)


def jpeg_dimensions(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as handle:
        if handle.read(2) != b"\xff\xd8":
            return None
        while True:
            marker_start = handle.read(1)
            if not marker_start:
                return None
            if marker_start != b"\xff":
                continue

            marker_byte = handle.read(1)
            while marker_byte == b"\xff":
                marker_byte = handle.read(1)
            if not marker_byte:
                return None

            marker = marker_byte[0]
            if marker in (0xD8, 0xD9):
                continue
            if marker == 0xDA:
                return None

            length_bytes = handle.read(2)
            if len(length_bytes) != 2:
                return None
            segment_length = struct.unpack(">H", length_bytes)[0]
            if segment_length < 2:
                return None

            if marker in JPEG_SOF_MARKERS:
                data = handle.read(segment_length - 2)
                if len(data) < 5:
                    return None
                height, width = struct.unpack(">HH", data[1:5])
                return int(width), int(height)

            handle.seek(segment_length - 2, 1)


def detect_dimensions(path: Path, warnings: list[str]) -> str:
    suffix = path.suffix.lower()
    try:
        if suffix == ".png":
            dimensions = png_dimensions(path)
        elif suffix in {".jpg", ".jpeg"}:
            dimensions = jpeg_dimensions(path)
        else:
            warnings.append(f"Screenshot format unsupported for dimension detection: {path.suffix or 'unknown'}")
            return "unknown"
    except OSError as exc:
        warnings.append(f"Could not read screenshot dimensions: {exc}")
        return "unknown"
    except struct.error:
        warnings.append("Screenshot dimensions could not be parsed from file header.")
        return "unknown"

    if not dimensions:
        warnings.append("Screenshot dimensions could not be detected from file header.")
        return "unknown"
    return f"{dimensions[0]} x {dimensions[1]}"


def screenshot_info(root: Path, screenshot: str, warnings: list[str]) -> tuple[str, str]:
    if not screenshot:
        return "None", "unknown"
    path = resolve_path(root, screenshot)
    if not path.exists():
        warnings.append(f"Screenshot path missing: {path}")
        return display_path(root, path), "unknown"
    return display_path(root, path), detect_dimensions(path, warnings)


def resolve_output_path(root: Path, task: str, output: str) -> Path:
    if output:
        path = Path(output)
        if not path.is_absolute():
            path = Path.cwd() / path
        return path
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return root / ".design-brain" / "pptx-precision-reviews" / f"{timestamp}-{safe_slug(task)}.md"


def slide_labels(slide_count: int, slide_names: str) -> list[str]:
    explicit = [item.strip() for item in slide_names.split("|") if item.strip()]
    if explicit:
        return explicit
    count = max(slide_count, 1)
    return [f"Slide {index:02d}" for index in range(1, count + 1)]


def build_slide_table(labels: list[str]) -> str:
    rows = [
        "| Slide | Status | Collision / Near-Collision | Title Clearance | Safe Margin / Footer | Alignment / Baseline | Placeholder Stress | Action |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for label in labels:
        rows.append(f"| {label} | Review |  |  |  |  |  |  |")
    return "\n".join(rows)


def build_report(
    task: str,
    target: str,
    screenshot_path: str,
    screenshot_dimensions: str,
    labels: list[str],
    notes: str,
    warnings: list[str],
) -> str:
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z")
    warning_section = ""
    if warnings:
        warning_section = "\n## Warnings\n\n" + "\n".join(f"- {warning}" for warning in warnings) + "\n"

    return f"""# PPTX Frame Precision Review: {task}

## Review Metadata

- Task: {task}
- Target: {target}
- Screenshot path: {screenshot_path}
- Screenshot dimensions: {screenshot_dimensions}
- Slide count listed: {len(labels)}
- Notes: {notes or "None"}
- Date/time: {now}
- Generated by: `python skills/presentation-deck/runtime/design_brain_pptx_frame_precision_review.py`

{warning_section}
## Important Limitation

This report is a structured precision-audit surface. The script does not visually analyze screenshots by itself. Codex must inspect every slide frame manually before marking a row as pass.

## Precision Gate

- [ ] Every slide was inspected at normal size.
- [ ] Every slide was inspected at thumbnail size.
- [ ] No slide was accepted only because the contact sheet looked organized.
- [ ] Figma-to-PPTX export fit was checked: one top-level frame becomes one slide and the frame fills the PowerPoint slide area.
- [ ] Export canvas size was validated, not only aspect ratio; use exact 1920x1080 frames when smaller 16:9 frames export undersized.
- [ ] Headline-to-content clearance was checked after multi-line titles.
- [ ] Element collision and near-collision were checked with imaginary bounding boxes.
- [ ] Tangent spacing was checked where edges almost touch or almost align.
- [ ] Safe margins, footer, page number, and tiny labels were checked.
- [ ] Baseline drift and column relationship were checked.
- [ ] Placeholder stress was considered for longer titles, wrapped bullets, and image swaps.

## Per-Slide Audit Table

{build_slide_table(labels)}

## Highest-Risk Slide Notes

- Slide:
- Observed issue:
- Why it matters:
- Required fix:

## Example Failure To Catch

If a large multi-line headline descends too close to the first card or a right-side chart panel begins at a height that visually crashes into the headline, mark the slide as `Fix`. This is a placement issue even when layers do not mathematically overlap.

## Final Decision

- Overall status:
- Slides requiring fix:
- Remaining risk:
- Recheck needed:
"""


def main() -> int:
    args = parse_args()
    root = repo_root()
    warnings: list[str] = []
    if not args.screenshot:
        warnings.append("No screenshot was provided; use this as a manual per-slide audit template.")

    labels = slide_labels(args.slide_count, args.slide_names)
    screenshot_path, dimensions = screenshot_info(root, args.screenshot, warnings)
    output_path = resolve_output_path(root, args.task, args.output)
    report = build_report(
        task=args.task,
        target=args.target,
        screenshot_path=screenshot_path,
        screenshot_dimensions=dimensions,
        labels=labels,
        notes=args.notes,
        warnings=warnings,
    )

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: Could not write precision review report to {output_path}: {exc}", file=sys.stderr)
        return 1

    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    print(f"PPTX frame precision review created: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
