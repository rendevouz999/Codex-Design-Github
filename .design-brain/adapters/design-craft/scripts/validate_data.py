#!/usr/bin/env python3
"""Validate Design Craft data files."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
JSON_COLUMNS = {"Decision_Rules"}
REQUIRED_PRODUCT_FAMILIES = {
    "real_estate_property",
    "education_course",
    "medical_clinic",
    "beauty_wellness",
    "car_rental_transport",
    "email_newsletter",
    "fashion_apparel_ecommerce",
    "furniture_rental_service",
    "presentation_deck",
    "brand_kit",
    "static_canvas",
    "menu_design",
    "social_post",
    "ui_kit",
    "component_library",
    "design_system",
    "brochure_design",
    "print_collateral",
    "poster_design",
    "banner_design",
    "thumbnail_design",
    "invoice_template",
    "resume_template",
    "ticket_receipt_design",
    "letterhead_design",
    "price_list_design",
    "table_tent_design",
    "catalog_design",
    "lookbook_design",
    "cover_design",
    "voucher_coupon_design",
    "sticker_design",
    "postcard_design",
    "certificate_design",
    "booklet_design",
    "packaging_label_design",
    "label_design",
    "price_tag_design",
    "hang_tag_design",
}
RESTRICTED_PATTERNS = {
    "Hero + Features + CTA",
    "Minimal Single Column",
    "Minimal & Direct",
    "Minimalism",
    "Flat Design",
}


def _json_loads_with_duplicate_check(raw: str, source: str) -> object:
    duplicates: list[str] = []

    def hook(pairs):
        seen = {}
        for key, value in pairs:
            if key in seen:
                duplicates.append(key)
            seen[key] = value
        return seen

    value = json.loads(raw, object_pairs_hook=hook)
    if duplicates:
        names = ", ".join(sorted(set(duplicates)))
        raise ValueError(f"duplicate JSON keys in {source}: {names}")
    return value


def _looks_like_json(value: str) -> bool:
    stripped = value.strip()
    return (
        stripped.startswith('{"')
        or stripped.startswith("{'")
        or stripped.startswith("[")
        or stripped.startswith("{ ")
    )


def validate_csv_json_cells() -> list[str]:
    errors: list[str] = []
    for csv_path in sorted(DATA_DIR.rglob("*.csv")):
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row_number, row in enumerate(reader, start=2):
                for column, value in row.items():
                    if column not in JSON_COLUMNS:
                        continue
                    if not isinstance(value, str) or not _looks_like_json(value):
                        continue
                    source = f"{csv_path.relative_to(ROOT)} row {row_number} column {column}"
                    try:
                        parsed = _json_loads_with_duplicate_check(value, source)
                    except Exception as exc:  # noqa: BLE001 - validation should collect all failures
                        errors.append(f"{source}: {exc}")
                        continue
                    if isinstance(parsed, dict) and "must_have" in parsed:
                        must_have = parsed["must_have"]
                        if not isinstance(must_have, (str, list)):
                            errors.append(f"{source}: must_have must be a string or list")
    return errors


def validate_json_files() -> list[str]:
    errors: list[str] = []
    for json_path in sorted(DATA_DIR.rglob("*.json")):
        try:
            with json_path.open("r", encoding="utf-8") as f:
                json.load(f)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{json_path.relative_to(ROOT)}: {exc}")
    return errors


def validate_structure_depth() -> list[str]:
    errors: list[str] = []
    structure_path = DATA_DIR / "structure_patterns.json"
    depth_path = DATA_DIR / "product_depth_rules.json"
    if not structure_path.exists() or not depth_path.exists():
        return ["Missing structure_patterns.json or product_depth_rules.json"]
    structures = json.loads(structure_path.read_text(encoding="utf-8"))
    depth_rules = json.loads(depth_path.read_text(encoding="utf-8"))
    for family, pattern in structures.items():
        count = len(pattern.get("sections", []))
        rule = depth_rules.get(family, {})
        minimum = rule.get("min_sections") or rule.get("min_modules") or rule.get("min_screens") or rule.get("min_slides") or rule.get("min_blocks")
        if minimum and count < minimum:
            errors.append(f"{family}: {count} units but minimum is {minimum}")
        if pattern.get("sections") == ["Hero", "Features", "CTA"]:
            errors.append(f"{family}: forbidden Hero > Features > CTA pattern")
    return errors


def validate_safety_metadata() -> list[str]:
    errors: list[str] = []
    safety_path = DATA_DIR / "legacy_pattern_safety.json"
    if not safety_path.exists():
        return ["Missing legacy_pattern_safety.json"]
    safety = json.loads(safety_path.read_text(encoding="utf-8"))
    for name in RESTRICTED_PATTERNS:
        meta = safety.get(name)
        if not isinstance(meta, dict):
            errors.append(f"Missing safety metadata for {name}")
            continue
        if meta.get("scope") == "full_template_safe":
            errors.append(f"{name}: restricted pattern cannot be full_template_safe")
        for key in ["scope", "risk_level", "allowed_when", "forbidden_when", "recommended_replacement"]:
            if not meta.get(key):
                errors.append(f"{name}: safety metadata must include {key}")
    return errors


def validate_required_product_families() -> list[str]:
    errors: list[str] = []
    structure_path = DATA_DIR / "structure_patterns.json"
    depth_path = DATA_DIR / "product_depth_rules.json"
    structures = json.loads(structure_path.read_text(encoding="utf-8"))
    depth_rules = json.loads(depth_path.read_text(encoding="utf-8"))
    for family in sorted(REQUIRED_PRODUCT_FAMILIES):
        if family not in structures:
            errors.append(f"Missing structure pattern for {family}")
        if family not in depth_rules:
            errors.append(f"Missing depth rule for {family}")
    email = structures.get("email_newsletter", {})
    if email.get("unit_label") != "blocks":
        errors.append("email_newsletter must use blocks")
    return errors


def validate_aliases_and_extensions() -> list[str]:
    errors: list[str] = []
    aliases_path = DATA_DIR / "indonesian_aliases.json"
    example_path = DATA_DIR / "user_extensions.example.json"
    if not aliases_path.exists():
        errors.append("Missing indonesian_aliases.json")
    if not example_path.exists():
        errors.append("Missing user_extensions.example.json")
        return errors
    example = json.loads(example_path.read_text(encoding="utf-8"))
    if example.get("allow_override_safety") is not False:
        errors.append("user_extensions.example.json must disable safety override by default")
    for key in ["custom_product_families", "custom_style_guards", "custom_structure_patterns", "custom_aliases"]:
        if key not in example:
            errors.append(f"user_extensions.example.json missing {key}")
    return errors


def validate_mode_priority_and_gate_behavior() -> list[str]:
    errors: list[str] = []
    mode_path = DATA_DIR / "mode_priority_rules.json"
    anti_path = DATA_DIR / "anti_scaffold_rules.json"
    if not mode_path.exists():
        errors.append("Missing mode_priority_rules.json")
    else:
        mode_rules = json.loads(mode_path.read_text(encoding="utf-8"))
        priority = mode_rules.get("priority_order", [])
        for mode in [
            "invoice_template",
            "resume_template",
            "ticket_receipt_design",
            "certificate_design",
            "booklet_design",
            "cover_design",
            "packaging_label_design",
            "label_design",
            "sticker_design",
            "postcard_design",
            "price_tag_design",
            "hang_tag_design",
            "voucher_coupon_design",
            "letterhead_design",
            "price_list_design",
            "table_tent_design",
            "catalog_design",
            "lookbook_design",
            "brochure_design",
            "presentation",
            "email",
            "brand_kit",
            "menu_design",
            "social_post",
            "poster_design",
            "banner_design",
            "thumbnail_design",
            "print_collateral",
            "ui_kit",
            "component_library",
            "design_system",
            "landing",
        ]:
            if mode not in priority:
                errors.append(f"mode_priority_rules.json missing priority mode {mode}")
        if "website" in priority:
            website_index = priority.index("website")
            for mode in ["invoice_template", "resume_template", "ticket_receipt_design", "certificate_design", "booklet_design", "cover_design", "packaging_label_design", "label_design", "sticker_design", "postcard_design", "price_tag_design", "hang_tag_design", "voucher_coupon_design", "letterhead_design", "price_list_design", "table_tent_design", "catalog_design", "lookbook_design", "brochure_design", "print_collateral", "poster_design", "banner_design", "thumbnail_design", "social_post"]:
                if mode in priority and priority.index(mode) > website_index:
                    errors.append(f"{mode} must be prioritized before website")
            for mode in ["catalog_design", "lookbook_design", "packaging_label_design", "label_design", "price_tag_design", "hang_tag_design"]:
                if "website" in priority and mode in priority and priority.index(mode) > website_index:
                    errors.append(f"{mode} must beat ecommerce/website intent for design collateral queries")
    anti = json.loads(anti_path.read_text(encoding="utf-8")) if anti_path.exists() else {}
    behavior = anti.get("behavior", {})
    if behavior.get("block_on_fail") is not True:
        errors.append("anti_scaffold_rules.json must set block_on_fail true")
    if behavior.get("auto_repair") is not True:
        errors.append("anti_scaffold_rules.json must set auto_repair true")
    if behavior.get("persist_on_fail") is not False:
        errors.append("anti_scaffold_rules.json must set persist_on_fail false")
    return errors


def validate_mode_payload_data() -> list[str]:
    errors: list[str] = []
    modes = [
        "website",
        "landing",
        "presentation",
        "web_deck",
        "email",
        "brand_kit",
        "menu_design",
        "social_post",
        "static_canvas",
        "ui_kit",
        "component_library",
        "design_system",
        "dashboard",
        "mobile_app",
        "brochure_design",
        "print_collateral",
        "poster_design",
        "banner_design",
        "thumbnail_design",
        "invoice_template",
        "resume_template",
        "ticket_receipt_design",
        "letterhead_design",
        "price_list_design",
        "table_tent_design",
        "catalog_design",
        "lookbook_design",
        "cover_design",
        "voucher_coupon_design",
        "sticker_design",
        "postcard_design",
        "certificate_design",
        "booklet_design",
        "packaging_label_design",
        "label_design",
        "price_tag_design",
        "hang_tag_design",
    ]
    files = {
        "mode_style_profiles.json": ("profiles", ["style_name", "style_intent", "keywords", "effect_language"]),
        "mode_effect_language.json": ("effects", ["key_effects", "forbidden_terms"]),
        "mode_quality_checklists.json": ("checklists", []),
    }
    for filename, (root_key, required_keys) in files.items():
        path = DATA_DIR / filename
        if not path.exists():
            errors.append(f"Missing {filename}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        entries = data.get(root_key, {})
        for mode in modes:
            if mode not in entries:
                errors.append(f"{filename} missing mode {mode}")
                continue
            if isinstance(entries[mode], dict):
                for key in required_keys:
                    if key == "effect_language":
                        continue
                    if key not in entries[mode]:
                        errors.append(f"{filename} {mode} missing {key}")
            elif not entries[mode]:
                errors.append(f"{filename} {mode} must not be empty")
    guard_path = DATA_DIR / "style_payload_guards.json"
    if not guard_path.exists():
        errors.append("Missing style_payload_guards.json")
    else:
        guards = json.loads(guard_path.read_text(encoding="utf-8"))
        for key in ["restricted_minimal_payload_terms", "web_only_effect_terms", "web_modes", "non_web_modes"]:
            if not guards.get(key):
                errors.append(f"style_payload_guards.json missing {key}")
        if "Parallax" not in guards.get("web_only_effect_terms", []):
            errors.append("style_payload_guards.json must list presentation/web forbidden terms")
        for mode in ["website", "ecommerce", "landing", "web_deck"]:
            if mode not in guards.get("web_modes", []):
                errors.append(f"style_payload_guards.json web_modes missing {mode}")
        if set(guards.get("web_modes", [])) & set(guards.get("non_web_modes", [])):
            errors.append("style_payload_guards.json web_modes and non_web_modes must not overlap")
    landing_path = DATA_DIR / "niche_landing_patterns.json"
    if not landing_path.exists():
        errors.append("Missing niche_landing_patterns.json")
    else:
        patterns = json.loads(landing_path.read_text(encoding="utf-8")).get("patterns", {})
        for family in ["finance_consulting", "restaurant_hospitality", "equipment_rental_service", "beauty_wellness", "car_rental_transport", "fashion_apparel_ecommerce", "real_estate_property", "education_course"]:
            if family not in patterns:
                errors.append(f"niche_landing_patterns.json missing {family}")
    action_path = DATA_DIR / "mode_action_model.json"
    if not action_path.exists():
        errors.append("Missing mode_action_model.json")
    else:
        actions = json.loads(action_path.read_text(encoding="utf-8")).get("actions", {})
        for mode in modes + ["email_newsletter"]:
            action_key = "email_newsletter" if mode == "email" else mode
            if action_key not in actions:
                errors.append(f"mode_action_model.json missing mode {action_key}")
                continue
            model = actions[action_key]
            for key in ["primary_action_label", "action_goal", "allowed_terms", "forbidden_terms"]:
                if key not in model:
                    errors.append(f"mode_action_model.json {action_key} missing {key}")
        dashboard = actions.get("dashboard", {})
        joined_dashboard = " ".join(dashboard.get("allowed_terms", []) + [dashboard.get("action_goal", "")]).lower()
        if "data hierarchy" not in joined_dashboard or "states" not in joined_dashboard:
            errors.append("dashboard action model must use data/state language")
        for mode in ["email_newsletter", "menu_design", "social_post", "brand_kit", "static_canvas", "web_deck", "letterhead_design", "price_list_design", "table_tent_design", "catalog_design", "lookbook_design", "cover_design", "voucher_coupon_design", "sticker_design", "postcard_design", "certificate_design", "booklet_design", "packaging_label_design", "label_design", "price_tag_design", "hang_tag_design"]:
            model = actions.get(mode, {})
            if not model.get("allowed_terms"):
                errors.append(f"{mode} action model must have medium-specific allowed terms")
        for mode in ["catalog_design", "lookbook_design", "packaging_label_design", "label_design", "price_tag_design", "hang_tag_design"]:
            forbidden = " ".join(actions.get(mode, {}).get("forbidden_terms", [])).lower()
            if "cart" not in forbidden or "checkout" not in forbidden or "website sections" not in forbidden:
                errors.append(f"{mode} action model must forbid cart/checkout/website sections")
        web_deck_forbidden = " ".join(actions.get("web_deck", {}).get("forbidden_terms", [])).lower()
        if "website sections" not in web_deck_forbidden or "scroll-triggered" not in web_deck_forbidden or "export to pptx" not in web_deck_forbidden:
            errors.append("web_deck action model must forbid website/scroll/static-export language")
    action_notes_path = DATA_DIR / "niche_landing_action_notes.json"
    if not action_notes_path.exists():
        errors.append("Missing niche_landing_action_notes.json")
    else:
        notes = json.loads(action_notes_path.read_text(encoding="utf-8")).get("notes", {})
        for family in ["finance_consulting", "restaurant_hospitality", "equipment_rental_service", "beauty_wellness", "car_rental_transport", "fashion_apparel_ecommerce", "real_estate_property", "education_course"]:
            note = notes.get(family)
            if not isinstance(note, dict):
                errors.append(f"niche_landing_action_notes.json missing {family}")
                continue
            for key in ["conversion_goal", "cta_strategy", "avoid"]:
                if key not in note:
                    errors.append(f"niche_landing_action_notes.json {family} missing {key}")
    fallback_path = DATA_DIR / "mode_family_fallbacks.json"
    if not fallback_path.exists():
        errors.append("Missing mode_family_fallbacks.json")
    else:
        fallbacks = json.loads(fallback_path.read_text(encoding="utf-8")).get("fallbacks", {})
        for mode in modes + ["email_newsletter", "document_template"]:
            if mode in {"website", "landing", "web_deck"}:
                continue
            value = fallbacks.get(mode)
            if not value:
                errors.append(f"mode_family_fallbacks.json missing {mode}")
            elif value == "full_website_template":
                errors.append(f"mode_family_fallbacks.json {mode} must not use full_website_template")
    return errors


def validate_component_tokens() -> list[str]:
    errors: list[str] = []
    token_path = DATA_DIR / "component_tokens.json"
    if not token_path.exists():
        return ["Missing component_tokens.json"]
    tokens = json.loads(token_path.read_text(encoding="utf-8")).get("required_tokens", [])
    for token in [
        "--radius-button",
        "--radius-card",
        "--font-heading",
        "--font-body",
        "--brand-accent",
        "--surface-depth-low",
        "--modal-width-md",
    ]:
        if token not in tokens:
            errors.append(f"component_tokens.json missing {token}")
    return errors


def validate_json_safety_capability() -> list[str]:
    search_path = ROOT / "scripts" / "search.py"
    text = search_path.read_text(encoding="utf-8")
    required = [
        "safety_scope",
        "risk_level",
        "forbidden_when",
        "recommended_replacement",
        "is_restricted",
        "offending_terms",
        "mode_compatibility",
        "safety_metadata",
        "action_model",
        "forbidden_payload_terms",
        "sanitized_fields",
        "requires_sanitization",
    ]
    return [f"search.py missing JSON safety field {field}" for field in required if field not in text]


def validate_export_reliability() -> list[str]:
    export_path = ROOT / "scripts" / "export_design_craft.py"
    text = export_path.read_text(encoding="utf-8")
    required = ["TimeoutExpired", "proc.kill", "stdin=subprocess.DEVNULL", "subprocess.Popen", "timeout=", "STEP_TIMEOUTS", "--skip-tests", "--verbose", "print_step", "print_manual_progress", "--manual-timeout", "--command-timeout", "manual_deadline", "FAIL"]
    return [f"export_design_craft.py missing timeout/progress guard: {field}" for field in required if field not in text]


def validate_action_gate_wiring() -> list[str]:
    errors: list[str] = []
    design_system_path = ROOT / "scripts" / "design_system.py"
    text = design_system_path.read_text(encoding="utf-8")
    for required in [
        "MODE_ACTION_MODEL_FILE",
        "NICHE_LANDING_ACTION_NOTES_FILE",
        "sanitize_pattern_metadata_for_mode",
        "validate_action_payload",
        "repair",
        "dashboard_conversion_language_leak",
        "landing_csv_payload_leak",
        "wrong_medium_keyword_leak",
        "social_carousel_payload_leak",
        "instagram_story_wrong_mode",
        "letterhead_wrong_mode",
        "price_list_wrong_mode",
        "table_tent_wrong_mode",
        "catalog_wrong_mode",
        "lookbook_wrong_mode",
        "facebook_cover_block",
        "cover_wrong_mode",
        "voucher_wrong_mode",
        "coupon_wrong_mode",
        "gift_card_wrong_mode",
        "loyalty_card_wrong_mode",
        "sticker_wrong_mode",
        "postcard_wrong_mode",
        "certificate_wrong_mode",
        "booklet_wrong_mode",
        "packaging_label_wrong_mode",
        "label_wrong_mode",
        "price_tag_wrong_mode",
        "hang_tag_wrong_mode",
        "tag_ecommerce_leak",
        "packaging_label_website_leak",
        "web_modes",
        "web_deck",
        "forbidden effect language for mode",
        "manual_subprocess_timeout_not_killed",
    ]:
        if required not in text:
            errors.append(f"design_system.py missing action gate wiring: {required}")
    return errors


def validate_v026_routing_triggers() -> list[str]:
    text = (ROOT / "scripts" / "design_system.py").read_text(encoding="utf-8").lower()
    required = [
        "social media carousel",
        "social carousel",
        "instagram story",
        "ig story",
        "letterhead",
        "price list",
        "table tent",
        "product catalog design",
        "lookbook design",
    ]
    return [f"design_system.py missing v0.2.6 trigger: {trigger}" for trigger in required if trigger not in text]


def validate_v027_routing_triggers() -> list[str]:
    text = (ROOT / "scripts" / "design_system.py").read_text(encoding="utf-8").lower()
    required = [
        "facebook cover",
        "book cover",
        "gift voucher",
        "coupon design",
        "gift card",
        "loyalty card",
        "sticker design",
        "postcard design",
        "certificate template",
        "booklet design",
        "packaging label",
        "label design",
        "price tag",
        "hang tag",
    ]
    return [f"design_system.py missing v0.2.7 trigger: {trigger}" for trigger in required if trigger not in text]


def main() -> int:
    errors = []
    errors.extend(validate_json_files())
    errors.extend(validate_csv_json_cells())
    errors.extend(validate_structure_depth())
    errors.extend(validate_safety_metadata())
    errors.extend(validate_required_product_families())
    errors.extend(validate_aliases_and_extensions())
    errors.extend(validate_mode_priority_and_gate_behavior())
    errors.extend(validate_mode_payload_data())
    errors.extend(validate_component_tokens())
    errors.extend(validate_json_safety_capability())
    errors.extend(validate_action_gate_wiring())
    errors.extend(validate_v026_routing_triggers())
    errors.extend(validate_v027_routing_triggers())
    errors.extend(validate_export_reliability())

    if errors:
        print("FAIL: Design Craft data validation")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASS: Design Craft data validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
