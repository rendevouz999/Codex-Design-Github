#!/usr/bin/env python
"""Smoke tests for section layout matching and dedupe behavior."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import design_brain_section_layout_extract as section_tool  # noqa: E402


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def base_pattern(pattern_id: str, section: str = "hero", *, stable: bool = True) -> dict[str, Any]:
    pattern: dict[str, Any] = {
        "patternId": pattern_id,
        "sectionType": section,
        "sourceRefs": ["matching-smoke-fixture"],
        "productFamilies": ["saas", "website"],
        "commercialPurpose": "Smoke fixture pattern with enough commercial purpose detail.",
        "purposeLayer": "Proves that matching can separate duplicate, variant, and new layout vocabulary.",
        "anatomyLayer": "Headline, proof cue, CTA row, offset media stage, and compact trust module.",
        "hierarchyLayer": "Primary message first, proof cue second, media credibility third, CTA fourth.",
        "gridRhythmLayer": "Asymmetric twelve column grid with a narrow proof rail and wide media stage.",
        "densityLimitLayer": "Hero keeps one primary message, one to two CTAs, one proof cue, and one media system.",
        "originalityLayer": "Use abstract layout vocabulary only; never copy exact source composition.",
        "usageRuleLayer": "Stable fixture can be selected only after PASS evidence in smoke tests.",
        "layoutGesture": "asymmetric proof rail",
        "sectionSilhouette": "wide masthead with offset media bay",
        "compositionTension": "left message weight balanced by right interface depth",
        "focalPath": "headline to proof cue to dashboard media to CTA",
        "negativeSpaceShape": "diagonal runway",
        "depthLayering": "layered panels",
        "moduleScaleVariation": "large media with small proof modules",
        "breakoutBehavior": "contained media breakout",
        "contentLimits": {"primaryMessage": 1, "cta": "1-2", "proofCue": 1, "mediaSystem": 1},
        "antiCopyBoundary": "Do not copy exact visual execution, spacing, color roles, imagery, or motif.",
        "compatibleBeforeAfter": {"before": ["navigation"], "after": ["trust-band", "features"], "notAScaffold": True},
        "confidence": "high" if stable else "medium",
        "qualityStatus": "PASS" if stable else "REVIEW_REQUIRED",
        "hyperAccuracyReceipt": {
            "status": "PASS" if stable else "REVIEW_REQUIRED",
            "reviewedAt": "2026-06-02" if stable else "",
            "evidenceType": "smoke fixture",
            "reviewNotes": "Fixture proves section layout matching behavior.",
            "nonCopyBoundary": "No source execution is copied.",
        },
    }
    signature = section_tool.structural_signature(pattern)
    pattern.update(
        {
            "structuralSignature": signature,
            "matchStatus": "NEW_PATTERN",
            "matchScore": 0.0,
            "matchGroupId": signature["signatureId"],
            "duplicateOf": None,
            "variantOf": None,
            "matchingEvidence": {
                "mode": "smoke-fixture",
                "matchingAxes": section_tool.MATCH_AXES,
                "thresholds": section_tool.MATCH_THRESHOLDS,
            },
            "dedupeDecision": "Fixture baseline pattern.",
        }
    )
    return pattern


def candidate(pattern_id: str, changes: dict[str, Any]) -> dict[str, Any]:
    payload = base_pattern(pattern_id, stable=False)
    payload.update(changes)
    return payload


def main() -> int:
    root = repo_root()
    tool = root / "scripts" / "design_brain_section_layout_extract.py"

    with tempfile.TemporaryDirectory(prefix="section-layout-matching-") as tmp:
        tmp_path = Path(tmp)
        catalog = tmp_path / "catalog"
        section_tool.ensure_catalog(catalog)
        stable = base_pattern("hero-saas-proof-rail")
        write_json(catalog / "hero" / "patterns" / "hero-saas-proof-rail.json", stable)

        exact = candidate("candidate-exact-duplicate", {})
        pattern_path, receipt_path, matched = section_tool.write_candidate_with_matching(catalog, exact)
        if pattern_path is not None or receipt_path is None or matched.get("matchStatus") != "DUPLICATE":
            print("Exact duplicate should create a receipt only and no incoming pattern.")
            return 1

        near = candidate(
            "candidate-near-duplicate",
            {
                "layoutGesture": "vertical launch column",
                "sectionSilhouette": "stacked launch panel",
            },
        )
        near_path, near_receipt, near_matched = section_tool.write_candidate_with_matching(catalog, near)
        if not near_path or not near_receipt or near_matched.get("matchStatus") != "NEAR_DUPLICATE":
            print("Near duplicate should create both a candidate and match receipt.")
            print(json.dumps(near_matched, indent=2))
            return 1

        variant = candidate(
            "candidate-variant",
            {
                "layoutGesture": "split editorial tower",
                "sectionSilhouette": "tall stacked stage",
                "compositionTension": "centered claim against bottom proof shelf",
                "focalPath": "badge to headline to proof shelf to CTA",
            },
        )
        variant_path, _variant_receipt, variant_matched = section_tool.write_candidate_with_matching(catalog, variant)
        if not variant_path or variant_matched.get("matchStatus") != "VARIANT":
            print("Variant should remain as an incoming candidate.")
            print(json.dumps(variant_matched, indent=2))
            return 1
        variant_payload = json.loads(variant_path.read_text(encoding="utf-8"))
        if not variant_payload.get("variantOf"):
            print("Variant candidate did not keep variantOf.")
            return 1

        fresh = candidate(
            "candidate-new-pattern",
            {
                "layoutGesture": "editorial magazine opener",
                "sectionSilhouette": "full bleed image strip",
                "compositionTension": "large vertical title against staggered captions",
                "focalPath": "image caption to title to category pills to booking CTA",
                "negativeSpaceShape": "open margin field",
                "depthLayering": "flat editorial spread",
                "moduleScaleVariation": "one oversized image with tiny caption stack",
                "breakoutBehavior": "full bleed photo rail",
            },
        )
        fresh_path, _fresh_receipt, fresh_matched = section_tool.write_candidate_with_matching(catalog, fresh)
        if not fresh_path or fresh_matched.get("matchStatus") != "NEW_PATTERN":
            print("New pattern should be classified as NEW_PATTERN.")
            print(json.dumps(fresh_matched, indent=2))
            return 1

        candidate_path = tmp_path / "match-candidate.json"
        write_json(candidate_path, exact)
        match_cli = run(
            [sys.executable, str(tool), "match", "--candidate", str(candidate_path), "--catalog", str(catalog), "--json"],
            root,
        )
        if match_cli.returncode != 0:
            print(match_cli.stdout)
            print(match_cli.stderr)
            return 1
        match_payload = json.loads(match_cli.stdout)
        if match_payload.get("matchStatus") != "DUPLICATE":
            print("CLI match did not detect exact duplicate.")
            print(match_cli.stdout)
            return 1

        duplicate_catalog = tmp_path / "duplicate-catalog"
        section_tool.ensure_catalog(duplicate_catalog)
        write_json(duplicate_catalog / "hero" / "patterns" / "hero-a.json", base_pattern("hero-a"))
        write_json(duplicate_catalog / "hero" / "patterns" / "hero-b.json", base_pattern("hero-b"))
        validation = run([sys.executable, str(tool), "validate", "--catalog", str(duplicate_catalog), "--json"], root)
        if validation.returncode == 0:
            print("Stable duplicate validation should fail.")
            print(validation.stdout)
            return 1
        validation_payload = json.loads(validation.stdout)
        if not any("stable duplicate patterns" in error for error in validation_payload.get("errors", [])):
            print("Stable duplicate validation did not report duplicate patterns.")
            print(validation.stdout)
            return 1

    print("PASS: section layout matching smoke test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
