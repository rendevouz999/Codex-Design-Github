#!/usr/bin/env python
"""Smoke tests for Brain Design post-build completion gate."""

from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any
from PIL import Image

sys.dont_write_bytecode = True

from design_brain_batch_similarity_audit import audit_fingerprints
from design_brain_design_cognition_smoke_test import base_receipt
from design_brain_design_system_check import validate_design_system
from design_brain_post_build_audit import run_post_build_audit, prepare_completion
from design_brain_process_utils import python_command, resolve_python_invocation, run_command as run_process_command
from test_design_brain_visual_inspect import Fixture


CHECKS = 0
PYTHON_INVOCATION = resolve_python_invocation()


def py_command(args: list[str]) -> list[str]:
    return python_command(args, PYTHON_INVOCATION)


def assert_true(condition: bool, message: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        raise AssertionError(message)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def fingerprint(template_id: str, hero: str, sections: list[str], visual: str) -> dict[str, Any]:
    return {
        "templateId": template_id,
        "sourceType": "ai_output",
        "productFamily": "website-template",
        "mode": "marketplace-template",
        "heroGrammar": hero,
        "sectionOrder": sections,
        "gridSystem": f"{hero} grid",
        "layoutGesture": f"{visual} layout gesture",
        "sectionSilhouettes": [f"{visual} hero silhouette", f"{visual} proof silhouette", f"{visual} CTA silhouette"],
        "sectionPatternMix": [
            {"sectionType": section, "patternId": f"{visual}-{section}"}
            for section in sections
        ],
        "sectionPatternIds": [f"{visual}-{section}" for section in sections],
        "sectionDensityLimits": {section: "1 primary message, 1-3 supporting modules" for section in sections},
        "catalogDivergenceNotes": f"Fixture uses {visual} composition decisions and the declared section roles.",
        "compositionTension": f"{visual} composition tension",
        "focalPath": f"{visual} focal path",
        "negativeSpaceShape": f"{visual} negative space",
        "depthLayering": f"{visual} depth layering",
        "moduleScaleVariation": f"{visual} module scale",
        "breakoutBehavior": f"{visual} breakout",
        "layoutRhythm": f"{visual} layout rhythm",
        "componentPatterns": f"{visual} components",
        "ctaPlacement": f"{hero} cta",
        "closureSilhouette": f"{visual} closure silhouette",
        "spacingCadence": f"{visual} spacing",
        "colorRoles": f"{visual} color",
        "navigationPattern": f"{visual} nav",
        "footerPattern": f"{visual} footer",
        "designSystemId": f"ds-{template_id}",
        "visualGrammarSummary": visual,
        "marketplaceReadinessSummary": f"{visual} marketplace ready",
        "gridRhythm": f"{hero} grid",
        "cardCadence": f"{visual} cards",
        "ctaPattern": f"{hero} cta",
        "imageTreatment": f"{visual} media",
        "typographyBehavior": f"{visual} type",
        "colorRoleBehavior": f"{visual} color",
        "effectLanguage": f"{visual} depth",
        "componentPattern": f"{visual} components",
        "visualLanguage": visual,
    }


def design_system(template_id: str = "template-1", auto_layout: bool = True, artifact_evidence: bool = True) -> dict[str, Any]:
    payload = {
        "templateId": template_id,
        "templateName": "Smoke Template",
        "productFamily": "restaurant_hospitality",
        "mode": "website",
        "designSystemScope": "per-template",
        "productDna": {
            "category": "restaurant hospitality website template",
            "targetBuyer": "marketplace buyer building a restaurant site",
            "commercialPurpose": "editable booking and menu website template",
            "visualMood": "warm editorial hospitality",
            "referenceInsight": "restaurant buyers need menu, reservation, gallery, location, and trust modules",
            "doNotCopyBoundary": "Do not copy any specific restaurant reference layout or brand system.",
        },
        "colorTokens": {
            "background": "#ffffff",
            "surface": "#f7f3ee",
            "surfaceElevated": "#ffffff",
            "textPrimary": "#161616",
            "textSecondary": "#525252",
            "textMuted": "#777777",
            "accent": "#b87a3a",
            "action": "#8d3f24",
            "border": "#ded6cc",
        },
        "typographyTokens": {
            "display": "Display",
            "h1": "H1",
            "h2": "H2",
            "h3": "H3",
            "body": "Body",
            "bodySmall": "Body small",
            "label": "Label",
            "button": "Button",
            "nav": "Navigation",
        },
        "spacingTokens": {
            "scale": [4, 8, 12, 16, 24, 32, 48, 64],
            "sectionY": 96,
            "componentPadding": 24,
            "cardGap": 24,
            "gridGap": 32,
            "container": 1200,
        },
        "layoutGrid": {"columns": 12, "container": 1200},
        "radiusElevation": {"card": 16, "button": 999, "shadow": "soft"},
        "components": [
            "button primary",
            "button secondary",
            "card",
            "navigation header",
            "footer",
            "cta reservation",
            "image placeholder",
            "form input",
            "testimonial proof",
            "menu item",
            "reservation panel",
            "gallery media",
            "location hours",
        ],
        "productSpecificModules": [
            "menu category module",
            "reservation booking module",
            "gallery atmosphere module",
            "location and hours module",
        ],
        "componentAnatomy": {
            "button": "label, icon slot, fill, border, focus ring",
            "card": "header, body, media/placeholder slot, action",
            "reservation panel": "fields, helper text, submit action, state area",
        },
        "states": ["default", "hover", "focus", "active", "disabled", "error", "loading", "empty"],
        "patternModules": [
            "hero",
            "menu proof",
            "reservation flow",
            "gallery",
            "location",
            "faq",
            "footer",
        ],
        "reusableSectionPatterns": [
            "hero with reservation CTA",
            "menu preview grid",
            "gallery and chef proof section",
            "location and hours footer block",
        ],
        "usageRules": [
            "Use reservation panel only where booking intent is primary.",
            "Use gallery modules for atmosphere proof, not decoration.",
        ],
        "surfaceEffectTokens": {
            "cardShadow": "soft separation",
            "imageOverlay": "readability and atmosphere",
        },
        "visualLanguageRules": {
            "motif": "warm hospitality surfaces with menu-card depth",
            "imageTreatment": "editorial food and interior placeholders",
            "ctaBehavior": "reservation actions stay prominent but calm",
        },
        "placeholderRules": [
            "image placeholder: restaurant interior or signature dish",
            "profile photo placeholder: chef portrait",
        ],
        "referenceStandardCoverage": [
            "menu, reservation, gallery, location, proof, and CTA modules are represented in the design system",
            "source-template media slots remain editable text placeholders",
        ],
        "usageExamples": [
            "reservation CTA with form states",
            "menu card grid with category filters",
            "gallery proof block with image placeholders",
            "location-hours footer module",
        ],
        "packageSourceMap": {
            "pages": ["Home", "Menu", "Reservation", "Gallery", "Location", "Contact"],
            "previewDirection": "cover can crop hero, menu, and design-system board",
        },
        "accessibilityEditingNotes": [
            "buttons keep touch-friendly height",
            "restaurant copy and placeholders remain editable",
            "contrast targets readable menu and reservation content",
        ],
        "sourceHygiene": {
            "autoLayout": auto_layout,
            "editableText": True,
            "editablePlaceholders": True,
            "clearLayerNames": True,
            "reusableComponents": True,
            "responsiveConstraints": True,
            "flattenedImportantContent": False,
        },
        "status": "PASS",
        "evidence": ["smoke fixture"],
    }
    if artifact_evidence:
        payload["artifactEvidence"] = {
            "figmaNodeSummaryPath": "figma-node-summary.json",
            "sourceComponentInventoryPath": "component-inventory.json",
            "screenshotPath": "screenshots/template-1.png",
            "componentInventory": ["button", "card", "navigation", "menu item"],
            "tokenSourcePath": "design-tokens.json",
            "boardMetrics": {
                "panelCount": 8,
                "componentSpecimenCount": 10,
                "productSpecificModuleCount": 4,
                "stateExampleCount": 6,
                "boardWidth": 1440,
                "boardHeight": 2200,
            },
        }
    return payload


def write_completion_receipt(build_dir: Path, final_status: str = "READY_WITH_LIMITATIONS") -> None:
    write_json(
        build_dir / "completion-receipt.json",
        {
            "templatesBuilt": 1,
            "designSystemsBuilt": "1/1",
            "auditPass1": "PASS",
            "auditPass2": "PASS",
            "auditPass3": "PASS",
            "repairCycles": 0,
            "remainingIssues": [],
            "visualVerification": "source heuristic only",
            "finalStatus": final_status,
        },
    )


class Args:
    def __init__(
        self,
        build_dir: Path,
        expected_templates: int = 1,
        batch: bool = False,
        strict: bool = False,
        allow_visual_limitation: bool = True,
        require_cognition: bool = False,
        cognition_receipt: str = "",
        session: str = "",
    ) -> None:
        self.build_dir = str(build_dir)
        self.session = session
        self.expected_templates = expected_templates
        self.batch = batch
        self.template_plan = ""
        self.design_system = ""
        self.cognition_receipt = cognition_receipt
        self.require_cognition = require_cognition
        self.allow_missing_cognition = False
        self.figma_summary = ""
        self.screenshot_dir = ""
        self.output_dir = ""
        self.max_repair_cycles = 3
        self.strict = strict
        self.require_completion_receipt = strict
        self.no_require_completion_receipt = False
        self.diagnostic_only = False
        self.allow_visual_limitation = allow_visual_limitation
        self.mode = "website"
        self.product_family = "restaurant_hospitality"
        self.json = True


def test_missing_design_system_fails(tmp: Path) -> None:
    print("[1/9] Missing design system fails ...", flush=True)
    write_json(tmp / "template-fingerprints" / "one.json", fingerprint("template-1", "immersive hero", ["hero", "menu", "reservation"], "warm editorial"))
    receipt = run_post_build_audit(Args(tmp))
    assert_true(receipt["finalStatus"] == "BLOCKED", "missing design system must block")
    assert_true(any("design system" in issue.lower() for issue in receipt["remainingIssues"]), "missing design system issue must be recorded")
    print("[1/9] PASS", flush=True)


def test_complete_design_system_passes(tmp: Path) -> None:
    print("[2/9] Complete design system passes ...", flush=True)
    write_json(tmp / "template-fingerprints" / "one.json", fingerprint("template-1", "immersive hero", ["hero", "menu", "reservation", "location"], "warm editorial"))
    write_json(tmp / "design-system-receipts" / "one.json", design_system())
    write_completion_receipt(tmp)
    receipt = run_post_build_audit(Args(tmp))
    assert_true(receipt["finalStatus"] == "READY_WITH_LIMITATIONS", "complete source audit should pass with visual limitation")
    assert_true(receipt["auditPasses"]["pass2DesignSystemSourceHygiene"] == "PASS", "design system pass expected")
    print("[2/9] PASS", flush=True)


def test_batch_similarity(tmp: Path) -> None:
    print("[3/9] Batch similarity catches reused scaffold ...", flush=True)
    same = [
        fingerprint("t1", "split hero", ["hero", "features", "pricing", "faq", "cta"], "blue glass"),
        fingerprint("t2", "split hero", ["hero", "features", "pricing", "faq", "cta"], "blue glass"),
        fingerprint("t3", "split hero", ["hero", "features", "pricing", "faq", "cta"], "blue glass"),
    ]
    result = audit_fingerprints(same, "similar-batch")
    assert_true(result["status"] == "FAIL", "similar batch must fail")
    assert_true(len(result["pairs"]) == 3, "three templates require three pair comparisons")
    print("[3/9] PASS", flush=True)

    print("[4/9] Batch distinct templates pass ...", flush=True)
    distinct = [
        fingerprint("t1", "immersive image hero", ["hero", "menu", "story", "reservation", "location"], "warm editorial"),
        fingerprint("t2", "asymmetric proof hero", ["hero", "stats", "services", "gallery", "booking"], "dark premium"),
        fingerprint("t3", "product-led cover hero", ["hero", "collections", "craft", "reviews", "footer"], "airy boutique"),
    ]
    result = audit_fingerprints(distinct, "distinct-batch")
    assert_true(result["status"] == "PASS", "distinct batch should pass")
    assert_true(len(result["pairs"]) == 3, "distinct batch still needs all pair comparisons")
    print("[4/9] PASS", flush=True)


def test_source_hygiene_and_visual_failures(tmp: Path) -> None:
    print("[5/9] Missing auto-layout/source hygiene fails ...", flush=True)
    result = validate_design_system(design_system(auto_layout=False))
    assert_true(result["status"] == "FAIL", "missing auto-layout must fail")
    assert_true(any("auto-layout" in error for error in result["errors"]), "auto-layout error must be explicit")

    compact = design_system()
    compact["components"] = ["button", "card", "navigation", "footer", "placeholder"]
    compact["productSpecificModules"] = ["menu module"]
    compact["reusableSectionPatterns"] = ["hero"]
    compact["usageExamples"] = ["button row"]
    compact["artifactEvidence"]["boardMetrics"] = {
        "panelCount": 4,
        "componentSpecimenCount": 5,
        "productSpecificModuleCount": 1,
        "stateExampleCount": 2,
        "boardWidth": 900,
        "boardHeight": 1000,
    }
    compact_result = validate_design_system(compact)
    assert_true(compact_result["status"] == "FAIL", "compact color/type/button/card design system must fail")
    assert_true(any("too thin" in error or "compact style summary" in error for error in compact_result["errors"]), "compact board failure must be explicit")

    receipt_only = validate_design_system(design_system(artifact_evidence=False))
    assert_true(receipt_only["status"] == "FAIL", "receipt-only design system must fail product-grade validation")
    assert_true(receipt_only["artifactEvidenceStatus"] == "MISSING", "receipt-only design system must record missing artifact evidence")

    receipt_only_dir = tmp / "receipt-only"
    write_json(receipt_only_dir / "template-fingerprints" / "one.json", fingerprint("template-1", "immersive hero", ["hero", "menu", "reservation"], "warm editorial"))
    write_json(receipt_only_dir / "design-system-receipts" / "one.json", design_system(artifact_evidence=False))
    write_completion_receipt(receipt_only_dir)
    receipt_only_audit = run_post_build_audit(Args(receipt_only_dir))
    assert_true(receipt_only_audit["finalStatus"] == "BLOCKED", "receipt-only artifact evidence must block marketplace website templates")
    assert_true(receipt_only_audit["auditPasses"]["pass2DesignSystemSourceHygiene"] == "FAIL", "receipt-only artifact evidence must fail pass 2")
    print("[5/9] PASS", flush=True)

    print("[6/9] Text overlap/clipping visual issue fails ...", flush=True)
    write_json(tmp / "template-fingerprints" / "one.json", fingerprint("template-1", "immersive hero", ["hero", "menu", "reservation"], "warm editorial"))
    write_json(tmp / "design-system-receipts" / "one.json", design_system())
    write_completion_receipt(tmp)
    write_json(tmp / "visual-qa.json", {"issues": [{"type": "text overlap", "severity": "critical"}, {"type": "clipping", "severity": "high"}]})
    receipt = run_post_build_audit(Args(tmp))
    assert_true(receipt["finalStatus"] == "BLOCKED", "visual overlap/clipping must block")
    assert_true(receipt["auditPasses"]["pass3VisualLayoutQA"] == "FAIL", "visual pass must fail")
    print("[6/9] PASS", flush=True)


def test_repair_loop_and_completion_receipt(tmp: Path) -> None:
    print("[7/9] Repair loop behavior ...", flush=True)
    write_json(tmp / "template-fingerprints" / "one.json", fingerprint("template-1", "immersive hero", ["hero", "menu", "reservation"], "warm editorial"))
    write_json(tmp / "design-system-receipts" / "one.json", design_system(auto_layout=False))
    write_completion_receipt(tmp)
    failed = run_post_build_audit(Args(tmp))
    assert_true(failed["finalStatus"] == "BLOCKED", "first failed fixture should block")
    write_json(tmp / "design-system-receipts" / "one.json", design_system(auto_layout=True))
    repaired = run_post_build_audit(Args(tmp))
    assert_true(repaired["finalStatus"] == "READY_WITH_LIMITATIONS", "repaired fixture should pass with limitation")
    print("[7/9] PASS", flush=True)

    print("[8/9] Completion receipt required in strict mode ...", flush=True)
    # Existing website fixture references these concrete local dependencies.
    # This builds test-only files; no native rendering or visual PASS is claimed.
    for name in ("component-inventory.json", "design-tokens.json", "figma-node-summary.json"):
        write_json(tmp / name, {"testOnly": True, "purpose": "source input closure"})
    (tmp / "screenshots").mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (4, 4), "white").save(tmp / "screenshots" / "template-1.png")
    artifact = tmp / "synthetic-browser-deck.html"
    artifact.write_text("<!doctype html><title>synthetic source audit only</title>", encoding="utf-8")
    prepare_completion(tmp, artifact)
    strict_missing = run_post_build_audit(Args(tmp, strict=True))
    assert_true(strict_missing["finalStatus"] == "READY_WITH_LIMITATIONS", "completion receipt already present should pass strict mode with visual limitation")
    (tmp / "completion-receipt.json").unlink()
    strict_missing = run_post_build_audit(Args(tmp, strict=True))
    assert_true(strict_missing["finalStatus"] == "BLOCKED", "missing completion receipt must fail in strict mode")
    prepare_completion(tmp, artifact)
    strict_ok = run_post_build_audit(Args(tmp, strict=True))
    assert_true(strict_ok["finalStatus"] == "READY_WITH_LIMITATIONS", "valid completion receipt should pass strict mode")
    print("[8/9] PASS", flush=True)


