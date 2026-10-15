#!/usr/bin/env python
"""Smoke tests for Brain Design Cognition Contract."""

from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from design_brain_design_cognition_check import validate_cognition
from design_brain_process_utils import python_command, resolve_python_invocation, run_command as run_process_command


CHECKS = 0
PYTHON_INVOCATION = resolve_python_invocation()


def py_command(args: list[str]) -> list[str]:
    return python_command(args, PYTHON_INVOCATION)


def assert_true(condition: bool, message: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        raise AssertionError(message)


def base_receipt() -> dict[str, Any]:
    return {
        "task": "restaurant website template from premium hospitality reference",
        "productFamily": "event_venue_travel_booking",
        "mode": "website",
        "referenceSource": "hospitality reference board",
        "batchItem": "",
        "routeSource": "brain_design_router",
        "styleDNA": {
            "typographyBehavior": "editorial serif display with compact sans supporting labels",
            "layoutRhythm": "alternating immersive media bands and dense reservation proof modules",
            "spacingDensity": "generous hero breathing room with denser menu and booking areas",
            "colorBehavior": "dark warm base, controlled accent pressure, and soft surface separation",
            "imageDirection": "ingredient, dining atmosphere, and chef/process placeholders",
            "shapeLanguage": "soft rectangular surfaces with thin dividers and editorial crops",
            "effectLanguage": "subtle shadow, warm overlay, and image depth used for hierarchy",
            "premiumSignal": "specific hospitality modules, strong first impression, and source-ready components",
        },
        "referenceStandard": {
            "observedSectionCountRange": "hospitality reference standard implies 9-12 meaningful sections",
            "sectionRoleEvidence": "hero, menu, atmosphere, reservation, location, reviews, service proof, final CTA, and footer/source notes",
            "layoutShapeInventory": "editorial masthead, media band, menu rows, reservation panel, gallery, proof strip, location block, footer closure",
            "colorRoleInventory": "dark warm base, ivory text, brass action, muted dividers, elevated surface, and image overlay roles",
            "effectGradientInventory": "warm image overlays, soft card shadows, subtle depth, and no copied neon glow",
            "marketplaceCompletenessClues": "editable sections, source-ready components, placeholders, responsive preview, and design-system notes",
            "remixPlan": "reuse hospitality depth and booking proof while changing layout proportions, palette identity, and component grouping",
            "minimalistFallbackRejected": True,
        },
        "designIntentLock": {
            "productType": "editable restaurant website template",
            "outputMedium": "Figma website source template",
            "targetBuyer": "restaurant owners and template buyers",
            "useCase": "marketplace-ready hospitality website starter",
            "marketplaceValue": "complete editable website structure with reservation, menu, gallery, trust, and location flows",
            "primaryGoal": "sell a premium restaurant web template with rich section depth",
        },
        "visualGrammar": {
            "gridBehavior": "12-column desktop grid with asymmetrical media/sidebar moments",
            "spacingCadence": "large hero spacing, medium section rhythm, compact proof rows",
            "typeHierarchy": "large editorial display, section titles, menu item hierarchy, and small uppercase metadata",
            "surfaceDepth": "layered image cards, elevated reservation panel, and quiet divider surfaces",
            "colorRoles": "background, surface, text, accent, action, divider, and warm highlight roles",
            "imageTreatment": "crop-safe atmospheric placeholders with menu and dining context labels",
            "effectLogic": "warm overlay on media only, soft card depth for booking and testimonials",
            "componentRhythm": "alternating feature clusters, menu rows, gallery cards, proof, and reservation components",
        },
        "referenceBoundary": {
            "allowedToLearn": "density, hospitality proof logic, premium image-led pacing, and editorial atmosphere",
            "forbiddenToCopy": "exact layout, exact color palette, section order, hero grammar, component scaffold, image placement, and signature color identity",
            "exactLayoutCopied": "no",
            "exactPaletteCopied": "no",
            "exactSectionOrderCopied": "no",
            "heroGrammarCopied": "no",
            "componentScaffoldCopied": "no",
        },
        "colorRoleRemapping": {
            "referenceDominantColorIdentity": "blue neon futuristic energy",
            "referenceColorRoles": "dark base, electric accent, high contrast action, cool glow",
            "remappedPaletteDirection": "dark graphite, smoked olive, warm brass, and soft ivory hierarchy",
            "newAccentIdentity": "warm brass reservation/action identity",
            "preservedEmotionalRole": "premium contrast and energy are preserved without copying hue identity",
            "avoidedExactHues": "blue neon and exact electric palette avoided",
            "contrastHierarchyBehavior": "dark base supports bright type, brass action, and quiet dividers",
        },
        "visualMoodReinterpretation": {
            "referenceMood": "premium, immersive, atmospheric, and high contrast",
            "reinterpretedMood": "warm hospitality, editorial dining, tactile surfaces, and reservation confidence",
            "changedComposition": "from reference layout into alternating editorial bands and booking-led modules",
            "changedHierarchy": "menu/reservation/location proof drives hierarchy instead of copied reference emphasis",
            "changedAssetTreatment": "role-specific text clue image placeholders replace exact reference imagery",
            "changedDepthEffect": "subtle hospitality shadows and warm overlays replace cool neon glow",
        },
        "structuralReconfiguration": {
            "referenceStructurePattern": "hero, feature grid, proof, CTA",
            "newStructurePattern": "immersive hero, signature menu, dining atmosphere, reservation flow, location, reviews, service details, source notes",
            "heroGrammarChange": "image-led editorial hero with reservation proof panel instead of split SaaS hero",
            "sectionOrderChange": "menu and dining proof move before generic feature logic",
            "gridSystemChange": "asymmetrical hospitality grid replaces symmetric card grid",
            "ctaFlowChange": "reservation CTA appears in hero, menu, and closing with different context",
            "componentLayoutChange": "menu rows, booking cards, atmosphere gallery, location cards, and source notes replace generic cards",
        },
        "patternDivergence": {
            "divergenceFromReference": "new section rhythm, palette identity, hospitality components, and CTA logic",
            "divergenceFromPreviousTemplate": "new hero grammar and warm editorial visual language",
            "heroDivergence": "reservation proof panel and atmosphere crop create a new opening strategy",
            "sectionRhythmDivergence": "alternates menu, atmosphere, reservation, location, proof, and details",
            "visualLanguageDivergence": "warm brass/graphite editorial mood diverges from reference blue neon",
            "componentCadenceDivergence": "menu rows, gallery cards, and booking blocks replace repeated feature cards",
        },
        "sectionLogic": {
            "sectionList": ["immersive hero", "signature menu", "chef story", "dining atmosphere", "reservation flow", "location hours", "reviews", "service details", "footer source notes"],
            "roleOfEachSection": "each section maps to buyer proof: first impression, food offer, craft, atmosphere, booking, logistics, trust, service confidence, source usability",
            "buyerJourneyFlow": "discover atmosphere, inspect menu, trust the place, reserve, locate, and reuse source template",
            "fillerSectionsRemoved": "no filler; every section supports buyer or diner decision",
            "productFamilyDepthStandard": "9-section hospitality website template standard with reservation, menu, gallery, location, proof, and footer/source notes",
        },
        "marketplaceReadiness": {
            "sectionDepth": "9 meaningful sections with hospitality-specific modules",
            "premiumSignal": "editorial typography, atmospheric media, reservation source components, and proof depth",
            "editability": "tokens, components, placeholders, text labels, and source sections are editable",
            "sourceReadiness": "auto-layout, named layers, reusable components, and placeholder rules are planned",
            "previewValue": "cover can show hero, menu, reservation, and gallery depth",
            "commercialUsefulness": "restaurant buyer can adapt menu, hours, booking, testimonials, and location immediately",
            "nonGenericProof": "not Hero > Features > CTA; includes menu, dining, reservation, location, reviews, source notes",
        },
        "status": "PASS",
    }


def result_for(receipt: dict[str, Any]) -> dict[str, Any]:
    return validate_cognition(receipt)


def expect_pass(name: str, receipt: dict[str, Any]) -> None:
    print(f"- {name} ...", flush=True)
    result = result_for(receipt)
    assert_true(result["status"] == "PASS", f"{name} expected PASS, got {result}")


def expect_fail(name: str, receipt: dict[str, Any], risk: str) -> None:
    print(f"- {name} ...", flush=True)
    result = result_for(receipt)
    assert_true(result["status"] == "FAIL", f"{name} expected FAIL")
    assert_true(risk in result["riskCategories"], f"{name} expected risk {risk}, got {result['riskCategories']}")


def main() -> int:
    start = time.monotonic()
    print("[1/14] Complete receipt passes", flush=True)
    expect_pass("complete receipt", base_receipt())

    print("[2/14] JSON template parses", flush=True)
    template_path = Path(__file__).resolve().parents[1] / ".design-brain" / "templates" / "DESIGN_COGNITION_RECEIPT.json"
    payload = json.loads(template_path.read_text(encoding="utf-8"))
    expect_pass("machine-readable JSON template", payload)

    print("[3/14] Fake status-only receipt fails", flush=True)
    expect_fail("fake status-only receipt", {"status": "PASS"}, "missing_style_dna")

    print("[4/14] Empty section objects fail", flush=True)
    empty = {"task": "x", "productFamily": "x", "mode": "website", "status": "PASS"}
    for section in ("styleDNA", "referenceStandard", "designIntentLock", "visualGrammar", "referenceBoundary", "colorRoleRemapping", "visualMoodReinterpretation", "structuralReconfiguration", "patternDivergence", "sectionLogic", "marketplaceReadiness"):
        empty[section] = {}
    expect_fail("empty section objects", empty, "missing_color_role_remapping")

    print("[5/14] Missing Color Role Re-Mapping fails", flush=True)
    receipt = base_receipt()
    receipt.pop("colorRoleRemapping")
    expect_fail("missing color remap", receipt, "missing_color_role_remapping")

    print("[6/14] Copied color identity fails", flush=True)
    receipt = base_receipt()
    receipt["colorRoleRemapping"]["remappedPaletteDirection"] = "same palette blue neon"
    expect_fail("copied blue neon identity", receipt, "copied_color_identity")

    print("[7/14] Proper Color Role Re-Mapping passes", flush=True)
    receipt = base_receipt()
    receipt["colorRoleRemapping"]["remappedPaletteDirection"] = "acid green neon and dark graphite"
    receipt["colorRoleRemapping"]["newAccentIdentity"] = "acid green signal identity"
    expect_pass("proper remap", receipt)

    print("[8/14] Missing Reference Boundary fails", flush=True)
    receipt = base_receipt()
    receipt.pop("referenceBoundary")
    expect_fail("missing reference boundary", receipt, "missing_reference_boundary")

    print("[9/14] Generic Section Logic fails", flush=True)
    receipt = base_receipt()
    receipt["sectionLogic"]["sectionList"] = ["Hero", "Features", "Pricing", "FAQ", "CTA"]
    receipt["sectionLogic"]["roleOfEachSection"] = "generic website sections"
    expect_fail("generic section logic", receipt, "generic_section_logic")

    print("[10/14] Strong Section Logic passes", flush=True)
    expect_pass("strong section logic", base_receipt())

    print("[11/14] Missing Pattern Divergence in batch fails", flush=True)
    receipt = base_receipt()
    receipt["batchItem"] = 2
    receipt["patternDivergence"]["divergenceFromPreviousTemplate"] = ""
    expect_fail("missing batch divergence", receipt, "missing_pattern_divergence")

    print("[12/14] Marketplace Readiness vague fails", flush=True)
    receipt = base_receipt()
    receipt["marketplaceReadiness"] = {"sectionDepth": "looks premium"}
    expect_fail("vague marketplace readiness", receipt, "weak_marketplace_readiness")

    print("[13/14] Marketplace Readiness concrete passes", flush=True)
    expect_pass("concrete marketplace readiness", base_receipt())

    print("[14/14] JSON output valid and Markdown is not machine-valid", flush=True)
    with tempfile.TemporaryDirectory(prefix="brain-design-cognition-smoke-") as tmp:
        path = Path(tmp) / "receipt.json"
        path.write_text(json.dumps(base_receipt(), indent=2), encoding="utf-8")
        proc = run_process_command(
            py_command([str(Path(__file__).with_name("design_brain_design_cognition_check.py")), "--receipt", str(path), "--json"]),
            cwd=Path(__file__).resolve().parents[1],
            timeout=20,
        )
        payload = json.loads(proc.stdout)
        assert_true(proc.returncode == 0, f"JSON command failed: {proc.stderr}")
        assert_true(payload["status"] == "PASS", "JSON payload should pass")
        md_template = Path(__file__).resolve().parents[1] / ".design-brain" / "templates" / "DESIGN_COGNITION_RECEIPT.md"
        proc = run_process_command(
            py_command([str(Path(__file__).with_name("design_brain_design_cognition_check.py")), "--receipt", str(md_template), "--json"]),
            cwd=Path(__file__).resolve().parents[1],
            timeout=20,
        )
        payload = json.loads(proc.stdout)
        assert_true(proc.returncode != 0, "Markdown template should not be treated as machine-valid JSON receipt.")
        assert_true(payload["status"] == "FAIL", "Markdown template should fail machine validation.")

    print(f"PASS: Design cognition smoke tests ({CHECKS} checks) in {time.monotonic() - start:.2f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
