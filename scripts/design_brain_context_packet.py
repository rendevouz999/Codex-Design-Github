#!/usr/bin/env python
"""Generate task-specific source-of-truth loading packets for Design Brain."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path

from design_brain_scope import presentation_mode, require_presentation
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
    ".design-brain/REFERENCE_CORPUS_CONFIG.md",
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
    ".design-brain/FIGMA_OUTPUT_TARGET.md when explicit Figma presentation output is requested",
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
    parser.add_argument("--stage", choices=["planning", "authoring", "review", "delivery", "diagnostic"], default="planning")
    parser.add_argument("--reference", action="store_true", help="Mark the task as reference-based.")
    parser.add_argument("--template-type", default="", help="Template product type.")
    parser.add_argument("--niche", default="", help="Template niche.")
    parser.add_argument("--target-buyer", default="", help="Template target buyer.")
    parser.add_argument("--visual-mood", default="", help="Visual mood or style direction.")
    parser.add_argument("--naming", action="store_true", help="Mark the task as naming-related.")
    parser.add_argument("--review", action="store_true", help="Mark the task as review/critique-related.")
    parser.add_argument("--output", default="", help="Optional output markdown path.")
    parser.add_argument("--dry-run", action="store_true", help="Print packet without saving.")
    parser.add_argument("--phase", choices=("plan", "build", "repair", "final"), default="plan")
    parser.add_argument("--role", choices=("main", "engineer"), default="main")
    parser.add_argument("--context-epoch", default="", help="New caller-supplied epoch after host compact/resume/context loss")
    parser.add_argument("--manifest-output", default="", help="Opt-in phase/hash loading manifest JSON")
    parser.add_argument("--previous-manifest", default="", help="Prior loading plan, never proof of retained model knowledge")
    parser.add_argument("--manifest-summary", action="store_true", help="Print bounded loading delta/pointers instead of the full dry-run packet; requires --manifest-output")
    parser.add_argument("--navigation", choices=("on", "off"), default="off", help="Optional advisory source navigation")
    parser.add_argument("--navigation-session", default="", help="Explicit private project namespace")
    parser.add_argument("--navigation-cache-dir", default="")
    parser.add_argument("--navigation-memory-discovery", default="", help="Existing adapter discovery JSON inside explicit session")
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
    """Require a Figma target; preserve authoring support when its target is ambiguous."""
    text = " ".join([args.task, args.template_type, args.niche, getattr(args, "visual_mood", "")]).lower()
    if re.search(r"\b(?:to|as|output|deliver|export|save)\s+(?:[\w./-]+)?\.fig\b", text):
        return True
    if "figma" not in text and not re.search(r"\.fig\b", text):
        return False
    if not has_figma_reference_intent(args):
        return True
    if re.search(
        r"\b(?:in|to|di|ke|as)\s+figma\b|\bfigma\s+(?:(?:presentation|deck|template)\s+)?output\b|"
        r"\b(?:create|build|make|buat|bikin)\s+(?:(?:a|an|new|editable)\s+)*figma\b|"
        r"\b(?:output|deliver|export|save|format)\b[^.;\n]{0,40}\bfigma\b", text):
        return True
    # A Figma reference is not itself a Figma deliverable when another target is explicit.
    return presentation_mode(f"{args.task} {args.template_type}") not in {"native", "web", "both"} and not has_any(
        text, ["google slide", "keynote", "pdf"])


def has_figma_reference_intent(args: argparse.Namespace) -> bool:
    text = " ".join([args.task, args.template_type, args.niche, args.visual_mood]).lower()
    if "figma.com" in text or re.search(r"\.fig\b", text):
        return True
    return "figma" in text and (getattr(args, "reference", False) or has_any(
        text,
        [
            "reference",
            "referensi",
            "contoh",
            "link",
            "frame",
            "source",
            "from figma",
            "study",
            "pelajari",
            "ambil insight",
        ],
    ))


def applicable_sources(items: list[str], args: argparse.Namespace) -> list[str]:
    """Evaluate known Figma conditions; unknown sources remain full-read obligations."""
    figma_output = has_figma_intent(args)
    figma_study = has_figma_reference_intent(args) or figma_output
    professional_learning = figma_study or has_any(
        " ".join([args.task, args.template_type, args.niche, args.visual_mood]),
        ["professional designer", "designer learning material", "professional template learning"])
    conditions = {
        ".design-brain/FIGMA_OUTPUT_TARGET.md": figma_output,
        ".design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md": figma_output,
        ".design-brain/FIGMA_REFERENCE_DEEP_STUDY.md": figma_study,
        ".design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md": professional_learning,
        ".design-brain/FIGMA_REFERENCE_LEARNING_CORPUS.md": figma_study,
        ".design-brain/templates/FIGMA_REFERENCE_SCHEMA_RECEIPT.md": figma_study,
    }
    return [label for label in unique(items) if conditions.get(label.split(" when ", 1)[0], True)]


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


def unique(items: list[str], root: Path | None = None) -> list[str]:
    """Deduplicate source paths, retaining unconditional reads over conditional labels."""
    result: dict[str, str] = {}
    base = root.resolve() if root is not None else None
    for item in items:
        name, _, condition = item.partition(" when ")
        if base is not None:
            path = (base / name).resolve()
            if Path(name).is_absolute() or not path.is_relative_to(base):
                raise ValueError("Packet source escapes plugin root")
            name = path.relative_to(base).as_posix()
        else:
            name = Path(name).as_posix()
        key = os.path.normcase(name)
        if key not in result or not condition:
            result[key] = name + (" when " + condition if condition else "")
    return list(result.values())


def loading_manifest(root: Path, files: list[str], task: str, role: str, phase: str,
                     epoch: str, previous: dict | None = None) -> dict:
    """Compare loading plans only. A hash cannot attest a read or host context retention."""
    if role not in {"main", "engineer"} or phase not in {"plan", "build", "repair", "final"}:
        raise ValueError("Invalid manifest role/phase")
    if not epoch.strip() or len(epoch) > 200 or len(task) > 12000 or len(files) > 200:
        raise ValueError("Manifest needs a bounded task/source list and explicit context epoch")
    identity = {"taskSha256": hashlib.sha256(task.encode()).hexdigest(), "role": role, "phase": phase, "contextEpoch": epoch}
    prior = previous or {}
    # Phase is navigation metadata; task, role and epoch delimit the retained context.
    same_context = all(prior.get(k) == identity[k] for k in ("taskSha256", "role", "contextEpoch"))
    old = {(root / item["path"]).resolve(): item.get("sha256") for item in prior.get("sources", [])
           if isinstance(item, dict) and isinstance(item.get("path"), str)} if same_context else {}
    sources = []
    for label in unique(files, root):
        name = label.split(" when ", 1)[0]
        path = (root / name).resolve()
        if Path(name).is_absolute() or not path.is_relative_to(root.resolve()):
            raise ValueError("Manifest source escapes plugin root")
        exists = path.is_file()
        digest = hashlib.sha256(path.read_bytes()).hexdigest() if exists and path.stat().st_size <= 4*1024*1024 else None
        # Whole policy documents mix authoring criteria and execution detail. Do not defer their criteria.
        action = "UNAVAILABLE" if digest is None else (
            "PRIOR_MANIFEST_ONLY" if old.get(path) == digest else "READ_REQUIRED")
        sources.append({"path": name, "condition": label[len(name):].strip(), "sha256": digest, "action": action})
    return {"schema": "design-brain.loading-manifest.v1", **identity, "sources": sources,
            "knowledge": "NOT_ASSERTED: this is a source loading plan, never a read receipt or proof of retained model knowledge.",
            "continuation": "PRIOR_MANIFEST_ONLY permits delta navigation only after the role confirms the source is still available in its current context. Otherwise read it. Change epoch after compact/resume/context loss; reload critical contract and applicable full guide.",
            "gates": "Authoring requirements and acceptance criteria load before build. All final gates remain active: first-three review when applicable, originality, editability/design system, target technical/render checks, actual final Main visual inspection, post-build/completion/lifecycle verification. Phase labels never waive a gate."}


def manifest_summary(manifest: dict, path: str | None, packet_path: str | None) -> dict:
    required = [item["path"] for item in manifest["sources"] if item["action"] == "READ_REQUIRED"]
    unavailable = [item["path"] for item in manifest["sources"] if item["action"] == "UNAVAILABLE"]
    return {"schema": "design-brain.loading-summary.v1", "role": manifest["role"], "phase": manifest["phase"],
            "contextEpoch": manifest["contextEpoch"], "taskSha256": manifest["taskSha256"],
            "sourceCount": len(manifest["sources"]), "readRequired": required, "unavailable": unavailable,
            "priorManifestOnlyCount": sum(item["action"] == "PRIOR_MANIFEST_ONLY" for item in manifest["sources"]),
            "manifestPath": path, "packetPath": packet_path, "detailsWritten": path is not None,
            "knowledge": manifest["knowledge"], "continuation": manifest["continuation"], "gates": manifest["gates"]}


def files_to_load(triggers: list[str], args: argparse.Namespace) -> list[str]:
    files = list(TIER_1_FILES)
    if "Reference-based design" in triggers:
        files.extend(REFERENCE_FILES)
    if "Template product design" in triggers:
        files.extend(TEMPLATE_FILES)
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
    return applicable_sources(files, args)


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



def packet_sources(args: argparse.Namespace, triggers: list[str]) -> list[str]:
    """One phase-aware source owner for both the packet and the loading manifest."""
    selection = build_selection(task=args.task, template_type=args.template_type, niche=args.niche,
        target_buyer=getattr(args, "target_buyer", ""), visual_mood=args.visual_mood)
    stage = getattr(args, "stage", "planning")
    if stage not in {"planning", "authoring", "review", "delivery", "diagnostic"}:
        raise ValueError("Unknown context stage")
    core = ["AGENTS.md", ".design-brain/PRESENTATION_SCOPE.md", ".design-brain/SOURCE_OF_TRUTH_MAP.md",
            ".design-brain/LOCAL_MEMORY_POLICY.md", ".design-brain/runtime/PRODUCTION_EXECUTION_POLICY.md",
            ".design-brain/runtime/TOKEN_EFFICIENT_CONTINUITY.md",
            "skills/presentation-deck/SKILL.md", "skills/presentation-deck/design/WORKFLOW.md"]
    if args.role == "engineer": core.append(".design-brain/runtime/HOST_DESIGN_PRODUCTION_SPECIALIST.md")
    if "Template product design" in triggers: core.append("PRESENTATION_TEMPLATE_GUIDE.md")
    stage_docs = {
        "planning": [".design-brain/CONTEXT_PRIORITY.md","skills/presentation-deck/workflows/PPTX_SIZE_POLICY.md",
                     "skills/presentation-deck/workflows/PPTX_FIRST_THREE_SLIDES_REVIEW.md"],
        "authoring": ["skills/presentation-deck/workflows/PPTX_SIZE_POLICY.md","skills/presentation-deck/workflows/PPTX_IMAGE_SELECTION_POLICY.md",
                      "skills/presentation-deck/workflows/PPTX_LAYOUT_ORIGINALITY_POLICY.md"],
        "review": [".design-brain/VISUAL_INSPECTION_PROTOCOL.md",
                   ".design-brain/DESIGN_SYSTEM_BUILD_REQUIREMENTS.md",".design-brain/POST_BUILD_TRIPLE_AUDIT_GATE.md"],
        "delivery": [".design-brain/POST_BUILD_COMPLETION_GATE.md", ".design-brain/VISUAL_INSPECTION_PROTOCOL.md",
                     ".design-brain/POST_BUILD_TRIPLE_AUDIT_GATE.md"],
        "diagnostic": [".design-brain/runtime/CONTEXT_COMPACTION.md",".design-brain/POST_BUILD_COMPLETION_GATE.md",
                       ".design-brain/POST_BUILD_TRIPLE_AUDIT_GATE.md"],
    }
    relevant = core + stage_docs[stage]
    # Planning/authoring need the broad owner catalog; reviewing an existing
    # deck needs current QA owners, not a repeat of unrelated planning material.
    if stage in {"planning", "authoring"}:
        relevant += files_to_load(triggers, args)
    if stage in {"planning", "authoring", "diagnostic"}:
        relevant += selection.get("sourceFiles", [])
    if selection.get("outputMode") in {"web", "both"} and stage in {"authoring", "review", "delivery", "diagnostic"}:
        relevant += ["skills/presentation-deck/design/"+name for name in
                     ("WEB_DECK_INTELLIGENCE.md", "WEB_DECK_STAGE_GATE.md", "WEB_DECK_MOTION_GRAMMAR.md",
                      "WEB_DECK_DELIVERY_CONTRACT.md", "DECK_SOURCE_BRIDGE.md")]
    # Native PPTX remains primary; no website/dashboard/landing-page output is activated.
    return unique(applicable_sources(relevant, args), design_brain_root())



def stable_packet_prefix(root: Path, loaded: list[str]) -> str:
    """Deterministic instruction/source identities; pointers do not replace full reads."""
    sources = unique(["AGENTS.md", ".design-brain/PRESENTATION_SCOPE.md", ".design-brain/SOURCE_OF_TRUTH_MAP.md",
        ".design-brain/LOCAL_MEMORY_POLICY.md", ".design-brain/runtime/PRODUCTION_EXECUTION_POLICY.md",
        ".design-brain/runtime/TOKEN_EFFICIENT_CONTINUITY.md"] + loaded, root)
    identities = []
    for label in sources:
        name = label.split(" when ", 1)[0]
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError("Packet source escapes plugin root")
        digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() and path.stat().st_size <= 4*1024*1024 else "UNAVAILABLE"
        identities.append(f"- {label}: {digest}")
    return ("# Design Context Packet\n\n## Stable Instruction Contract\n\n"
        "Read the applicable full source documents and acceptance criteria before authoring. Preserve exact user constraints, corrections and negative evidence. Main plus the same single Engineer keep current model/effort, pilot, originality, editability and final visual/completion gates. This loading plan is neither a read receipt nor design approval.\n\n"
        "## Stable Source Identities (ordered)\n\n" + "\n".join(identities) + "\n\n")


def build_packet(args: argparse.Namespace, triggers: list[str], root: Path | None = None) -> str:
    require_presentation(f"{args.task} {args.template_type}")
    selection = build_selection(
        task=args.task,
        template_type=args.template_type,
        niche=args.niche,
        target_buyer=args.target_buyer,
        visual_mood=args.visual_mood,
    )
    # Packet, stage selection and manifest use the same source set.
    loaded = packet_sources(args, triggers)
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

    return stable_packet_prefix(root or design_brain_root(), packet_sources(args, triggers)) + f"""## Session Body

