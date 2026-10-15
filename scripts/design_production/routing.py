"""Read-only execution planning. Never invokes a model or grants production approval."""
from __future__ import annotations

import ast
import json

from pydantic import ValidationError

from .contracts import DesignTask
from .policy import ROOT, digest, input_path
from .profiles import PROFILES, select


def plan(request_path: str, preferred: str = "auto", offline: bool = False) -> dict:
    if preferred not in {"auto", "main", "host_agents", "sdk"}:
        raise ValueError("Unknown production route")
    path = input_path(request_path)
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, dict):
        raise ValueError("Production request must be a JSON object")
    limits = []
    task = None
    try:
        task = DesignTask.model_validate(raw)
    except ValidationError as error:
        errors = error.errors(include_url=False, include_input=False)
        # These are recognized SDK-only font restrictions. Other malformed scope
        # must be repaired rather than silently routed around schema validation.
        font_fields = {("presentation", "title_font"), ("presentation", "body_font")}
        if any(tuple(e["loc"]) not in font_fields or e["type"] != "literal_error" for e in errors):
            return {"status": "BLOCKED", "planOnly": True, "finalAllowed": False,
                    "blockerScope": "request", "selectedRoute": None,
                    "errors": [{"field": ".".join(map(str, e["loc"])), "message": e["msg"]} for e in errors]}
        limits.extend({"code": "SDK_FONT_LIMIT", "detail": ".".join(e["loc"])} for e in errors)

    result = {"status": "PASS", "planOnly": True, "finalAllowed": False,
              "request": str(path), "requestSha256": digest(path), "selectedRoute": None,
              "sdkSchemaAccepted": task is not None, "sdkLimitations": limits,
              "executionStarted": False, "paidCalls": 0}
    if raw.get("authorized") is not True or raw.get("no_execution") is True or raw.get("operation") in {"brainstorm", "prompt", "other"}:
        return {**result, "decision": "SKIP", "nextAction": "No production is authorized by this request."}

    profile = PROFILES.get(raw.get("artifact_type"), {})
    if not profile.get("adapter") or raw.get("output_format") not in profile.get("formats", []):
        limits.append({"code": "SDK_PROFILE_LIMIT", "detail": "No SDK adapter for the requested medium/format."})
    else:
        unsupported = sorted(set(raw.get("required_features", [])) - set(profile.get("features", ["editable_text", "editable_shapes", "text_clue_placeholders"])))
        if unsupported:
            limits.append({"code": "SDK_FEATURE_LIMIT", "features": unsupported})
        if task is not None and not unsupported:
            try:
                select(task)
            except ValueError as error:
                limits.append({"code": "SDK_CONTRACT_LIMIT", "detail": str(error)})

    settings = raw.get("presentation") or {}
    if settings.get("reusable_template") and raw.get("units"):
        config = ROOT / "skills/presentation-deck/runtime/native/config.py"
        # Read the literal registry without importing native runtime modules or
        # running their environment/stdio setup during a read-only plan.
        tree = ast.parse(config.read_text(encoding="utf-8-sig"))
        registry = next(node.value for node in tree.body if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == "CANVAS_FORMATS" for target in node.targets))
        presets = ast.literal_eval(registry)
        unit = raw["units"][0]
        viewbox = f"0 0 {unit['width']} {unit['height']}"
        if not any(value["viewbox"] == viewbox for value in presets.values()):
            limits.append({"code": "SDK_CANVAS_LIMIT", "detail": f"Reusable template preset is unavailable: {viewbox}"})
    if not offline and not (raw.get("approval_policy") or {}).get("allow_paid_model", False):
        limits.append({"code": "SDK_PAID_AUTHORIZATION_REQUIRED", "detail": "Paid SDK execution is not authorized; local routes do not require this permission."})

    # This planner belongs to the custom plugin. Its owner selected one host
    # Engineer; SDK compatibility alone must not silently select another route.
    selected = "host_agents" if preferred == "auto" else preferred
    result.update(selectedRoute=selected, decision="PLAN")
    if selected == "sdk" and limits:
        result.update(status="BLOCKED", blockerScope="sdk", alternatives=["main", "host_agents"],
                      nextAction="Repair the explicitly selected SDK route or choose an authorized alternate route. Preserve the brief.")
    elif selected == "sdk":
        result.update(nextAction="Use the explicit SDK production command; input hashes, provider access, scope and all SDK checks still apply.",
                      prerequisites=["Existing provider authentication for paid execution", "Full-build permission and current declared input hashes", "Main review of actual output"])
    elif selected == "host_agents":
        result.update(nextAction="Within this custom plugin, reuse or dispatch exactly one General Design Production Engineer (Codex: gpt-6.1-sol with reasoning_effort=xhigh; Claude Code: plugin agent codex-design:general-design-production-engineer with model claude-opus-5-5 and effort xhigh). Main directs and approves; this plan does not spawn or verify models.",
                      prerequisites=["Authorized plugin task scope; standing single-Engineer delegation authorization", "Available host subagent tool with explicit gpt-6.1-sol and xhigh effort selection (Codex) or the codex-design:general-design-production-engineer plugin agent (Claude Code); no other active worker", "Bounded ownership; one writer per mutable artifact", "Main inspects evidence and decides PASS or REVISE under auto-full trust"],
                      team={"scope": "custom-plugin-only", "mainRequestedModel": "gpt-6-astra", "workerModel": "gpt-6.1-sol", "workerRole": "General Design Production Engineer", "workerReasoningEffort": "xhigh", "claudeCodeMainModel": "claude-fable-5-1", "claudeCodeWorkerAgent": "codex-design:general-design-production-engineer", "claudeCodeWorkerModel": "claude-opus-5-5", "claudeCodeWorkerEffort": "xhigh", "workerEffortVerified": False, "maximumActiveWorkers": 1, "maximumActiveParticipants": 2, "mainModelVerified": False, "workerModelVerified": False},
                      nativeCapabilityVerified=False)
    else:
        result.update(nextAction="Main continues through existing native/local medium tools within the authorized scope; an SDK exception is not required.",
                      prerequisites=["Verify local application/connector, exact fonts, assets and native features", "Validate original brief and scoped inputs in the chosen native workflow", "Render, inspect, repair and verify the actual artifact"],
                      nativeCapabilityVerified=False)
    return result
