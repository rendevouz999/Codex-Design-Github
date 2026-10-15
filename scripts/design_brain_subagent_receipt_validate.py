#!/usr/bin/env python
"""Validate semantic quality of Brain Design subagent evidence receipts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

AGENTS_REL = ".design-brain/design-subagents/agents.json"
RULES_REL = ".design-brain/design-subagents/semantic-validation-rules.json"
SCHEMA_ID = "design-brain.design-subagents.semantic-validation.v1"
STATUS_VALUES = {"PASS", "REVISE_REQUIRED", "BLOCK", "BLOCKED", "FAIL"}
EMPTY_EVIDENCE_MARKERS = {
    "smoke evidence",
    "todo",
    "tbd",
    "placeholder",
    "lorem ipsum",
    "dummy evidence",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Brain Design subagent evidence semantics.")
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--receipt", default="", help="Optional orchestration receipt JSON; active agents are read from it.")
    parser.add_argument("--mode", choices=("full", "standard", "lightweight"), default="full")
    parser.add_argument("--active-agents", default="", help="Comma-separated active agent ids when no receipt is supplied.")
    parser.add_argument("--task", default="")
    parser.add_argument("--template-type", default="")
    parser.add_argument("--niche", default="")
    parser.add_argument("--target-buyer", default="")
    parser.add_argument("--final", action="store_true")
    parser.add_argument("--has-reference", action="store_true")
    parser.add_argument("--figma-source", action="store_true")
    parser.add_argument("--marketplace", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_agents(root: Path) -> dict[str, Any]:
    return load_json(root / AGENTS_REL)


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def textify(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join([str(k) for k in value.keys()] + [textify(v) for v in value.values()])
    if isinstance(value, list):
        return " ".join(textify(item) for item in value)
    return str(value)


def lower_blob(files: dict[str, dict[str, Any]]) -> str:
    return " ".join(str(item.get("text", "")) for item in files.values()).lower()


def read_evidence_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    payload: Any = None
    parse_error = ""
    if path.suffix.lower() == ".json":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            parse_error = str(exc)
    return {
        "path": path,
        "text": text,
        "json": payload,
        "parseError": parse_error,
        "chars": len(text.strip()),
    }


def evidence_candidates(evidence_dir: Path, agent_id: str, output_name: str) -> list[Path]:
    return [
        evidence_dir / agent_id / output_name,
        evidence_dir / output_name,
    ]


def read_agent_files(evidence_dir: Path, agent_id: str, required_outputs: list[str]) -> dict[str, dict[str, Any]]:
    files: dict[str, dict[str, Any]] = {}
    for output_name in required_outputs:
        for candidate in evidence_candidates(evidence_dir, agent_id, output_name):
            if candidate.is_file():
                files[output_name] = read_evidence_file(candidate)
                break
    return files


def iter_json_nodes(value: Any) -> list[Any]:
    nodes = [value]
    if isinstance(value, dict):
        for child in value.values():
            nodes.extend(iter_json_nodes(child))
    elif isinstance(value, list):
        for child in value:
            nodes.extend(iter_json_nodes(child))
    return nodes


def find_status(value: Any) -> str:
    for node in iter_json_nodes(value):
        if isinstance(node, dict):
            for key, child in node.items():
                if normalize_key(str(key)) in {"status", "verdict", "result"}:
                    status = str(child).upper()
                    if status in STATUS_VALUES:
                        return "BLOCK" if status in {"BLOCKED", "FAIL"} else status
    return ""


def field_values(value: Any, names: set[str]) -> list[Any]:
    normalized = {normalize_key(name) for name in names}
    results: list[Any] = []
    for node in iter_json_nodes(value):
        if not isinstance(node, dict):
            continue
        for key, child in node.items():
            key_norm = normalize_key(str(key))
            if key_norm in normalized or any(name in key_norm or key_norm in name for name in normalized):
                results.append(child)
    return results


def count_field(value: Any, names: set[str]) -> int:
    best = 0
    for child in field_values(value, names):
        if isinstance(child, list):
            best = max(best, len([item for item in child if textify(item).strip()]))
        elif isinstance(child, dict):
            best = max(best, len([item for item in child.values() if textify(item).strip()]))
        elif isinstance(child, str):
            parts = [part.strip() for part in re.split(r"[,;\n]+", child) if part.strip()]
            best = max(best, len(parts) if len(parts) > 1 else (1 if child.strip() else 0))
        elif isinstance(child, (int, float, bool)):
            best = max(best, 1)
    return best


def truthy_field(value: Any, names: set[str]) -> bool:
    for child in field_values(value, names):
        if isinstance(child, bool):
            return child
        if isinstance(child, list):
            return bool(child)
        if isinstance(child, dict):
            return bool(child)
        if isinstance(child, (int, float)):
            return child > 0
        if isinstance(child, str):
            if child.strip().lower() in {"true", "yes", "pass", "passed", "inspected", "present"}:
                return True
            if child.strip():
                return True
    return False


def numeric_values(value: Any, names: set[str]) -> list[float]:
    numbers: list[float] = []
    for child in field_values(value, names):
        if isinstance(child, (int, float)):
            numbers.append(float(child))
        elif isinstance(child, str):
            for match in re.findall(r"\d+(?:\.\d+)?", child):
                try:
                    numbers.append(float(match))
                except ValueError:
                    pass
        elif isinstance(child, dict):
            for nested in child.values():
                if isinstance(nested, (int, float)):
                    numbers.append(float(nested))
    return numbers


def normalized_similarity(value: float) -> float:
    return value / 100.0 if value > 1 else value


def term_groups_present(blob: str, groups: list[set[str]]) -> int:
    count = 0
    for group in groups:
        if any(term in blob for term in group):
            count += 1
    return count


def json_outputs(files: dict[str, dict[str, Any]]) -> list[tuple[str, dict[str, Any]]]:
    return [
        (name, item)
        for name, item in files.items()
        if name.endswith(".json")
    ]


def has_json(files: dict[str, dict[str, Any]], output_name: str) -> dict[str, Any] | None:
    item = files.get(output_name)
    if item and isinstance(item.get("json"), dict):
        return item["json"]
    return None


def add_status_issue(files: dict[str, dict[str, Any]], warnings: list[str], blockers: list[str], *, final_gate: bool, critical: bool) -> None:
    for output_name, item in json_outputs(files):
        if item.get("parseError"):
            blockers.append(f"{output_name} is not valid JSON.")
            continue
        payload = item.get("json")
        if payload in ({}, [], None):
            blockers.append(f"{output_name} is empty or structurally meaningless.")
            continue
        status = find_status(payload)
        if status == "BLOCK":
            blockers.append(f"{output_name} reports BLOCK.")
        elif status == "REVISE_REQUIRED":
            warnings.append(f"{output_name} reports REVISE_REQUIRED.")
        elif final_gate and critical and status and status != "PASS":
            blockers.append(f"{output_name} does not report PASS in final gate.")


def add_generic_quality_issues(files: dict[str, dict[str, Any]], warnings: list[str], blockers: list[str]) -> None:
    for output_name, item in files.items():
        text = str(item.get("text", "")).strip()
        if not text:
            blockers.append(f"{output_name} is empty.")
            continue
        compact = re.sub(r"\s+", " ", text.lower()).strip()
        if len(compact) < 24:
            blockers.append(f"{output_name} is too short to prove semantic evidence.")
        if compact in EMPTY_EVIDENCE_MARKERS or any(compact == marker for marker in EMPTY_EVIDENCE_MARKERS):
            blockers.append(f"{output_name} is placeholder/smoke evidence, not a real receipt.")
        if any(marker in compact for marker in {"lorem ipsum", "todo:", "tbd only"}):
            warnings.append(f"{output_name} still contains unfinished placeholder language.")


def validate_reference_visual(files: dict[str, dict[str, Any]], warnings: list[str], _: list[str]) -> None:
    groups = [
        {"typography", "type scale", "font"},
        {"layout", "grid", "composition"},
        {"hierarchy", "information density"},
        {"color", "palette", "accent"},
        {"spacing", "rhythm", "density"},
        {"media", "image", "imagery", "mockup"},
        {"effect", "shadow", "gradient", "depth", "polish"},
        {"copying risk", "copy risk", "do-not-copy", "do not copy"},
    ]
    if term_groups_present(lower_blob(files), groups) < 6:
        warnings.append("Reference analysis must cover typography, layout, hierarchy, color, spacing, media/effects, and copying risk.")


def validate_style_dna(files: dict[str, dict[str, Any]], warnings: list[str], blockers: list[str]) -> None:
    blob = lower_blob(files)
    groups = [
        {"style dna", "transferable", "abstract logic"},
        {"reinterpret", "reconfigure", "remap", "original"},
        {"do-not-copy", "do not copy", "boundary", "non-transferable"},
        {"color role", "section order", "hero grammar", "visual signature"},
    ]
    if term_groups_present(blob, groups) < 4:
        blockers.append("Style DNA must include transferable logic, reinterpretation plan, do-not-copy boundary, and remapped visual roles.")


def validate_brand_memory(files: dict[str, dict[str, Any]], warnings: list[str], blockers: list[str]) -> None:
    blob = lower_blob(files)
    if not all(term in blob for term in ("brand", "reference")):
        warnings.append("Brand/reference guardian evidence must mention both brand uniqueness and reference usage policy.")
    for output in ("reference-usage-check.json", "brand-name-check.json"):
        payload = has_json(files, output)
        if payload is not None and find_status(payload) not in {"PASS", ""}:
            blockers.append(f"{output} must PASS before template planning continues.")


def validate_product_architecture(files: dict[str, dict[str, Any]], warnings: list[str], blockers: list[str], context: dict[str, Any]) -> None:
    blob = lower_blob(files)
    groups = [
        {"buyer", "target audience", "target buyer"},
        {"product promise", "value proposition", "commercial purpose"},
        {"marketplace", "sellable", "template product"},
        {"section", "page list", "screen list"},
        {"conversion", "journey", "cta"},
    ]
    if term_groups_present(blob, groups) < 4:
        warnings.append("Product architecture must prove buyer, product promise, marketplace value, section/page scope, and conversion logic.")
    count = section_count_from_payloads(files)
    if is_marketplace_template_context(context) and 0 < count < 8:
        blockers.append("Marketplace website template architecture has fewer than 8 meaningful sections.")


def section_count_from_payloads(files: dict[str, dict[str, Any]]) -> int:
    best = 0
    for _, item in json_outputs(files):
        payload = item.get("json")
        if payload is None:
            continue
        best = max(
            best,
            count_field(payload, {"sections", "sectionList", "sectionFlow", "sectionArchitecture", "blocks"}),
        )
        for value in numeric_values(payload, {"sectionCount", "sectionsCount"}):
            best = max(best, int(value))
    return best


def is_marketplace_template_context(context: dict[str, Any]) -> bool:
    blob = " ".join(
        str(context.get(key, ""))
        for key in ("task", "templateType", "niche", "targetBuyer")
    ).lower()
    return bool(context.get("marketplace")) or any(term in blob for term in ("marketplace", "website template", "figma template", "template"))


def validate_section_flow(files: dict[str, dict[str, Any]], warnings: list[str], blockers: list[str], context: dict[str, Any]) -> None:
    blob = lower_blob(files)
    if term_groups_present(blob, [{"rhythm", "pacing"}, {"density"}, {"cta"}, {"anti-generic", "generic"}, {"buyer journey", "conversion"}]) < 4:
        warnings.append("Section flow needs rhythm, density variation, CTA placement, and anti-generic buyer journey logic.")
    count = section_count_from_payloads(files)
    if is_marketplace_template_context(context) and 0 < count < 8:
        blockers.append("Section flow is too short for marketplace website-template standard.")


def validate_layout(files: dict[str, dict[str, Any]], warnings: list[str], _: list[str]) -> None:
    blob = lower_blob(files)
    if term_groups_present(blob, [{"grid"}, {"hero"}, {"card", "media"}, {"responsive"}, {"similarity", "fingerprint"}]) < 4:
        warnings.append("Layout composition evidence must cover grid, hero grammar, card/media behavior, responsive behavior, and similarity risk.")


def validate_design_system(files: dict[str, dict[str, Any]], warnings: list[str], blockers: list[str]) -> None:
    payload = has_json(files, "design-system-depth-check.json")
    if payload is None:
        blockers.append("design-system-depth-check.json must be valid structured JSON.")
        return
    counts = {
        "product DNA": count_field(payload, {"productDna", "productDNA", "templateDna", "templateDNA"}),
        "color token roles": count_field(payload, {"colorTokens", "colorRoles", "surfaceTokens"}),
        "typography styles": count_field(payload, {"typographyTokens", "typeScale", "textStyles"}),
        "spacing rhythms": count_field(payload, {"spacingTokens", "spacingRhythm", "layoutSpacing"}),
        "components": count_field(payload, {"components", "componentSystem", "componentAnatomy"}),
        "product-specific modules": count_field(payload, {"productSpecificModules", "categoryModules", "domainModules"}),
        "states or variants": max(count_field(payload, {"states"}), count_field(payload, {"variants"}), count_field(payload, {"componentStates"})),
        "section modules": count_field(payload, {"sectionModules", "patternModules", "modules"}),
        "usage examples": count_field(payload, {"usageExamples", "examples", "componentUsage"}),
        "package/source map": count_field(payload, {"packageSourceMap", "sourceMap", "includedSourceMap"}),
    }
    thresholds = {
        "product DNA": 1,
        "color token roles": 5,
        "typography styles": 5,
        "spacing rhythms": 3,
        "components": 8,
        "product-specific modules": 3,
        "states or variants": 4,
        "section modules": 5,
        "usage examples": 3,
        "package/source map": 1,
    }
    weak = [name for name, minimum in thresholds.items() if counts[name] < minimum]
    if weak:
        blockers.append("Design system depth is insufficient: " + ", ".join(f"{name}={counts[name]}" for name in weak))
    if not truthy_field(payload, {"effectLanguage", "shadowTokens", "gradientTokens", "surfaceDepth", "visualSignature"}):
        warnings.append("Design system should document effect/surface-depth or visual-signature rules, not just flat tokens.")
    if not truthy_field(payload, {"boardMetrics", "artifactEvidence", "figmaBoardMetrics"}):
        blockers.append("Design system depth check must include board metrics or artifact evidence, not only a text receipt.")


def validate_visual_signature(files: dict[str, dict[str, Any]], warnings: list[str], _: list[str]) -> None:
    blob = lower_blob(files)
    if term_groups_present(blob, [{"motif", "signature"}, {"background", "surface"}, {"cta"}, {"icon", "container"}, {"unique", "original"}]) < 4:
        warnings.append("Visual signature evidence must define motif, surface/background treatment, CTA language, icon/container language, and uniqueness.")


def validate_figma_source(files: dict[str, dict[str, Any]], warnings: list[str], blockers: list[str]) -> None:
    payload = has_json(files, "figma-source-qa.json")
    if payload is None:
        blockers.append("figma-source-qa.json must be valid structured JSON.")
        return
    required = {
        "auto-layout": {"autoLayout", "autoLayoutCoverage", "layoutMode"},
        "components": {"components", "componentCount"},
        "variants": {"variants", "variantSets"},
        "layer naming": {"layerNaming", "namedLayers"},
        "tokens/styles": {"tokens", "styles", "variables"},
        "editability": {"editability", "editable"},
    }
    missing = [name for name, keys in required.items() if not truthy_field(payload, keys)]
    if missing:
        blockers.append("Figma source QA is missing proof for " + ", ".join(missing))
    if find_status(payload) not in {"PASS", ""}:
        blockers.append("Figma source QA must PASS for Figma source-template work.")
    if not truthy_field(payload, {"screenshot", "screenshots", "inspectedScreenshot"}):
        warnings.append("Figma source QA should include screenshot or frame inspection evidence.")


def validate_originality(files: dict[str, dict[str, Any]], warnings: list[str], blockers: list[str]) -> None:
    payload = has_json(files, "originality-audit.json")
    if payload is None:
        blockers.append("originality-audit.json must be valid structured JSON.")
        return
    scores = [
        normalized_similarity(value)
        for value in numeric_values(payload, {"similarityScore", "referenceSimilarityScore", "previousTemplateSimilarityScore", "maxSimilarity", "pairwiseSimilarity"})
    ]
    if scores and max(scores) > 0.10:
        blockers.append(f"Originality audit similarity exceeds 10 percent: {max(scores):.2f}")
    if not scores:
        warnings.append("Originality audit should include a numeric similarity score.")
    if term_groups_present(textify(payload).lower(), [{"hero grammar"}, {"section flow"}, {"layout"}, {"component rhythm"}, {"reference", "previous"}]) < 4:
        warnings.append("Originality audit should compare hero grammar, section flow, layout, component rhythm, and reference/prior-template risk.")
    if find_status(payload) not in {"PASS", ""}:
        blockers.append("Originality audit must PASS before final delivery.")


def validate_visual_qa(files: dict[str, dict[str, Any]], warnings: list[str], blockers: list[str]) -> None:
    payload = has_json(files, "visual-qa-report.json")
    if payload is None:
        blockers.append("visual-qa-report.json must be valid structured JSON.")
        return
    if not truthy_field(payload, {"screenshotInspected", "screenshotEvidence", "screenshots", "finalScreenshot", "imageInspected"}):
        blockers.append("Visual QA must prove screenshot or rendered visual inspection.")
    score_keys = {
        "heroStrength",
        "hierarchyScore",
        "spacingScore",
        "densityScore",
        "contrastScore",
        "depthScore",
        "polishScore",
        "marketplaceFeelScore",
    }
    scores = numeric_values(payload, score_keys)
    normalized = [score / 100.0 if score > 5 else score / 5.0 for score in scores]
    if normalized and min(normalized) < 0.60:
        blockers.append("Visual QA score is below premium threshold.")
    if not normalized:
        warnings.append("Visual QA should include hero, hierarchy, spacing, density, contrast, depth, polish, and marketplace-feel scores.")
    issue_text = textify(field_values(payload, {"issues", "defects", "blockingIssues", "bugs"})).lower()
    if any(term in issue_text for term in ("clipped", "overlap", "flat", "generic", "cramped", "too empty", "weak hero")):
        blockers.append("Visual QA contains blocking visual defects.")
    if find_status(payload) not in {"PASS", ""}:
        blockers.append("Visual QA must PASS before final delivery.")


def validate_marketplace(files: dict[str, dict[str, Any]], warnings: list[str], blockers: list[str]) -> None:
    payload = has_json(files, "marketplace-readiness-verdict.json")
    if payload is None:
        blockers.append("marketplace-readiness-verdict.json must be valid structured JSON.")
        return
    if find_status(payload) != "PASS":
        blockers.append("Marketplace readiness verdict must explicitly PASS.")
    required = {
        "critical subagents": {"criticalAgentsPass", "allCriticalAgentsPass", "criticalSubagents"},
        "screenshot evidence": {"screenshotEvidence", "screenshots", "visualEvidence"},
        "design-system depth": {"designSystemDepth", "designSystemStatus"},
        "originality": {"originalityStatus", "similarityStatus"},
        "buyer value": {"buyerValue", "marketplaceValue", "commercialValue"},
    }
    missing = [name for name, keys in required.items() if not truthy_field(payload, keys)]
    if missing:
        blockers.append("Marketplace verdict is missing proof for " + ", ".join(missing))
    if truthy_field(payload, {"missingCriticalReceipts", "openRepairTickets", "blockingIssues"}):
        blockers.append("Marketplace verdict reports missing critical receipts or open blocking issues.")


AGENT_VALIDATORS = {
    "reference_visual_analyst": validate_reference_visual,
    "style_dna_extractor": validate_style_dna,
    "brand_reference_memory_guardian": validate_brand_memory,
    "template_product_architect": validate_product_architecture,
    "section_flow_strategist": validate_section_flow,
    "layout_composition_director": validate_layout,
    "design_system_director": validate_design_system,
    "visual_signature_builder": validate_visual_signature,
    "figma_source_qa": validate_figma_source,
    "originality_similarity_auditor": validate_originality,
    "visual_qa_inspector": validate_visual_qa,
    "marketplace_readiness_judge": validate_marketplace,
}


def call_agent_validator(agent_id: str, files: dict[str, dict[str, Any]], warnings: list[str], blockers: list[str], context: dict[str, Any]) -> None:
    validator = AGENT_VALIDATORS.get(agent_id)
    if validator is None:
        return
    if agent_id in {"template_product_architect", "section_flow_strategist"}:
        validator(files, warnings, blockers, context)  # type: ignore[misc]
    else:
        validator(files, warnings, blockers)  # type: ignore[misc]


def relative_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def validate_subagent_evidence(
    *,
    root: Path,
    agents_payload: dict[str, Any],
    active_agents: list[str],
    evidence_dir: Path,
    final_gate: bool,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    agents_by_id = {str(agent["id"]): agent for agent in agents_payload.get("agents", [])}
    context = context or {}
    agent_results: list[dict[str, Any]] = []
    blocking_reasons: list[str] = []
    required_repairs: list[str] = []

    for agent_id in active_agents:
        agent = agents_by_id.get(agent_id, {})
        required_outputs = [str(item) for item in agent.get("requiredOutputs", [])]
        files = read_agent_files(evidence_dir, agent_id, required_outputs)
        critical = bool(agent.get("critical"))
        missing = [name for name in required_outputs if name not in files]
        warnings: list[str] = []
        blockers: list[str] = []
        if missing:
            blockers.append("Missing required outputs: " + ", ".join(missing))
        add_generic_quality_issues(files, warnings, blockers)
        add_status_issue(files, warnings, blockers, final_gate=final_gate, critical=critical)
        call_agent_validator(agent_id, files, warnings, blockers, context)

        if blockers:
            status = "BLOCK"
        elif warnings:
            status = "REVISE_REQUIRED"
        else:
            status = "PASS"
        if final_gate and critical and status != "PASS":
            status = "BLOCK"

        evidence_paths = [
            relative_path(item["path"], root)
            for item in files.values()
            if isinstance(item.get("path"), Path)
        ]
        if status == "BLOCK":
            blocking_reasons.extend(f"{agent_id}: {reason}" for reason in blockers)
        if status != "PASS":
            required_repairs.append(f"Repair semantic receipt quality for {agent.get('name', agent_id)}.")
        agent_results.append(
            {
                "agentId": agent_id,
                "name": str(agent.get("name", agent_id)),
                "critical": critical,
                "status": status,
                "missingOutputs": missing,
                "evidence": sorted(evidence_paths),
                "semanticWarnings": sorted(set(warnings)),
                "semanticBlockers": sorted(set(blockers)),
            }
        )

    if any(item["status"] == "BLOCK" for item in agent_results):
        status = "BLOCK"
    elif any(item["status"] == "REVISE_REQUIRED" for item in agent_results):
        status = "REVISE_REQUIRED"
    else:
        status = "PASS"
    return {
        "schema": SCHEMA_ID,
        "version": "1.0.0",
        "status": status,
        "finalGate": final_gate,
        "evidenceDir": relative_path(evidence_dir, root),
        "activeAgents": active_agents,
        "agentResults": agent_results,
        "blockingReasons": sorted(set(blocking_reasons)),
        "requiredRepairs": sorted(set(required_repairs)),
        "rulesSource": RULES_REL,
        "generatedAt": now_iso(),
    }


def active_from_args(args: argparse.Namespace, payload: dict[str, Any]) -> list[str]:
    if args.receipt:
        receipt = load_json(Path(args.receipt).expanduser().resolve())
        return [str(item) for item in receipt.get("activeAgents", [])]
    if args.active_agents:
        return [item.strip() for item in args.active_agents.split(",") if item.strip()]
    mode = payload.get("modes", {}).get(args.mode, {})
    return [str(item) for item in mode.get("requiredAgentIds", [])]


def main() -> int:
    args = parse_args()
    root = repo_root()
    payload = load_agents(root)
    evidence_dir = Path(args.evidence_dir).expanduser()
    if not evidence_dir.is_absolute():
        evidence_dir = root / evidence_dir
    context = {
        "task": args.task,
        "templateType": args.template_type,
        "niche": args.niche,
        "targetBuyer": args.target_buyer,
        "marketplace": args.marketplace,
        "hasReference": args.has_reference,
        "figmaSource": args.figma_source,
    }
    result = validate_subagent_evidence(
        root=root,
        agents_payload=payload,
        active_agents=active_from_args(args, payload),
        evidence_dir=evidence_dir,
        final_gate=args.final,
        context=context,
    )
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Subagent semantic validation: {result['status']}")
        for repair in result["requiredRepairs"]:
            print(f"- {repair}")
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
