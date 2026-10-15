#!/usr/bin/env python
"""Create an end-to-end template product orchestration report."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from design_brain_modules import build_selection, explicit_web_deck_intent
from design_brain_website_types import (
    concise_standard,
    explicit_landing_intent,
    select_website_product_type,
    website_intent,
)


PACK_MATCHERS = [
    ("Presentation Deck Pack", ["powerpoint", "presentation", "pitch deck", "deck", "slides", "google slide", "keynote", "ppt", "pptx"]),
    ("Elegant Event Pack", ["wedding", "event", "beauty", "boutique", "luxury", "elegant"]),
    ("Dashboard Product Pack", ["dashboard", "admin", "analytics", "crm", "internal tool", "data table", "kpi", "back office", "operations"]),
    ("UI Kit System Pack", ["ui kit", "design system", "component", "components", "variant", "states"]),
    ("Brand Kit Pack", ["brand kit", "branding", "identity", "brand guideline", "logo", "stationery"]),
    ("SaaS Product Website Pack", ["saas website", "software website", "app website", "product website", "startup website", "platform website", "ai platform", "tech product"]),
    ("Commerce Website Pack", ["ecommerce", "e-commerce", "shop", "store", "storefront", "marketplace website", "directory", "listing", "real estate", "property", "job board", "booking marketplace"]),
    ("Editorial Content Website Pack", ["blog", "editorial", "magazine", "news", "publication", "cms", "newsletter website", "media site"]),
    ("Knowledge Education Website Pack", ["education", "course", "lms", "academy", "documentation", "docs", "help center", "knowledge base", "developer docs", "api docs"]),
    ("Portfolio Studio Website Pack", ["portfolio", "resume website", "case study site", "agency website", "studio website", "creative agency", "design studio"]),
    ("Website Template Pack", ["website template", "full website", "homepage template", "web template", "business website", "agency website", "service website", "corporate website"]),
    ("Service Business Pack", ["repair", "service", "booking", "local", "professional", "corporate", "hiring", "freelancer"]),
    ("Editorial Publishing Pack", ["editorial", "publishing", "publication", "magazine", "portfolio", "blog"]),
    ("Marketplace Preview Pack", ["preview", "cover", "mockup", "marketplace", "showcase"]),
    ("Landing Page Pack", ["landing", "website", "saas", "homepage", "marketing"]),
]


QUALITY_GATE_ITEMS = [
    "medium/product-type fit",
    "clear product concept",
    "niche clarity",
    "section logic",
    "competitive website section floor",
    "visual differentiation",
    "editability",
    "Figma reference schema receipt and professional reading when a Figma reference/link/source is used",
    "Figma auto-layout receipt when output is Figma",
    "reusable value",
    "preview strength",
    "originality strength",
    "human craft",
    "no generic AI output",
    "no random decoration",
    "no style mismatch",
]

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

# These patterns only prevent negated wording from being misread as a positive
# product request. They are not persistent bans on components, devices, covers,
# previews, or desktop scope.
NEGATED_SCOPE_PATTERNS = [
    r"\b(no|without)\s+(cover|preview|mockup|showcase|thumbnail|component|components|device|devices|mobile|tablet)\b",
    r"\b(tanpa|tidak perlu|tidak usah|gak perlu|nggak perlu|bukan)\s+(cover|preview|pratinjau|mockup|showcase|thumbnail|component|components|komponen|device|devices|mobile|tablet)\b",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a marketplace template product orchestration report."
    )
    parser.add_argument("--template-name", default="", help="Optional template product name.")
    parser.add_argument("--template-type", required=True, help="Template product type.")
    parser.add_argument("--niche", default="", help="Template niche or vertical.")
    parser.add_argument("--target-buyer", default="", help="Target buyer or user.")
    parser.add_argument("--visual-mood", default="", help="Desired visual mood.")
    parser.add_argument("--marketplace", default="", help="Marketplace or sales channel.")
    parser.add_argument("--target", default="", help="Target file, screen, or design surface.")
    parser.add_argument("--preview-type", default="", help="Desired preview or cover type.")
    parser.add_argument("--notes", default="", help="Additional planning notes.")
    parser.add_argument("--output", default="", help="Output markdown path.")
    parser.add_argument("--dry-run", action="store_true", help="Print report without saving.")
    return parser.parse_args()


def design_brain_root() -> Path:
    return Path(__file__).resolve().parents[1]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "template-orchestration"


def read_text_if_exists(path: Path, warnings: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        warnings.append(f"Missing reference file: {path}")
    except OSError as exc:
        warnings.append(f"Could not read {path}: {exc}")
    return ""


def load_json_if_exists(path: Path, warnings: list[str]) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        warnings.append(f"Missing JSON file: {path}")
    except json.JSONDecodeError as exc:
        warnings.append(f"Invalid JSON in {path}: {exc.msg} at line {exc.lineno}")
    except OSError as exc:
        warnings.append(f"Could not read {path}: {exc}")
    return {}


def load_extracted_skills(root: Path, warnings: list[str]) -> dict[str, dict[str, Any]]:
    extracted_dir = root / ".design-brain" / "typeui-skills" / "extracted"
    skills: dict[str, dict[str, Any]] = {}
    if not extracted_dir.exists():
        warnings.append(
            "No extracted TypeUI skill directory found. Run python scripts/design_brain_typeui_ingest.py."
        )
        return skills

    for path in sorted(extracted_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            warnings.append(f"Invalid extracted skill JSON {path}: {exc.msg} at line {exc.lineno}")
            continue
        except OSError as exc:
            warnings.append(f"Could not read extracted skill JSON {path}: {exc}")
            continue
        slug = str(data.get("slug") or path.stem)
        skills[slug] = data

    if not skills:
        warnings.append(
            "No extracted TypeUI skill JSON files found. The report will use style pack definitions only."
        )
    return skills


def combined_context(args: argparse.Namespace) -> str:
    return " ".join(
        [
            args.template_name,
            args.template_type,
            args.niche,
            args.target_buyer,
            args.visual_mood,
            args.marketplace,
            args.preview_type,
            args.notes,
        ]
    ).lower()


def strip_no_extra_terms(text: str) -> str:
    cleaned = text.lower()
    for pattern in NEGATED_SCOPE_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned)
    return cleaned


def preview_artifact_requested(args: argparse.Namespace) -> bool:
    if args.preview_type.strip():
        return True
    text = strip_no_extra_terms(" ".join([args.template_type, args.marketplace, args.notes]))
    explicit_preview_terms = ["marketplace preview", "product cover", "template cover", "cover", "preview", "mockup", "showcase"]
    return any(term in text for term in explicit_preview_terms)


def website_type_record(args: argparse.Namespace) -> dict[str, Any]:
    text = strip_no_extra_terms(product_context(args))
    return select_website_product_type(text)


def website_type_applies(args: argparse.Namespace) -> bool:
    text = strip_no_extra_terms(product_context(args))
    if any(token in text for token in PRESENTATION_KEYWORDS):
        return False
    if any(token in text for token in ["ui kit", "design system", "brand kit", "branding", "identity"]):
        return False
    if preview_artifact_requested(args) and not website_intent(text):
        return False
    return website_intent(text) or "website" in args.template_type.lower()


def product_context(args: argparse.Namespace) -> str:
    return " ".join(
        [
            args.template_name,
            args.template_type,
            args.niche,
            args.target_buyer,
            args.visual_mood,
            args.notes,
        ]
    ).lower()


def preview_context(args: argparse.Namespace) -> str:
    return " ".join([args.template_type, args.marketplace, args.preview_type, args.notes]).lower()


def recommend_pack_names(args: argparse.Namespace, packs: dict[str, Any]) -> list[str]:
    text = strip_no_extra_terms(product_context(args))
    matches: list[str] = []
    for pack_name, keywords in PACK_MATCHERS:
        if pack_name == "Marketplace Preview Pack":
            continue
        if pack_name in packs and any(keyword in text for keyword in keywords):
            matches.append(pack_name)

    if "Web Deck Pack" in packs and explicit_web_deck_intent(text):
        matches.insert(0, "Web Deck Pack")
        if "Presentation Deck Pack" in matches:
            matches.remove("Presentation Deck Pack")

    if "Marketplace Preview Pack" in packs and preview_artifact_requested(args):
        if any(keyword in args.template_type.lower() for keyword in ["preview", "cover", "mockup", "showcase"]):
            matches.insert(0, "Marketplace Preview Pack")
        elif "Marketplace Preview Pack" not in matches:
            matches.append("Marketplace Preview Pack")

    if "Dashboard Product Pack" in matches and "wedding" in text:
        matches.remove("Dashboard Product Pack")
    if "Dashboard Product Pack" in matches and any(
        keyword in text for keyword in ["editorial", "publishing", "publication", "newsletter", "magazine", "culture journal"]
    ):
        matches.remove("Dashboard Product Pack")
    if "Elegant Event Pack" in matches and "repair" in text:
        matches.remove("Elegant Event Pack")
    website_packs = {
        "Website Template Pack",
        "SaaS Product Website Pack",
        "Commerce Website Pack",
        "Editorial Content Website Pack",
        "Knowledge Education Website Pack",
        "Portfolio Studio Website Pack",
        "Service Business Pack",
    }
    if any(name in matches for name in website_packs) and "Landing Page Pack" in matches and not explicit_landing_intent(text):
        matches.remove("Landing Page Pack")

    if not matches and "Landing Page Pack" in packs:
        matches.append("Landing Page Pack")
    if not matches:
        matches.extend(list(packs.keys())[:1])

    if "Marketplace Preview Pack" in matches and not any(
        keyword in args.template_type.lower() for keyword in ["preview", "cover", "mockup", "showcase"]
    ):
        primary = [name for name in matches if name != "Marketplace Preview Pack"][:1]
        return primary + ["Marketplace Preview Pack"]

    return matches[:2]


def skills_for_packs(pack_names: list[str], packs: dict[str, Any]) -> list[str]:
    selected: list[str] = []
    for pack_name in pack_names:
        pack = packs.get(pack_name, {})
        for skill in pack.get("skills", []):
            if skill not in selected:
                selected.append(skill)
    return selected


def command_quote(value: str) -> str:
    return '"' + value.replace('"', '\\"') + '"'


def build_command(base: str, pairs: list[tuple[str, str]]) -> str:
    parts = [base]
    for flag, value in pairs:
        if value:
            parts.extend([flag, command_quote(value)])
    return " ".join(parts)


def product_diagnosis(args: argparse.Namespace) -> list[str]:
    template_type = args.template_type or "template product"
    niche = args.niche or "the selected niche"
    buyer = args.target_buyer or "template buyers"
    marketplace = args.marketplace or "the intended marketplace"
    diagnosis = [
        f"Product: a sellable {template_type} for {niche}.",
        f"Buyer expectation: {buyer} need a polished, editable product they can adapt confidently.",
        f"Marketplace category: {marketplace}.",
        "Likely buyer use case: start from a premium, credible structure without sacrificing originality or quality.",
        "Positioning: practical commercial template with a clear niche, standard product depth, and reusable sections.",
    ]
    if website_type_applies(args):
        record = website_type_record(args)
        diagnosis.append(f"Website product family: {record.get('name', 'Not classified')}.")
        diagnosis.append(f"Family standard: {record.get('standardRange', 'No standard range defined')}.")
    if preview_artifact_requested(args):
        diagnosis.append("Preview scope: include a cover/preview system because it was requested as part of the product.")
    else:
        diagnosis.append("Preview scope: optional unless the current product strategy needs it; do not inherit old no-cover/no-preview restrictions.")
    return diagnosis


def structure_plan(args: argparse.Namespace) -> dict[str, list[str]]:
    text = strip_no_extra_terms(product_context(args))
    if any(token in text for token in PRESENTATION_KEYWORDS):
        sections = [
            "Deck overview or slide contact sheet",
            "Cover slide",
            "Agenda or table of contents slide",
            "Section divider slide",
            "Context or company introduction slide",
            "Problem or opportunity slide",
            "Solution, service, or offer slide",
            "Market, audience, or customer insight slide",
            "Metric, achievement, timeline, roadmap, chart/table, comparison, team/profile, proof, contact, and closing slides",
            "Presentation design-system frame",
        ]
        required = [
            "Slide-role matrix",
            "16:9 slide frames",
            "Theme colors",
            "Heading/body type scale",
            "Safe margins",
            "Footer/page number rules",
            "Chart and table styles",
            "Image placeholders",
        ]
    elif any(token in text for token in ["dashboard", "admin", "analytics", "crm", "internal tool", "data table", "kpi", "back office", "operations"]):
        sections = [
            "Product promise / dashboard hero",
            "App shell overview",
            "KPI and analytics cards",
            "Workflow or feature modules",
            "Data table and detail view",
            "Settings, empty, loading, and error states",
            "Responsive preview and component overview",
        ]
        required = [
            "Navigation shell",
            "KPI cards",
            "Charts",
            "Tables",
            "Filters",
            "Status states",
            "Responsive panels",
        ]
    elif preview_artifact_requested(args):
        sections = [
            "Marketplace cover",
            "Hero preview composition",
            "Section breakdown overview",
            "Responsive desktop/tablet/mobile spread",
            "Component and token detail crops",
            "Included pages or sections list",
            "Final marketplace thumbnail",
        ]
        required = [
            "Cover canvas",
            "Perspective or flat preview frame",
            "Breakdown labels",
            "Responsive frames",
            "Detail crops",
            "Feature badges",
        ]
    elif any(token in text for token in ["ui kit", "design system", "component"]):
        sections = [
            "Kit overview",
            "Foundations and tokens",
            "Core components",
            "Variants and states",
            "Example screens",
            "Responsive usage examples",
            "Marketplace cover and documentation preview",
        ]
        required = [
            "Color tokens",
            "Type scale",
            "Spacing scale",
            "Components",
            "Variants",
            "States",
            "Usage examples",
        ]
    elif any(token in text for token in ["branding", "identity", "brand kit"]):
        sections = [
            "Brand concept cover",
            "Logo and mark presentation",
            "Palette and typography",
            "Social and marketing assets",
            "Stationery or collateral mockups",
            "Editable brand guidelines",
            "Marketplace overview",
        ]
        required = [
            "Logo placeholders",
            "Palette tokens",
            "Typography styles",
            "Asset mockups",
            "Guideline pages",
        ]
    elif website_type_applies(args):
        record = website_type_record(args)
        sections = [str(item) for item in record.get("homepageSections", [])]
        required = [str(item) for item in record.get("requiredPagesOrScreens", [])]
        required.extend(["product-specific design-system scope", "editable layer/content notes", "Figma auto-layout receipt"])
    else:
        sections = [
            "Header/navigation system with trust or category signal",
            "Niche-specific hero with one primary CTA and concrete product/service evidence",
            "Trust band: logos, metrics, credentials, ratings, or proof cue",
            "Problem, audience-fit, or market context section",
            "Product/service overview with clear buyer value",
            "Feature/capability modules with varied composition, not repeated cards only",
            "Process, workflow, method, or how-it-works section",
            "Case study, portfolio, product preview, gallery, or demo evidence",
            "Comparison, pricing, package, plan, or offer details when relevant",
            "Testimonials, reviews, team, credentials, or authority proof",
            "FAQ, objection handling, security/support/logistics, or guarantee block",
            "Lead capture, booking, contact, or final CTA section",
            "Footer with navigation, contact, legal/social, and trust cues",
            "Inner page map / extendable page plan even when only the desktop homepage is produced",
            "Design-system and template overview with tokens, reusable section rules, editable area notes, and auto-layout receipt",
        ]
        required = [
            "Header",
            "Hero",
            "Trust/proof",
            "Problem or audience fit",
            "Value/benefits",
            "Feature or service depth",
            "Process/workflow",
            "Case study or product preview",
            "Pricing/package/offer when relevant",
            "Testimonials or credentials",
            "FAQ or objection handling",
            "Lead/contact/booking conversion",
            "Footer",
            "Inner page map",
        ]

    optional = [
        "Testimonials",
        "Comparison table",
        "Integrations",
        "Team/profile cards",
        "Lead capture form",
        "Documentation or handoff page",
    ]
    if any(token in text for token in PRESENTATION_KEYWORDS):
        flow = [
            "Start with a cover that establishes topic, mood, and deck category.",
            "Move through slide roles from context to problem, solution, proof, and next steps.",
            "Use section dividers and repeated title/footer rules to create deck rhythm.",
            "End with contact, closing, and a slide overview for marketplace inspection.",
        ]
    else:
        flow = [
            "Start with a clear product promise.",
            "Move from niche pain point to benefit proof.",
            "Show reusable sections before decorative presentation.",
            "End with a strong CTA, footer, and extendable page map.",
        ]
    if any(token in text for token in PRESENTATION_KEYWORDS):
        reusable = [
            "Cover slide module",
            "Divider slide module",
            "Content slide module",
            "Metric slide module",
            "Chart/table slide module",
            "Profile/team slide module",
            "Contact/closing slide module",
        ]
    else:
        reusable = [
            "Header/navigation system",
            "Hero and trust entry",
            "Benefit and feature-depth modules",
            "Process/workflow module",
            "Case study or proof module",
            "Pricing/offer module",
            "FAQ/objection module",
            "Lead/contact CTA module",
            "Footer and inner-page-map module",
        ]
    return {
        "sections": sections,
        "required_components": required,
        "optional_components": optional,
        "conversion_flow": flow,
        "reusable_sections": reusable,
    }


def editable_requirements(args: argparse.Namespace) -> dict[str, list[str]]:
    requirements = {
        "editable_text_areas": [
            "Template name, headline, subheadline, CTAs, feature copy, proof copy, FAQ, and footer text.",
        ],
        "image_placeholders": [
            "`image placeholder: [purpose]` zones for hero media, product screenshots, testimonial avatars, gallery/mockup images, and preview thumbnails; do not generate final images unless explicitly requested.",
        ],
        "icon_placeholders": [
            "Feature icons, navigation icons, status icons, CTA icons, and marketplace feature badges.",
        ],
        "component_variants": [
            "Button states, card variants, pricing states, form states, nav states, and responsive section variants.",
        ],
        "color_style_tokens": [
            "Primary, secondary, background, surface, border, text, muted text, accent, radius, shadow, and spacing tokens.",
        ],
        "responsive_areas": [
            "Hero, navigation, card grids, preview frames, pricing/offers, forms, and footer layouts.",
        ],
        "reusable_section_modules": [
            "Hero, bento grid, stats/proof, process, pricing, FAQ, CTA, cover, and section overview modules.",
        ],
        "figma_auto_layout": [
            "Editable sections, navigation, CTAs, cards, repeated rows, forms, dashboards, responsive groups, and design-system panels must use real Figma auto-layout when the output is Figma.",
            "Document decorative absolute-position exceptions in an auto-layout receipt.",
        ],
    }
    if any(token in product_context(args) for token in PRESENTATION_KEYWORDS):
        requirements["editable_text_areas"] = [
            "Deck title, slide titles, agenda rows, bullet groups, metric labels, chart captions, footers, and closing/contact text.",
        ]
        requirements["image_placeholders"] = [
            "`image placeholder: [purpose]` for cover visual, screenshots, gallery images, case-study images, and slide-specific media masks; `profile photo placeholder: [role]` for profile photos; use generated images only when explicitly requested.",
        ]
        requirements["component_variants"] = [
            "Cover, divider, content, metric, chart/table, timeline, comparison, team/profile, quote/proof, contact, and closing slide layouts.",
        ]
        requirements["color_style_tokens"] = [
            "Theme colors, heading/body styles, chart palette, table style, footer/page number style, safe margin, callout, and divider tokens.",
        ]
        requirements["responsive_areas"] = [
            "Not responsive in web sense. Validate 16:9 slide frames, thumbnail readability, and editable slide-role variants.",
        ]
        requirements["reusable_section_modules"] = [
            "Slide-role modules, not website sections: cover, agenda, divider, content, metric, chart/table, profile, proof, and closing.",
        ]
    if not preview_artifact_requested(args) and not any(token in product_context(args) for token in PRESENTATION_KEYWORDS):
        requirements["image_placeholders"] = [
            "Role-specific `image placeholder: [purpose]` text for hero media, product screenshots, service imagery, gallery/demo images, and case-study visuals; use `profile photo placeholder: [role]` for avatars; generated final images require an explicit request.",
        ]
        requirements["icon_placeholders"] = [
            "Feature icons, navigation icons, status icons, CTA icons, form/support icons, and trust cues; no marketplace badge set required.",
        ]
    return requirements


def preview_direction(args: argparse.Namespace) -> list[str]:
    text = combined_context(args)
    explicit = args.preview_type.strip()
    direction = []
    if explicit:
        direction.append(f"Requested preview type: {explicit}.")
    if any(token in text for token in PRESENTATION_KEYWORDS):
        direction.extend(
            [
                "Show a deck cover and flat slide contact sheet before perspective mockups.",
                "Include slide-role breakdowns for cover, divider, content, metric, chart/table, team, and closing slides.",
                "Show design-system rules for theme colors, type, safe margins, footers, and chart/table styles.",
                "Add thumbnail readability crops to prove the deck works as a real presentation.",
            ]
        )
    elif preview_artifact_requested(args):
        direction.extend(
            [
                "Create a strong marketplace cover with the product visible immediately.",
                "Use perspective mockups only as presentation support, not as a substitute for showing real sections.",
                "Include a bento-style section breakdown so buyers understand what is included.",
                "Show responsive desktop/tablet/mobile frames with legible crops.",
            ]
        )
    elif any(token in text for token in ["dashboard", "analytics", "platform"]):
        direction.extend(
            [
                "Show a complete dashboard surface with data hierarchy and reusable panels.",
                "Include detail crops for cards, charts, tables, filters, and states.",
                "Use a responsive preview spread to prove the template adapts beyond desktop.",
            ]
        )
    else:
        direction.extend(
            [
                "Use the product canvas itself as the primary proof of value.",
                "Show standard section depth before decorative presentation.",
                "Keep design-system, editable areas, and page-map decisions visible in the plan.",
                "Do not reduce structure count because the visual mood is clean or premium.",
            ]
        )
    return direction


def quality_gate_items(args: argparse.Namespace) -> list[str]:
    items = QUALITY_GATE_ITEMS.copy()
    if not preview_artifact_requested(args):
        items = ["delivery-scope clarity" if item == "preview strength" else item for item in items]
    if any(token in combined_context(args) for token in ["website", "landing", "web template", "figma website"]):
        items.append("website/standard landing template has at least 8 meaningful sections unless explicitly small-scope")
    if re.search(r"(figma\.com|\.fig\b|figma\s+(reference|referensi|link|frame|source)|reference\s+figma|referensi\s+figma)", combined_context(args)):
        items.append("Figma reference standard inferred from professional reading and page/frame/component/state evidence, not minimalist fallback")
    return items


def generic_risks(args: argparse.Namespace, selected_skills: list[str]) -> list[str]:
    text = combined_context(args)
    if any(token in text for token in PRESENTATION_KEYWORDS):
        risks = [
            "Treating the deck as a sliced landing page instead of a slide-role system.",
            "Copying the reference slide sequence, title placement, or decorative motif.",
            "Leaving chart, table, footer, page-number, and safe-margin rules undefined.",
            "Making slides visually dramatic but unreadable as thumbnails.",
            "Using too many TypeUI-derived moods at once instead of a focused deck theme.",
            "Treating visual style as deck strategy instead of defining buyer, story arc, and reusable slide roles.",
        ]
    else:
        risks = [
            "Using a generic hero that does not signal the niche in the first viewport.",
            "Making the visual style look polished while the underlying template structure is thin.",
            "Letting minimalist, safe, fallback, clean, simple, restrained, or basic language justify fewer than 8 website/landing sections.",
            "Adding decorative effects that do not support buyer decision-making.",
            "Leaving editable placeholders unclear or inconsistent.",
            "Using a Figma reference as a flat mood board without a schema receipt or product-standard inference.",
            "Building Figma template structure as manual x/y placement instead of real auto-layout.",
            "Using too many TypeUI-derived moods at once instead of a focused style strategy.",
            "Treating visual style as product strategy instead of defining buyer, use case, and reusable value.",
        ]
    if "dashboard" in selected_skills and any(token in text for token in ["wedding", "event", "beauty"]):
        risks.append("Letting dashboard density overpower a soft event or lifestyle template.")
    if "perspective" in selected_skills:
        risks.append("Overusing perspective mockups so the actual template becomes hard to inspect.")
    if "storytelling" in selected_skills:
        if any(token in text for token in PRESENTATION_KEYWORDS):
            risks.append("Turning narrative flow into too many slides instead of a crisp slide-role arc.")
        else:
            risks.append("Turning narrative flow into too many long sections instead of a crisp conversion path.")
    return risks


def skill_contributions(selected_skills: list[str], extracted: dict[str, dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for skill in selected_skills:
        data = extracted.get(skill, {})
        strengths = data.get("template_strengths") or []
        notes = data.get("marketplace_template_notes") or ""
        if isinstance(strengths, list) and strengths:
            contribution = ", ".join(str(item) for item in strengths[:4])
        else:
            contribution = "style constraints from the selected pack"
        if notes:
            lines.append(f"{skill}: {contribution}. Marketplace note: {notes}")
        else:
            lines.append(f"{skill}: {contribution}.")
    return lines


def selected_style_strategy(
    args: argparse.Namespace,
    style_packs: dict[str, Any],
    extracted: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    packs = style_packs.get("packs", {}) if isinstance(style_packs.get("packs"), dict) else {}
    pack_names = recommend_pack_names(args, packs)
    selected_skills = skills_for_packs(pack_names, packs)
    dominant = selected_skills[0] if selected_skills else "unspecified"
    supporting = selected_skills[1:]
    conflict_rules = style_packs.get("conflict_rules", [])
    return {
        "pack_names": pack_names,
        "selected_skills": selected_skills,
        "dominant_style": dominant,
        "supporting_styles": supporting,
        "contributions": skill_contributions(selected_skills, extracted),
        "conflicts_to_avoid": conflict_rules,
    }


def suggested_commands(args: argparse.Namespace) -> dict[str, str]:
    core_pairs = [
        ("--template-type", args.template_type),
        ("--niche", args.niche),
        ("--visual-mood", args.visual_mood),
        ("--target-buyer", args.target_buyer),
    ]
    review_task = args.template_name or f"{args.template_type} template"
    target = args.target or "TARGET_FILE_OR_SCREEN"
    notes = args.notes or "Use the orchestration report to critique template structure, style, editability, Figma auto-layout when relevant, preview strength, and marketplace readiness."
    visual_note = "Inspect the rendered template or screenshots, then review hierarchy, spacing, CTA clarity, preview quality, and marketplace readiness."
    if not preview_artifact_requested(args):
        visual_note = "Inspect the rendered template or screenshots, then review hierarchy, spacing, CTA clarity, standard structure depth, editability, and marketplace readiness."
    return {
        "medium_playbook": build_command(
            "python scripts/design_brain_medium_playbook.py",
            [
                ("--task", review_task),
                ("--template-type", args.template_type),
                ("--niche", args.niche),
                ("--target-buyer", args.target_buyer),
                ("--visual-mood", args.visual_mood),
            ],
        ),
        "style_select": build_command("python scripts/design_brain_style_select.py", core_pairs),
        "template_plan": build_command("python scripts/design_brain_template_plan.py", core_pairs),
        "originality_score": build_command(
            "python scripts/design_brain_originality_score.py",
            [
                ("--reference-summary", "REFERENCE_STRUCTURE_SUMMARY"),
                ("--proposed-structure", "PROPOSED_STRUCTURE_SUMMARY"),
                ("--template-type", args.template_type),
            ],
        ),
        "design_simulation": build_command(
            "python scripts/design_brain_design_simulate.py",
            [
                ("--task", review_task),
                ("--template-type", args.template_type),
                ("--niche", args.niche),
                ("--target-buyer", args.target_buyer),
                ("--visual-mood", args.visual_mood),
                ("--marketplace", args.marketplace),
                ("--proposed-structure", "PROPOSED_STRUCTURE_SUMMARY"),
                ("--reference-summary", "REFERENCE_DNA_AND_DO_NOT_COPY_BOUNDARY"),
            ],
        ),
        "design_review": build_command(
            "python scripts/design_brain_review.py",
            [
                ("--task", review_task),
                ("--target", target),
                ("--notes", notes),
            ],
        ),
        "visual_review": build_command(
            "python scripts/design_brain_visual_review.py",
            [
                ("--task", review_task),
                ("--target", target),
                ("--notes", visual_note),
            ],
        ),
        "reflection": build_command(
            "python scripts/design_brain_reflect.py",
            [
                ("--task", review_task),
                ("--feedback", "USER_FEEDBACK"),
                ("--went-wrong", "WHAT_WENT_WRONG"),
                ("--lesson", "REUSABLE_TEMPLATE_DESIGN_LESSON"),
                ("--rule", "RULE_TO_REUSE_NEXT_TIME"),
            ],
        ),
    }


def acceptance_criteria(args: argparse.Namespace) -> list[str]:
    niche = args.niche or "the chosen niche"
    buyer = args.target_buyer or "the intended buyer"
    criteria = [
        f"The template immediately reads as a {args.template_type} for {niche}.",
        f"The design answers a real need for {buyer}.",
        "Medium/product-type fit is confirmed before visual styling.",
        "Website product family is explicit and is not auto-routed to landing page unless landing-page intent is explicit.",
        "Selected style skills are focused and compatible.",
        "Editable text, image, icon, color, and component areas are obvious.",
        "Standard product structure is complete before visual polish is judged.",
        "Originality and human craft checks are represented in the review gate.",
        "The result passes the marketplace quality gate without generic filler or random decoration.",
    ]
    criteria.insert(4, "Sections, components, or design-system patterns form a reusable product, not a one-off screen.")
    if preview_artifact_requested(args):
        criteria.insert(6, "Preview/cover system shows enough real template value to sell the product.")
    else:
        criteria.insert(6, "Preview/cover system is optional, but product value is still clear from the template structure and editable surfaces.")
    criteria.insert(7, "Responsive or device behavior is planned when it improves the core buyer-facing surfaces.")
    if any(token in product_context(args) for token in PRESENTATION_KEYWORDS):
        criteria.append("Presentation output uses slide-role matrix, slide master/layout thinking, safe margins, footers, chart/table rules, and thumbnail readability checks.")
    return criteria


def bullet_list(items: list[str]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def website_product_type_report(args: argparse.Namespace) -> list[str]:
    if not website_type_applies(args):
        return []
    record = website_type_record(args)
    return [
        f"Selected family: {record.get('name', 'Not classified')}.",
        f"Standard range: {record.get('standardRange', 'No standard range defined')}.",
        f"Minimum structure units: {record.get('minStructureUnits', 'Not defined')}.",
        f"Required page/screen evidence: {', '.join(str(item) for item in record.get('requiredPagesOrScreens', [])[:8])}.",
        f"Anti-landing-page guard: {record.get('antiLandingPageGuard', 'Not defined')}",
    ]


def build_report(args: argparse.Namespace, root: Path, warnings: list[str]) -> str:
    for relative in [
        ".design-brain/TEMPLATE_PRODUCT_INTELLIGENCE.md",
        ".design-brain/TEMPLATE_STYLE_ROUTER.md",
        ".design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md",
    ]:
        read_text_if_exists(root / relative, warnings)

    style_packs = load_json_if_exists(root / ".design-brain" / "TEMPLATE_STYLE_PACKS.json", warnings)
    extracted = load_extracted_skills(root, warnings)
    selection = build_selection(
        task=args.notes,
        template_type=args.template_type,
        niche=args.niche,
        target_buyer=args.target_buyer,
        visual_mood=args.visual_mood,
        root=root,
    )
    strategy = selected_style_strategy(args, style_packs, extracted)
    structure = structure_plan(args)
    editable = editable_requirements(args)
    commands = suggested_commands(args)
    website_report = website_product_type_report(args)

    marketplace = args.marketplace or "Not specified"
    target = args.target or "Not specified"
    preview_type = args.preview_type or "Not specified"

    lines = [
        "# Template Product Orchestration Report",
        "",
        f"Generated: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z%z')}",
        "",
    ]
    if warnings:
        lines.extend(["## Warnings", "", bullet_list(warnings), ""])

    lines.extend(
        [
            "## Input Summary",
            "",
            f"- Template name: {args.template_name or 'Not specified'}",
            f"- Template type: {args.template_type}",
            f"- Niche: {args.niche or 'Not specified'}",
            f"- Target buyer: {args.target_buyer or 'Not specified'}",
            f"- Marketplace: {marketplace}",
            f"- Visual mood: {args.visual_mood or 'Not specified'}",
            f"- Preview type: {preview_type}",
            f"- Target file/screen: {target}",
            f"- Notes: {args.notes or 'None'}",
            "",
            "## Template Product Diagnosis",
            "",
            bullet_list(product_diagnosis(args)),
            "",
        ]
    )
    if website_report:
        lines.extend(
            [
                "## Website Product Type Standard",
                "",
                bullet_list(website_report),
                "",
            ]
        )

    lines.extend(
        [
            "## Recommended Style Strategy",
            "",
            f"- Recommended style pack(s): {', '.join(strategy['pack_names']) or 'None'}",
            f"- Selected TypeUI-derived skills: {', '.join(strategy['selected_skills']) or 'None'}",
            f"- Dominant style: {strategy['dominant_style']}",
            f"- Supporting style(s): {', '.join(strategy['supporting_styles']) or 'None'}",
            "",
            "## Design-Anything Module Selection",
            "",
            f"- Selected module: {selection.get('moduleId', 'unknown')}",
            f"- Seed pack: {selection.get('seedPack') or 'None'}",
            f"- Direction pack: {selection.get('directionPack') or 'None'}",
            "",
            "### Craft Modules",
            "",
            bullet_list(selection.get("requiredCraft", [])),
            "",
            "### Seed Files",
            "",
            bullet_list(selection.get("seedFiles", [])),
            "",
            "### Validation Gates",
            "",
            bullet_list(selection.get("validators", [])),
            "",
            "### Why Each Skill Is Selected",
            "",
            bullet_list(strategy["contributions"]),
            "",
            "### Conflicting Styles To Avoid",
            "",
            bullet_list([str(item) for item in strategy["conflicts_to_avoid"]]),
            "",
            "## Template Structure Plan",
            "",
            "### Suggested Page/Section Structure",
            "",
            bullet_list(structure["sections"]),
            "",
            "### Required Components",
            "",
            bullet_list(structure["required_components"]),
            "",
            "### Optional Components",
            "",
            bullet_list(structure["optional_components"]),
            "",
            "### Conversion / Storytelling Flow",
            "",
            bullet_list(structure["conversion_flow"]),
            "",
            "### Reusable Sections",
            "",
            bullet_list(structure["reusable_sections"]),
            "",
            "## Editable Template Requirements",
            "",
        ]
    )

    for title, items in editable.items():
        lines.extend([f"### {title.replace('_', ' ').title()}", "", bullet_list(items), ""])

    lines.extend(
        [
            "## Preview / Cover Direction",
            "",
            bullet_list(preview_direction(args)),
            "",
            "## Marketplace Quality Gate",
            "",
            bullet_list(quality_gate_items(args)),
            "",
            "## Generic Output Risks",
            "",
            bullet_list(generic_risks(args, strategy["selected_skills"])),
            "",
            "## Suggested Next Commands",
            "",
            "### Medium Playbook",
            "",
            f"```bash\n{commands['medium_playbook']}\n```",
            "",
            "### Style Select",
            "",
            f"```bash\n{commands['style_select']}\n```",
            "",
            "### Template Plan",
            "",
            f"```bash\n{commands['template_plan']}\n```",
            "",
            "### Design Simulation Gate",
            "",
            "Run this before build. If it returns REVISE or BLOCKED, revise the structure and run it again before implementation.",
            "",
            f"```bash\n{commands['design_simulation']}\n```",
            "",
            "### Design Review",
            "",
            f"```bash\n{commands['design_review']}\n```",
            "",
            "### Visual Review",
            "",
            f"```bash\n{commands['visual_review']}\n```",
            "",
            "### Originality Score",
            "",
            f"```bash\n{commands['originality_score']}\n```",
            "",
            "### Reflection After Feedback",
            "",
            f"```bash\n{commands['reflection']}\n```",
            "",
            "## Acceptance Criteria",
            "",
            bullet_list(acceptance_criteria(args)),
            "",
        ]
    )
    return "\n".join(lines)


def output_path(args: argparse.Namespace, root: Path) -> Path:
    if args.output:
        return Path(args.output).expanduser().resolve()
    name = args.template_name or args.template_type
    filename = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slugify(name)}.md"
    return root / ".design-brain" / "template-orchestrations" / filename


def main() -> int:
    args = parse_args()
    root = design_brain_root()
    warnings: list[str] = []
    report = build_report(args, root, warnings)

    if args.dry_run:
        print(report)
        return 0

    path = output_path(args, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8", newline="\n")
    print(f"Template orchestration report written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
