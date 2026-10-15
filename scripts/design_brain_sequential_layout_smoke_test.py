#!/usr/bin/env python
"""Smoke tests for Brain Design sequential layout originality gate."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from contextlib import ExitStack
from test_design_brain_visual_inspect import Fixture
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from design_brain_layout_similarity_audit import audit_batch, audit_candidate_against_many
from design_brain_process_utils import python_command, resolve_python_invocation


ROOT = Path(__file__).resolve().parents[1]
INVOCATION = resolve_python_invocation()


def fp(
    template_id: str,
    hero: str,
    sections: list[str],
    grid: str,
    component: str,
    cta: str,
    source_type: str = "ai_output",
    color: str = "new accent system",
    effect: str = "new surface depth",
) -> dict[str, Any]:
    return {
        "templateId": template_id,
        "sourceType": source_type,
        "productFamily": "website-template",
        "mode": "marketplace-template",
        "heroGrammar": hero,
        "sectionOrder": sections,
        "gridSystem": grid,
        "layoutGesture": f"{grid} gesture {template_id}",
        "sectionSilhouettes": [f"{template_id} masthead", f"{template_id} proof shelf", f"{template_id} CTA island"],
        "sectionPatternMix": [
            {"sectionType": "hero", "patternId": f"{template_id}-hero-pattern"},
            {"sectionType": "features", "patternId": f"{template_id}-feature-pattern"},
            {"sectionType": "cta", "patternId": f"{template_id}-cta-pattern"},
        ],
        "sectionPatternIds": [
            f"{template_id}-hero-pattern",
            f"{template_id}-feature-pattern",
            f"{template_id}-cta-pattern",
        ],
        "sectionDensityLimits": {
            "hero": "1 primary message, 1-2 CTA, 1 proof cue",
            "features": "3-6 primary modules",
            "cta": "1 primary message, 1-2 CTA",
        },
        "catalogDivergenceNotes": f"catalog divergence for {template_id}",
        "compositionTension": f"controlled tension {template_id}",
        "focalPath": f"eye path {template_id}",
        "negativeSpaceShape": f"negative space {template_id}",
        "depthLayering": f"depth layering {template_id}",
        "moduleScaleVariation": f"module scale variation {template_id}",
        "breakoutBehavior": f"breakout behavior {template_id}",
        "layoutRhythm": f"{grid} rhythm {template_id}",
        "cardCadence": f"{component} cadence {template_id}",
        "componentPatterns": component,
        "ctaPlacement": cta,
        "closureSilhouette": f"closure silhouette {template_id}",
        "imageTreatment": f"media treatment {template_id}",
        "spacingCadence": f"spacing cadence {template_id}",
        "typographyBehavior": f"type hierarchy {template_id}",
        "colorRoles": color,
        "effectLanguage": effect,
        "navigationPattern": f"navigation {template_id}",
        "footerPattern": f"footer {template_id}",
        "designSystemId": f"ds-{template_id}",
        "visualGrammarSummary": f"visual grammar {template_id}",
        "marketplaceReadinessSummary": f"marketplace ready {template_id}",
    }


REFERENCE = fp(
    "reference-a",
    "split hero left headline right product image",
    ["hero", "logos", "features", "pricing", "faq", "cta"],
    "twelve column centered grid",
    "three card feature grid",
    "final centered CTA band",
    source_type="reference",
)

CLONE = dict(REFERENCE, templateId="clone-a", sourceType="ai_output")

RECONFIGURED = fp(
    "template-a",
    "editorial masthead with staggered proof rail and bottom booking strip",
    ["hero", "menu highlights", "chef proof", "reservation flow", "gallery", "location", "footer"],
    "asymmetric editorial grid with side rail",
    "menu tiles mixed with quote panels",
    "sticky reservation strip after proof",
    color="deep olive, ivory, and copper restaurant roles",
    effect="editorial paper depth with soft inset dividers",
)

TEMPLATE_B_SIMILAR = dict(RECONFIGURED, templateId="template-b", designSystemId="ds-template-b")

TEMPLATE_B_DISTINCT = fp(
    "template-b",
    "full bleed cinematic opener with floating menu tabs",
    ["hero", "signature dishes", "ambience story", "private events", "hours map", "booking drawer", "footer"],
    "masonry led content grid",
    "wide media cards and compact menu rows",
    "booking drawer after ambience story",
    color="warm ink and saffron role system",
    effect="film grain overlays and inset shadows",
)

TEMPLATE_C_SIMILAR_B = dict(TEMPLATE_B_DISTINCT, templateId="template-c", designSystemId="ds-template-c")

TEMPLATE_C_DISTINCT = fp(
    "template-c",
    "concierge style hero with stacked trust ledger and route planner",
    ["hero", "seasonal route", "tasting timeline", "group packages", "review ledger", "map cards", "footer"],
    "timeline and ledger hybrid grid",
    "timeline cards mixed with ledger rows",
    "split reservation and route planner module",
    color="charcoal paper and tomato accent roles",
    effect="paper depth and fine divider rules",
)

CORPUS = fp(
    "corpus-layout",
    "split hero left headline right product image",
    ["hero", "logos", "features", "pricing", "faq", "cta"],
    "twelve column centered grid",
    "three card feature grid",
    "final centered CTA band",
    source_type="corpus_inspiration",
)

CORPUS_RECONFIGURED = fp(
    "corpus-reconfigured",
    "two tier magazine opener with top utility rail",
    ["hero", "editor picks", "process", "proof wall", "interactive selector", "cta", "footer"],
    "magazine rail and feature well grid",
    "mixed editorial cards and process panels",
    "selector CTA before proof wall",
    source_type="corpus_inspiration",
    color="clay, ink, and lime editorial roles",
    effect="cut-paper panels with angled shadow depth",
)


def assert_true(name: str, condition: bool, details: str = "") -> None:
    if not condition:
        raise AssertionError(f"{name} failed. {details}")
    print(f"[PASS] {name}")


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path


def run_build_session(args: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    command = python_command(["scripts/design_brain_build_session.py"] + args, INVOCATION)
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=30)


def smoke_layout_audits() -> None:
    clone_result = audit_candidate_against_many(CLONE, [REFERENCE], "ai_vs_reference")
    assert_true("A. single template reference clone fails", clone_result["status"] in {"REVISE_REQUIRED", "BLOCKED"} and not clone_result["safeToProceed"], json.dumps(clone_result))

    reconfigured = audit_candidate_against_many(RECONFIGURED, [REFERENCE], "ai_vs_reference")
    assert_true("B. single template reconfigured layout passes", reconfigured["status"] == "PASS" and reconfigured["safeToProceed"], json.dumps(reconfigured))

    b_similar = audit_candidate_against_many(TEMPLATE_B_SIMILAR, [RECONFIGURED], "ai_vs_ai")
    assert_true("C. batch B similar to A fails", b_similar["status"] in {"REVISE_REQUIRED", "BLOCKED"} and not b_similar["safeToProceed"], json.dumps(b_similar))

    b_distinct = audit_candidate_against_many(TEMPLATE_B_DISTINCT, [RECONFIGURED], "ai_vs_ai")
    assert_true("D. batch B distinct from A passes", b_distinct["status"] == "PASS", json.dumps(b_distinct))

    c_similar = audit_candidate_against_many(TEMPLATE_C_SIMILAR_B, [RECONFIGURED, TEMPLATE_B_DISTINCT], "ai_vs_ai")
    assert_true("E1. batch C compares against A and B and fails when similar to B", c_similar["status"] in {"REVISE_REQUIRED", "BLOCKED"}, json.dumps(c_similar))

    c_distinct = audit_candidate_against_many(TEMPLATE_C_DISTINCT, [RECONFIGURED, TEMPLATE_B_DISTINCT], "ai_vs_ai")
    assert_true("E2. batch C distinct from both passes", c_distinct["status"] == "PASS", json.dumps(c_distinct))

    corpus_copy = audit_candidate_against_many(dict(CORPUS, templateId="candidate-corpus-copy"), [CORPUS], "ai_vs_reference")
    assert_true("H1. copying corpus fingerprint fails", corpus_copy["status"] in {"REVISE_REQUIRED", "BLOCKED"}, json.dumps(corpus_copy))

    corpus_reconfigured = audit_candidate_against_many(CORPUS_RECONFIGURED, [CORPUS], "ai_vs_reference")
    assert_true("H2. reconfigured corpus-inspired fingerprint passes", corpus_reconfigured["status"] == "PASS", json.dumps(corpus_reconfigured))

    hero_only_risk = fp(
        "hero-risk",
        REFERENCE["heroGrammar"],
        ["hero", "chef ledger", "tasting path", "booking", "map", "footer"],
        "split ledger and timeline grid",
        "ledger row and gallery stack",
        "route planner cta",
        color="plum, moss, and chalk roles",
        effect="paper fold depth",
    )
    hero_only_result = audit_candidate_against_many(hero_only_risk, [REFERENCE], "ai_vs_reference")
    assert_true("H3. high hero grammar similarity fails even when aggregate is lower", hero_only_result["status"] == "BLOCKED" and "heroGrammarSimilarity" in hero_only_result["hardFailAxes"], json.dumps(hero_only_result))

    stiff_layout = fp(
        "stiff-layout-risk",
        "new concierge hero with proof sidebar",
        ["hero", "selector", "trust", "packages", "faq", "footer"],
        "split ledger and timeline grid",
        "ledger row and gallery stack",
        "route planner cta",
        color="sienna, fern, and pearl roles",
        effect="paper fold depth",
    )
    stiff_layout.update(
        layoutGesture=REFERENCE["layoutGesture"],
        sectionSilhouettes=REFERENCE["sectionSilhouettes"],
        focalPath=REFERENCE["focalPath"],
        compositionTension=REFERENCE["compositionTension"],
        moduleScaleVariation=REFERENCE["moduleScaleVariation"],
    )
    stiff_result = audit_candidate_against_many(stiff_layout, [REFERENCE], "ai_vs_reference")
    assert_true(
        "H3b. repeated layout gesture and section silhouettes fail as stiffness",
        stiff_result["status"] == "BLOCKED"
        and "layoutGestureSimilarity" in stiff_result["hardFailAxes"]
        and "sectionSilhouetteSimilarity" in stiff_result["hardFailAxes"],
        json.dumps(stiff_result),
    )

    section_only_risk = fp(
        "section-risk",
        "concierge ledger opener with reservation tab rail",
        REFERENCE["sectionOrder"],
        "split ledger and timeline grid",
        "ledger row and gallery stack",
        "route planner cta",
        color="fig, linen, and brass roles",
        effect="paper fold depth",
    )
    section_only_result = audit_candidate_against_many(section_only_risk, [REFERENCE], "ai_vs_reference")
    assert_true("H4. high section order similarity fails even when aggregate is lower", section_only_result["status"] == "BLOCKED" and "sectionOrderSimilarity" in section_only_result["hardFailAxes"], json.dumps(section_only_result))

    batch = audit_batch([RECONFIGURED, TEMPLATE_B_DISTINCT, TEMPLATE_C_DISTINCT], batch_id="abc")
    assert_true("batch all-pairs distinct passes", batch["status"] == "PASS", json.dumps(batch))


def smoke_lifecycle() -> None:
    with tempfile.TemporaryDirectory(prefix="brain-design-layout-session-") as tmp, ExitStack() as visual_fixtures:
        session = Path(tmp) / "session"
        fingerprints = session / "fingerprints"
        receipts = session / "receipts"
        plans = session / "plans"
        builds = session / "builds"
        ref = write_json(fingerprints / "reference-a.json", REFERENCE)
        a = write_json(fingerprints / "template-a.json", RECONFIGURED)
        b = write_json(fingerprints / "template-b.json", TEMPLATE_B_DISTINCT)
        plan_a = write_json(plans / "plan-a.json", {"templateId": "A"})
        plan_b = write_json(plans / "plan-b.json", {"templateId": "B"})
        cognition = write_json(receipts / "cognition.json", {"status": "PASS"})
        simulation = write_json(receipts / "simulation.json", {"verdict": "PASS"})
        reference_usage_check_a = write_json(receipts / "reference-usage-check-a.json", {"status": "PASS", "referenceGroupKey": "ref-a", "referenceUsageMode": "single"})
        reference_usage_check_b = write_json(receipts / "reference-usage-check-b.json", {"status": "PASS", "referenceGroupKey": "ref-b", "referenceUsageMode": "single"})
        reference_usage_record_a = write_json(receipts / "reference-usage-record-a.json", {"status": "PASS", "referenceGroupKey": "ref-a", "referenceUsageMode": "single"})
        reference_usage_record_b = write_json(receipts / "reference-usage-record-b.json", {"status": "PASS", "referenceGroupKey": "ref-b", "referenceUsageMode": "single"})
        scaffold_disposal_a = write_json(receipts / "scaffold-disposal-a.json", {"status": "PASS", "templateId": "A", "discardedScaffold": "template A page-level scaffold"})
        design_system = write_json(
            receipts / "design-system.json",
            {
                "status": "PASS",
                "templateId": "A",
                "templateName": "Smoke Consultant Website Template",
                "productFamily": "business consultant website template",
                "mode": "website-template",
                "designSystemScope": "per-template source board",
                "productDna": {
                    "category": "business consultant website template",
                    "targetBuyer": "marketplace buyer creating advisory and consulting websites",
                    "commercialPurpose": "editable lead-generation and proof-led consultant website template",
                    "visualMood": "premium advisory with proof, process, and diagnostic modules",
                    "referenceInsight": "consultant templates need strategy, diagnostic, case proof, process, form, and trust patterns",
                    "doNotCopyBoundary": "Do not copy any exact reference layout, palette, motif, or brand name.",
                },
                "colorTokens": [
                    "background",
                    "surface",
                    "surfaceElevated",
                    "textPrimary",
                    "textSecondary",
                    "textMuted",
                    "accent",
                    "action",
                    "border",
                ],
                "typographyTokens": ["display", "h1", "h2", "h3", "body", "bodySmall", "label", "button", "nav"],
                "spacingTokens": ["scale", "sectionY", "componentPadding", "cardGap", "gridGap", "container"],
                "components": [
                    "navigation header",
                    "strategy hero button",
                    "diagnostic CTA button",
                    "proof case card",
                    "process step card",
                    "strategy service card",
                    "lead capture form",
                    "testimonial quote card",
                    "advisor profile placeholder",
                    "footer conversion block",
                ],
                "productSpecificModules": [
                    "strategy diagnostic module",
                    "case proof module",
                    "consulting process module",
                    "lead qualification form module",
                ],
                "componentAnatomy": {
                    "button": "label, icon slot, focus ring, action fill",
                    "card": "header, body, metadata, action",
                    "lead form": "field label, input, helper text, submit button, success state",
                },
                "patternModules": ["hero module", "proof card module", "cta strip module", "footer module", "case study module", "diagnostic form module"],
                "reusableSectionPatterns": [
                    "advisory hero with diagnostic CTA",
                    "strategy service matrix",
                    "case proof and metrics section",
                    "lead qualification form section",
                ],
                "usageRules": ["Use action color only for primary conversion and paired focus states."],
                "surfaceEffectTokens": {"cardShadow": "consultant proof card elevation", "focusRing": "clear advisory CTA focus ring"},
                "visualLanguageRules": {
                    "motif": "structured advisory blocks with proof-led hierarchy",
                    "imageTreatment": "profile and workshop placeholders stay editable",
                    "ctaBehavior": "diagnostic CTA stays stronger than secondary advisory links",
                },
                "placeholderRules": ["Use image placeholder labels with purpose-specific replacement clues."],
                "referenceStandardCoverage": [
                    "strategy, diagnostic, case, proof, process, and form modules are represented",
                    "source-template media slots remain editable placeholders",
                ],
                "usageExamples": [
                    "diagnostic CTA with hover and focus states",
                    "case proof card with metric row",
                    "strategy service matrix section",
                    "lead qualification form with error state",
                ],
                "packageSourceMap": {
                    "pages": ["Home", "Services", "Case Studies", "Process", "Contact"],
                    "previewDirection": "cover may crop hero, proof modules, and design-system board",
                },
                "accessibilityEditingNotes": [
                    "CTA targets stay touch-friendly",
                    "form labels and helper text remain editable",
                    "proof metrics keep readable contrast",
                ],
                "states": ["default", "hover", "focus", "active", "disabled"],
                "sourceHygiene": {
                    "autoLayout": True,
                    "editableText": True,
                    "editablePlaceholders": True,
                    "clearLayerNames": True,
                    "reusableComponents": True,
                    "responsiveConstraints": True,
                    "flattenedImportantContent": False,
                },
                "artifactEvidence": {
                    "designSystemPageId": "ds-board",
                    "figmaNodeSummaryPath": "figma-node-summary.json",
                    "sourceComponentInventoryPath": "component-inventory.json",
                    "screenshotPath": "screenshots/design-system.png",
                    "componentInventory": ["navigation header", "proof case card", "lead capture form", "process step card"],
                    "tokenSourcePath": "design-tokens.json",
                    "boardMetrics": {
                        "panelCount": 8,
                        "componentSpecimenCount": 10,
                        "productSpecificModuleCount": 4,
                        "stateExampleCount": 6,
                        "boardWidth": 1440,
                        "boardHeight": 2200,
                    },
                },
            },
        )
        build_a = write_json(builds / "a.json", {"artifact": "A"})
        build_b = write_json(builds / "b.json", {"artifact": "B"})
        # Synthetic test evidence only; separate receipts enforce artifact identity.
        fixture_a, fixture_b = Fixture(artifact=build_a), Fixture(artifact=build_b)
        visual_fixtures.callback(fixture_a.close)
        visual_fixtures.callback(fixture_b.close)
        post_build_a, post_build_b = fixture_a.write_receipt(), fixture_b.write_receipt()

        route = json.dumps({"routeSource": "brain_design_router", "module": "website-template", "mode": "marketplace-template"})
        result = run_build_session(["start", "--task", "build 2 templates", "--expected-templates", "2", "--output-dir", str(session), "--route", route])
        assert_true("session start command passes", result.returncode == 0, result.stderr + result.stdout)

        result = run_build_session(["can-start-next", "--session", str(session), "--template-id", "A"])
        assert_true("F0. first template can start", result.returncode == 0, result.stdout + result.stderr)

        result = run_build_session(["register-reference-usage-check", "--session", str(session), "--template-id", "A", "--candidate-brand-name", "Smoke A", "--reference-usage-mode", "single", "--reference-group-key", "ref-a", "--receipt", str(reference_usage_check_a)])
        assert_true("F1. lifecycle register-reference-usage-check A starts first template", result.returncode == 0, result.stderr + result.stdout)

        result = run_build_session(["can-start-next", "--session", str(session), "--template-id", "B"])
        assert_true("F2. template cannot start next before previous fingerprint locked", result.returncode != 0, result.stdout + result.stderr)

        for template_id, plan, candidate in (("A", plan_a, a),):
            commands = [
                ["register-reference", "--session", str(session), "--template-id", template_id, "--reference", str(ref), "--fingerprint", str(ref)],
                ["register-cognition", "--session", str(session), "--template-id", template_id, "--receipt", str(cognition)],
                ["register-simulation", "--session", str(session), "--template-id", template_id, "--verdict", str(simulation)],
                ["register-plan", "--session", str(session), "--template-id", template_id, "--plan", str(plan), "--fingerprint", str(candidate)],
                ["audit-layout", "--session", str(session), "--template-id", template_id],
                ["register-build", "--session", str(session), "--template-id", template_id, "--artifact", str(build_a), "--fingerprint", str(candidate)],
                ["register-design-system", "--session", str(session), "--template-id", template_id, "--receipt", str(design_system)],
                ["register-post-build", "--session", str(session), "--template-id", template_id, "--receipt", str(post_build_a)],
                ["lock-template", "--session", str(session), "--template-id", template_id],
            ]
            for command in commands:
                result = run_build_session(command)
                assert_true(f"lifecycle {command[0]} {template_id}", result.returncode == 0, result.stderr + result.stdout)

        result = run_build_session(["can-start-next", "--session", str(session), "--template-id", "B"])
        assert_true("G0. template cannot start next before scaffold disposal", result.returncode != 0 and "scaffold" in result.stdout.lower(), result.stdout + result.stderr)

        result = run_build_session(["register-scaffold-disposal", "--session", str(session), "--template-id", "A", "--receipt", str(scaffold_disposal_a)])
        assert_true("G1. lifecycle register-scaffold-disposal A", result.returncode == 0, result.stderr + result.stdout)

        result = run_build_session(["can-start-next", "--session", str(session), "--template-id", "B"])
        assert_true("G2. template can start next after previous lock and disposal", result.returncode == 0, result.stdout + result.stderr)

        commands_b = [
            ["register-reference-usage-check", "--session", str(session), "--template-id", "B", "--candidate-brand-name", "Smoke B", "--reference-usage-mode", "single", "--reference-group-key", "ref-b", "--receipt", str(reference_usage_check_b)],
            ["register-reference", "--session", str(session), "--template-id", "B", "--reference", str(ref), "--fingerprint", str(ref)],
            ["register-cognition", "--session", str(session), "--template-id", "B", "--receipt", str(cognition)],
            ["register-simulation", "--session", str(session), "--template-id", "B", "--verdict", str(simulation)],
            ["register-plan", "--session", str(session), "--template-id", "B", "--plan", str(plan_b), "--fingerprint", str(b)],
            ["audit-layout", "--session", str(session), "--template-id", "B"],
            ["register-build", "--session", str(session), "--template-id", "B", "--artifact", str(build_b), "--fingerprint", str(b)],
            ["register-design-system", "--session", str(session), "--template-id", "B", "--receipt", str(design_system)],
            ["register-post-build", "--session", str(session), "--template-id", "B", "--receipt", str(post_build_b)],
            ["lock-template", "--session", str(session), "--template-id", "B"],
        ]
        for command in commands_b:
            result = run_build_session(command)
            assert_true(f"lifecycle {command[0]} B", result.returncode == 0, result.stderr + result.stdout)

        result = run_build_session(["verify-final", "--session", str(session), "--json"])
        assert_true("I1. verify-final blocks before completion receipt exists", result.returncode != 0 and "completion receipt" in result.stdout.lower(), result.stdout + result.stderr)

        result = run_build_session(["finalize", "--session", str(session), "--json"])
        assert_true("I. completion receipt includes layout audit fields", result.returncode == 0 and "sequentialLayoutAudit" in result.stdout, result.stdout + result.stderr)

        result = run_build_session(["verify-final", "--session", str(session), "--json"])
        assert_true("I2. verify-final blocks before reference usage registry record", result.returncode != 0 and "brand/reference usage registry record" in result.stdout.lower(), result.stdout + result.stderr)

        for template_id, receipt in (("A", reference_usage_record_a), ("B", reference_usage_record_b)):
            result = run_build_session(["register-reference-usage-record", "--session", str(session), "--template-id", template_id, "--receipt", str(receipt)])
            assert_true(f"lifecycle register-reference-usage-record {template_id}", result.returncode == 0, result.stderr + result.stdout)

        result = run_build_session(["verify-final", "--session", str(session), "--json"])
        assert_true("I3. verify-final passes after lifecycle completion receipt and reference usage records", result.returncode == 0 and '"safeToDeliver": true' in result.stdout, result.stdout + result.stderr)


def main() -> int:
    try:
        smoke_layout_audits()
        smoke_lifecycle()
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1
    print("Sequential layout smoke PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
