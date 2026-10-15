#!/usr/bin/env python
"""Generate task-specific source-of-truth loading packets for Design Brain."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

from design_brain_modules import build_selection


TIER_1_FILES = [
    ".design-brain/DESIGN_SOUL.md",
    ".design-brain/DESIGN_IDENTITY.md",
    ".design-brain/USER_DESIGN_CONTEXT.md",
    ".design-brain/DESIGN_PRINCIPLES.md",
    ".design-brain/DESIGN_OPERATING_RULES.md",
    ".design-brain/AUTOLOAD_POLICY.md",
    ".design-brain/DESIGNER_COGNITION_LAYER.md",
    ".design-brain/CONTEXT_PRIORITY.md",
]

REFERENCE_FILES = [
    ".design-brain/DESIGNER_COGNITION_LAYER.md",
    ".design-brain/FIGMA_REFERENCE_DEEP_STUDY.md when the reference is a Figma link, Figma frame, Figma template file, or .fig source",
    ".design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md when the reference is a Figma template or professional designer learning material",
    ".design-brain/FIGMA_REFERENCE_LEARNING_CORPUS.md when using the user-provided Figma material links",
    ".design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md",
    ".design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md",
    ".design-brain/REFERENCE_INSIGHT_SYSTEM.md",
    ".design-brain/REFERENCE_DECONSTRUCTION_MATRIX.md",
    ".design-brain/REFERENCE_INSIGHT_JOURNAL.md",
    ".design-brain/ORIGINALITY_GUARD.md",
    ".design-brain/ORIGINALITY_SIMILARITY_SCORECARD.md",
    ".design-brain/TEMPLATE_BUILD_JOURNAL.md",
    ".design-brain/TEMPLATE_NAMING_LEDGER.md",
]

TEMPLATE_FILES = [
    ".design-brain/TEMPLATE_ORCHESTRATOR.md",
    ".design-brain/TEMPLATE_PRODUCT_INTELLIGENCE.md",
    ".design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md",
    ".design-brain/FIGMA_OUTPUT_TARGET.md when Figma or natural website-template design output is implied",
    ".design-brain/FIGMA_REFERENCE_DEEP_STUDY.md when a Figma reference/link/template source is used",
    ".design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md when a Figma reference/link/template source is used",
    ".design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md when Figma/source-template output is implied",
    ".design-brain/MEDIUM_PRODUCT_PLAYBOOKS.md",
    ".design-brain/ADVANCED_STYLE_GRAMMAR_MATRIX.md",
    ".design-brain/HUMAN_CRAFT_HEURISTICS.md",
    ".design-brain/TEMPLATE_STYLE_ROUTER.md",
    ".design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md",
    ".design-brain/TEMPLATE_BUILD_JOURNAL.md",
    ".design-brain/TEMPLATE_NAMING_LEDGER.md",
]

PRESENTATION_FILES = [
    "skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md",
]

NAMING_FILES = [
    ".design-brain/TEMPLATE_NAMING_LEDGER.md",
    ".design-brain/USER_DESIGN_CONTEXT.md",
    ".design-brain/DESIGN_PRINCIPLES.md",
    ".design-brain/ORIGINALITY_GUARD.md",
]

REVIEW_FILES = [
    ".agents/skills/design-critic/SKILL.md",
    ".design-brain/VISUAL_CRITIQUE_CHECKLIST.md",
    ".design-brain/DESIGNER_COGNITION_LAYER.md",
    ".design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md",
    ".design-brain/FIGMA_REFERENCE_DEEP_STUDY.md when reviewing a Figma-reference-led template",
    ".design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md when reviewing a Figma-reference-led template",
    ".design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md when reviewing Figma source templates",
    ".design-brain/ORIGINALITY_GUARD.md",
    ".design-brain/ORIGINALITY_SIMILARITY_SCORECARD.md",
    ".design-brain/HUMAN_CRAFT_HEURISTICS.md",
]

REFERENCE_KEYWORDS = [
    "reference",
    "screenshot",
    "visual reference",
    "figma reference",
    "figma.com",
    "link figma",
    ".fig",
    "website reference",
    "use this as reference",
    "ambil insight",
    "jangan identik",
    "buat seperti arah ini",
    "not copy",
    "reinterpret",
]

TEMPLATE_KEYWORDS = [
    "template",
    "marketplace",
    "envato",
    "figma",
    "figma template",
    "create new design",
    "design template di figma",
    "design template website",
    "landing page template",
    "dashboard template",
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
    "ui kit",
    "design system",
    "brand kit",
    "branding",
    "portfolio",
    "cover",
    "preview",
    "design overview",
    "mockup preview",
]

NAMING_KEYWORDS = ["name", "naming", "title", "brand name", "template name"]
REVIEW_KEYWORDS = ["review", "critique", "audit", "evaluate", "quality gate"]
PRESENTATION_KEYWORDS = ["powerpoint", "presentation", "pitch deck", "deck", "slides", "google slide", "keynote", "ppt", "pptx"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a Design Brain context packet.")
    parser.add_argument("--task", required=True, help="Task description.")
    parser.add_argument("--reference", action="store_true", help="Mark the task as reference-based.")
    parser.add_argument("--template-type", default="", help="Template product type.")
    parser.add_argument("--niche", default="", help="Template niche.")
    parser.add_argument("--target-buyer", default="", help="Template target buyer.")
    parser.add_argument("--visual-mood", default="", help="Visual mood or style direction.")
    parser.add_argument("--naming", action="store_true", help="Mark the task as naming-related.")
    parser.add_argument("--review", action="store_true", help="Mark the task as review/critique-related.")
    parser.add_argument("--output", default="", help="Optional output markdown path.")
    parser.add_argument("--dry-run", action="store_true", help="Print packet without saving.")
    return parser.parse_args()


def design_brain_root() -> Path:
    return Path(__file__).resolve().parents[1]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "context-packet"


def has_any(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)


def has_figma_intent(args: argparse.Namespace) -> bool:
    text = " ".join([args.task, args.template_type, args.niche]).lower()
    return has_any(
        text,
        [
            "figma",
            "figma template",
            "create new design",
            "design template di figma",
            "design template website",
            "buat design template",
            "bikin template website",
        ],
    )


def has_figma_reference_intent(args: argparse.Namespace) -> bool:
    text = " ".join([args.task, args.template_type, args.niche, args.visual_mood]).lower()
    if "figma.com" in text or ".fig" in text:
        return True
    return "figma" in text and has_any(
        text,
        [
            "reference",
            "referensi",
            "contoh",
            "link",
            "frame",
            "template source",
            "study",
            "pelajari",
            "ambil insight",
        ],
    )


def infer_triggers(args: argparse.Namespace) -> list[str]:
    triggers: list[str] = []
    task = " ".join([args.task, args.template_type, args.niche])
    if args.reference or has_any(task, REFERENCE_KEYWORDS):
        triggers.append("Reference-based design")
    if args.template_type or has_any(task, TEMPLATE_KEYWORDS):
        triggers.append("Template product design")
    if has_any(task, PRESENTATION_KEYWORDS):
        triggers.append("Presentation deck design")
    if args.naming or has_any(task, NAMING_KEYWORDS):
        triggers.append("Naming/title task")
    if args.review or has_any(task, REVIEW_KEYWORDS):
        triggers.append("Review/critique task")
    if not triggers:
        triggers.append("Small edit / general design task")
    return triggers


def unique(items: list[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def files_to_load(triggers: list[str], args: argparse.Namespace) -> list[str]:
    files = list(TIER_1_FILES)
    if "Reference-based design" in triggers:
        files.extend(REFERENCE_FILES)
    if "Template product design" in triggers:
        files.extend(TEMPLATE_FILES)
    if "Presentation deck design" in triggers:
        files.extend(PRESENTATION_FILES)
    if "Naming/title task" in triggers:
        files.extend(NAMING_FILES)
    if "Review/critique task" in triggers:
        files.extend(REVIEW_FILES)
        if "Reference-based design" in triggers:
            files.append(".design-brain/REFERENCE_INSIGHT_JOURNAL.md")
    if has_figma_reference_intent(args):
        files.extend(
            [
                ".design-brain/FIGMA_REFERENCE_DEEP_STUDY.md",
                ".design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md",
                ".design-brain/templates/FIGMA_REFERENCE_SCHEMA_RECEIPT.md",
            ]
        )
    return unique(files)


def journals_to_check(triggers: list[str]) -> list[str]:
    journals: list[str] = []
    if "Reference-based design" in triggers:
        journals.append(".design-brain/REFERENCE_INSIGHT_JOURNAL.md")
    if "Template product design" in triggers:
        journals.append(".design-brain/TEMPLATE_BUILD_JOURNAL.md")
    if "Naming/title task" in triggers or "Template product design" in triggers:
        journals.append(".design-brain/TEMPLATE_NAMING_LEDGER.md")
    if "Review/critique task" in triggers:
        journals.append(".design-brain/REFLECTION_LOG.md")
    return unique(journals)


def command_quote(value: str) -> str:
    return '"' + value.replace('"', '\\"') + '"'


def build_command(base: str, pairs: list[tuple[str, str]]) -> str:
    parts = [base]
    for flag, value in pairs:
        if value:
            parts.extend([flag, command_quote(value)])
    return " ".join(parts)


def next_commands(args: argparse.Namespace, triggers: list[str]) -> list[str]:
    task_name = args.task
    template_type = args.template_type or "TEMPLATE_TYPE"
    niche = args.niche or "NICHE"
    commands: list[str] = []

    if "Reference-based design" in triggers:
        if re.search(r"\b(website|web template|homepage|saas|ecommerce|shop|store|portfolio|agency|blog|docs|dashboard|admin|event|travel|service)\b", " ".join([task_name, template_type, niche]).lower()):
            commands.append(
                build_command(
                    "python scripts/design_brain_website_reference_select.py",
                    [
                        ("--task", task_name),
                        ("--template-type", template_type),
                        ("--niche", niche),
                        ("--target-buyer", args.target_buyer),
                    ],
                )
                + " --dry-run"
            )
        commands.append(
            build_command(
                "python scripts/design_brain_reference_insight.py",
                [
                    ("--reference-name", "REFERENCE_NAME"),
                    ("--template-category", f"{niche} {template_type}"),
                    ("--buyer-decision-model", "BUYER_DECISION_MODEL"),
                    ("--cognition-evidence", "OBSERVED_EVIDENCE_INFERRED_REASON_EFFECT_TRANSFORMATION_CONFIDENCE"),
                    ("--attention-strategy", "ATTENTION_FLOW"),
                    ("--emotional-rhythm", "CALM_DENSE_BOLD_QUIET_MOMENTS"),
                    ("--trust-strategy", "CREDIBILITY_LOGIC"),
                    ("--density-strategy", "WHERE_DETAIL_IS_ADDED_OR_REMOVED_AND_WHY"),
                    ("--conversion-logic", "HOW_VIEWER_MOVES_TOWARD_ACTION"),
                    ("--component-reasoning", "WHY_COMPONENTS_ARE_USED"),
                    ("--lesson", "REUSABLE_REFERENCE_LESSON"),
                    ("--do-not-copy", "REFERENCE_DETAILS_TO_AVOID"),
                    ("--reinterpretation", "HOW_TO_REINTERPRET_STRUCTURE"),
                ],
            )
            + " --dry-run"
        )

    if "Template product design" in triggers:
        commands.append(
            build_command(
                "python scripts/design_brain_module_select.py",
                [
                    ("--task", task_name),
                    ("--template-type", template_type),
                    ("--niche", niche),
                    ("--target-buyer", args.target_buyer),
                    ("--visual-mood", args.visual_mood),
                ],
            )
            + " --dry-run"
        )
        commands.append(
            build_command(
                "python scripts/design_brain_medium_playbook.py",
                [
                    ("--task", task_name),
                    ("--template-type", template_type),
                    ("--niche", niche),
                    ("--target-buyer", args.target_buyer),
                    ("--visual-mood", args.visual_mood),
                ],
            )
            + " --dry-run"
        )
        commands.append(
            build_command(
                "python scripts/design_brain_template_orchestrate.py",
                [
                    ("--template-type", template_type),
                    ("--niche", niche),
                    ("--notes", task_name),
                ],
            )
        )

    if "Naming/title task" in triggers:
        commands.append(
            build_command(
                "python scripts/design_brain_name_check.py",
                [
                    ("--candidate-name", "CANDIDATE_NAME"),
                    ("--niche", niche),
                    ("--template-type", template_type),
                ],
            )
            + " --dry-run"
        )

    if "Review/critique task" in triggers:
        commands.append(
            build_command(
                "python scripts/design_brain_review.py",
                [
                    ("--task", task_name),
                    ("--target", "TARGET_FILE_OR_SCREEN"),
                    ("--notes", "Use source-of-truth identity, originality guard, and marketplace quality gate."),
                ],
            )
        )
        commands.append(
            build_command(
                "python scripts/design_brain_visual_review.py",
                [
                    ("--task", task_name),
                    ("--target", "TARGET_FILE_OR_SCREEN"),
                    ("--notes", "Inspect visual evidence before filling this report."),
                ],
            )
        )
        commands.append(
            build_command(
                "python scripts/design_brain_originality_score.py",
                [
                    ("--reference-summary", "REFERENCE_STRUCTURE_SUMMARY"),
                    ("--proposed-structure", "PROPOSED_STRUCTURE_SUMMARY"),
                    ("--template-type", template_type),
                ],
            )
            + " --dry-run"
        )

    commands.append(
        build_command(
            "python scripts/design_brain_reflect.py",
            [
                ("--task", task_name),
                ("--feedback", "USER_FEEDBACK"),
                ("--went-wrong", "WHAT_WENT_WRONG"),
                ("--lesson", "REUSABLE_LESSON"),
                ("--rule", "RULE_TO_REUSE"),
            ],
        )
    )

    if "Template product design" in triggers:
        commands.append(
            build_command(
                "python scripts/design_brain_build_record.py",
                [
                    ("--template-name", "FINAL_TEMPLATE_NAME"),
                    ("--template-type", template_type),
                    ("--niche", niche),
                    ("--related-report", "RELATED_REPORT_PATH"),
                ],
            )
        )

    return commands


def files_not_loaded(triggers: list[str]) -> list[str]:
    skipped: list[str] = []
    if "Reference-based design" not in triggers:
        skipped.append("Reference insight journals: no reference trigger was detected.")
    if "Template product design" not in triggers:
        skipped.append("Template orchestrator/product files: no template product trigger was detected.")
    if "Presentation deck design" not in triggers:
        skipped.append("Presentation Deck Intelligence: no PowerPoint/deck trigger was detected.")
    if "Naming/title task" not in triggers:
        skipped.append("Naming ledger details: no naming trigger was detected beyond basic context.")
    if "Review/critique task" not in triggers:
        skipped.append("Review reports and visual review workflow: no critique trigger was detected.")
    skipped.append("Generated reports: load only latest relevant reports when needed.")
    return skipped


def bullet_list(items: list[str]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def fenced_commands(commands: list[str]) -> str:
    if not commands:
        return "None"
    return "\n\n".join(f"```bash\n{command}\n```" for command in commands)


def build_packet(args: argparse.Namespace, triggers: list[str]) -> str:
    selection = build_selection(
        task=args.task,
        template_type=args.template_type,
        niche=args.niche,
        target_buyer=args.target_buyer,
        visual_mood=args.visual_mood,
    )
    loaded = files_to_load(triggers, args)
    if "Template product design" in triggers or "Presentation deck design" in triggers:
        loaded = unique(loaded + selection.get("sourceFiles", []))
    journals = journals_to_check(triggers)
    commands = next_commands(args, triggers)

    reference_summary = (
        "Reference trigger detected. Inspect the reference, extract intent and reusable design logic, record do-not-copy notes, and reinterpret structure before designing."
        if "Reference-based design" in triggers
        else "No reference trigger detected. Do not invent reference insight."
    )
    template_intent = (
        f"Template type: {args.template_type or 'Not specified'}; niche: {args.niche or 'Not specified'}."
        if "Template product design" in triggers
        else "No template product trigger detected."
    )
    figma_auto_layout = (
        "Figma auto-layout enforcement active. Build editable structure with real auto-layout and include an auto-layout/API-alignment receipt; use absolute positioning only for documented decorative or overlay exceptions. Normalize Figma Plugin API alignment values before use_figma: END becomes MAX, START becomes MIN, and stretch behavior uses child sizing FILL."
        if has_figma_intent(args)
        else "Figma auto-layout enforcement not triggered by this packet."
    )
    figma_reference_study = (
        "Figma reference deep-study active. Inspect product purpose, visual direction, section structure, grid/layout, typography hierarchy, color roles, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, Figma source hygiene, file/page/frame/component/state scheme, infer product-family standard, create a Figma reference schema receipt, and do not default to minimalist if the standard is unclear."
        if has_figma_reference_intent(args)
        else "Figma reference deep-study not triggered by this packet."
    )
    medium_intent = (
        "Presentation deck trigger detected. Use slide-role matrix, slide master/layout thinking, safe margins, chart/table rules, and thumbnail readability."
        if "Presentation deck design" in triggers
        else "Use medium playbook when the task names a product type such as website, deck, dashboard, UI kit, brand kit, portfolio, or preview."
    )
    naming_risk = (
        "Naming trigger detected. Check TEMPLATE_NAMING_LEDGER.md and run name check before finalizing."
        if "Naming/title task" in triggers
        else "No explicit naming trigger. Still avoid recycled names if a template name appears."
    )
    originality_risk = (
        "High originality sensitivity because reference/template/review cues are present. Use ORIGINALITY_GUARD.md."
        if any(trigger in triggers for trigger in ["Reference-based design", "Template product design", "Review/critique task"])
        else "Normal originality risk."
    )
    style_direction = (
        "Use Template Style Router and selected TypeUI-derived style packs only; do not activate all styles."
        if "Template product design" in triggers
        else "No style router needed unless task becomes a template product."
    )

    return f"""# Design Context Packet

