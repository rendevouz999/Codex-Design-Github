#!/usr/bin/env python
"""Select a medium/product-type playbook for advanced Design Brain work."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

from design_brain_modules import build_selection
from design_brain_website_types import (
    explicit_landing_intent,
    phrase_in_text,
    select_website_product_type,
    website_intent,
)


# The web_deck tuple is the same 34 canonical triggers as WEB_DECK_EXPLICIT_TERMS in
# scripts/design_brain_modules.py, in the same order. Keep the two lists identical, or
# detect_medium and the router disagree on the medium for the same prompt.
MEDIUM_KEYWORDS = {
    "web_deck": (
        "web deck",
        "html deck",
        "html presentation",
        "web presentation",
        "browser deck",
        "animated deck",
        "animated slides",
        "animated presentation",
        "interactive deck",
        "slide deck html",
        "single file deck",
        "presenter deck",
        "webinar deck",
        "demo day deck",
        "deck to web",
        "ppt to web",
        "pptx to html",
        "convert deck to html",
        "self running deck",
        "deck html",
        "presentasi web",
        "presentasi html",
        "slide web",
        "slide animasi",
        "presentasi animasi",
        "deck browser",
        "deck interaktif",
        "ppt ke web",
        "ppt ke html",
        "pptx ke html",
        "ubah ppt jadi web",
        "presentasi satu file",
        "slide buat live",
        "deck buat webinar",
    ),
    "presentation_deck": (
        "powerpoint",
        "presentation",
        "pitch deck",
        "deck",
        "slides",
        "google slide",
        "keynote",
        "ppt",
        "pptx",
        "figma slides",
    ),
    "dashboard": ("dashboard", "admin", "analytics", "crm", "internal tool", "data table", "kpi", "back office", "operations"),
    "ui_kit": ("ui kit", "design system", "component library", "component", "variant", "states"),
    "brand_kit": ("brand kit", "branding", "identity", "brand guideline", "logo", "stationery"),
    "marketplace_preview": ("marketplace preview", "cover", "mockup", "preview", "overview", "showcase"),
    "portfolio": ("portfolio", "case study", "gallery", "creative profile", "personal brand"),
    "ecommerce": ("ecommerce", "product page", "shop", "store", "checkout", "catalog"),
    "mobile_app": ("mobile app", "ios", "android", "onboarding", "login screen", "app screen"),
    "email_newsletter": ("email", "newsletter", "campaign email", "marketing email"),
    "static_canvas": ("poster", "canvas", "static design", "social carousel", "visual art"),
    "document_report": ("document", "report", "pdf", "docx", "whitepaper", "proposal document"),
    "website_template": ("website", "homepage", "web template", "website template", "figma website", "saas website", "business website"),
    "landing_page": ("landing page", "lead generation", "lead-gen", "campaign page", "sales page", "squeeze page", "waitlist page"),
}

MODULE_TO_PLAYBOOK = {
    "website-template": "website_template",
    "landing-page": "landing_page",
    "presentation-deck": "presentation_deck",
    "web-deck": "web_deck",
    "dashboard": "dashboard",
    "ui-kit": "ui_kit",
    "brand-kit": "brand_kit",
    "marketplace-preview": "marketplace_preview",
    "portfolio": "portfolio",
    "ecommerce": "ecommerce",
    "mobile-app": "mobile_app",
    "email-newsletter": "email_newsletter",
    "static-canvas": "static_canvas",
    "document-report": "document_report",
}


PLAYBOOKS = {
    "website_template": {
        "label": "Figma Website Template Product Family",
        "diagnosis": [
            "Choose the website product family before choosing section order.",
            "Landing page is a specific family, not the default website-template interpretation.",
            "The product value comes from standard section depth, page/screen map, states, editability, and design-system scope.",
        ],
        "required_structure": [
            "Use .design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.md to classify one of 16 families.",
            "Homepage or main canvas follows the selected family standard, usually 7-14 blocks for content sites and 8-12 screens for dashboards/admin.",
            "Page/screen map includes the family-specific required pages, flows, or states.",
            "Design system covers tokens, typography, spacing, nav, cards, forms, buttons, footer, and product-specific modules.",
            "For Figma outputs, editable sections, nav, cards, CTAs, forms, repeated rows, responsive previews, and design-system panels use real auto-layout; Figma Plugin API alignment enums must be normalized before use_figma, including END -> MAX.",
        ],
        "design_system_scope": [
            "Family-specific section modules, page map, states, editable content areas, navigation/footer system, responsive behavior, and auto-layout receipt.",
        ],
        "anti_patterns": [
            "Routing generic website, SaaS website, ecommerce, portfolio, blog, docs, dashboard, event, or service briefs into landing page.",
            "Calling a homepage-only concept a full website product without page-map evidence.",
            "Using clean/premium mood to reduce required structure.",
            "Building Figma source templates primarily with manual x/y positioning.",
        ],
        "critique_gate": [
            "Website product family clarity.",
            "Family standard section/page/screen count.",
            "Page-map and state completeness.",
            "Design-system reuse.",
            "Figma auto-layout and API-alignment receipt when output is Figma.",
        ],
    },
    "landing_page": {
        "label": "Landing Page / Website Template",
        "diagnosis": [
            "Optimize for a vertical conversion path.",
            "The first viewport must communicate product/category/value clearly.",
            "Responsive desktop/mobile behavior is part of the template value.",
        ],
        "required_structure": [
            "Hero with one primary CTA.",
            "Trust or proof band.",
            "Problem/audience fit.",
            "Benefits or features with varied layout rhythm.",
            "Product/service preview.",
            "Process, social proof, pricing or offer, FAQ, final CTA, footer.",
            "For Figma outputs, every editable section stack, card row, CTA row, FAQ row, and form module uses auto-layout with Figma API alignment enums normalized before use_figma.",
        ],
        "design_system_scope": [
            "Color, type, spacing, radius, shadow, buttons, forms, nav, cards, icons, responsive rules, and auto-layout receipt.",
        ],
        "anti_patterns": [
            "Using one repeated hero/card grid/CTA formula for every niche.",
            "Adding decorative mockups that hide the actual page.",
            "Treating CTA repetition as content progression.",
            "Figma layout built as a fixed coordinate drawing instead of editable auto-layout groups.",
        ],
        "critique_gate": [
            "First viewport signal.",
            "Conversion flow.",
            "Responsive readiness.",
            "Buyer specificity.",
            "Figma auto-layout and API-alignment receipt when output is Figma.",
        ],
    },
    "presentation_deck": {
        "label": "PowerPoint / Pitch Deck / Presentation Template",
        "diagnosis": [
            "Optimize for a horizontal slide story, not scroll.",
            "Use a slide-role matrix before visual styling.",
            "The deck product value is reusable layouts, masters, and presentation rules.",
        ],
        "required_structure": [
            "Cover, agenda, divider, intro, problem, solution, market, product/service.",
            "Metrics, timeline, chart/table, comparison, team/profile, quote/proof, contact, closing.",
            "Individual 16:9 slide frames with thumbnail-readable hierarchy.",
            "For Figma-to-PPTX work, one export-page top-level frame must equal one slide.",
            "For Figma-to-PPTX work, validate canvas size as well as ratio; use exact 1920x1080 Full HD frames when smaller 16:9 frames export undersized.",
        ],
        "design_system_scope": [
            "Theme colors, heading/body fonts, slide title positions, safe margins, footer/page numbers.",
            "Slide master/layout logic, image placeholders, chart palette, table style, callouts, divider rules.",
        ],
        "anti_patterns": [
            "Resizing a landing page into slides.",
            "Copying reference slide order, title placement, or decorative motif.",
            "Leaving chart/table/footer rules undefined.",
            "Nesting several slide frames inside a row, board, contact-sheet, or overview wrapper on the PPTX export page.",
            "Assuming 16:9 alone is enough without checking whether the converted PowerPoint slide fills the expected slide area.",
        ],
        "critique_gate": [
            "Slide-role completeness.",
            "Thumbnail readability.",
            "Master/layout consistency.",
            "Figma export tree: only individual slide frames appear as top-level frames on the export page.",
            "Figma export fit: converted PowerPoint output fills the slide area instead of appearing inset or undersized.",
            "One idea per slide.",
        ],
    },
    "web_deck": {
        "label": "Web Deck / HTML Presentation",
        "diagnosis": [
            "Optimize for a browser-rendered slide story on a fixed stage, not scroll and not a static export.",
            "Choose this medium only when motion, runtime navigation, or link sharing is part of the value.",
            "Pick the density mode, speaker-led or reading-first, before writing slide copy.",
        ],
        "required_structure": [
            "Use the slide archetype set: cover, agenda, section-divider, problem, solution, feature, data, dashboard, timeline, roadmap, case-study, testimonial, team, pricing, portfolio, closing.",
            "Author every slide on a fixed 1920x1080 stage that scales uniformly to the viewport and letterboxes the leftover space.",
            "Give each slide a reveal order so its blocks arrive in reading order instead of all at once.",
            "Runtime navigation covers arrow and page keys, space, Home and End, coarse-pointer tap zones, a debounced wheel step, and a `#<n>` deep link.",
            "Keep chrome such as progress, page number, and controls outside the scaled stage and out of print output.",
            "Plan print as one slide per page so the deck leaves a shareable PDF behind.",
        ],
        "design_system_scope": [
            "Stage tokens, color roles, display/body pairing, type scale authored at stage size, stage padding, block and item gaps, slide-role matrix, chart palette, media placeholder rules, chrome rules.",
            "Motion signature with entrance set, accent set, forbidden set, entrance/transition/stagger durations, and one easing curve, plus a reduced-motion path and a visible focus state for every runtime control.",
        ],
        "anti_patterns": [
            "Reflowing slide content for phones instead of scaling the stage.",
            "Identical entrance on every slide, or motion used in place of structure.",
            "Display-toggled slides, which a later layout rule overrides so every slide reveals at once.",
            "Chrome drawn inside the stage, so it scales with the slides and prints with them.",
            "Framework or CDN payload for a deck that needs one file.",
        ],
        "critique_gate": [
            "One dominant idea per slide, held at any scale.",
            "Stage fit with no clipped, overlapping, or overflowing content.",
            "Navigation, deep link, reduced motion, and print behavior.",
            "Motion signature followed and varied by slide role.",
            "Static audit and rendered review both pass and are recorded.",
        ],
    },
    "dashboard": {
        "label": "Dashboard / Admin / Analytics Template",
        "diagnosis": [
            "Optimize for scanning, comparison, filtering, and repeated work.",
            "Operational density matters more than marketing drama.",
        ],
        "required_structure": [
            "App shell, topbar, navigation, KPI overview, charts, tables, filters.",
            "Detail panel, activity feed, settings, empty/loading/error states.",
        ],
        "design_system_scope": [
            "Data color roles, chart styles, density scale, tables, forms, badges, nav states, focus states.",
        ],
        "anti_patterns": [
            "Oversized hero sections.",
            "Charts without labels, comparison, or state meaning.",
            "Decorative nested cards.",
        ],
        "critique_gate": [
            "Scan hierarchy.",
            "Data state coverage.",
            "Table and chart usability.",
            "Operational clarity.",
        ],
    },
    "ui_kit": {
        "label": "UI Kit / Design System Template",
        "diagnosis": [
            "Optimize for reuse, states, variants, and documentation.",
            "The board must teach usage, not only show beautiful primitives.",
        ],
        "required_structure": [
            "Foundations, tokens, typography, color, spacing, radius, shadows, icons.",
            "Buttons, inputs, nav, cards, tables, modals, states, variants, examples, usage notes.",
        ],
        "design_system_scope": [
            "Token naming, component states, variants, documentation, accessibility notes, usage boundaries.",
        ],
        "anti_patterns": [
            "Components without states.",
            "Tokens without semantic usage.",
            "Pretty boards that leave buyers guessing.",
        ],
        "critique_gate": [
            "Component completeness.",
            "State coverage.",
            "Token semantics.",
            "Documentation clarity.",
        ],
    },
    "brand_kit": {
        "label": "Brand Kit / Identity Template",
        "diagnosis": [
            "Optimize for consistent identity application across touchpoints.",
            "The buyer needs usable rules, not only mockups.",
        ],
        "required_structure": [
            "Brand concept, logo usage, palette, typography, graphic elements.",
            "Photography/art direction, social layouts, stationery/collateral, mockups, usage rules.",
        ],
        "design_system_scope": [
            "Logo clear space, palette roles, type roles, image treatment, motif, layout examples, do/dont rules.",
        ],
        "anti_patterns": [
            "Logo mockups without application rules.",
            "Random palettes without roles.",
            "Identity that fails at small size or one-color usage.",
        ],
        "critique_gate": [
            "Brand consistency.",
            "Touchpoint coverage.",
            "Usage rule clarity.",
            "Small-size resilience.",
        ],
    },
    "portfolio": {
        "label": "Portfolio Template",
        "diagnosis": [
            "Optimize for work evidence, taste, and credibility.",
            "The work or case evidence should be visible early.",
        ],
        "required_structure": [
            "Intro, selected work, case detail, about/philosophy, services/capabilities.",
            "Testimonials/proof and contact.",
        ],
        "design_system_scope": [
            "Editorial typography, project cards, image/gallery treatment, case-study structure, contact rules.",
        ],
        "anti_patterns": [
            "Generic personal hero with no work signal.",
            "Project grids that hide actual work.",
            "Decorative typography that harms readability.",
        ],
        "critique_gate": [
            "Work visibility.",
            "Case-study clarity.",
            "Editorial rhythm.",
            "Contact credibility.",
        ],
    },
    "marketplace_preview": {
        "label": "Marketplace Preview / Cover Template",
        "diagnosis": [
            "Optimize for buyer inspection and clear product understanding.",
            "The preview must reveal real template quality.",
        ],
        "required_structure": [
            "Cover, primary preview, section/screen breakdown, responsive spread.",
            "Style overview, detail crops, included items, final thumbnail.",
        ],
        "design_system_scope": [
            "Preview frame rules, mockup angle rules, label system, product naming, crop/detail rules.",
        ],
        "anti_patterns": [
            "Beautiful cover that hides weak template structure.",
            "Unreadable perspective mockups.",
            "Cover text that claims premium without product evidence.",
        ],
        "critique_gate": [
            "Instant category clarity.",
            "Inspectability.",
            "Preview honesty.",
            "Marketplace polish.",
        ],
    },
    "ecommerce": {
        "label": "Ecommerce / Product Page Template",
        "diagnosis": [
            "Optimize for product inspection, comparison, trust, and purchase confidence.",
            "The template value comes from reusable commerce states, not only a beautiful hero.",
        ],
        "required_structure": [
            "Product/category lead, gallery, benefits, specs, price/offer, reviews, trust, related items.",
            "Catalog or collection module, checkout/contact intent, responsive product-card behavior.",
        ],
        "design_system_scope": [
            "Product cards, gallery states, price/discount states, badges, forms, quantity controls, reviews, trust marks.",
        ],
        "anti_patterns": [
            "Treating ecommerce as a generic landing page.",
            "Hiding product detail behind decorative mockups.",
            "Using fake metrics or discounts without clear placeholder labeling.",
        ],
        "critique_gate": [
            "Product inspectability.",
            "Commerce state coverage.",
            "Trust and comparison clarity.",
            "Mobile buying flow.",
        ],
    },
    "mobile_app": {
        "label": "Mobile App / Native UI Template",
        "diagnosis": [
            "Optimize for task flow, thumb reach, state clarity, and small-screen hierarchy.",
            "Mobile templates need multiple screen roles, not a single resized desktop composition.",
        ],
        "required_structure": [
            "Onboarding, auth, home, list/detail, search/filter, settings, profile, empty/loading/error states.",
            "Screen-to-screen flow map and reusable mobile component rules.",
        ],
        "design_system_scope": [
            "Mobile type scale, safe areas, navigation bars, input states, cards/list rows, sheets, alerts, icons, motion rules.",
        ],
        "anti_patterns": [
            "Desktop spacing and typography squeezed into phone frames.",
            "Screens without navigation/state transitions.",
            "Decorative onboarding that does not teach the product.",
        ],
        "critique_gate": [
            "Thumb-friendly layout.",
            "Flow completeness.",
            "State coverage.",
            "Small-screen readability.",
        ],
    },
    "email_newsletter": {
        "label": "Email Newsletter / Campaign Template",
        "diagnosis": [
            "Optimize for inbox scanning, narrow-column readability, CTA clarity, and image-fallback resilience.",
            "Email design is modular and constrained; it should not behave like a full website.",
        ],
        "required_structure": [
            "Header, hero/offer, story or product module, proof, CTA, secondary links, footer/legal.",
            "Mobile-safe single-column fallback and image-blocked fallback logic.",
        ],
        "design_system_scope": [
            "Email-safe type, button modules, image ratios, divider rules, CTA bands, footer rules, dark-mode risk notes.",
        ],
        "anti_patterns": [
            "Complex web interactions that cannot survive email clients.",
            "Tiny text inside images.",
            "CTA hidden after too much decorative content.",
        ],
        "critique_gate": [
            "Inbox readability.",
            "CTA scanability.",
            "Email-client compatibility.",
            "Mobile/narrow-column flow.",
        ],
    },
    "static_canvas": {
        "label": "Static Canvas / Poster / Social Graphic",
        "diagnosis": [
            "Optimize for one strong message, composition tension, and thumbnail impact.",
            "The artifact should feel authored, not assembled from UI sections.",
        ],
        "required_structure": [
            "Message hierarchy, focal visual, supporting detail, brand/signature mark, export-safe margins.",
            "Optional series rules for carousel or poster variants.",
        ],
        "design_system_scope": [
            "Canvas size, safe margins, type lockup, palette roles, motif rules, image treatment, export specs.",
        ],
        "anti_patterns": [
            "Turning a poster into a landing page.",
            "Using too many slogans or disconnected decorative elements.",
            "Forgetting thumbnail readability.",
        ],
        "critique_gate": [
            "One-message clarity.",
            "Composition tension.",
            "Thumbnail impact.",
            "Export readiness.",
        ],
    },
    "document_report": {
        "label": "Document / Report / Whitepaper Template",
        "diagnosis": [
            "Optimize for long-form readability, page hierarchy, evidence, and repeatable sections.",
            "Documents need page-system thinking, not slide or webpage section logic.",
        ],
        "required_structure": [
            "Cover, contents, executive summary, section opener, body page, chart/table page, quote/callout, appendix.",
            "Header/footer/folio rules and print/PDF-safe margins.",
        ],
        "design_system_scope": [
            "Page grid, type scale, table/chart styles, callouts, footnotes, page numbers, image captions, export rules.",
        ],
        "anti_patterns": [
            "Over-styled pages that make long reading tiring.",
            "Charts and tables without reusable formatting rules.",
            "Missing footer, page number, or section hierarchy.",
        ],
        "critique_gate": [
            "Long-form readability.",
            "Page system completeness.",
            "Chart/table clarity.",
            "Print/PDF readiness.",
        ],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a medium/product-type playbook report.")
    parser.add_argument("--task", required=True, help="Natural-language task or brief.")
    parser.add_argument("--template-type", default="", help="Optional template product type.")
    parser.add_argument("--niche", default="", help="Optional niche.")
    parser.add_argument("--target-buyer", default="", help="Optional target buyer.")
    parser.add_argument("--visual-mood", default="", help="Optional visual mood.")
    parser.add_argument("--output", default="", help="Optional output markdown path.")
    parser.add_argument("--dry-run", action="store_true", help="Print report without saving it.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:72] or "medium-playbook"


def combined_text(args: argparse.Namespace) -> str:
    return " ".join(
        [args.task, args.template_type, args.niche, args.target_buyer, args.visual_mood]
    ).lower()


def detect_medium(args: argparse.Namespace) -> str:
    text = combined_text(args)
    # Word-boundary matching, the same matcher design_brain_modules.explicit_web_deck_intent
    # uses. Plain containment would read `slide web` inside `slide website` and steal a
    # website request from website_template, because this branch runs before website_intent.
    if any(phrase_in_text(keyword, text) for keyword in MEDIUM_KEYWORDS["web_deck"]):
        return "web_deck"
    if website_intent(text) and not explicit_landing_intent(text):
        return "website_template"
    for medium, keywords in MEDIUM_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return medium
    return "website_template"


def bullet(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- None"


def build_report(args: argparse.Namespace) -> str:
    selection = build_selection(
        task=args.task,
        template_type=args.template_type,
        niche=args.niche,
        target_buyer=args.target_buyer,
        visual_mood=args.visual_mood,
    )
    medium = MODULE_TO_PLAYBOOK.get(str(selection.get("moduleId")), detect_medium(args))
    playbook = PLAYBOOKS.get(medium, PLAYBOOKS["landing_page"])
    source_files = [
        ".design-brain/MEDIUM_PRODUCT_PLAYBOOKS.md",
        ".design-brain/ADVANCED_STYLE_GRAMMAR_MATRIX.md",
        ".design-brain/HUMAN_CRAFT_HEURISTICS.md",
    ]
    if medium == "presentation_deck":
        source_files.append("skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md")
    if medium == "web_deck":
        source_files.extend(
            [
                "skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md",
                "skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md",
                "skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md",
                "skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md",
                "skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md",
            ]
        )
    if medium in {"website_template", "landing_page", "dashboard", "ui_kit", "marketplace_preview", "portfolio", "ecommerce", "mobile_app"}:
        source_files.append(".design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md")
    if re.search(r"(figma\.com|\.fig\b|figma\s+(reference|referensi|link|frame|source)|reference\s+figma|referensi\s+figma)", combined_text(args)):
        source_files.extend(
            [
                ".design-brain/FIGMA_REFERENCE_DEEP_STUDY.md",
                ".design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md",
                ".design-brain/templates/FIGMA_REFERENCE_SCHEMA_RECEIPT.md",
            ]
        )
    source_files.extend(selection.get("sourceFiles", []))
    source_files = list(dict.fromkeys(source_files))
    website_record = select_website_product_type(combined_text(args)) if medium in {"website_template", "landing_page", "ecommerce", "portfolio", "dashboard"} else {}
    website_block = ""
    if website_record:
        website_block = f"""
