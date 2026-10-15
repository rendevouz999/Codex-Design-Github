#!/usr/bin/env python
"""Add Design Brain v2.0.0 professional presentation-template knowledge files.

This migration is intentionally additive: it creates v2 rule files, versioning,
evidence folders, and manifest entries without rewriting stable design memory or
preference weights.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


VERSION = "2.0.0"
LAST_REVIEWED = "2026-05-26"

TECH_SOURCES = [
    "Microsoft Support: What is a slide master in PowerPoint? https://support.microsoft.com/en-us/office/what-is-a-slide-master-in-powerpoint-b9abb2a0-7aef-4257-a14e-4329c904da54",
    "Microsoft Support: Create and save a PowerPoint template https://support.microsoft.com/en-us/office/create-and-save-a-powerpoint-template-ee4429ad-2a74-4100-82f7-50f8169c8aca",
    "Microsoft Learn: Structure of a PresentationML document https://learn.microsoft.com/en-us/office/open-xml/presentation/structure-of-a-presentationml-document",
    "Microsoft Learn: Working with slide masters https://learn.microsoft.com/en-us/office/open-xml/presentation/working-with-slide-masters",
]
MARKETPLACE_SOURCES = [
    "Envato Author Support: PowerPoint and Keynote Presentation Template Requirements https://help.author.envato.com/hc/en-us/articles/360000472123-PowerPoint-and-Keynote-Presentation-Template-Requirements",
    "Envato Elements: Presentation templates reference library https://elements.envato.com/presentation-templates",
]
ACCESSIBILITY_SOURCES = [
    "Microsoft Support: Make PowerPoint presentations accessible https://support.microsoft.com/en-us/accessibility/powerpoint/make-your-powerpoint-presentations-accessible-to-people-with-disabilities",
    "Section508.gov: Accessible Presentations https://www.section508.gov/create/presentations/",
    "Section508.gov: Creating PowerPoint Templates https://www.section508.gov/training/presentations/creating-powerpoint-templates/",
]
QA_SOURCES = [
    "Playwright: Screenshots https://playwright.dev/docs/screenshots",
    "Playwright: Visual comparisons https://playwright.dev/docs/test-snapshots",
]
WORKFLOW_SOURCES = TECH_SOURCES + MARKETPLACE_SOURCES + ACCESSIBILITY_SOURCES + QA_SOURCES


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def metadata(title: str, category: str, sources: list[str]) -> str:
    lines = [
        f"# {title}",
        "",
        f"- Rule category: {category}",
        f"- Last reviewed: {LAST_REVIEWED}",
        "- Source references used:",
    ]
    lines.extend(f"  - {source}" for source in sources)
    lines.append("")
    return "\n".join(lines)


def body(*sections: tuple[str, list[str]]) -> str:
    chunks: list[str] = []
    for heading, bullets in sections:
        chunks.append(f"## {heading}")
        chunks.append("")
        chunks.extend(f"- {bullet}" for bullet in bullets)
        chunks.append("")
    return "\n".join(chunks).rstrip() + "\n"


def rule_doc(title: str, category: str, sources: list[str], *sections: tuple[str, list[str]]) -> str:
    return metadata(title, category, sources) + body(*sections)


def make_docs() -> dict[str, str]:
    docs: dict[str, str] = {}

    input_sources = WORKFLOW_SOURCES
    docs["skills/presentation-deck/design/00_input_system/template-brief-schema.md"] = rule_doc(
        "Template Brief Schema",
        "workflow",
        input_sources,
        ("Required Brief Fields", [
            "Resolve target buyer, marketplace target, output format, reference direction, no-copy boundary, asset rules, scoring priority, and feedback memory before designing.",
            "If a field is missing, infer the safest default and label it as an assumption in the plan or report.",
            "For presentation products, do not start with mood alone; start with buyer, format, editability, and marketplace use case.",
        ]),
        ("Decision Rule", [
            "The agent can proceed only when the brief is sufficient to choose slide archetypes, visual system, editability rules, and QA gates.",
            "Missing buyer or output format is high risk and must be inferred explicitly or asked when inference is not possible.",
        ]),
    )
    docs["skills/presentation-deck/design/00_input_system/target-buyer-library.md"] = rule_doc(
        "Target Buyer Library",
        "workflow",
        input_sources,
        ("Buyer Families", [
            "Startup founder: investor-ready pitch, metrics, market, team, traction, ask.",
            "Marketing agency: campaign story, services, proof, pricing, portfolio, next steps.",
            "Corporate consultant: structured analysis, frameworks, timelines, risk, recommendations.",
            "Creative studio or filmmaker: concept, world, characters, visual style, production plan.",
            "Educator or trainer: learning outcomes, modules, exercises, recap, assessment.",
            "Real estate or finance professional: trust, numbers, charts, property or portfolio proof.",
        ]),
        ("Use Rule", [
            "Buyer choice controls tone, density, archetypes, preview style, and editable placeholders.",
            "Do not reuse a generic business deck flow when a niche buyer needs a different proof model.",
        ]),
    )
    docs["skills/presentation-deck/design/00_input_system/marketplace-target-rules.md"] = rule_doc(
        "Marketplace Target Rules",
        "marketplace",
        MARKETPLACE_SOURCES,
        ("Targets", [
            "Envato Elements and GraphicRiver require strict file organization, documentation, editability, and preview quality.",
            "Figma Community and Figma Slides prioritize reusable components, visible edit zones, and clear page/frame organization.",
            "Client or internal decks can optimize for exact brand fit, but still need editability, differentiation, and QA.",
        ]),
        ("Default", [
            "When marketplace is not specified for presentation templates, use Envato as the strictest default gate.",
        ]),
    )
    docs["skills/presentation-deck/design/00_input_system/output-format-rules.md"] = rule_doc(
        "Output Format Rules",
        "workflow",
        TECH_SOURCES + QA_SOURCES,
        ("Format Rules", [
            "PPTX requires slide size, masters/layouts, placeholders, editable text/shapes, theme colors, theme fonts, and export checks.",
            "Google Slides and Keynote require theme/layout thinking and editable media/text placeholders.",
            "Figma Slides and Figma Design require visible frame organization, editable placeholders, and export-aware 16:9 structure.",
            "HTML previews require Chromium screenshot QA, responsive checks, and visual regression when baselines exist.",
        ]),
        ("Decision Rule", [
            "Never validate a PPTX only by screenshot; native PPTX structure must also be checked.",
        ]),
    )
    docs["skills/presentation-deck/design/00_input_system/reference-classification.md"] = rule_doc(
        "Reference Classification",
        "workflow",
        WORKFLOW_SOURCES,
        ("Reference Types", [
            "Good reference: learn quality principles and market fit.",
            "Bad reference: learn what to avoid, such as clutter, weak hierarchy, or cheap effects.",
            "Competitor reference: benchmark buyer expectations without copying.",
            "Mood reference: learn tone only, not layout.",
            "Structure reference: learn flow only, not visual treatment.",
            "Component reference: learn a chart, card, timeline, or gallery pattern only.",
        ]),
        ("Output Rule", [
            "Every reference-based task must name what is learned and what is forbidden to copy.",
        ]),
    )
    docs["skills/presentation-deck/design/00_input_system/asset-rules.md"] = rule_doc(
        "Asset Rules",
        "workflow",
        TECH_SOURCES + MARKETPLACE_SOURCES,
        ("Asset Decisions", [
            "Declare font style and whether commercial/free fonts are required.",
            "Declare image style, icon style, illustration style, and whether placeholder-only output is acceptable.",
            "For marketplace products, prefer editable placeholders over flattened decorative images unless the preview image is separate from source.",
            "Missing fonts and broken image links are export-readiness blockers.",
        ]),
    )
    docs["skills/presentation-deck/design/00_input_system/scoring-priority-system.md"] = rule_doc(
        "Scoring Priority System",
        "workflow",
        WORKFLOW_SOURCES,
        ("100 Point Score", [
            "Premium polish: 20 points.",
            "Originality: 15 points.",
            "Editability: 20 points.",
            "Marketplace readiness: 15 points.",
            "Visual hierarchy: 10 points.",
            "Technical export readiness: 10 points.",
            "Accessibility and readability: 5 points.",
            "Quality verification and differentiation: 5 points.",
        ]),
        ("Thresholds", [
            "80+ is acceptable for marketplace draft.",
            "90+ is required for premium marketplace product.",
            "If premium polish or originality is low, the output cannot be called final.",
        ]),
    )

    technical = {
        "slide-master-rules.md": ("Slide Master Rules", [
            "Define global fonts, logos, backgrounds, recurring markers, and theme-level behavior on masters before designing individual slides.",
            "Keep accidental user edits away from global master elements.",
            "Clean unused masters before final delivery when possible.",
        ]),
        "slide-layout-rules.md": ("Slide Layout Rules", [
            "Each layout must have a clear role: cover, divider, content, chart, profile, gallery, timeline, closing.",
            "Layouts must survive realistic text length changes and image swaps.",
            "Avoid creating a separate one-off layout for every slide when a reusable layout can work.",
        ]),
        "placeholder-system.md": ("Placeholder System", [
            "Use text, picture, chart, table, and content placeholders where the buyer is expected to replace content.",
            "Label replacement intent clearly in design files and documentation.",
            "Do not fake editability with flattened text or rasterized card groups.",
        ]),
        "theme-color-font-rules.md": ("Theme Color And Font Rules", [
            "Map palette roles: background, surface, primary accent, secondary accent, text, muted text, chart series, warning.",
            "Use theme fonts or documented font choices so buyers can replace typography predictably.",
            "Avoid hardcoded color clutter that prevents theme customization.",
        ]),
        "pptx-openxml-structure.md": ("PPTX Open XML Structure", [
            "A valid PresentationML package depends on presentation, slide master, slide layout, slide, and theme relationships.",
            "Technical inspections should check for expected masters, layouts, slide parts, media assets, charts, and theme parts.",
            "Broken relationships or missing media are release blockers.",
        ]),
        "editable-template-rules.md": ("Editable Template Rules", [
            "Text should remain text, shapes should remain shapes, and chart/table objects should remain editable when possible.",
            "Only flatten visuals for preview images, not source template content.",
            "Every repeated slide role should be reusable by a non-designer buyer.",
        ]),
        "export-compatibility-rules.md": ("Export Compatibility Rules", [
            "Validate slide size, aspect ratio, exported PDF/PNG preview, missing assets, fonts, and image links.",
            "PPTX, Keynote, Google Slides, and Figma export paths may differ; document limitations per format.",
            "If conversion changes layout, revise source or document the export caveat.",
        ]),
    }
    for filename, (title, bullets) in technical.items():
        docs[f".design-brain/01_powerpoint_technical/{filename}"] = rule_doc(
            title,
            "technical",
            TECH_SOURCES,
            ("Rules", bullets),
            ("Hard Gate", ["If this rule fails on a PPTX output, do not call the template final."]),
        )

    design_docs = {
        "visual-hierarchy.md": ["One dominant idea per slide.", "Use size, contrast, placement, grouping, and silence to control attention.", "Avoid competing hero elements."],
        "grid-spacing-alignment.md": ["Use consistent safe margins and grid rhythm.", "Avoid almost-aligned edges and accidental gaps.", "Frame precision matters more in slides than in scrolling pages."],
        "typography-system.md": ["Use a readable type scale for live presentation and PDF reading.", "Limit font weights.", "Keep title/body hierarchy clear at thumbnail size."],
        "color-system.md": ["Use color roles instead of decorative color noise.", "Reserve accents for focus, markers, and charts.", "Check contrast against dark and light backgrounds."],
        "composition-patterns.md": ["Use varied slide silhouettes across a deck.", "Balance image-led, text-led, data-led, and rest slides.", "Avoid repeating the same title/media placement across many slides."],
        "slide-rhythm.md": ["Plan fast-read, slow-read, rest, data, and climax slides.", "Do not make every slide equally loud.", "Thumbnail rhythm must show a journey."],
        "premium-vs-generic.md": ["Premium feels precise, restrained, and buyer-specific.", "Generic design repeats common cards, random gradients, and vague copy.", "Remove decoration that does not improve communication."],
        "visual-polish-rules.md": ["Inspect local spacing, baseline drift, text clipping, and tangent collisions.", "Use fewer stronger effects.", "Revise until the deck feels intentional rather than generated."],
    }
    for filename, bullets in design_docs.items():
        docs[f".design-brain/02_design_principles/{filename}"] = rule_doc(
            filename[:-3].replace("-", " ").title(),
            "visual",
            WORKFLOW_SOURCES,
            ("Rules", bullets),
        )

    archetypes = {
        "cover-slide.md": "Set product mood, title, category, and one unforgettable first impression.",
        "agenda-slide.md": "Orient the audience with a short sequence and clear reading order.",
        "section-divider-slide.md": "Create pacing and reset attention between story chapters.",
        "problem-slide.md": "Frame pain, gap, or conflict with one clear message.",
        "solution-slide.md": "Explain the answer, offer, or concept without clutter.",
        "feature-slide.md": "Group feature benefits into scannable modules.",
        "data-slide.md": "Present numbers with editable charts, labels, and restrained gridlines.",
        "timeline-slide.md": "Show sequence, phases, or development schedule.",
        "roadmap-slide.md": "Show strategic stages, milestones, and ownership.",
        "pricing-slide.md": "Compare packages or budgets with aligned, editable rows.",
        "team-slide.md": "Present people, roles, credibility, and profile placeholders.",
        "portfolio-slide.md": "Show work samples or scenes with intentional image crops.",
        "testimonial-slide.md": "Use proof, quote, source, and optional portrait placeholder.",
        "dashboard-slide.md": "Show dense metrics with clear comparison and chart hierarchy.",
        "case-study-slide.md": "Connect context, action, result, and proof.",
        "closing-slide.md": "End with a memorable statement and practical contact/action.",
    }
    for filename, purpose in archetypes.items():
        docs[f".design-brain/03_slide_archetypes/{filename}"] = rule_doc(
            filename[:-3].replace("-", " ").title(),
            "workflow",
            TECH_SOURCES + MARKETPLACE_SOURCES,
            ("Purpose", [purpose]),
            ("Template Requirements", [
                "Define editable text fields, image/media placeholders, safe margins, and expected content density.",
                "Make the role reusable across multiple buyer projects.",
                "Check thumbnail readability before final approval.",
            ]),
        )

    marketplace = {
        "envato-presentation-requirements.md": ["Use organized files and English documentation.", "Avoid overlap, misalignment, low-quality previews, and unusable source structures.", "Include buyer-facing help and file-preparation notes."],
        "file-organization.md": ["Group source, preview, documentation, fonts/license notes, and assets predictably.", "Avoid loose unnamed exports.", "Keep generated evidence separate from marketplace deliverables."],
        "documentation-requirements.md": ["Explain font installation, image replacement, color editing, slide duplication, and export notes.", "Document any non-included assets.", "Keep instructions short and buyer-friendly."],
        "preview-image-rules.md": ["Show real slide value clearly.", "Use contact sheets and role breakdowns before decorative mockups.", "Do not hide weak slides behind perspective effects."],
        "marketplace-originality-rules.md": ["Avoid copyright-sensitive copied layouts, copied copywriting, and recognizable motifs.", "Use licensed or placeholder assets.", "Keep reference-derived work transformed."],
        "buyer-usability-rules.md": ["A non-designer buyer should be able to replace text, images, charts, and colors without breaking the design.", "Stress test longer titles, more bullets, image swaps, and chart changes."],
    }
    for filename, bullets in marketplace.items():
        docs[f".design-brain/04_marketplace_standard/{filename}"] = rule_doc(
            filename[:-3].replace("-", " ").title(),
            "marketplace",
            MARKETPLACE_SOURCES,
            ("Rules", bullets),
        )

    reference_docs = {
        "reference-analysis-template.md": ["Identify reference role, buyer, marketplace fit, slide archetypes, hierarchy, spacing, visual system, and reusable principle.", "Separate lesson from surface appearance."],
        "good-bad-reference-pairs.md": ["Analyze why good references feel premium.", "Analyze why bad references feel generic, cheap, outdated, crowded, or weak.", "Extract one reusable lesson per pair."],
        "plagiarism-transformation-method.md": ["Allowed: niche, buyer, slide purpose, hierarchy principle, spacing principle, component category.", "Forbidden: exact layout, composition, decoration, typography treatment, color combination, image placement, sequence, copywriting, chart style, icon placement.", "If similarity remains high, change structure, rhythm, visual system, content angle, and component style."],
        "redesign-from-reference-method.md": ["Start from buyer intent, not reference order.", "Change naming, slide order, component system, palette role mapping, and motif.", "Re-score originality before delivery."],
        "reference-to-original-concept-pipeline.md": ["Classify reference.", "Extract principle.", "Define forbidden copy zones.", "Create a new concept angle.", "Map new slide archetypes.", "Run originality and visual QA."],
    }
    for filename, bullets in reference_docs.items():
        docs[f".design-brain/05_reference_breakdowns/{filename}"] = rule_doc(
            filename[:-3].replace("-", " ").title(),
            "workflow",
            WORKFLOW_SOURCES,
            ("Rules", bullets),
        )

    qc_docs = {
        "design-review-checklist.md": ["Score hierarchy, spacing, typography, alignment, contrast, consistency, emotional direction, and buyer fit.", "List concrete revisions before final."],
        "powerpoint-technical-checklist.md": ["Check slide size, editable text, editable shapes, placeholders, theme colors, theme fonts, missing fonts/assets, image links, master/layout consistency, and export previews."],
        "accessibility-checklist.md": ["Check contrast, readable font sizes, meaningful order, unique slide titles, alt text expectations, and color-not-only meaning."],
        "marketplace-readiness-checklist.md": ["Check product clarity, role variety, editability, documentation potential, preview strength, and buyer usability."],
        "premium-polish-scorecard.md": ["Use the 100-point scoring system.", "Minimum 80 for marketplace draft and 90 for premium product.", "Document weakest scoring categories."],
        "generic-design-detector.md": ["Hard gate: low originality or premium polish blocks final delivery.", "Detect random gradients, repeated cards, vague copy, copied motif, weak spacing, and marketplace formula slides.", "Revise concept, rhythm, spacing, or visual system before final."],
        "final-export-checklist.md": ["Confirm source file organization, preview exports, docs, fonts, assets, slide size, no overlap, no clipped text, and no broken media."],
    }
    for filename, bullets in qc_docs.items():
        sources = ACCESSIBILITY_SOURCES if "accessibility" in filename else WORKFLOW_SOURCES
        docs[f".design-brain/06_quality_control/{filename}"] = rule_doc(
            filename[:-3].replace("-", " ").title(),
            "QA",
            sources,
            ("Rules", bullets),
        )

    visual_docs = {
        "chromium-visual-review.md": ["Do not trust metadata or generator output only.", "Render the output, capture screenshots, inspect overlap, cropped text, spacing, alignment, contrast, card consistency, margins, hierarchy, and generic feel.", "Save evidence to .design-brain/evidence/visual-reviews/."],
        "playwright-setup.md": ["Use local Playwright tooling when package.json exists.", "Scripts: visual:review, visual:update, visual:headed.", "Use Chromium by default for stable local preview checks."],
        "screenshot-review-checklist.md": ["Check one-glance premium feel, message clarity, breathing room, alignment, hierarchy, balance, trust, and reference distance."],
        "overlap-detection-rules.md": ["Flag intersecting text, clipped content, cramped title/content clearance, tangent spacing, footer collisions, and unsafe image crops."],
        "desktop-mobile-preview-rules.md": ["For responsive HTML/template previews, capture desktop and mobile.", "For deck outputs, use thumbnail/contact-sheet and per-frame checks instead of mobile."],
        "visual-regression-rules.md": ["Use Playwright toHaveScreenshot baselines when a render target is stable.", "Review snapshot updates manually and keep baseline environment consistent."],
    }
    for filename, bullets in visual_docs.items():
        docs[f".design-brain/07_visual_pipeline/{filename}"] = rule_doc(
            filename[:-3].replace("-", " ").title(),
            "QA",
            QA_SOURCES,
            ("Rules", bullets),
        )

    feedback_docs = {
        "feedback-log.md": ["Append user feedback with date, task, output, issue, lesson, and next rule.", "Do not rewrite history."],
        "accepted-design-patterns.md": ["Record patterns the user confirms as premium, useful, original, or marketplace-ready."],
        "rejected-design-patterns.md": ["Record patterns the user rejects as generic, messy, copied, cheap, uneditable, or weak."],
        "premium-lessons.md": ["Record reusable premium craft lessons from accepted outputs and strong references."],
        "client-style-preferences.md": ["Record buyer/client-specific preferences only when clearly stated."],
        "README.md": ["Operational feedback memory is append-only and separate from stable DESIGN_MEMORY.md.", "Promote only after explicit user instruction: save this as stable memory."],
    }
    for filename, bullets in feedback_docs.items():
        docs[f".design-brain/08_feedback_memory/{filename}"] = rule_doc(
            filename[:-3].replace("-", " ").title() if filename != "README.md" else "Feedback Memory",
            "workflow",
            WORKFLOW_SOURCES,
            ("Rules", bullets),
        )

    prompt_docs = {
        "master-agent-instruction.md": ["Think in order: buyer, marketplace, output format, reference role, no-copy boundary, design system, slide archetypes, editability, visual QA, feedback loop.", "Specialize in PowerPoint, Google Slides, Keynote, Figma Slides, pitch decks, reports, proposals, and marketplace presentation products."],
        "reference-analyzer-prompt.md": ["Classify each reference and extract only transferable principles.", "Write forbidden copy zones before concepting."],
        "slide-planner-prompt.md": ["Choose slide archetypes based on buyer and use case.", "Every slide must have a purpose, editable content zones, and expected density."],
        "design-system-builder-prompt.md": ["Define palette roles, typography, grid, spacing, image style, icon style, chart style, background style, and rhythm before slide design."],
        "pptx-qa-prompt.md": ["Validate PPTX-native structure and editability, not only screenshots.", "Check masters, layouts, placeholders, theme, fonts, media, and exports."],
        "visual-review-prompt.md": ["Inspect screenshots for hierarchy, spacing, overlap, contrast, and generic feel.", "Save evidence and revision notes."],
        "natural-intent-router.md": ["Route presentation tasks to v2 presentation stack.", "Route reference tasks to reference/no-copy stack.", "Route visual tasks to visual pipeline.", "Route feedback tasks to feedback memory only."],
    }
    for filename, bullets in prompt_docs.items():
        docs[f".design-brain/09_prompt_system/{filename}"] = rule_doc(
            filename[:-3].replace("-", " ").title(),
            "workflow",
            WORKFLOW_SOURCES,
            ("Instruction", bullets),
        )

    docs[".design-brain/evidence/README.md"] = rule_doc(
        "Evidence Folder",
        "QA",
        QA_SOURCES,
        ("Purpose", ["Store visual QA evidence separately from stable memory and generated review reports."]),
    )
    docs[".design-brain/evidence/visual-reviews/README.md"] = rule_doc(
        "Visual Review Evidence",
        "QA",
        QA_SOURCES,
        ("Required Evidence", [
            "Screenshot or render artifact.",
            "Review notes.",
            "Score.",
            "Detected issues.",
            "Before/after comparison when revised.",
        ]),
    )
    return docs


def write_file(path: Path, content: str) -> str:
    if path.exists():
        return "skipped"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return "created"


def upsert_file(path: Path, content: str) -> str:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return "skipped"
    path.parent.mkdir(parents=True, exist_ok=True)
    action = "updated" if path.exists() else "created"
    path.write_text(content, encoding="utf-8", newline="\n")
    return action


def update_manifest(root: Path, v2_files: list[str]) -> str:
    path = root / ".design-brain" / "MANIFEST.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["version"] = VERSION
    managed = data.setdefault("managed_files", [])
    for item in [".design-brain/VERSION.md", ".design-brain/MIGRATION_LOG.md", *v2_files]:
        if item not in managed:
            managed.append(item)
    generated = data.setdefault("generated_folders", [])
    for item in [".design-brain/evidence", ".design-brain/evidence/visual-reviews"]:
        if item not in generated:
            generated.append(item)
    data["v2_behavior"] = {
        "purpose": "Professional presentation-template system for PowerPoint, Google Slides, Keynote, Figma Slides, and marketplace deck products.",
        "autoload_control": "Load v2 files selectively by intent: presentation, reference, visual preview, or feedback.",
        "pptx_validation": "PPTX work requires native checks for slide size, editable objects, placeholders, themes, fonts, assets, masters/layouts, and export previews.",
        "feedback_memory": "08_feedback_memory is append-only operational memory and must not be promoted into DESIGN_MEMORY.md without explicit user instruction.",
        "generic_hard_gate": "Low originality or premium polish blocks final delivery until revised.",
    }
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    return "updated"


def append_section(path: Path, marker: str, section: str) -> str:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return "skipped"
    path.write_text(text.rstrip() + "\n\n" + section.strip() + "\n", encoding="utf-8", newline="\n")
    return "updated"


def append_migration_log(path: Path, content: str) -> str:
    if path.exists():
        existing = path.read_text(encoding="utf-8").rstrip()
        path.write_text(existing + "\n\n" + content.strip() + "\n", encoding="utf-8", newline="\n")
        return "updated"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8", newline="\n")
    return "created"


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Design Brain v2.0.0 files.")
    parser.add_argument("--snapshot", required=True, help="Rollback snapshot folder created before migration.")
    args = parser.parse_args()

    root = repo_root()
    snapshot = args.snapshot
    docs = make_docs()
    created: list[str] = []
    updated: list[str] = []
    skipped: list[str] = []

    version_content = f"""# Design Brain Version

