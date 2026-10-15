#!/usr/bin/env python
"""Generate a structured Codex Design Brain review report.

This utility does not visually analyze screenshots or UI output by itself.
It creates a repeatable markdown template that Codex can fill after inspecting
the target screen, file, mockup, or design output.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REVIEW_CATEGORIES = [
    "medium fit",
    "hierarchy",
    "spacing",
    "typography",
    "alignment",
    "contrast",
    "CTA visibility",
    "visual consistency",
    "responsiveness",
    "accessibility",
    "marketplace quality",
    "emotional direction",
    "generic risk",
    "originality risk",
    "human craft",
    "product-type completeness",
    "buyer usability",
    "quality-gate failure taxonomy",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Codex Design Brain markdown review report template."
    )
    parser.add_argument("--task", required=True, help="Design task name.")
    parser.add_argument("--target", required=True, help="Target file, screen, URL, or mockup.")
    parser.add_argument("--notes", default="", help="Extra review focus notes.")
    parser.add_argument(
        "--output",
        default="",
        help="Optional output markdown path. Relative paths resolve from the current directory.",
    )
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_text(path: Path, warnings: list[str]) -> str:
    if not path.exists():
        warnings.append(f"Missing Design Brain file: {path}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        warnings.append(f"Could not read {path}: {exc}")
        return ""


def read_preferences(path: Path, warnings: list[str]) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        warnings.append(f"Missing Design Brain file: {path}")
        return {}
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid DESIGN_PREFERENCES.json at {path}: {exc.msg} "
            f"(line {exc.lineno}, column {exc.colno})"
        ) from exc
    except OSError as exc:
        raise RuntimeError(f"Could not read {path}: {exc}") from exc


def bullet_summary(markdown: str, max_items: int = 8) -> list[str]:
    items: list[str] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped)
        if len(items) >= max_items:
            break
    return items


def heading_summary(markdown: str, max_items: int = 8) -> list[str]:
    headings: list[str] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            headings.append(f"- {stripped[3:]}")
        if len(headings) >= max_items:
            break
    return headings


def preference_summary(preferences: dict[str, Any]) -> list[str]:
    weights = preferences.get("weights", {})
    if not isinstance(weights, dict):
        return ["- No valid preference weights found."]

    rows: list[str] = []
    for key, value in sorted(weights.items(), key=lambda item: str(item[0])):
        rows.append(f"- {key}: {value}")
    return rows or ["- No preference weights configured."]


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    return slug[:70] or "design-review"


def resolve_output_path(root: Path, task: str, output: str) -> Path:
    if output:
        output_path = Path(output)
        if not output_path.is_absolute():
            output_path = Path.cwd() / output_path
        return output_path

    reviews_dir = root / ".design-brain" / "reviews"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}-{safe_slug(task)}.md"
    return reviews_dir / filename


def markdown_list(items: list[str], fallback: str) -> str:
    return "\n".join(items) if items else fallback


def build_report(
    task: str,
    target: str,
    notes: str,
    memory: str,
    preferences: dict[str, Any],
    checklist: str,
    patterns: str,
    warnings: list[str],
) -> str:
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z")
    memory_items = bullet_summary(memory)
    pattern_items = heading_summary(patterns)
    checklist_items = bullet_summary(checklist, max_items=4)
    defaults = preferences.get("defaults", {})

    category_rows = "\n".join(
        f"| {category} | /10 | Fill after inspecting the target. |"
        for category in REVIEW_CATEGORIES
    )

    warning_section = ""
    if warnings:
        warning_section = "\n## Warnings\n\n" + "\n".join(f"- {warning}" for warning in warnings) + "\n"

    defaults_section = ""
    if isinstance(defaults, dict) and defaults:
        defaults_section = "\n".join(f"- {key}: {value}" for key, value in sorted(defaults.items()))
    else:
        defaults_section = "- No defaults configured."

    return f"""# Design Brain Review: {task}

## Review Metadata

- Task: {task}
- Target: {target}
- Notes: {notes or "None"}
- Date/time: {now}
- Generated by: `python scripts/design_brain_review.py`

{warning_section}## Important Limitation