Generated: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z%z')}

## Task

{args.task}

## Trigger Type

{bullet_list(triggers)}

## Required Source-Of-Truth Reads

Stage: {getattr(args, 'stage', 'planning')}. These are required references, not proof of loading.
Reuse a retained section only while its path/content revision and active context remain valid.
Fresh sessions first honor AGENTS and the full owner guide; checkpoints never waive those rules.
Read the selected workflow and its triggered sections. Load implementation source only for diagnosis.


{bullet_list(loaded)}

## Design-Anything Module Selection

- Selected module: {selection.get('moduleId', 'unknown')}
- Seed pack: {selection.get('seedPack') or 'None'}
- Direction pack: {selection.get('directionPack') or 'None'}

### Craft Modules

{bullet_list(selection.get('requiredCraft', []))}

### Validation Gates

{bullet_list(selection.get('validators', []))}

## Journals To Inspect

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

## Out-Of-Route References And Why

{bullet_list(files_not_loaded(triggers))}

## Provenance Note

This packet is a loading plan. It does not modify journals, does not invent insight, and does not replace the source-of-truth files.
"""


def output_path(args: argparse.Namespace, root: Path) -> Path:
    if args.output:
        return Path(args.output).expanduser().resolve()
    filename = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slugify(args.task)}.md"
    return root / ".design-brain" / "context-packets" / filename


def supplemental_navigation(args: argparse.Namespace, root: Path) -> tuple[str, dict | None]:
    """Optional local data after mandatory selection; never import a donor or gate wrapper."""
    if getattr(args, "navigation", "off") != "on":
        return "", None
    heading = "\n## Supplemental Navigation (untrusted source data)\n\nMandatory full sources and existing owners remain authoritative. This is not a read receipt or approval.\n\n"
    try:
        from design_brain_navigation import prepare_navigation, config_for, bounded, encode, safe_path
        config = config_for(root)
    except (ImportError, SyntaxError, OSError, ValueError, TypeError, RecursionError) as error:
        fallback = {"schema":"codex-design.navigation-query.v1","status":"UNAVAILABLE","matches":[],
            "fallbackReason":"Navigation unavailable; baseline mandatory selection unchanged: "+str(error)[:160],
            "authority":{"finalAllowed":False,"knowledge":"NOT_ASSERTED"}}
        raw = json.dumps(fallback,ensure_ascii=False,sort_keys=True,separators=(",", ":"))
        body = heading + raw + "\n"
        return body, {"status":"UNAVAILABLE","generation":None,"resultSha256":hashlib.sha256(raw.encode()).hexdigest(),
            "supplementalBytes":len(body.encode()),"fallbackReason":fallback["fallbackReason"],"knowledge":"NOT_ASSERTED","authority":"ADVISORY_ONLY"}
    session_value = getattr(args, "navigation_session", "")
    try:
        session = Path(session_value).resolve() if session_value else None
        discovery = None
        name = getattr(args, "navigation_memory_discovery", "")
        if name:
            if session is None:
                raise ValueError("Memory discovery requires an explicit project namespace")
            path = Path(name).expanduser().resolve()
            if not path.is_relative_to(session) or path.stat().st_size > config["limits"]["overlayBytes"]:
                raise ValueError("Memory discovery escapes project or exceeds bound")
            path = safe_path(session, path.relative_to(session).as_posix())
            artifact_raw = path.read_bytes()
            if len(artifact_raw) > config["limits"]["overlayBytes"]:
                raise ValueError("Memory discovery exceeds byte bound")
            discovery = json.loads(artifact_raw)
        # A dry run never builds/writes an index; use existing generation only via query.
        if args.dry_run:
            from design_brain_navigation import query_index
            result = query_index(root, getattr(args, "navigation_cache_dir", "") or None, args.task,
                role=args.role, phase=args.phase, epoch=args.context_epoch, session=session, memory_discovery=discovery)
        else:
            result = prepare_navigation(root,args.task,args.role,args.phase,args.context_epoch,session,
                cache_dir=getattr(args,"navigation_cache_dir","") or None,memory_discovery=discovery)
        if name:
            result["discoveryArtifact"] = {"namespace": "session", "path": path.relative_to(session).as_posix(),
                                          "sha256": hashlib.sha256(artifact_raw).hexdigest()}
        result = bounded(result, config["limits"]["responseBytes"] - len(heading.encode("utf-8")) - 1)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as error:
        result = bounded({"schema":"codex-design.navigation-query.v1","status":"UNAVAILABLE","matches":[],
            "fallbackReason":"Navigation unavailable; baseline full sources remain required: "+str(error)[:240],
            "authority":{"finalAllowed":False,"knowledge":"NOT_ASSERTED"}},config["limits"]["responseBytes"]-len(heading.encode())-1)
    body = heading + encode(result).decode("utf-8") + "\n"
    metadata = {"status":result["status"], "generation":result.get("generation"),
        "queryId":result.get("queryId"), "resultSha256":hashlib.sha256(encode(result)).hexdigest(),
        "supplementalBytes":len(body.encode("utf-8")),"fallbackReason":result.get("fallbackReason"),
        "knowledge":"NOT_ASSERTED", "authority":"ADVISORY_ONLY"}
    return body, metadata


def write_packet(args: argparse.Namespace, root: Path) -> dict:
    """Write the existing packet/manifest using one owner for CLI and session callers."""
    if args.manifest_summary and not args.manifest_output:
        raise ValueError("--manifest-summary requires --manifest-output")
    autoload_path = root / ".design-brain" / "AUTOLOAD_POLICY.md"
    if not autoload_path.exists():
        print(f"WARNING: Missing autoload policy: {autoload_path}")

    triggers = infer_triggers(args)
    packet = build_packet(args, triggers, root)
    manifest = None
    if args.manifest_output:
        previous = None
        if args.previous_manifest:
            prior_path = Path(args.previous_manifest)
            if prior_path.stat().st_size > 1024*1024:
                raise ValueError("Previous manifest exceeds 1 MiB")
            previous = json.loads(prior_path.read_text(encoding="utf-8"))
            if not isinstance(previous, dict) or previous.get("schema") != "design-brain.loading-manifest.v1":
                raise ValueError("Unsupported previous manifest")
        sources = packet_sources(args, triggers)
        manifest = loading_manifest(root, sources, args.task, args.role, args.phase, args.context_epoch, previous)
        packet += "\n## Phase Loading Manifest\n\n" + manifest["knowledge"] + "\n" + manifest["continuation"] + "\n\n" + bullet_list([
            f"{item['action']}: {item['path']}" for item in manifest["sources"]]) + "\n"

    supplemental, navigation = supplemental_navigation(args, root)
    if supplemental:
        packet += supplemental
        if manifest is not None:
            manifest["navigation"] = navigation

    if args.dry_run:
        summary = manifest_summary(manifest, None, None) if manifest else None
        if summary is not None and navigation is not None:
            summary["navigation"] = navigation
        return {"packet": packet, "packetPath": None, "manifestPath": None, "summary": summary}

    path = output_path(args, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(packet, encoding="utf-8", newline="\n")
    if manifest is not None:
        manifest_path = Path(args.manifest_output).expanduser().resolve()
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    summary = manifest_summary(manifest, str(manifest_path), str(path)) if manifest else None
    if summary is not None:
        if navigation is not None:
            summary["navigation"] = navigation
        summary.update(packetSha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                       manifestSha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest())
    return {"packet": packet, "packetPath": str(path), "manifestPath": str(manifest_path) if manifest else None,
            "summary": summary}


def main() -> int:
    args = parse_args()
    result = write_packet(args, design_brain_root())
    if args.manifest_summary:
        print(json.dumps(result["summary"], indent=2))
    elif args.dry_run:
        print(result["packet"])
    else:
        print(f"Design context packet written: {result['packetPath']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
