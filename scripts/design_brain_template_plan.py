#!/usr/bin/env python
"""Generate a marketplace-ready template product plan."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from design_brain_modules import build_selection, explicit_web_deck_intent
from design_brain_website_types import explicit_landing_intent, select_website_product_type, website_intent
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Codex Design Brain template product plan.")
    parser.add_argument("--template-type", required=True, help="Template product type.")
    parser.add_argument("--niche", default="", help="Niche or marketplace category.")
    parser.add_argument("--target-buyer", default="", help="Target buyer.")
    parser.add_argument("--visual-mood", default="", help="Desired visual mood.")
    parser.add_argument("--output", default="", help="Optional output markdown path.")
    parser.add_argument("--dry-run", action="store_true", help="Print the plan without saving it.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def now_human() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z")


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "template-product-plan"


def load_packs(root: Path) -> dict[str, Any]:
    path = root / ".design-brain" / "TEMPLATE_STYLE_PACKS.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"packs": {}}


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


def recommend_pack_names(template_type: str, niche: str, buyer: str, mood: str) -> list[str]:
    text = f"{template_type} {niche} {buyer} {mood}".lower()
    packs: list[str] = []
    if explicit_web_deck_intent(text):
        packs.append("Web Deck Pack")
    if not packs and contains_any(text, PRESENTATION_KEYWORDS):
        packs.append("Presentation Deck Pack")
    if contains_any(text, ["wedding", "event", "beauty", "boutique", "luxury"]):
        packs.append("Elegant Event Pack")
    if contains_any(text, ["dashboard", "admin", "analytics", "crm", "internal tool", "data table", "kpi", "back office", "operations", "hiring"]):
        packs.append("Dashboard Product Pack")
    if contains_any(text, ["ui kit", "design system", "component library", "components", "variants", "states"]):
        packs.append("UI Kit System Pack")
    if contains_any(text, ["brand kit", "branding", "identity", "brand guideline", "logo", "stationery"]):
        packs.append("Brand Kit Pack")
    if contains_any(text, ["saas website", "software website", "app website", "product website", "ai platform", "startup website"]):
        packs.append("SaaS Product Website Pack")
    if contains_any(text, ["ecommerce", "e-commerce", "shop", "store", "storefront", "marketplace website", "directory", "listing", "real estate"]):
        packs.append("Commerce Website Pack")
    if contains_any(text, ["blog", "editorial", "magazine", "news", "publication", "cms", "newsletter website"]):
        packs.append("Editorial Content Website Pack")
    if contains_any(text, ["education", "course", "lms", "academy", "documentation", "docs", "help center", "knowledge base"]):
        packs.append("Knowledge Education Website Pack")
    if contains_any(text, ["portfolio", "resume website", "case study site", "agency website", "studio website"]):
        packs.append("Portfolio Studio Website Pack")
    if contains_any(text, ["repair", "service", "booking", "local", "professional", "corporate", "hiring"]):
        packs.append("Service Business Pack")
    if contains_any(text, ["editorial", "publishing", "publication", "magazine", "portfolio", "blog"]):
        packs.append("Editorial Publishing Pack")
    if contains_any(text, ["preview", "cover", "mockup", "marketplace"]):
        packs.append("Marketplace Preview Pack")
    if website_intent(text) and not explicit_landing_intent(text) and "Website Template Pack" not in packs:
        packs.append("Website Template Pack")
    if explicit_landing_intent(text) and not packs:
        packs.append("Landing Page Pack")
    if not packs:
        packs.append("Website Template Pack")
    return packs[:2]


def skills_for_packs(packs_data: dict[str, Any], pack_names: list[str]) -> list[str]:
    skills: list[str] = []
    for pack_name in pack_names:
        pack = packs_data.get("packs", {}).get(pack_name, {})
        for skill in pack.get("skills", []):
            if skill not in skills:
                skills.append(skill)
    return skills


def section_structure(template_type: str, niche: str) -> list[str]:
    text = f"{template_type} {niche}".lower()
    if contains_any(text, PRESENTATION_KEYWORDS):
        return [
            "Deck overview or slide contact sheet.",
            "Cover slide with clear deck category and mood.",
            "Agenda or table of contents slide.",
            "Section divider slide.",
            "Company/context introduction slide.",
            "Problem or opportunity slide.",
            "Solution, service, or offer slide.",
            "Market, audience, or customer insight slide.",
            "Metrics, achievement, timeline, roadmap, chart/table, comparison, team/profile, proof, contact, and closing slides.",
            "Design system frame with theme colors, type, safe margins, footer/page numbers, chart/table rules, image placeholders, and divider rules.",
        ]
    if contains_any(text, ["marketplace-preview", "marketplace preview", "cover", "mockup", "template product showcase"]):
        return [
            "Marketplace cover with product name, category, and strongest visual preview.",
            "Primary template preview shown flat enough to inspect.",
            "Bento or section breakdown overview showing included sections/screens.",
            "Responsive desktop/mobile preview composition.",
            "Style overview with typography, palette, spacing, and UI details.",
            "Feature/value callouts that explain what buyers receive.",
            "Optional perspective mockup layer that does not hide readability.",
            "Export or handoff notes for marketplace listing assets.",
        ]
    if contains_any(text, ["dashboard", "admin", "analytics", "crm", "internal tool", "data table", "kpi", "back office", "operations"]):
        return [
            "Marketplace cover with dashboard/product preview.",
            "App shell with navigation and topbar.",
            "Overview dashboard with KPI hierarchy.",
            "Analytics cards, charts, and insight panels.",
            "Data table with filters and row actions.",
            "Detail view or side panel.",
            "Empty, loading, success, warning, and error states.",
            "Responsive compact preview.",
        ]
    if contains_any(text, ["ui kit", "design system", "component"]):
        return [
            "Cover showing component breadth.",
            "Foundations: colors, typography, spacing, radius, shadows.",
            "Core components and variants.",
            "Interaction states and accessibility notes.",
            "Composition examples.",
            "Usage/documentation frames.",
        ]
    if contains_any(text, ["brand", "branding", "identity"]):
        return [
            "Brand kit cover.",
            "Logo, color, and typography frames.",
            "Graphic elements and social layouts.",
            "Collateral or mockup examples.",
            "Editable asset overview.",
        ]
    if website_intent(text) or "website" in template_type.lower():
        record = select_website_product_type(text)
        sections = [str(item) + "." for item in record.get("homepageSections", [])]
        sections.append(
            "Page/screen map: " + ", ".join(str(item) for item in record.get("requiredPagesOrScreens", [])) + "."
        )
        sections.append("Figma reference schema receipt when a Figma link/source is used: product purpose, visual direction, section structure, grid/layout, typography hierarchy, color roles, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, Figma source hygiene, observed pages, frames, components, states, variants, design-system panels, standard inference, and do-not-copy boundary.")
        sections.append("Figma auto-layout receipt: major section stacks, repeated modules, responsive groups, and documented decorative exceptions.")
        sections.append(f"Product-family guard: {record.get('antiLandingPageGuard', 'Do not default to landing page')}.")
        return sections
    return [
        "Product-family diagnosis before section planning.",
        "Core value or usage entry.",
        "Proof, depth, states, or page-map evidence required by the medium.",
        "Reusable structure and editable area overview.",
        "Design-system rules and marketplace readiness check.",
    ]


def editable_areas(template_type: str) -> list[str]:
    if contains_any(template_type, PRESENTATION_KEYWORDS):
        return [
            "Deck title, slide titles, subtitles, agenda rows, bullet groups, quote/proof copy, and closing/contact text.",
            "Theme colors, typography, safe margins, footer/page number rules, chart palette, table style, and callout styles.",
            "Slide roles: cover, agenda, divider, content, metric, chart/table, comparison, team/profile, proof, contact, and closing.",
            "`image placeholder: [purpose]` for cover visuals, screenshots, case-study media, and galleries; `profile photo placeholder: [role]` for profile photos; generated images only when explicitly requested.",
            "Slide grid/contact sheet, flat slide previews, and thumbnail readability crops.",
        ]
    areas = [
        "Brand name, logo, navigation labels, and CTA text.",
        "Hero headline, supporting copy, and role-specific `image placeholder: [purpose]` media clues.",
        "Colors, typography, spacing, radius, and shadow tokens.",
        "Feature cards, testimonials, pricing, metrics, FAQ, and section content.",
        "Preview screenshots, mockup assets, and responsive frames when requested; source-template image zones stay editable placeholders.",
        "For Figma outputs: auto-layout frames for editable sections, nav, CTAs, cards, repeated rows, forms, and design-system panels.",
    ]
    if contains_any(template_type, ["dashboard", "admin", "analytics"]):
        areas.append("KPI values, chart labels, tables, filters, navigation, and states.")
    if contains_any(template_type, ["ui kit", "design system"]):
        areas.append("Component variants, states, tokens, and documentation labels.")
    return areas


def preview_system(template_type: str, niche: str) -> list[str]:
    text = f"{template_type} {niche}".lower()
    if contains_any(text, PRESENTATION_KEYWORDS):
        return [
            "Deck cover plus slide grid/contact sheet.",
            "Flat slide previews before any perspective mockup.",
            "Role breakdown showing cover, divider, content, metric, chart/table, team, and closing slides.",
            "Design-system preview for colors, typography, safe margins, footers, and chart/table styles.",
            "Thumbnail readability crop to prove slide clarity.",
        ]
    if contains_any(text, ["marketplace-preview", "marketplace preview", "cover", "mockup", "template product showcase"]):
        return [
            "Premium cover with one dominant readable product preview.",
            "Perspective or floating mockup as a presentation layer, not the only proof.",
            "Bento section breakdown to show product breadth.",
            "Responsive desktop/mobile previews for buyer confidence.",
            "Detail crop or style overview to prove polish and editability.",
        ]
    if contains_any(text, ["dashboard", "admin", "analytics"]):
        return [
            "Dashboard wall or bento overview cover.",
            "One flat readable screen preview.",
            "Chart/table/card breakdown preview.",
            "Responsive compact layout preview.",
        ]
    if contains_any(text, ["wedding", "event", "beauty", "luxury", "editorial"]):
        return [
            "Elegant cover with one dominant preview and premium typography.",
            "Section breakdown showing narrative flow.",
            "Desktop and mobile responsive previews.",
            "Style overview with typography, palette, and imagery direction.",
        ]
    return [
        "Strong cover with product name, category, and main preview.",
        "Section breakdown overview.",
        "Responsive desktop/mobile preview.",
        "Component/style overview.",
        "Optional perspective mockup if readability remains high.",
    ]


def quality_checklist() -> list[str]:
    return [
        "Clear product concept, niche, buyer, and marketplace category.",
        "Medium fit is correct before style is selected.",
        "Section/component structure fits the template type.",
        "Website and standard landing-page template plans use at least 8 meaningful sections unless the brief explicitly asks for a small-scope kit, micro landing, narrow campaign, squeeze page, or waitlist.",
        "Selected style pack fits buyer and mood.",
        "Editable placeholders and reusable sections are obvious.",
        "Figma reference links include professional reading and a schema receipt before build; unknown standards trigger evidence/corpus lookup, not minimalist fallback.",
        "Figma outputs include real auto-layout for editable structure and an auto-layout receipt.",
        "Originality risk is checked for reference-based or batch work.",
        "Human craft is visible through hierarchy, rhythm, restraint, and buyer-specific details.",
        "Spacing, typography, and component rules are consistent.",
        "Preview/cover direction can sell the template.",
        "No random decoration, visual clutter, or mismatched style pack.",
        "The product feels marketplace-ready, not generic.",
    ]


def generic_risks() -> list[str]:
    return [
        "Designing from visual mood before defining product purpose.",
        "Skipping medium/product-type diagnosis and defaulting to landing-page structure.",
        "Letting minimalist, safe, fallback, clean, simple, restrained, or basic language justify fewer than 8 website/landing sections.",
        "Combining too many TypeUI styles at once.",
        "Repeating interchangeable card grids without section logic.",
        "Using dramatic mockups that hide the actual template quality.",
        "Ignoring editability, responsive previews, or reusable structure.",
        "Building Figma source templates as fixed manual-coordinate drawings instead of auto-layout systems.",
        "Using a Figma reference as a flat mood board and defaulting to a minimalist structure without page/frame/component/state evidence.",
        "Using trendy effects without a buyer/category reason.",
        "Building PowerPoint or presentation templates as sliced website sections instead of slide roles.",
    ]


def markdown_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def build_plan(args: argparse.Namespace) -> str:
    root = repo_root()
    packs_data = load_packs(root)
    pack_names = recommend_pack_names(args.template_type, args.niche, args.target_buyer, args.visual_mood)
    selected_skills = skills_for_packs(packs_data, pack_names)
    selection = build_selection(
        task=f"{args.template_type} {args.niche}",
        template_type=args.template_type,
        niche=args.niche,
        target_buyer=args.target_buyer,
        visual_mood=args.visual_mood,
        root=root,
    )
    style_direction = ", ".join(selected_skills) if selected_skills else "No style skills available"
    now = now_human()

    return f"""# Template Product Plan: {args.template_type}

