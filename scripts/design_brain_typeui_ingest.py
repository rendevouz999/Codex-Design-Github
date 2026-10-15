#!/usr/bin/env python
"""Normalize TypeUI DESIGN.md files and extract structured JSON rules."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any


EXPECTED_SKILLS = [
    "bento",
    "clean",
    "dashboard",
    "elegant",
    "perspective",
    "premium",
    "professional",
    "refined",
    "spacious",
    "storytelling",
]

DETERMINISTIC_RULES = {
    "bento": {
        "template_strengths": ["modular grids", "card systems", "scannable sections", "feature blocks", "overview panels"],
        "best_for_template_types": ["landing page feature grids", "SaaS sections", "marketplace previews", "section breakdowns", "dashboard cards"],
        "avoid_when": ["single-column editorial pages where modular cards would feel forced"],
        "marketplace_template_notes": "Useful for product previews, section overviews, and reusable card-based template sections.",
    },
    "clean": {
        "template_strengths": ["simplicity", "whitespace", "legibility", "limited palette", "reduced clutter"],
        "best_for_template_types": ["service websites", "documentation", "professional landing pages", "UI kits", "general template bases"],
        "avoid_when": ["highly expressive campaign pages needing strong visual drama"],
        "marketplace_template_notes": "Safe foundation for editable templates and broad buyer appeal.",
    },
    "dashboard": {
        "template_strengths": ["data hierarchy", "dark UI", "modular panels", "analytics cards", "productivity surfaces"],
        "best_for_template_types": ["SaaS dashboards", "admin panels", "analytics products", "platform templates", "internal tools"],
        "avoid_when": ["wedding, cafe, editorial, or soft lifestyle templates"],
        "marketplace_template_notes": "Use for dashboard products and data-heavy template previews.",
    },
    "elegant": {
        "template_strengths": ["refined typography", "graceful layout", "sophistication", "delicate visual mood"],
        "best_for_template_types": ["wedding", "event", "beauty", "boutique", "luxury services", "editorial templates"],
        "avoid_when": ["heavy enterprise dashboards or technical admin tools"],
        "marketplace_template_notes": "Strong for premium niche templates that need calm luxury and polished typography.",
    },
    "perspective": {
        "template_strengths": ["spatial depth", "isometric/floating layouts", "layered presentation", "3D-like overview"],
        "best_for_template_types": ["marketplace covers", "perspective mockup previews", "design overviews", "product showcases"],
        "avoid_when": ["simple content pages where depth would distract from usability"],
        "marketplace_template_notes": "Strongest as preview/presentation layer rather than default UI style.",
    },
    "premium": {
        "template_strengths": ["polished visual language", "precise spacing", "modern typography", "Apple-like restraint"],
        "best_for_template_types": ["premium SaaS", "agency templates", "product landing pages", "high-end marketplace templates"],
        "avoid_when": ["playful novelty themes where premium restraint would weaken the concept"],
        "marketplace_template_notes": "Core quality layer for sellable, polished, high-value template products.",
    },
    "professional": {
        "template_strengths": ["business-ready structure", "trustworthy identity", "structured layout", "modern typography"],
        "best_for_template_types": ["B2B", "local service", "hiring", "repair", "corporate", "professional service templates"],
        "avoid_when": ["playful experimental art direction or highly editorial mood"],
        "marketplace_template_notes": "Good default for practical commercial templates with clear buyer use cases.",
    },
    "refined": {
        "template_strengths": ["curated restraint", "elegant serif typography", "understated sophistication"],
        "best_for_template_types": ["editorial", "portfolio", "luxury", "publication", "boutique brand templates"],
        "avoid_when": ["dense dashboards or highly utilitarian enterprise layouts"],
        "marketplace_template_notes": "Useful for templates that need taste, typography, and high-end calm.",
    },
    "spacious": {
        "template_strengths": ["generous whitespace", "consistent padding", "breathable composition", "readable layouts"],
        "best_for_template_types": ["premium landing pages", "service sites", "wellness", "wedding", "portfolio", "documentation"],
        "avoid_when": ["dense data products where information density is required"],
        "marketplace_template_notes": "Prevents AI-like clutter and improves marketplace presentation quality.",
    },
    "storytelling": {
        "template_strengths": ["narrative flow", "emotional journey", "guided sections", "campaign structure"],
        "best_for_template_types": ["landing pages", "brand stories", "product launches", "event pages", "service conversion pages"],
        "avoid_when": ["compact utility dashboards where narrative sections slow down usage"],
        "marketplace_template_notes": "Useful for section order, homepage flow, and conversion-focused template storytelling.",
    },
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def typeui_root(root: Path) -> Path:
    return root / ".design-brain" / "typeui-skills"


def strip_quotes(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def parse_scalar(value: str) -> Any:
    return strip_quotes(value)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str, list[str]]:
    warnings: list[str] = []
    if not text.startswith("---"):
        return {}, text, ["Missing frontmatter block."]
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text, ["Unclosed frontmatter block."]
    yaml_text = parts[1]
    markdown = parts[2]
    data: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, data)]

    for raw_line in yaml_text.splitlines():
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            warnings.append(f"Could not parse frontmatter line: {raw_line}")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        current = stack[-1][1]
        if value == "":
            child: dict[str, Any] = {}
            current[key] = child
            stack.append((indent, child))
        else:
            current[key] = parse_scalar(value)
    return data, markdown, warnings


def extract_sections(markdown: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in markdown.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        if current:
            sections[current].append(line)
    return {key: "\n".join(value).strip() for key, value in sections.items()}


def foundation_value(style_text: str, label: str) -> str:
    pattern = re.compile(rf"-\s+\*\*{re.escape(label)}:\*\*\s*(.+)", re.IGNORECASE)
    match = pattern.search(style_text)
    return match.group(1).strip() if match else ""


def normalize_raw_files(root: Path) -> list[str]:
    actions: list[str] = []
    base = typeui_root(root)
    raw_root = base / "raw"
    extracted_root = base / "extracted"
    raw_root.mkdir(parents=True, exist_ok=True)
    extracted_root.mkdir(parents=True, exist_ok=True)

    for slug in EXPECTED_SKILLS:
        raw_path = raw_root / slug / "DESIGN.md"
        source_path = base / slug / "DESIGN.md"
        if raw_path.exists():
            actions.append(f"OK raw exists: {raw_path}")
            continue
        if source_path.exists():
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, raw_path)
            actions.append(f"COPIED raw: {source_path} -> {raw_path}")
        else:
            actions.append(f"WARNING missing source and raw file for: {slug}")
    return actions


def extract_skill(root: Path, path: Path) -> tuple[Path, dict[str, Any]]:
    slug = path.parent.name.lower()
    text = path.read_text(encoding="utf-8")
    frontmatter, markdown, warnings = parse_frontmatter(text)
    sections = extract_sections(markdown)
    style_text = sections.get("Style Foundations", "")
    rules = DETERMINISTIC_RULES.get(slug, {})

    colors = frontmatter.get("colors", {})
    typography = frontmatter.get("typography", {})
    rounded = frontmatter.get("rounded", {})
    spacing = frontmatter.get("spacing", {})

    output = {
        "skill_name": frontmatter.get("name", slug.title()),
        "slug": slug,
        "source_file": str(path.relative_to(root)),
        "overview": sections.get("Overview", ""),
        "visual_style": foundation_value(style_text, "Visual style"),
        "typography_scale": foundation_value(style_text, "Typography scale") or typography.get("sourceScale", ""),
        "typography_fonts": foundation_value(style_text, "Typography fonts"),
        "typography_weights": foundation_value(style_text, "Typography weights") or typography.get("weights", ""),
        "color_tokens": colors if isinstance(colors, dict) else {},
        "spacing_scale": foundation_value(style_text, "Spacing scale") or spacing.get("sourceScale", ""),
        "radius_tokens": rounded if isinstance(rounded, dict) else {},
        "template_strengths": rules.get("template_strengths", []),
        "best_for_template_types": rules.get("best_for_template_types", []),
        "avoid_when": rules.get("avoid_when", []),
        "marketplace_template_notes": rules.get("marketplace_template_notes", ""),
        "extraction_warnings": warnings,
    }

    output_path = typeui_root(root) / "extracted" / f"{slug}.json"
    return output_path, output


def main() -> int:
    root = repo_root()
    actions = normalize_raw_files(root)
    raw_files = sorted((typeui_root(root) / "raw").glob("*/DESIGN.md"))
    extracted: list[Path] = []

    for raw_file in raw_files:
        output_path, payload = extract_skill(root, raw_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8", newline="\n")
        extracted.append(output_path)

    print("TypeUI Skill Ingestion")
    print("======================")
    for action in actions:
        print(f"- {action}")
    print("")
    print(f"Raw DESIGN.md files found: {len(raw_files)}")
    print(f"Extracted JSON files written: {len(extracted)}")
    for path in extracted:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
