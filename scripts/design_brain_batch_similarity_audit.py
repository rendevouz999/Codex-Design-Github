#!/usr/bin/env python
"""Run pairwise scaffold/similarity checks for Brain Design template batches."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from design_brain_layout_similarity_audit import audit_batch as audit_layout_batch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit batch template pairwise similarity.")
    parser.add_argument("--batch-dir", default="", help="Directory containing template fingerprint JSON files.")
    parser.add_argument("--fingerprints", nargs="*", default=[], help="Explicit fingerprint JSON files.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_fingerprints(batch_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for pattern in ("template-fingerprints/*.json", "fingerprints/*.json", "*fingerprint*.json", "template-*.json"):
        paths.extend(batch_dir.glob(pattern))
    return sorted(set(paths))


def audit_fingerprints(fingerprints: list[dict[str, Any]], batch_id: str = "batch") -> dict[str, Any]:
    if len(fingerprints) < 2:
        return {
            "batchId": batch_id,
            "pairs": [],
            "overallRisk": "low",
            "requiredRepairs": [],
            "status": "PASS",
        }
    layout_result = audit_layout_batch(fingerprints, batch_id=batch_id)
    pairs = []
    for item in layout_result.get("pairMatrix", []):
        scores = item.get("axisScores", {})
        structural = max(
            float(scores.get("heroGrammarSimilarity", 0.0)),
            float(scores.get("sectionOrderSimilarity", 0.0)),
            float(scores.get("gridSystemSimilarity", 0.0)),
            float(scores.get("layoutGestureSimilarity", 0.0)),
            float(scores.get("sectionSilhouetteSimilarity", 0.0)),
            float(scores.get("compositionTensionSimilarity", 0.0)),
            float(scores.get("focalPathSimilarity", 0.0)),
            float(scores.get("moduleScaleVariationSimilarity", 0.0)),
            float(scores.get("componentPatternSimilarity", 0.0)),
            float(scores.get("ctaPlacementSimilarity", 0.0)),
            float(scores.get("closureSilhouetteSimilarity", 0.0)),
        )
        visual = max(
            float(scores.get("colorRoleSimilarity", 0.0)),
            float(scores.get("effectLanguageSimilarity", 0.0)),
            float(scores.get("imageTreatmentSimilarity", 0.0)),
            float(scores.get("typographyBehaviorSimilarity", 0.0)),
            float(scores.get("negativeSpaceShapeSimilarity", 0.0)),
            float(scores.get("depthLayeringSimilarity", 0.0)),
            float(scores.get("breakoutBehaviorSimilarity", 0.0)),
        )
        pairs.append(
            {
                "pair": [item.get("candidate"), item.get("comparedAgainst")],
                "structureDefiningAxisSimilarity": round(structural, 3),
                "visualLanguageAxisSimilarity": round(visual, 3),
                "scaffoldRisk": item.get("overallScaffoldRisk", 0.0),
                "failedAxes": item.get("failedAxes", []),
                "hardFailAxes": item.get("hardFailAxes", []),
                "softRiskAxes": item.get("softRiskAxes", []),
                "requiredStructuralRepairs": item.get("requiredRepairs", []),
                "axisScores": scores,
                "status": "FAIL" if item.get("status") != "PASS" else "PASS",
            }
        )
    repairs: list[str] = []
    for item in pairs:
        repairs.extend(item["requiredStructuralRepairs"])
    max_similarity = max(float(item["scaffoldRisk"]) for item in pairs) if pairs else 0.0
    risk = "high" if max_similarity >= 0.65 else "medium" if max_similarity >= 0.50 else "low"
    return {
        "batchId": batch_id,
        "pairs": pairs,
        "overallRisk": risk,
        "requiredRepairs": repairs,
        "failedAxes": layout_result.get("failedAxes", []),
        "hardFailAxes": layout_result.get("hardFailAxes", []),
        "softRiskAxes": layout_result.get("softRiskAxes", []),
        "structureDefiningAxisSimilarity": layout_result.get("structureDefiningAxisSimilarity", 0.0),
        "visualLanguageAxisSimilarity": layout_result.get("visualLanguageAxisSimilarity", 0.0),
        "status": "FAIL" if any(item["status"] == "FAIL" for item in pairs) else "PASS",
    }


def main() -> int:
    args = parse_args()
    paths = [Path(path).expanduser().resolve() for path in args.fingerprints]
    if args.batch_dir:
        paths.extend(discover_fingerprints(Path(args.batch_dir).expanduser().resolve()))
    paths = sorted(set(paths))
    if not paths:
        result = {"batchId": "batch", "pairs": [], "overallRisk": "high", "requiredRepairs": ["No template fingerprints found."], "status": "FAIL"}
    else:
        fingerprints = [load_json(path) for path in paths]
        result = audit_fingerprints(fingerprints, batch_id=Path(args.batch_dir).name if args.batch_dir else "batch")
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['status']}: {len(result['pairs'])} pairs checked, risk={result['overallRisk']}")
        for repair in result.get("requiredRepairs", []):
            print(f"- {repair}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