def test_json_output(tmp: Path) -> None:
    print("[9/10] JSON output parseable ...", flush=True)
    write_json(tmp / "template-fingerprints" / "one.json", fingerprint("template-1", "immersive hero", ["hero", "menu", "reservation"], "warm editorial"))
    write_json(tmp / "design-system-receipts" / "one.json", design_system())
    write_completion_receipt(tmp)
    script_dir = Path(__file__).resolve().parent
    support_dir = next(p / "scripts" for p in script_dir.parents if (p / "scripts/design_brain_batch_similarity_audit.py").is_file())
    bootstrap = f"import sys,runpy; sys.path[:0]=[{str(script_dir)!r},{str(support_dir)!r}]; script=sys.argv.pop(1); runpy.run_path(script,run_name='__main__')"
    cmd = py_command(
        [
            "-c",
            bootstrap,
            str(Path(__file__).with_name("design_brain_post_build_audit.py")),
            "--build-dir",
            str(tmp),
            "--expected-templates",
            "1",
            "--allow-visual-limitation",
            "--json",
        ]
    )
    proc = run_process_command(cmd, cwd=Path(__file__).resolve().parents[1], timeout=20)
    assert_true(proc.returncode == 0, f"post-build audit JSON command failed: {proc.stderr}")
    payload = json.loads(proc.stdout)
    assert_true(payload["finalStatus"] == "READY_WITH_LIMITATIONS", "JSON payload should contain final status")
    print("[9/10] PASS", flush=True)


