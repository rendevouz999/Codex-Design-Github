#!/usr/bin/env python3
"""Design Craft adapter for Brain Design runtime."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


REQUIRED_FIELDS = [
    "route",
    "productFamily",
    "mode",
    "designCognition",
    "layoutFingerprint",
    "simulationVerdict",
    "layoutAuditStatus",
    "designSystemRequirement",
    "craftScope",
]

FORBIDDEN_OVERRIDE_FIELDS = {
    "overrideRoute": "route",
    "overrideProductFamily": "productFamily",
    "overrideMode": "mode",
    "overrideStructure": "sectionStructure",
    "overrideCognition": "designCognition",
    "overrideSimulationVerdict": "simulationVerdict",
    "overrideLayoutAuditStatus": "layoutAuditStatus",
    "overridePostBuildStatus": "postBuildStatus",
    "finalStatus": "finalStatus",
}

GENERIC_MINIMAL_TERMS = [
    "hero > features > cta",
    "generic minimalist",
    "shorten full template",
    "minimal scaffold",
    "3 section landing",
]


def load_request(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def blocked(status_reason: str, request: dict[str, Any], blocked_overrides: list[str]) -> dict[str, Any]:
    return {
        "status": "BLOCKED_BY_BRAIN_DESIGN_CONTRACT",
        "craftResult": {
            "reason": status_reason,
            "brainDesignRoute": request.get("route", ""),
            "brainDesignProductFamily": request.get("productFamily", ""),
            "brainDesignMode": request.get("mode", ""),
        },
        "tokens": {},
        "typography": {},
        "spacing": {},
        "components": [],
        "states": [],
        "accessibility": [],
        "sourceHandoff": [],
        "polishNotes": [],
        "blockedOverrides": blocked_overrides,
    }


def validate_request(request: dict[str, Any]) -> list[str]:
    return [field for field in REQUIRED_FIELDS if field not in request]


def detect_overrides(request: dict[str, Any]) -> list[str]:
    blocked = []
    for field, decision in FORBIDDEN_OVERRIDE_FIELDS.items():
        if field in request:
            blocked.append(f"{field} attempts to override Brain Design {decision}")
    proposed = request.get("proposedOverrides", {})
    if isinstance(proposed, dict):
        for field in proposed:
            if field in {"route", "productFamily", "mode", "structure", "simulationVerdict", "layoutAuditStatus", "postBuildStatus", "finalStatus"}:
                blocked.append(f"proposedOverrides.{field} attempts to override Brain Design")
    text = json.dumps(request, ensure_ascii=False).lower()
    for term in GENERIC_MINIMAL_TERMS:
        if term in text:
            blocked.append(f"generic scaffold override attempt: {term}")
    return blocked


def scope_list(request: dict[str, Any]) -> list[str]:
    scope = request.get("craftScope", [])
    if isinstance(scope, str):
        return [scope]
    return [str(item) for item in scope]


def build_result(request: dict[str, Any]) -> dict[str, Any]:
    missing = validate_request(request)
    if missing:
        return blocked(f"Missing Brain Design contract fields: {', '.join(missing)}", request, missing)
    blocked_overrides = detect_overrides(request)
    if blocked_overrides:
        return blocked("Design Craft cannot override Brain Design decisions.", request, blocked_overrides)

    mode = request.get("mode", "website-template")
    product = request.get("productFamily", "template_product")
    scope = scope_list(request)
    accent = "mapped_accent_from_brain_design"
    return {
        "status": "PASS",
        "craftResult": {
            "role": "support_only",
            "route": request.get("route", ""),
            "productFamily": product,
            "mode": mode,
            "craftScope": scope,
            "brainDesignFinalAuthority": True,
        },
        "tokens": {
            "colorRoles": {
                "background": "use Brain Design background role",
                "surface": "use Brain Design surface role",
                "accent": accent,
                "cta": "preserve Brain Design CTA/action role",
                "border": "low contrast divider role",
            },
            "radius": {"card": "8px or Brain Design token", "button": "matched to component role"},
        },
        "typography": {
            "display": "preserve Brain Design hierarchy; improve contrast and rhythm",
            "body": "optimize readability and marketplace editability",
            "label": "clear labels for components and forms",
        },
        "spacing": {
            "scale": [4, 8, 12, 16, 24, 32, 48, 64],
            "sectionRhythm": "support Brain Design section logic without changing order",
            "componentGap": "consistent with layout fingerprint density",
        },
        "components": [
            "button primary/secondary/tertiary",
            "cards",
            "navigation/header",
            "CTA block",
            "media placeholder",
            "footer",
        ],
        "states": ["default", "hover", "focus", "active", "disabled", "error", "loading", "empty"],
        "accessibility": [
            "maintain readable contrast",
            "preserve focus indicators",
            "avoid text overlap",
            "keep editable text and placeholders",
        ],
        "sourceHandoff": [
            "do not flatten important text",
            "name layers/components clearly",
            "keep placeholders replaceable",
            "support auto-layout/source hygiene",
        ],
        "polishNotes": [
            "refine visual depth without changing Brain Design structure",
            "apply typography rhythm to existing section logic",
            "use color remapping rather than reference palette copying",
        ],
        "blockedOverrides": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Design Craft as Brain Design support adapter.")
    parser.add_argument("--request", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        request = load_request(Path(args.request))
        result = build_result(request)
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        result = {
            "status": "ERROR",
            "craftResult": {"reason": str(exc)},
            "tokens": {},
            "typography": {},
            "spacing": {},
            "components": [],
            "states": [],
            "accessibility": [],
            "sourceHandoff": [],
            "polishNotes": [],
            "blockedOverrides": [str(exc)],
        }
    print(json.dumps(result, indent=2) if args.json else result["status"])
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
