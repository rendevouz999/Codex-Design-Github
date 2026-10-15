#!/usr/bin/env python
"""Smoke tests for section layout extraction and similarity gating."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True


REQUIRED_FINGERPRINT_FIELDS = {
    "templateId": "tpl",
    "sourceType": "ai_output",
    "productFamily": "saas",
    "mode": "test",
    "heroGrammar": "asymmetric proof-first hero",
    "sectionOrder": ["hero", "features", "pricing", "cta", "footer"],
    "gridSystem": "12-column editorial grid",
    "layoutGesture": "editorial rail",
    "sectionSilhouettes": ["masthead", "feature well", "pricing island", "footer slab"],
    "compositionTension": "offset rail beside dense modules",
    "focalPath": "headline > proof rail > CTA",
    "negativeSpaceShape": "runway",
    "depthLayering": "layered panels",
    "moduleScaleVariation": "large-small alternation",
    "breakoutBehavior": "full-bleed proof strip",
    "layoutRhythm": "calm-dense-calm",
    "cardCadence": "mixed card sizes",
    "componentPatterns": "feature modules, pricing tiers, CTA bar",
    "ctaPlacement": "hero and final action",
    "closureSilhouette": "proof-led action footer",
    "imageTreatment": "dashboard placeholders",
    "spacingCadence": "section-variable",
    "typographyBehavior": "strong display and compact labels",
    "colorRoles": "dark stage with signal accent",
    "effectLanguage": "soft surface depth",
    "navigationPattern": "compact nav",
    "footerPattern": "ledger footer",
    "designSystemId": "ds-test",
    "visualGrammarSummary": "test grammar",
    "marketplaceReadinessSummary": "test ready",
    "sectionPatternMix": [
        {"sectionType": "hero", "patternId": "hero-saas-proof-stage"},
        {"sectionType": "features", "patternId": "features-saas-proof-rail"},
    ],
    "sectionPatternIds": ["hero-saas-proof-stage", "features-saas-proof-rail"],
    "sectionDensityLimits": {"hero": "1 message, 1-2 CTA", "features": "3-6 modules"},
    "catalogDivergenceNotes": "test fixture",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def stable_pattern(pattern_id: str, section: str, family: str) -> dict[str, object]:
    payload: dict[str, object] = {
        "patternId": pattern_id,
        "sectionType": section,
        "sourceRefs": ["smoke-fixture"],
        "productFamilies": [family, "website"],
        "commercialPurpose": "Smoke fixture pattern with enough commercial purpose detail.",
        "purposeLayer": "Proves that section-level selection can return a stable pattern.",
        "anatomyLayer": "Headline, proof cue, module group, CTA, and placeholder media.",
        "hierarchyLayer": "Primary message first, evidence second, action third.",
        "gridRhythmLayer": "Asymmetric grid with controlled section rhythm.",
        "densityLimitLayer": "Uses the section density limit and avoids clutter.",
        "originalityLayer": "Use abstract layout vocabulary only; do not copy a source section.",
        "usageRuleLayer": "Valid only as a smoke fixture for stable PASS selection.",
        "layoutGesture": "editorial rail",
        "sectionSilhouette": "masthead",
        "compositionTension": "offset proof rail",
        "focalPath": "headline > proof > CTA",
        "negativeSpaceShape": "runway",
        "depthLayering": "layered panels",
        "moduleScaleVariation": "large-small alternation",
        "breakoutBehavior": "contained breakout strip",
        "contentLimits": {"primaryModules": "3-6", "cta": "1-2"},
        "antiCopyBoundary": "Do not copy exact visual execution from any source.",
        "compatibleBeforeAfter": {"before": ["navigation"], "after": ["proof", "features"], "notAScaffold": True},
        "confidence": "high",
        "qualityStatus": "PASS",
        "hyperAccuracyReceipt": {
            "status": "PASS",
            "reviewedAt": "2026-06-02",
            "evidenceType": "smoke fixture",
            "reviewNotes": "Fixture proves validation and selection behavior.",
            "nonCopyBoundary": "No source execution is copied.",
        },
    }
    payload.update(
        {
            "structuralSignature": {
                "signatureId": f"{section}:{pattern_id}",
                "hash": f"smoke-{pattern_id}",
                "axes": {
                    "layoutGesture": payload["layoutGesture"],
                    "sectionSilhouette": payload["sectionSilhouette"],
                    "anatomyLayer": payload["anatomyLayer"],
                    "hierarchyLayer": payload["hierarchyLayer"],
                    "gridRhythmLayer": payload["gridRhythmLayer"],
                    "focalPath": payload["focalPath"],
                    "compositionTension": payload["compositionTension"],
                    "negativeSpaceShape": payload["negativeSpaceShape"],
                    "moduleScaleVariation": payload["moduleScaleVariation"],
                    "breakoutBehavior": payload["breakoutBehavior"],
                    "contentLimits": payload["contentLimits"],
                },
            },
            "matchStatus": "NEW_PATTERN",
            "matchScore": 0.0,
            "matchGroupId": f"{section}:{pattern_id}",
            "duplicateOf": None,
            "variantOf": None,
            "matchingEvidence": {
                "mode": "smoke-fixture",
                "matchingAxes": [
                    "layoutGesture",
                    "sectionSilhouette",
                    "anatomyLayer",
                    "hierarchyLayer",
                    "gridRhythmLayer",
                    "focalPath",
                    "compositionTension",
                    "negativeSpaceShape",
                    "moduleScaleVariation",
                    "breakoutBehavior",
                    "contentLimits",
                ],
            },
            "dedupeDecision": "Fixture baseline pattern.",
        }
    )
    return payload


def main() -> int:
    root = repo_root()
    tool = root / "scripts" / "design_brain_section_layout_extract.py"
    layout_audit = root / "scripts" / "design_brain_layout_similarity_audit.py"

    with tempfile.TemporaryDirectory(prefix="section-layout-smoke-") as tmp:
        tmp_path = Path(tmp)
        catalog = tmp_path / "catalog"
        new_refs = tmp_path / "new-refs"
        new_refs.mkdir()
        (new_refs / "hero-reference.png").write_bytes(b"not-a-real-image-but-valid-test-source")

        extract = run(
            [
                sys.executable,
                str(tool),
                "extract",
                "--source",
                ".design-brain/evidence/fig-extracts",
                "--new-source",
                str(new_refs),
                "--mode",
                "hybrid",
                "--output",
                str(catalog),
                "--max-patterns",
                "8",
                "--json",
            ],
            root,
        )
        if extract.returncode != 0:
            print(extract.stdout)
            print(extract.stderr)
            return 1

        incoming = list((catalog / "_incoming").glob("*/*.json"))
        incoming_patterns = [path for path in incoming if path.parent.name not in {"source-records", "_matches"}]
        if not incoming_patterns:
            print("Expected incoming patterns from extraction.")
            return 1
        if any(json.loads(path.read_text(encoding="utf-8")).get("qualityStatus") == "PASS" for path in incoming_patterns):
            print("Incoming extraction must not create stable PASS patterns.")
            return 1

        validate = run([sys.executable, str(tool), "validate", "--catalog", str(catalog), "--json"], root)
        if validate.returncode != 0:
            print(validate.stdout)
            print(validate.stderr)
            return 1

        write_json(catalog / "hero" / "patterns" / "hero-saas-proof-stage.json", stable_pattern("hero-saas-proof-stage", "hero", "saas"))
        write_json(catalog / "features" / "patterns" / "features-saas-proof-rail.json", stable_pattern("features-saas-proof-rail", "features", "saas"))
        write_json(catalog / "pricing-packages" / "patterns" / "pricing-agency-package-island.json", stable_pattern("pricing-agency-package-island", "pricing-packages", "agency"))

        for section, family in [("hero", "saas"), ("features", "saas"), ("pricing", "agency")]:
            selected = run(
                [
                    sys.executable,
                    str(tool),
                    "select",
                    "--catalog",
                    str(catalog),
                    "--product-family",
                    family,
                    "--section",
                    section,
                    "--density",
                    "balanced",
                    "--json",
                ],
                root,
            )
            if selected.returncode != 0:
                print(selected.stdout)
                print(selected.stderr)
                return 1
            payload = json.loads(selected.stdout)
            if not payload.get("selectedPattern", {}).get("contentLimits") or not payload.get("antiCopyBoundary"):
                print("Selection did not return contentLimits and antiCopyBoundary.")
                return 1

        first = dict(REQUIRED_FINGERPRINT_FIELDS)
        second = dict(REQUIRED_FINGERPRINT_FIELDS)
        second["templateId"] = "tpl-2"
        first_path = tmp_path / "first.json"
        second_path = tmp_path / "second.json"
        write_json(first_path, first)
        write_json(second_path, second)

        audit = run(
            [
                sys.executable,
                str(layout_audit),
                "--candidate",
                str(second_path),
                "--reference",
                str(first_path),
                "--type",
                "ai-vs-reference",
                "--json",
            ],
            root,
        )
        if audit.returncode == 0:
            print("Expected layout audit to block identical sectionPatternMix.")
            print(audit.stdout)
            return 1
        audit_payload = json.loads(audit.stdout)
        if "sectionPatternMixSimilarity" not in audit_payload.get("failedAxes", []):
            print("Expected sectionPatternMixSimilarity failed axis.")
            print(audit.stdout)
            return 1

    print("PASS: section layout extraction smoke test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
