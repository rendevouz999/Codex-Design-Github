#!/usr/bin/env python
"""Score reference similarity risk for template/product design work."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path


AXES = [
    "section_or_slide_order",
    "composition",
    "spacing_rhythm",
    "visual_motif",
    "effect_language",
    "gradient_logic",
    "surface_depth",
    "component_grouping",
    "title_and_media_placement",
    "color_role_mapping",
    "cta_behavior",
    "media_placeholder_treatment",
    "naming_and_metaphor",
    "marketplace_preview_staging",
    "product_type_fit",
]

KEYWORD_GROUPS = {
    "composition": (
        "hero",
        "split",
        "center",
        "centered",
        "left",
        "right",
        "grid",
        "bento",
        "timeline",
        "gallery",
        "sidebar",
        "card",
        "full bleed",
        "asymmetric",
    ),
    "spacing_rhythm": (
        "dense",
        "spacious",
        "compact",
        "breathing",
        "open",
        "tight",
        "large margin",
        "narrow",
        "wide",
    ),
    "visual_motif": (
        "orb",
        "gradient",
        "line",
        "circle",
        "blob",
        "pattern",
        "mesh",
        "glass",
        "shadow",
        "border",
        "mask",
        "frame",
    ),
    "effect_language": (
        "shadow",
        "drop shadow",
        "inner shadow",
        "glow",
        "blur",
        "glass",
        "overlay",
        "scrim",
        "hairline",
        "border",
        "rim light",
        "backlight",
        "halo",
        "sheen",
        "depth",
        "elevation",
    ),
    "gradient_logic": (
        "gradient",
        "mesh",
        "wash",
        "beam",
        "glaze",
        "sweep",
        "spotlight",
        "light field",
        "signal",
        "metal",
        "pearl",
        "chroma",
        "duotone",
    ),
    "surface_depth": (
        "flat",
        "floating",
        "raised",
        "inset",
        "layered",
        "console",
        "panel",
        "shelf",
        "deck",
        "stage",
        "glass",
        "tactile",
        "editorial",
    ),
    "component_grouping": (
        "cards",
        "metric",
        "stats",
        "testimonial",
        "pricing",
        "profile",
        "team",
        "faq",
        "table",
        "chart",
        "rate card",
    ),
    "title_and_media_placement": (
        "title left",
        "title right",
        "title top",
        "image left",
        "image right",
        "mockup",
        "avatar",
        "photo",
        "screenshot",
        "cover",
    ),
    "color_role_mapping": (
        "accent",
        "primary",
        "secondary",
        "cta",
        "background",
        "surface",
        "highlight",
        "muted",
        "dark",
        "light",
    ),
    "cta_behavior": (
        "shop",
        "book",
        "brief",
        "contact",
        "signup",
        "subscribe",
        "download",
        "waitlist",
        "lead",
        "checkout",
        "purchase",
    ),
    "media_placeholder_treatment": (
        "image placeholder",
        "profile photo placeholder",
        "photo placeholder",
        "screenshot placeholder",
        "video placeholder",
        "mockup placeholder",
        "crop",
        "frame",
        "media zone",
        "render",
        "product image",
        "portrait",
    ),
    "marketplace_preview_staging": (
        "cover",
        "mockup",
        "perspective",
        "overview",
        "responsive",
        "desktop",
        "mobile",
        "section breakdown",
        "detail crop",
    ),
}

MEDIUM_KEYWORDS = {
    "deck": ("powerpoint", "presentation", "deck", "slide", "slides", "keynote", "ppt", "pptx"),
    "website": ("website", "landing", "homepage", "web", "wordpress", "cta", "scroll"),
    "dashboard": ("dashboard", "admin", "analytics", "chart", "table", "kpi"),
    "brand": ("brand", "branding", "identity", "logo", "guideline"),
    "ui_kit": ("ui kit", "design system", "component", "variant", "states"),
}


@dataclass
class AxisScore:
    name: str
    score: float
    reason: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score originality risk against a reference summary.")
    parser.add_argument("--reference-summary", required=True, help="Reference structure, mood, or summary.")
    parser.add_argument("--proposed-structure", required=True, help="Proposed structure or design summary.")
    parser.add_argument("--reference-name", default="", help="Optional reference name.")
    parser.add_argument("--proposed-name", default="", help="Optional proposed template name.")
    parser.add_argument("--template-type", default="", help="Optional template type.")
    parser.add_argument(
        "--comparison-mode",
        choices=["reference", "batch"],
        default="reference",
        help="Use reference for template-vs-reference scoring, or batch for template-vs-template scoring.",
    )
    parser.add_argument(
        "--batch-threshold-percent",
        type=float,
        default=10.0,
        help="Maximum allowed cross-template similarity percent in batch mode.",
    )
    parser.add_argument(
        "--visual-evidence",
        default="",
        help="Optional screenshot/render/Figma screenshot evidence path or note. Without this, visual similarity is not verified.",
    )
    parser.add_argument(
        "--visual-verified",
        action="store_true",
        help="Set only after screenshot/render/visual inspection was actually performed.",
    )
    parser.add_argument("--output", default="", help="Optional output markdown path.")
    parser.add_argument("--dry-run", action="store_true", help="Print report without saving it.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def split_roles(text: str) -> list[str]:
    parts = re.split(r"[\n,;>|/]+|\s+-\s+", text.lower())
    roles = [re.sub(r"[^a-z0-9 ]+", "", part).strip() for part in parts]
    return [role for role in roles if role]


def ratio_score(reference: str, proposed: str) -> float:
    if not reference or not proposed:
        return 0.0
    return SequenceMatcher(None, reference, proposed).ratio() * 10


def role_overlap_score(reference_roles: list[str], proposed_roles: list[str]) -> float:
    ref_set = {role for role in reference_roles if role}
    prop_set = {role for role in proposed_roles if role}
    if not ref_set or not prop_set:
        return 0.0
    return (len(ref_set & prop_set) / max(len(ref_set | prop_set), 1)) * 10


def generic_template_name(name: str) -> bool:
    value = normalize(name)
    return bool(re.fullmatch(r"(template|design|concept|layout)\s*\d*", value))


def contains_keyword(text: str, keyword: str) -> bool:
    pattern = r"(?<![a-z0-9])" + re.escape(keyword) + r"(?![a-z0-9])"
    return bool(re.search(pattern, text))


def keyword_score(reference: str, proposed: str, keywords: tuple[str, ...]) -> tuple[float, list[str]]:
    ref_hits = {keyword for keyword in keywords if contains_keyword(reference, keyword)}
    prop_hits = {keyword for keyword in keywords if contains_keyword(proposed, keyword)}
    if not ref_hits and not prop_hits:
        return 0.0, []
    overlap = sorted(ref_hits & prop_hits)
    denominator = max(len(ref_hits | prop_hits), 1)
    return (len(overlap) / denominator) * 10, overlap


def detect_medium(text: str) -> str:
    value = normalize(text)
    for medium, keywords in MEDIUM_KEYWORDS.items():
        if any(keyword in value for keyword in keywords):
            return medium
    return "unknown"


def product_type_fit_score(reference: str, proposed: str, template_type: str) -> AxisScore:
    ref_medium = detect_medium(reference)
    prop_medium = detect_medium(" ".join([proposed, template_type]))
    if ref_medium == "unknown" or prop_medium == "unknown":
        return AxisScore("product_type_fit", 3.0, "Medium is underspecified; verify with medium playbook.")
    if ref_medium == prop_medium:
        return AxisScore("product_type_fit", 4.0, f"Both appear to be {ref_medium}; similarity depends on structure.")
    if {ref_medium, prop_medium} == {"website", "deck"}:
        return AxisScore("product_type_fit", 7.0, "Website/deck signals mixed; ensure deck is not a sliced landing page.")
    return AxisScore("product_type_fit", 2.0, f"Reference medium {ref_medium} differs from proposed medium {prop_medium}.")


def naming_score(reference_name: str, proposed_name: str) -> AxisScore:
    if not reference_name or not proposed_name:
        return AxisScore("naming_and_metaphor", 2.0, "Naming not fully specified.")
    score = ratio_score(normalize(reference_name), normalize(proposed_name))
    return AxisScore("naming_and_metaphor", score, "Name similarity measured with sequence ratio.")


def score_axes(args: argparse.Namespace) -> list[AxisScore]:
    reference = normalize(args.reference_summary)
    proposed = normalize(args.proposed_structure)
    ref_roles = " > ".join(split_roles(args.reference_summary))
    prop_roles = " > ".join(split_roles(args.proposed_structure))
    ref_role_list = split_roles(args.reference_summary)
    prop_role_list = split_roles(args.proposed_structure)

    scores: list[AxisScore] = [
        AxisScore(
            "section_or_slide_order",
            role_overlap_score(ref_role_list, prop_role_list)
            if args.comparison_mode == "batch"
            else ratio_score(ref_roles, prop_roles),
            "Role/order similarity measured from exact role overlap."
            if args.comparison_mode == "batch"
            else "Role/order similarity measured from split structure tokens.",
        )
    ]

    for axis in [
        "composition",
        "spacing_rhythm",
        "visual_motif",
        "effect_language",
        "gradient_logic",
        "surface_depth",
        "component_grouping",
        "title_and_media_placement",
        "color_role_mapping",
        "cta_behavior",
        "media_placeholder_treatment",
        "marketplace_preview_staging",
    ]:
        score, overlap = keyword_score(reference, proposed, KEYWORD_GROUPS[axis])
        reason = f"Overlapping cues: {', '.join(overlap)}." if overlap else "No strong overlapping cues detected."
        scores.append(AxisScore(axis, score, reason))

    if args.comparison_mode == "batch":
        if (
            args.reference_name
            and args.proposed_name
            and not generic_template_name(args.reference_name)
            and not generic_template_name(args.proposed_name)
        ):
            scores.append(naming_score(args.reference_name, args.proposed_name))
        return scores

    scores.append(naming_score(args.reference_name, args.proposed_name))
    scores.append(product_type_fit_score(reference, proposed, args.template_type))
    return scores


def pass_fail(scores: list[AxisScore], args: argparse.Namespace) -> str:
    average = sum(score.score for score in scores) / len(scores)
    highest = max(scores, key=lambda score: score.score)
    if args.comparison_mode == "batch":
        average_percent = average * 10
        highest_percent = highest.score * 10
        if average_percent >= args.batch_threshold_percent or highest_percent >= args.batch_threshold_percent:
            return "FAIL - rebuild the newer template before final."
        return "PASS - cross-template similarity is below the strict batch gate."
    if average > 5 or highest.score > 7:
        return "FAIL - restructure before final."
    return "PASS - similarity risk is controlled."


def required_reinterpretation(scores: list[AxisScore]) -> list[str]:
    actions: list[str] = []
    for score in sorted(scores, key=lambda item: item.score, reverse=True):
        if score.score <= 5:
            continue
        if score.name == "section_or_slide_order":
            actions.append("Change section/slide sequence and role progression.")
        elif score.name == "composition":
            actions.append("Change layout grammar, hierarchy anchor, and grouping.")
        elif score.name == "spacing_rhythm":
            actions.append("Change density cadence and whitespace rhythm.")
        elif score.name == "visual_motif":
            actions.append("Replace decorative motif with a new system.")
        elif score.name == "effect_language":
            actions.append("Redesign the effect system: shadows, glow, blur, borders, overlays, and depth roles.")
        elif score.name == "gradient_logic":
            actions.append("Change gradient purpose, placement, direction, and hierarchy role.")
        elif score.name == "surface_depth":
            actions.append("Change the surface-depth grammar: flat, raised, inset, glass, console, shelf, stage, or deck.")
        elif score.name == "component_grouping":
            actions.append("Regroup cards, metrics, profiles, proof, and pricing into a new pattern.")
        elif score.name == "title_and_media_placement":
            actions.append("Move title/media anchors and redesign image/mockup placement.")
        elif score.name == "color_role_mapping":
            actions.append("Reconstruct the palette from product purpose: change accent, CTA, background, surface, glow, proof, and highlight roles instead of copying the reference colors.")
        elif score.name == "cta_behavior":
            actions.append("Change CTA behavior, urgency, placement, and action model.")
        elif score.name == "media_placeholder_treatment":
            actions.append("Change media placeholder crop, role, overlay, label logic, and replacement expectation.")
        elif score.name == "naming_and_metaphor":
            actions.append("Generate a different naming metaphor.")
        elif score.name == "marketplace_preview_staging":
            actions.append("Change cover, preview wall, responsive spread, or detail crop staging.")
        elif score.name == "product_type_fit":
            actions.append("Run medium playbook and rebuild the structure for the correct medium.")
    return actions or ["No required reinterpretation; keep checking visual evidence during review."]


def bullet(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- None"


def build_report(args: argparse.Namespace) -> str:
    scores = score_axes(args)
    average = sum(score.score for score in scores) / len(scores)
    rows = "\n".join(f"| {score.name} | {score.score:.1f}/10 | {score.reason} |" for score in scores)
    high_risks = [f"{score.name}: {score.score:.1f}/10" for score in scores if score.score > 5]
    average_percent = average * 10
    highest = max(scores, key=lambda score: score.score)

    if args.comparison_mode == "batch":
        high_risks = [
            f"{score.name}: {score.score * 10:.1f}%"
            for score in scores
            if score.score * 10 >= args.batch_threshold_percent
        ]

    visual_note = (
        f"Visual similarity verified from: {args.visual_evidence or 'provided visual evidence'}"
        if args.visual_verified
        else "Visual similarity not verified; only textual/structural heuristic checked."
    )

    return f"""# Originality Similarity Score

