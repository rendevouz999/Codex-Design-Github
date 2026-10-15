#!/usr/bin/env python
"""Select TypeUI-derived style packs for template product work."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from design_brain_modules import explicit_web_deck_intent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a template style decision report.")
    parser.add_argument("--template-type", required=True, help="Template product type.")
    parser.add_argument("--niche", default="", help="Niche or marketplace category.")
    parser.add_argument("--visual-mood", default="", help="Desired visual mood.")
    parser.add_argument("--target-buyer", default="", help="Target buyer.")
    parser.add_argument("--output", default="", help="Optional output markdown path.")
    parser.add_argument("--dry-run", action="store_true", help="Print report without saving it.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def now_human() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z")


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "style-decision"


def contains_any(text: str, keywords: list[str]) -> bool:
    value = text.lower()
    return any(keyword in value for keyword in keywords)


PRESENTATION_KEYWORDS = [
    "powerpoint",
    "presentation",
    "pitch deck",
    "deck",
    "slides",
    "google slide",
    "keynote",
    "ppt",
    "pptx",
]


def load_packs(root: Path) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    path = root / ".design-brain" / "TEMPLATE_STYLE_PACKS.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        warnings.append(f"Missing style pack file: {path}")
        data = {"packs": {}, "conflict_rules": []}
    except json.JSONDecodeError as exc:
        warnings.append(f"Invalid style pack JSON: {exc.msg} at line {exc.lineno}")
        data = {"packs": {}, "conflict_rules": []}
    return data, warnings


def load_extracted(root: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    extracted_dir = root / ".design-brain" / "typeui-skills" / "extracted"
    warnings: list[str] = []
    skills: dict[str, dict[str, Any]] = {}
    if not extracted_dir.exists():
        warnings.append(f"Extracted TypeUI directory missing: {extracted_dir}")
        return skills, warnings
    for path in sorted(extracted_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            warnings.append(f"Invalid extracted JSON {path}: {exc.msg} at line {exc.lineno}")
            continue
        slug = str(data.get("slug") or path.stem)
        skills[slug] = data
    if not skills:
        warnings.append("No extracted TypeUI skill JSON files found. Run scripts/design_brain_typeui_ingest.py.")
    return skills, warnings


def recommend_packs(template_type: str, niche: str, buyer: str, mood: str) -> list[str]:
    text = f"{template_type} {niche} {buyer} {mood}".lower()
    selected: list[str] = []
    if explicit_web_deck_intent(text):
        selected.append("Web Deck Pack")
    if not selected and contains_any(text, PRESENTATION_KEYWORDS):
        selected.append("Presentation Deck Pack")
    if contains_any(text, ["wedding", "event", "beauty", "boutique", "luxury"]):
        selected.append("Elegant Event Pack")
    if contains_any(text, ["dashboard", "admin", "analytics", "crm", "platform", "internal", "hiring", "freelancer"]):
        selected.append("Dashboard Product Pack")
    if contains_any(text, ["ui kit", "design system", "component library", "components", "variants", "states"]):
        selected.append("UI Kit System Pack")
    if contains_any(text, ["brand kit", "branding", "identity", "brand guideline", "logo", "stationery"]):
        selected.append("Brand Kit Pack")
    if contains_any(text, ["repair", "service", "booking", "local", "professional", "corporate", "hiring", "freelancer"]):
        selected.append("Service Business Pack")
    if contains_any(text, ["editorial", "publishing", "publication", "magazine", "portfolio", "blog"]):
        selected.append("Editorial Publishing Pack")
    if contains_any(text, ["preview", "cover", "mockup", "marketplace"]):
        selected.append("Marketplace Preview Pack")
    if not selected and contains_any(text, ["landing", "website", "saas", "homepage"]):
        selected.append("Landing Page Pack")
    if not selected:
        selected.append("Landing Page Pack")
    return selected[:2]


def skills_for_pack_names(packs: dict[str, Any], pack_names: list[str]) -> list[str]:
    skills: list[str] = []
    pack_map = packs.get("packs", {})
    for pack_name in pack_names:
        for skill in pack_map.get(pack_name, {}).get("skills", []):
            if skill not in skills:
                skills.append(skill)
    return skills


def contribution(skill: str, extracted: dict[str, dict[str, Any]]) -> str:
    data = extracted.get(skill)
    if not data:
        return "Style reference available in pack definition; extracted JSON is missing."
    strengths = ", ".join(data.get("template_strengths", [])[:4])
    notes = data.get("marketplace_template_notes", "")
    return f"{strengths}. {notes}".strip()


def structure_implications(skills: list[str]) -> list[str]:
    items: list[str] = []
    if "storytelling" in skills:
        items.append("Use a clear narrative section flow from promise to proof to conversion.")
        items.append("For presentation decks, convert narrative into slide roles rather than long scroll sections.")
    if "bento" in skills:
        items.append("Use modular card grids for feature blocks, breakdowns, and overview panels.")
    if "dashboard" in skills:
        items.append("Prioritize KPI hierarchy, navigation, tables, charts, and state coverage.")
    if "perspective" in skills:
        items.append("Use perspective mainly for cover, overview, and mockup presentation.")
    if "spacious" in skills or "clean" in skills:
        items.append("Keep whitespace and legibility as non-negotiable structure constraints.")
    return items or ["Keep structure clear, reusable, and easy to adapt."]


def preview_direction(skills: list[str]) -> list[str]:
    items = ["Create a cover that states the product category and shows the strongest preview."]
    if "storytelling" in skills and ("professional" in skills or "refined" in skills):
        items.append("For decks, show flat slide contact sheets and role breakdowns before dramatic mockups.")
    if "perspective" in skills:
        items.append("Add a perspective mockup only if the UI remains readable.")
    if "bento" in skills:
        items.append("Use a bento overview for section breakdowns and included screens.")
    if "dashboard" in skills:
        items.append("Show dashboards flat and readable before any dramatic presentation.")
    if "elegant" in skills or "refined" in skills:
        items.append("Use typography, spacing, and calm composition to sell premium niche value.")
    return items


def quality_criteria() -> list[str]:
    return [
        "Medium/product-type fit is confirmed before style decisions dominate.",
        "Template type, niche, buyer, and marketplace category are obvious.",
        "Selected style pack fits the buyer and does not conflict with the product type.",
        "Editable sections, placeholders, and reusable components are clear.",
        "Preview and cover direction can sell the product without hiding the UI.",
        "Originality risk and human craft are checked for reference-based or batch work.",
        "The design avoids generic AI output, random decoration, and mismatched style moods.",
    ]


def markdown_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def build_report(args: argparse.Namespace) -> str:
    root = repo_root()
    packs, pack_warnings = load_packs(root)
    extracted, extracted_warnings = load_extracted(root)
    warnings = pack_warnings + extracted_warnings
    pack_names = recommend_packs(args.template_type, args.niche, args.target_buyer, args.visual_mood)
    skills = skills_for_pack_names(packs, pack_names)
    conflicts = packs.get("conflict_rules", [])
    warning_block = ""
    if warnings:
        warning_block = "\n## Warnings\n\n" + markdown_list(warnings) + "\n"

    contributions = [f"**{skill}**: {contribution(skill, extracted)}" for skill in skills]

    return f"""# Template Style Decision Report

