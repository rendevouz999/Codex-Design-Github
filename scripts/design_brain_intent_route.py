#!/usr/bin/env python
"""Route natural design requests into Design Brain workflows.

This script is deterministic and dependency-free. It creates a markdown
decision report for Codex to use internally. It does not modify memory files,
journals, or preference values.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from design_brain_presentation_route import artifact_intent


@dataclass(frozen=True)
class IntentRule:
    name: str
    keywords: tuple[str, ...]
    workflows: tuple[str, ...]
    source_files: tuple[str, ...]
    tools: tuple[str, ...]
    next_actions: tuple[str, ...]


COMMON_SOURCE_FILES = (
    ".design-brain/AUTOLOAD_POLICY.md",
    ".design-brain/CONTEXT_PRIORITY.md",
    ".design-brain/NATURAL_INTENT_ROUTER.md",
    ".design-brain/DESIGN_AUTOPILOT.md",
    ".design-brain/WORKFLOW_TRIGGER_MAP.md",
    ".design-brain/RESPONSE_BEHAVIOR.md",
    ".design-brain/DESIGNER_COGNITION_LAYER.md when reference, template, or batch intent is present",
    ".design-brain/FIGMA_REFERENCE_DEEP_STUDY.md when a Figma reference/link/template source is present",
    ".design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md when Figma/source-template intent is present",
    ".design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md when Figma/source-template/editable-template intent is present",
    ".design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md when Figma/source-template/editable-template intent is present",
    ".design-brain/VISUAL_CRITIQUE_CHECKLIST.md when Figma/source-template/editable-template intent is present",
    ".design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md when batch intent is present",
)

INTENT_RULES = (
    IntentRule(
        name="native_pptx",
        keywords=("pptx", "powerpoint", "ppt master", "ppt-master"),
        workflows=("Native PPTX Workflow", "Presentation Deck Intelligence"),
        source_files=("skills/presentation-deck/workflows/native.md", "skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md"),
        tools=("skills/presentation-deck/runtime/presentation.py", "skills/presentation-deck/tests/design_brain_pptx_smoke_test.py"),
        next_actions=("Resolve native generation, template workspace creation, or source-preserving editing; run engine doctor before native execution.",),
    ),
    IntentRule(
        name="reference",
        keywords=(
            "reference",
            "referensi",
            "contoh",
            "inspired by",
            "arah seperti ini",
            "mirip vibe",
            "vibe",
            "jangan identik",
            "jangan copy",
            "not copy",
            "ambil insight",
            "insight",
            "reinterpret",
            "re-interpret",
        ),
        workflows=(
            "Designer Cognition Layer",
            "Reference Insight System",
            "Originality Guard",
            "Reference Insight Journal",
            "Template Build Journal if relevant",
        ),
        source_files=(
            ".design-brain/DESIGNER_COGNITION_LAYER.md",
            ".design-brain/REFERENCE_INSIGHT_SYSTEM.md",
            ".design-brain/REFERENCE_INSIGHT_JOURNAL.md",
            ".design-brain/ORIGINALITY_GUARD.md",
            ".design-brain/TEMPLATE_BUILD_JOURNAL.md",
        ),
        tools=(
            "scripts/design_brain_reference_insight.py",
            "scripts/design_brain_context_packet.py",
        ),
        next_actions=(
            "Extract evidence-backed designer cognition from the reference before designing.",
            "State what must not be copied.",
            "Reinterpret structure, hierarchy, flow, and composition into a new direction.",
        ),
    ),
    IntentRule(
        name="figma_reference",
        keywords=(
            "figma reference",
            "figma.com",
            "link figma",
            "figma link",
            "figma frame",
            "figma design template",
            ".fig",
            "pelajari link figma",
            "study this figma",
        ),
        workflows=(
            "Figma Reference Deep Study",
            "Figma Professional Template Learning",
            "Figma Reference Schema Receipt",
            "Designer Cognition Layer",
            "Reference Insight System",
            "Product-family standard inference",
            "Originality Guard",
        ),
        source_files=(
            ".design-brain/FIGMA_REFERENCE_DEEP_STUDY.md",
            ".design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md",
            ".design-brain/FIGMA_REFERENCE_LEARNING_CORPUS.md when using the user-provided Figma material links",
            ".design-brain/templates/FIGMA_REFERENCE_SCHEMA_RECEIPT.md",
            ".design-brain/DESIGNER_COGNITION_LAYER.md",
            ".design-brain/REFERENCE_INSIGHT_SYSTEM.md",
            ".design-brain/TEMPLATE_PRODUCT_INTELLIGENCE.md",
            ".design-brain/TEMPLATE_STRUCTURE_RULES.md",
            ".design-brain/ORIGINALITY_GUARD.md",
            ".design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md when website-template intent is present",
        ),
        tools=(
            "Figma get_metadata/get_design_context/get_screenshot when access is available",
            "scripts/design_brain_context_packet.py",
            "scripts/design_brain_lint_plan.py",
            "scripts/design_brain_reference_insight.py after inspection",
        ),
        next_actions=(
            "Inspect product purpose, visual direction, section structure, grid/layout, typography hierarchy, color roles, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, Figma source hygiene, Figma pages, frames, sections, components, variants, states, design-system panels, density rhythm, and source-template signals before planning.",
            "Write a Figma reference schema receipt before build.",
            "Infer product family and normal marketplace standard before choosing section/page/screen depth.",
            "If the standard is unclear, use taxonomy, local corpus, category research, or one targeted question; do not default to minimalist.",
            "Reconstruct color roles and effect language instead of copying exact palette, gradient, glow, CTA, or background roles.",
        ),
    ),
    IntentRule(
        name="figma_output",
        keywords=(
            "figma",
            "figma template",
            "create new design",
            "design template di figma",
            "design template website",
            "buat design template",
            "bikin template website",
            "website template",
        ),
        workflows=(
            "Figma Output Target",
            "Figma Auto-Layout Enforcement",
            "Template Product Intelligence",
            "Website Template Reference Corpus when website-template intent is present",
            "Template Orchestrator",
            "Visual review and output verification",
        ),
        source_files=(
            ".design-brain/FIGMA_OUTPUT_TARGET.md",
            ".design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md",
            ".design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md",
            ".design-brain/TEMPLATE_PRODUCT_INTELLIGENCE.md",
            ".design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md when website-template intent is present",
            ".design-brain/TEMPLATE_ORCHESTRATOR.md",
            ".design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md",
            ".design-brain/VISUAL_CRITIQUE_CHECKLIST.md",
        ),
        tools=(
            "Figma create_new_file tool only when a configured project ID or user-supplied Figma target is available",
            "Figma use_figma tool after the design file exists",
            "scripts/design_brain_website_reference_select.py when website-template intent is present",
            "scripts/design_brain_template_orchestrate.py",
        ),
        next_actions=(
            "If no other Figma target is supplied, use the configured Figma output target; if it is missing or still a placeholder, ask for a valid project/file target before creating a file.",
            "Treat natural website-template design requests in this workspace as Figma website template work unless the user explicitly asks for code or another medium.",
            "Build editable structure with real auto-layout, normalize Figma Plugin API alignment enums before use_figma (END -> MAX, START -> MIN), and include auto-layout, API-alignment, layer/component naming, placeholder, responsive/editability, and source-hygiene receipts.",
            "Do not ask for the same project link again unless the Figma create step fails or the user requests another destination.",
        ),
    ),
    IntentRule(
        name="template_product",
        keywords=(
            "template",
            "landing page",
            "dashboard template",
            "ui kit",
            "envato",
            "figma template",
            "marketplace",
            "product preview",
            "preview product",
            "sellable",
            "template product",
            "website template",
            "web template",
            "powerpoint",
            "presentation",
            "pitch deck",
            "deck",
            "slides",
            "google slide",
            "keynote",
            "ppt",
            "pptx",
            "brand kit",
            "branding",
            "portfolio",
        ),
        workflows=(
            "Template Product Intelligence",
            "Template Image Placeholder Policy",
            "Figma Auto-Layout Enforcement when output is Figma",
            "Template Orchestrator",
            "Style Router",
            "Quality Gate",
        ),
        source_files=(
            ".design-brain/DESIGNER_COGNITION_LAYER.md",
            ".design-brain/TEMPLATE_PRODUCT_INTELLIGENCE.md",
            ".design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md",
            ".design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md when output is Figma",
            ".design-brain/TEMPLATE_ORCHESTRATOR.md",
            ".design-brain/TEMPLATE_STYLE_ROUTER.md",
            ".design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md",
            ".design-brain/MARKETPLACE_QUALITY_GATE.md",
            ".design-brain/PREVIEW_PRESENTATION_SYSTEM.md",
            ".design-brain/TEMPLATE_STRUCTURE_RULES.md",
            ".design-brain/TEMPLATE_TAXONOMY.md",
            ".design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md when website-template intent is present",
            ".design-brain/TEMPLATE_STYLE_PACKS.json",
            ".design-brain/MEDIUM_PRODUCT_PLAYBOOKS.md",
            ".design-brain/ADVANCED_STYLE_GRAMMAR_MATRIX.md",
            ".design-brain/HUMAN_CRAFT_HEURISTICS.md",
            "skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md when presentation intent is present",
        ),
        tools=(
            "scripts/design_brain_medium_playbook.py",
            "scripts/design_brain_template_orchestrate.py",
            "scripts/design_brain_style_select.py",
            "scripts/design_brain_template_plan.py",
        ),
        next_actions=(
            "Define template type, niche, target buyer, marketplace category, and editable structure.",
            "Use text clue placeholders for source-template image zones, such as `image placeholder: [purpose]`, unless generated images were explicitly requested.",
            "For Figma outputs, require auto-layout for editable sections, nav, cards, CTAs, forms, repeated rows, responsive previews, and design-system panels.",
            "Select a coherent style strategy before creating visuals.",
            "Apply marketplace quality gates before finalizing.",
        ),
    ),
    IntentRule(
        name="medium_product",
        keywords=(
            "website template",
            "web template",
            "landing page",
            "powerpoint",
            "presentation",
            "pitch deck",
            "deck",
            "slides",
            "google slide",
            "keynote",
            "ppt",
            "pptx",
            "dashboard",
            "ui kit",
            "design system",
            "brand kit",
            "branding",
            "portfolio",
            "marketplace",
            "cover",
            "preview",
            "marketplace preview",
        ),
        workflows=(
            "Medium Product Playbook",
            "Advanced Style Grammar",
            "Human Craft Heuristics",
            "Presentation Deck Intelligence when relevant",
        ),
        source_files=(
            ".design-brain/MEDIUM_PRODUCT_PLAYBOOKS.md",
            ".design-brain/ADVANCED_STYLE_GRAMMAR_MATRIX.md",
            ".design-brain/HUMAN_CRAFT_HEURISTICS.md",
            "skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md when presentation intent is present",
        ),
        tools=(
            "scripts/design_brain_medium_playbook.py",
        ),
        next_actions=(
            "Classify the target medium before using landing-page assumptions.",
            "Load the product-type playbook and critique gate.",
            "Convert style words into medium-specific grammar and acceptance criteria.",
        ),
    ),
    IntentRule(
        name="web_deck",
        keywords=(
            # detect_intents matches these with plain containment, so every keyword here
            # must be safe as a substring. The canonical trigger `slide web` is deliberately
            # absent: it sits inside `slide website`, which is a website request, and no
            # substring of `slide web` can separate the two. The word-boundary matcher in
            # design_brain_modules.explicit_web_deck_intent carries that trigger instead,
            # and it is the matcher the module router actually routes on.
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
        workflows=(
            "Web Deck Intelligence",
            "Web Deck Stage Gate",
            "Web Deck Motion Grammar",
            "Web Deck Delivery Contract",
            "Deck Source Bridge when an existing deck, PPT, or PPTX is the input",
        ),
        source_files=(
            "skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md",
            "skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md",
            "skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md",
            "skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md",
            "skills/presentation-deck/resources/web-deck/deck-plan-schema.json",
            "skills/presentation-deck/design/craft/deck-motion.md",
            "skills/presentation-deck/design/craft/web-deck-stage-fidelity.md",
            "skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md when an existing deck, PPT, or PPTX is the input",
        ),
        tools=(
            "skills/presentation-deck/runtime/web/design_brain_web_deck_plan.mjs",
            "skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs",
            "skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs",
            "skills/presentation-deck/runtime/web/design_brain_deck_source_extract.mjs",
        ),
        next_actions=(
            "Plan the deck as a fixed 1920x1080 stage with slide archetypes, density mode, and reveal order before writing markup.",
            "Keep slide switching, runtime navigation, deep links, and reduced-motion behavior inside the stage and runtime contract.",
            "Run the web deck audit and the render review before calling the deck done.",
        ),
    ),
    IntentRule(
        name="batch",
        keywords=(
            "batch",
            "beberapa template",
            "beberapa design",
            "beberapa desain",
            "gambar design",
            "gambar desain",
            "template pack",
            "collection",
            "koleksi",
            "set",
            "sekaligus",
            "multiple",
            "variants",
            "varian",
            "variasi",
            "variasi template",
            "versi",
        ),
        workflows=(
            "Designer Cognition Layer",
            "Sequential Reference-Led Batch Workflow",
            "Per-Cycle Reference Study",
            "Pattern Lock After Each Template",
            "Similarity Guard Against Previous Cycles",
            "Automatic Visual-Language Gate",
            "Effect / Gradient / Surface-Depth Review",
        ),
        source_files=(
            ".design-brain/DESIGNER_COGNITION_LAYER.md",
            ".design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md",
            ".design-brain/templates/SEQUENTIAL_REFERENCE_BATCH_CYCLE.md",
            ".design-brain/BATCH_TEMPLATE_HARD_GATES.md",
            ".design-brain/EFFECT_LANGUAGE_JUDGMENT.md",
            ".design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md when the batch contains website-template outputs",
            ".design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md",
            ".design-brain/TEMPLATE_STRUCTURE_RULES.md",
            ".design-brain/TEMPLATE_ORCHESTRATOR.md",
            ".design-brain/ORIGINALITY_GUARD.md",
            ".design-brain/TEMPLATE_BUILD_JOURNAL.md",
        ),
        tools=(
            "scripts/design_brain_sequential_batch.py",
            "scripts/design_brain_website_reference_select.py when website-template intent is present",
            "scripts/design_brain_template_orchestrate.py",
            "scripts/design_brain_review.py",
        ),
        next_actions=(
            "Build one template at a time instead of creating one global batch scaffold.",
            "For each template, select the next active product-purpose reference group, using up to 10 eligible varied references when enough local matches exist, and infer buyer decision model, designer intent, attention, rhythm, trust, density, conversion, component reasoning, structure, and visual logic.",
            "Before building each template, define both a structure fingerprint and a visual-language fingerprint: color roles, gradient logic, effects, surface depth, CTA behavior, and media-placeholder treatment.",
            "Do not wait for explicit user requests for effects or gradients; infer and apply the correct visual-language pass automatically.",
            "Convert reference imagery into role-specific source-template text clues; use `profile photo placeholder: [role]` for human/profile images.",
            "Complete the current template plus its own design-system board, screenshot-inspect effect/gradient/surface-depth quality and the design-system board when possible, lock its pattern memory, then restart reference study for the next template.",
            "Use similarity guard against selected references and previous locked patterns before presenting the batch as complete.",
        ),
    ),
    IntentRule(
        name="sequential_batch",
        keywords=(
            "satu per satu",
            "1 per 1",
            "one by one",
            "masing-masing",
            "tiap",
            "per template",
            "per desain",
            "per design",
            "per gambar",
        ),
        workflows=(
            "Sequential Reference-Led Batch Workflow",
            "Batch Template Hard Gates",
            "One Template = One Full Cycle",
            "Scaffold Disposal Receipt before the next output",
        ),
        source_files=(
            ".design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md",
            ".design-brain/templates/SEQUENTIAL_REFERENCE_BATCH_CYCLE.md",
            ".design-brain/BATCH_TEMPLATE_HARD_GATES.md",
            ".design-brain/EFFECT_LANGUAGE_JUDGMENT.md",
        ),
        tools=(
            "scripts/design_brain_sequential_batch.py",
            "scripts/design_brain_website_reference_select.py when website-template intent is present",
        ),
        next_actions=(
            "Treat every output as a separate reference-led cycle.",
            "Do not begin the next output until the current output plus its own design-system board pass quality, validation, and similarity gates.",
            "Record what scaffold/pattern was disposed before planning the next item.",
        ),
    ),
    IntentRule(
        name="naming",
        keywords=(
            "nama",
            "title",
            "item name",
            "branding name",
            "nama template",
            "template name",
            "name",
            "judul",
        ),
        workflows=(
            "Template Naming Ledger",
            "Name Check",
        ),
        source_files=(
            ".design-brain/TEMPLATE_NAMING_LEDGER.md",
            ".design-brain/ORIGINALITY_GUARD.md",
            ".design-brain/USER_DESIGN_CONTEXT.md",
        ),
        tools=(
            "scripts/design_brain_name_check.py",
        ),
        next_actions=(
            "Check naming patterns before committing to a name.",
            "Avoid repeated prefixes, suffixes, metaphors, and rhythms from previous templates.",
            "Offer several name candidates when the user asks for naming.",
        ),
    ),
    IntentRule(
        name="review",
        keywords=(
            "cek",
            "check",
            "review",
            "critique",
            "kritik",
            "terlalu mirip",
            "kurang premium",
            "generic",
            "spacing aneh",
            "struktur sama",
            "identik",
            "copy-paste",
            "copy paste",
            "sama dengan referensi",
            "improve",
            "perbaiki",
            "buat lebih premium",
        ),
        workflows=(
            "Design Critic",
            "Visual Review if evidence exists",
            "Sequential Batch Similarity if multiple templates",
            "Reflection if useful feedback",
        ),
        source_files=(
            ".agents/skills/design-critic/SKILL.md",
            ".design-brain/VISUAL_CRITIQUE_CHECKLIST.md",
            ".design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md",
            ".design-brain/ORIGINALITY_GUARD.md",
            ".design-brain/ORIGINALITY_SIMILARITY_SCORECARD.md",
            ".design-brain/HUMAN_CRAFT_HEURISTICS.md",
        ),
        tools=(
            "scripts/design_brain_review.py",
            "scripts/design_brain_visual_review.py",
            "scripts/design_brain_originality_score.py when similarity risk can be summarized",
            "scripts/design_brain_reflect.py only for real user feedback worth preserving",
        ),
        next_actions=(
            "Identify the highest-impact design issues first.",
            "Use visual evidence when available before claiming visual review.",
            "Make concrete revisions when editable files are available.",
        ),
    ),
    IntentRule(
        name="preview",
        keywords=(
            "cover",
            "preview",
            "overview",
            "mockup",
            "section breakdown",
            "responsive preview",
            "marketplace cover",
        ),
        workflows=(
            "Template Orchestrator",
            "Marketplace Preview direction",
            "Perspective/Bento style guidance",
        ),
        source_files=(
            ".design-brain/PREVIEW_PRESENTATION_SYSTEM.md",
            ".design-brain/MARKETPLACE_QUALITY_GATE.md",
            ".design-brain/TEMPLATE_ORCHESTRATOR.md",
            ".design-brain/PATTERN_LIBRARY.md",
        ),
        tools=(
            "scripts/design_brain_template_orchestrate.py",
            "scripts/design_brain_visual_review.py",
        ),
        next_actions=(
            "Plan cover, overview, section breakdown, mockup, and responsive preview as a selling system.",
            "Make the product inspectable instead of hiding it behind decoration.",
            "Use perspective or bento guidance only when it helps communicate value.",
        ),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Route a natural design task into Design Brain workflows.")
    parser.add_argument("--task", required=True, help="Natural-language user task.")
    parser.add_argument("--has-reference", action="store_true", help="Force reference intent on.")
    parser.add_argument("--template-count", type=int, default=None, help="Number of templates requested.")
    parser.add_argument("--needs-naming", action="store_true", help="Force naming intent on.")
    parser.add_argument("--needs-review", action="store_true", help="Force review intent on.")
    parser.add_argument("--output", default="", help="Optional markdown output path.")
    parser.add_argument("--dry-run", action="store_true", help="Print the report without writing it.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


BATCH_NUMBER_TERMS = {
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "dua",
    "tiga",
    "empat",
    "lima",
    "enam",
    "tujuh",
    "delapan",
    "sembilan",
    "sepuluh",
    "beberapa",
    "banyak",
    "multiple",
    "several",
}

BATCH_OUTPUT_NOUNS = (
    "template",
    "design",
    "desain",
    "gambar design",
    "gambar desain",
    "varian",
    "variasi",
    "versi",
    "section",
    "bagian",
    "screen",
    "page",
    "halaman",
    "output",
    "landing page",
)

SEQUENTIAL_TERMS = (
    "satu per satu",
    "1 per 1",
    "one by one",
    "masing-masing",
    "tiap",
    "per template",
    "per desain",
    "per design",
    "per gambar",
)


def slugify(text: str, limit: int = 72) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if not slug:
        return "design-task"
    return slug[:limit].strip("-") or "design-task"


def contains_output_noun(task_text: str) -> bool:
    return any(noun in task_text for noun in BATCH_OUTPUT_NOUNS)


def contains_batch_number(task_text: str) -> bool:
    for term in BATCH_NUMBER_TERMS:
        if term.isdigit():
            if re.search(rf"\b{re.escape(term)}\b", task_text):
                return True
        elif re.search(rf"\b{re.escape(term)}\b", task_text):
            return True
    return False


def task_mentions_sequential_batch(task_text: str) -> bool:
    return contains_output_noun(task_text) and any(term in task_text for term in SEQUENTIAL_TERMS)


def task_mentions_multiple_templates(task_text: str, template_count: int | None) -> bool:
    if template_count and template_count > 1:
        return True
    if contains_batch_number(task_text) and contains_output_noun(task_text):
        return True
    if task_mentions_sequential_batch(task_text):
        return True
    if re.search(r"\b\d+\s*(template|templates|landing|page|screen|cover|preview)", task_text):
        return True
    if re.search(
        r"\b\d+\s+(?:[a-z0-9_-]+\s+){0,4}(template|templates|landing|pages|screens|covers|previews|website|websites|deck|decks|slide|slides)",
        task_text,
    ):
        return True
    if re.search(r"\b(link|figma|file|url)\s*\d+\s*(,|dan|&|\+)\s*\d+", task_text):
        return True
    return False


def detect_intents(args: argparse.Namespace) -> list[IntentRule]:
    task_text = normalize(args.task)
    detected: list[IntentRule] = []
    artifact = artifact_intent(args.task)

    for rule in INTENT_RULES:
        if rule.name == "web_deck" and artifact == "native":
            continue
        if rule.name == "native_pptx" and artifact == "web":
            continue
        if any(keyword in task_text for keyword in rule.keywords) or (rule.name == "native_pptx" and artifact in {"native", "both"}):
            detected.append(rule)

    forced_names = set()
    if args.has_reference:
        forced_names.add("reference")
    if args.needs_naming:
        forced_names.add("naming")
    if args.needs_review:
        forced_names.add("review")
    if task_mentions_multiple_templates(task_text, args.template_count):
        forced_names.add("batch")
    if task_mentions_sequential_batch(task_text):
        forced_names.add("sequential_batch")
        forced_names.add("batch")
    if args.template_count and args.template_count > 0:
        forced_names.add("template_product")

    for rule in INTENT_RULES:
        if rule.name in forced_names and rule not in detected:
            detected.append(rule)

    if not detected and any(word in task_text for word in ("design", "ui", "figma", "web", "css", "dashboard", "landing", "powerpoint", "presentation", "slides", "deck", "brand")):
        detected.append(next(rule for rule in INTENT_RULES if rule.name == "template_product"))

    return detected


def unique_lines(groups: list[tuple[str, ...]]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for group in groups:
        for item in group:
            if item not in seen:
                seen.add(item)
                result.append(item)
    return result


def bullet(items: list[str]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def trigger_map_status(root: Path) -> str:
    path = root / ".design-brain" / "WORKFLOW_TRIGGER_MAP.md"
    if not path.exists():
        return "- Trigger map: missing; used built-in deterministic keyword map."
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return f"- Trigger map: found but unreadable ({exc}); used built-in deterministic keyword map."
    line_count = len(text.splitlines())
    return f"- Trigger map: loaded `.design-brain/WORKFLOW_TRIGGER_MAP.md` ({line_count} lines)."


def natural_response(task: str, intent_names: list[str]) -> str:
    if "reference" in intent_names and "batch" in intent_names:
        return (
            "Paham. Ini reference-based batch template task. Aku akan kerjakan satu per satu: "
            "pilih active product-purpose reference group untuk template pertama, gunakan hingga 10 referensi eligible yang variatif bila kandidat lokal cukup, pelajari tujuan, audiens, struktur, "
            "visual logic, effect/gradient, surface depth, dan color-role system-nya, "
            "bangun satu template penuh, screenshot-check kualitasnya, lalu kunci polanya sebelum "
            "mengulang proses dari awal untuk template berikutnya."
        )
    if "naming" in intent_names:
        return (
            "Paham. Ini naming task. Aku akan cek pola nama sebelumnya, lalu usulkan nama yang terasa "
            "segar, sesuai niche, dan tidak terdengar seperti daur ulang."
        )
    if "review" in intent_names and "batch" in intent_names:
        return (
            "Paham. Ini batch review. Aku akan mencari kemiripan struktur, bagian yang terasa generic, "
            "effect/gradient yang kurang hidup, color-role yang terlalu dekat, dan titik yang perlu "
            "dibuat lebih premium sebelum memberi revisi konkret."
        )
    if "figma_reference" in intent_names:
        return (
            "Paham. Ini Figma-reference study. Aku akan membaca skema Figma-nya sebagai sistem template "
            "lengkap, bukan screenshot datar: page, frame, komponen, state, standar produk, lalu baru "
            "membangun rekonstruksi yang original."
        )
    if "reference" in intent_names:
        return (
            "Paham. Ini reference-based design task. Aku akan mengambil logika visual dan insightnya, "
            "bukan menyalin layout, lalu mengubahnya menjadi arah desain baru."
        )
    if "preview" in intent_names:
        return (
            "Paham. Ini marketplace preview task. Aku akan memikirkan cover, overview, mockup, dan "
            "responsive preview sebagai satu sistem presentasi produk."
        )
    if "figma_output" in intent_names:
        return (
            "Paham. Aku akan pakai target Figma yang sudah dikonfigurasi bila valid, lalu "
            "menjalankan workflow website-template Design Brain, auto-layout enforcement, placeholder policy, dan quality gate sebelum membangun visualnya."
        )
    if "medium_product" in intent_names:
        return (
            "Paham. Aku akan menentukan mediumnya dulu, lalu memilih struktur, style grammar, "
            "dan quality gate yang sesuai supaya tidak semua task berubah jadi landing page generic."
        )
    if "template_product" in intent_names:
        return (
            "Paham. Ini template product task. Aku akan tentukan buyer, struktur, style direction, "
            "editable area, dan quality gate sebelum masuk ke visual."
        )
    return (
        "Paham. Aku akan membaca intent desainnya, memilih workflow Design Brain yang relevan, "
        "dan menjaga hasilnya tetap natural tanpa meminta kamu mengingat command internal."
    )


def what_not_to_do(intent_names: list[str]) -> list[str]:
    items = [
        "Do not ask the user to choose internal workflow names when intent is clear.",
        "Do not expose command details unless they help explain or verify the work.",
        "Do not modify `.design-brain/DESIGN_MEMORY.md` or `.design-brain/DESIGN_PREFERENCES.json` values.",
        "Do not add fake journal entries.",
        "Do not promote memory automatically.",
    ]
    if "reference" in intent_names:
        items.append("Do not copy the reference layout, section order, composition, or component grouping one-to-one.")
    if "figma_reference" in intent_names:
        items.append("Do not use a Figma reference without a Figma reference schema receipt.")
        items.append("Do not default to minimalist or a short safe structure when the Figma product standard is unclear.")
        items.append("Do not ignore nested pages, frames, component sets, variants, states, or design-system panels.")
    if "medium_product" in intent_names:
        items.append("Do not apply landing-page structure to PowerPoint decks, dashboards, UI kits, brand kits, or preview covers.")
    if "figma_output" in intent_names:
        items.append("Do not use placeholder Figma project IDs for `create_new_file`; treat placeholder targets as not configured.")
        items.append("Do not ask for the default Figma project link again when a valid configured target exists, unless file creation fails or the user asks for another destination.")
        items.append("Do not force the Figma target when the user explicitly asks for local code, PowerPoint, Slides, FigJam, or another medium.")
        items.append("Do not build Figma template source structure primarily with manual x/y positioning, skip the auto-layout receipt, or send invalid Figma API alignment values such as END for primaryAxisAlignItems/counterAxisAlignItems.")
    if "batch" in intent_names:
        items.append("Do not create one global batch scaffold or study all references once for the whole batch.")
        items.append("Do not create multiple templates that only differ by color, copy, or superficial styling.")
        items.append("Do not start the next template until the current template plus its own design-system board are complete, checked, and pattern-locked.")
        items.append("Do not reach 10 percent similarity against any accepted previous template fingerprint.")
    if "review" in intent_names:
        items.append("Do not claim visual inspection happened unless screenshot, browser, or rendered evidence was actually inspected.")
    return items


def build_report(args: argparse.Namespace, root: Path) -> str:
    detected = detect_intents(args)
    intent_names = [rule.name for rule in detected]

    workflows = unique_lines([rule.workflows for rule in detected])
    source_files = unique_lines([COMMON_SOURCE_FILES] + [rule.source_files for rule in detected])
    tools = unique_lines([rule.tools for rule in detected])
    next_actions = unique_lines([rule.next_actions for rule in detected])

    if not detected:
        next_actions = [
            "Ask one concise clarification because no confident Design Brain workflow intent was detected.",
        ]

    lines = [
        "# Natural Intent Decision",
        "",
        "## Task",
        "",
        args.task,
        "",
        "## Router Context",
        "",
        trigger_map_status(root),
        f"- Has reference flag: {'yes' if args.has_reference else 'no'}",
        f"- Template count: {args.template_count if args.template_count is not None else 'not specified'}",
        f"- Needs naming flag: {'yes' if args.needs_naming else 'no'}",
        f"- Needs review flag: {'yes' if args.needs_review else 'no'}",
        "",
        "## Detected Intents",
        "",
        bullet(intent_names),
        "",
        "## Triggered Workflows",
        "",
        bullet(workflows),
        "",
        "## Source-Of-Truth Files To Load",
        "",
        bullet(source_files),
        "",
        "## Internal Scripts Or Tools",
        "",
        bullet(tools),
        "",
        "## What Codex Should Do Next",
        "",
        bullet(next_actions),
        "",
        "## What Codex Should Not Do",
        "",
        bullet(what_not_to_do(intent_names)),
        "",
        "## Natural Response Framing",
        "",
        natural_response(args.task, intent_names),
        "",
    ]
    return "\n".join(lines)


def default_output_path(root: Path, task: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = slugify(task)
    return root / ".design-brain" / "context-packets" / f"{stamp}-intent-decision-{slug}.md"


def main() -> int:
    args = parse_args()
    root = repo_root()
    report = build_report(args, root)

    print(report)

    if args.dry_run:
        return 0

    output_path = Path(args.output).expanduser() if args.output else default_output_path(root, args.task)
    if not output_path.is_absolute():
        output_path = (Path.cwd() / output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8", newline="\n")
    print(f"Saved intent decision report: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
