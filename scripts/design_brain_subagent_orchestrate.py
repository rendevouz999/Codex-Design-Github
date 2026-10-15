#!/usr/bin/env python
"""Plan and verify Brain Design subagent orchestration receipts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from design_brain_subagent_receipt_validate import validate_subagent_evidence

SCHEMA_ID = "design-brain.design-subagents.orchestration-receipt.v1"
VERSION = "1.0.0"
AGENTS_REL = ".design-brain/design-subagents/agents.json"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug[:64] or "subagent-run"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Brain Design subagent orchestration gate.")
    parser.add_argument("--task", default="")
    parser.add_argument("--template-type", default="")
    parser.add_argument("--niche", default="")
    parser.add_argument("--target-buyer", default="")
    parser.add_argument("--mode", choices=("auto", "full", "standard", "lightweight"), default="auto")
    parser.add_argument("--has-reference", action="store_true")
    parser.add_argument("--figma-source", action="store_true")
    parser.add_argument("--marketplace", action="store_true")
    parser.add_argument("--template-count", type=int, default=1)
    parser.add_argument("--final", action="store_true", help="Treat missing critical evidence as BLOCK instead of REVISE_REQUIRED.")
    parser.add_argument("--evidence-dir", default="", help="Directory containing expected subagent receipt files.")
    parser.add_argument("--output-dir", default="", help="Directory where orchestration receipt files should be written.")
    parser.add_argument("--skip-semantic-validation", action="store_true", help="Debug only: validate file presence without validating receipt contents.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def load_agents(root: Path) -> dict[str, Any]:
    path = root / AGENTS_REL
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"ERROR: cannot read {AGENTS_REL}: {exc}") from exc
    if payload.get("schema") != "design-brain.design-subagents.agents.v1":
        raise SystemExit(f"ERROR: invalid subagent schema in {AGENTS_REL}")
    agents = payload.get("agents")
    if not isinstance(agents, list) or not agents:
        raise SystemExit(f"ERROR: {AGENTS_REL} must contain agents.")
    seen: set[str] = set()
    for agent in agents:
        agent_id = str(agent.get("id") or "")
        if not agent_id or agent_id in seen:
            raise SystemExit(f"ERROR: duplicate or missing agent id: {agent_id!r}")
        seen.add(agent_id)
        for key in ("name", "role", "phase", "focus", "requiredInputs", "requiredOutputs", "evaluation_axes", "blockingAuthority", "critical", "blockingRules", "vote_rules"):
            if key not in agent:
                raise SystemExit(f"ERROR: agent {agent_id} missing {key}.")
    return payload


def text_blob(args: argparse.Namespace) -> str:
    return " ".join(
        [
            args.task,
            args.template_type,
            args.niche,
            args.target_buyer,
        ]
    ).lower()


def infer_mode(args: argparse.Namespace) -> str:
    if args.mode != "auto":
        return args.mode
    blob = text_blob(args)
    if args.template_count > 1 or args.has_reference or args.figma_source or args.marketplace:
        return "full"
    if any(term in blob for term in ("template", "landing", "homepage", "design system", "marketplace", "figma")):
        return "standard"
    return "lightweight"


def active_agent_ids(payload: dict[str, Any], mode: str, args: argparse.Namespace) -> list[str]:
    modes = payload.get("modes", {})
    mode_payload = modes.get(mode, {})
    active = list(mode_payload.get("requiredAgentIds", []))
    if mode == "lightweight":
        conditional = list(mode_payload.get("conditionalAgentIds", []))
        if args.has_reference:
            active.extend(["reference_visual_analyst", "style_dna_extractor", "brand_reference_memory_guardian"])
        if args.figma_source:
            active.append("figma_source_qa")
        if args.marketplace:
            active.append("marketplace_readiness_judge")
        for item in conditional:
            if item in active:
                continue
    deduped: list[str] = []
    for agent_id in active:
        if agent_id not in deduped:
            deduped.append(agent_id)
    return deduped


def evidence_paths_for_output(root: Path, evidence_dir: Path | None, agent_id: str, output_name: str) -> list[str]:
    if evidence_dir is None:
        return []
    candidates = [
        evidence_dir / agent_id / output_name,
        evidence_dir / output_name,
    ]
    found: list[str] = []
    for path in candidates:
        if path.is_file():
            try:
                found.append(path.resolve().relative_to(root.resolve()).as_posix())
            except ValueError:
                found.append(str(path.resolve()))
    return found


def build_receipt(args: argparse.Namespace, payload: dict[str, Any]) -> dict[str, Any]:
    root = repo_root()
    mode = infer_mode(args)
    agents_by_id = {str(agent["id"]): agent for agent in payload["agents"]}
    active = active_agent_ids(payload, mode, args)
    evidence_dir = Path(args.evidence_dir).expanduser() if args.evidence_dir else None
    if evidence_dir is not None and not evidence_dir.is_absolute():
        evidence_dir = root / evidence_dir

    agent_statuses: list[dict[str, Any]] = []
    missing_critical: list[str] = []
    blocking_reasons: list[str] = []
    required_repairs: list[str] = []
    semantic_validation: dict[str, Any] | None = None

    for agent_id in active:
        agent = agents_by_id.get(agent_id)
        if agent is None:
            blocking_reasons.append(f"Active subagent is not defined: {agent_id}")
            continue
        required_outputs = [str(item) for item in agent.get("requiredOutputs", [])]
        evidence: list[str] = []
        missing_outputs: list[str] = []
        for output_name in required_outputs:
            paths = evidence_paths_for_output(root, evidence_dir, agent_id, output_name)
            if paths:
                evidence.extend(paths)
            else:
                missing_outputs.append(output_name)
        critical = bool(agent.get("critical"))
        authority = str(agent.get("blockingAuthority") or "none")
        if missing_outputs:
            if args.final and critical:
                status = "BLOCK"
                reason = f"{agent['name']} missing required final evidence: {', '.join(missing_outputs)}"
                blocking_reasons.append(reason)
                missing_critical.extend(f"{agent_id}/{item}" for item in missing_outputs)
                required_repairs.append(f"Create and attach required evidence for {agent['name']}: {', '.join(missing_outputs)}")
            else:
                status = "REVISE_REQUIRED"
                if critical:
                    missing_critical.extend(f"{agent_id}/{item}" for item in missing_outputs)
                required_repairs.append(f"Complete {agent['name']} outputs: {', '.join(missing_outputs)}")
        else:
            status = "PASS"
        agent_statuses.append(
            {
                "agentId": agent_id,
                "name": str(agent["name"]),
                "phase": str(agent["phase"]),
                "critical": critical,
                "blockingAuthority": authority,
                "status": status,
                "missingOutputs": missing_outputs,
                "evidence": sorted(set(evidence)),
                "blockingReasons": [reason for reason in blocking_reasons if str(agent["name"]) in reason],
            }
        )

    if evidence_dir is not None and not args.skip_semantic_validation:
        semantic_validation = validate_subagent_evidence(
            root=root,
            agents_payload=payload,
            active_agents=active,
            evidence_dir=evidence_dir,
            final_gate=bool(args.final),
            context={
                "task": args.task,
                "templateType": args.template_type,
                "niche": args.niche,
                "targetBuyer": args.target_buyer,
                "marketplace": args.marketplace,
                "hasReference": args.has_reference,
                "figmaSource": args.figma_source,
            },
        )
        semantic_by_agent = {item["agentId"]: item for item in semantic_validation.get("agentResults", [])}
        for item in agent_statuses:
            semantic = semantic_by_agent.get(item["agentId"])
            if not semantic:
                continue
            item["semanticStatus"] = semantic.get("status", "PASS")
            item["semanticWarnings"] = semantic.get("semanticWarnings", [])
            item["semanticBlockers"] = semantic.get("semanticBlockers", [])
            critical = bool(item.get("critical"))
            if semantic.get("status") == "BLOCK" or (args.final and critical and semantic.get("status") != "PASS"):
                item["status"] = "BLOCK"
                reason = f"{item['name']} semantic evidence is not final-pass quality."
                blocking_reasons.append(reason)
                required_repairs.append(f"Repair semantic evidence for {item['name']}.")
            elif semantic.get("status") == "REVISE_REQUIRED" and item["status"] == "PASS":
                item["status"] = "REVISE_REQUIRED"
                required_repairs.append(f"Strengthen semantic evidence for {item['name']}.")
        blocking_reasons.extend(str(item) for item in semantic_validation.get("blockingReasons", []))
        required_repairs.extend(str(item) for item in semantic_validation.get("requiredRepairs", []))

    if any(item["status"] == "BLOCK" for item in agent_statuses) or blocking_reasons:
        overall = "BLOCK"
    elif any(item["status"] == "REVISE_REQUIRED" for item in agent_statuses):
        overall = "REVISE_REQUIRED"
    else:
        overall = "PASS"

    return {
        "schema": SCHEMA_ID,
        "version": VERSION,
        "runId": slugify(args.task or args.template_type or "subagent-run") + "-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
        "mode": mode,
        "finalGate": bool(args.final),
        "task": args.task,
        "templateType": args.template_type,
        "niche": args.niche,
        "targetBuyer": args.target_buyer,
        "status": overall,
        "activeAgents": active,
        "agentStatuses": agent_statuses,
        "missingCriticalEvidence": sorted(set(missing_critical)),
        "blockingReasons": sorted(set(blocking_reasons)),
        "requiredRepairs": sorted(set(required_repairs)),
        "semanticValidationEnabled": bool(evidence_dir is not None and not args.skip_semantic_validation),
        "semanticValidation": semantic_validation,
        "agentSource": AGENTS_REL,
        "generatedAt": now_iso(),
    }


def write_outputs(receipt: dict[str, Any], output_dir: str) -> None:
    if not output_dir:
        return
    root = repo_root()
    out = Path(output_dir).expanduser()
    if not out.is_absolute():
        out = root / out
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "subagent-orchestration-receipt.json"
    md_path = out / "subagent-orchestration-receipt.md"
    json_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    lines = [
        "# Subagent Orchestration Receipt",
        "",
        f"- Run ID: {receipt['runId']}",
        f"- Mode: {receipt['mode']}",
        f"- Final gate: {'yes' if receipt['finalGate'] else 'no'}",
        f"- Status: {receipt['status']}",
        "",
        "## Active Agents",
        "",
    ]
    for item in receipt["agentStatuses"]:
        lines.extend(
            [
                f"### {item['name']}",
                "",
                f"- Agent ID: {item['agentId']}",
                f"- Phase: {item['phase']}",
                f"- Status: {item['status']}",
                f"- Missing outputs: {', '.join(item['missingOutputs']) if item['missingOutputs'] else 'none'}",
                f"- Evidence: {', '.join(item['evidence']) if item['evidence'] else 'none'}",
                "",
            ]
        )
    if receipt["requiredRepairs"]:
        lines.append("## Required Repairs")
        lines.append("")
        lines.extend(f"- {item}" for item in receipt["requiredRepairs"])
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> int:
    args = parse_args()
    payload = load_agents(repo_root())
    receipt = build_receipt(args, payload)
    write_outputs(receipt, args.output_dir)
    if args.json:
        sys.stdout.write(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
    else:
        print(f"Subagent orchestration: {receipt['status']} ({receipt['mode']} mode, {len(receipt['activeAgents'])} agents)")
        for repair in receipt["requiredRepairs"]:
            print(f"- {repair}")
    return 0 if receipt["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