- Current version: Design Brain v{VERSION}
- Previous version: Design Brain v1.8.0
- Upgrade date: {LAST_REVIEWED}
- Upgrade type: additive migration
- Rollback snapshot: `{snapshot}`

## Stable Memory Boundary

`DESIGN_MEMORY.md` and `DESIGN_PREFERENCES.json` are not changed by v2 migration. Feedback promotion requires explicit user instruction: save this as stable memory.
"""
    action = upsert_file(root / ".design-brain" / "VERSION.md", version_content)
    {"created": created, "updated": updated, "skipped": skipped}[action].append(".design-brain/VERSION.md")

    for rel, content in docs.items():
        action = write_file(root / rel, content)
        {"created": created, "updated": updated, "skipped": skipped}[action].append(rel)

    update_manifest(root, sorted(docs.keys()))
    updated.append(".design-brain/MANIFEST.json")

    autoload = """## Design Brain v2.0.0 Controlled Autoload

Do not autoload every v2 file into every task.

- Presentation task: load `00_input_system`, `01_powerpoint_technical`, relevant `03_slide_archetypes`, `04_marketplace_standard`, and `06_quality_control`.
- Reference task: load `05_reference_breakdowns/reference-analysis-template.md`, `05_reference_breakdowns/plagiarism-transformation-method.md`, and good/bad reference rules when examples exist.
- Visual preview task: load `07_visual_pipeline` and save evidence into `.design-brain/evidence/visual-reviews/`.
- Feedback task: load `08_feedback_memory` only; do not edit `DESIGN_MEMORY.md` unless the user explicitly says "save this as stable memory".
- PPTX task: run native PPTX validation in addition to screenshots.
"""
    action = append_section(root / ".design-brain" / "AUTOLOAD_POLICY.md", "Design Brain v2.0.0 Controlled Autoload", autoload)
    {"updated": updated, "skipped": skipped}[action].append(".design-brain/AUTOLOAD_POLICY.md")

    context = """## Design Brain v2.0.0 Priority

