#!/usr/bin/env python
"""Run Brain Design post-build completion validation."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from design_brain_batch_similarity_audit import audit_fingerprints
from design_brain_build_session import (
    reference_usage_receipt_status,
    template_requires_reference_usage,
    template_requires_web_deck_evidence,
    web_deck_evidence_issues,
)
from design_brain_design_cognition_check import validate_cognition
from design_brain_design_system_check import is_web_deck_text, validate_design_system
from design_brain_sequential_provenance_check import validate_sequential_provenance
from design_brain_visual_inspect import file_ref, verify_manifest


CRITICAL_VISUAL_TERMS = {
    "overlap",
    "text overlap",
    "overflow",
    "clipping",
    "clipped",
    "outside frame",
    "poor contrast",
    "unreadable",
    "alignment break",
    "z-index",
    "stacking",
    "crop issue",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Brain Design post-build completion audit.")
    parser.add_argument("--build-dir", required=True, help="Directory containing build artifacts/receipts.")
    parser.add_argument("--session", default="", help="Optional build-session lifecycle directory or ledger JSON.")
    parser.add_argument("--expected-templates", type=int, default=1)
    parser.add_argument("--batch", action="store_true")
    parser.add_argument("--template-plan", default="")
    parser.add_argument("--design-system", default="")
    parser.add_argument("--cognition-receipt", default="")
    parser.add_argument("--require-cognition", action="store_true")
    parser.add_argument("--allow-missing-cognition", action="store_true")
    parser.add_argument("--figma-summary", default="")
    parser.add_argument("--screenshot-dir", default="")
    parser.add_argument("--visual-inspection", default="", help="Current visual inspection manifest; default: build-dir/visual-inspection.json.")
    parser.add_argument("--visual-artifact", default="", help="Expected current artifact path for the visual inspection; required to establish target identity.")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--max-repair-cycles", type=int, default=3)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--require-completion-receipt", action="store_true")
    parser.add_argument("--no-require-completion-receipt", action="store_true")
    parser.add_argument("--diagnostic-only", action="store_true")
    parser.add_argument("--allow-visual-limitation", action="store_true")
    parser.add_argument("--mode", default="")
    parser.add_argument("--product-family", default="")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_json(build_dir: Path, patterns: list[str]) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(build_dir.glob(pattern))
    return sorted(set(path for path in paths if path.is_file()))


def discover_fingerprints(build_dir: Path) -> list[Path]:
    return discover_json(build_dir, ["template-fingerprints/*.json", "fingerprints/*.json", "*fingerprint*.json", "template-*.json"])


def discover_design_systems(build_dir: Path, explicit: str = "") -> list[Path]:
    if explicit:
        return [Path(explicit).expanduser().resolve()]
    return discover_json(
        build_dir,
        [
            "design-system-receipts/*.json",
            "design_system_receipts/*.json",
            "design-system-receipt.json",
            "design_system_receipt.json",
            "design-system*.json",
            "design_system*.json",
        ],
    )


def discover_visual_reports(build_dir: Path) -> list[Path]:
    return discover_json(build_dir, ["visual-qa*.json", "visual_qa*.json", "layout-qa*.json", "layout_qa*.json"])


def visual_audit(build_dir: Path, screenshot_dir: str = "", inspection: str = "", expected_artifact: str = "") -> dict[str, Any]:
    reports = discover_visual_reports(build_dir)
    issues: list[str] = []
    for path in reports:
        try:
            payload = load_json(path)
            if not isinstance(payload, dict):
                raise ValueError("visual QA report must be a JSON object")
        except Exception as exc:
            issues.append(f"invalid visual QA report {path.name}: {exc}")
            continue
        raw_issues = payload.get("issues", [])
        if isinstance(raw_issues, list):
            for item in raw_issues:
                if isinstance(item, dict):
                    severity = str(item.get("severity", "")).lower()
                    text = str(item.get("type") or item.get("message") or item)
                    if severity in {"critical", "high"} or any(term in text.lower() for term in CRITICAL_VISUAL_TERMS):
                        issues.append(text)
                else:
                    text = str(item)
                    if any(term in text.lower() for term in CRITICAL_VISUAL_TERMS):
                        issues.append(text)
    # Screenshot existence and issue-free legacy metadata cannot attest visual review.
    # Keep those reports for defect detection while requiring current inspected pixels.
    manifest_path = Path(inspection).expanduser().resolve() if inspection else build_dir / "visual-inspection.json"
    verification = None
    verified_manifests: list[dict[str, str]] = []
    if manifest_path.exists() or inspection:
        verification = verify_manifest(manifest_path, stage="final", expected_artifact=expected_artifact or None)
        if verification["status"] != "PASS":
            issues.extend(f"visual inspection: {item}" for item in verification["issues"])
        else:
            verified_manifests.append(file_ref(manifest_path))
    if issues:
        status = "FAIL"
    elif verified_manifests:
        status = "PASS"
    else:
        status = "LIMITED"
    return {
        "status": status,
        "issues": issues,
        "visualVerificationStatus": "current_evidence_and_explicit_main_review" if status == "PASS" else "inspection_failed" if status == "FAIL" else "not_verified",
        "visualInspectionManifests": verified_manifests,
        "visualInspectionValidation": verification,
        "limitation": "Technical receipt validation cannot prove actual seeing or creative quality; Main/Engineer attestations remain accountable human/model claims.",
    }


def completion_receipt_exists(build_dir: Path) -> bool:
    candidates = discover_json(build_dir, ["completion-receipt.json", "completion_receipt.json", "final-completion-receipt.json"])
    for path in candidates:
        try:
            payload = load_json(path)
        except Exception:
            continue
        if payload.get("finalStatus") in {"READY", "READY_WITH_LIMITATIONS", "REVISE_REQUIRED", "BLOCKED"}:
            return True
    return False


def completion_receipt_required(args: argparse.Namespace) -> bool:
    if getattr(args, "diagnostic_only", False) or getattr(args, "no_require_completion_receipt", False):
        return False
    if getattr(args, "require_completion_receipt", False) or getattr(args, "strict", False):
        return True
    mode = str(getattr(args, "mode", "") or "").lower()
    product = str(getattr(args, "product_family", "") or "").lower()
    if is_web_deck_text(f"{mode} {product}"):
        return True
    markers = {
        "template",
        "website",
        "dashboard",
        "presentation",
        "ecommerce",
        "brand",
        "ui-kit",
        "figma",
        "source",
        "marketplace",
        "static",
    }
    return bool(markers & set(mode.replace("_", "-").split("-") + product.replace("_", "-").split("-")))


def discover_cognition_receipts(build_dir: Path, explicit: str = "") -> list[Path]:
    if explicit:
        return [Path(explicit).expanduser().resolve()]
    return discover_json(
        build_dir,
        [
            "design-cognition-receipts/*.json",
            "design_cognition_receipts/*.json",
            "design-cognition-receipt.json",
            "design_cognition_receipt.json",
            "*cognition*receipt*.json",
        ],
    )


def post_build_requires_cognition(args: argparse.Namespace, build_dir: Path) -> bool:
    if getattr(args, "require_cognition", False):
        return True
    if getattr(args, "allow_missing_cognition", False):
        return False
    reference_markers = discover_json(
        build_dir,
        [
            "reference*.json",
            "reference-*/*.json",
            "reference-insight*.json",
            "template-plan*.json",
            "template-orchestration*.json",
            "*reference*.json",
        ],
    )
    if reference_markers:
        return True
    mode = str(getattr(args, "mode", "") or "").lower()
    product = str(getattr(args, "product_family", "") or "").lower()
    return "reference" in product or "reference" in mode


def load_session_ledger(session_arg: str) -> dict[str, Any]:
    if not session_arg:
        return {}
    session_path = Path(session_arg).expanduser().resolve()
    if session_path.is_dir():
        session_dir = session_path
        session_path = session_path / "build-session-ledger.json"
    else:
        session_dir = session_path.parent
    if not session_path.exists():
        return {"status": "BLOCKED", "issues": [f"build-session ledger not found: {session_path}"]}
    try:
        payload = load_json(session_path)
    except Exception as exc:
        return {"status": "BLOCKED", "issues": [f"build-session ledger invalid JSON: {exc}"]}
    issues: list[str] = []
    if not isinstance(payload.get("route"), dict) or not payload.get("route"):
        issues.append("build-session route missing")
    templates = payload.get("templates", [])
    expected = int(payload.get("expectedTemplateCount") or 0)
    if expected and len(templates) < expected:
        issues.append(f"build-session expected {expected} templates, found {len(templates)}")
    locked = 0
    completion_present = bool(payload.get("completionReceipt"))
    for index, item in enumerate(templates):
        template_id = str(item.get("templateId") or f"template-{index + 1}")
        stages = item.get("stages", [])
        if not isinstance(stages, list):
            stages = []
        if not item.get("cognitionReceiptPath"):
            issues.append(f"{template_id} missing cognition receipt path")
        if not item.get("simulationVerdictPath"):
            issues.append(f"{template_id} missing simulation verdict path")
        if not item.get("referenceLayoutAuditPath"):
            issues.append(f"{template_id} missing reference layout audit receipt")
        if index > 0 and not item.get("pairwiseAudits"):
            issues.append(f"{template_id} missing AI pairwise layout audit receipt")
        if not item.get("fingerprintPath"):
            issues.append(f"{template_id} missing fingerprint path")
        if not item.get("buildArtifactPath"):
            issues.append(f"{template_id} missing build artifact path")
        if item.get("status") == "fingerprint_locked":
            locked += 1
        else:
            issues.append(f"{template_id} fingerprint not locked")
        if not item.get("designSystemReceiptPath"):
            issues.append(f"{template_id} missing design system receipt")
        if not item.get("postBuildAuditPath"):
            issues.append(f"{template_id} missing post-build audit receipt")
        if template_requires_reference_usage(payload, item):
            if not str(item.get("candidateBrandName") or "").strip():
                issues.append(f"{template_id} missing candidate output brand name")
            if not str(item.get("referenceUsageMode") or "").strip():
                issues.append(f"{template_id} missing reference usage mode")
            if not str(item.get("referenceGroupKey") or "").strip():
                issues.append(f"{template_id} missing reference group key")
            check_ok, check_issues = reference_usage_receipt_status(
                session_dir,
                str(item.get("brandReferenceUsageCheckPath") or ""),
                "check",
            )
            if not check_ok:
                issues.append(f"{template_id} brand/reference usage check receipt not PASS: {'; '.join(check_issues)}")
            final_record_required = completion_present or "completion_receipt_created" in stages or "brand_reference_usage_recorded" in stages
            if final_record_required:
                record_ok, record_issues = reference_usage_receipt_status(
                    session_dir,
                    str(item.get("brandReferenceUsageRecordPath") or ""),
                    "record",
                )
                if not record_ok:
                    issues.append(f"{template_id} brand/reference usage registry record not PASS: {'; '.join(record_issues)}")
        if template_requires_web_deck_evidence(payload, item):
            for evidence_issue in web_deck_evidence_issues(item):
                issues.append(f"{template_id} {evidence_issue}")
    if expected and locked < expected:
        issues.append(f"build-session expected {expected} fingerprint locks, found {locked}")
    return {
        "status": "PASS" if not issues else "BLOCKED",
        "sessionId": payload.get("sessionId", ""),
        "expectedTemplateCount": expected,
        "templateCount": len(templates),
        "fingerprintLocks": locked,
        "issues": issues,
        "ledger": payload,
    }


def write_receipt(output_dir: Path, receipt: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "post-build-audit-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    if receipt.get("repairPlan"):
        (output_dir / "post-build-repair-plan.json").write_text(json.dumps(receipt["repairPlan"], indent=2) + "\n", encoding="utf-8", newline="\n")


def run_post_build_audit(args: argparse.Namespace) -> dict[str, Any]:
    build_dir = Path(args.build_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else build_dir
    fingerprint_paths = discover_fingerprints(build_dir)
    fingerprints = [load_json(path) for path in fingerprint_paths]
    template_ids = [str(item.get("templateId") or item.get("id") or f"template-{index}") for index, item in enumerate(fingerprints, start=1)]
    if not template_ids:
        template_ids = [f"template-{index}" for index in range(1, args.expected_templates + 1)]

    design_paths = discover_design_systems(build_dir, args.design_system)
    cognition_paths = discover_cognition_receipts(build_dir, getattr(args, "cognition_receipt", ""))
    session_result = load_session_ledger(getattr(args, "session", ""))
    provenance_result = validate_sequential_provenance(
        build_dir=build_dir,
        session_arg=getattr(args, "session", ""),
        expected_templates=args.expected_templates,
        batch=bool(args.batch),
        mode=getattr(args, "mode", ""),
        product_family=getattr(args, "product_family", ""),
    )
    cognition_required = post_build_requires_cognition(args, build_dir)
    cognition_results: dict[str, Any] = {}
    cognition_errors: list[str] = []
    if cognition_required and not cognition_paths:
        cognition_errors.append("Design Cognition Receipt is required for this post-build audit.")
    for path in cognition_paths:
        try:
            payload = load_json(path)
            result = validate_cognition(payload)
            key = str(payload.get("task") or path.stem)
        except Exception as exc:
            result = {"status": "FAIL", "missingFields": [], "riskCategories": ["invalid_receipt"], "requiredRepairs": [str(exc)]}
            key = path.stem
        cognition_results[key] = result
        if result.get("status") != "PASS":
            cognition_errors.extend(str(item) for item in result.get("requiredRepairs", []) or result.get("riskCategories", []))
    design_results: dict[str, Any] = {}
    design_errors: list[str] = []
    design_artifact_limitations: list[str] = []
    for path in design_paths:
        try:
            payload = load_json(path)
            result = validate_design_system(payload)
        except Exception as exc:
            result = {"status": "FAIL", "templateId": path.stem, "errors": [str(exc)], "warnings": []}
        key = str(result.get("templateId") or path.stem)
        design_results[key] = result
        design_errors.extend(str(error) for error in result.get("errors", []))
        artifact_status = str(result.get("artifactEvidenceStatus", "MISSING"))
        if artifact_status != "PASS":
            message = f"{key} design system artifact evidence is {artifact_status}; receipt-only/source-only proof cannot produce final READY."
            if args.strict:
                design_errors.append(message)
            else:
                design_artifact_limitations.append(message)
    if len(design_paths) < args.expected_templates:
        design_errors.append(f"expected {args.expected_templates} design system receipt(s), found {len(design_paths)}")

    batch_result = {"status": "PASS", "pairs": [], "requiredRepairs": [], "overallRisk": "low"}
    if args.batch or args.expected_templates > 1:
        if len(fingerprints) < args.expected_templates:
            batch_result = {
                "status": "FAIL",
                "pairs": [],
                "requiredRepairs": [f"expected {args.expected_templates} template fingerprints, found {len(fingerprints)}"],
                "overallRisk": "high",
            }
        else:
            batch_result = audit_fingerprints(fingerprints, batch_id=build_dir.name or "batch")

    visual = visual_audit(build_dir, args.screenshot_dir, getattr(args, "visual_inspection", ""), getattr(args, "visual_artifact", ""))
    has_completion_receipt = completion_receipt_exists(build_dir)
    completion_missing = completion_receipt_required(args) and not has_completion_receipt

    pass1_status = "FAIL" if batch_result["status"] == "FAIL" or cognition_errors else "PASS"
    pass2_status = "FAIL" if design_errors else "LIMITED" if design_artifact_limitations else "PASS"
    pass3_status = "FAIL" if visual["status"] == "FAIL" else "PASS" if visual["status"] == "PASS" else "LIMITED"

    repair_plan: list[dict[str, str]] = []
    for error in batch_result.get("requiredRepairs", []):
        repair_plan.append({"auditPass": "pass1", "issue": str(error), "repair": "Rebuild or recompose similar template fingerprint before final delivery."})
    for error in cognition_errors:
        repair_plan.append({"auditPass": "pass1", "issue": str(error), "repair": "Repair the Design Cognition Receipt or rebuild to honor Color Role Re-Mapping, Reference Boundary, Structural Reconfiguration, Section Logic, and Marketplace Readiness."})
    for error in design_errors:
        repair_plan.append({"auditPass": "pass2", "issue": str(error), "repair": "Complete design system/source hygiene and rerun audit."})
    for error in visual.get("issues", []):
        repair_plan.append({"auditPass": "pass3", "issue": str(error), "repair": "Fix layout/visual defect and rerun visual QA."})
    if completion_missing:
        repair_plan.append({"auditPass": "completion", "issue": "final completion receipt missing", "repair": "Generate completion receipt before final response."})
    for error in session_result.get("issues", []):
        repair_plan.append({"auditPass": "lifecycle", "issue": str(error), "repair": "Complete build-session lifecycle, rerun layout audit, and lock template fingerprint before final delivery."})
    for error in provenance_result.get("issues", []):
        repair_plan.append({"auditPass": "serial-provenance", "issue": str(error), "repair": "Rebuild through one completed template cycle at a time; lock and scaffold-dispose each template before starting the next."})

    critical_failure = bool(
        cognition_errors
        or design_errors
        or batch_result["status"] == "FAIL"
        or visual["status"] == "FAIL"
        or completion_missing
        or session_result.get("status") == "BLOCKED"
        or provenance_result.get("status") == "BLOCKED"
    )
    limitations: list[str] = []
    if visual["status"] == "LIMITED":
        limitations.append("No current visual inspection with explicit Main/Engineer observations was verified; source/legacy screenshot metadata cannot establish visual PASS.")
    limitations.extend(design_artifact_limitations)
    if (args.diagnostic_only or args.no_require_completion_receipt) and not has_completion_receipt:
        limitations.append("Completion receipt was not required for this diagnostic run; final status cannot be READY.")
    if critical_failure:
        final_status = "BLOCKED"
    elif args.diagnostic_only or args.no_require_completion_receipt:
        final_status = "READY_WITH_LIMITATIONS"
    elif visual["status"] == "LIMITED" or design_artifact_limitations:
        final_status = "READY_WITH_LIMITATIONS" if args.allow_visual_limitation else "REVISE_REQUIRED"
    else:
        final_status = "READY"

    receipt = {
        "buildId": f"post-build-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "templateCount": args.expected_templates,
        "templates": template_ids,
        "designCognitionRequired": cognition_required,
        "completionReceiptRequired": completion_receipt_required(args),
        "completionReceiptPresent": has_completion_receipt,
        "designSystemResults": design_results,
        "designCognitionResults": cognition_results,
        "auditPasses": {
            "pass0SerialProvenance": "PASS" if provenance_result.get("status") == "PASS" else "FAIL",
            "pass1OriginalityBatchSimilarity": pass1_status,
            "pass2DesignSystemSourceHygiene": pass2_status,
            "pass3VisualLayoutQA": pass3_status,
        },
        "serialProvenance": provenance_result,
        "batchSimilarity": batch_result,
        "buildSessionLifecycle": {
            "status": session_result.get("status", "not_provided") if session_result else "not_provided",
            "sessionId": session_result.get("sessionId", "") if session_result else "",
            "fingerprintLockStatus": "PASS" if session_result and session_result.get("status") == "PASS" else "N/A" if not session_result else "FAIL",
            "layoutAuditVsReference": "PASS" if session_result and session_result.get("status") == "PASS" else "N/A" if not session_result else "FAIL",
            "pairwiseAiLayoutAudit": "PASS" if session_result and session_result.get("status") == "PASS" else "N/A" if not session_result else "FAIL",
            "issues": session_result.get("issues", []) if session_result else [],
        },
        "layoutOriginality": {
            "buildSessionId": session_result.get("sessionId", "") if session_result else "",
            "layoutAuditVsReference": "PASS" if session_result and session_result.get("status") == "PASS" else "N/A" if not session_result else "FAIL",
            "pairwiseAiLayoutAudit": "PASS" if session_result and session_result.get("status") == "PASS" else "N/A" if not session_result else "FAIL",
            "fingerprintLockStatus": "PASS" if session_result and session_result.get("status") == "PASS" else "N/A" if not session_result else "FAIL",
            "ideaRecoveryCorpusUsed": False,
            "corpusInspirationIds": [],
            "layoutRepairCycles": 0,
            "axisFailuresRepaired": [],
            "safeToProceedToNextTemplate": bool(session_result and session_result.get("status") == "PASS") if session_result else None,
        },
        "repairCycles": 0,
        "repairPlan": repair_plan,
        "remainingIssues": [item["issue"] for item in repair_plan],
        "visualVerificationStatus": visual["visualVerificationStatus"],
        "visualInspectionManifests": visual["visualInspectionManifests"],
        "visualInspectionValidation": visual["visualInspectionValidation"],
        "finalStatus": final_status,
        "limitations": limitations,
        "completionStatement": "Post-build gate satisfied." if final_status in {"READY", "READY_WITH_LIMITATIONS"} else "Post-build gate failed; repair required before final delivery.",
    }
    write_receipt(output_dir, receipt)
    return receipt


def main() -> int:
    args = parse_args()
    try:
        receipt = run_post_build_audit(args)
    except Exception as exc:
        receipt = {
            "buildId": "post-build-error",
            "templateCount": args.expected_templates,
            "templates": [],
            "designSystemResults": {},
            "auditPasses": {},
            "repairCycles": 0,
            "repairPlan": [{"auditPass": "runtime", "issue": str(exc), "repair": "Fix post-build audit input and rerun."}],
            "remainingIssues": [str(exc)],
            "visualVerificationStatus": "not_verified",
            "finalStatus": "BLOCKED",
            "limitations": [],
            "completionStatement": "Post-build audit crashed.",
        }
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"{receipt['finalStatus']}: {receipt['completionStatement']}")
        for issue in receipt.get("remainingIssues", []):
            print(f"- {issue}")
    return 0 if receipt["finalStatus"] in {"READY", "READY_WITH_LIMITATIONS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
