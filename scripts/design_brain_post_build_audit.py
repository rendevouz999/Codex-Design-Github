#!/usr/bin/env python
"""Run Brain Design post-build completion validation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
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
from design_brain_repair_ticket import create_ticket, load_tickets, ticket_file, save_tickets, repair_accounting


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
    parser.add_argument("--repair-session", default="", help="Existing runtime ticket directory; default build-dir. Audit calls never count as repairs.")
    parser.add_argument("--completion-phase", choices=("prepare", "audit", "finalize"), default="audit")
    parser.add_argument("--audit-receipt", default="", help="Actual current audit receipt for final completion")
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


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                prefix=".completion-", suffix=".tmp", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(payload, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


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


def collect_audited_inputs(build_dir: Path, args: argparse.Namespace,
                           fingerprints: list[Path], designs: list[Path],
                           cognition: list[Path], session_result: dict,
                           visual: dict) -> tuple[list[dict[str, str]], list[str]]:
    """Capture exact decision inputs without retroactively refreshing stale hashes."""
    names = set([*fingerprints, *designs, *cognition])
    immutable_preparation = build_dir / 'completion-preparation.json'
    if immutable_preparation.is_file():
        names.add(immutable_preparation)
    errors = []
    for key in ("visual_artifact", "template_plan", "figma_summary", "visual_inspection"):
        value = str(getattr(args, key, "") or "").strip()
        if value: names.add(Path(value).expanduser().resolve())
    for reference in visual.get("visualInspectionManifests", []):
        if isinstance(reference, dict) and reference.get("path"):
            names.add(Path(reference["path"]).resolve())
    session_arg = str(getattr(args, "session", "") or "").strip()
    if session_arg:
        session_path = Path(session_arg).expanduser().resolve()
        names.add(session_path / "build-session-ledger.json" if session_path.is_dir() else session_path)
    ledger = session_result.get("ledger")
    def scan(value, field="", depth=0):
        if depth>12: return
        if isinstance(value, dict):
            for key, item in value.items(): scan(item, str(key), depth+1)
        elif isinstance(value, list):
            for item in value[:1000]: scan(item, field, depth+1)
        elif isinstance(value, str) and value.strip() and (field.lower().endswith("path") or field.lower().endswith("paths")):
            if "://" in value: return
            # Some design-grammar fields (for example focalPath) describe a
            # visual trajectory, not a filesystem path. Require file-like syntax.
            if not ("/" in value or "\\" in value or Path(value).suffix):
                return
            raw = Path(value)
            names.add(raw.resolve() if raw.is_absolute() else (build_dir/raw).resolve())
    if isinstance(ledger, dict): scan(ledger)
    examined=set()
    while len(examined)<2048:
        next_paths=[Path(item) for item in names if Path(item) not in examined]
        if not next_paths:break
        for item in next_paths:
            examined.add(item)
            if item.is_file() and item.suffix.lower()==".json" and item.stat().st_size<=4*1024*1024:
                try:
                    value=load_json(item)
                    scan(value)
                except (OSError,ValueError,TypeError,KeyError) as error:
                    errors.append("Audit input JSON unavailable: "+str(item)+": "+str(error))
    if len(examined)>=2048: errors.append("Audited dependency closure exceeds 2048 paths")
    refs=[]
    for item in sorted(names, key=lambda name: str(name).lower()):
        item=Path(item).resolve()
        # Legacy compatibility receipt intentionally transitions from preparation
        # to final. Its immutable preparation counterpart is the audit input.
        if item == (build_dir / 'completion-receipt.json').resolve():
            continue
        if not item.is_file():
            errors.append("Audit input missing: "+str(item))
            continue
        try:
            refs.append(file_ref(item))
        except (OSError, ValueError) as error:
            errors.append("Audit input unreadable: "+str(item)+": "+str(error))
    return refs, errors


def audit_inputs_current(audit: dict[str, Any]) -> bool:
    refs = audit.get("auditInputRefs")
    if not isinstance(refs, list) or not refs or audit.get("auditInputMissing"):
        return False
    normalized=json.dumps(refs,sort_keys=True,separators=(",",":")).encode()
    if hashlib.sha256(normalized).hexdigest()!=audit.get("auditInputRevision"):
        return False
    try:
        return all(isinstance(ref,dict) and set(ref)=={"path","sha256"} and
                   Path(ref["path"]).is_absolute() and file_ref(Path(ref["path"]))==ref
                   for ref in refs)
    except (OSError, ValueError, KeyError, TypeError):
        return False


def completion_prepared(build_dir: Path) -> bool:
    """A legacy declaration alone is not the immutable prepare-stage contract."""
    try:
        immutable = load_json(build_dir / "completion-preparation.json")
        current = load_json(build_dir / "completion-receipt.json")
        return bool(immutable.get("phase") == current.get("phase") == "preparation"
            and immutable.get("finalAllowed") is False
            and current.get("finalAllowed") is False
            and immutable.get("artifact") == current.get("artifact")
            and immutable.get("schemaVersion") == current.get("schemaVersion") == 1)
    except (OSError, ValueError, TypeError, AttributeError):
        return False


def completion_receipt_exists(build_dir: Path) -> bool:
    candidates = discover_json(build_dir, ["completion-preparation.json", "completion-receipt.json", "completion_receipt.json", "final-completion-receipt.json"])
    for path in candidates:
        try:
            payload = load_json(path)
        except Exception:
            continue
        if isinstance(payload, dict) and payload.get("finalStatus") in {"PENDING_AUDIT", "READY", "READY_WITH_LIMITATIONS", "REVISE_REQUIRED", "BLOCKED"}:
            return True
    return False


def prepare_completion(build_dir: Path, artifact: Path) -> dict[str, Any]:
    """Preparation exists before auditing; it is explicitly not completion."""
    payload = {"schemaVersion": 1, "phase": "preparation", "finalStatus": "PENDING_AUDIT", "finalAllowed": False, "artifact": file_ref(artifact), "preparedAt": datetime.now(timezone.utc).isoformat()}
    # Never mutate the audited preparation in place during finalization.
    atomic_json(build_dir / "completion-preparation.json", payload)
    # Keep the existing preparation-presence path for older callers.
    atomic_json(build_dir / "completion-receipt.json", payload)
    return payload


def finalize_completion(build_dir: Path, audit_path: Path, artifact: Path) -> dict[str, Any]:
    """Bind final completion to the latest audited bytes; no audit→final→audit cycle."""
    from design_brain_visual_gate import validate_post_build_receipt
    try:
        audit = load_json(audit_path)
    except (OSError, ValueError) as error:
        raise ValueError(f"completion audit unavailable: {error}") from error
    if not isinstance(audit, dict):
        raise ValueError("completion audit must be a JSON object")
    if audit.get("buildDir") and Path(audit["buildDir"]).resolve() != build_dir.resolve():
        raise ValueError("completion build directory differs from audited project directory")
    if audit.get("auditPhase") != "evidence" or audit.get("finalStatus") not in {"READY", "READY_WITH_LIMITATIONS"} or audit.get("remainingIssues"):
        raise ValueError("completion requires successful current audit evidence with no remaining issues")
    if not audit_inputs_current(audit):
        raise ValueError("audited inputs or dependencies changed/missing; rerun affected audit")
    preparation_path = build_dir / "completion-preparation.json"
    try:
        preparation = load_json(preparation_path)
        preparation_ref = file_ref(preparation_path)
    except (OSError, ValueError) as error:
        raise ValueError("immutable completion preparation missing; rerun prepare and audit") from error
    if (preparation.get("phase") != "preparation" or preparation.get("finalAllowed") is not False
            or preparation.get("artifact") != file_ref(artifact)
            or preparation_ref not in audit["auditInputRefs"]):
        raise ValueError("preparation is stale or absent from audited inputs; rerun audit")
    if audit.get("artifact") != file_ref(artifact):
        raise ValueError("completion artifact changed or does not match the audited revision")
    passes = audit.get("auditPasses", {})
    required_passes = {"pass0SerialProvenance", "pass1OriginalityBatchSimilarity", "pass2DesignSystemSourceHygiene", "pass3VisualLayoutQA"}
    if not isinstance(passes, dict) or not required_passes.issubset(passes) or any(status != "PASS" for status in passes.values()):
        raise ValueError("final completion requires all actual audit passes PASS")
    visual = validate_post_build_receipt(audit_path, artifact)
    if visual["status"] != "PASS":
        raise ValueError("final completion visual evidence is not current: " + "; ".join(visual["issues"]))
    payload = {"schemaVersion": 1, "phase": "final", "finalStatus": audit["finalStatus"], "finalAllowed": audit["finalStatus"] == "READY", "artifact": file_ref(artifact), "audit": file_ref(audit_path), "preparation": preparation_ref, "auditInputRefs": audit["auditInputRefs"], "auditInputRevision": audit["auditInputRevision"], "limitations": audit.get("limitations", []), "completedAt": datetime.now(timezone.utc).isoformat()}
    atomic_json(build_dir / "completion-receipt.json", payload)
    return payload


def validate_final_completion(path: Path, audit_path: Path, artifact: Path) -> bool:
    """Check the final contract without rewriting a completion receipt."""
    try:
        payload = load_json(path)
        audit = load_json(audit_path)
        prep_path = path.parent / "completion-preparation.json"
        prep = load_json(prep_path)
        prep_ref = file_ref(prep_path)
        return bool(prep.get("phase") == "preparation" and prep.get("finalAllowed") is False
            and prep.get("artifact") == file_ref(artifact)
            and prep_ref in audit.get("auditInputRefs", [])
            and payload.get("preparation") == prep_ref
            and payload.get("phase") == "final" and payload.get("finalStatus") == "READY" and payload.get("finalAllowed") is True
            and payload.get("artifact") == file_ref(artifact) and payload.get("audit") == file_ref(audit_path)
            and audit_inputs_current(audit) and payload.get("auditInputRevision") == audit.get("auditInputRevision")
            and payload.get("auditInputRefs") == audit.get("auditInputRefs")
            and audit.get("finalStatus") == "READY" and not audit.get("remainingIssues"))
    except (OSError, ValueError, TypeError, AttributeError):
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
    if args.max_repair_cycles < 1:
        raise ValueError("max repair cycles must be positive")
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
    audited_refs, dependency_errors = collect_audited_inputs(build_dir, args, fingerprint_paths, design_paths, cognition_paths, session_result, visual)
    audited_revision = hashlib.sha256(json.dumps(audited_refs, sort_keys=True, separators=(",",":")).encode()).hexdigest()
    has_completion_receipt = completion_receipt_exists(build_dir)
    completion_missing = completion_receipt_required(args) and not completion_prepared(build_dir)

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
        repair_plan.append({"auditPass": "completion", "issue": "completion preparation receipt missing", "repair": "Prepare a PENDING_AUDIT completion receipt, rerun audit, then finalize against its evidence."})
    for error in session_result.get("issues", []):
        repair_plan.append({"auditPass": "lifecycle", "issue": str(error), "repair": "Complete build-session lifecycle, rerun layout audit, and lock template fingerprint before final delivery."})
    for error in dependency_errors:
        repair_plan.append({"auditPass": "dependency", "issue": str(error), "repair": "Recollect actual input and rerun audit; never refresh hash to pass old audit."})
    for error in provenance_result.get("issues", []):
        repair_plan.append({"auditPass": "serial-provenance", "issue": str(error), "repair": "Rebuild through one completed template cycle at a time; lock and scaffold-dispose each template before starting the next."})

    critical_failure = bool(
        cognition_errors
        or design_errors
        or batch_result["status"] == "FAIL"
        or visual["status"] == "FAIL"
        # Source-only LIMITED diagnostics retain missing-input issues without
        # claiming readiness. A current visual PASS or strict audit fails closed.
        or (completion_missing and (args.strict or visual["status"] == "PASS"))
        or session_result.get("status") == "BLOCKED"
        or provenance_result.get("status") == "BLOCKED"
        or (dependency_errors and (args.strict or visual["status"] == "PASS"))
    )
    limitations: list[str] = []
    if visual["status"] == "LIMITED":
        limitations.append("No current visual inspection with explicit Main/Engineer observations was verified; source/legacy screenshot metadata cannot establish visual PASS.")
    limitations.extend(design_artifact_limitations)
    if completion_missing:
        limitations.append("Immutable preparation is absent; audit is diagnostic evidence only, never final eligibility.")
    if dependency_errors:
        limitations.append(f"{len(dependency_errors)} declared audit input(s) missing or unverifiable; resolve before finalization.")
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

    repair_session = Path(getattr(args, "repair_session", "") or build_dir).resolve()
    # Audited refs are immutable for the receipt. Appending the artifact after
    # computing auditInputRevision would invalidate the audit immediately.
    artifact = getattr(args, "visual_artifact", "")
    input_revision = audited_revision
    # Reports of the same issue/revision reuse a ticket. An audit is not a patch.
    for item in repair_plan:
        create_ticket(session_id=repair_session.name, source_gate="post_build_" + item["auditPass"], template_id=item["auditPass"], issue=item["issue"], required_repair=item["repair"], input_revision=input_revision, session=repair_session)
    statuses = {"pass1": pass1_status, "pass2": pass2_status, "pass3": pass3_status, "completion": "FAIL" if completion_missing else "PASS", "lifecycle": session_result.get("status", "PASS") if session_result else "PASS", "serial-provenance": provenance_result.get("status")}
    records = load_tickets(ticket_file(repair_session))
    for ticket in records:
        audit_pass = ticket.get("sourceGate", "").removeprefix("post_build_")
        if ticket.get("sourceGate", "").startswith("post_build_") and statuses.get(audit_pass) == "PASS":
            ticket.update(status="closed", closedAt=datetime.now(timezone.utc).isoformat(), rerunGateRequired=False, qualityStatus="source_gate_checked", checkedInputRevision=input_revision)
    if records:
        save_tickets(ticket_file(repair_session), records)
    accounting = repair_accounting(repair_session, args.max_repair_cycles)
    if accounting["budgetExhausted"]:
        limitations.append("Repair budget exhausted for unresolved issue(s); reassess the strategy or report the blocked/partial result. No automatic PASS or additional patch is authorized by this audit.")

    receipt = {
        "buildDir": str(build_dir.resolve()),
        "buildId": f"post-build-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "templateCount": args.expected_templates,
        "templates": template_ids,
        "designCognitionRequired": cognition_required,
        "completionReceiptRequired": completion_receipt_required(args),
        "completionReceiptPresent": has_completion_receipt,
        "auditPhase": "evidence",
        "auditedAt": datetime.now(timezone.utc).isoformat(),
        "completionPhase": "pending_final",
        "finalAllowed": False,
        "artifact": file_ref(Path(artifact)) if artifact and Path(artifact).is_file() else None,
        "auditInputRevision": audited_revision,
        "auditInputRefs": audited_refs,
        "auditInputMissing": dependency_errors,
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
            "layoutRepairCycles": accounting["layoutRepairCycles"],
            "axisFailuresRepaired": [],
            "safeToProceedToNextTemplate": bool(session_result and session_result.get("status") == "PASS") if session_result else None,
        },
        "repairCycles": accounting["repairCycles"],
        "repairAccounting": accounting,
        "repairPlan": repair_plan,
        "remainingIssues": [item["issue"] for item in repair_plan],
        "visualVerificationStatus": visual["visualVerificationStatus"],
        "visualInspectionManifests": visual["visualInspectionManifests"],
        "visualInspectionValidation": visual["visualInspectionValidation"],
        "finalStatus": final_status,
        "limitations": limitations,
        "completionStatement": ("All required audit evidence current; finalization still requires binding." if final_status == "READY" and not repair_plan else "Audit is limited or blocked; outstanding evidence and final binding must be resolved before delivery."),
    }
    write_receipt(output_dir, receipt)
    return receipt


def main() -> int:
    args = parse_args()
    try:
        if args.completion_phase in {"prepare", "finalize"}:
            if not args.visual_artifact:
                raise ValueError("completion preparation/finalization requires --visual-artifact")
            build_dir = Path(args.build_dir).resolve()
            artifact = Path(args.visual_artifact).resolve()
            if args.completion_phase == "prepare":
                receipt = prepare_completion(build_dir, artifact)
            else:
                receipt = finalize_completion(build_dir, Path(args.audit_receipt).resolve() if args.audit_receipt else build_dir / "post-build-audit-receipt.json", artifact)
            print(json.dumps(receipt, indent=2))
            return 0
        receipt = run_post_build_audit(args)
    except Exception as exc:
        receipt = {
            "buildId": "post-build-error",
            "templateCount": args.expected_templates,
            "templates": [],
            "designSystemResults": {},
            "auditPasses": {},
            "repairCycles": None,
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