- Date/time: {now_human()}
- Template type: {args.template_type}
- Niche: {args.niche or "Not specified"}
- Target buyer: {args.target_buyer or "Not specified"}
- Visual mood: {args.visual_mood or "Not specified"}

{warning_block}## Recommended Style Pack

{markdown_list(pack_names)}

## Selected Skills

{markdown_list(skills)}

## Why Selected

{markdown_list(contributions)}

## Conflicting Styles To Avoid

{markdown_list(conflicts)}

## Template Structure Implications

{markdown_list(structure_implications(skills))}

## Preview Direction

{markdown_list(preview_direction(skills))}

## Marketplace Quality Criteria

{markdown_list(quality_criteria())}

## Next Action

- Run `python scripts/design_brain_medium_playbook.py --task "{args.template_type} {args.niche}" --template-type "{args.template_type}" --niche "{args.niche}" --visual-mood "{args.visual_mood}" --target-buyer "{args.target_buyer}"`.
- Convert the selected skills into concrete design constraints before designing.
- Do not activate all TypeUI skills at once.
- Run `python scripts/design_brain_template_plan.py --template-type "{args.template_type}" --niche "{args.niche}" --visual-mood "{args.visual_mood}" --target-buyer "{args.target_buyer}"`.
"""


def output_path(args: argparse.Namespace) -> Path:
    if args.output:
        path = Path(args.output).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.resolve()
    return repo_root() / ".design-brain" / "template-plans" / f"{now_stamp()}-{slugify(args.template_type)}-style-decision.md"


def main() -> int:
    args = parse_args()
    report = build_report(args)
    if args.dry_run:
        print(report)
        return 0
    path = output_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8", newline="\n")
    print(f"Template style decision report saved: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
