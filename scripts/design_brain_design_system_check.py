#!/usr/bin/env python
"""Validate Brain Design post-build design system receipts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


REQUIRED_COLOR_TOKENS = {
    "background",
    "surface",
    "surfaceElevated",
    "textPrimary",
    "textSecondary",
    "textMuted",
    "accent",
    "action",
    "border",
}

REQUIRED_TYPE_TOKENS = {
    "display",
    "h1",
    "h2",
    "h3",
    "body",
    "bodySmall",
    "label",
    "button",
    "nav",
}

REQUIRED_SPACING_TOKENS = {
    "scale",
    "sectionY",
    "componentPadding",
    "cardGap",
    "gridGap",
    "container",
}

REQUIRED_STATES = {"default", "hover", "focus", "active", "disabled"}

REQUIRED_FUNCTIONAL_FIELDS = {
    "componentAnatomy",
    "patternModules",
    "productDna",
    "productSpecificModules",
    "reusableSectionPatterns",
    "visualLanguageRules",
    "referenceStandardCoverage",
    "usageExamples",
    "packageSourceMap",
    "accessibilityEditingNotes",
    "usageRules",
    "surfaceEffectTokens",
    "placeholderRules",
}

ARTIFACT_EVIDENCE_FIELDS = {
    "figmaNodeSummaryPath",
    "designSystemPageId",
    "sourceComponentInventoryPath",
    "screenshotPath",
    "renderPath",
    "componentInventory",
    "tokenSourcePath",
    "boardMetrics",
}

BASE_COMPONENT_KEYWORDS = {
    "button",
    "card",
    "navigation",
    "header",
    "footer",
    "cta",
    "placeholder",
}

PRODUCT_COMPONENT_KEYWORDS = {
    "restaurant": {"menu", "reservation", "gallery", "location"},
    "hospitality": {"menu", "reservation", "gallery", "location"},
    "ecommerce": {"product", "category", "cart", "trust"},
    "home_decor": {"product", "room", "material", "filter", "cart", "trust"},
    "decor": {"product", "room", "material", "filter", "cart", "trust"},
    "sneaker": {"product", "size", "drop", "cart", "review"},
    "shoes": {"product", "size", "drop", "cart", "review"},
    "consultant": {"strategy", "diagnostic", "case", "proof", "process", "form"},
    "business": {"strategy", "diagnostic", "case", "proof", "process", "form"},
    "saas": {"pricing", "integration", "workflow", "proof", "form"},
    "product": {"pricing", "integration", "workflow", "proof", "form"},
    "dashboard": {"kpi", "chart", "table", "filter", "empty", "loading", "error"},
    "presentation": {"slide", "master", "cover", "divider", "chart", "closing"},
    "web-deck": {"slide", "stage", "motion", "reveal", "chrome", "chart", "print"},
    "brand": {"logo", "application", "export"},
    "static": {"export", "placeholder"},
    "ui-kit": {"token", "variant", "state", "accessibility"},
    "design-system": {"token", "variant", "state", "accessibility"},
}

MIN_PRODUCT_GRADE_COUNTS = {
    "components": 8,
    "productSpecificModules": 3,
    "reusableSectionPatterns": 3,
    "usageExamples": 3,
    "boardPanels": 6,
    "componentSpecimens": 8,
    "productModuleSpecimens": 3,
    "stateExamples": 4,
}

MIN_WEBSITE_BOARD_HEIGHT = 1800

WEB_DECK_PRODUCT_MARKERS = (
    "web deck",
    "html deck",
    "html presentation",
    "web presentation",
    "browser deck",
    "browser presentation",
    "animated deck",
    "animated slides",
    "animated presentation",
    "web slides",
    "interactive deck",
    "single file deck",
)

STATIC_PRESENTATION_ONLY_KEYWORDS = {"master"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a Brain Design design system receipt.")
    parser.add_argument("--receipt", default="", help="Design system receipt JSON path.")
    parser.add_argument("--build-dir", default="", help="Build directory containing design system receipts.")
    parser.add_argument("--template-id", default="", help="Template id to resolve inside --build-dir.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_items(items: Any) -> set[str]:
    if isinstance(items, dict):
        return {str(key).strip() for key, value in items.items() if value not in (None, "")}
    if isinstance(items, list):
        return {str(item).strip() for item in items if str(item).strip()}
    return set()


def item_count(items: Any) -> int:
    if isinstance(items, dict):
        return len([key for key, value in items.items() if str(key).strip() and value not in (None, "", [], {})])
    if isinstance(items, list):
        return len([item for item in items if is_meaningful(item)])
    if isinstance(items, str):
        return 1 if is_meaningful(items) else 0
    return 1 if items not in (None, "", [], {}) else 0


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


def components_text(receipt: dict[str, Any]) -> str:
    values = [
        receipt.get("components", []),
        receipt.get("componentAnatomy", {}),
        receipt.get("patternModules", []),
        receipt.get("productSpecificModules", []),
        receipt.get("reusableSectionPatterns", []),
    ]
    parts: list[str] = []
    for value in values:
        if isinstance(value, list):
            parts.extend(str(item).lower() for item in value)
        elif isinstance(value, dict):
            parts.extend(str(key).lower() for key in value.keys())
            parts.extend(str(item).lower() for item in value.values())
        else:
            parts.append(str(value).lower())
    return " ".join(parts)


def has_keywords(text: str, keywords: set[str]) -> bool:
    return all(keyword.lower() in text for keyword in keywords)


def missing_keywords(text: str, keywords: set[str]) -> set[str]:
    return {keyword for keyword in keywords if keyword.lower() not in text}


def is_web_deck_text(text: str) -> bool:
    normalized = str(text or "").lower().replace("_", " ").replace("-", " ")
    return any(marker in normalized for marker in WEB_DECK_PRODUCT_MARKERS)


def product_keywords(receipt: dict[str, Any]) -> set[str]:
    combined = f"{receipt.get('productFamily', '')} {receipt.get('mode', '')}".lower()
    required: set[str] = set()
    for marker, keywords in PRODUCT_COMPONENT_KEYWORDS.items():
        if marker in combined:
            required.update(keywords)
    if is_web_deck_text(combined):
        required.update(PRODUCT_COMPONENT_KEYWORDS["web-deck"])
        required -= STATIC_PRESENTATION_ONLY_KEYWORDS
    return required


def is_website_template_receipt(receipt: dict[str, Any]) -> bool:
    combined = " ".join(
        str(receipt.get(field, "")).lower()
        for field in ("productFamily", "mode", "designSystemScope", "templateName", "templateId")
    )
    markers = {"website", "figma", "source", "template", "ecommerce", "saas", "consultant", "landing"}
    return any(marker in combined for marker in markers)


def board_metrics(receipt: dict[str, Any]) -> dict[str, Any]:
    direct = receipt.get("boardMetrics")
    if isinstance(direct, dict):
        return direct
    evidence = receipt.get("artifactEvidence")
    if isinstance(evidence, dict) and isinstance(evidence.get("boardMetrics"), dict):
        return evidence["boardMetrics"]
    return {}


def numeric_metric(metrics: dict[str, Any], key: str) -> float | None:
    value = metrics.get(key)
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def validate_artifact_evidence(receipt: dict[str, Any]) -> tuple[str, list[str]]:
    evidence = receipt.get("artifactEvidence")
    warnings: list[str] = []
    if not isinstance(evidence, dict):
        return "MISSING", ["artifactEvidence missing; receipt proves structure only, not final source artifact evidence"]

    present = [field for field in ARTIFACT_EVIDENCE_FIELDS if evidence.get(field) not in (None, "", [], {})]
    if not present:
        return "MISSING", ["artifactEvidence has no concrete source/render/Figma proof fields"]

    source_signals = {"figmaNodeSummaryPath", "designSystemPageId", "sourceComponentInventoryPath", "componentInventory", "tokenSourcePath"}
    visual_signals = {"screenshotPath", "renderPath"}
    has_source = any(field in present for field in source_signals)
    has_visual = any(field in present for field in visual_signals)
    if not has_source:
        warnings.append("artifactEvidence lacks source/component/token proof")
    if not has_visual:
        warnings.append("artifactEvidence lacks screenshot/render proof")
    if has_source and has_visual:
        return "PASS", warnings
    return "LIMITED", warnings


def resolve_receipt(build_dir: Path, template_id: str = "") -> Path | None:
    candidates: list[Path] = []
    for pattern in (
        "design-system-receipt.json",
        "design_system_receipt.json",
        "design-system*.json",
        "design_system*.json",
        "design-system-receipts/*.json",
        "design_system_receipts/*.json",
    ):
        candidates.extend(build_dir.glob(pattern))
    if template_id:
        for path in candidates:
            try:
                payload = load_json(path)
            except Exception:
                continue
            if str(payload.get("templateId", "")) == template_id:
                return path
    return candidates[0] if candidates else None


def validate_design_system(receipt: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    for field in (
        "templateId",
        "productFamily",
        "designSystemScope",
        "productDna",
        "colorTokens",
        "typographyTokens",
        "spacingTokens",
        "components",
        "productSpecificModules",
        "states",
        "reusableSectionPatterns",
        "visualLanguageRules",
        "referenceStandardCoverage",
        "usageExamples",
        "packageSourceMap",
        "accessibilityEditingNotes",
        "sourceHygiene",
    ):
        if field not in receipt:
            errors.append(f"missing required field: {field}")

    for field in sorted(REQUIRED_FUNCTIONAL_FIELDS):
        if not is_meaningful(receipt.get(field)):
            errors.append(f"missing functional design-system coverage: {field}")

    color_tokens = normalize_items(receipt.get("colorTokens"))
    missing_color = sorted(REQUIRED_COLOR_TOKENS - color_tokens)
    if missing_color:
        errors.append("missing color tokens: " + ", ".join(missing_color))

    type_tokens = normalize_items(receipt.get("typographyTokens"))
    missing_type = sorted(REQUIRED_TYPE_TOKENS - type_tokens)
    if missing_type:
        errors.append("missing typography tokens: " + ", ".join(missing_type))

    spacing_tokens = normalize_items(receipt.get("spacingTokens"))
    missing_spacing = sorted(REQUIRED_SPACING_TOKENS - spacing_tokens)
    if missing_spacing:
        errors.append("missing spacing tokens: " + ", ".join(missing_spacing))

    state_tokens = normalize_items(receipt.get("states"))
    missing_states = sorted(REQUIRED_STATES - state_tokens)
    if missing_states:
        errors.append("missing component states: " + ", ".join(missing_states))

    component_text = components_text(receipt)
    if not has_keywords(component_text, BASE_COMPONENT_KEYWORDS):
        errors.append("base component inventory is incomplete")
    required_product_keywords = product_keywords(receipt)
    missing_product_keywords = missing_keywords(component_text, required_product_keywords)
    if missing_product_keywords:
        errors.append("missing product-specific components: " + ", ".join(sorted(missing_product_keywords)))

    if is_website_template_receipt(receipt):
        count_checks = {
            "components": item_count(receipt.get("components")),
            "productSpecificModules": item_count(receipt.get("productSpecificModules")),
            "reusableSectionPatterns": item_count(receipt.get("reusableSectionPatterns")),
            "usageExamples": item_count(receipt.get("usageExamples")),
        }
        for key, minimum in (
            ("components", MIN_PRODUCT_GRADE_COUNTS["components"]),
            ("productSpecificModules", MIN_PRODUCT_GRADE_COUNTS["productSpecificModules"]),
            ("reusableSectionPatterns", MIN_PRODUCT_GRADE_COUNTS["reusableSectionPatterns"]),
            ("usageExamples", MIN_PRODUCT_GRADE_COUNTS["usageExamples"]),
        ):
            if count_checks[key] < minimum:
                errors.append(f"product-grade design-system depth too thin: {key}={count_checks[key]} minimum={minimum}")

        metrics = board_metrics(receipt)
        if not metrics:
            errors.append("missing boardMetrics for product-grade Figma/source website design system")
        else:
            metric_requirements = {
                "panelCount": ("boardPanels", "design-system board panel count"),
                "componentSpecimenCount": ("componentSpecimens", "component specimen count"),
                "productSpecificModuleCount": ("productModuleSpecimens", "product-specific module specimen count"),
                "stateExampleCount": ("stateExamples", "state example count"),
            }
            for metric_key, (minimum_key, label) in metric_requirements.items():
                value = numeric_metric(metrics, metric_key)
                minimum = MIN_PRODUCT_GRADE_COUNTS[minimum_key]
                if value is None or value < minimum:
                    errors.append(f"{label} too thin: {metric_key}={value if value is not None else 'missing'} minimum={minimum}")
            height = numeric_metric(metrics, "boardHeight")
            if height is not None and height < MIN_WEBSITE_BOARD_HEIGHT:
                errors.append(f"design-system board height is below product-grade depth: boardHeight={height:g} minimum={MIN_WEBSITE_BOARD_HEIGHT}")

        compact_summary = (
            item_count(receipt.get("components")) <= 5
            or item_count(receipt.get("productSpecificModules")) < MIN_PRODUCT_GRADE_COUNTS["productSpecificModules"]
            or item_count(receipt.get("reusableSectionPatterns")) < MIN_PRODUCT_GRADE_COUNTS["reusableSectionPatterns"]
        )
        if compact_summary:
            errors.append("design system resembles a compact style summary; build a buyer-usable product kit instead")

    source = receipt.get("sourceHygiene", {})
    if not isinstance(source, dict):
        errors.append("sourceHygiene must be an object")
        source = {}
    source_requirements = {
        "autoLayout": "auto-layout/source hygiene missing",
        "editableText": "editable text missing",
        "editablePlaceholders": "editable placeholders missing",
        "clearLayerNames": "clear layer names missing",
        "reusableComponents": "reusable components missing",
        "responsiveConstraints": "responsive constraints missing",
    }
    for key, message in source_requirements.items():
        if source.get(key) is not True:
            errors.append(message)
    if source.get("flattenedImportantContent") is True:
        errors.append("important content is flattened")

    artifact_status, artifact_warnings = validate_artifact_evidence(receipt)
    warnings.extend(artifact_warnings)

    status = "PASS" if not errors else "FAIL"
    if receipt.get("status") == "PASS" and errors:
        warnings.append("receipt status says PASS but validation found failures")

    return {
        "status": status,
        "templateId": str(receipt.get("templateId", "")),
        "errors": errors,
        "warnings": warnings,
        "artifactEvidenceStatus": artifact_status,
    }


def main() -> int:
    args = parse_args()
    if args.receipt:
        receipt_path = Path(args.receipt).expanduser().resolve()
    elif args.build_dir:
        receipt_path = resolve_receipt(Path(args.build_dir).expanduser().resolve(), args.template_id)
        if receipt_path is None:
            result = {"status": "FAIL", "errors": ["design system receipt not found"], "warnings": []}
            print(json.dumps(result, indent=2) if args.json else "FAIL: design system receipt not found")
            return 1
    else:
        raise SystemExit("Provide --receipt or --build-dir.")

    try:
        receipt = load_json(receipt_path)
        result = validate_design_system(receipt)
    except Exception as exc:
        result = {"status": "FAIL", "errors": [f"invalid receipt JSON: {exc}"], "warnings": []}

    result["receiptPath"] = str(receipt_path)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['status']}: {receipt_path}")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
