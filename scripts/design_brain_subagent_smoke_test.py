#!/usr/bin/env python
"""Smoke tests for Brain Design subagent orchestration."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(args: list[str], expect_code: int | None = None) -> dict:
    completed = subprocess.run(
        [PYTHON, "scripts/design_brain_subagent_orchestrate.py", *args, "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=20,
    )
    if expect_code is not None and completed.returncode != expect_code:
        raise AssertionError(f"Expected code {expect_code}, got {completed.returncode}: {completed.stderr or completed.stdout}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Invalid JSON output: {completed.stdout}\n{completed.stderr}") from exc


def touch_required_outputs(evidence_dir: Path, receipt: dict) -> None:
    agents = json.loads((ROOT / ".design-brain" / "design-subagents" / "agents.json").read_text(encoding="utf-8"))["agents"]
    by_id = {agent["id"]: agent for agent in agents}
    for agent_id in receipt["activeAgents"]:
        agent_dir = evidence_dir / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)
        for output_name in by_id[agent_id]["requiredOutputs"]:
            path = agent_dir / output_name
            if output_name.endswith(".json"):
                path.write_text(json.dumps(valid_json(agent_id, output_name), indent=2) + "\n", encoding="utf-8", newline="\n")
            else:
                path.write_text(valid_text(agent_id, output_name), encoding="utf-8", newline="\n")


def valid_text(agent_id: str, output_name: str) -> str:
    return (
        f"# {agent_id} {output_name}\n\n"
        "Status: PASS.\n"
        "This receipt includes typography, layout, hierarchy, color, spacing, media imagery, effect depth, polish, "
        "copying risk, transferable Style DNA, reinterpretation plan, do-not-copy boundary, buyer value, product promise, "
        "marketplace value, section flow, rhythm, density variation, CTA placement, grid behavior, hero grammar, "
        "component rhythm, visual motif, surface treatment, originality, screenshot evidence, auto-layout, components, "
        "variants, tokens, editability, and final marketplace readiness proof.\n"
    )


def valid_json(agent_id: str, output_name: str) -> dict:
    base = {
        "status": "PASS",
        "agentId": agent_id,
        "output": output_name,
        "summary": "Meaningful semantic smoke receipt with enough structured proof for final-pass validation.",
    }
    if output_name == "design-system-depth-check.json":
        base.update(
            {
                "productDna": {
                    "category": "website template",
                    "targetBuyer": "marketplace buyer",
                    "commercialPurpose": "editable premium source template",
                    "visualMood": "distinct product-grade direction",
                    "referenceInsight": "category depth drives component system",
                    "doNotCopyBoundary": "no reference layout or brand copying",
                },
                "colorTokens": ["background", "surface", "surfaceRaised", "text", "mutedText", "accent", "border"],
                "typographyTokens": ["display", "h1", "h2", "subtitle", "body", "caption", "label"],
                "spacingTokens": ["sectionDense", "sectionAiry", "cardGap", "gridGap"],
                "components": ["button", "navbar", "card", "form", "badge", "footer", "image placeholder", "CTA block", "proof block"],
                "productSpecificModules": ["category module", "offer module", "proof module", "conversion module"],
                "states": ["default", "hover", "focus", "disabled"],
                "sectionModules": ["hero", "trust", "features", "gallery", "testimonial", "faq", "cta", "footer"],
                "usageExamples": ["hero CTA composition", "feature-card grid", "pricing or offer block", "responsive placeholder module"],
                "effectLanguage": ["shadow depth", "gradient overlay", "surface border"],
                "packageSourceMap": {"pages": ["Home", "Product", "Pricing", "Contact"], "preview": "cover and source board"},
                "boardMetrics": {
                    "panelCount": 8,
                    "componentSpecimenCount": 9,
                    "productSpecificModuleCount": 4,
                    "stateExampleCount": 4,
                    "boardWidth": 1440,
                    "boardHeight": 2200,
                },
            }
        )
    elif output_name == "figma-source-qa.json":
        base.update(
            {
                "autoLayout": True,
                "components": ["button", "card", "nav", "form", "footer", "badge"],
                "variants": ["button state", "card density", "form state"],
                "layerNaming": "PASS",
                "tokens": ["color variables", "type styles", "spacing notes"],
                "editability": "PASS",
                "screenshots": ["final-frame.png"],
            }
        )
    elif output_name == "originality-audit.json":
        base.update(
            {
                "referenceSimilarityScore": 0.05,
                "previousTemplateSimilarityScore": 0.04,
                "heroGrammar": "hero grammar is different from reference",
                "sectionFlow": "section flow is an original buyer journey",
                "layoutComparison": "layout comparison shows unique composition axes",
                "componentRhythm": "component rhythm is not reused",
                "referenceRisk": "reference and previous template risk is safe",
            }
        )
    elif output_name == "visual-qa-report.json":
        base.update(
            {
                "screenshotInspected": True,
                "screenshotEvidence": ["final-desktop.png", "design-system-board.png"],
                "heroStrength": 4.2,
                "hierarchyScore": 4.1,
                "spacingScore": 4.0,
                "densityScore": 4.0,
                "contrastScore": 4.3,
                "depthScore": 4.0,
                "polishScore": 4.2,
                "marketplaceFeelScore": 4.1,
                "issues": [],
            }
        )
    elif output_name == "marketplace-readiness-verdict.json":
        base.update(
            {
                "criticalAgentsPass": True,
                "screenshotEvidence": ["final-desktop.png"],
                "designSystemDepth": "PASS",
                "originalityStatus": "PASS",
                "buyerValue": "PASS",
                "criticalSubagents": ["PASS"],
                "blockingIssues": [],
            }
        )
    elif output_name in {"reference-usage-check.json", "brand-name-check.json", "reference-usage-record.json"}:
        base.update({"brand": "Original Smoke Brand", "reference": "reference-safe", "policy": "PASS"})
    elif output_name == "template-product-architecture.json":
        base.update(
            {
                "targetBuyer": "marketplace buyer",
                "productPromise": "premium website template",
                "marketplaceValue": "sellable and editable",
                "sections": ["hero", "trust", "problem", "services", "process", "gallery", "testimonials", "faq", "cta", "footer"],
                "conversionLogic": "clear CTA journey",
            }
        )
    elif output_name == "section-flow-fingerprint.json":
        base.update(
            {
                "sections": ["hero", "trust", "problem", "services", "process", "gallery", "testimonials", "faq", "cta", "footer"],
                "rhythm": "varied",
                "densityVariation": "dense to airy",
                "ctaPlacement": "distributed",
                "antiGenericFlow": "PASS",
                "buyerJourney": "PASS",
            }
        )
    elif output_name == "layout-fingerprint.json":
        base.update({"grid": "asymmetric", "hero": "split proof", "cardMedia": "layered", "responsive": "planned", "similarityFingerprint": "unique"})
    elif output_name == "style-dna.json":
        base.update({"styleDNA": "transferable abstract logic", "reinterpretationPlan": "original remap", "doNotCopyBoundary": "do not copy layout palette motif", "colorRoleRemapping": "new roles", "heroGrammar": "new grammar", "visualSignature": "new signature"})
    elif output_name == "visual-signature-check.json":
        base.update({"motif": "original motif", "backgroundSurface": "layered", "cta": "branded", "iconContainer": "custom", "unique": True})
    elif output_name == "reference-visual-analysis.json":
        base.update({"typography": "observed", "layout": "observed", "hierarchy": "observed", "color": "observed", "spacing": "observed", "media": "observed", "effect": "observed", "copyingRisk": "documented"})
    return base


def main() -> int:
    agents_payload = json.loads((ROOT / ".design-brain" / "design-subagents" / "agents.json").read_text(encoding="utf-8"))
    agents = agents_payload["agents"]
    ids = {agent["id"] for agent in agents}
    expected = {
        "reference_visual_analyst",
        "style_dna_extractor",
        "brand_reference_memory_guardian",
        "template_product_architect",
        "section_flow_strategist",
        "layout_composition_director",
        "design_system_director",
        "visual_signature_builder",
        "figma_source_qa",
        "originality_similarity_auditor",
        "visual_qa_inspector",
        "marketplace_readiness_judge",
    }
    if ids != expected:
        raise AssertionError(f"Subagent ids mismatch: {sorted(ids ^ expected)}")

    full_missing = run(
        [
            "--task",
            "Build a reference-led marketplace Figma website template",
            "--has-reference",
            "--figma-source",
            "--marketplace",
            "--final",
        ],
        expect_code=2,
    )
    if full_missing["mode"] != "full" or len(full_missing["activeAgents"]) != 12:
        raise AssertionError("Full mode did not activate all 12 agents.")
    if full_missing["status"] != "BLOCK":
        raise AssertionError("Final full mode without evidence must BLOCK.")

    standard = run(
        [
            "--task",
            "Create a homepage concept template",
            "--mode",
            "standard",
        ],
        expect_code=2,
    )
    if standard["mode"] != "standard" or len(standard["activeAgents"]) != 7:
        raise AssertionError("Standard mode did not activate the required 7 agents.")
    if standard["status"] != "REVISE_REQUIRED":
        raise AssertionError("Non-final standard mode without evidence should require revision.")

    with tempfile.TemporaryDirectory(prefix="brain-design-subagent-evidence-") as tmp:
        evidence = Path(tmp)
        planned = run(["--task", "Build full website template", "--mode", "full"], expect_code=2)
        touch_required_outputs(evidence, planned)
        passed = run(
            [
                "--task",
                "Build full website template",
                "--mode",
                "full",
                "--final",
                "--evidence-dir",
                str(evidence),
                "--marketplace",
                "--has-reference",
                "--figma-source",
            ],
            expect_code=0,
        )
        if passed["status"] != "PASS":
            raise AssertionError("Full final mode with all evidence should PASS.")
        if passed.get("semanticValidation", {}).get("status") != "PASS":
            raise AssertionError("Full final mode must validate semantic receipt contents.")

    print("PASS: Subagent orchestration smoke tests (4 checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
