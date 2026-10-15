#!/usr/bin/env python
"""Axis-based layout originality audit for Brain Design build sessions."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


FINGERPRINT_FIELDS = [
    "templateId",
    "sourceType",
    "productFamily",
    "mode",
    "heroGrammar",
    "sectionOrder",
    "gridSystem",
    "layoutGesture",
    "sectionSilhouettes",
    "sectionPatternMix",
    "sectionPatternIds",
    "sectionDensityLimits",
    "catalogDivergenceNotes",
    "compositionTension",
    "focalPath",
    "negativeSpaceShape",
    "depthLayering",
    "moduleScaleVariation",
    "breakoutBehavior",
    "layoutRhythm",
    "cardCadence",
    "componentPatterns",
    "ctaPlacement",
    "closureSilhouette",
    "imageTreatment",
    "spacingCadence",
    "typographyBehavior",
    "colorRoles",
    "effectLanguage",
    "navigationPattern",
    "footerPattern",
    "designSystemId",
    "visualGrammarSummary",
    "marketplaceReadinessSummary",
]


AXIS_MAP = {
    "heroGrammarSimilarity": ("heroGrammar", 0.70),
    "sectionOrderSimilarity": ("sectionOrder", 0.70),
    "gridSystemSimilarity": ("gridSystem", 0.70),
    "layoutGestureSimilarity": ("layoutGesture", 0.70),
    "sectionSilhouetteSimilarity": ("sectionSilhouettes", 0.70),
    "sectionPatternMixSimilarity": ("sectionPatternMix", 0.70),
    "compositionTensionSimilarity": ("compositionTension", 0.72),
    "focalPathSimilarity": ("focalPath", 0.75),
    "negativeSpaceShapeSimilarity": ("negativeSpaceShape", 0.80),
    "depthLayeringSimilarity": ("depthLayering", 0.78),
    "moduleScaleVariationSimilarity": ("moduleScaleVariation", 0.74),
    "breakoutBehaviorSimilarity": ("breakoutBehavior", 0.78),
    "layoutRhythmSimilarity": ("layoutRhythm", 0.75),
    "cardCadenceSimilarity": ("cardCadence", 0.75),
    "componentPatternSimilarity": ("componentPatterns", 0.70),
    "ctaPlacementSimilarity": ("ctaPlacement", 0.75),
    "closureSilhouetteSimilarity": ("closureSilhouette", 0.70),
    "imageTreatmentSimilarity": ("imageTreatment", 0.78),
    "spacingCadenceSimilarity": ("spacingCadence", 0.80),
    "typographyBehaviorSimilarity": ("typographyBehavior", 0.80),
    "colorRoleSimilarity": ("colorRoles", 0.80),
    "effectLanguageSimilarity": ("effectLanguage", 0.82),
    "navigationFooterPatternSimilarity": (("navigationPattern", "footerPattern"), 0.80),
}

STRUCTURE_AXES = {
    "heroGrammarSimilarity",
    "sectionOrderSimilarity",
    "gridSystemSimilarity",
    "layoutGestureSimilarity",
    "sectionSilhouetteSimilarity",
    "sectionPatternMixSimilarity",
    "compositionTensionSimilarity",
    "focalPathSimilarity",
    "moduleScaleVariationSimilarity",
    "componentPatternSimilarity",
    "ctaPlacementSimilarity",
    "closureSilhouetteSimilarity",
}

VISUAL_LANGUAGE_AXES = {
    "imageTreatmentSimilarity",
    "typographyBehaviorSimilarity",
    "colorRoleSimilarity",
    "effectLanguageSimilarity",
    "negativeSpaceShapeSimilarity",
    "depthLayeringSimilarity",
    "breakoutBehaviorSimilarity",
}


@dataclass
class PairAudit:
    candidate_id: str
    compared_id: str
    comparison_type: str
    axis_scores: dict[str, float]
    failed_axes: list[str]
    hard_fail_axes: list[str]
    soft_risk_axes: list[str]
    safe_axes: list[str]
    overall_scaffold_risk: float
    required_repairs: list[str]
    status: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run axis-based layout similarity audit.")
    parser.add_argument("--candidate", default="", help="Candidate layout fingerprint JSON.")
    parser.add_argument("--reference", default="", help="Reference layout fingerprint JSON.")
    parser.add_argument("--previous", nargs="*", default=[], help="Previous AI output fingerprint JSON files.")
    parser.add_argument("--batch-dir", default="", help="Session or batch directory containing fingerprints.")
    parser.add_argument("--type", choices=("ai-vs-reference", "ai-vs-ai", "batch"), default="ai-vs-reference")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def template_id(payload: dict[str, Any], fallback: str = "template") -> str:
    return str(payload.get("templateId") or payload.get("id") or fallback)


def normalize_value(value: Any) -> str:
    if isinstance(value, list):
        return " > ".join(normalize_value(item) for item in value)
    if isinstance(value, dict):
        parts: list[str] = []
        for key in sorted(value):
            parts.append(f"{key}:{normalize_value(value[key])}")
        return " | ".join(parts)
    return str(value or "").strip().lower()


def tokenize(value: Any) -> list[str]:
    text = normalize_value(value)
    for char in ",;|/()[]{}:\n\t":
        text = text.replace(char, " ")
    return [word for word in text.split() if word]


def sequence_similarity(a: Any, b: Any) -> float:
    left = [normalize_value(item) for item in a] if isinstance(a, list) else [item for item in normalize_value(a).split(">") if item.strip()]
    right = [normalize_value(item) for item in b] if isinstance(b, list) else [item for item in normalize_value(b).split(">") if item.strip()]
    left = [item.strip() for item in left if item.strip()]
    right = [item.strip() for item in right if item.strip()]
    if not left or not right:
        return 0.0
    same_position = sum(1 for a_item, b_item in zip(left, right) if a_item == b_item)
    shared = len(set(left) & set(right))
    length = max(len(left), len(right))
    return max(same_position / length, shared / length)


def scalar_similarity(a: Any, b: Any) -> float:
    left = normalize_value(a)
    right = normalize_value(b)
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    left_words = set(tokenize(left))
    right_words = set(tokenize(right))
    if not left_words or not right_words:
        return 0.0
    return len(left_words & right_words) / len(left_words | right_words)


def closure_signature(payload: dict[str, Any]) -> str:
    """Summarize the local conversion/footer ending so it cannot hide in page totals."""
    parts: list[str] = []
    explicit = payload.get("closureSilhouette")
    if explicit:
        parts.append(normalize_value(explicit))
    silhouettes = payload.get("sectionSilhouettes")
    if isinstance(silhouettes, list) and silhouettes:
        parts.extend(normalize_value(item) for item in silhouettes[-2:])
    section_order = payload.get("sectionOrder")
    if isinstance(section_order, list) and section_order:
        parts.extend(normalize_value(item) for item in section_order[-2:])
    parts.append(normalize_value(payload.get("ctaPlacement")))
    parts.append(normalize_value(payload.get("footerPattern")))
    return " | ".join(part for part in parts if part)


def section_pattern_sequence(payload: dict[str, Any]) -> list[str]:
    values: list[str] = []
    pattern_ids = payload.get("sectionPatternIds")
    if isinstance(pattern_ids, list):
        values.extend(normalize_value(item) for item in pattern_ids if normalize_value(item))

    pattern_mix = payload.get("sectionPatternMix")
    if isinstance(pattern_mix, list):
        for item in pattern_mix:
            if isinstance(item, dict):
                pattern_id = item.get("patternId")
                section_type = item.get("sectionType")
                if pattern_id:
                    values.append(normalize_value(pattern_id))
                elif section_type:
                    values.append(
                        normalize_value(
                            f"{section_type} {item.get('layoutGesture', '')} {item.get('sectionSilhouette', '')}"
                        )
                    )
            else:
                normalized = normalize_value(item)
                if normalized:
                    values.append(normalized)
    return [value for value in values if value]


def section_pattern_mix_similarity(candidate: dict[str, Any], other: dict[str, Any]) -> float:
    left = section_pattern_sequence(candidate)
    right = section_pattern_sequence(other)
    if not left or not right:
        return 0.0
    same_position = sum(1 for a_item, b_item in zip(left, right) if a_item == b_item)
    shared = len(set(left) & set(right))
    length = max(len(left), len(right))
    return max(same_position / length, shared / length)


def axis_similarity(axis: str, field: str | tuple[str, str], candidate: dict[str, Any], other: dict[str, Any]) -> float:
    if axis == "sectionOrderSimilarity":
        return sequence_similarity(candidate.get("sectionOrder"), other.get("sectionOrder"))
    if axis == "sectionSilhouetteSimilarity":
        return sequence_similarity(candidate.get("sectionSilhouettes"), other.get("sectionSilhouettes"))
    if axis == "sectionPatternMixSimilarity":
        return section_pattern_mix_similarity(candidate, other)
    if axis == "closureSilhouetteSimilarity":
        return scalar_similarity(closure_signature(candidate), closure_signature(other))
    if isinstance(field, tuple):
        cand = " ".join(normalize_value(candidate.get(item)) for item in field)
        prev = " ".join(normalize_value(other.get(item)) for item in field)
        return scalar_similarity(cand, prev)
    return scalar_similarity(candidate.get(field), other.get(field))


def missing_fingerprint_fields(payload: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for field in FINGERPRINT_FIELDS:
        value = payload.get(field)
        if value is None or value == "" or value == [] or value == {}:
            missing.append(field)
    return missing


def repair_for_axis(axis: str) -> str:
    repairs = {
        "heroGrammarSimilarity": "Change hero composition, media treatment, headline placement, and CTA logic.",
        "sectionOrderSimilarity": "Reorder buyer journey and section role logic.",
        "gridSystemSimilarity": "Change grid architecture and container behavior.",
        "layoutGestureSimilarity": "Change the spatial concept: editorial rail, dashboard shell, split ledger, product stage, timeline spine, or another product-fit gesture.",
        "sectionSilhouetteSimilarity": "Recompose the zoomed-out section silhouette sequence.",
        "sectionPatternMixSimilarity": "Select a different section layout pattern mix from the catalog; do not reuse the same section vocabulary or pattern IDs.",
        "compositionTensionSimilarity": "Change asymmetry, overlap, offset, density split, or restraint logic.",
        "focalPathSimilarity": "Change the first-second-third attention route.",
        "negativeSpaceShapeSimilarity": "Change how empty space works: runway, margin well, editorial pause, product breathing room, proof separation, or scan buffer.",
        "depthLayeringSimilarity": "Change depth layering: foreground/background, overlays, panels, shadows, or deliberate flatness logic.",
        "moduleScaleVariationSimilarity": "Change large/small rhythm and repeated-module proportions.",
        "breakoutBehaviorSimilarity": "Change where and how the layout escapes the container rhythm.",
        "layoutRhythmSimilarity": "Rework section rhythm, density cadence, and contrast between blocks.",
        "cardCadenceSimilarity": "Change card cadence and repeated module rhythm.",
        "componentPatternSimilarity": "Redesign component anatomy and repeated module structure.",
        "ctaPlacementSimilarity": "Change CTA placement, closure, and conversion flow.",
        "closureSilhouetteSimilarity": "Recompose the local CTA/footer ending silhouette; do not solve this with color, copy, or small spacing changes.",
        "imageTreatmentSimilarity": "Change media framing, placeholder strategy, and visual treatment.",
        "spacingCadenceSimilarity": "Change spacing scale and vertical rhythm.",
        "typographyBehaviorSimilarity": "Change type hierarchy behavior and emphasis rhythm.",
        "colorRoleSimilarity": "Apply Color Role Re-Mapping; recolor alone is not enough if layout axes fail.",
        "effectLanguageSimilarity": "Redefine visual grammar, effects, surface depth, and motif.",
        "navigationFooterPatternSimilarity": "Change navigation and footer closure pattern.",
        "overallScaffoldRisk": "Reconfigure the scaffold, not only colors or images.",
    }
    return repairs.get(axis, "Reconfigure layout axis before proceeding.")


def compare_pair(candidate: dict[str, Any], other: dict[str, Any], comparison_type: str) -> PairAudit:
    candidate_id = template_id(candidate, "candidate")
    other_id = template_id(other, "reference" if comparison_type == "ai_vs_reference" else "previous")

    candidate_missing = missing_fingerprint_fields(candidate)
    other_missing = missing_fingerprint_fields(other)
    if candidate_missing or other_missing:
        repairs = []
        if candidate_missing:
            repairs.append(f"Candidate fingerprint missing fields: {', '.join(candidate_missing)}.")
        if other_missing:
            repairs.append(f"Compared fingerprint missing fields: {', '.join(other_missing)}.")
        return PairAudit(
            candidate_id=candidate_id,
            compared_id=other_id,
            comparison_type=comparison_type,
            axis_scores={},
            failed_axes=["missing_fingerprint_fields"],
            hard_fail_axes=["missing_fingerprint_fields"],
            soft_risk_axes=[],
            safe_axes=[],
            overall_scaffold_risk=1.0,
            required_repairs=repairs,
            status="BLOCKED",
        )

    axis_scores: dict[str, float] = {}
    for axis, (field, _threshold) in AXIS_MAP.items():
        axis_scores[axis] = round(axis_similarity(axis, field, candidate, other), 3)

    structure_scores = [axis_scores[axis] for axis in STRUCTURE_AXES]
    weighted = (
        max(structure_scores) * 0.45
        + (sum(structure_scores) / len(structure_scores)) * 0.35
        + max(axis_scores.values()) * 0.20
    )
    overall = round(weighted, 3)
    axis_scores["overallScaffoldRisk"] = overall

    hard_fail_axes = []
    soft_risk_axes = []
    for axis, score in axis_scores.items():
        threshold = AXIS_MAP.get(axis, ("", 1.0))[1]
        near_clone = score >= 0.85
        scaffold_hard_fail = axis == "overallScaffoldRisk" and score >= 0.65
        structure_hard_fail = axis in STRUCTURE_AXES and score >= threshold
        threshold_risk = axis != "overallScaffoldRisk" and score >= threshold
        if near_clone or scaffold_hard_fail or structure_hard_fail:
            hard_fail_axes.append(axis)
        elif threshold_risk:
            soft_risk_axes.append(axis)
    failed_axes = sorted(set(hard_fail_axes + soft_risk_axes))
    safe_axes = [axis for axis in axis_scores if axis not in failed_axes]
    repairs = [repair_for_axis(axis) for axis in failed_axes]
    if failed_axes and set(failed_axes) <= {"colorRoleSimilarity"}:
        repairs.append("Color-role repair is allowed only when no structure-defining axis failed.")
    elif any(axis in STRUCTURE_AXES or axis == "overallScaffoldRisk" for axis in failed_axes):
        repairs.append("Recolor or image swap is not a valid repair; reconfigure layout, structure, rhythm, or component cadence.")

    if hard_fail_axes:
        status = "BLOCKED"
    elif soft_risk_axes:
        status = "REVISE_REQUIRED"
    else:
        status = "PASS"

    return PairAudit(
        candidate_id=candidate_id,
        compared_id=other_id,
        comparison_type=comparison_type,
        axis_scores=axis_scores,
        failed_axes=failed_axes,
        hard_fail_axes=sorted(set(hard_fail_axes)),
        soft_risk_axes=sorted(set(soft_risk_axes)),
        safe_axes=safe_axes,
        overall_scaffold_risk=overall,
        required_repairs=sorted(set(repairs)),
        status=status,
    )


def pair_to_dict(pair: PairAudit) -> dict[str, Any]:
    structure_similarity = max((pair.axis_scores.get(axis, 0.0) for axis in STRUCTURE_AXES), default=0.0)
    visual_similarity = max((pair.axis_scores.get(axis, 0.0) for axis in VISUAL_LANGUAGE_AXES), default=0.0)
    return {
        "candidate": pair.candidate_id,
        "comparedAgainst": pair.compared_id,
        "comparisonType": pair.comparison_type,
        "axisScores": pair.axis_scores,
        "structureDefiningAxisSimilarity": round(float(structure_similarity), 3),
        "visualLanguageAxisSimilarity": round(float(visual_similarity), 3),
        "scaffoldRisk": pair.overall_scaffold_risk,
        "failedAxes": pair.failed_axes,
        "hardFailAxes": pair.hard_fail_axes,
        "softRiskAxes": pair.soft_risk_axes,
        "safeAxes": pair.safe_axes,
        "overallScaffoldRisk": pair.overall_scaffold_risk,
        "requiredRepairs": pair.required_repairs,
        "status": pair.status,
        "safeToProceed": pair.status == "PASS",
        "thresholdSemantics": {
            "structureHardFail": "hero/section/grid/layout gesture/section silhouette/section pattern mix/composition/focal path/module scale/component/CTA/closure axes fail at their thresholds because they define scaffold identity.",
            "overallHardFail": "overallScaffoldRisk >= 0.65 blocks final readiness.",
            "nearCloneHardFail": "any axis >= 0.85 is treated as near-clone risk.",
            "tenPercentRule": "The 10 percent rule is a product-level human similarity standard, not literal pixel percentage.",
            "layoutStiffnessRule": "Repeated spatial gesture, zoomed-out silhouette, focal path, or breakout behavior is treated as layout stiffness even when colors and copy differ.",
        },
    }


def discover_fingerprints(batch_dir: Path) -> list[Path]:
    patterns = [
        "fingerprints/*.json",
        "template-fingerprints/*.json",
        "locked-fingerprints/*.json",
        "**/*fingerprint*.json",
    ]
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(path for path in batch_dir.glob(pattern) if path.is_file())
    return sorted(set(paths))


def audit_candidate_against_many(candidate: dict[str, Any], others: list[dict[str, Any]], comparison_type: str) -> dict[str, Any]:
    pairs = [compare_pair(candidate, other, comparison_type) for other in others]
    failed = [pair for pair in pairs if pair.status != "PASS"]
    required_repairs: list[str] = []
    for pair in failed:
        required_repairs.extend(pair.required_repairs)
    status = "PASS"
    if any(pair.status == "BLOCKED" for pair in failed):
        status = "BLOCKED"
    elif failed:
        status = "REVISE_REQUIRED"
    max_risk = max((pair.overall_scaffold_risk for pair in pairs), default=0.0)
    return {
        "status": status,
        "comparisonType": comparison_type,
        "candidate": template_id(candidate, "candidate"),
        "referencesCompared": [template_id(item, "reference") for item in others],
        "pairMatrix": [pair_to_dict(pair) for pair in pairs],
        "axisScores": pairs[0].axis_scores if len(pairs) == 1 else {},
        "failedAxes": sorted(set(axis for pair in failed for axis in pair.failed_axes)),
        "hardFailAxes": sorted(set(axis for pair in failed for axis in pair.hard_fail_axes)),
        "softRiskAxes": sorted(set(axis for pair in failed for axis in pair.soft_risk_axes)),
        "structureDefiningAxisSimilarity": round(max((pair_to_dict(pair)["structureDefiningAxisSimilarity"] for pair in pairs), default=0.0), 3),
        "visualLanguageAxisSimilarity": round(max((pair_to_dict(pair)["visualLanguageAxisSimilarity"] for pair in pairs), default=0.0), 3),
        "overallScaffoldRisk": round(max_risk, 3),
        "requiredRepairs": sorted(set(required_repairs)),
        "safeToProceed": status == "PASS",
    }


def audit_batch(fingerprints: list[dict[str, Any]], batch_id: str = "batch") -> dict[str, Any]:
    pairs = [
        compare_pair(left, right, "ai_vs_ai")
        for left, right in itertools.combinations(fingerprints, 2)
    ]
    failed = [pair for pair in pairs if pair.status != "PASS"]
    repairs: list[str] = []
    for pair in failed:
        repairs.extend(pair.required_repairs)
    status = "PASS"
    if any(pair.status == "BLOCKED" for pair in failed):
        status = "BLOCKED"
    elif failed:
        status = "REVISE_REQUIRED"
    max_risk = max((pair.overall_scaffold_risk for pair in pairs), default=0.0)
    return {
        "batchId": batch_id,
        "status": status,
        "comparisonType": "batch",
        "candidate": "",
        "referencesCompared": [],
        "pairMatrix": [pair_to_dict(pair) for pair in pairs],
        "axisScores": {},
        "failedAxes": sorted(set(axis for pair in failed for axis in pair.failed_axes)),
        "hardFailAxes": sorted(set(axis for pair in failed for axis in pair.hard_fail_axes)),
        "softRiskAxes": sorted(set(axis for pair in failed for axis in pair.soft_risk_axes)),
        "structureDefiningAxisSimilarity": round(max((pair_to_dict(pair)["structureDefiningAxisSimilarity"] for pair in pairs), default=0.0), 3),
        "visualLanguageAxisSimilarity": round(max((pair_to_dict(pair)["visualLanguageAxisSimilarity"] for pair in pairs), default=0.0), 3),
        "overallScaffoldRisk": round(max_risk, 3),
        "requiredRepairs": sorted(set(repairs)),
        "safeToProceed": status == "PASS",
    }


def main() -> int:
    args = parse_args()
    try:
        if args.type == "batch" or args.batch_dir:
            batch_dir = Path(args.batch_dir).expanduser().resolve()
            paths = discover_fingerprints(batch_dir)
            fingerprints = [load_json(path) for path in paths]
            result = audit_batch(fingerprints, batch_id=batch_dir.name or "batch")
        else:
            candidate = load_json(Path(args.candidate).expanduser().resolve())
            if args.type == "ai-vs-reference":
                reference = load_json(Path(args.reference).expanduser().resolve())
                result = audit_candidate_against_many(candidate, [reference], "ai_vs_reference")
            else:
                previous = [load_json(Path(path).expanduser().resolve()) for path in args.previous]
                result = audit_candidate_against_many(candidate, previous, "ai_vs_ai")
    except Exception as exc:
        result = {
            "status": "BLOCKED",
            "comparisonType": args.type.replace("-", "_"),
            "candidate": args.candidate,
            "referencesCompared": [],
            "pairMatrix": [],
            "axisScores": {},
            "failedAxes": ["runtime_error"],
            "overallScaffoldRisk": 1.0,
            "requiredRepairs": [str(exc)],
            "safeToProceed": False,
        }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['status']}: scaffold risk={result['overallScaffoldRisk']}")
        for repair in result.get("requiredRepairs", []):
            print(f"- {repair}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