def test_require_cognition(tmp: Path) -> None:
    print("[10/10] Required cognition blocks missing/fake receipt ...", flush=True)
    write_json(tmp / "template-fingerprints" / "one.json", fingerprint("template-1", "immersive hero", ["hero", "menu", "reservation"], "warm editorial"))
    write_json(tmp / "design-system-receipts" / "one.json", design_system())
    write_completion_receipt(tmp)

    missing = run_post_build_audit(Args(tmp, require_cognition=True))
    assert_true(missing["finalStatus"] == "BLOCKED", "require-cognition should block missing receipt")
    assert_true(any("Design Cognition Receipt is required" in issue for issue in missing["remainingIssues"]), "missing cognition issue should be explicit")

    fake_path = tmp / "design-cognition-receipt.json"
    write_json(fake_path, {"status": "PASS"})
    fake = run_post_build_audit(Args(tmp, require_cognition=True, cognition_receipt=str(fake_path)))
    assert_true(fake["finalStatus"] == "BLOCKED", "fake cognition receipt should block")
    assert_true(fake["designCognitionResults"], "fake cognition validation result should be recorded")

    write_json(fake_path, base_receipt())
    valid = run_post_build_audit(Args(tmp, require_cognition=True, cognition_receipt=str(fake_path)))
    assert_true(valid["finalStatus"] == "READY_WITH_LIMITATIONS", "valid cognition receipt should allow post-build pass")
    print("[10/10] PASS", flush=True)


