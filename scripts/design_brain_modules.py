#!/usr/bin/env python
"""Shared module selection helpers for Design Brain."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from design_brain_presentation_route import artifact_intent

from design_brain_website_types import (
    editorial_website_intent,
    explicit_ecommerce_intent,
    explicit_email_newsletter_intent,
    explicit_landing_intent,
    hospitality_website_intent,
    normalize_for_routing,
    phrase_in_text,
    pricing_without_ecommerce_intent,
    website_intent,
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "design-brain"


def load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return fallback


def registry_path(root: Path | None = None) -> Path:
    base = root or repo_root()
    return base / ".design-brain" / "registry" / "modules.json"


def directions_path(root: Path | None = None) -> Path:
    base = root or repo_root()
    return base / ".design-brain" / "direction-packs" / "directions.json"


def load_registry(root: Path | None = None) -> dict[str, Any]:
    return load_json(registry_path(root), {"modules": []})


def load_directions(root: Path | None = None) -> dict[str, dict[str, Any]]:
    data = load_json(directions_path(root), {"directions": []})
    return {
        str(direction.get("id")): direction
        for direction in data.get("directions", [])
        if isinstance(direction, dict) and direction.get("id")
    }


def combined_task_text(
    task: str = "",
    template_type: str = "",
    niche: str = "",
    target_buyer: str = "",
    visual_mood: str = "",
) -> str:
    return " ".join([task, template_type, niche, target_buyer, visual_mood]).lower()


WEB_DECK_EXPLICIT_TERMS = (
    "web deck",
    "html deck",
    "html presentation",
    "web presentation",
    "browser deck",
    "animated deck",
    "animated slides",
    "animated presentation",
    "interactive deck",
    "slide deck html",
    "single file deck",
    "presenter deck",
    "webinar deck",
    "demo day deck",
    "deck to web",
    "ppt to web",
    "pptx to html",
    "convert deck to html",
    "self running deck",
    "deck html",
    "presentasi web",
    "presentasi html",
    "slide web",
    "slide animasi",
    "presentasi animasi",
    "deck browser",
    "deck interaktif",
    "ppt ke web",
    "ppt ke html",
    "pptx ke html",
    "ubah ppt jadi web",
    "presentasi satu file",
    "slide buat live",
    "deck buat webinar",
)


def explicit_web_deck_intent(text: str) -> bool:
    if artifact_intent(text) in {"native", "both"}:
        return False
    return any(phrase_in_text(term, text) for term in WEB_DECK_EXPLICIT_TERMS)


def score_module(module: dict[str, Any], text: str) -> int:
    if module.get("id") == "email-newsletter" and not explicit_email_newsletter_intent(text):
        return 0
    if module.get("id") == "web-deck" and not explicit_web_deck_intent(text):
        return 0
    if module.get("id") == "ecommerce" and not explicit_ecommerce_intent(text):
        return 0
    if module.get("id") == "portfolio":
        strict_portfolio_terms = (
            "portfolio",
            "portofolio",
            "case study",
            "selected works",
            "projects showcase",
            "personal brand",
            "creative profile",
            "designer portfolio",
            "developer portfolio",
            "photographer portfolio",
            "creator portfolio",
        )
        if not any(phrase_in_text(term, text) for term in strict_portfolio_terms):
            return 0
    score = 0
    for trigger in module.get("triggers", []):
        trigger_text = str(trigger).lower()
        if phrase_in_text(trigger_text, text):
            score += 10 + min(len(trigger_text.split()), 3)
    for product_type in module.get("productTypes", []):
        value = str(product_type).lower()
        if phrase_in_text(value, text):
            score += 6
    for medium in module.get("mediums", []):
        value = str(medium).replace("_", " ").lower()
        if phrase_in_text(value, text):
            score += 4
    return score


def explicit_website_template_scope(text: str, root: Path | None = None) -> bool:
    return website_intent(text, root) and not explicit_landing_intent(text, root)


def explicit_website_word(text: str) -> bool:
    return bool(
        re.search(
            r"\b(website|web|situs|situs web|template website|website template|web template|homepage|site)\b",
            text,
        )
    )


SPECIFIC_MODULE_IDS = {
    "dashboard",
    "ecommerce",
    "portfolio",
    "mobile-app",
    "ui-kit",
    "brand-kit",
    "presentation-deck",
    "web-deck",
    "marketplace-preview",
    "email-newsletter",
    "document-report",
    "static-canvas",
    "hero-header-kit",
}
MIN_SPECIFIC_MODULE_SCORE = 8


def module_by_id(modules: list[dict[str, Any]], module_id: str) -> dict[str, Any]:
    for module in modules:
        if module.get("id") == module_id:
            return module
    return {}


def select_module(
    task: str = "",
    template_type: str = "",
    niche: str = "",
    target_buyer: str = "",
    visual_mood: str = "",
    root: Path | None = None,
) -> dict[str, Any]:
    registry = load_registry(root)
    modules = [m for m in registry.get("modules", []) if isinstance(m, dict)]
    base = root or repo_root()
    raw_text = combined_task_text(task, template_type, niche, target_buyer, visual_mood)
    # Resolve requested artifacts before taxonomy aliases append terms like PPTX.
    artifact = artifact_intent(raw_text)
    if artifact in {"native", "both"}:
        return module_by_id(modules, "presentation-deck")
    if artifact == "web" or explicit_web_deck_intent(raw_text):
        return module_by_id(modules, "web-deck")
    text = normalize_for_routing(raw_text, base)
    scored = sorted(
        ((score_module(module, text), int(module.get("loadPriority", 999)), module) for module in modules),
        key=lambda item: (-item[0], item[1], str(item[2].get("id", ""))),
    )

    if explicit_email_newsletter_intent(text, base):
        email_module = module_by_id(modules, "email-newsletter")
        if email_module and score_module(email_module, text) > 0:
            return email_module

    if explicit_web_deck_intent(text):
        web_deck_module = module_by_id(modules, "web-deck")
        if web_deck_module and score_module(web_deck_module, text) > 0:
            return web_deck_module

    landing_module = module_by_id(modules, "landing-page")
    if explicit_landing_intent(text, base):
        landing_score = score_module(landing_module, text) if landing_module else 0
        if landing_score > 0:
            return landing_module

    raw_specific_text = raw_text
    raw_specific_scored = [
        (score_module(module, raw_specific_text), int(module.get("loadPriority", 999)), module)
        for module in modules
        if module.get("id") in {"static-canvas", "document-report"}
    ]
    raw_specific_scored = sorted(
        (item for item in raw_specific_scored if item[0] >= MIN_SPECIFIC_MODULE_SCORE),
        key=lambda item: (-item[0], item[1], str(item[2].get("id", ""))),
    )
    if raw_specific_scored:
        return raw_specific_scored[0][2]

    if hospitality_website_intent(text, base) and explicit_website_word(raw_text) and not explicit_ecommerce_intent(text, base):
        website_module = module_by_id(modules, "website-template")
        if website_module:
            return website_module

    if pricing_without_ecommerce_intent(text, base):
        website_module = module_by_id(modules, "website-template")
        if website_module and explicit_website_template_scope(text, base):
            return website_module
        if landing_module:
            return landing_module

    specific_scored = [
        item for item in scored if item[2].get("id") in SPECIFIC_MODULE_IDS and item[0] >= MIN_SPECIFIC_MODULE_SCORE
    ]
    if editorial_website_intent(text, base) and not explicit_email_newsletter_intent(text, base):
        website_module = module_by_id(modules, "website-template")
        if website_module:
            return website_module
    if specific_scored:
        return specific_scored[0][2]

    if explicit_website_template_scope(text, base):
        website_module = module_by_id(modules, "website-template")
        if website_module:
            return website_module

    if scored and scored[0][0] > 0:
        return scored[0][2]
    if landing_module:
        return landing_module
    return {}


def craft_paths(module: dict[str, Any]) -> list[str]:
    owned = {"pptx-readability", "pptx-frame-precision", "deck-motion", "web-deck-stage-fidelity"}
    return [f"skills/presentation-deck/design/craft/{craft}.md" if craft in owned else f".design-brain/craft/{craft}.md" for craft in module.get("requiredCraft", [])]


def seed_paths(module: dict[str, Any]) -> list[str]:
    seed = str(module.get("seedPack") or "")
    if not seed:
        return []
    base = f"skills/presentation-deck/resources/seed-packs/{seed}" if seed in {"presentation-deck", "web-deck"} else f".design-brain/seed-packs/{seed}"
    return [
        f"{base}/layouts.md",
        f"{base}/checklist.md",
        f"{base}/content-patterns.md",
        f"{base}/design-system-scope.md",
    ]


def direction_record(module: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    direction_id = str(module.get("directionPack") or "")
    return load_directions(root).get(direction_id, {})


def source_files_for_selection(module: dict[str, Any], figma_output: bool = False) -> list[str]:
    files = [
        ".design-brain/registry/modules.json",
        ".design-brain/MEDIUM_PRODUCT_PLAYBOOKS.md",
        ".design-brain/ADVANCED_STYLE_GRAMMAR_MATRIX.md",
        ".design-brain/HUMAN_CRAFT_HEURISTICS.md",
        ".design-brain/direction-packs/directions.json",
    ]
    files.extend(craft_paths(module))
    files.extend(seed_paths(module))
    if module.get("id") == "presentation-deck":
        files.append("skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md")
        files.append("skills/presentation-deck/workflows/native.md")
    if module.get("id") == "web-deck":
        files.append("skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md")
        files.append("skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md")
        files.append("skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md")
        files.append("skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md")
        files.append("skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md")
    if module.get("id") in {"marketplace-preview", "website-template", "landing-page", "portfolio", "ecommerce"}:
        files.append(".design-brain/ORIGINALITY_SIMILARITY_SCORECARD.md")
    if module.get("id") in {"website-template", "landing-page", "portfolio", "ecommerce", "dashboard"}:
        files.append(".design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.md")
        files.append(".design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.json")
        files.append(".design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md")
        files.append(".design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md")
    if figma_output or "figma-auto-layout" in module.get("requiredCraft", []):
        files.extend(
            [
                ".design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md",
                ".design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md",
                ".design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md",
                ".design-brain/VISUAL_CRITIQUE_CHECKLIST.md",
            ]
        )
    return unique(files)


def unique(items: list[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def build_selection(
    task: str = "",
    template_type: str = "",
    niche: str = "",
    target_buyer: str = "",
    visual_mood: str = "",
    root: Path | None = None,
) -> dict[str, Any]:
    base = root or repo_root()
    module = select_module(task, template_type, niche, target_buyer, visual_mood, base)
    direction = direction_record(module, base)
    text = normalize_for_routing(combined_task_text(task, template_type, niche, target_buyer, visual_mood), base)
    figma_output = bool(
        "figma" in text
        or "source template" in text
        or "editable template" in text
        or "editable source" in text
        or "design template di figma" in text
    )
    return {
        "moduleId": module.get("id", "unknown"),
        "additionalModules": ["web-deck"] if artifact_intent(task) == "both" else [],
        "capability": module.get("capability", module.get("id")),
        "outputMode": module.get("outputMode"),
        "kind": module.get("kind", "medium"),
        "mediums": module.get("mediums", []),
        "productTypes": module.get("productTypes", []),
        "requiredCraft": module.get("requiredCraft", []),
        "craftFiles": craft_paths(module),
        "seedPack": module.get("seedPack", ""),
        "seedFiles": seed_paths(module),
        "directionPack": module.get("directionPack", ""),
        "direction": direction,
        "validators": module.get("validators", []),
        "sourceInspiration": module.get("sourceInspiration", []),
        "sourceFiles": source_files_for_selection(module, figma_output=figma_output),
    }


def bullet(items: list[Any]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- None"