Load v2 files selectively. For presentation-template work, the first v2 layer is:

1. `skills/presentation-deck/design/00_input_system/template-brief-schema.md`
2. `skills/presentation-deck/design/01_powerpoint_technical/editable-template-rules.md`
3. Relevant files in `.design-brain/03_slide_archetypes/`
4. `skills/presentation-deck/design/04_marketplace_standard/envato-presentation-requirements.md`
5. `skills/presentation-deck/design/06_quality_control/powerpoint-technical-checklist.md`
6. `skills/presentation-deck/design/06_quality_control/generic-design-detector.md`

For visual preview tasks, prefer `.design-brain/07_visual_pipeline/chromium-visual-review.md` and `.design-brain/evidence/visual-reviews/`.
"""
    action = append_section(root / ".design-brain" / "CONTEXT_PRIORITY.md", "Design Brain v2.0.0 Priority", context)
    {"updated": updated, "skipped": skipped}[action].append(".design-brain/CONTEXT_PRIORITY.md")

    quick = """## Design Brain v2.0.0 Presentation Workflow

For professional presentation-template work:

1. Resolve buyer, marketplace, output format, reference role, no-copy boundary, asset rules, and scoring priority.
2. Define the design system before slide planning.
3. Select slide archetypes from buyer and use case.
4. Validate editability: placeholders, text, shapes, theme colors, theme fonts, masters/layouts, and export behavior.
5. Run Chromium visual QA when renderable and save evidence to `.design-brain/evidence/visual-reviews/`.
6. For PPTX, run native PPTX checks; screenshots alone are not enough.
7. Apply the generic detector hard gate before final delivery.
"""
    action = append_section(root / ".design-brain" / "QUICK_START.md", "Design Brain v2.0.0 Presentation Workflow", quick)
    {"updated": updated, "skipped": skipped}[action].append(".design-brain/QUICK_START.md")

    log = [f"## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Design Brain v{VERSION}", ""]
    log.extend([
        f"- Rollback snapshot: `{snapshot}`",
        "- Migration type: additive upgrade.",
        "- Stable memory untouched: `DESIGN_MEMORY.md`, `DESIGN_PREFERENCES.json`.",
        "",
        "### Created",
        *[f"- {item}" for item in created],
        "",
        "### Updated",
        *[f"- {item}" for item in updated],
        "",
        "### Skipped",
        *[f"- {item}" for item in skipped],
        "",
    ])
    append_migration_log(root / ".design-brain" / "MIGRATION_LOG.md", "\n".join(log))

    print(json.dumps({"created": created, "updated": updated, "skipped": skipped}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