def test_session_lifecycle_required(tmp: Path) -> None:
    print("[11/11] Build-session lifecycle blocks missing lock ...", flush=True)
    write_json(tmp / "template-fingerprints" / "one.json", fingerprint("template-1", "immersive hero", ["hero", "menu", "reservation"], "warm editorial"))
    write_json(tmp / "design-system-receipts" / "one.json", design_system())
    write_completion_receipt(tmp)
    session = tmp / "session"
    write_json(
        session / "build-session-ledger.json",
        {
            "sessionId": "smoke-session",
            "expectedTemplateCount": 1,
            "templates": [
                {
                    "templateId": "template-1",
                    "referenceLayoutAuditPath": "layout-audits/template-1-reference.json",
                    "pairwiseAudits": [],
                    "fingerprintPath": "",
                    "designSystemReceiptPath": "design-system-receipts/one.json",
                    "postBuildAuditPath": "post-build-audit-receipt.json",
                    "status": "layout_audit_passed",
                }
            ],
        },
    )
    blocked = run_post_build_audit(Args(tmp, session=str(session)))
    assert_true(blocked["finalStatus"] == "BLOCKED", "session with missing fingerprint lock must block")
    assert_true(blocked["layoutOriginality"]["fingerprintLockStatus"] == "FAIL", "fingerprint lock status must be recorded")
    print("[11/11] PASS", flush=True)