This report is a structured review template. The script does not visually analyze screenshots, rendered UI, or design files by itself. Codex should fill the scores and findings after inspecting the target output.

Use `.design-brain/QUALITY_GATE_FAILURE_TAXONOMY.md` for failed gates. Output PASS/FAIL, failure category, evidence, root cause, required action, and whether rebuild, recompose, recolor, rewrite, or source repair is needed.

## Relevant Design Memory Summary

{markdown_list(memory_items, "- No design memory summary available.")}

## Preference Weights Summary

{markdown_list(preference_summary(preferences), "- No preference weights available.")}

## Preference Defaults

{defaults_section}

## Pattern Library Reminders

{markdown_list(pattern_items, "- No pattern library headings available.")}

## Checklist Scale Reminder

{markdown_list(checklist_items, "- Use 1-10 scores where 1 is weak and 10 is marketplace-ready.")}

## Review Scores

| Category | Score | Notes |
| --- | --- | --- |
{category_rows}

## Weakest Areas

- [ ] Area 1:
- [ ] Area 2:
- [ ] Area 3:

## Quality Gate Failure Diagnosis

- PASS/FAIL:
- Failure category:
- Evidence:
- Root cause:
- Required action:
- Needed action type: rebuild / recompose / recolor / rewrite / source repair / none

## Concrete Revision Plan

1. Revision:
2. Revision:
3. Revision:

## Final Improvement Checklist

- [ ] Hierarchy is clear and the primary action is obvious.
- [ ] Spacing rhythm is consistent and intentional.
- [ ] Typography scale is polished and readable.
- [ ] Alignment and composition feel clean.
- [ ] Contrast and accessibility basics are covered.
- [ ] Responsive behavior has been considered.
- [ ] The result avoids generic or auto-generated visual output.
- [ ] Medium fit is correct for website, deck, dashboard, UI kit, brand kit, or preview.
- [ ] Originality risk is checked against reference/order/composition/motif.
- [ ] Human craft is visible through rhythm, restraint, tension, and buyer specificity.
- [ ] Product-type completeness is strong enough for the intended buyer.
- [ ] Marketplace presentation quality is strong enough for review.

## Reflection Lesson Candidate

- Lesson:
- Rule to reuse next time:

## Suggested REFLECTION_LOG.md Entry

Use this only if user feedback exists.

```markdown
### Date

{datetime.now().strftime("%Y-%m-%d")}

### Task

{task}

### User Feedback


### What Went Wrong


### Design Lesson


### Rule To Reuse Next Time


---
```
"""


def main() -> int:
    args = parse_args()
    root = repo_root()
    design_brain = root / ".design-brain"
    reviews_dir = design_brain / "reviews"
    warnings: list[str] = []

    memory_path = design_brain / "DESIGN_MEMORY.md"
    preferences_path = design_brain / "DESIGN_PREFERENCES.json"
    checklist_path = design_brain / "VISUAL_CRITIQUE_CHECKLIST.md"
    patterns_path = design_brain / "PATTERN_LIBRARY.md"
    medium_playbooks_path = design_brain / "MEDIUM_PRODUCT_PLAYBOOKS.md"
    originality_path = design_brain / "ORIGINALITY_SIMILARITY_SCORECARD.md"
    human_craft_path = design_brain / "HUMAN_CRAFT_HEURISTICS.md"

    memory = read_text(memory_path, warnings)
    checklist = read_text(checklist_path, warnings)
    patterns = "\n".join(
        [
            read_text(patterns_path, warnings),
            read_text(medium_playbooks_path, warnings),
            read_text(originality_path, warnings),
            read_text(human_craft_path, warnings),
        ]
    )

    try:
        preferences = read_preferences(preferences_path, warnings)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    output_path = resolve_output_path(root, args.task, args.output)
    try:
        if not args.output:
            reviews_dir.mkdir(parents=True, exist_ok=True)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report = build_report(
            task=args.task,
            target=args.target,
            notes=args.notes,
            memory=memory,
            preferences=preferences,
            checklist=checklist,
            patterns=patterns,
            warnings=warnings,
        )
        output_path.write_text(report, encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: Could not write review report to {output_path}: {exc}", file=sys.stderr)
        return 1

    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    print(f"Design Brain review report created: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
