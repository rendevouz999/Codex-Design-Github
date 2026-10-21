"""Validate current visual evidence at runtime/lifecycle receipt boundaries.

This checks the recorded evidence, not whether a model truly perceived pixels.
"""
from pathlib import Path
import hashlib
import json


def validate_post_build_receipt(path, expected_artifact=None):
    from design_brain_visual_inspect import verify_manifest, file_ref

    receipt_path = Path(path).resolve()
    issues = []
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
        if not isinstance(receipt, dict):
            raise ValueError("post-build receipt must be an object")
        passes = receipt.get("auditPasses", {})
        required = ("pass0SerialProvenance", "pass1OriginalityBatchSimilarity",
                    "pass2DesignSystemSourceHygiene", "pass3VisualLayoutQA")
        if not isinstance(passes, dict) or any(passes.get(name) != "PASS" for name in required):
            issues.append("all four actual post-build audit passes must be PASS")
        if receipt.get("auditPhase") != "evidence" or receipt.get("completionPhase") != "pending_final":
            issues.append("post-build evidence phase is absent or obsolete")
        if receipt.get("finalAllowed") is not False:
            issues.append("audit evidence must not self-authorize final delivery")
        if receipt.get("finalStatus") != "READY" or receipt.get("remainingIssues"):
            issues.append("post-build evidence is limited, blocked, or has unresolved issues")
        from design_brain_post_build_audit import audit_inputs_current
        if not audit_inputs_current(receipt):
            issues.append("audited input dependencies are missing, stale, or unverifiable")
        build_root = receipt.get("buildDir")
        if not isinstance(build_root, str) or not Path(build_root).is_absolute():
            issues.append("audited build directory must be explicit and absolute")
        else:
            preparation = Path(build_root).resolve() / "completion-preparation.json"
            refs = receipt.get("auditInputRefs")
            matches = ([item for item in refs if isinstance(item, dict)
                        and item.get("path") == str(preparation)]
                       if isinstance(refs, list) else [])
            if len(matches) != 1 or matches[0] != file_ref(preparation):
                issues.append("current immutable preparation is not bound to the audit")
            else:
                prepared = json.loads(preparation.read_text(encoding="utf-8"))
                if (prepared.get("phase") != "preparation" or prepared.get("finalAllowed") is not False
                        or prepared.get("artifact") != receipt.get("artifact")):
                    issues.append("immutable preparation artifact/phase no longer agrees with the audit")
        manifests = receipt.get("visualInspectionManifests")
        if not isinstance(manifests, list) or not manifests:
            raise ValueError("current visual inspection manifests missing")
        seen = set()
        for ref in manifests:
            manifest_path = Path(ref["path"])
            if not manifest_path.is_absolute():
                raise ValueError("inspection manifest path must be absolute")
            manifest_path = manifest_path.resolve()
            if manifest_path in seen:
                raise ValueError("duplicate inspection manifest")
            seen.add(manifest_path)
            digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
            if digest != ref.get("sha256"):
                raise ValueError("inspection manifest changed after post-build audit")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            actual = Path(manifest["artifact"]["path"]).resolve()
            result = verify_manifest(manifest_path, stage="final", expected_artifact=actual)
            if result.get("evidence_status") != "VERIFIED" or result.get("review_status") != "MAIN_ACCEPTED":
                issues.append(f"current inspection is not accepted: {manifest_path}")
                issues.extend(str(item) for item in result.get("issues", []))
            if expected_artifact:
                expected = Path(expected_artifact).resolve()
                if not expected.is_file():
                    issues.append("expected build artifact must be an explicit current file, not a directory scope")
                if actual != expected:
                    issues.append("visual evidence belongs to a different build artifact")
                if expected.is_file() and receipt.get("artifact") != file_ref(expected):
                    issues.append("audited artifact path/hash differs from the expected current artifact")
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        issues.append(str(error))
    return {"status": "BLOCKED" if issues else "PASS", "issues": issues,
            "receiptPath": str(receipt_path), "scope": "current recorded visual evidence; not proof of perception"}
