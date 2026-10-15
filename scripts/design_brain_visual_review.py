#!/usr/bin/env python
"""Generate a structured visual review report from screenshot or URL evidence.

This utility does not capture URLs or visually analyze screenshots by itself.
It organizes visual evidence so Codex can fill the report after inspecting a
screenshot, browser view, or rendered UI.
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
    parser = argparse.ArgumentParser(
        description="Generate a Codex Design Brain visual review report."
    )
    parser.add_argument("--task", required=True, help="Visual review task name.")
    parser.add_argument("--target", required=True, help="Target file, screen, or design surface.")
    parser.add_argument("--screenshot", default="", help="Optional screenshot path.")
    parser.add_argument("--url", default="", help="Optional URL reference.")
    parser.add_argument("--notes", default="", help="Optional visual review notes.")
    parser.add_argument("--output", default="", help="Optional output markdown path.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    return slug[:70] or "visual-review"


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
            warnings.append(
                f"Screenshot format unsupported for dimension detection: {path.suffix or 'unknown'}"
            )
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
    return root / ".design-brain" / "visual-reviews" / f"{timestamp}-{safe_slug(task)}.md"


def build_report(
    task: str,
    target: str,
    screenshot_path: str,
    screenshot_dimensions: str,
    url: str,
    notes: str,
    warnings: list[str],
) -> str:
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z")
    warning_section = ""
    if warnings:
        warning_section = "\n## Warnings\n\n" + "\n".join(f"- {warning}" for warning in warnings) + "\n\n"

    url_note = ""
    if url:
        url_note = (
            "\nThe URL is included as a reference only. This script does not open, "
            "capture, or inspect the URL by itself.\n"
        )

    return f"""# Visual Design Review: {task}

## Review Metadata

- Task: {task}
- Target: {target}
- Screenshot path: {screenshot_path}
- Screenshot dimensions: {screenshot_dimensions}
- URL: {url or "None"}
- Notes: {notes or "None"}
- Date/time: {now}
- Generated by: `python scripts/design_brain_visual_review.py`

{warning_section}## Important Limitation

This report organizes visual evidence. The script does not capture URLs or visually analyze screenshots by itself. Codex should fill this report only after inspecting a screenshot, browser view, or rendered UI.
{url_note}
## Source-Bound Inspection Evidence

Follow `.design-brain/VISUAL_INSPECTION_PROTOCOL.md`. This Markdown template is not a machine inspection receipt and never proves that pixels were viewed.

- Current artifact path and SHA-256:
- Complete frame/page/slide/state inventory, render method and source hashes:
- Machine manifest path (`visual-inspection.json`) and verification result:
- Named questions: critical risks, small text, ambiguous detail, alignment, completeness:
- Actual host image-view calls: overview, relevant detail crops, return to whole-frame context:
- Coordinate space and source boxes for each crop:
- Main observations versus Engineer observations (independent, not copied verdicts):
- Observed facts versus inference; unresolved questions and missing source detail:
- Repair, fresh render and reinspection evidence:
- Main decision, reason and scope; any limitation must remain visible:

## Visual Inspection Checklist

- [ ] Screenshot or rendered output was actually inspected.
- [ ] Above-the-fold hierarchy is clear.
- [ ] Primary CTA is visible and visually distinct.
- [ ] Spacing rhythm feels intentional.
- [ ] Typography is readable and well-scaled.
- [ ] Color and contrast support accessibility.
- [ ] Responsive behavior is checked when evidence is available.
- [ ] Medium fit is visible: website, deck, dashboard, UI kit, brand kit, portfolio, or preview.
- [ ] Generic risk is checked: repeated cards, random decoration, one-note palette, or default template look.
- [ ] Originality risk is checked against reference order, composition, motif, and preview staging.
- [ ] Human craft is visible through hierarchy, rhythm, restraint, and buyer-specific decisions.
- [ ] Product-type completeness is visible in the rendered output.
- [ ] Marketplace presentation quality is strong.
- [ ] For PPTX/deck work, each slide frame was inspected individually at normal size, not only as a contact sheet.
- [ ] For PPTX/deck work, overlap, near-collision, tangent spacing, title/content clearance, footer clearance, and safe margins were checked.

## Above-The-Fold Review

- Observation:
- Risk:
- Revision:

## Hierarchy Review

- Observation:
- Risk:
- Revision:

## Spacing Review

- Observation:
- Risk:
- Revision:

## Typography Review

- Observation:
- Risk:
- Revision:

## CTA Review

- Observation:
- Risk:
- Revision:

## Color/Contrast Review

- Observation:
- Risk:
- Revision:

## Responsiveness Review

- Observation:
- Risk:
- Revision:

## Marketplace Presentation Review

- Observation:
- Risk:
- Revision:

## Medium Fit Review

- Observation:
- Risk:
- Revision:

## Originality / Generic Risk Review

- Observation:
- Risk:
- Revision:

## Human Craft Review

- Observation:
- Risk:
- Revision:

## Product-Type Completeness Review

- Observation:
- Risk:
- Revision:

## PPTX Frame Precision Review

- Observation:
- Collision or near-collision risk:
- Title/content clearance:
- Safe-margin and footer clearance:
- Baseline/alignment drift:
- Placeholder stress risk:
- Revision:

## Problems Observed

- [ ] Problem 1:
- [ ] Problem 2:
- [ ] Problem 3:

## Concrete Visual Revision Plan

1. Revision:
2. Revision:
3. Revision:

## Before/After Comparison Notes

- Before:
- After:
- Remaining risk:

## Reflection Lesson Candidate

- Lesson:
- Rule to reuse next time:
"""


def main() -> int:
    args = parse_args()
    root = repo_root()
    warnings: list[str] = []

    if not args.screenshot and not args.url:
        warnings.append("Neither --screenshot nor --url was provided; visual evidence is missing.")

    screenshot_path, dimensions = screenshot_info(root, args.screenshot, warnings)
    output_path = resolve_output_path(root, args.task, args.output)

    report = build_report(
        task=args.task,
        target=args.target,
        screenshot_path=screenshot_path,
        screenshot_dimensions=dimensions,
        url=args.url,
        notes=args.notes,
        warnings=warnings,
    )

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: Could not write visual review report to {output_path}: {exc}", file=sys.stderr)
        return 1

    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    print(f"Visual review report created: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