Generated: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z%z')}

## Task

{args.task}

## Trigger Type

{bullet_list(triggers)}

## Loaded Source-Of-Truth Files

{bullet_list(loaded)}

## Design-Anything Module Selection

- Selected module: {selection.get('moduleId', 'unknown')}
- Seed pack: {selection.get('seedPack') or 'None'}
- Direction pack: {selection.get('directionPack') or 'None'}

### Craft Modules

{bullet_list(selection.get('requiredCraft', []))}

### Validation Gates

{bullet_list(selection.get('validators', []))}

## Relevant Journals Checked

{bullet_list(journals)}

## Reference Insight Summary

{reference_summary}

## Template Product Intent

{template_intent}

## Figma Auto-Layout Enforcement

{figma_auto_layout}

## Figma Reference Deep Study

{figma_reference_study}

## Medium/Product-Type Intent

{medium_intent}

## Naming Risk

{naming_risk}

## Originality Risk

{originality_risk}

## Style / Router Direction

{style_direction}

## Required Next Workflow

{fenced_commands(commands)}

## Files Not Loaded And Why

{bullet_list(files_not_loaded(triggers))}

## Provenance Note

This packet is a loading plan. It does not modify journals, does not invent insight, and does not replace the source-of-truth files.
"""


def output_path(args: argparse.Namespace, root: Path) -> Path:
    if args.output:
        return Path(args.output).expanduser().resolve()
    filename = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slugify(args.task)}.md"
    return root / ".design-brain" / "context-packets" / filename


def main() -> int:
    args = parse_args()
    root = design_brain_root()
    autoload_path = root / ".design-brain" / "AUTOLOAD_POLICY.md"
    if not autoload_path.exists():
        print(f"WARNING: Missing autoload policy: {autoload_path}")

    triggers = infer_triggers(args)
    packet = build_packet(args, triggers)

    if args.dry_run:
        print(packet)
        return 0

    path = output_path(args, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(packet, encoding="utf-8", newline="\n")
    print(f"Design context packet written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
