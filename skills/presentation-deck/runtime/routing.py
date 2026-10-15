"""Presentation artifact disambiguation shared with the plugin hook via JSON."""
from __future__ import annotations

import json
import re
from pathlib import Path


def artifact_intent(text: str) -> str | None:
    rules = json.loads((Path(__file__).resolve().parents[3] / "skills/presentation-deck/resources/routing.json").read_text(encoding="utf-8"))
    value = " " + re.sub(r"[^a-z0-9&]+", " ", text.lower()).strip() + " "
    has = lambda terms: any(f" {term} " in value for term in terms)
    if re.search(rules["dualPattern"], value):
        return "both"
    if re.search(rules["toNativePattern"], value):
        return "native"
    if has(rules["nativeTerms"]):
        return "web" if has(rules["browserTerms"]) else "native"
    return None


def route_pptx(task: str, source_pptx: str = "") -> dict:
    artifact = artifact_intent(task)
    text = task.lower()
    if artifact in {"web", "both"}:
        return {"artifact": artifact, "route": "web-deck" if artifact == "web" else "presentation-and-web", "workflow": "skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md"}
    if any(term in text for term in ("keynote", "google slides", "figma")) and artifact != "native":
        return {"artifact": "other-slides", "route": "presentation-deck", "workflow": "skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md"}
    quick = bool(re.search(r"\b(quick|fast|cepat)\b|skip strategy|tanpa strategi", text))
    reusable = any(term in text for term in ("reusable", "workspace template", "template workspace", "buat template", "create template", "template brand", "template style", "template layout"))
    redesign = any(term in text for term in ("redesign", "desain ulang", "beautify", "percantik", "re-outline"))
    editing = any(term in text for term in ("edit", "fill", "isi", "notes", "catatan", "narration", "narasi", "animation", "animasi", "reorder", "urut", "tambahkan", "ganti", "ubah"))
    existing_source = bool(source_pptx or ".pptx" in text or re.search(r"\b(?:pptx?|powerpoint|deck|presentasi)\s+(?:ini|tersebut)\b|\b(?:this|existing)\s+(?:pptx?|powerpoint|deck|presentation)\b", text))
    route = "create-template" if reusable else "edit-native" if editing and existing_source and not redesign else "generate"
    profile = "quick" if quick else "default"
    if route == "generate" and any(term in text for term in ("beautify", "percantik")):
        profile = "beautify-quick" if quick else "beautify"
    authority = "workflows/create-template.md" if route == "create-template" else "workflows/edit-native-pptx.md" if route == "edit-native" else "workflows/profiles/beautify-pptx.md" if "beautify" in profile else "workflows/profiles/quick-generate.md" if quick else "workflows/generate-pptx.md"
    return {"artifact": "native", "route": route, "profile": profile if route == "generate" else None, "authority": authority, "workflow": "skills/presentation-deck/workflows/native.md", "sourcePptx": source_pptx or None, "sourceRequired": route == "edit-native" and not source_pptx}