## Website Product Family

- Selected family: {website_record.get('name', 'Not classified')}
- Standard: {website_record.get('standardRange', 'No standard range defined')}
- Guard: {website_record.get('antiLandingPageGuard', 'Not defined')}
"""

    return f"""# Medium Product Playbook Report

- Date/time: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z%z')}
- Task: {args.task}
- Template type: {args.template_type or 'Not specified'}
- Niche: {args.niche or 'Not specified'}
- Target buyer: {args.target_buyer or 'Not specified'}
- Visual mood: {args.visual_mood or 'Not specified'}
- Detected medium: {medium}
- Playbook: {playbook['label']}
- Selected module: {selection.get('moduleId', 'unknown')}
- Seed pack: {selection.get('seedPack') or 'None'}
- Direction pack: {selection.get('directionPack') or 'None'}

## Medium Diagnosis

{bullet(playbook['diagnosis'])}
{website_block}

## Design-Anything Module Selection

### Craft Modules

{bullet(selection.get('requiredCraft', []))}

### Seed Pack Files

{bullet(selection.get('seedFiles', []))}

### Validation Gates

{bullet(selection.get('validators', []))}

## Required Structure

{bullet(playbook['required_structure'])}

## Design System Scope

{bullet(playbook['design_system_scope'])}

## Anti-Patterns

{bullet(playbook['anti_patterns'])}

## Recommended Critique Gate

{bullet(playbook['critique_gate'])}

## Source Files To Load

{bullet(source_files)}

## Next Actions

- Plan from the detected medium before choosing visual style.
- Run template orchestration with this medium in mind.
- Use originality scoring when a reference or batch is involved.
"""


def output_path(args: argparse.Namespace) -> Path:
    if args.output:
        path = Path(args.output).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.resolve()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return repo_root() / ".design-brain" / "context-packets" / f"{stamp}-medium-playbook-{slugify(args.task)}.md"


def main() -> int:
    args = parse_args()
    report = build_report(args)
    if args.dry_run:
        print(report)
        return 0
    path = output_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8", newline="\n")
    print(f"Medium playbook report saved: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
