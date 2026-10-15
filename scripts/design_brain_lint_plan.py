#!/usr/bin/env python
"""Lint a proposed design structure before production work starts."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from design_brain_modules import build_selection
from design_brain_website_types import (
    explicit_landing_intent,
    page_map_matches,
    select_website_product_type,
    signal_matches,
    website_intent,
)


GENERIC_SEQUENCE = ("hero", "features", "pricing", "faq", "cta")
WEBSITE_SCOPE_TYPES = {"website-template", "landing-page", "portfolio", "ecommerce"}
FIGMA_INTENT_PATTERN = re.compile(
    r"\b(figma|figma template|create new design|design template di figma|buat design template|"
    r"bikin template website|website-template design)\b",
    re.IGNORECASE,
)
FIGMA_REFERENCE_PATTERN = re.compile(
    r"(figma\.com|\.fig\b|figma\s+(reference|referensi|link|frame|source|template source)|"
    r"(reference|referensi|link)\s+figma|pelajari\s+.*figma|study\s+.*figma)",
    re.IGNORECASE,
)
FIGMA_REFERENCE_SCHEMA_TERMS = (
    "figma reference schema receipt",
    "reference schema receipt",
    "figma schema receipt",
    "figma reference receipt",
    "schema receipt",
)
FIGMA_OBSERVED_SCHEME_TERMS = (
    "observed pages",
    "page/frame",
    "page map",
    "frame map",
    "component groups",
    "component sets",
    "variants",
    "states",
    "state map",
    "design-system panels",
    "design system panels",
    "node/frame",
)
FIGMA_STANDARD_INFERENCE_TERMS = (
    "product-family standard",
    "product family standard",
    "category standard",
    "marketplace standard",
    "standard inference",
    "normal standard",
    "section/page/screen",
    "page/screen/state",
    "standard structure",
)
FIGMA_PROFESSIONAL_READING_TERMS = (
    "product purpose",
    "niche",
    "visual direction",
    "section structure",
    "section map",
    "grid",
    "layout system",
    "typography hierarchy",
    "color-role",
    "color role",
    "image direction",
    "component style",
    "spacing rhythm",
    "visual signature",
    "visual uniqueness",
    "content logic",
    "responsive behavior",
    "figma source hygiene",
    "layer naming",
    "auto-layout",
    "default-template syndrome",
    "professional reading",
)
FIGMA_MINIMALIST_FALLBACK_TERMS = (
    "minimalist",
    "minimal",
    "simple",
    "basic",
    "thin",
    "5-section",
    "5 section",
    "five-section",
    "safe layout",
)
COMPETITIVE_UNDERBUILD_TERMS = (
    "minimalist",
    "minimal",
    "simple",
    "basic",
    "thin",
    "sparse",
    "safe",
    "safety",
    "fallback",
    "clean",
    "restrained",
)
EXPLICIT_SMALL_WEBSITE_SCOPE_TERMS = (
    "hero/header kit",
    "hero header kit",
    "header kit",
    "hero kit",
    "micro landing",
    "micro-landing",
    "narrow campaign",
    "squeeze page",
    "waitlist page",
    "one focused conversion",
    "small campaign",
    "campaign asset",
)
FIGMA_EVIDENCE_TERMS = (
    "figma evidence",
    "observed",
    "metadata",
    "screenshot",
    "reference schema",
    "schema receipt",
    "category evidence",
    "corpus evidence",
    "standard inference",
)
FIGMA_AUTO_LAYOUT_TERMS = (
    "auto-layout",
    "auto layout",
    "layoutmode",
    "layout mode",
    "hug",
    "fill container",
    "layout sizing",
    "auto-layout receipt",
    "auto layout receipt",
)
FIGMA_AUTO_LAYOUT_EXCEPTION_TERMS = (
    "decorative exception",
    "documented exception",
    "absolute-position exception",
    "absolute position exception",
    "decorative background",
    "overlay exception",
    "auto-layout receipt",
    "auto layout receipt",
)
FIGMA_INVALID_ALIGNMENT_ENUM_PATTERN = re.compile(
    r"\b(?:primaryaxisalignitems|counteraxisalignitems)\b\s*(?:=|:)\s*['\"]?end['\"]?",
    re.IGNORECASE,
)
BATCH_TEMPLATE_PATTERN = re.compile(
    r"\b(batch|multiple|several|template pack|collection|variants|more than one|"
    r"[2-9]\s+templates?|[1-9][0-9]\s+templates?|beberapa|lebih dari 1|lebih dari satu|"
    r"banyak template|batch template)\b",
    re.IGNORECASE,
)
BATCH_HARD_GATE_TERMS = {
    "reference_cycle": ("reference-led cycle", "reference led cycle", "fresh reference", "selected references", "reference group", "active reference group", "product-purpose reference group", "micro-references"),
    "fingerprint": ("structure fingerprint", "hero grammar", "section order", "module cadence", "opening strategy"),
    "scaffold_disposal": ("scaffold disposal", "disposed", "dispose", "spent scaffold", "negative memory", "primitive helpers"),
    "pairwise": ("pairwise", "accepted fingerprint", "previous fingerprint", "10 percent", "10%", "cross-template"),
    "root_cause": ("root cause", "structure similarity", "composition similarity", "effect similarity", "color-only", "copy/naming"),
    "reference_proximity": ("closer to", "selected reference", "own reference", "previous output", "previous template"),
}
WEBSITE_STRUCTURE_TERMS = {
    "hero",
    "header",
    "proof",
    "trust",
    "about",
    "service",
    "services",
    "feature",
    "features",
    "benefit",
    "process",
    "workflow",
    "portfolio",
    "project",
    "case",
    "pricing",
    "package",
    "testimonial",
    "review",
    "team",
    "faq",
    "blog",
    "news",
    "resource",
    "contact",
    "form",
    "footer",
    "responsive",
    "mobile",
    "page",
    "pages",
    "search",
    "category",
    "categories",
    "article",
    "articles",
    "docs",
    "documentation",
    "api",
    "reference",
    "changelog",
    "support",
    "listing",
    "filter",
    "filters",
    "cart",
    "checkout",
    "account",
    "wishlist",
    "state",
    "states",
}
CONVERSION_ARC_TERMS = {
    "proof",
    "trust",
    "problem",
    "audience",
    "benefit",
    "feature",
    "service",
    "services",
    "product",
    "preview",
    "process",
    "workflow",
    "case",
    "testimonial",
    "review",
    "pricing",
    "package",
    "comparison",
    "faq",
    "objection",
    "contact",
    "form",
    "booking",
    "cta",
    "footer",
}
DECK_ROLE_GROUPS = {
    "cover": ("cover", "title slide", "opening"),
    "agenda": ("agenda", "overview", "contents"),
    "divider": ("divider", "section", "chapter"),
    "story": ("problem", "solution", "market", "product", "strategy"),
    "data": ("chart", "table", "metric", "financial", "timeline"),
    "close": ("closing", "contact", "thank", "appendix"),
}
WEB_DECK_PLAN_SCHEMA = "design-brain.web-deck.deck-plan.v1"
WEB_DECK_STAGE_CONTRACT = {"width": 1920, "height": 1080, "fit": "uniform-scale", "overflow": "letterbox"}
WEB_DECK_ARCHETYPES = ("cover", "agenda", "section-divider", "problem", "solution", "feature", "data", "dashboard", "timeline", "roadmap", "case-study", "testimonial", "team", "pricing", "portfolio", "closing")
WEB_DECK_REQUIRED_ARCHETYPES = ("cover", "agenda", "section-divider", "closing")
WEB_DECK_EVIDENCE_ARCHETYPES = ("data", "dashboard", "case-study", "timeline", "testimonial")
WEB_DECK_SIGNATURE_KEYS = ("id", "entrance", "accent", "forbidden")
WEB_DECK_CHROME_KEYS = ("progress", "pageNumber", "deepLink", "notesPane")
WEB_DECK_TOKEN_GROUPS = ("color", "type", "space", "motion")
WEB_DECK_FONT_SOURCES = ("google", "self-host", "system-stack")
WEB_DECK_DENSITY_BUDGETS = {
    "speaker_led": {"minSlides": 12, "maxSlides": 20, "maxSupport": 3, "maxRevealSteps": 5},
    "reading_first": {"minSlides": 18, "maxSlides": 32, "maxSupport": 5, "maxRevealSteps": 2},
}
WEB_DECK_STAGE_TERMS = ("1920x1080", "1920 x 1080", "fixed stage", "scaled stage", "uniform scale", "uniform-scale", "letterbox")
WEB_DECK_MOTION_TERMS = ("motion signature", "entrance set", "forbidden motion", "reveal order", "reveal step", "reduced motion")
WEB_DECK_RUNTIME_TERMS = ("deep link", "arrow key", "page key", "keyboard navigation", "wheel step", "slide per page")
WEB_DECK_DELIVERY_TERMS = ("single file", "single-file", "assets directory", "assets dir", "font source", "self-host", "system stack")
WEB_DECK_EVIDENCE_TERMS = ("stage audit", "static audit", "render review", "rendered review", "deck audit")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint Design Brain plan structure.")
    parser.add_argument("--task", default="", help="Natural-language task or brief.")
    parser.add_argument("--template-type", default="", help="Template/product type.")
    parser.add_argument("--niche", default="", help="Optional niche.")
    parser.add_argument("--target-buyer", default="", help="Optional target buyer.")
    parser.add_argument("--visual-mood", default="", help="Optional visual mood.")
    parser.add_argument(
        "--proposed-structure",
        required=True,
        help="Proposed section, screen, board, or slide structure.",
    )
    parser.add_argument("--output", default="", help="Optional report path.")
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:72] or "plan-lint"


def text_for(args: argparse.Namespace) -> str:
    return " ".join(
        [
            args.task,
            args.template_type,
            args.niche,
            args.target_buyer,
            args.visual_mood,
            args.proposed_structure,
        ]
    ).lower()


def tokens(value: str) -> list[str]:
    chunks = re.split(r"[^a-zA-Z0-9]+", value.lower())
    return [chunk for chunk in chunks if chunk]


def contains_in_order(text: str, sequence: tuple[str, ...]) -> bool:
    cursor = 0
    for item in sequence:
        index = text.find(item, cursor)
        if index == -1:
            return False
        cursor = index + len(item)
    return True


def add(findings: list[dict[str, str]], severity: str, area: str, message: str, fix: str) -> None:
    lower = area.lower()
    if "route" in lower or "landing-page-not-explicit" in lower:
        category = "A. Routing/Product-Family Failure"
        action_type = "rebuild plan"
    elif "depth" in lower or "count" in lower or "coverage" in lower or "completeness" in lower:
        category = "B. Section/Page/Screen Depth Failure"
        action_type = "expand"
    elif "generic-sequence" in lower or "fingerprint" in lower:
        category = "C. Structure Fingerprint Failure"
        action_type = "rebuild"
    elif "similarity" in lower or "scaffold" in lower or "pairwise" in lower:
        category = "L. Originality/Similarity Failure"
        action_type = "diagnose then rebuild/recompose/recolor/rewrite"
    elif "image" in lower or "placeholder" in lower:
        category = "J. Placeholder/Image Direction Failure"
        action_type = "rewrite"
    elif "figma" in lower or "auto-layout" in lower:
        category = "K. Figma Source Hygiene Failure"
        action_type = "source repair"
    else:
        category = "Unclassified; consult QUALITY_GATE_FAILURE_TAXONOMY.md"
        action_type = "diagnose"
    findings.append(
        {
            "severity": severity,
            "area": area,
            "failureCategory": category,
            "message": message,
            "rootCause": message,
            "requiredFix": fix,
            "requiredActionType": action_type,
        }
    )


def matched_role_groups(text: str) -> list[str]:
    result: list[str] = []
    for group, keywords in DECK_ROLE_GROUPS.items():
        if any(keyword in text for keyword in keywords):
            result.append(group)
    return result


def duplicate_structure_tokens(structure: str) -> list[str]:
    role_words = [
        word
        for word in tokens(structure)
        if word
        in {
            "hero",
            "features",
            "cta",
            "pricing",
            "faq",
            "testimonials",
            "cards",
            "grid",
            "chart",
            "table",
            "metrics",
            "cover",
            "preview",
            "section",
        }
    ]
    seen: set[str] = set()
    duplicates: list[str] = []
    for word in role_words:
        if word in seen and word not in duplicates:
            duplicates.append(word)
        seen.add(word)
    return duplicates


def matched_terms(text: str, terms: set[str]) -> set[str]:
    words = set(tokens(text))
    return {term for term in terms if term in words}


def estimated_structure_units(structure: str) -> int:
    """Estimate explicitly planned sections/screens from a human plan string."""
    chunks = re.split(r"(?:\n+|;|->|\||,|\s+[0-9]{1,2}[\).]\s+)", structure)
    meaningful: list[str] = []
    for chunk in chunks:
        normalized = " ".join(tokens(chunk))
        if len(normalized) < 4:
            continue
        if any(term in normalized.split() for term in WEBSITE_STRUCTURE_TERMS | CONVERSION_ARC_TERMS):
            meaningful.append(normalized)
    return len(meaningful)


def explicit_small_website_scope(text: str) -> bool:
    return has_any(text, EXPLICIT_SMALL_WEBSITE_SCOPE_TERMS)


def batch_template_intent(text: str) -> bool:
    match = BATCH_TEMPLATE_PATTERN.search(text)
    if not match or "template" not in text:
        return False
    matched = match.group(0).lower()
    if "variant" in matched and not re.search(
        r"\b(batch|multiple|several|template pack|collection|more than one|"
        r"[2-9]\s+templates?|[1-9][0-9]\s+templates?|beberapa|lebih dari 1|lebih dari satu|"
        r"banyak template|template variants?)\b",
        text,
    ):
        return False
    return True


def has_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def web_deck_plan(structure: str) -> dict[str, Any] | None:
    """Return the deck plan when the proposed structure carries deck-plan JSON."""
    raw = structure.strip()
    if not raw.startswith("{"):
        return None
    try:
        plan = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(plan, dict):
        return None
    if plan.get("schema") == WEB_DECK_PLAN_SCHEMA or ("stage" in plan and "slides" in plan):
        return plan
    return None


def lint(args: argparse.Namespace) -> dict[str, Any]:
    selection = build_selection(
        task=args.task,
        template_type=args.template_type,
        niche=args.niche,
        target_buyer=args.target_buyer,
        visual_mood=args.visual_mood,
    )
    module_id = str(selection.get("moduleId", "unknown"))
    text = text_for(args)
    structure = args.proposed_structure.lower()
    findings: list[dict[str, str]] = []
    website_type = select_website_product_type(text) if website_intent(text) or module_id in WEBSITE_SCOPE_TYPES else {}
    template_like = module_id in WEBSITE_SCOPE_TYPES or "template" in text
    batch_like = template_like and batch_template_intent(text)
    figma_like = bool(FIGMA_INTENT_PATTERN.search(text))
    figma_reference_like = bool(FIGMA_REFERENCE_PATTERN.search(text))

    if figma_like and template_like:
        if FIGMA_INVALID_ALIGNMENT_ENUM_PATTERN.search(text):
            add(
                findings,
                "FAIL",
                "figma-api-alignment-enum",
                "Figma plan/code uses END for auto-layout alignment, but the Figma Plugin API requires MAX for end alignment.",
                "Replace END with MAX for primaryAxisAlignItems/counterAxisAlignItems before calling use_figma. Use MIN for start, CENTER for center, SPACE_BETWEEN only on the primary axis, and child sizing FILL for stretch behavior.",
            )
        if not has_any(text, FIGMA_AUTO_LAYOUT_TERMS):
            add(
                findings,
                "FAIL",
                "figma-auto-layout-required",
                "Figma template plan does not require real auto-layout for editable structure.",
                "Add auto-layout requirements for major sections, nav, cards, CTAs, forms, repeated rows, responsive previews, and design-system panels before building.",
            )
        if re.search(r"\b(manual x/y|manual coordinate|manual positioning|absolute positioning as primary|freeform positioning|without auto-layout|without auto layout|no auto-layout|no auto layout)\b", text) and not has_any(text, FIGMA_AUTO_LAYOUT_EXCEPTION_TERMS):
            add(
                findings,
                "FAIL",
                "figma-manual-layout-risk",
                "Figma plan appears to rely on manual or absolute positioning without documented decorative exceptions.",
                "Use auto-layout as the primary editable structure. Reserve absolute positioning only for documented decorative backgrounds, overlays, mockup callouts, or preview-only effects.",
            )
        if not has_any(text, ("auto-layout receipt", "auto layout receipt")):
            add(
                findings,
                "WARN",
                "figma-auto-layout-receipt",
                "Figma plan does not mention an auto-layout receipt.",
                "Record which page/section/component groups use auto-layout and which decorative layers remain absolute-position exceptions.",
            )

    if figma_reference_like and template_like:
        professional_reading_hits = sum(1 for term in FIGMA_PROFESSIONAL_READING_TERMS if term in text)
        if professional_reading_hits < 8:
            add(
                findings,
                "FAIL",
                "figma-professional-template-reading",
                f"Figma-reference-led plan does not show enough professional template reading ({professional_reading_hits}/8 minimum signals found).",
                "Before planning, cover product purpose/niche, visual direction, section structure, grid/layout, typography hierarchy, color roles, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, and Figma source hygiene.",
            )
        if not has_any(text, FIGMA_REFERENCE_SCHEMA_TERMS):
            add(
                findings,
                "FAIL",
                "figma-reference-schema-receipt",
                "Figma-reference-led plan does not include a Figma reference schema receipt before build.",
                "Add a receipt naming file/page/node/frame scope, observed pages/frames/sections/components/states/variants, standard inference, do-not-copy boundary, and reconstruction plan.",
            )
        if not has_any(text, FIGMA_OBSERVED_SCHEME_TERMS):
            add(
                findings,
                "FAIL",
                "figma-reference-observed-scheme",
                "Figma reference plan does not show that pages, frames, components, variants, states, or design-system panels were studied.",
                "Inspect or infer the Figma source scheme before planning: page/frame map, section map, component groups, variants, states, design-system panels, density rhythm, and editable-source signals.",
            )
        if not has_any(text, FIGMA_STANDARD_INFERENCE_TERMS):
            add(
                findings,
                "FAIL",
                "figma-reference-standard-inference",
                "Figma reference plan does not infer the product-family or marketplace standard before choosing structure.",
                "Classify the product family and define normal section/page/screen/state depth. If the standard is unclear, use taxonomy, corpus/category evidence, or one targeted question before planning.",
            )
        if has_any(text, FIGMA_MINIMALIST_FALLBACK_TERMS) and not has_any(text, FIGMA_EVIDENCE_TERMS):
            add(
                findings,
                "FAIL",
                "figma-minimalist-fallback",
                "Plan uses minimalist/simple/thin structure language around a Figma reference without evidence.",
                "Do not default to minimalist when the Figma standard is unclear. Prove the short scope from Figma evidence or use product-family standard research.",
            )
        if re.search(r"\b(copy|clone|match|duplicate|use exact)\s+(color|palette|gradient|glow|cta|background)\b", text):
            add(
                findings,
                "FAIL",
                "figma-reference-color-copy",
                "Plan appears to copy Figma reference colors, gradients, or CTA/background roles.",
                "Treat colors and effects as functional insight, then reconstruct a new palette role map and surface-depth system for the new product.",
            )

    if batch_like:
        if re.search(r"\b(one|single|same|shared|global|master)\s+(scaffold|builder|schema|layout|structure)\b", text):
            add(
                findings,
                "FAIL",
                "batch-shared-scaffold",
                "Batch plan appears to use one shared scaffold, builder, schema, layout, or structure.",
                "Use one reference-led cycle per template. Retain only primitive helpers; do not reuse page grammar, hero grammar, section sequence, card/grid cadence, CTA rhythm, or footer closure.",
            )
        if not has_any(text, BATCH_HARD_GATE_TERMS["reference_cycle"]):
            add(
                findings,
                "FAIL",
                "batch-reference-cycle",
                "Batch plan does not clearly require a fresh reference-led cycle for each template.",
                "For every template, select the next active product-purpose reference group, use up to 10 eligible varied references when enough local matches exist, study buyer/design cognition, and build that template before starting the next one.",
            )
        if not has_any(text, BATCH_HARD_GATE_TERMS["fingerprint"]):
            add(
                findings,
                "FAIL",
                "batch-structure-fingerprint",
                "Batch plan does not define a pre-build structure fingerprint.",
                "Before implementation, write the opening strategy, hero grammar, navigation model, section order, module cadence, proof/CTA/footer closure, effect language, color roles, density rhythm, and design-system panel logic.",
            )
        if not has_any(text, BATCH_HARD_GATE_TERMS["scaffold_disposal"]):
            add(
                findings,
                "FAIL",
                "batch-scaffold-disposal",
                "Batch plan does not include a scaffold disposal receipt between templates.",
                "After each accepted template, dispose of the page-level scaffold from active context and retain only primitive helpers before starting the next cycle.",
            )
        if not has_any(text, BATCH_HARD_GATE_TERMS["pairwise"]):
            add(
                findings,
                "FAIL",
                "batch-pairwise-audit",
                "Batch plan does not include a pairwise audit against accepted previous fingerprints.",
                "Compare every later template against every accepted earlier fingerprint before final delivery; if structure-defining similarity reaches 10 percent, rebuild the newer template.",
            )
        if not has_any(text, BATCH_HARD_GATE_TERMS["root_cause"]):
            add(
                findings,
                "FAIL",
                "batch-root-cause-similarity",
                "Batch plan does not diagnose whether similarity is structure, composition, effect, color-only, or copy/naming-only.",
                "Add root-cause diagnosis. Rebuild structure defects, recompose composition defects, redesign effect defects, recolor color-only defects, and rewrite copy/naming-only defects.",
            )
        if not has_any(text, BATCH_HARD_GATE_TERMS["reference_proximity"]):
            add(
                findings,
                "WARN",
                "batch-reference-proximity",
                "Batch plan does not state that each output must be closer to its own selected references than to prior templates.",
                "Add an explicit reference-proximity check before build and before final delivery.",
            )

    if template_like and re.search(r"\b(generate|generated|ai[- ]?generated|create|stock)\s+(image|photo|portrait|picture)\b", text):
        add(
            findings,
            "FAIL",
            "source-template-image-generation",
            "Plan appears to generate or force images for an editable source template.",
            "Replace image generation with text clue placeholders such as `image placeholder: [purpose]`; use `profile photo placeholder: [role]` for human/profile slots unless the user explicitly requested generated images.",
        )

    if template_like and re.search(r"\b(image|photo|portrait|screenshot|media|gallery)\b", text) and not re.search(
        r"image placeholder|profile photo placeholder|chart placeholder|diagram placeholder",
        text,
    ):
        add(
            findings,
            "WARN",
            "missing-image-placeholder-policy",
            "Plan mentions image/media needs but does not define source-template placeholder clue text.",
            "Add role-specific placeholder wording, for example `image placeholder: product screenshot` or `profile photo placeholder: founder portrait`.",
        )

    if contains_in_order(structure, GENERIC_SEQUENCE):
        add(
            findings,
            "FAIL",
            "generic-sequence",
            "The structure follows the overused hero/features/pricing/FAQ/CTA sequence.",
            "Replan the information architecture with a niche-specific proof, product, story, or interaction order.",
        )

    if re.search(r"\b(thin|sparse|reduced(?![\s-]+motion)|underbuilt|too short)\b", text) and re.search(
        r"\b(section|sections|page|pages|structure|layout|template)\b",
        text,
    ):
        add(
            findings,
            "FAIL",
            "reduced-structure",
            "The plan appears to use reduced-scope language as a structure rule.",
            "Choose section/page count from product purpose, buyer journey, and marketplace scope. Refined visual style is allowed; missing required structure is not.",
        )

    duplicates = duplicate_structure_tokens(args.proposed_structure)
    if duplicates:
        add(
            findings,
            "WARN",
            "rhythm",
            f"Repeated structure tokens detected: {', '.join(duplicates)}.",
            "Vary pacing, density, and composition instead of repeating the same block role.",
        )

    if module_id == "dashboard":
        if not re.search(r"\b(empty|loading|error|success|warning|disabled|permission|offline)\b", text):
            add(
                findings,
                "FAIL",
                "state-coverage",
                "Dashboard plan does not name operational states.",
                "Add empty, loading, error, success/warning, disabled, and permission states before visual design.",
            )
        if not re.search(r"\b(filter|sort|search|table|chart|detail|drawer|panel)\b", text):
            add(
                findings,
                "WARN",
                "dashboard-usability",
                "Dashboard plan is thin on repeated-work controls.",
                "Add filtering, sorting, search, table behavior, charts, and detail-panel behavior.",
            )

    if module_id == "presentation-deck":
        groups = matched_role_groups(text)
        if len(groups) < 4 or "cover" not in groups or "data" not in groups:
            add(
                findings,
                "FAIL",
                "slide-roles",
                "Deck plan does not contain a credible slide-role matrix.",
                "Plan roles such as cover, agenda, divider, story slides, metric/chart/table slides, team/proof, contact, and closing.",
            )
        if not re.search(r"\b(master|layout|placeholder|footer|page number|safe margin|thumbnail)\b", text):
            add(
                findings,
                "FAIL",
                "deck-system",
                "Deck plan misses master/layout or thumbnail-readability rules.",
                "Add master/layout rules, placeholders, safe margins, footer/page numbers, and thumbnail readability checks.",
            )
        if re.search(r"\b(figma|convert to pptx|pptx export|export plugin)\b", text) and not re.search(
            r"\b(top[- ]level|one frame|one slide|export[- ]ready page|individual slide frames)\b",
            text,
        ):
            add(
                findings,
                "FAIL",
                "figma-pptx-export-tree",
                "Figma deck plan does not state that the export page uses one top-level frame per slide.",
                "Plan an export-ready Figma page containing only individual 16:9 slide frames as top-level children; move boards, row wrappers, contact sheets, and design systems to non-export pages.",
            )
        if re.search(r"\b(figma|convert to pptx|pptx export|export plugin)\b", text) and not re.search(
            r"\b(1920\s*x\s*1080|1920x1080|full\s*hd|canvas size|export size|powerpoint fit|fit check)\b",
            text,
        ):
            add(
                findings,
                "WARN",
                "figma-pptx-export-fit",
                "Figma deck plan does not state how export canvas size will map to PowerPoint slide bounds.",
                "Validate the converted PowerPoint output. Prefer exact 1920x1080 Full HD top-level frames if smaller 16:9 frames export as inset or undersized content.",
            )

    deck_plan = web_deck_plan(args.proposed_structure)
    if module_id == "web-deck" or deck_plan is not None:
        if deck_plan is None:
            if not has_any(text, WEB_DECK_STAGE_TERMS):
                add(
                    findings,
                    "FAIL",
                    "web-deck-stage-contract",
                    "Web deck plan does not state the fixed stage contract.",
                    "Author every slide on a fixed 1920x1080 stage, scale the stage as one unit to the viewport, and letterbox the leftover space. `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md` owns the contract.",
                )
            if re.search(r"\b(breakpoint|breakpoints|reflow|media query|mobile layout)\b", text) and not has_any(
                text,
                ("no reflow", "never reflow", "uniform scale", "uniform-scale"),
            ):
                add(
                    findings,
                    "FAIL",
                    "web-deck-stage-reflow",
                    "Web deck plan treats the stage as a responsive page instead of one scaled stage.",
                    "Remove breakpoint and reflow rules from slide content. The only responsive behavior is the uniform stage scale recomputed on resize.",
                )
            groups = matched_role_groups(text)
            if len(groups) < 4 or "cover" not in groups or "close" not in groups:
                add(
                    findings,
                    "FAIL",
                    "web-deck-archetype-coverage",
                    "Web deck plan does not cover enough slide archetypes.",
                    f"Plan slides from the fixed vocabulary: {', '.join(WEB_DECK_ARCHETYPES)}.",
                )
            if not re.search(r"\b(density mode|speaker[- ]led|reading[- ]first)\b", text):
                add(
                    findings,
                    "FAIL",
                    "web-deck-density-budget",
                    "Web deck plan does not pick a density mode.",
                    "Choose speaker_led (12 to 20 slides, 3 support items, 5 reveal steps) or reading_first (18 to 32 slides, 5 support items, 2 reveal steps) before writing slide copy.",
                )
            if not has_any(text, WEB_DECK_MOTION_TERMS):
                add(
                    findings,
                    "FAIL",
                    "web-deck-motion-signature",
                    "Web deck plan does not name a motion signature.",
                    "Name the signature id, entrance set, accent moments, forbidden motion, and the per-slide reveal order. `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md` owns the step budget.",
                )
            if not has_any(text, WEB_DECK_RUNTIME_TERMS):
                add(
                    findings,
                    "FAIL",
                    "web-deck-runtime-contract",
                    "Web deck plan does not state runtime navigation behavior.",
                    "Plan key, pointer, and wheel navigation, the deep link, reduced-motion fallback, chrome outside the scaled stage, and one slide per printed page.",
                )
            if not has_any(text, WEB_DECK_DELIVERY_TERMS):
                add(
                    findings,
                    "WARN",
                    "web-deck-delivery-shape",
                    "Web deck plan does not state the delivery shape.",
                    "State whether the deck ships as one file or with an assets directory, name the font source, and say whether a PDF export is part of the handover.",
                )
        else:
            stage = deck_plan.get("stage") if isinstance(deck_plan.get("stage"), dict) else {}
            stage_defects = [f"{key}={stage.get(key)}" for key, expected in WEB_DECK_STAGE_CONTRACT.items() if stage.get(key) != expected]
            if stage_defects:
                add(
                    findings,
                    "FAIL",
                    "web-deck-stage-contract",
                    f"Deck plan stage breaks the fixed stage contract: {', '.join(stage_defects)}.",
                    "Set stage width 1920, height 1080, fit uniform-scale, overflow letterbox. Slide content is authored once at stage size and never reflows.",
                )
            slides = [item for item in (deck_plan.get("slides") or []) if isinstance(item, dict)]
            density_mode = str(deck_plan.get("densityMode", ""))
            budget = WEB_DECK_DENSITY_BUDGETS.get(density_mode)
            if budget is None:
                add(
                    findings,
                    "FAIL",
                    "web-deck-density-budget",
                    f"Deck plan density mode `{density_mode or 'none'}` is not a known density mode.",
                    "Set densityMode to speaker_led or reading_first, then size slide count, support items, and reveal steps to that budget.",
                )
            else:
                if len(slides) < budget["minSlides"] or len(slides) > budget["maxSlides"]:
                    add(
                        findings,
                        "FAIL",
                        "web-deck-density-budget",
                        f"Deck plan carries {len(slides)} slides; `{density_mode}` runs {budget['minSlides']} to {budget['maxSlides']}.",
                        "Bring the slide count inside the density-mode budget, or change the density mode and rewrite the slide content for it.",
                    )
                crowded = [str(slide.get("id") or slide.get("index")) for slide in slides if len(slide.get("support") or []) > budget["maxSupport"]]
                if crowded:
                    add(
                        findings,
                        "FAIL",
                        "web-deck-density-budget",
                        f"Slides carry more support items than `{density_mode}` allows: {', '.join(crowded)}.",
                        f"Cut each slide to {budget['maxSupport']} support items or split it. One claim per slide; a second claim is a second slide.",
                    )
                over_budget = [str(slide.get("id") or slide.get("index")) for slide in slides if len(slide.get("revealOrder") or []) > budget["maxRevealSteps"]]
                if over_budget:
                    add(
                        findings,
                        "FAIL",
                        "web-deck-reveal-budget",
                        f"Slides exceed the `{density_mode}` reveal-step budget of {budget['maxRevealSteps']}: {', '.join(over_budget)}.",
                        "Cut reveal steps to the budget in `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`. A slide that needs another step is a slide holding two arguments.",
                    )
            missing_reveal = [str(slide.get("id") or slide.get("index")) for slide in slides if not isinstance(slide.get("revealOrder"), list)]
            if missing_reveal:
                add(
                    findings,
                    "FAIL",
                    "web-deck-reveal-budget",
                    f"Slides have no reveal order: {', '.join(missing_reveal)}.",
                    "Give every slide a revealOrder so its blocks arrive in reading order instead of all at once.",
                )
            archetypes = [str(slide.get("archetype", "")) for slide in slides]
            unknown = sorted({item for item in archetypes if item not in WEB_DECK_ARCHETYPES})
            if unknown:
                add(
                    findings,
                    "FAIL",
                    "web-deck-archetype-vocabulary",
                    f"Deck plan uses slide archetypes outside the fixed vocabulary: {', '.join(unknown)}.",
                    f"Use only {', '.join(WEB_DECK_ARCHETYPES)}. Do not invent new slide nouns.",
                )
            missing_archetypes = [item for item in WEB_DECK_REQUIRED_ARCHETYPES if item not in archetypes]
            if missing_archetypes:
                add(
                    findings,
                    "FAIL",
                    "web-deck-archetype-coverage",
                    f"Deck plan misses required slide archetypes: {', '.join(missing_archetypes)}.",
                    "A deck needs an opening, a stated sequence, at least one section break, and a closing decision slide.",
                )
            if not any(item in WEB_DECK_EVIDENCE_ARCHETYPES for item in archetypes):
                add(
                    findings,
                    "WARN",
                    "web-deck-evidence-coverage",
                    "Deck plan carries no evidence slide.",
                    "Add a data, dashboard, case-study, timeline, or testimonial slide so the argument rests on something the room can check.",
                )
            signature = deck_plan.get("motionSignature") if isinstance(deck_plan.get("motionSignature"), dict) else {}
            signature_gaps = [key for key in WEB_DECK_SIGNATURE_KEYS if not signature.get(key)]
            if signature_gaps:
                add(
                    findings,
                    "FAIL",
                    "web-deck-motion-signature",
                    f"Deck plan motion signature is missing or incomplete: {', '.join(signature_gaps)}.",
                    "Name the signature id, the entrance set, the accent moments, and the forbidden motion that keeps the deck off stock animation.",
                )
            chrome = deck_plan.get("chrome") if isinstance(deck_plan.get("chrome"), dict) else {}
            chrome_gaps = [key for key in WEB_DECK_CHROME_KEYS if not isinstance(chrome.get(key), bool)]
            if chrome_gaps:
                add(
                    findings,
                    "FAIL",
                    "web-deck-chrome-placement",
                    f"Deck plan chrome is not declared: {', '.join(chrome_gaps)}.",
                    "Declare progress, pageNumber, deepLink, and notesPane as booleans. Chrome renders outside the scaled stage and stays out of print output.",
                )
            token_layer = deck_plan.get("tokens") if isinstance(deck_plan.get("tokens"), dict) else {}
            token_gaps = [group for group in WEB_DECK_TOKEN_GROUPS if not isinstance(token_layer.get(group), dict) or not token_layer.get(group)]
            if token_gaps:
                add(
                    findings,
                    "FAIL",
                    "web-deck-token-layer",
                    f"Deck plan token layer is incomplete: {', '.join(token_gaps)}.",
                    "Define the color, type, space, and motion token groups at stage size before slide work starts.",
                )
            delivery = deck_plan.get("delivery") if isinstance(deck_plan.get("delivery"), dict) else {}
            single_file = delivery.get("singleFile")
            if not isinstance(single_file, bool):
                add(
                    findings,
                    "FAIL",
                    "web-deck-delivery-shape",
                    "Deck plan does not say whether the deck ships as one file.",
                    "Set delivery.singleFile, and name assetsDir when the deck ships external assets.",
                )
            elif single_file and delivery.get("assetsDir"):
                add(
                    findings,
                    "FAIL",
                    "web-deck-delivery-shape",
                    "Deck plan claims single-file delivery and also names an assets directory.",
                    "Inline every asset for single-file delivery, or set singleFile false and keep the assets directory.",
                )
            elif not single_file and not delivery.get("assetsDir"):
                add(
                    findings,
                    "FAIL",
                    "web-deck-delivery-shape",
                    "Deck plan ships external assets without naming the assets directory.",
                    "Name assetsDir, or inline the assets and set singleFile true.",
                )
            if delivery.get("fontSource") not in WEB_DECK_FONT_SOURCES:
                add(
                    findings,
                    "FAIL",
                    "web-deck-delivery-shape",
                    f"Deck plan font source `{delivery.get('fontSource') or 'none'}` is not a delivery option.",
                    "Set delivery.fontSource to google, self-host, or system-stack. Fonts are the only external request a deck may make.",
                )
        if not has_any(text, WEB_DECK_EVIDENCE_TERMS):
            add(
                findings,
                "WARN",
                "web-deck-audit-evidence",
                "Web deck plan does not require the stage audit and the rendered review before completion.",
                "Run `skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs` and `skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs` on the built deck, then record both results before calling the deck done.",
            )

    if module_id in WEBSITE_SCOPE_TYPES:
        structure_terms = matched_terms(text, WEBSITE_STRUCTURE_TERMS)
        conversion_terms = matched_terms(text, CONVERSION_ARC_TERMS)
        unit_count = estimated_structure_units(args.proposed_structure)
        flow_product_ids = {
            "ecommerce_storefront",
            "marketplace_listing_directory",
            "editorial_blog_cms",
            "documentation_help_center",
            "dashboard_admin_web_app",
            "utility_pages_kit",
        }
        generic_journey_applies = not website_type or website_type.get("id") not in flow_product_ids
        small_scope_explicit = explicit_small_website_scope(text)
        if module_id == "landing-page" and not explicit_landing_intent(text):
            add(
                findings,
                "FAIL",
                "landing-page-not-explicit",
                "The plan routed to landing-page without explicit landing/campaign/lead-generation intent.",
                "Route generic website, Figma website template, SaaS website, business website, ecommerce, portfolio, blog, docs, dashboard, and similar briefs to the matching website product family instead.",
            )
        if module_id == "website-template" and website_type:
            required_min = int(website_type.get("minStructureUnits") or 0)
            if website_type.get("id") == "landing_page_campaign" and small_scope_explicit:
                required_min = min(required_min, 6)
            matched_signals = signal_matches(website_type, text)
            matched_pages = page_map_matches(website_type, text)
            min_signals = int(website_type.get("minRequiredSignals") or 0)
            min_pages = int(website_type.get("minPageMapItems") or 0)
            if unit_count < required_min:
                add(
                    findings,
                    "FAIL",
                    "website-product-type-depth",
                    f"{website_type.get('name', 'Website product')} requires at least {required_min} explicit structure units; {unit_count} found.",
                    f"Use the product-family standard: {website_type.get('standardRange', 'define full structure before designing')}.",
                )
            if len(matched_signals) < min_signals:
                add(
                    findings,
                    "FAIL",
                    "website-product-type-signals",
                    f"{website_type.get('name', 'Website product')} is missing product-family signals ({len(matched_signals)}/{min_signals} found).",
                    f"Add product-specific roles such as: {', '.join(str(item) for item in website_type.get('requiredSignals', [])[:10])}.",
                )
            if min_pages and len(matched_pages) < min_pages:
                add(
                    findings,
                    "FAIL",
                    "website-product-type-page-map",
                    f"{website_type.get('name', 'Website product')} page/screen map is too thin ({len(matched_pages)}/{min_pages} found).",
                    f"Name relevant pages/screens such as: {', '.join(str(item) for item in website_type.get('requiredPagesOrScreens', [])[:10])}.",
                )
        if (
            module_id in {"website-template", "landing-page"}
            and template_like
            and unit_count < 8
            and not small_scope_explicit
        ):
            add(
                findings,
                "FAIL",
                "competitive-section-floor",
                f"Competitive website/landing template plan has fewer than 8 meaningful sections ({unit_count} found).",
                "Use at least 8 meaningful sections for standard website or landing-page templates. Under-8 structure is allowed only for explicitly requested hero/header kits, micro landing pages, narrow campaigns, squeeze pages, or waitlists.",
            )
        if (
            module_id in {"website-template", "landing-page"}
            and unit_count < 8
            and has_any(text, COMPETITIVE_UNDERBUILD_TERMS)
        ):
            add(
                findings,
                "FAIL",
                "minimalist-under-8",
                f"Plan combines minimalist/safe/simple/clean language with fewer than 8 sections ({unit_count} found).",
                "Do not use minimalist, safe, fallback, clean, simple, restrained, or basic visual language to justify under-8 website template structure.",
            )
        if module_id == "website-template" and generic_journey_applies and len(structure_terms) < 8:
            add(
                findings,
                "FAIL",
                "website-structure-depth",
                f"Full website template plan names too few structure roles ({len(structure_terms)} found).",
                "Add a homepage block map and inner page map. Typical full website templates need 8-12 homepage blocks plus relevant inner pages.",
            )
        if module_id == "website-template" and generic_journey_applies and unit_count < 8:
            add(
                findings,
                "FAIL",
                "website-block-count",
                f"Full website template plan appears to include too few explicit homepage blocks ({unit_count} found).",
                "Plan a standard product-ready homepage before visual work. Most website template products need 8-12 blocks; serious service/SaaS/trust-heavy pages usually need 10-14.",
            )
        if module_id == "website-template" and generic_journey_applies and len(conversion_terms) < 7:
            add(
                findings,
                "FAIL",
                "website-buyer-journey",
                f"Website plan does not cover enough buyer-journey roles ({len(conversion_terms)} found).",
                "Cover discovery, trust/proof, problem or audience fit, value/features/services, process or product detail, evaluation/pricing/case proof, objection handling, conversion, and footer.",
            )
        if module_id == "website-template" and generic_journey_applies and not re.search(
            r"\b(inner page|inner pages|page map|about|service|services|portfolio|project|blog|contact|faq|pricing|team|detail)\b",
            text,
        ):
            add(
                findings,
                "FAIL",
                "website-page-map",
                "Full website template plan does not define inner pages.",
                "Add an inner page map such as about, service listing/detail, portfolio listing/detail, blog listing/detail, FAQ, pricing, team, contact, auth/account, or error pages as relevant.",
            )
        landing_minimum = 6 if small_scope_explicit else 8
        if module_id == "landing-page" and len(structure_terms) < landing_minimum:
            add(
                findings,
                "FAIL",
                "landing-page-depth",
                f"Landing page plan names too few structure roles ({len(structure_terms)} found).",
                "Plan at least 8 roles for standard product/service landing pages; 6-8 is allowed only for explicitly narrow campaigns, squeeze pages, waitlists, or micro landing scope.",
            )
        if module_id == "landing-page" and unit_count < landing_minimum:
            add(
                findings,
                "FAIL",
                "landing-page-block-count",
                f"Landing page plan appears to include too few explicit sections ({unit_count} found).",
                "Use at least 8 sections for standard product/service landing-page templates and 10-14 for trust-heavy pages; use 6-8 only for explicitly narrow campaigns, squeeze pages, waitlists, or micro landing scope.",
            )
        if not re.search(r"\b(responsive|mobile|desktop|tablet|breakpoint)\b", text):
            add(
                findings,
                "WARN",
                "responsive-logic",
                "Website-like plan does not mention responsive behavior.",
                "Add desktop/mobile structure, breakpoint behavior, and text-overflow safeguards.",
            )

    if module_id == "hero-header-kit":
        if re.search(r"\b(full website|website template|multipage|multi page|inner page|inner pages)\b", text):
            add(
                findings,
                "FAIL",
                "hero-kit-scope",
                "Hero/header kit plan is mixing kit scope with full website scope.",
                "Either keep it as a hero/header kit with variants, navigation, CTA, and responsive behavior, or route it to full website-template planning.",
            )
        if not re.search(r"\b(variant|variants|mobile|responsive|nav|navigation|cta|headline)\b", text):
            add(
                findings,
                "WARN",
                "hero-kit-completeness",
                "Hero/header kit plan does not name variant or responsive requirements.",
                "Add variant count, desktop/mobile behavior, navigation, CTA hierarchy, headline length, and media placeholder rules.",
            )

    if module_id == "ui-kit":
        if not re.search(r"\b(state|variant|hover|focus|disabled|error|token|component)\b", text):
            add(
                findings,
                "FAIL",
                "ui-kit-completeness",
                "UI kit plan misses states, variants, or token semantics.",
                "Add component states, variant rules, semantic tokens, documentation notes, and accessibility checks.",
            )

    if module_id == "brand-kit":
        if not re.search(r"\b(clear space|logo usage|do not|do/don|typography|palette|application)\b", text):
            add(
                findings,
                "WARN",
                "brand-usage",
                "Brand kit plan lacks application rules.",
                "Add logo usage, clear space, palette roles, typography roles, image treatment, and do/don't rules.",
            )

    if module_id == "marketplace-preview":
        preview_terms = re.findall(r"\b(cover|preview|mockup|responsive|detail|crop|breakdown|thumbnail)\b", text)
        if len(set(preview_terms)) < 3:
            add(
                findings,
                "FAIL",
                "marketplace-inspectability",
                "Marketplace preview plan does not reveal enough product evidence.",
                "Add cover, flat preview, section breakdown, responsive spread, detail crops, and thumbnail readability.",
            )

    if not re.search(r"\b(token|design system|style guide|color role|type scale|spacing)\b", text):
        add(
            findings,
            "WARN",
            "design-system",
            "Plan does not define reusable design-system scope.",
            "Name the minimum tokens, typography, color roles, spacing rules, components, and states for the medium.",
        )

    fail_count = sum(1 for item in findings if item["severity"] == "FAIL")
    warn_count = sum(1 for item in findings if item["severity"] == "WARN")
    return {
        "generatedAt": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z"),
        "verdict": "FAIL" if fail_count else "PASS",
        "moduleId": module_id,
        "websiteProductType": website_type.get("name", "") if website_type else "",
        "websiteProductStandard": website_type.get("standardRange", "") if website_type else "",
        "seedPack": selection.get("seedPack", ""),
        "directionPack": selection.get("directionPack", ""),
        "failCount": fail_count,
        "warnCount": warn_count,
        "findings": findings,
        "validators": selection.get("validators", []),
    }


def markdown_report(args: argparse.Namespace, result: dict[str, Any]) -> str:
    finding_lines = []
    for finding in result["findings"]:
        finding_lines.extend(
            [
                f"### {finding['severity']} - {finding['area']}",
                "",
                f"- Failure category: {finding.get('failureCategory', 'See QUALITY_GATE_FAILURE_TAXONOMY.md')}",
                f"- Issue: {finding['message']}",
                f"- Root cause: {finding.get('rootCause', finding['message'])}",
                f"- Required fix: {finding['requiredFix']}",
                f"- Required action type: {finding.get('requiredActionType', 'diagnose')}",
                "",
            ]
        )
    if not finding_lines:
        finding_lines = ["- No blocking findings.", ""]

    return "\n".join(
        [
            "# Design Brain Plan Lint",
            "",
            f"- Generated: {result['generatedAt']}",
            f"- Verdict: {result['verdict']}",
            f"- Selected module: {result['moduleId']}",
            f"- Website product type: {result['websiteProductType'] or 'None'}",
            f"- Website product standard: {result['websiteProductStandard'] or 'None'}",
            f"- Seed pack: {result['seedPack'] or 'None'}",
            f"- Direction pack: {result['directionPack'] or 'None'}",
            f"- Failures: {result['failCount']}",
            f"- Warnings: {result['warnCount']}",
            "- Failure taxonomy: `.design-brain/QUALITY_GATE_FAILURE_TAXONOMY.md`",
            "",
            "## Proposed Structure",
            "",
            args.proposed_structure,
            "",
            "## Findings",
            "",
            *finding_lines,
            "## Validators In Scope",
            "",
            "\n".join(f"- {item}" for item in result.get("validators", [])) or "- None",
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
    return repo_root() / ".design-brain" / "context-packets" / f"{stamp}-{slugify(args.task or args.template_type)}-plan-lint.md"


def main() -> int:
    args = parse_args()
    result = lint(args)
    text = json.dumps(result, indent=2, ensure_ascii=False) if args.json else markdown_report(args, result)
    if args.dry_run:
        print(text)
        return 0
    path = output_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"Plan lint report written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