def test_reference_usage_record_required_after_completion(tmp: Path) -> None:
    print("[12/12] Reference usage record required after completion ...", flush=True)
    write_json(tmp / "template-fingerprints" / "one.json", fingerprint("template-1", "immersive hero", ["hero", "proof", "catalog", "cta"], "reference-led editorial"))
    write_json(tmp / "design-system-receipts" / "one.json", design_system())
    write_completion_receipt(tmp)
    session = tmp / "session"
    write_json(session / "receipts" / "reference-check.json", {"command": "check", "status": "PASS"})
    ledger = {
        "sessionId": "reference-usage-session",
        "task": "reference-led website template",
        "route": {"workflow": "reference-led-template"},
        "expectedTemplateCount": 1,
        "completionReceipt": {"templatesBuilt": 1, "fingerprintLocks": 1, "sequentialLayoutAudit": "PASS"},
        "templates": [
            {
                "templateId": "template-1",
                "candidateBrandName": "Sourceproof",
                "referenceUsageMode": "single",
                "referenceGroupKey": "ref-a",
                "brandReferenceUsageCheckPath": "receipts/reference-check.json",
                "brandReferenceUsageRecordPath": "",
                "cognitionReceiptPath": "receipts/cognition.json",
                "simulationVerdictPath": "receipts/simulation.json",
                "referenceLayoutAuditPath": "receipts/reference-layout.json",
                "fingerprintPath": "fingerprints/template-1.json",
                "buildArtifactPath": "artifacts/template-1.json",
                "designSystemReceiptPath": "receipts/design-system.json",
                "postBuildAuditPath": "receipts/post-build.json",
                "pairwiseAudits": [],
                "status": "fingerprint_locked",
                "stages": ["brand_reference_usage_checked", "completion_receipt_created", "fingerprint_locked"],
            }
        ],
    }
    write_json(session / "build-session-ledger.json", ledger)

    # Keep visual proof meaningful while testing the independent reference-registry gate.
    # These are explicitly synthetic attestations, never actual product acceptance.
    artifact = session / "artifacts/template-1.json"
    write_json(artifact, {"fixture": "synthetic reference-usage regression source"})
    visual_fixture = Fixture(artifact=artifact)
    visual_receipt = visual_fixture.write_receipt()
    write_json(session / "receipts/post-build.json", json.loads(visual_receipt.read_text()))

    blocked = run_post_build_audit(Args(tmp, session=str(session)))
    assert_true(blocked["finalStatus"] == "BLOCKED", "missing reference usage record must block after completion receipt")
    assert_true(any("brand/reference usage registry record" in issue for issue in blocked["remainingIssues"]), "missing registry record issue must be explicit")

    write_json(session / "receipts" / "reference-record.json", {"command": "record", "status": "PASS"})
    ledger["templates"][0]["brandReferenceUsageRecordPath"] = "receipts/reference-record.json"
    ledger["templates"][0]["stages"].append("brand_reference_usage_recorded")
    write_json(session / "build-session-ledger.json", ledger)
    passed = run_post_build_audit(Args(tmp, session=str(session)))
    assert_true(passed["finalStatus"] == "READY_WITH_LIMITATIONS", "PASS record receipt should unblock post-build final audit")
    visual_fixture.close()
    print("[12/12] PASS", flush=True)


def main() -> int:
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="brain-design-post-build-smoke-") as tmp_root:
        root = Path(tmp_root)
        test_missing_design_system_fails(root / "missing-ds")
        test_complete_design_system_passes(root / "complete-ds")
        test_batch_similarity(root / "batch")
        test_source_hygiene_and_visual_failures(root / "visual")
        test_repair_loop_and_completion_receipt(root / "repair")
        test_json_output(root / "json")
        test_require_cognition(root / "cognition")
        test_session_lifecycle_required(root / "session")
        test_reference_usage_record_required_after_completion(root / "reference-usage")
    print(f"PASS: Post-build smoke tests ({CHECKS} checks) in {time.monotonic() - start:.2f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