- Date/time: {now}
- Template product type: {args.template_type}
- Niche: {args.niche or "Not specified"}
- Target buyer: {args.target_buyer or "Not specified"}
- Visual mood: {args.visual_mood or "Not specified"}

## Recommended Style Direction

Use `{style_direction}` as style constraints. Do not merge unrelated TypeUI skills.

## Recommended Style Packs

{markdown_list(pack_names)}

## Design-Anything Module Selection

- Selected module: {selection.get("moduleId", "unknown")}
- Seed pack: {selection.get("seedPack") or "None"}
- Direction pack: {selection.get("directionPack") or "None"}

### Craft Modules

{markdown_list(selection.get("requiredCraft", []))}

### Validation Gates

{markdown_list(selection.get("validators", []))}

## Suggested Page / Section Structure

{markdown_list(section_structure(args.template_type, args.niche))}

## Required Editable Areas

{markdown_list(editable_areas(args.template_type))}

## Suggested Preview / Cover System

{markdown_list(preview_system(args.template_type, args.niche))}

## Marketplace Quality Checklist

{markdown_list(quality_checklist())}

## Risks Of Generic Output

{markdown_list(generic_risks())}

## Commands To Run Next

```bash
python scripts/design_brain_module_select.py --task "{args.template_type} {args.niche}" --template-type "{args.template_type}" --niche "{args.niche}" --visual-mood "{args.visual_mood}" --target-buyer "{args.target_buyer}" --dry-run
python scripts/design_brain_medium_playbook.py --task "{args.template_type} {args.niche}" --template-type "{args.template_type}" --niche "{args.niche}" --visual-mood "{args.visual_mood}" --target-buyer "{args.target_buyer}"
python scripts/design_brain_style_select.py --template-type "{args.template_type}" --niche "{args.niche}" --visual-mood "{args.visual_mood}" --target-buyer "{args.target_buyer}"
python scripts/design_brain_review.py --task "{args.template_type} template review" --target "TARGET" --notes "Review structure, style fit, editability, preview quality, and marketplace readiness."
python scripts/design_brain_visual_review.py --task "{args.template_type} visual review" --target "TARGET" --screenshot ".design-brain/screenshots/SCREENSHOT.png" --notes "Inspect visual hierarchy, preview quality, style consistency, and marketplace polish."
python scripts/design_brain_reflect.py --task "{args.template_type} template" --feedback "USER_FEEDBACK" --went-wrong "WHAT_WENT_WRONG" --lesson "REUSABLE_LESSON" --rule "RULE_TO_REUSE"
```
"""


def output_path(args: argparse.Namespace) -> Path:
    if args.output:
        path = Path(args.output).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.resolve()
    return repo_root() / ".design-brain" / "template-plans" / f"{now_stamp()}-{slugify(args.template_type)}.md"


def main() -> int:
    args = parse_args()
    plan = build_plan(args)
    if args.dry_run:
        print(plan)
        return 0

    path = output_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(plan, encoding="utf-8", newline="\n")
    print(f"Template product plan saved: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