- Date/time: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z%z')}
- Comparison mode: {args.comparison_mode}
- Reference name: {args.reference_name or 'Not specified'}
- Proposed name: {args.proposed_name or 'Not specified'}
- Template type: {args.template_type or 'Not specified'}
- Overall similarity risk: {average:.1f}/10
- Overall similarity percent: {average_percent:.1f}%
- Highest axis percent: {highest.score * 10:.1f}% ({highest.name})
- Batch threshold percent: {args.batch_threshold_percent:.1f}% if comparison mode is batch
- Result: {pass_fail(scores, args)}
- Visual evidence: {args.visual_evidence or 'None'}
- Visual verification status: {visual_note}

## Axis Scores

| Axis | Score | Reason |
| --- | --- | --- |
{rows}

## Highest Risk Areas

{bullet(high_risks)}

## Required Reinterpretation

{bullet(required_reinterpretation(scores))}

## Guardrail

- If comparison mode is batch and average or any structure/visual-language-defining axis reaches the batch threshold percent, keep the earlier accepted template as the fingerprint and rebuild, recompose, redesign effects, recolor, or rewrite according to the failing axis before final.
- If any reference-mode score is above 7, redesign before final.
- If reference-mode overall risk is above 5, do another structural pass.
- If effect_language, gradient_logic, or surface_depth is high in batch mode, do not solve with color alone; redesign the semantic visual language.
- Text heuristics are not visual proof. Do not claim a visual similarity pass unless screenshot/render/visual inspection was actually performed.
- Use `.design-brain/REFERENCE_DECONSTRUCTION_MATRIX.md` and `.design-brain/MEDIUM_PRODUCT_PLAYBOOKS.md` before continuing.
"""


def output_path(args: argparse.Namespace) -> Path:
    if args.output:
        path = Path(args.output).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.resolve()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    name = args.proposed_name or args.reference_name or args.template_type or "originality-score"
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower()).strip("-")[:72] or "originality-score"
    return repo_root() / ".design-brain" / "context-packets" / f"{stamp}-originality-score-{slug}.md"


def main() -> int:
    args = parse_args()
    report = build_report(args)
    if args.dry_run:
        print(report)
        return 0
    path = output_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8", newline="\n")
    print(f"Originality score report saved: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
