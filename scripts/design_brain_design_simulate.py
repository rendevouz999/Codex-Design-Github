#!/usr/bin/env python
"""Brain Design-native design simulation gate.

This is a MiroFish-style workflow adaptation for Brain Design:
seed material -> context graph -> agent panel -> simulation rounds -> verdict/report.

It does not import, bundle, execute, or depend on MiroFish or OASIS source code.
The layer is a local design review and quality-gate workflow, not a social or
public-opinion simulation engine.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from types import SimpleNamespace
from typing import Any

try:
    from design_brain_design_cognition_check import validate_cognition
    from design_brain_layout_similarity_audit import audit_candidate_against_many, load_json as load_layout_json
    from design_brain_intent_route import detect_intents
    from design_brain_modules import build_selection, explicit_web_deck_intent
    from design_brain_website_types import normalize_for_routing, select_website_product_type

    ROUTER_IMPORT_ERROR: Exception | None = None
except Exception as exc:  # pragma: no cover - emergency fallback path
    validate_cognition = None
    audit_candidate_against_many = None
    load_layout_json = None
    detect_intents = None
    build_selection = None
    explicit_web_deck_intent = None
    normalize_for_routing = None
    select_website_product_type = None
    ROUTER_IMPORT_ERROR = exc


SCHEMA_ID = "design-brain.design-simulation.verdict.v2"
VERSION = "2.5.0"
AGENT_SOURCE_REL = ".design-brain/design-simulation/agents.json"
SCHEMA_REL = ".design-brain/design-simulation/verdict-schema.json"

SAFE_ANTI_COPY_PHRASES = (
    "do-not-copy exact layout",
    "do-not-copy exact colors",
    "do-not-copy exact color",
    "do-not-copy exact palette",
    "do-not-copy exact image",
    "do-not-copy exact composition",
    "do not copy exact layout",
    "do not copy exact colors",
    "do not copy exact color",
    "do not copy exact palette",
    "do not copy exact composition",
    "avoid copying exact layout",
    "avoid copying exact palette",
    "avoid copying exact composition",
    "do-not-clone",
    "do not clone",
    "originality boundary",
    "anti-copy boundary",
)

RISKY_COPY_PHRASES = (
    "copy exact layout",
    "copy exact layout and colors",
    "copy exact colors",
    "clone this design",
    "match exactly",
    "recreate exact same",
    "duplicate this page",
    "duplicate the same page composition",
    "same layout and colors",
    "pixel-perfect clone",
    "pixel perfect clone",
    "pixel-perfect same",
    "pixel perfect same",
    "copy the reference exactly",
    "use exact same composition",
    "use exact same layout and palette",
)

MODE_PROFILES: dict[str, dict[str, Any]] = {
    "website": {
        "minimumUnits": 9,
        "required": ("hero", "proof", "service", "process", "testimonial", "cta", "footer"),
        "axes": ("section depth", "conversion flow", "proof/trust", "visual richness", "marketplace preview value"),
    },
    "landing": {
        "minimumUnits": 7,
        "required": ("hero", "problem", "benefit", "proof", "faq", "cta"),
        "axes": ("focused action", "objection handling", "proof/trust", "CTA rhythm", "visual richness"),
    },
    "dashboard": {
        "minimumUnits": 6,
        "required": ("kpi", "chart", "table", "filter", "state", "role"),
        "axes": ("KPI hierarchy", "chart/table density", "filters/search", "states", "task efficiency"),
    },
    "presentation": {
        "minimumUnits": 7,
        "required": ("cover", "agenda", "problem", "data", "comparison", "closing", "master"),
        "axes": ("slide role matrix", "master consistency", "data readability", "narrative flow", "export compatibility"),
    },
    "web-deck": {
        "minimumUnits": 8,
        "required": ("cover", "agenda", "section divider", "data", "closing", "stage", "reveal", "motion", "navigation"),
        "axes": ("slide role matrix", "stage fidelity", "motion signature", "reveal choreography", "runtime navigation"),
    },
    "brand-kit": {
        "minimumUnits": 6,
        "required": ("logo", "color", "typography", "application", "do", "dont"),
        "axes": ("logo usage", "color roles", "type pairing", "application examples", "do/don't rules"),
    },
    "ui-kit": {
        "minimumUnits": 6,
        "required": ("token", "component", "variant", "state", "accessibility", "naming"),
        "axes": ("token system", "component variants", "component states", "naming", "accessibility states"),
    },
    "ecommerce": {
        "minimumUnits": 8,
        "required": ("collection", "category", "product", "card", "shipping", "returns", "cart"),
        "axes": ("product/category logic", "product cards", "trust/shipping/returns", "cart/checkout", "merchandising"),
    },
    "mobile-app": {
        "minimumUnits": 6,
        "required": ("screen", "navigation", "state", "task", "onboarding", "component"),
        "axes": ("screen flow", "navigation", "task completion", "states", "mobile source hygiene"),
    },
    "email-newsletter": {
        "minimumUnits": 5,
        "required": ("email", "mobile stack", "alt text", "unsubscribe", "cta"),
        "axes": ("email client compatibility", "mobile stack", "alt text", "deliverability", "CTA block"),
    },
    "static-canvas": {
        "minimumUnits": 5,
        "required": ("format", "headline", "safe margin", "export", "readability"),
        "axes": ("visual hierarchy", "safe margins", "crop/export", "readability", "brand consistency"),
    },
    "document-report": {
        "minimumUnits": 6,
        "required": ("cover", "contents", "section", "table", "figure", "pdf"),
        "axes": ("document hierarchy", "page rhythm", "table clarity", "PDF export", "source hygiene"),
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Brain Design v2.5.0 design simulation.")
    parser.add_argument("--task", default="")
    parser.add_argument("--template-type", default="")
    parser.add_argument("--niche", default="")
    parser.add_argument("--target-buyer", default="")
    parser.add_argument("--visual-mood", default="")
    parser.add_argument("--marketplace", default="Envato")
    parser.add_argument("--mode", default="", help="Explicit output mode override for simulation routing.")
    parser.add_argument("--module", default="", help="Explicit Brain Design module override.")
    parser.add_argument("--product-family", default="", help="Explicit product family override.")
    parser.add_argument("--website-type", default="", help="Explicit website product type override.")
    parser.add_argument("--output-contract", default="", help="Explicit output contract or medium contract.")
    parser.add_argument("--proposed-structure", required=True)
    parser.add_argument("--reference-summary", default="")
    parser.add_argument("--prior-fingerprint", action="append", default=[])
    parser.add_argument("--prior-fingerprint-file", action="append", default=[])
    parser.add_argument("--reference-layout-fingerprint", default="", help="Reference layout fingerprint JSON for layout originality simulation context.")
    parser.add_argument("--candidate-layout-fingerprint", default="", help="Candidate layout fingerprint JSON for layout originality simulation context.")
    parser.add_argument("--previous-ai-fingerprint", action="append", default=[], help="Previous locked AI layout fingerprint JSON for pairwise layout risk.")
    parser.add_argument("--layout-audit-status", default="", help="Optional precomputed layout audit status: PASS, REVISE_REQUIRED, BLOCKED.")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--agents", default="", help="Optional agents.json path; defaults to Design Brain agent source.")
    parser.add_argument("--cognition-receipt", default="", help="Optional Design Cognition Receipt JSON path for reference-led/template simulations.")
    parser.add_argument("--require-cognition", action="store_true", help="Require a valid Design Cognition Receipt for this simulation.")
    parser.add_argument("--allow-missing-cognition", action="store_true", help="Debug only: record missing cognition but keep the run non-final/non-PASS.")
    parser.add_argument("--allow-default-agents", action="store_true")
    parser.add_argument("--no-strict-envato", action="store_true")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug[:64] or "design-simulation"


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9%+-]+", " ", value.lower())).strip()


def text_blob(args: argparse.Namespace) -> str:
    return "\n".join(
        [
            args.task,
            args.template_type,
            args.niche,
            args.target_buyer,
            args.visual_mood,
            args.marketplace,
            args.proposed_structure,
            args.reference_summary,
        ]
    )


def route_text_blob(args: argparse.Namespace) -> str:
    return "\n".join(
        [
            args.task,
            args.template_type,
            args.niche,
            args.target_buyer,
            args.visual_mood,
            args.marketplace,
            args.output_contract,
        ]
    )


def load_agents(root: Path, allow_default: bool = False, agents_path: str = "") -> tuple[list[dict[str, Any]], str]:
    if agents_path:
        path = Path(agents_path).expanduser()
        if not path.is_absolute():
            path = root / path
        source_label = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
    else:
        path = root / AGENT_SOURCE_REL
        source_label = AGENT_SOURCE_REL
    if not path.exists():
        if allow_default:
            return [
                {
                    "id": "default_reviewer",
                    "name": "Default Design Reviewer",
                    "role": "Emergency fallback reviewer.",
                    "focus": "General design quality",
                    "evaluation_axes": ["structure", "visual quality", "source hygiene"],
                    "vote_rules": "Vote based on blockers.",
                    "repair_behavior": "Request concrete repair actions.",
                }
            ], "default emergency agents"
        raise SystemExit(f"ERROR: required agent source not found: {source_label}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: {source_label} is invalid JSON: {exc}") from exc
    agents = payload.get("agents")
    if not isinstance(agents, list) or not agents:
        raise SystemExit(f"ERROR: {source_label} must contain a non-empty agents array.")
    for index, agent in enumerate(agents, start=1):
        missing = [
            key
            for key in ("id", "name", "role", "focus")
            if not isinstance(agent.get(key), str) or not agent.get(key, "").strip()
        ]
        has_axes = isinstance(agent.get("checklist"), list) or isinstance(agent.get("evaluation_axes"), list)
        has_vote = isinstance(agent.get("vote_rules"), str) or isinstance(agent.get("verdict_behavior"), str)
        if missing or not has_axes or not has_vote:
            raise SystemExit(
                f"ERROR: agent #{index} in {source_label} is invalid; "
                f"missing={missing}, has_axes={has_axes}, has_vote={has_vote}"
            )
    return agents, source_label


def short_summary(value: Any, max_length: int = 220) -> str:
    if isinstance(value, dict):
        text = "; ".join(f"{key}: {short_summary(item, 80)}" for key, item in value.items() if item not in (None, "", [], {}))
    elif isinstance(value, list):
        text = "; ".join(str(item) for item in value if str(item).strip())
    else:
        text = str(value or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_length]


def load_cognition_receipt(root: Path, receipt_path: str = "") -> dict[str, Any]:
    if not receipt_path:
        return {
            "status": "not_provided",
            "validationStatus": "not_provided",
            "receiptPath": "",
            "missingFields": [],
            "riskCategories": [],
            "requiredRepairs": [],
            "warnings": ["No Design Cognition Receipt was provided to this simulation run."],
            "styleDNA": "",
            "colorRoleRemapping": "",
            "referenceBoundary": "",
            "structuralReconfiguration": "",
            "patternDivergence": "",
            "sectionLogic": "",
            "marketplaceReadiness": "",
        }
    path = Path(receipt_path).expanduser()
    if not path.is_absolute():
        path = root / path
    label = path.relative_to(root).as_posix() if path.exists() and path.is_relative_to(root) else str(path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "status": "FAIL",
            "validationStatus": "FAIL",
            "receiptPath": label,
            "missingFields": [],
            "riskCategories": ["invalid_receipt"],
            "requiredRepairs": [f"Provide a valid JSON Design Cognition Receipt: {exc}"],
            "warnings": [f"Design Cognition Receipt could not be read: {exc}"],
            "styleDNA": "",
            "colorRoleRemapping": "",
            "referenceBoundary": "",
            "structuralReconfiguration": "",
            "patternDivergence": "",
            "sectionLogic": "",
            "marketplaceReadiness": "",
        }
    if validate_cognition is None:
        validation = {
            "status": "FAIL",
            "missingFields": [],
            "riskCategories": ["cognition_checker_unavailable"],
            "requiredRepairs": ["Fix design_brain_design_cognition_check import before simulation/build."],
        }
    else:
        validation = validate_cognition(payload)
    validation_status = str(validation.get("status") or "FAIL").upper()
    repairs = [str(item) for item in validation.get("requiredRepairs", [])]
    risks = [str(item) for item in validation.get("riskCategories", [])]
    missing = [str(item) for item in validation.get("missingFields", [])]
    return {
        "status": "PASS" if validation_status == "PASS" else "FAIL",
        "validationStatus": validation_status,
        "receiptPath": label,
        "missingFields": missing,
        "riskCategories": risks,
        "requiredRepairs": repairs,
        "warnings": [] if validation_status == "PASS" else [f"Design Cognition Receipt validation failed: {', '.join(risks or missing or ['invalid_receipt'])}."],
        "styleDNA": short_summary(payload.get("styleDNA", {})),
        "colorRoleRemapping": short_summary(payload.get("colorRoleRemapping", {})),
        "referenceBoundary": short_summary(payload.get("referenceBoundary", {})),
        "structuralReconfiguration": short_summary(payload.get("structuralReconfiguration", {})),
        "patternDivergence": short_summary(payload.get("patternDivergence", {})),
        "sectionLogic": short_summary(payload.get("sectionLogic", {})),
        "marketplaceReadiness": short_summary(payload.get("marketplaceReadiness", {})),
    }


def load_layout_originality(args: argparse.Namespace) -> dict[str, Any]:
    result: dict[str, Any] = {
        "layoutOriginalityStatus": "not_provided",
        "referenceLayoutRisk": "not_provided",
        "aiPairwiseLayoutRisk": "not_provided",
        "referenceAudit": {},
        "aiPairwiseAudit": {},
        "requiredLayoutRepairs": [],
        "warnings": [],
    }
    explicit_status = str(getattr(args, "layout_audit_status", "") or "").strip().upper()
    if explicit_status:
        if explicit_status in {"PASS", "REVISE_REQUIRED", "BLOCKED"}:
            result["layoutOriginalityStatus"] = explicit_status
            result["referenceLayoutRisk"] = "precomputed"
            result["aiPairwiseLayoutRisk"] = "precomputed"
            if explicit_status != "PASS":
                result["requiredLayoutRepairs"].append("Resolve precomputed layout originality audit failure before build/finalization.")
            return result
        result["layoutOriginalityStatus"] = "BLOCKED"
        result["requiredLayoutRepairs"].append(f"Invalid layout audit status: {explicit_status}")
        return result

    candidate_path = str(getattr(args, "candidate_layout_fingerprint", "") or "").strip()
    reference_path = str(getattr(args, "reference_layout_fingerprint", "") or "").strip()
    previous_paths = [str(path) for path in getattr(args, "previous_ai_fingerprint", []) if str(path).strip()]
    if not candidate_path and not reference_path and not previous_paths:
        result["warnings"].append("No layout originality fingerprints were provided to simulation.")
        return result
    if audit_candidate_against_many is None or load_layout_json is None:
        result["layoutOriginalityStatus"] = "BLOCKED"
        result["requiredLayoutRepairs"].append("Layout similarity audit module is unavailable.")
        return result
    if not candidate_path:
        result["layoutOriginalityStatus"] = "BLOCKED"
        result["requiredLayoutRepairs"].append("Candidate layout fingerprint is required when layout originality context is provided.")
        return result
    try:
        candidate = load_layout_json(Path(candidate_path).expanduser().resolve())
        statuses: list[str] = []
        repairs: list[str] = []
        if reference_path:
            reference = load_layout_json(Path(reference_path).expanduser().resolve())
            reference_audit = audit_candidate_against_many(candidate, [reference], "ai_vs_reference")
            result["referenceAudit"] = reference_audit
            result["referenceLayoutRisk"] = reference_audit.get("status", "not_provided")
            statuses.append(str(reference_audit.get("status", "")))
            repairs.extend(str(item) for item in reference_audit.get("requiredRepairs", []))
        if previous_paths:
            previous = [load_layout_json(Path(path).expanduser().resolve()) for path in previous_paths]
            pairwise = audit_candidate_against_many(candidate, previous, "ai_vs_ai")
            result["aiPairwiseAudit"] = pairwise
            result["aiPairwiseLayoutRisk"] = pairwise.get("status", "not_provided")
            statuses.append(str(pairwise.get("status", "")))
            repairs.extend(str(item) for item in pairwise.get("requiredRepairs", []))
        if any(status == "BLOCKED" for status in statuses):
            result["layoutOriginalityStatus"] = "BLOCKED"
        elif any(status == "REVISE_REQUIRED" for status in statuses):
            result["layoutOriginalityStatus"] = "REVISE_REQUIRED"
        elif statuses:
            result["layoutOriginalityStatus"] = "PASS"
        result["requiredLayoutRepairs"] = sorted(set(repairs))
        return result
    except Exception as exc:
        result["layoutOriginalityStatus"] = "BLOCKED"
        result["requiredLayoutRepairs"].append(f"Layout originality audit failed to run: {exc}")
        return result


MODULE_MODE_MAP = {
    "website-template": "website",
    "landing-page": "landing",
    "portfolio": "website",
    "dashboard": "dashboard",
    "presentation-deck": "presentation",
    "web-deck": "web-deck",
    "brand-kit": "brand-kit",
    "ui-kit": "ui-kit",
    "email-newsletter": "email-newsletter",
    "mobile-app": "mobile-app",
    "ecommerce": "ecommerce",
    "static-canvas": "static-canvas",
    "marketplace-preview": "static-canvas",
    "document-report": "document-report",
    "hero-header-kit": "website",
}

MODE_PRODUCT_FALLBACK = {
    "dashboard": "dashboard_template",
    "presentation": "presentation_deck",
    "web-deck": "web_deck_template",
    "brand-kit": "brand_identity_system",
    "ui-kit": "ui_component_system",
    "email-newsletter": "email_campaign_template",
    "mobile-app": "mobile_app_template",
    "document-report": "document_report_template",
    "static-canvas": "static_canvas_template",
    "landing": "landing_page_campaign",
    "ecommerce": "ecommerce_storefront",
    "website": "website_template",
}

NON_WEB_FALLBACK_TERMS = {
    "static-canvas": (
        "restaurant menu design",
        "menu design",
        "social media carousel",
        "social carousel",
        "facebook cover",
        "social media post",
        "instagram story",
        "poster",
        "flyer",
        "banner",
        "thumbnail",
        "cover design",
    ),
    "document-report": (
        "invoice template",
        "invoice design",
        "resume template",
        "resume design",
        "cv template",
        "document template",
        "report template",
        "certificate template",
        "booklet design",
    ),
}


def explicit_route_args(args: argparse.Namespace) -> bool:
    return any(
        str(getattr(args, name, "")).strip()
        for name in ("mode", "module", "product_family", "website_type", "output_contract")
    )


def fallback_infer_mode(args: argparse.Namespace) -> str:
    raw = normalize_text(f"{args.task} {args.template_type} {args.output_contract}")
    for mode, terms in NON_WEB_FALLBACK_TERMS.items():
        if any(term in raw for term in terms):
            return mode
    if any(term in raw for term in ("ui kit", "design system", "component library", "component set")):
        return "ui-kit"
    if any(term in raw for term in ("dashboard", "admin", "analytics", "kpi")):
        return "dashboard"
    if explicit_web_deck_intent is not None and explicit_web_deck_intent(raw):
        return "web-deck"
    if any(term in raw for term in ("ppt", "pptx", "presentation", "deck", "slides", "keynote")):
        return "presentation"
    if any(term in raw for term in ("brand kit", "brand identity", "logo system")):
        return "brand-kit"
    if any(term in raw for term in ("email newsletter", "newsletter email", "email template", "mailchimp")):
        return "email-newsletter"
    if any(term in raw for term in ("mobile app", "ios", "android", "app screen")):
        return "mobile-app"
    if any(term in raw for term in ("coffee product ecommerce", "toko online kopi", "ecommerce", "online store", "cart", "checkout")):
        return "ecommerce"
    if any(term in raw for term in ("landing page", "sales page", "waitlist")):
        return "landing"
    return "website"


def route_intents(args: argparse.Namespace) -> list[str]:
    if detect_intents is None:
        return []
    detector_args = SimpleNamespace(
        task=text_blob(args),
        has_reference=bool(args.reference_summary.strip()),
        needs_naming=False,
        needs_review=False,
        template_count=0,
    )
    try:
        return [rule.name for rule in detect_intents(detector_args)]
    except Exception:
        return []


def website_type_for_args(args: argparse.Namespace) -> str:
    if args.website_type.strip():
        return slugify(args.website_type)
    if select_website_product_type is None:
        return ""
    record = select_website_product_type(route_text_blob(args), repo_root())
    return str(record.get("id") or "") if record else ""


def fallback_product_family(args: argparse.Namespace, mode: str, website_type: str = "") -> str:
    if args.product_family.strip():
        return slugify(args.product_family)
    if mode in {"website", "landing", "ecommerce"} and website_type:
        return website_type
    if args.niche.strip():
        return slugify(args.niche)
    return MODE_PRODUCT_FALLBACK.get(mode, "website_template")


def resolve_simulation_route(args: argparse.Namespace) -> dict[str, Any]:
    warnings: list[str] = []
    input_task = text_blob(args)
    if explicit_route_args(args):
        mode = args.mode.strip() or MODULE_MODE_MAP.get(args.module.strip(), "") or fallback_infer_mode(args)
        module = args.module.strip() or next((key for key, value in MODULE_MODE_MAP.items() if value == mode), mode)
        website_type = args.website_type.strip() or (website_type_for_args(args) if mode in {"website", "landing", "ecommerce"} else "")
        return {
            "inputTask": input_task,
            "routeSource": "explicit_cli",
            "module": module,
            "mode": mode,
            "productFamily": fallback_product_family(args, mode, website_type),
            "websiteType": website_type,
            "intent": route_intents(args),
            "confidence": 1.0,
            "warnings": warnings,
            "rawRouterResult": {},
        }

    if build_selection is not None:
        selection = build_selection(
            task=args.task,
            template_type=args.template_type,
            niche=args.niche,
            target_buyer=args.target_buyer,
            visual_mood=args.visual_mood,
            root=repo_root(),
        )
        module = str(selection.get("moduleId") or "")
        mode = MODULE_MODE_MAP.get(module, "")
        if mode:
            website_type = website_type_for_args(args) if mode in {"website", "landing", "ecommerce"} else ""
            return {
                "inputTask": input_task,
                "routeSource": "brain_design_router",
                "module": module,
                "mode": mode,
                "productFamily": fallback_product_family(args, mode, website_type),
                "websiteType": website_type,
                "intent": route_intents(args),
                "confidence": 0.92,
                "warnings": [],
                "rawRouterResult": {
                    "moduleId": selection.get("moduleId", ""),
                    "seedPack": selection.get("seedPack", ""),
                    "directionPack": selection.get("directionPack", ""),
                    "productTypes": selection.get("productTypes", []),
                    "mediums": selection.get("mediums", []),
                },
            }
        warnings.append("Brain Design router returned no module; simulation fallback used.")
    else:
        warnings.append(f"Simulation route fallback used; verify Brain Design router availability. Import error: {ROUTER_IMPORT_ERROR}")

    mode = fallback_infer_mode(args)
    website_type = website_type_for_args(args) if mode in {"website", "landing", "ecommerce"} else ""
    return {
        "inputTask": input_task,
        "routeSource": "fallback",
        "module": mode,
        "mode": mode,
        "productFamily": fallback_product_family(args, mode, website_type),
        "websiteType": website_type,
        "intent": route_intents(args),
        "confidence": 0.55,
        "warnings": warnings or ["Simulation route fallback used; verify Brain Design router availability."],
        "rawRouterResult": {},
    }


def requires_cognition(args: argparse.Namespace, route: dict[str, Any]) -> bool:
    if getattr(args, "require_cognition", False):
        return True
    if getattr(args, "allow_missing_cognition", False):
        return False
    module = str(route.get("module") or "").lower()
    mode = str(route.get("mode") or "").lower()
    route_blob = normalize_text(" ".join([module, mode, str(route.get("productFamily") or ""), str(route.get("websiteType") or "")]))
    raw = normalize_text(
        "\n".join(
            [
                args.task,
                args.template_type,
                args.niche,
                args.target_buyer,
                args.visual_mood,
                args.proposed_structure,
                args.reference_summary,
            ]
        )
    )
    reference_terms = (
        "reference",
        "inspired",
        "inspired by",
        "like this",
        "based on reference",
        "from reference",
        "figma reference",
        "screenshot reference",
    )
    template_terms = (
        "template",
        "marketplace",
        "envato",
        "figma",
        "source",
        "editable",
        "build",
        "website template",
        "landing page",
        "dashboard",
        "presentation",
        "ui kit",
        "brand kit",
    )
    routed_template_modules = {
        "website-template",
        "landing-page",
        "ecommerce",
        "dashboard",
        "presentation-deck",
        "web-deck",
        "ui-kit",
        "brand-kit",
        "marketplace-preview",
        "email-newsletter",
        "mobile-app",
        "static-canvas",
        "document-report",
    }
    if module in routed_template_modules:
        return True
    if any(term in raw for term in reference_terms):
        return True
    if args.reference_summary.strip():
        return True
    if any(term in raw for term in template_terms):
        return True
    return any(term in route_blob for term in ("template", "marketplace", "figma", "source"))


def structure_units(structure: str) -> list[str]:
    chunks = re.split(r"(?:\n+|;|->|\||\s+[0-9]{1,2}[\).]\s+)", structure)
    return [" ".join(chunk.strip().split()) for chunk in chunks if len(normalize_text(chunk)) > 2]


def detect_copy_risk(reference_summary: str) -> dict[str, Any]:
    normalized = normalize_text(reference_summary)
    masked = normalized
    safe_hits = []
    for phrase in SAFE_ANTI_COPY_PHRASES:
        phrase_norm = normalize_text(phrase)
        if phrase_norm in masked:
            safe_hits.append(phrase)
            masked = masked.replace(phrase_norm, " anti copy boundary ")
    risky_hits = [phrase for phrase in RISKY_COPY_PHRASES if normalize_text(phrase) in masked]
    return {
        "hasCopyRisk": bool(risky_hits),
        "evidence": risky_hits,
        "safeAntiCopyEvidence": safe_hits,
    }


def count_hits(text: str, terms: tuple[str, ...]) -> int:
    normalized = normalize_text(text)
    return sum(1 for term in terms if normalize_text(term) in normalized)


def has_generic_sequence(structure: str) -> bool:
    normalized = normalize_text(structure)
    cursor = 0
    for item in ("hero", "features", "pricing", "faq", "cta"):
        index = normalized.find(item, cursor)
        if index < 0:
            return False
        cursor = index + len(item)
    return True


def prior_similarity(current: str, priors: list[str]) -> list[dict[str, Any]]:
    current_tokens = set(normalize_text(current).split())
    results = []
    for index, prior in enumerate(priors, start=1):
        prior_tokens = set(normalize_text(prior).split())
        overlap = len(current_tokens & prior_tokens) / max(1, len(current_tokens | prior_tokens))
        results.append({"priorIndex": index, "tokenOverlap": round(overlap, 4), "risk": "high" if overlap >= 0.33 else "low"})
    return results


def read_prior_fingerprints(args: argparse.Namespace) -> list[str]:
    values = list(args.prior_fingerprint or [])
    for item in args.prior_fingerprint_file or []:
        path = Path(item).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        try:
            values.append(path.read_text(encoding="utf-8"))
        except OSError as exc:
            values.append(f"UNREADABLE PRIOR FINGERPRINT: {exc}")
    return values


def evaluate(args: argparse.Namespace, agents: list[dict[str, Any]], mode: str, product_family: str) -> dict[str, Any]:
    profile = MODE_PROFILES.get(mode, MODE_PROFILES["website"])
    raw_text = text_blob(args)
    normalized = normalize_text(raw_text)
    units = structure_units(args.proposed_structure)
    unit_count = len(units)
    required = tuple(profile["required"])
    required_hits = count_hits(args.proposed_structure, required)
    copy_risk = detect_copy_risk(args.reference_summary)
    visual_hits = count_hits(raw_text, ("gradient", "shadow", "surface", "depth", "motif", "imagery", "gallery", "typography", "contrast"))
    source_hits = count_hits(raw_text, ("editable", "auto-layout", "auto layout", "component", "variant", "state", "placeholder", "layer", "documentation", "source hygiene"))
    preview_hits = count_hits(raw_text, ("cover", "preview", "thumbnail", "mockup", "section breakdown", "responsive spread", "package notes"))
    legal_hits = count_hits(raw_text, ("license", "attribution", "preview-only", "do-not-copy", "do not copy", "original", "reinterpret"))
    stage_hits = count_hits(raw_text, ("1920", "1080", "uniform scale", "letterbox", "reveal order", "motion signature", "reduced motion", "deep link", "keyboard", "slide per page"))

    blockers: list[str] = []
    required_repairs: list[str] = []
    recommended_improvements: list[str] = []
    minimum = int(profile["minimumUnits"])
    if unit_count < minimum:
        blockers.append(f"thin structure: {unit_count} units, expected at least {minimum} for {mode}.")
        required_repairs.append("Expand the structure with mode-specific sections, states, proof, preview, and source-template notes.")
    if has_generic_sequence(args.proposed_structure) and mode in {"website", "landing"}:
        blockers.append("generic scaffold: hero/features/pricing/FAQ/CTA sequence is too default for a marketplace template.")
        required_repairs.append("Replace the generic scaffold with product-family-specific section rhythm and proof logic.")
    if required_hits < max(3, min(len(required), 5)):
        blockers.append(f"section depth issue: missing enough {mode} anatomy signals ({required_hits}/{len(required)} required axes found).")
        required_repairs.append(f"Add {mode} anatomy: {', '.join(required)}.")
    if mode in {"website", "landing", "ecommerce"} and preview_hits < 2:
        blockers.append("marketplace value issue: preview/package value is under-specified.")
        required_repairs.append("Add cover, preview, responsive spread, section breakdown, and included-file notes.")
    if mode == "web-deck" and stage_hits < 4:
        blockers.append(f"web-deck stage/runtime issue: stage fidelity, motion signature, and runtime behavior are under-specified ({stage_hits}/10 stage signals found).")
        required_repairs.append("Add the fixed 1920x1080 stage with uniform scale and letterbox, a named motion signature, per-slide reveal order, keyboard and deep-link navigation, reduced motion, and one slide per printed page.")
    if copy_risk["hasCopyRisk"]:
        blockers.append("copy-risk blocker: " + "; ".join(copy_risk["evidence"]))
        required_repairs.append("Rewrite the reference instruction as transformed insight with a do-not-copy boundary.")
    if visual_hits < 2:
        recommended_improvements.append("Define visual mood, typography, color-role, imagery, and effect/depth direction before build.")
    if source_hits < 2:
        recommended_improvements.append("Add editable source-template hygiene: components, states, naming, placeholders, and documentation.")
    if "mirofish source" in normalized or "oasis runtime" in normalized:
        blockers.append("licensing/runtime blocker: Design Simulation Layer must not bundle or execute MiroFish/OASIS source.")
        required_repairs.append("Keep the layer as a Brain Design-native workflow adaptation only.")

    base = 100
    base -= max(0, minimum - unit_count) * 7
    base -= max(0, len(required) - required_hits) * 4
    base -= 18 if has_generic_sequence(args.proposed_structure) and mode in {"website", "landing"} else 0
    base -= 30 if copy_risk["hasCopyRisk"] else 0
    base += min(8, visual_hits * 2)
    base += min(8, source_hits * 2)
    base += min(8, preview_hits * 2)
    score = max(0, min(100, base))

    status = "PASS"
    if blockers or score < 78:
        status = "REVISE"
    if copy_risk["hasCopyRisk"] or len(blockers) >= 3 or score < 60:
        status = "BLOCKED"

    agent_votes = []
    for agent in agents:
        axes = agent.get("evaluation_axes") or agent.get("checklist") or []
        focus_text = normalize_text(" ".join([agent.get("focus", ""), agent.get("role", ""), " ".join(map(str, axes))]))
        agent_blockers = []
        agent_repairs = []
        agent_improvements = []
        agent_score = score
        if "copy" in focus_text or "legal" in focus_text or "original" in focus_text:
            if copy_risk["hasCopyRisk"]:
                agent_blockers.append("Reference instruction contains risky clone/exact-copy language.")
                agent_repairs.append("Convert exact-copy wording into transformed reference insight.")
            if legal_hits < 1:
                agent_improvements.append("Add license/originality/preview-only disclosure notes.")
        if "marketplace" in focus_text or "buyer" in focus_text or "preview" in focus_text:
            if preview_hits < 2 and mode in {"website", "landing", "ecommerce"}:
                agent_blockers.append("Marketplace preview value is too thin.")
            agent_improvements.append("Show buyer value through preview, source hygiene, and category-specific completeness.")
        if "source" in focus_text or "component" in focus_text or "auto" in focus_text:
            if source_hits < 2:
                agent_improvements.append("Add source hygiene, components, states, naming, and editable placeholders.")
        if "visual" in focus_text or "creative" in focus_text:
            if visual_hits < 2:
                agent_improvements.append("Add a stronger visual-language fingerprint.")
        if "section" in focus_text or "scaffold" in focus_text or "minimal" in focus_text:
            if unit_count < minimum or has_generic_sequence(args.proposed_structure):
                agent_blockers.append("Structure risks thin/generic scaffold output.")
                agent_repairs.append("Increase product-specific depth and break default section rhythm.")
        if mode == "web-deck" and ("motion" in focus_text or "stage" in focus_text or "visual" in focus_text or "component" in focus_text or "responsive" in focus_text):
            if stage_hits < 4:
                agent_blockers.append("Stage fidelity, motion signature, and runtime behavior are unproven for a browser-rendered deck.")
                agent_repairs.append("Specify the scaled stage, motion signature, reveal order, runtime navigation, reduced motion, and print output.")
        if agent_blockers:
            agent_score = min(agent_score, 58)
        agent_verdict = "PASS" if not agent_blockers and agent_score >= 78 else "REVISE"
        if agent_blockers and (copy_risk["hasCopyRisk"] or unit_count < minimum - 2):
            agent_verdict = "BLOCKED"
        if agent_verdict == "PASS":
            agent_required_repairs = []
            agent_recommended = agent_improvements[:5]
        else:
            agent_required_repairs = (agent_repairs or agent_improvements)[:5]
            agent_recommended = agent_improvements[len(agent_required_repairs) : len(agent_required_repairs) + 5]
        agent_votes.append(
            {
                "agentId": agent["id"],
                "agentName": agent["name"],
                "role": agent["role"],
                "focus": agent["focus"],
                "score": agent_score,
                "verdict": agent_verdict,
                "signals": [
                    f"Mode: {mode}",
                    f"Mode axes: {', '.join(profile['axes'])}",
                    f"Structure units: {unit_count}",
                    f"Required anatomy hits: {required_hits}/{len(required)}",
                ],
                "blockers": agent_blockers,
                "requiredRepairs": agent_required_repairs,
                "recommendedImprovements": agent_recommended,
            }
        )

    all_repairs = list(required_repairs)
    all_improvements = list(recommended_improvements)
    for vote in agent_votes:
        all_repairs.extend(vote["requiredRepairs"])
        all_improvements.extend(vote.get("recommendedImprovements", []))
    deduped_repairs = []
    seen = set()
    for repair in all_repairs:
        key = normalize_text(repair)
        if key and key not in seen:
            deduped_repairs.append(repair)
            seen.add(key)
    deduped_improvements = []
    improvement_seen = set()
    for item in all_improvements:
        key = normalize_text(item)
        if key and key not in improvement_seen and key not in seen:
            deduped_improvements.append(item)
            improvement_seen.add(key)

    if status == "PASS":
        blockers = []
        deduped_repairs = []
    elif not deduped_repairs:
        fallback_repair = deduped_improvements[0] if deduped_improvements else "Repair the plan until it satisfies the routed mode and product-family contract."
        deduped_repairs = [fallback_repair]
        deduped_improvements = [item for item in deduped_improvements if normalize_text(item) != normalize_text(fallback_repair)]

    scores = {
        "overall": score,
        "structureDepth": max(0, min(100, 100 - max(0, minimum - unit_count) * 12)),
        "modeCompleteness": max(0, min(100, int(required_hits / max(1, len(required)) * 100))),
        "visualLanguage": max(0, min(100, 48 + visual_hits * 10)),
        "sourceHygiene": max(0, min(100, 45 + source_hits * 10)),
        "marketplaceValue": max(0, min(100, 45 + preview_hits * 10)),
        "copySafety": 35 if copy_risk["hasCopyRisk"] else 100,
    }

    return {
        "status": status,
        "confidence": round(mean([scores["overall"], scores["modeCompleteness"], scores["copySafety"]]) / 100, 2),
        "scores": scores,
        "blockers": blockers,
        "requiredRepairs": deduped_repairs[:20],
        "recommendedImprovements": deduped_improvements[:20],
        "agentVotes": agent_votes,
        "copyRisk": copy_risk,
        "modeProfile": profile,
        "structureUnits": units,
        "productFamily": product_family,
        "mode": mode,
    }


def build_context_graph(args: argparse.Namespace, evaluation: dict[str, Any], prior: list[dict[str, Any]]) -> dict[str, Any]:
    routing = evaluation["routing"]
    nodes = [
        {"id": "UserRequest", "type": "seed", "label": args.task or args.template_type or "Design task"},
        {"id": "BrainDesignRoute", "type": "route", "label": routing.get("module") or routing.get("mode") or "unknown"},
        {"id": "RouteSource", "type": "route_source", "label": routing.get("routeSource", "unknown")},
        {"id": "ProductFamily", "type": "product_family", "label": evaluation["productFamily"]},
        {"id": "Medium", "type": "medium", "label": evaluation["mode"]},
        {"id": "TemplatePlan", "type": "plan", "label": f"{len(evaluation['structureUnits'])} units"},
        {"id": "BuyerPersona", "type": "buyer", "label": args.target_buyer or "unspecified"},
        {"id": "ReferenceDNA", "type": "reference", "label": "supplied" if args.reference_summary else "not supplied"},
        {"id": "StyleDNA", "type": "style", "label": args.visual_mood or "unspecified"},
        {"id": "DesignCognitionReceipt", "type": "cognition", "label": evaluation.get("cognition", {}).get("status", "not_provided")},
        {"id": "ColorRoleRemapping", "type": "cognition", "label": evaluation.get("cognition", {}).get("colorRoleRemapping") or "not supplied"},
        {"id": "ReferenceBoundary", "type": "cognition", "label": evaluation.get("cognition", {}).get("referenceBoundary") or "not supplied"},
        {"id": "VisualMood", "type": "visual_mood", "label": args.visual_mood or "unspecified"},
        {"id": "StructuralReconfiguration", "type": "structure", "label": f"{len(evaluation['structureUnits'])} units"},
        {"id": "SectionDepthRisk", "type": "risk", "label": "active" if any("thin structure" in b for b in evaluation["blockers"]) else "low"},
        {"id": "CopyRisk", "type": "risk", "label": "active" if evaluation["copyRisk"]["hasCopyRisk"] else "low"},
        {"id": "LayoutOriginalityGate", "type": "layout_originality", "label": evaluation.get("layoutOriginality", {}).get("layoutOriginalityStatus", "not_provided")},
        {"id": "ReferenceLayoutRisk", "type": "layout_originality", "label": evaluation.get("layoutOriginality", {}).get("referenceLayoutRisk", "not_provided")},
        {"id": "AiPairwiseLayoutRisk", "type": "layout_originality", "label": evaluation.get("layoutOriginality", {}).get("aiPairwiseLayoutRisk", "not_provided")},
        {"id": "MinimalistCollapseRisk", "type": "risk", "label": "checked"},
        {"id": "ScaffoldSimilarityRisk", "type": "risk", "label": "checked"},
        {"id": "MarketplaceValueRisk", "type": "risk", "label": "active" if any("marketplace" in b for b in evaluation["blockers"]) else "low"},
        {"id": "FigmaSourceHygieneRisk", "type": "risk", "label": "checked"},
        {"id": "AgentVerdict", "type": "verdict", "label": evaluation["status"]},
    ]
    if routing.get("routeSource") == "fallback":
        nodes.append({"id": "SimulationFallbackRoutingRisk", "type": "risk", "label": "active"})
    for index, repair in enumerate(evaluation["requiredRepairs"][:8], start=1):
        nodes.append({"id": f"RequiredRepair{index}", "type": "repair", "label": repair})
    for index, improvement in enumerate(evaluation["recommendedImprovements"][:8], start=1):
        nodes.append({"id": f"RecommendedImprovement{index}", "type": "improvement", "label": improvement})
    edges = [
        {"from": "UserRequest", "to": "BrainDesignRoute", "relationship": "requires"},
        {"from": "BrainDesignRoute", "to": "RouteSource", "relationship": "supports"},
        {"from": "BrainDesignRoute", "to": "ProductFamily", "relationship": "requires"},
        {"from": "BrainDesignRoute", "to": "Medium", "relationship": "requires"},
        {"from": "UserRequest", "to": "ProductFamily", "relationship": "requires"},
        {"from": "UserRequest", "to": "Medium", "relationship": "requires"},
        {"from": "UserRequest", "to": "TemplatePlan", "relationship": "transforms"},
        {"from": "ReferenceDNA", "to": "StyleDNA", "relationship": "supports"},
        {"from": "StyleDNA", "to": "DesignCognitionReceipt", "relationship": "requires"},
        {"from": "DesignCognitionReceipt", "to": "ColorRoleRemapping", "relationship": "requires"},
        {"from": "DesignCognitionReceipt", "to": "ReferenceBoundary", "relationship": "requires"},
        {"from": "StyleDNA", "to": "VisualMood", "relationship": "transforms"},
        {"from": "ProductFamily", "to": "StructuralReconfiguration", "relationship": "requires"},
        {"from": "StructuralReconfiguration", "to": "SectionDepthRisk", "relationship": "risks"},
        {"from": "ReferenceDNA", "to": "CopyRisk", "relationship": "risks"},
        {"from": "ReferenceDNA", "to": "LayoutOriginalityGate", "relationship": "audits"},
        {"from": "LayoutOriginalityGate", "to": "ReferenceLayoutRisk", "relationship": "checks"},
        {"from": "LayoutOriginalityGate", "to": "AiPairwiseLayoutRisk", "relationship": "checks"},
        {"from": "LayoutOriginalityGate", "to": "AgentVerdict", "relationship": "blocks_or_repairs"},
        {"from": "StructuralReconfiguration", "to": "ScaffoldSimilarityRisk", "relationship": "resembles"},
        {"from": "SectionDepthRisk", "to": "AgentVerdict", "relationship": "blocks"},
        {"from": "CopyRisk", "to": "AgentVerdict", "relationship": "blocks"},
        {"from": "MarketplaceValueRisk", "to": "AgentVerdict", "relationship": "risks"},
    ]
    for index in range(1, min(8, len(evaluation["requiredRepairs"])) + 1):
        edges.append({"from": f"RequiredRepair{index}", "to": "AgentVerdict", "relationship": "repairs"})
    for index in range(1, min(8, len(evaluation["recommendedImprovements"])) + 1):
        edges.append({"from": f"RecommendedImprovement{index}", "to": "AgentVerdict", "relationship": "supports"})
    if routing.get("routeSource") == "fallback":
        edges.append({"from": "SimulationFallbackRoutingRisk", "to": "AgentVerdict", "relationship": "risks"})
    return {"nodes": nodes, "edges": edges, "priorFingerprintComparisons": prior}


def artifact_dir(args: argparse.Namespace, run_id: str) -> Path:
    if args.output_dir:
        path = Path(args.output_dir).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.resolve()
    return repo_root() / ".design-brain" / "context-packets" / "design-sim" / run_id


def build_verdict(args: argparse.Namespace, agents: list[dict[str, Any]], agent_source: str) -> dict[str, Any]:
    routing = resolve_simulation_route(args)
    mode = str(routing["mode"])
    product_family = str(routing["productFamily"])
    cognition = load_cognition_receipt(repo_root(), args.cognition_receipt)
    cognition_required = requires_cognition(args, routing)
    cognition["required"] = cognition_required
    cognition["allowMissing"] = bool(getattr(args, "allow_missing_cognition", False))
    priors = read_prior_fingerprints(args)
    prior = prior_similarity(args.proposed_structure, priors)
    layout_originality = load_layout_originality(args)
    evaluation = evaluate(args, agents, mode, product_family)
    if cognition_required and cognition["status"] == "not_provided":
        cognition_issue = "Design Cognition Receipt is required before simulation/build for reference-led/template task."
        evaluation["blockers"].append(cognition_issue)
        evaluation["requiredRepairs"].append(cognition_issue)
        evaluation["status"] = "BLOCKED"
        evaluation["confidence"] = min(evaluation["confidence"], 0.55)
    elif getattr(args, "allow_missing_cognition", False) and cognition["status"] == "not_provided":
        cognition_issue = "Missing Design Cognition Receipt was explicitly allowed for debug only; this run cannot be considered final PASS."
        cognition["warnings"].append(cognition_issue)
        evaluation["requiredRepairs"].append("Provide a valid Design Cognition Receipt before build/finalization.")
        evaluation["status"] = "REVISE"
        evaluation["confidence"] = min(evaluation["confidence"], 0.7)
    elif cognition["status"] == "FAIL":
        cognition_issue = "Design Cognition Receipt failed validation; revise cognition before simulation/build."
        evaluation["blockers"].append(cognition_issue)
        repairs = cognition.get("requiredRepairs") or [cognition_issue]
        evaluation["requiredRepairs"].extend(str(item) for item in repairs)
        evaluation["status"] = "BLOCKED"
        evaluation["confidence"] = min(evaluation["confidence"], 0.58)
    if layout_originality["layoutOriginalityStatus"] in {"REVISE_REQUIRED", "BLOCKED"}:
        issue = "Sequential Layout Originality Gate reported layout similarity risk."
        if layout_originality["layoutOriginalityStatus"] == "BLOCKED":
            evaluation["blockers"].append(issue)
            evaluation["status"] = "BLOCKED"
            evaluation["confidence"] = min(evaluation["confidence"], 0.56)
        else:
            if evaluation["status"] == "PASS":
                evaluation["status"] = "REVISE"
            evaluation["confidence"] = min(evaluation["confidence"], 0.72)
        evaluation["requiredRepairs"].extend(layout_originality.get("requiredLayoutRepairs") or [issue])
    evaluation["routing"] = routing
    evaluation["cognition"] = cognition
    evaluation["layoutOriginality"] = layout_originality
    graph = build_context_graph(args, evaluation, prior)
    run_seed = json.dumps(
        {
            "task": args.task,
            "structure": args.proposed_structure,
            "reference": args.reference_summary,
            "time": now_iso(),
        },
        sort_keys=True,
    )
    run_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slugify(args.task or args.template_type)}-{hashlib.sha1(run_seed.encode()).hexdigest()[:8]}"
    out_dir = artifact_dir(args, run_id)
    manifest_path = out_dir / "manifest.json"
    report_path = out_dir / "report" / "report.md"
    verdict_path = out_dir / "report" / "design_verdict.json"
    status = evaluation["status"]
    verdict = {
        "schema": SCHEMA_ID,
        "version": VERSION,
        "runId": run_id,
        "artifactDir": str(out_dir),
        "verdict": status,
        "status": status,
        "confidence": evaluation["confidence"],
        "productFamily": product_family,
        "mode": mode,
        "routing": routing,
        "cognition": cognition,
        "layoutOriginality": layout_originality,
        "layoutOriginalityStatus": layout_originality["layoutOriginalityStatus"],
        "referenceLayoutRisk": layout_originality["referenceLayoutRisk"],
        "aiPairwiseLayoutRisk": layout_originality["aiPairwiseLayoutRisk"],
        "requiredLayoutRepairs": layout_originality["requiredLayoutRepairs"],
        "scores": evaluation["scores"],
        "blockers": evaluation["blockers"],
        "requiredRepairs": evaluation["requiredRepairs"],
        "recommendedImprovements": evaluation["recommendedImprovements"],
        "agentVotes": evaluation["agentVotes"],
        "agentSource": agent_source,
        "agentCount": len(agents),
        "manifestPath": str(manifest_path),
        "reportPath": str(report_path),
        "verdictPath": str(verdict_path),
        "designContextGraph": graph,
        "copyRisk": evaluation["copyRisk"],
        "modeProfile": evaluation["modeProfile"],
        "sourcePattern": "Brain Design-native MiroFish-style workflow adaptation; no MiroFish/OASIS runtime.",
        "generatedAt": now_iso(),
    }
    return verdict


def validate_verdict(verdict: dict[str, Any], schema_path: Path) -> None:
    required = {
        "runId",
        "artifactDir",
        "verdict",
        "status",
        "confidence",
        "productFamily",
        "mode",
        "scores",
        "blockers",
        "requiredRepairs",
        "recommendedImprovements",
        "routing",
        "cognition",
        "layoutOriginality",
        "agentVotes",
        "manifestPath",
        "reportPath",
        "verdictPath",
    }
    missing = sorted(required - set(verdict))
    if missing:
        raise SystemExit(f"ERROR: verdict missing required fields: {', '.join(missing)}")
    if verdict["verdict"] not in {"PASS", "REVISE", "BLOCKED"}:
        raise SystemExit(f"ERROR: invalid verdict value: {verdict['verdict']}")
    if not isinstance(verdict["scores"], dict) or not isinstance(verdict["agentVotes"], list):
        raise SystemExit("ERROR: verdict scores/agentVotes shape is invalid.")
    if not isinstance(verdict.get("routing"), dict):
        raise SystemExit("ERROR: verdict routing shape is invalid.")
    if not isinstance(verdict.get("cognition"), dict):
        raise SystemExit("ERROR: verdict cognition shape is invalid.")
    if not isinstance(verdict.get("layoutOriginality"), dict):
        raise SystemExit("ERROR: verdict layoutOriginality shape is invalid.")
    if verdict["verdict"] == "PASS":
        if verdict["blockers"]:
            raise SystemExit("ERROR: PASS verdict cannot contain blockers.")
        if verdict["requiredRepairs"]:
            raise SystemExit("ERROR: PASS verdict cannot contain requiredRepairs.")
    if verdict["verdict"] in {"REVISE", "BLOCKED"} and not verdict["requiredRepairs"]:
        raise SystemExit("ERROR: REVISE/BLOCKED verdict must include requiredRepairs.")
    if verdict["verdict"] == "BLOCKED" and not verdict["blockers"]:
        raise SystemExit("ERROR: BLOCKED verdict must include blockers.")
    if schema_path.exists():
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"ERROR: verdict schema is invalid JSON: {exc}") from exc
        schema_required = set(schema.get("required", []))
        missing_schema_fields = sorted(schema_required - set(verdict))
        if missing_schema_fields:
            raise SystemExit(f"ERROR: verdict does not satisfy schema required fields: {missing_schema_fields}")


def markdown_report(verdict: dict[str, Any], args: argparse.Namespace) -> str:
    def bullets(values: list[Any]) -> str:
        return "\n".join(f"- {value}" for value in values) if values else "- None"

    lines = [
        "# Design Simulation Verdict",
        "",
        f"Run ID: `{verdict['runId']}`",
        f"Verdict: **{verdict['verdict']}**",
        f"Confidence: {verdict['confidence']}",
        f"Mode: `{verdict['mode']}`",
        f"Product family: `{verdict['productFamily']}`",
        f"Route source: `{verdict['routing']['routeSource']}`",
        f"Module: `{verdict['routing']['module']}`",
        f"Website type: `{verdict['routing'].get('websiteType') or 'none'}`",
        f"Agent source: {verdict['agentSource']}",
        "",
        "## Routing",
        "",
        f"- Route source: {verdict['routing']['routeSource']}",
        f"- Module: {verdict['routing']['module']}",
        f"- Mode: {verdict['routing']['mode']}",
        f"- Product family: {verdict['routing']['productFamily']}",
        f"- Website type: {verdict['routing'].get('websiteType') or 'none'}",
        f"- Intent: {', '.join(verdict['routing'].get('intent') or []) or 'none'}",
        f"- Confidence: {verdict['routing']['confidence']}",
        "- Warnings:",
        bullets(verdict["routing"].get("warnings", [])),
        "",
        "## Design Cognition",
        "",
        f"- Receipt status: {verdict['cognition'].get('status')}",
        f"- Required: {verdict['cognition'].get('required')}",
        f"- Validation status: {verdict['cognition'].get('validationStatus')}",
        f"- Receipt path: {verdict['cognition'].get('receiptPath') or 'not provided'}",
        f"- Color Role Re-Mapping: {verdict['cognition'].get('colorRoleRemapping') or 'not supplied'}",
        f"- Reference Boundary: {verdict['cognition'].get('referenceBoundary') or 'not supplied'}",
        f"- Structural Reconfiguration: {verdict['cognition'].get('structuralReconfiguration') or 'not supplied'}",
        f"- Pattern Divergence: {verdict['cognition'].get('patternDivergence') or 'not supplied'}",
        f"- Section Logic: {verdict['cognition'].get('sectionLogic') or 'not supplied'}",
        f"- Marketplace Readiness: {verdict['cognition'].get('marketplaceReadiness') or 'not supplied'}",
        f"- Risk categories: {', '.join(verdict['cognition'].get('riskCategories') or []) or 'none'}",
        f"- Missing fields: {', '.join(verdict['cognition'].get('missingFields') or []) or 'none'}",
        "- Cognition warnings:",
        bullets(verdict["cognition"].get("warnings", [])),
        "",
        "## Sequential Layout Originality",
        "",
        f"- Layout originality status: {verdict['layoutOriginality'].get('layoutOriginalityStatus')}",
        f"- Reference layout risk: {verdict['layoutOriginality'].get('referenceLayoutRisk')}",
        f"- AI pairwise layout risk: {verdict['layoutOriginality'].get('aiPairwiseLayoutRisk')}",
        "- Required layout repairs:",
        bullets(verdict["layoutOriginality"].get("requiredLayoutRepairs", [])),
        "- Layout warnings:",
        bullets(verdict["layoutOriginality"].get("warnings", [])),
        "",
        "## Licensing Boundary",
        "",
        "This is a Brain Design-native MiroFish-style workflow adaptation. It does not bundle, copy, import, or execute MiroFish source code and it does not run OASIS or social/public-opinion simulation.",
        "",
        "## Input",
        "",
        f"- Task: {args.task or 'Not specified'}",
        f"- Template type: {args.template_type or 'Not specified'}",
        f"- Niche: {args.niche or 'Not specified'}",
        f"- Target buyer: {args.target_buyer or 'Not specified'}",
        f"- Visual mood: {args.visual_mood or 'Not specified'}",
        "",
        "## Blockers",
        "",
        bullets(verdict["blockers"]),
        "",
        "## Required Repairs",
        "",
        bullets(verdict["requiredRepairs"]),
        "",
        "## Recommended Improvements",
        "",
        bullets(verdict["recommendedImprovements"]),
        "",
        "## Agent Votes",
        "",
    ]
    for vote in verdict["agentVotes"]:
        lines.extend(
            [
                f"### {vote['verdict']} - {vote['agentName']} - {vote['score']}/100",
                "",
                f"Focus: {vote['focus']}",
                "",
                "Blockers:",
                bullets(vote["blockers"]),
                "",
                "Repairs:",
                bullets(vote["requiredRepairs"]),
                "",
            ]
        )
    return "\n".join(lines)


def write_artifacts(verdict: dict[str, Any], args: argparse.Namespace, report: str) -> None:
    out_dir = Path(verdict["artifactDir"])
    files: dict[str, str] = {
        "input/task.txt": args.task,
        "input/proposed_structure.txt": args.proposed_structure,
        "input/reference_summary.txt": args.reference_summary,
        "report/report.md": report,
        "report/revision_brief.md": "\n".join(f"- {item}" for item in verdict["requiredRepairs"]),
    }
    json_files: dict[str, Any] = {
        "manifest.json": {
            "runId": verdict["runId"],
            "createdAt": verdict["generatedAt"],
            "verdict": verdict["verdict"],
            "agentSource": verdict["agentSource"],
            "artifactDir": verdict["artifactDir"],
            "routing": verdict["routing"],
            "cognition": verdict["cognition"],
        },
        "graph/design_context_graph.json": verdict["designContextGraph"],
        "simulation/agent_panel.json": verdict["agentVotes"],
        "report/design_verdict.json": verdict,
    }
    for relative, text in files.items():
        path = out_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    for relative, payload in json_files.items():
        path = out_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    args = parse_args()
    root = repo_root()
    agents, agent_source = load_agents(root, args.allow_default_agents, args.agents)
    verdict = build_verdict(args, agents, agent_source)
    validate_verdict(verdict, root / SCHEMA_REL)
    report = markdown_report(verdict, args)
    if not args.dry_run:
        write_artifacts(verdict, args, report)
        if not args.json:
            print(f"Design simulation artifacts written: {verdict['artifactDir']}")
        else:
            print(f"Design simulation artifacts written: {verdict['artifactDir']}", file=sys.stderr)
    if args.json:
        print(json.dumps(verdict, indent=2, ensure_ascii=False))
    else:
        print(report)
    return 0 if verdict["verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

