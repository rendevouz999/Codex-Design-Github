#!/usr/bin/env python
"""Create a real-project pilot report for Codex Design Brain.

The pilot report is planning and evidence scaffolding only. It never edits the
selected project files, never captures URLs, and never visually analyzes
screenshots by itself.
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


DESIGN_BRAIN_REQUIRED_FILES = [
    "AGENTS.md",
    ".design-brain/DESIGN_MEMORY.md",
    ".design-brain/DESIGN_PREFERENCES.json",
    ".agents/skills/design-critic/SKILL.md",
    "scripts/design_brain_status.py",
    "scripts/design_brain_review.py",
    "scripts/design_brain_visual_review.py",
    "scripts/design_brain_reflect.py",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Design Brain real-project pilot report.")
    parser.add_argument(
        "--project-root",
        default="",
        help="Project root to inspect. Defaults to the Design Brain repo where this script lives.",
    )
    parser.add_argument("--task", required=True, help="Design/UI task name.")
    parser.add_argument("--target", default="", help="Target file, route, screen, or component.")
    parser.add_argument("--notes", default="", help="Additional pilot notes.")
    parser.add_argument("--screenshot", default="", help="Optional screenshot path used as visual evidence.")
    parser.add_argument("--url", default="", help="Optional URL reference. The script does not open or capture it.")
    parser.add_argument("--output", default="", help="Optional markdown output path.")
    parser.add_argument("--dry-run", action="store_true", help="Print report without saving it.")
    return parser.parse_args()


def design_brain_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_project_root(value: str) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    return design_brain_root()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "pilot"


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def now_human() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z")


def check_installation(project_root: Path) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    present: list[str] = []
    if not project_root.exists():
        return DESIGN_BRAIN_REQUIRED_FILES[:], []

    for relative in DESIGN_BRAIN_REQUIRED_FILES:
        path = project_root / relative
        if path.exists():
            present.append(relative)
        else:
            missing.append(relative)
    return missing, present


def resolve_reference_path(path_value: str, base: Path) -> Path:
    path = Path(path_value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def warning_lines(project_root: Path, screenshot: str, url: str, missing: list[str]) -> list[str]:
    warnings: list[str] = []
    if not project_root.exists():
        warnings.append(f"Project root does not exist: {project_root}")
    if not screenshot and not url:
        warnings.append("No screenshot or URL was provided. Add visual evidence before judging visual quality.")
    if screenshot:
        screenshot_path = resolve_reference_path(screenshot, project_root if project_root.exists() else Path.cwd())
        if not screenshot_path.exists():
            warnings.append(f"Screenshot path does not exist: {screenshot_path}")
    if missing:
        warnings.append("Design Brain is missing required files in the selected project root.")
    return warnings


def command_quote(value: str | Path) -> str:
    return f'"{value}"'


def build_report(args: argparse.Namespace, project_root: Path, missing: list[str], present: list[str]) -> str:
    installed = not missing and project_root.exists()
    target = args.target or "Not specified"
    notes = args.notes or "None"
    screenshot = args.screenshot or "None"
    url = args.url or "None"
    warnings = warning_lines(project_root, args.screenshot, args.url, missing)

    if installed:
        install_recommendation = (
            f"Run status before implementation: `python scripts/design_brain_status.py --root {command_quote(project_root)}`"
        )
        next_action = "Inspect the target, capture or open visual evidence, then create review and visual review reports before finalizing UI."
    else:
        install_recommendation = (
            f"Design Brain is not fully installed. Preview install first: "
            f"`python scripts/install_design_brain.py --target {command_quote(project_root)} --dry-run`"
        )
        next_action = "Do not claim the project is ready. Install or repair missing Design Brain files first."

    review_target = args.target or "TARGET_FILE_OR_SCREEN"
    visual_arg = ""
    if args.screenshot:
        visual_arg = f" --screenshot {command_quote(args.screenshot)}"
    elif args.url:
        visual_arg = f" --url {command_quote(args.url)}"
    else:
        visual_arg = ' --screenshot ".design-brain/screenshots/SCREENSHOT.png"'

    lines = [
        f"# Pilot Report: {args.task}",
        "",
        f"- Date/time: {now_human()}",
        f"- Task: {args.task}",
        f"- Project root: {project_root}",
        f"- Target file/screen: {target}",
        f"- URL: {url}",
        f"- Screenshot: {screenshot}",
        f"- Notes: {notes}",
        "",
        "## Report Storage Note",
        "- The pilot script does not edit the selected project files.",
        f"- If `--output` is not provided, the report is saved in the Design Brain repo where this script lives: `{design_brain_root() / '.design-brain' / 'pilots'}`.",
        "- To save inside a target project, pass an explicit `--output` path.",
        "- Saving a report inside an external project should be intentional.",
        "",
        "## Warnings",
    ]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Design Brain Installation Status",
            f"- Ready: {'yes' if installed else 'no'}",
            f"- Present required files: {len(present)}",
            f"- Missing required files: {len(missing)}",
            "",
            "### Missing Files",
        ]
    )
    if missing:
        lines.extend(f"- {item}" for item in missing)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Project Context Checklist",
            "- Identify framework, routing model, styling system, and component library.",
            "- Identify the target screen, owner file, supporting components, and asset dependencies.",
            "- Identify current visual problem, product type, audience, primary CTA, and constraints.",
            "- Check existing spacing, typography, color, radius, shadow, and interaction conventions.",
            "- Confirm whether screenshot, URL, or rendered output is available for visual review.",
            "",
            "## Suggested Project Inspection Steps",
            "- Read the target file and nearby components.",
            "- Check global styles, design tokens, layout wrappers, and reusable UI primitives.",
            "- Inspect existing responsive behavior and breakpoints before changing layout.",
            "- Look for current screenshots, previews, or local dev instructions.",
            "- Keep edits scoped to the requested UI/design task.",
            "",
            "## Suggested Baseline Screenshot Plan",
            "- Capture or provide a desktop screenshot before changes.",
            "- Capture or provide a mobile screenshot before changes for responsive risk.",
            "- Save screenshots under `.design-brain/screenshots/` when working inside a Design Brain-enabled project.",
            "- This script does not inspect screenshots visually. Visual inspection must happen manually or by Codex after seeing actual screenshot/browser/rendered evidence.",
            "",
            "## Suggested First Implementation Plan",
            "- Establish one clear focal point and primary CTA.",
            "- Improve hierarchy, spacing rhythm, typography scale, alignment, and contrast.",
            "- Remove clutter and generic decorative elements that do not support the concept.",
            "- Preserve project conventions and avoid broad refactors.",
            "- Verify responsive behavior after changes.",
            "",
            "## Suggested Review Command",
            "```bash",
            f"python scripts/design_brain_review.py --task {command_quote(args.task)} --target {command_quote(review_target)} --notes {command_quote(args.notes or 'Pilot review for hierarchy, spacing, CTA clarity, responsiveness, and marketplace quality')}",
            "```",
            "",
            "## Suggested Visual Review Command",
            "```bash",
            f"python scripts/design_brain_visual_review.py --task {command_quote(args.task)} --target {command_quote(review_target)}{visual_arg} --notes {command_quote(args.notes or 'Inspect hierarchy, spacing, CTA clarity, and marketplace quality')}",
            "```",
            "",
            "## Suggested Reflection Command Template",
            "```bash",
            f"python scripts/design_brain_reflect.py --task {command_quote(args.task)} --feedback {command_quote('USER_FEEDBACK')} --went-wrong {command_quote('WHAT_WENT_WRONG')} --lesson {command_quote('REUSABLE_DESIGN_LESSON')} --rule {command_quote('RULE_TO_REUSE_NEXT_TIME')}",
            "```",
            "",
            "## Acceptance Criteria",
            "- Design Brain status is checked for the project.",
            "- First draft is not treated as final.",
            "- Review report is created and filled after inspection.",
            "- Visual review report is created when screenshot, URL, browser, or rendered UI evidence exists.",
            "- Concrete revisions are applied after critique when code/design edits are in scope.",
            "- Useful user feedback is converted into a controlled reflection lesson.",
            "",
            "## Risks",
            "- Missing Design Brain files can make the workflow inconsistent.",
            "- Judging visual quality without screenshot, URL, browser, or rendered evidence can produce false confidence.",
            "- Overwriting project files without explicit user intent can damage unrelated work.",
            "- One-off feedback should not be promoted into stable memory.",
            "",
            "## Next Action",
            f"- {install_recommendation}",
            f"- {next_action}",
            "",
        ]
    )
    if args.url:
        lines.append("Note: URL was recorded as a reference only. This script does not open or capture URLs.")
        lines.append("")
    if args.screenshot:
        lines.append("Note: Screenshot path was recorded as evidence only. This script does not analyze image contents.")
        lines.append("")
    return "\n".join(lines)


def output_path(args: argparse.Namespace) -> Path:
    if args.output:
        return Path(args.output).expanduser().resolve()
    return design_brain_root() / ".design-brain" / "pilots" / f"{now_stamp()}-{slugify(args.task)}.md"


def main() -> int:
    args = parse_args()
    project_root = resolve_project_root(args.project_root)
    missing, present = check_installation(project_root)
    report = build_report(args, project_root, missing, present)

    if args.dry_run:
        print(report)
        return 0

    path = output_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8", newline="\n")
    print(f"Pilot report saved: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
