#!/usr/bin/env python
"""Validate Brain Design Design Cognition Receipt."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


REQUIRED_SECTIONS = [
    "styleDNA",
    "referenceStandard",
    "designIntentLock",
    "visualGrammar",
    "referenceBoundary",
    "colorRoleRemapping",
    "visualMoodReinterpretation",
    "structuralReconfiguration",
    "patternDivergence",
    "sectionLogic",
    "marketplaceReadiness",
]

REQUIRED_FIELDS = {
    "styleDNA": ["typographyBehavior", "layoutRhythm", "spacingDensity", "colorBehavior", "imageDirection", "shapeLanguage", "effectLanguage", "premiumSignal"],
    "referenceStandard": ["observedSectionCountRange", "sectionRoleEvidence", "layoutShapeInventory", "colorRoleInventory", "effectGradientInventory", "marketplaceCompletenessClues", "remixPlan", "minimalistFallbackRejected"],
    "designIntentLock": ["productType", "outputMedium", "targetBuyer", "useCase", "marketplaceValue", "primaryGoal"],
    "visualGrammar": ["gridBehavior", "spacingCadence", "typeHierarchy", "surfaceDepth", "colorRoles", "imageTreatment", "effectLogic", "componentRhythm"],
    "referenceBoundary": ["allowedToLearn", "forbiddenToCopy"],
    "colorRoleRemapping": ["referenceDominantColorIdentity", "referenceColorRoles", "remappedPaletteDirection", "newAccentIdentity", "preservedEmotionalRole", "avoidedExactHues", "contrastHierarchyBehavior"],
    "visualMoodReinterpretation": ["referenceMood", "reinterpretedMood", "changedComposition", "changedHierarchy", "changedAssetTreatment", "changedDepthEffect"],
    "structuralReconfiguration": ["referenceStructurePattern", "newStructurePattern", "heroGrammarChange", "sectionOrderChange", "gridSystemChange", "ctaFlowChange", "componentLayoutChange"],
    "patternDivergence": ["divergenceFromReference", "heroDivergence", "sectionRhythmDivergence", "visualLanguageDivergence", "componentCadenceDivergence"],
    "sectionLogic": ["sectionList", "roleOfEachSection", "buyerJourneyFlow", "fillerSectionsRemoved", "productFamilyDepthStandard"],
    "marketplaceReadiness": ["sectionDepth", "premiumSignal", "editability", "sourceReadiness", "previewValue", "commercialUsefulness", "nonGenericProof"],
}

RISK_BY_SECTION = {
    "styleDNA": "missing_style_dna",
    "referenceStandard": "missing_reference_standard",
    "designIntentLock": "missing_design_intent",
    "visualGrammar": "missing_visual_grammar",
    "referenceBoundary": "missing_reference_boundary",
    "colorRoleRemapping": "missing_color_role_remapping",
    "visualMoodReinterpretation": "missing_visual_mood_reinterpretation",
    "structuralReconfiguration": "missing_structural_reconfiguration",
    "patternDivergence": "missing_pattern_divergence",
    "sectionLogic": "generic_section_logic",
    "marketplaceReadiness": "weak_marketplace_readiness",
}

COPY_RISK_PHRASES = [
    "copy exact layout",
    "same palette",
    "same color identity",
    "use reference color",
    "keep exact blue neon",
    "copy the reference exactly",
    "same layout and colors",
    "pixel-perfect clone",
]

GENERIC_SECTION_SEQUENCES = [
    ["hero", "features", "cta"],
    ["hero", "features", "pricing", "faq", "cta"],
    ["hero", "features", "testimonials", "pricing", "faq", "cta"],
]

VAGUE_MARKETPLACE_PHRASES = {"looks premium", "premium", "nice", "clean", "modern", "good", "market ready"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a Design Cognition Receipt.")
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_meaningful(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return len(value.strip()) >= 8 and value.strip().lower() not in {"n/a", "none", "tbd", "todo"}
    if isinstance(value, list):
        return bool(value) and any(is_meaningful(item) for item in value)
    if isinstance(value, dict):
        return bool(value) and any(is_meaningful(item) for item in value.values())
    if isinstance(value, bool):
        return True
    return True


def text_blob(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(text_blob(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(text_blob(item) for item in value)
    return str(value or "")


def section_list(receipt: dict[str, Any]) -> list[str]:
    value = receipt.get("sectionLogic", {}).get("sectionList", [])
    if isinstance(value, list):
        return [str(item).strip().lower() for item in value if str(item).strip()]
    return [part.strip().lower() for part in re.split(r">|,|\n", str(value)) if part.strip()]


def is_generic_section_logic(receipt: dict[str, Any]) -> bool:
    sections = section_list(receipt)
    if not sections:
        return True
    simplified = [re.sub(r"[^a-z0-9]+", " ", item).strip() for item in sections]
    simplified = ["features" if "feature" in item else "cta" if item in {"cta", "call to action"} or "cta" in item else item for item in simplified]
    for sequence in GENERIC_SECTION_SEQUENCES:
        if simplified == sequence or simplified[: len(sequence)] == sequence:
            return True
    if len(simplified) < 6 and receipt.get("mode", "").lower() in {"website", "website-template", "landing-page"}:
        return True
    roles = receipt.get("sectionLogic", {}).get("roleOfEachSection")
    if not is_meaningful(roles):
        return True
    return False


def has_explicit_same_palette_request(receipt: dict[str, Any]) -> bool:
    value = str(receipt.get("explicitSamePaletteRequest", "")).lower()
    return value in {"true", "yes", "user_requested", "explicit_user_request"}


def copied_color_identity(receipt: dict[str, Any]) -> bool:
    remap = receipt.get("colorRoleRemapping", {})
    blob = text_blob(remap).lower()
    if has_explicit_same_palette_request(receipt):
        return False
    if any(phrase in blob for phrase in COPY_RISK_PHRASES):
        return True
    ref = str(remap.get("referenceDominantColorIdentity", "")).strip().lower()
    new = str(remap.get("remappedPaletteDirection", "")).strip().lower()
    accent = str(remap.get("newAccentIdentity", "")).strip().lower()
    if ref and (new == ref or accent == ref):
        return True
    if ref and ref in new and any(word in new for word in ("same", "exact", "copy", "keep")):
        return True
    return False


def reference_boundary_weak(receipt: dict[str, Any]) -> bool:
    boundary = receipt.get("referenceBoundary", {})
    forbidden = text_blob(boundary.get("forbiddenToCopy", "")).lower()
    required = ["layout", "color", "section", "hero", "component"]
    if not all(word in forbidden for word in required):
        return True
    for key in ("exactLayoutCopied", "exactPaletteCopied", "exactSectionOrderCopied", "heroGrammarCopied", "componentScaffoldCopied"):
        if str(boundary.get(key, "no")).strip().lower() in {"yes", "true"}:
            return True
    return False


def structural_reconfiguration_weak(receipt: dict[str, Any]) -> bool:
    struct = receipt.get("structuralReconfiguration", {})
    for key in ("heroGrammarChange", "sectionOrderChange", "gridSystemChange"):
        value = str(struct.get(key, "")).strip().lower()
        if not is_meaningful(value) or value in {"same", "unchanged", "no change", "copy reference"}:
            return True
    return False


def pattern_divergence_required(receipt: dict[str, Any]) -> bool:
    batch = receipt.get("batchItem")
    return bool(batch not in (None, "", False, 0, "none", "n/a"))


def pattern_divergence_weak(receipt: dict[str, Any]) -> bool:
    divergence = receipt.get("patternDivergence", {})
    if pattern_divergence_required(receipt) and not is_meaningful(divergence.get("divergenceFromPreviousTemplate")):
        return True
    for key in ("divergenceFromReference", "heroDivergence", "sectionRhythmDivergence", "visualLanguageDivergence", "componentCadenceDivergence"):
        if not is_meaningful(divergence.get(key)):
            return True
    return False


def marketplace_readiness_weak(receipt: dict[str, Any]) -> bool:
    readiness = receipt.get("marketplaceReadiness", {})
    blob = text_blob(readiness).strip().lower()
    if blob in VAGUE_MARKETPLACE_PHRASES or len(blob.split()) < 12:
        return True
    for key in REQUIRED_FIELDS["marketplaceReadiness"]:
        if not is_meaningful(readiness.get(key)):
            return True
    return False


def reference_standard_weak(receipt: dict[str, Any]) -> bool:
    standard = receipt.get("referenceStandard", {})
    if not isinstance(standard, dict):
        return True
    rejected = standard.get("minimalistFallbackRejected")
    if rejected is not True and str(rejected).strip().lower() not in {"true", "yes", "rejected"}:
        return True
    for key in REQUIRED_FIELDS["referenceStandard"]:
        if not is_meaningful(standard.get(key)):
            return True
    return False


def validate_cognition(receipt: dict[str, Any]) -> dict[str, Any]:
    missing_fields: list[str] = []
    risk_categories: list[str] = []
    repairs: list[str] = []

    for top in ("task", "productFamily", "mode", "status"):
        if receipt.get(top) in (None, ""):
            missing_fields.append(top)

    for section in REQUIRED_SECTIONS:
        payload = receipt.get(section)
        if not isinstance(payload, dict) or not payload:
            missing_fields.append(section)
            risk_categories.append(RISK_BY_SECTION[section])
            repairs.append(f"Define {section}.")
            continue
        for field in REQUIRED_FIELDS[section]:
            if not is_meaningful(payload.get(field)):
                missing_fields.append(f"{section}.{field}")
                if RISK_BY_SECTION[section] not in risk_categories:
                    risk_categories.append(RISK_BY_SECTION[section])

    if isinstance(receipt.get("referenceBoundary"), dict) and reference_boundary_weak(receipt):
        risk_categories.append("missing_reference_boundary")
        repairs.append("Add explicit Reference Boundary forbidden copy items for layout, color palette, section order, hero grammar, and component scaffold.")

    if isinstance(receipt.get("colorRoleRemapping"), dict) and copied_color_identity(receipt):
        risk_categories.append("copied_color_identity")
        repairs.append("Replace copied color identity with Color Role Re-Mapping that changes hue/palette identity while preserving emotional role and hierarchy.")

    if isinstance(receipt.get("referenceStandard"), dict) and reference_standard_weak(receipt):
        risk_categories.append("missing_reference_standard")
        repairs.append("Extract reference standard: section count/range, section roles, layout-shape inventory, color-role inventory, effect/gradient inventory, marketplace completeness clues, remix plan, and rejected minimalist fallback.")

    if isinstance(receipt.get("structuralReconfiguration"), dict) and structural_reconfiguration_weak(receipt):
        risk_categories.append("missing_structural_reconfiguration")
        repairs.append("Change hero grammar, section order, and grid behavior before orchestration.")

    if isinstance(receipt.get("patternDivergence"), dict) and pattern_divergence_weak(receipt):
        risk_categories.append("missing_pattern_divergence")
        repairs.append("Define divergence from reference and previous templates across hero, rhythm, visual language, and component cadence.")

    if isinstance(receipt.get("sectionLogic"), dict) and is_generic_section_logic(receipt):
        risk_categories.append("generic_section_logic")
        repairs.append("Replace generic Hero > Features > CTA section logic with product-family buyer journey roles.")

    if isinstance(receipt.get("marketplaceReadiness"), dict) and marketplace_readiness_weak(receipt):
        risk_categories.append("weak_marketplace_readiness")
        repairs.append("Make Marketplace Readiness concrete: depth, editability, preview value, commercial usefulness, and non-generic proof.")

    risk_categories = sorted(set(risk_categories))
    status = "PASS" if not missing_fields and not risk_categories else "FAIL"
    return {
        "status": status,
        "missingFields": sorted(set(missing_fields)),
        "riskCategories": risk_categories,
        "requiredRepairs": repairs,
    }


def main() -> int:
    args = parse_args()
    path = Path(args.receipt).expanduser().resolve()
    try:
        receipt = load_json(path)
        result = validate_cognition(receipt)
    except Exception as exc:
        result = {"status": "FAIL", "missingFields": [], "riskCategories": ["invalid_receipt"], "requiredRepairs": [str(exc)]}
    result["receiptPath"] = str(path)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['status']}: {path}")
        for risk in result.get("riskCategories", []):
            print(f"- {risk}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
