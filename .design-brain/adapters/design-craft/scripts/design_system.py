#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Design System Generator - Aggregates search results and applies reasoning
to generate comprehensive design system recommendations.

Usage:
    from .design_system import generate_design_system
    result = generate_design_system("SaaS dashboard", "My Project")
    
    # With persistence (Master + Overrides pattern)
    result = generate_design_system("SaaS dashboard", "My Project", persist=True)
    result = generate_design_system("SaaS dashboard", "My Project", persist=True, page="dashboard")
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
# Allow both `python design_system.py ...` and `python -m ...` execution.
try:
    from core import DATA_DIR, normalize_query_for_design_craft, search, tokenize_query
except ImportError:  # pragma: no cover
    from .core import DATA_DIR, normalize_query_for_design_craft, search, tokenize_query


# ============ CONFIGURATION ============
REASONING_FILE = "ui-reasoning.csv"

SEARCH_CONFIG = {
    "product": {"max_results": 1},
    "style": {"max_results": 3},
    "color": {"max_results": 2},
    "landing": {"max_results": 2},
    "typography": {"max_results": 2}
}

PRODUCT_DEPTH_FILE = "product_depth_rules.json"
STRUCTURE_PATTERNS_FILE = "structure_patterns.json"
ANTI_SCAFFOLD_FILE = "anti_scaffold_rules.json"
LEGACY_PATTERN_SAFETY_FILE = "legacy_pattern_safety.json"
USER_EXTENSIONS_FILE = "user_extensions.local.json"
STYLE_PAYLOAD_GUARDS_FILE = "style_payload_guards.json"
MODE_STYLE_PROFILES_FILE = "mode_style_profiles.json"
MODE_EFFECT_LANGUAGE_FILE = "mode_effect_language.json"
MODE_QUALITY_CHECKLISTS_FILE = "mode_quality_checklists.json"
NICHE_LANDING_PATTERNS_FILE = "niche_landing_patterns.json"
MODE_ACTION_MODEL_FILE = "mode_action_model.json"
NICHE_LANDING_ACTION_NOTES_FILE = "niche_landing_action_notes.json"
MODE_FAMILY_FALLBACKS_FILE = "mode_family_fallbacks.json"

PRODUCT_AWARE_FALLBACK = {
    "pattern": "Product-specific marketplace structure required",
    "style_priority": [
        "Reference-led art direction",
        "Domain-appropriate visual identity",
        "Non-generic composition",
        "Marketplace-level section depth"
    ],
    "color_mood": "Domain-specific color role system",
    "typography_mood": "Product-appropriate hierarchy",
    "key_effects": "Semantic depth, contrast, and interaction polish",
    "anti_patterns": "Hero + Features + CTA default + Minimalism as fallback + Flat generic SaaS scaffold",
    "decision_rules": {
        "warning": "No exact design-craft corpus match found. Using product-aware fallback, not minimalist scaffold."
    },
    "severity": "HIGH"
}

FAMILY_STYLE_FALLBACKS = {
    "restaurant_hospitality": "Atmospheric Hospitality",
    "finance_consulting": "Trust-Led Professional",
    "equipment_rental_service": "Operational Service Booking",
    "ecommerce_storefront": "Commerce Storefront System",
    "jewelry_ecommerce": "Luxury Commerce",
    "luxury_furniture": "Editorial Interior Commerce",
    "agency_portfolio": "Expressive Studio",
    "dashboard_admin": "Data-Dense Operational System",
    "editorial_blog_cms": "Editorial Publishing",
    "saas_product_website": "Product-Led SaaS",
    "full_website_template": "Reference-Led Website",
    "landing_page": "Campaign Conversion",
    "mobile_app": "Mobile Flow System",
    "presentation_deck": "Narrative Slide System",
    "web_deck": "Motion Stage Deck System",
    "real_estate_property": "Property Listing Trust System",
    "education_course": "Learning Platform Clarity",
    "medical_clinic": "Clinical Trust System",
    "beauty_wellness": "Beauty Wellness Atmosphere",
    "car_rental_transport": "Transport Booking Utility",
    "email_newsletter": "Email Campaign System",
    "fashion_apparel_ecommerce": "Editorial Fashion Commerce",
    "furniture_rental_service": "Furniture Rental Booking",
    "brand_kit": "Identity System Craft",
    "static_canvas": "Static Canvas Hierarchy",
    "menu_design": "Hospitality Menu System",
    "social_post": "Social Content System",
    "ui_kit": "Interface Kit System",
    "component_library": "Component Library System",
    "design_system": "Token-Driven Design System",
    "brochure_design": "Brochure Information System",
    "print_collateral": "Print Collateral Hierarchy",
    "poster_design": "Poster Focal System",
    "banner_design": "Banner Message System",
    "thumbnail_design": "Thumbnail Hook System",
    "invoice_template": "Invoice Clarity System",
    "resume_template": "Resume Information Hierarchy",
    "ticket_receipt_design": "Order Ticket Receipt System",
    "letterhead_design": "Letterhead Identity System",
    "price_list_design": "Price List Scan System",
    "table_tent_design": "Table Tent Menu System",
    "catalog_design": "Catalog Browsing System",
    "lookbook_design": "Editorial Lookbook System",
    "cover_design": "Cover Visual System",
    "voucher_coupon_design": "Voucher Coupon Redemption System",
    "sticker_design": "Sticker Recognition System",
    "postcard_design": "Postcard Message System",
    "certificate_design": "Certificate Hierarchy System",
    "booklet_design": "Booklet Reading System",
    "packaging_label_design": "Packaging Label System",
    "label_design": "Label Design System",
    "price_tag_design": "Retail Price Tag System",
    "hang_tag_design": "Hang Tag Information System"
}

FAMILY_STYLE_KEYWORDS = {
    "dashboard_admin": ["Data-Dense Dashboard", "dashboard", "data dense"],
    "mobile_app": ["mobile", "app", "micro-interactions"],
    "presentation_deck": ["storytelling", "presentation", "narrative"],
    "restaurant_hospitality": ["restaurant", "hospitality", "atmospheric"],
    "finance_consulting": ["Trust & Authority", "professional", "finance"],
    "equipment_rental_service": ["booking", "service", "operational"],
    "agency_portfolio": ["creative agency", "portfolio", "expressive"],
    "editorial_blog_cms": ["editorial", "publishing", "magazine"],
    "jewelry_ecommerce": ["luxury", "ecommerce", "product"],
    "ecommerce_storefront": ["ecommerce", "product", "storefront"],
    "luxury_furniture": ["luxury", "interior", "furniture"],
    "real_estate_property": ["real estate", "property", "listing"],
    "education_course": ["course", "education", "learning"],
    "medical_clinic": ["clinic", "healthcare", "appointment"],
    "beauty_wellness": ["beauty", "wellness", "salon"],
    "car_rental_transport": ["car rental", "transport booking", "fleet"],
    "email_newsletter": ["email newsletter", "email template", "campaign"],
    "fashion_apparel_ecommerce": ["fashion", "apparel", "clothing", "lookbook"],
    "furniture_rental_service": ["furniture rental", "rental booking", "service"],
    "brand_kit": ["brand identity", "logo system", "identity"],
    "static_canvas": ["poster", "static canvas", "visual hierarchy"],
    "menu_design": ["menu design", "restaurant menu", "food menu"],
    "social_post": ["social media", "instagram", "carousel"],
    "ui_kit": ["ui kit", "interface kit", "components"],
    "component_library": ["component library", "variants", "states"],
    "design_system": ["design system", "tokens", "style guide"],
    "brochure_design": ["brochure", "service overview", "contact block", "print pdf"],
    "print_collateral": ["flyer", "print", "safe margin", "readability"],
    "poster_design": ["poster", "focal visual", "print export"],
    "banner_design": ["banner", "aspect ratio", "crop safety"],
    "thumbnail_design": ["thumbnail", "hook", "small-size readability"],
    "invoice_template": ["invoice", "item table", "totals", "payment"],
    "resume_template": ["resume", "cv", "experience", "ats"],
    "ticket_receipt_design": ["order ticket", "receipt", "quantity", "total"],
    "letterhead_design": ["letterhead", "logo placement", "contact info", "safe margin"],
    "price_list_design": ["price list", "price alignment", "category", "readability"],
    "table_tent_design": ["table tent", "front back", "fold", "qr", "print"],
    "catalog_design": ["catalog", "product grid", "spread", "print pdf"],
    "lookbook_design": ["lookbook", "editorial opener", "collection story", "image spread"],
    "cover_design": ["cover", "title hierarchy", "focal visual", "crop safety"],
    "voucher_coupon_design": ["voucher", "coupon", "gift card", "loyalty card", "redemption"],
    "sticker_design": ["sticker", "die-cut", "safe margin", "finish"],
    "postcard_design": ["postcard", "front back", "message", "print export"],
    "certificate_design": ["certificate", "recipient", "issuer", "signature", "seal"],
    "booklet_design": ["booklet", "spread", "page flow", "print pdf"],
    "packaging_label_design": ["packaging label", "product name", "variant", "barcode", "dieline"],
    "label_design": ["label", "shape", "brand product hierarchy", "material finish"],
    "price_tag_design": ["price tag", "price", "sku", "barcode", "die-cut"],
    "hang_tag_design": ["hang tag", "brand", "size", "material", "front back"],
}

STRICT_FAMILY_STYLE_FALLBACKS = {
    "real_estate_property",
    "education_course",
    "medical_clinic",
    "beauty_wellness",
    "car_rental_transport",
    "email_newsletter",
    "fashion_apparel_ecommerce",
    "furniture_rental_service",
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

MODE_DEPTH_RULES = {
    "landing": "landing_page",
    "web_deck": "presentation_deck",
}

PRESENTATION_TERMS = {
    "ppt", "pptx", "powerpoint", "presentation", "presentasi", "pitch deck",
    "slide deck", "slides", "google slides", "keynote", "deck template"
}
WEB_DECK_TERMS = {
    "web deck", "html deck", "html presentation", "web presentation", "browser deck",
    "animated deck", "animated slides", "animated presentation", "interactive deck",
    "slide deck html", "single file deck", "presenter deck", "webinar deck",
    "demo day deck", "deck to web", "ppt to web", "pptx to html",
    "convert deck to html", "self running deck", "deck html", "presentasi web",
    "presentasi html", "slide web", "slide animasi", "presentasi animasi",
    "deck browser", "deck interaktif", "ppt ke web", "ppt ke html", "pptx ke html",
    "ubah ppt jadi web", "presentasi satu file", "slide buat live", "deck buat webinar"
}
BRAND_KIT_TERMS = {
    "logo design", "brand identity", "branding", "visual identity", "brand kit",
    "brand guideline", "identity system", "logo system", "stationery", "kartu nama",
    "business card"
}
MENU_TERMS = {
    "menu design", "restaurant menu", "cafe menu", "food menu", "poster menu",
    "daftar menu", "menu restoran", "menu kafe"
}
SOCIAL_TERMS = {
    "social media post", "instagram post", "instagram carousel", "carousel post",
    "feed design", "story design", "reels cover", "social campaign", "social banner",
    "social media carousel", "social carousel", "carousel design", "ig carousel",
    "instagram story", "ig story", "feed post", "social media banner"
}
COVER_TERMS = {
    "cover design", "book cover", "ebook cover", "magazine cover", "report cover",
    "facebook cover", "social cover", "profile cover", "cover image", "cover banner"
}
VOUCHER_COUPON_TERMS = {
    "gift voucher", "restaurant voucher", "coupon", "coupon design", "promo coupon",
    "discount coupon", "gift card", "gift card design", "loyalty card",
    "loyalty card design", "membership card", "reward card", "voucher"
}
STICKER_TERMS = {
    "sticker", "sticker design", "label sticker", "packaging sticker",
    "brand sticker", "restaurant sticker"
}
POSTCARD_TERMS = {
    "postcard", "postcard design", "greeting card", "invitation card",
    "promo postcard", "restaurant postcard"
}
CERTIFICATE_TERMS = {
    "certificate", "certificate template", "award certificate", "diploma certificate",
    "sertifikat", "sertifikat template"
}
BOOKLET_TERMS = {
    "booklet", "booklet design", "mini brochure", "booklet template",
    "guide booklet", "finance booklet", "product booklet"
}
PACKAGING_LABEL_TERMS = {
    "packaging label", "packaging label design", "package label",
    "coffee packaging label", "product label", "bottle label", "jar label",
    "pouch label", "box label"
}
PRICE_TAG_TERMS = {
    "price tag", "price tag design", "fashion price tag", "retail price tag",
    "product price tag", "tag harga"
}
HANG_TAG_TERMS = {
    "hang tag", "hang tag design", "fashion hang tag", "clothing hang tag",
    "apparel tag", "swing tag", "retail hang tag"
}
LABEL_TERMS = {
    "label design", "label coffee", "coffee label", "product label design",
    "sticker label", "brand label"
}
LETTERHEAD_TERMS = {
    "letterhead", "letterhead design", "kop surat", "company letterhead",
    "business letterhead", "stationery letterhead", "finance letterhead"
}
PRICE_LIST_TERMS = {
    "price list", "pricelist", "price list design", "restaurant price list",
    "daftar harga", "price menu", "service price list", "menu price list"
}
TABLE_TENT_TERMS = {
    "table tent", "table tent menu", "tent card", "table card", "menu tent",
    "restaurant table tent", "table display menu", "tabletop menu"
}
CATALOG_TERMS = {
    "product catalog design", "catalog design", "catalogue design", "katalog produk",
    "product catalogue", "fashion catalog", "catalog template", "katalog fashion",
    "product catalog"
}
LOOKBOOK_TERMS = {
    "lookbook", "lookbook design", "fashion lookbook", "collection lookbook",
    "editorial lookbook", "style guide lookbook", "seasonal lookbook"
}
BROCHURE_TERMS = {
    "brochure", "brosur", "company profile", "company brochure", "product brochure",
    "service brochure", "restaurant brochure", "finance brochure", "brochure design",
    "desain brosur"
}
PRINT_COLLATERAL_TERMS = {
    "flyer", "flier", "leaflet", "pamphlet", "signage", "print design",
    "desain cetak", "flyer design"
}
POSTER_TERMS = {
    "poster", "poster design", "desain poster", "event poster", "food poster",
    "restaurant poster", "promo poster"
}
BANNER_TERMS = {
    "banner", "web banner", "restaurant banner", "ad banner", "hero banner",
    "display banner", "banner design"
}
THUMBNAIL_TERMS = {
    "thumbnail", "cover thumbnail", "youtube thumbnail", "video thumbnail",
    "restaurant thumbnail", "thumbnail design"
}
INVOICE_TERMS = {
    "invoice", "invoice template", "faktur", "billing template", "receipt invoice",
    "payment invoice"
}
RESUME_TERMS = {
    "resume", "cv", "curriculum vitae", "resume template", "cv template",
    "portfolio resume"
}
TICKET_RECEIPT_TERMS = {
    "order ticket", "restaurant order ticket", "receipt", "struk", "nota",
    "order receipt", "kitchen ticket", "kasir receipt", "bill template"
}
STATIC_CANVAS_TERMS = {
    "poster", "flyer", "banner", "social media", "instagram post", "carousel",
    "thumbnail", "cover", "static design", "desain poster", "desain feed",
    "social post"
}
DESIGN_SYSTEM_TERMS = {
    "design system", "token system", "style guide", "component system", "design tokens"
}
COMPONENT_LIBRARY_TERMS = {
    "component library", "design system components", "component set",
    "component variants", "figma components", "reusable components"
}
UI_KIT_TERMS = {
    "ui kit", "interface kit", "screen kit", "app kit", "dashboard ui kit"
}
LANDING_TERMS = {
    "landing page", "halaman landing", "sales page", "campaign page",
    "lead generation page", "waitlist page", "conversion page"
}
MOBILE_APP_TERMS = {
    "mobile app", "app screens", "ios", "android", "app ui", "mobile ui",
    "screen flow", "onboarding screens", "app onboarding", "fintech app"
}

MINIMALIST_TERMS = {"minimalist", "minimalism", "flat design"}
SMALL_SCOPE_TERMS = {"hero", "header", "micro landing", "squeeze page", "waitlist"}
RESTRICTED_MINIMAL_NAMES = {
    "minimal & direct",
    "minimal single column",
    "minimalism",
    "flat design",
    "hero + features + cta"
}
ECOMMERCE_CONTEXT = {
    "ecommerce", "e-commerce", "store", "shopify", "checkout", "cart", "keranjang",
    "online store", "toko online", "product catalog", "katalog produk", "product page",
    "product listing", "marketplace", "sell products", "jual produk", "store ecommerce"
}
HOSPITALITY_CONTEXT = {
    "coffee shop", "cafe", "kafe", "restaurant", "restoran", "rumah makan",
    "hospitality", "reservation", "reservasi", "venue", "hotel", "resort",
    "travel", "tour", "food service"
}

ACTION_GATE_FAILURE_CATEGORIES = {
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
    "manual_subprocess_timeout_not_killed",
}


def _load_json_data(filename: str, fallback):
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return fallback
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return fallback


def _load_user_extensions() -> dict:
    """Load optional local extensions without letting invalid files crash generation."""
    data = _load_json_data(USER_EXTENSIONS_FILE, {})
    return data if isinstance(data, dict) else {}


def _merge_extension_data(depth_rules: dict, structure_patterns: dict, extensions: dict) -> tuple[dict, dict]:
    if not extensions:
        return depth_rules, structure_patterns
    for family in extensions.get("custom_product_families", []) or []:
        if not isinstance(family, dict) or not family.get("id"):
            continue
        family_id = family["id"]
        if isinstance(family.get("depth_rule"), dict):
            depth_rules.setdefault(family_id, family["depth_rule"])
        if isinstance(family.get("structure_pattern"), dict):
            structure_patterns.setdefault(family_id, family["structure_pattern"])
    for pattern in extensions.get("custom_structure_patterns", []) or []:
        if isinstance(pattern, dict) and pattern.get("id"):
            structure_patterns.setdefault(pattern["id"], pattern)
    return depth_rules, structure_patterns


def _mode_key(output_mode: str) -> str:
    if output_mode == "ecommerce":
        return "website"
    return output_mode or "website"


def _as_lower_text(value) -> str:
    if isinstance(value, dict):
        return " ".join(_as_lower_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(_as_lower_text(v) for v in value)
    return str(value).lower()


def _find_terms(text: str, terms: list[str]) -> list[str]:
    text_lower = text.lower()
    return [term for term in terms if term.lower() in text_lower]


def detect_brain_design_context(start: Path | None = None) -> dict:
    """Detect Brain Design repository markers without assuming a local path."""
    markers = [
        ".design-brain",
        "AGENTS.md",
        "scripts/design_brain_module_select.py",
        "scripts/design_brain_router_smoke_test.py",
        "PACKAGE_MANIFEST.generated.json",
    ]
    root = Path(start or Path.cwd()).resolve()
    for candidate in [root, *root.parents]:
        found = [marker for marker in markers if (candidate / marker).exists()]
        if ".design-brain" in found or "scripts/design_brain_module_select.py" in found or len(found) >= 2:
            return {
                "detected": True,
                "root": str(candidate),
                "markers": found,
                "note": "active: Brain Design markers detected; Design Craft must stay in support-layer mode."
            }
    return {
        "detected": False,
        "root": "",
        "markers": [],
        "note": "standalone safe mode: no Brain Design markers detected; do not override Brain Design if it is later found."
    }


def _contains_phrase(text: str, phrase: str) -> bool:
    text_lower = f" {text.lower()} "
    phrase_lower = phrase.lower()
    if " " in phrase_lower or "-" in phrase_lower:
        normalized = phrase_lower.replace("-", " ")
        return f" {normalized} " in text_lower.replace("-", " ")
    return phrase_lower in set(tokenize_query(text_lower))


def _contains_any(text: str, phrases) -> bool:
    return any(_contains_phrase(text, phrase) for phrase in phrases)


def _allows_minimalism(query: str) -> bool:
    query_lower = query.lower()
    return any(term in query_lower for term in MINIMALIST_TERMS)


def _is_small_scope(query: str) -> bool:
    query_lower = query.lower()
    return any(term in query_lower for term in SMALL_SCOPE_TERMS)


def _is_explicit_email_context(text: str) -> bool:
    return _contains_any(text, [
        "email newsletter", "newsletter email", "email template", "email campaign",
        "marketing email", "mailchimp", "edm", "e-mail campaign", "template email"
    ])


def detect_explicit_output_mode(query: str, normalized_query: str = "") -> str | None:
    """Detect explicit medium/mode before product family routing."""
    text = " ".join([query or "", normalized_query or ""]).lower()
    if _contains_any(text, INVOICE_TERMS):
        return "invoice_template"
    if _contains_any(text, RESUME_TERMS):
        return "resume_template"
    if _contains_any(text, TICKET_RECEIPT_TERMS):
        return "ticket_receipt_design"
    if _contains_any(text, CERTIFICATE_TERMS):
        return "certificate_design"
    if _contains_any(text, BOOKLET_TERMS):
        return "booklet_design"
    if _contains_any(text, PACKAGING_LABEL_TERMS):
        return "packaging_label_design"
    if _contains_any(text, STICKER_TERMS):
        return "sticker_design"
    if _contains_any(text, POSTCARD_TERMS):
        return "postcard_design"
    if _contains_any(text, PRICE_TAG_TERMS):
        return "price_tag_design"
    if _contains_any(text, HANG_TAG_TERMS):
        return "hang_tag_design"
    if _contains_any(text, LABEL_TERMS):
        return "label_design"
    if _contains_any(text, VOUCHER_COUPON_TERMS):
        return "voucher_coupon_design"
    if _contains_any(text, LETTERHEAD_TERMS):
        return "letterhead_design"
    if _contains_any(text, PRICE_LIST_TERMS):
        return "price_list_design"
    if _contains_any(text, TABLE_TENT_TERMS):
        return "table_tent_design"
    if _contains_any(text, CATALOG_TERMS):
        return "catalog_design"
    if _contains_any(text, LOOKBOOK_TERMS):
        return "lookbook_design"
    if _contains_any(text, BROCHURE_TERMS):
        return "brochure_design"
    if _contains_any(text, WEB_DECK_TERMS):
        return "web_deck"
    if _contains_any(text, PRESENTATION_TERMS):
        return "presentation"
    if _is_explicit_email_context(text):
        return "email"
    if _contains_any(text, DESIGN_SYSTEM_TERMS):
        return "design_system"
    if _contains_any(text, COMPONENT_LIBRARY_TERMS):
        return "component_library"
    if _contains_any(text, UI_KIT_TERMS):
        return "ui_kit"
    if _contains_any(text, ["dashboard", "admin", "pos", "kasir", "crm", "analytics", "analitik", "back office", "data table"]):
        return "dashboard"
    if _contains_any(text, MOBILE_APP_TERMS):
        return "mobile_app"
    if _contains_any(text, BRAND_KIT_TERMS):
        return "brand_kit"
    if _contains_any(text, MENU_TERMS):
        return "menu_design"
    if _contains_any(text, SOCIAL_TERMS):
        return "social_post"
    if _contains_any(text, COVER_TERMS):
        return "cover_design"
    if _contains_any(text, POSTER_TERMS):
        return "poster_design"
    if _contains_any(text, BANNER_TERMS):
        return "banner_design"
    if _contains_any(text, THUMBNAIL_TERMS):
        return "thumbnail_design"
    if _contains_any(text, PRINT_COLLATERAL_TERMS):
        return "print_collateral"
    if _contains_any(text, LANDING_TERMS):
        return "landing"
    if _contains_any(text, STATIC_CANVAS_TERMS):
        return "static_canvas"
    return None


def _is_full_template_scope(query: str, output_mode: str) -> bool:
    query_lower = query.lower()
    return (
        output_mode in {"website", "ecommerce"}
        and not _is_small_scope(query_lower)
        and _contains_any(query_lower, ["website", "template", "full website", "marketplace template"])
    )


def _infer_custom_product_family(query: str, normalized_query: str, extensions: dict) -> str | None:
    text = " ".join([query or "", normalized_query or ""]).lower()
    for family in extensions.get("custom_product_families", []) or []:
        if not isinstance(family, dict):
            continue
        family_id = family.get("id")
        keywords = family.get("keywords", [])
        if family_id and isinstance(keywords, list) and _contains_any(text, keywords):
            return family_id
    return None


def infer_product_family(
    query: str,
    category: str = "",
    normalized_query: str = "",
    extensions: dict | None = None,
    allow_mode_families: bool = True,
) -> str:
    """Infer product family before selecting craft guidance."""
    text = " ".join([query or "", category or "", normalized_query or ""]).lower()
    intent_text = " ".join([query or "", normalized_query or ""]).lower()
    custom_family = _infer_custom_product_family(query, normalized_query, extensions or {})
    if custom_family:
        return custom_family

    if allow_mode_families and _contains_any(intent_text, ["dashboard", "admin", "pos", "kasir", "crm", "analytics", "analitik", "back office", "data table"]):
        return "dashboard_admin"
    if allow_mode_families and _contains_any(intent_text, MOBILE_APP_TERMS):
        return "mobile_app"
    if allow_mode_families and _contains_any(intent_text, WEB_DECK_TERMS):
        return "web_deck"
    if allow_mode_families and _contains_any(intent_text, PRESENTATION_TERMS):
        return "presentation_deck"
    if allow_mode_families and _is_explicit_email_context(intent_text):
        return "email_newsletter"
    if _contains_any(text, ["car rental", "rental mobil", "sewa mobil", "vehicle rental", "transport booking", "driver service", "airport transfer"]):
        return "car_rental_transport"
    if _contains_any(text, ["furniture rental", "rental furniture", "sewa furniture", "sewa furnitur", "rental furnitur", "event furniture rental", "office furniture rental", "home staging rental"]):
        return "furniture_rental_service"
    if _contains_any(text, ["klinik kecantikan", "beauty salon", "beauty", "skincare", "spa", "salon", "wellness", "aesthetic", "kecantikan", "perawatan", "massage"]):
        return "beauty_wellness"
    if _contains_any(text, ["clinic", "klinik", "medical", "healthcare", "doctor", "dokter", "appointment", "dental", "dentist", "health service"]):
        return "medical_clinic"
    if _contains_any(text, ["course", "kursus", "kursus online", "education", "edukasi", "sekolah", "academy", "akademi", "online learning", "lms", "class", "kelas online", "bootcamp"]):
        return "education_course"
    if _contains_any(text, ["real estate", "property", "properti", "listing", "apartment", "apartemen", "house listing", "rumah", "villa", "agent property", "broker property"]):
        return "real_estate_property"
    if _contains_any(text, ["fashion", "apparel", "clothing", "clothes", "baju", "pakaian", "toko baju", "fashion store", "apparel store", "butik", "boutique", "streetwear", "fashion ecommerce", "clothing shop", "online fashion store"]):
        return "fashion_apparel_ecommerce"
    if _contains_any(text, ["coffee shop", "cafe", "kafe", "restaurant", "restoran", "rumah makan", "hotel", "resort", "travel", "tour", "venue", "reservation", "reservasi", "hospitality"]):
        if not _contains_any(text, ["coffee bean online store", "coffee product ecommerce", "toko online kopi", "checkout", "cart", "keranjang"]):
            return "restaurant_hospitality"
    if _contains_any(text, ["jewelry ecommerce", "perhiasan ecommerce", "luxury ecommerce", "jewelry", "perhiasan"]) and _contains_any(text, ECOMMERCE_CONTEXT):
        return "jewelry_ecommerce"
    if _contains_any(text, ["ecommerce", "e-commerce", "online store", "toko online", "product catalog", "katalog produk", "checkout", "cart", "keranjang", "product page", "product listing", "marketplace", "coffee bean online store", "coffee product ecommerce"]):
        return "jewelry_ecommerce" if _contains_any(text, ["jewelry", "perhiasan"]) else "ecommerce_storefront"
    if _contains_any(text, ["luxury furniture", "furniture", "furnitur", "interior", "home decor"]):
        return "luxury_furniture"
    if _contains_any(text, ["financial consultant", "financial consulting", "finance", "fintech", "keuangan", "finansial", "konsultan keuangan", "consulting", "consultant", "akuntansi", "accounting", "investment", "tax", "pajak"]):
        return "finance_consulting"
    if _contains_any(text, ["sewa alat", "rental alat", "equipment rental", "rental booking", "service booking"]):
        return "equipment_rental_service"
    if _contains_any(text, ["creative agency", "agency", "agensi kreatif", "studio kreatif", "portfolio", "portofolio", "case study", "selected works"]):
        return "agency_portfolio"
    if _contains_any(text, ["blog", "editorial", "news", "berita", "magazine", "majalah", "cms", "newsletter website"]):
        return "editorial_blog_cms"
    if _contains_any(text, ["saas", "software", "product website", "platform"]):
        return "saas_product_website"
    if _contains_any(text, ["landing page", "halaman landing", "campaign", "sales page", "waitlist"]):
        return "landing_page"
    if _contains_any(text, ["website template", "template website", "full website", "website"]):
        return "full_website_template"
    return "full_website_template"


def resolve_product_family_for_mode(explicit_mode: str | None, niche_family: str) -> str:
    """Keep niche family for landing, but use mode-specific families for non-website artifacts."""
    if explicit_mode == "presentation":
        return "presentation_deck"
    if explicit_mode == "email":
        return "email_newsletter"
    if explicit_mode == "dashboard":
        return "dashboard_admin"
    if explicit_mode == "mobile_app":
        return "mobile_app"
    if explicit_mode in {
        "web_deck",
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
    }:
        return explicit_mode
    if explicit_mode == "landing":
        return niche_family if niche_family != "full_website_template" else "landing_page"
    return niche_family


def infer_output_mode(product_family: str, explicit_mode: str | None = None) -> str:
    if explicit_mode:
        return explicit_mode
    if product_family == "dashboard_admin":
        return "dashboard"
    if product_family == "mobile_app":
        return "mobile_app"
    if product_family == "presentation_deck":
        return "presentation"
    if product_family == "email_newsletter":
        return "email"
    if product_family in {"jewelry_ecommerce", "ecommerce_storefront", "luxury_furniture", "fashion_apparel_ecommerce"}:
        return "ecommerce"
    if product_family in {
        "web_deck",
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
    }:
        return product_family
    if product_family == "landing_page":
        return "landing"
    return "website"


def _minimalism_only_style(style: dict) -> bool:
    name = style.get("Style Category", style.get("name", "")).lower()
    return name in {"minimalism", "flat design", "minimal & direct", "minimal single column"} or name == "minimalism + flat design"


def _is_restricted_style_name(name: str) -> bool:
    name_lower = (name or "").lower().strip()
    return any(restricted in name_lower for restricted in RESTRICTED_MINIMAL_NAMES)


def _style_matches_keywords(style: dict, keywords: list[str]) -> bool:
    if not style or not keywords:
        return False
    haystack = " ".join(
        str(style.get(key, ""))
        for key in ["Style Category", "Type", "Keywords", "Best For", "Effects & Animation"]
    ).lower()
    return any(keyword.lower() in haystack for keyword in keywords if keyword)


def _sanitize_style_priority(style_priority: list, query: str) -> list:
    if _allows_minimalism(query):
        return style_priority
    sanitized = [
        item for item in style_priority
        if item and "minimalism" not in item.lower() and "flat design" not in item.lower()
    ]
    return sanitized or PRODUCT_AWARE_FALLBACK["style_priority"]


def _resolve_structure(product_family: str, output_mode: str, depth_rules: dict, structure_patterns: dict, best_landing: dict, reasoning: dict, niche_landing_patterns: dict | None = None) -> dict:
    pattern_key = MODE_DEPTH_RULES.get(output_mode, product_family)
    pattern = structure_patterns.get(pattern_key) or structure_patterns.get(product_family) or structure_patterns.get("full_website_template", {})
    sections = pattern.get("sections", [])
    unit_label = pattern.get("unit_label", "sections")

    if output_mode == "landing":
        landing_patterns = (niche_landing_patterns or {}).get("patterns", {})
        if product_family in landing_patterns:
            sections = landing_patterns[product_family]
            unit_label = "sections"

    if not sections:
        sections = [
            "Product-specific hero",
            "Audience/problem framing",
            "Core offer overview",
            "Proof or brand credibility",
            "Feature/service detail",
            "Process or workflow",
            "Showcase/gallery/module preview",
            "CTA closing",
            "Footer"
        ]

    depth_rule = depth_rules.get(pattern_key, depth_rules.get(product_family, depth_rules.get("full_website_template", {})))
    pattern_name = pattern.get("name", reasoning.get("pattern", PRODUCT_AWARE_FALLBACK["pattern"]))
    if output_mode == "web_deck":
        pattern_name = "Web Deck Stage System"
    if output_mode == "landing" and product_family != "landing_page":
        readable_family = product_family.replace("_", " ").title()
        pattern_name = f"{readable_family} Landing Page System"
    return {
        "name": pattern_name,
        "unit_label": unit_label,
        "sections": " > ".join(sections),
        "section_count": len(sections),
        "depth_rule": depth_rule,
        "pattern_key": pattern_key,
        "cta_placement": best_landing.get("Primary CTA Placement", "Mapped to product-family conversion path"),
        "color_strategy": best_landing.get("Color Strategy", "Color roles follow product meaning, not copied fallback"),
        "conversion": best_landing.get("Conversion Optimization", "Buyer decision path follows the product family")
    }


def _mode_profile(mode_profiles: dict, output_mode: str) -> dict:
    profiles = mode_profiles.get("profiles", {})
    return profiles.get(_mode_key(output_mode), profiles.get("website", {}))


def _mode_effect(mode_effects: dict, output_mode: str) -> dict:
    effects = mode_effects.get("effects", {})
    return effects.get(_mode_key(output_mode), effects.get("website", {}))


def _mode_checklist(mode_checklists: dict, output_mode: str) -> list[str]:
    checklists = mode_checklists.get("checklists", {})
    return checklists.get(_mode_key(output_mode), checklists.get("website", []))


def _action_mode_key(output_mode: str) -> str:
    if output_mode == "email":
        return "email_newsletter"
    if output_mode == "ecommerce":
        return "website"
    return output_mode or "website"


def _mode_action_model(action_models: dict, output_mode: str) -> dict:
    actions = action_models.get("actions", {})
    return actions.get(_action_mode_key(output_mode), actions.get(_mode_key(output_mode), actions.get("website", {})))


NON_WEBSITE_OUTPUT_MODES = {
    "dashboard",
    "mobile_app",
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


GENERIC_OR_MODE_FAMILIES = {
    "full_website_template",
    "landing_page",
    "email_newsletter",
    "presentation_deck",
    "web_deck",
    "dashboard_admin",
    "mobile_app",
    "brand_kit",
    "menu_design",
    "social_post",
    "static_canvas",
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


def resolve_niche_family(mode: str, detected_family: str, query: str, fallbacks: dict) -> tuple[str, str]:
    """Return visible niche/fallback family and separate domain context for non-web modes."""
    if mode not in NON_WEBSITE_OUTPUT_MODES:
        return detected_family, ""
    fallback_map = fallbacks.get("fallbacks", {}) if isinstance(fallbacks, dict) else {}
    visible = fallback_map.get(_action_mode_key(mode), fallback_map.get(mode, f"generic_{mode}"))
    domain_context = "" if detected_family in GENERIC_OR_MODE_FAMILIES else detected_family
    return visible, domain_context


MODE_KEYWORD_BASE = {
    "website": ["product-specific", "marketplace-ready", "structured hierarchy", "decision path"],
    "landing": ["niche landing", "campaign action", "objection handling", "proof rhythm"],
    "dashboard": ["KPI", "data hierarchy", "filters", "states", "workflow"],
    "presentation": ["slide system", "deck narrative", "master layout", "data readability"],
    "web_deck": ["stage scale", "slide flow", "reveal choreography", "runtime navigation"],
    "email_newsletter": ["email-safe", "mobile stack", "CTA block", "client compatibility"],
    "menu_design": ["menu hierarchy", "price alignment", "print/digital", "readability"],
    "social_post": ["hook", "aspect ratio", "crop safety", "carousel rhythm", "export"],
    "brand_kit": ["logo", "identity", "color roles", "applications"],
    "static_canvas": ["safe margin", "focal point", "print clarity", "export"],
    "ui_kit": ["tokens", "components", "states", "variants"],
    "component_library": ["tokens", "components", "states", "variants"],
    "design_system": ["tokens", "components", "states", "variants", "naming"],
    "mobile_app": ["screen flow", "navigation", "states", "task completion"],
    "brochure_design": ["brochure", "cover", "service overview", "contact block", "print/PDF"],
    "print_collateral": ["headline", "supporting copy", "safe margin", "print/export", "readability"],
    "poster_design": ["headline", "focal visual", "supporting info", "print", "export"],
    "banner_design": ["aspect ratio", "headline", "visual focus", "crop safety", "export"],
    "thumbnail_design": ["hook", "contrast", "small-size readability", "crop safety", "export"],
    "invoice_template": ["invoice metadata", "item table", "totals", "payment", "PDF/print"],
    "resume_template": ["profile", "experience", "skills", "education", "ATS", "PDF"],
    "ticket_receipt_design": ["order metadata", "item list", "quantity", "total", "receipt width", "print"],
    "letterhead_design": ["logo placement", "contact info", "footer", "safe margin", "print/PDF"],
    "price_list_design": ["category", "price alignment", "currency", "readability", "print/digital"],
    "table_tent_design": ["front/back", "panel", "QR", "fold", "safe margin", "print", "readability"],
    "catalog_design": ["cover", "category", "product grid", "spread", "print/PDF", "SKU", "price"],
    "lookbook_design": ["editorial opener", "collection story", "image spread", "style notes", "print/PDF", "visual rhythm"],
    "cover_design": ["title hierarchy", "focal visual", "safe area", "crop safety", "export", "readability"],
    "voucher_coupon_design": ["offer", "code", "QR", "expiry", "terms", "redemption", "print/digital"],
    "sticker_design": ["shape", "die-cut", "safe margin", "print", "material", "finish"],
    "postcard_design": ["front/back", "message", "image", "address", "safe margin", "print/export"],
    "certificate_design": ["recipient", "issuer", "signature", "seal", "date", "border", "PDF/print"],
    "booklet_design": ["cover", "spread", "page flow", "section", "print/PDF", "back cover"],
    "packaging_label_design": ["product name", "variant", "barcode", "dieline", "print", "material", "finish"],
    "label_design": ["label shape", "brand/product hierarchy", "supporting info", "material", "finish", "print/export"],
    "price_tag_design": ["price", "SKU", "barcode", "tag", "die-cut", "print/export"],
    "hang_tag_design": ["brand", "size", "material", "SKU", "barcode", "hole", "front/back", "print/export"],
}


def _keyword_items(source_keywords) -> list[str]:
    if isinstance(source_keywords, str):
        raw = source_keywords.replace(";", ",").split(",")
        return [item.strip() for item in raw if item.strip()]
    if isinstance(source_keywords, list):
        return [str(item).strip() for item in source_keywords if str(item).strip()]
    return []


def build_mode_keywords(mode: str, product_family: str, niche: str, source_keywords) -> str:
    """Build keywords that cannot leak raw website/full-template wording into other modes."""
    action_key = _action_mode_key(mode)
    keywords = list(MODE_KEYWORD_BASE.get(action_key, MODE_KEYWORD_BASE["website"]))
    if mode in {"website", "ecommerce", "landing"}:
        keywords.extend(_keyword_items(source_keywords))
    if product_family:
        keywords.append(product_family.replace("_", " "))
    if niche and niche != product_family:
        keywords.append(niche.replace("_", " "))

    safe_keywords: list[str] = []
    for keyword in keywords:
        lower = keyword.lower()
        if mode not in {"website", "ecommerce", "landing"} and "full website" in lower:
            continue
        if mode not in {"website", "ecommerce", "landing"} and "website sections" in lower:
            continue
        if mode not in {"website", "ecommerce", "landing"} and lower in {"conversion", "conversion funnel", "cta placement"}:
            continue
        if keyword not in safe_keywords:
            safe_keywords.append(keyword)
    return ", ".join(safe_keywords)


def _landing_action_note(landing_action_notes: dict, product_family: str) -> dict:
    notes = landing_action_notes.get("notes", {})
    return notes.get(product_family, {})


def sanitize_pattern_metadata_for_mode(metadata: dict, mode: str, product_family: str, action_models: dict, landing_action_notes: dict) -> dict:
    """Strip or replace raw landing.csv conversion fields with medium-specific action metadata."""
    pattern = dict(metadata)
    action_model = _mode_action_model(action_models, mode)
    sanitized_fields: list[str] = []
    action_payload = {
        "primary_action_label": action_model.get("primary_action_label", "Primary action"),
        "action_goal": action_model.get("action_goal", "Use a medium-appropriate action path."),
        "allowed_terms": action_model.get("allowed_terms", []),
        "forbidden_terms": action_model.get("forbidden_terms", []),
    }
    pattern["action_model"] = action_payload
    pattern["primary_action_label"] = action_payload["primary_action_label"]
    pattern["primary_action"] = action_payload["action_goal"]

    if mode == "landing":
        note = _landing_action_note(landing_action_notes, product_family)
        conversion_goal = note.get("conversion_goal", action_payload["action_goal"])
        cta_strategy = note.get("cta_strategy", "CTA after niche-specific proof, offer clarity, and objection handling.")
        pattern["conversion"] = conversion_goal
        pattern["cta_placement"] = cta_strategy
        pattern["medium_notes"] = cta_strategy
        pattern["niche_action_note"] = note
        return pattern

    if mode in {"website", "ecommerce"}:
        pattern.setdefault("medium_notes", action_payload["action_goal"])
        return pattern

    for field in ["conversion", "conversion_focus", "cta_placement", "section_order", "best_for", "color_strategy"]:
        if field in pattern:
            pattern.pop(field, None)
            sanitized_fields.append(field)
    pattern["sanitized_fields"] = sanitized_fields
    pattern["medium_notes"] = action_payload["action_goal"]

    if mode == "dashboard":
        pattern["workflow_strategy"] = "Prioritize task efficiency, KPI scanability, filtering, and operational state handling."
        pattern["data_hierarchy"] = "KPI hierarchy, chart/table priority, filters/search, and status clarity."
        pattern["state_coverage"] = "Empty, loading, error, permission, and role-aware states."
    return pattern


def _build_style_payload(
    output_mode: str,
    product_family: str,
    niche_family: str,
    query: str,
    mode_profiles: dict,
    mode_effects: dict,
) -> dict:
    profile = _mode_profile(mode_profiles, output_mode)
    effect = _mode_effect(mode_effects, output_mode)
    style_name = profile.get("style_name", FAMILY_STYLE_FALLBACKS.get(product_family, "Reference-Led Visual Identity"))
    keywords = build_mode_keywords(output_mode, product_family, niche_family, profile.get("keywords", []))
    return {
        "name": style_name,
        "style_name": style_name,
        "type": "Mode-specific payload",
        "intent": profile.get("style_intent", "Mode-compatible craft direction."),
        "style_intent": profile.get("style_intent", "Mode-compatible craft direction."),
        "keywords": keywords,
        "layout_behavior": profile.get("layout_behavior", ""),
        "visual_depth": profile.get("visual_depth", ""),
        "effect_language": effect.get("key_effects", profile.get("visual_depth", "")),
        "effects": effect.get("key_effects", ""),
        "key_effects": effect.get("key_effects", ""),
        "best_for": profile.get("best_for", ""),
        "avoid": "Mode-incompatible interaction language and generic fallback structure",
        "accessibility": profile.get("accessibility_notes", ""),
        "accessibility_notes": profile.get("accessibility_notes", ""),
        "performance": "Mode-specific performance constraints apply",
        "mode_compatibility": profile.get("mode_compatibility", [_mode_key(output_mode)]),
        "risk_level": profile.get("risk_level", "low"),
        "safety_scope": profile.get("safety_scope", "mode_safe"),
    }


def validate_style_payload(design_system_output: dict, guards: dict, mode_effects: dict) -> dict:
    output_mode = design_system_output.get("output_mode", "")
    query = design_system_output.get("query", "")
    style = design_system_output.get("style", {})
    pattern = design_system_output.get("pattern", {})
    checklist = design_system_output.get("quality_checklist", [])
    visible_pattern = dict(pattern)
    visible_pattern.pop("sanitized_fields", None)
    if isinstance(visible_pattern.get("action_model"), dict):
        visible_pattern["action_model"] = {
            key: value
            for key, value in visible_pattern["action_model"].items()
            if key != "forbidden_terms"
        }
    if isinstance(visible_pattern.get("niche_action_note"), dict):
        visible_pattern["niche_action_note"] = {
            key: value
            for key, value in visible_pattern["niche_action_note"].items()
            if key != "avoid"
        }
    payload_text = _as_lower_text({
        "style": style,
        "key_effects": design_system_output.get("key_effects", ""),
        "pattern": visible_pattern,
        "checklist": checklist,
    })
    restricted_terms = guards.get("restricted_minimal_payload_terms", [])
    web_modes = set(guards.get("web_modes", [])) or {"website", "ecommerce", "landing"}
    if output_mode in web_modes and not _allows_minimalism(query):
        found = _find_terms(payload_text, restricted_terms)
        if found:
            return {
                "status": "FAIL",
                "category": "restricted minimal payload leak",
                "offending_terms": found,
                "recommended_fix": "Replace the full style payload, not only the style name.",
            }
    is_non_web = output_mode in set(guards.get("non_web_modes", []))
    forbidden = []
    if is_non_web:
        forbidden.extend(guards.get("web_only_effect_terms", []))
        forbidden.extend(_mode_effect(mode_effects, output_mode).get("forbidden_terms", []))
    elif output_mode == "web_deck":
        forbidden.extend(_mode_effect(mode_effects, output_mode).get("forbidden_terms", []))
    if forbidden:
        found = _find_terms(payload_text, sorted(set(forbidden)))
        if found:
            return {
                "status": "FAIL",
                "category": "web-only effect in non-web mode" if is_non_web else "forbidden effect language for mode",
                "offending_terms": found,
                "recommended_fix": "Replace with mode-specific effect language and checklist.",
            }
    if output_mode == "landing" and design_system_output.get("product_family") != "landing_page":
        sections = pattern.get("sections", "").lower()
        generic = ["campaign hero", "offer/value proof", "benefits", "how it works", "social proof", "faq/objections", "cta closing"]
        if all(item in sections for item in generic):
            return {
                "status": "FAIL",
                "category": "generic landing structure in niche landing",
                "offending_terms": ["generic landing sections"],
                "recommended_fix": "Use niche_landing_patterns.json for this product family.",
            }
    return {"status": "PASS", "category": "", "offending_terms": [], "recommended_fix": ""}


def validate_action_payload(design_system_output: dict, action_models: dict, landing_action_notes: dict) -> dict:
    output_mode = design_system_output.get("output_mode", "")
    product_family = design_system_output.get("product_family", "")
    query = design_system_output.get("query", "")
    visible_niche = design_system_output.get("visible_niche_family", design_system_output.get("niche_family", ""))
    pattern = design_system_output.get("pattern", {})
    style = design_system_output.get("style", {})
    checklist = design_system_output.get("quality_checklist", [])
    action_model = _mode_action_model(action_models, output_mode)
    if _contains_any(query, VOUCHER_COUPON_TERMS) and output_mode != "voucher_coupon_design":
        if _contains_any(query, ["coupon"]):
            category = "coupon_wrong_mode"
        elif _contains_any(query, ["gift card"]):
            category = "gift_card_wrong_mode"
        elif _contains_any(query, ["loyalty card", "membership card", "reward card"]):
            category = "loyalty_card_wrong_mode"
        else:
            category = "voucher_wrong_mode"
        return {
            "status": "FAIL",
            "category": category,
            "offending_terms": [output_mode or "missing mode"],
            "recommended_fix": "Detect voucher/coupon/card collateral before product/website routing.",
        }
    wrong_mode_checks = [
        (SOCIAL_TERMS, {"social_post"}, "instagram_story_wrong_mode"),
        (LETTERHEAD_TERMS, {"letterhead_design"}, "letterhead_wrong_mode"),
        (PRICE_LIST_TERMS, {"price_list_design", "menu_design"}, "price_list_wrong_mode"),
        (TABLE_TENT_TERMS, {"table_tent_design", "menu_design"}, "table_tent_wrong_mode"),
        (CATALOG_TERMS, {"catalog_design"}, "catalog_wrong_mode"),
        (LOOKBOOK_TERMS, {"lookbook_design"}, "lookbook_wrong_mode"),
        (COVER_TERMS, {"cover_design", "social_post"}, "cover_wrong_mode"),
        (STICKER_TERMS, {"sticker_design"}, "sticker_wrong_mode"),
        (POSTCARD_TERMS, {"postcard_design"}, "postcard_wrong_mode"),
        (CERTIFICATE_TERMS, {"certificate_design"}, "certificate_wrong_mode"),
        (BOOKLET_TERMS, {"booklet_design"}, "booklet_wrong_mode"),
        (PACKAGING_LABEL_TERMS, {"packaging_label_design"}, "packaging_label_wrong_mode"),
        (LABEL_TERMS, {"label_design", "packaging_label_design"}, "label_wrong_mode"),
        (PRICE_TAG_TERMS, {"price_tag_design"}, "price_tag_wrong_mode"),
        (HANG_TAG_TERMS, {"hang_tag_design"}, "hang_tag_wrong_mode"),
    ]
    for terms, allowed_modes, category in wrong_mode_checks:
        if _contains_any(query, terms) and output_mode not in allowed_modes:
            return {
                "status": "FAIL",
                "category": category,
                "offending_terms": [output_mode or "missing mode"],
                "recommended_fix": "Detect explicit medium intent before product/website routing.",
            }
    if output_mode in NON_WEBSITE_OUTPUT_MODES and visible_niche == "full_website_template":
        return {
            "status": "FAIL",
            "category": "non_web_full_website_family_label",
            "offending_terms": ["NICHE FAMILY: full_website_template"],
            "recommended_fix": "Use mode_family_fallbacks.json for visible non-web family labels.",
        }
    visible_pattern = dict(pattern)
    visible_pattern.pop("sanitized_fields", None)
    if isinstance(visible_pattern.get("action_model"), dict):
        visible_pattern["action_model"] = {
            key: value
            for key, value in visible_pattern["action_model"].items()
            if key != "forbidden_terms"
        }
    if isinstance(visible_pattern.get("niche_action_note"), dict):
        visible_pattern["niche_action_note"] = {
            key: value
            for key, value in visible_pattern["niche_action_note"].items()
            if key != "avoid"
        }
    payload_text = _as_lower_text({
        "pattern": visible_pattern,
        "style_keywords": style.get("keywords", ""),
        "best_for": style.get("best_for", ""),
        "checklist": checklist,
        "action_model": {
            "primary_action_label": pattern.get("action_model", {}).get("primary_action_label", ""),
            "action_goal": pattern.get("action_model", {}).get("action_goal", ""),
            "allowed_terms": pattern.get("action_model", {}).get("allowed_terms", []),
        },
        "medium_notes": pattern.get("medium_notes", ""),
    })

    action_forbidden = action_model.get("forbidden_terms", [])
    found = _find_terms(payload_text, action_forbidden)
    if found:
        return {
            "status": "FAIL",
            "category": "mode_action_mismatch",
            "offending_terms": found,
            "recommended_fix": "Replace raw conversion/CTA metadata with the mode action model.",
        }

    if output_mode not in {"website", "ecommerce", "landing"}:
        wrong_keyword = _find_terms(payload_text, ["full website"])
        if wrong_keyword:
            return {
                "status": "FAIL",
                "category": "wrong_medium_keyword_leak",
                "offending_terms": wrong_keyword,
                "recommended_fix": "Rebuild keywords from the mode keyword generator.",
            }
        raw_landing = _find_terms(payload_text, ["logo carousel", "tab switching", "Contact Sales + Login", "Bottom section", "86% higher engagement with video"])
        if raw_landing:
            if output_mode in {"price_tag_design", "hang_tag_design"}:
                category = "tag_ecommerce_leak"
            elif output_mode in {"packaging_label_design", "label_design"}:
                category = "packaging_label_website_leak"
            elif output_mode == "cover_design" and _contains_any(query, ["facebook cover"]):
                category = "facebook_cover_block"
            elif output_mode == "cover_design":
                category = "cover_wrong_mode"
            elif output_mode == "social_post":
                category = "social_carousel_payload_leak"
            elif output_mode in {"static_canvas", "print_collateral", "poster_design", "banner_design", "thumbnail_design", "brochure_design", "letterhead_design", "price_list_design", "table_tent_design", "catalog_design", "lookbook_design", "voucher_coupon_design", "sticker_design", "postcard_design", "certificate_design", "booklet_design"}:
                category = "static_collateral_landing_payload_leak"
            else:
                category = "landing_csv_payload_leak"
            return {
                "status": "FAIL",
                "category": category,
                "offending_terms": raw_landing,
                "recommended_fix": "Strip raw landing.csv metadata and replace it with the mode action model.",
            }
        non_web_forbidden = [
            "Conversion Strategy",
            "CTA Placement",
            "Contact Sales",
            "Contact Sales + Login",
            "logo carousel",
            "tab switching",
            "website sections",
            "conversion funnel",
            "marketing CTA",
            "cart",
            "checkout",
        ]
        found = _find_terms(payload_text, non_web_forbidden)
        if found:
            if output_mode in {"price_tag_design", "hang_tag_design"}:
                category = "tag_ecommerce_leak"
            elif output_mode in {"packaging_label_design", "label_design"}:
                category = "packaging_label_website_leak"
            elif output_mode == "cover_design" and _contains_any(query, ["facebook cover"]):
                category = "facebook_cover_block"
            elif output_mode == "cover_design":
                category = "cover_wrong_mode"
            elif output_mode == "social_post":
                category = "social_carousel_payload_leak"
            elif output_mode in {"invoice_template", "resume_template", "ticket_receipt_design", "letterhead_design", "certificate_design", "booklet_design"}:
                category = "document_mode_website_leak"
            elif output_mode in {"catalog_design"}:
                category = "catalog_wrong_mode"
            elif output_mode in {"lookbook_design"}:
                category = "lookbook_wrong_mode"
            else:
                category = "non_web_conversion_leak"
            return {
                "status": "FAIL",
                "category": category,
                "offending_terms": found,
                "recommended_fix": "Sanitize landing.csv metadata before outputting non-web modes.",
            }

    if output_mode == "dashboard":
        found = _find_terms(payload_text, ["Conversion Strategy", "CTA Placement", "Contact Sales", "marketing CTA", "conversion funnel"])
        if found:
            return {
                "status": "FAIL",
                "category": "dashboard_conversion_language_leak",
                "offending_terms": found,
                "recommended_fix": "Use workflow/data/state dashboard language instead of marketing conversion labels.",
            }

    if output_mode == "landing" and product_family != "landing_page":
        note = _landing_action_note(landing_action_notes, product_family)
        avoid_terms = list(note.get("avoid", [])) + [
            "Narrative increases time-on-page",
            "Final climax CTA",
            "End of each chapter",
            "Parallax Storytelling",
        ]
        found = _find_terms(payload_text, avoid_terms)
        if found:
            return {
                "status": "FAIL",
                "category": "niche_landing_action_mismatch",
                "offending_terms": found,
                "recommended_fix": "Replace generic storytelling conversion note with niche landing action notes.",
            }
    return {"status": "PASS", "category": "", "offending_terms": [], "recommended_fix": ""}


def run_anti_scaffold_gate(design_system_output: dict) -> dict:
    """Check for dangerous generic design-system output."""
    guards = design_system_output.get("_style_payload_guards", {})
    mode_effects = design_system_output.get("_mode_effect_language", {})
    action_models = design_system_output.get("_mode_action_model", {})
    landing_action_notes = design_system_output.get("_niche_landing_action_notes", {})
    if guards:
        payload_validation = validate_style_payload(design_system_output, guards, mode_effects)
        if payload_validation.get("status") != "PASS":
            return {
                "status": "FAIL",
                "reason": f"{payload_validation.get('category')}: {', '.join(payload_validation.get('offending_terms', []))}",
                "recommended_fix": payload_validation.get("recommended_fix", ""),
                "failure_category": payload_validation.get("category", ""),
                "offending_terms": payload_validation.get("offending_terms", []),
            }
    if action_models:
        action_validation = validate_action_payload(design_system_output, action_models, landing_action_notes)
        if action_validation.get("status") != "PASS":
            return {
                "status": "FAIL",
                "reason": f"{action_validation.get('category')}: {', '.join(action_validation.get('offending_terms', []))}",
                "recommended_fix": action_validation.get("recommended_fix", ""),
                "failure_category": action_validation.get("category", ""),
                "offending_terms": action_validation.get("offending_terms", []),
            }
    pattern = design_system_output.get("pattern", {})
    style = design_system_output.get("style", {})
    family = design_system_output.get("product_family", "")
    output_mode = design_system_output.get("output_mode", "")
    sections = pattern.get("sections", "")
    section_count = pattern.get("section_count", 0)
    depth_rule = pattern.get("depth_rule", {})

    if sections.strip().lower() in {"hero > features > cta", "hero + features + cta"}:
        return {"status": "FAIL", "reason": "Default Hero + Features + CTA scaffold detected.", "recommended_fix": "Resolve structure from product family rules."}
    if not _allows_minimalism(design_system_output.get("query", "")) and _minimalism_only_style(style):
        return {"status": "FAIL", "reason": "Minimalism/Flat Design was selected as fallback.", "recommended_fix": "Use reference-led, domain-aware art direction."}
    if design_system_output.get("restricted_style_used") and _is_full_template_scope(design_system_output.get("query", ""), output_mode):
        return {"status": "FAIL", "reason": "Restricted minimal/small-scope style was used for full template scope.", "recommended_fix": "Replace with product-family art direction."}
    if output_mode == "dashboard" and any(term in sections.lower() for term in ["hero", "testimonial", "cta closing"]):
        return {"status": "FAIL", "reason": "Dashboard was treated as a landing page.", "recommended_fix": "Use dashboard modules, data states, and navigation."}
    min_sections = depth_rule.get("min_sections")
    if min_sections and section_count < min_sections:
        return {"status": "FAIL", "reason": f"{family} has {section_count} sections; minimum is {min_sections}.", "recommended_fix": "Expand with product-family meaningful sections."}
    min_modules = depth_rule.get("min_modules")
    if min_modules and section_count < min_modules:
        return {"status": "FAIL", "reason": f"{family} has {section_count} modules; minimum is {min_modules}.", "recommended_fix": "Add dashboard modules and states."}
    min_blocks = depth_rule.get("min_blocks")
    if min_blocks and section_count < min_blocks:
        return {"status": "FAIL", "reason": f"{family} has {section_count} blocks; minimum is {min_blocks}.", "recommended_fix": "Add required template blocks."}
    return {"status": "PASS", "reason": "Product-aware structure and style checks passed.", "recommended_fix": ""}


def _auto_repair_design_system(
    design_system: dict,
    depth_rules: dict,
    structure_patterns: dict,
    mode_profiles: dict,
    mode_effects: dict,
    mode_checklists: dict,
    niche_landing_patterns: dict,
    mode_action_model: dict,
    niche_landing_action_notes: dict,
) -> dict:
    """Apply one conservative repair pass before blocking output."""
    output_mode = design_system.get("output_mode", "")
    product_family = design_system.get("product_family", "")
    niche_family = design_system.get("visible_niche_family", design_system.get("niche_family", ""))
    domain_context = design_system.get("domain_context", "")
    design_system["style"] = _build_style_payload(output_mode, product_family, niche_family, design_system.get("query", ""), mode_profiles, mode_effects)
    design_system["key_effects"] = design_system["style"].get("key_effects", "")
    design_system["quality_checklist"] = _mode_checklist(mode_checklists, output_mode)
    design_system["anti_patterns"] = "Mode-incompatible scaffold or generic fallback structure"
    design_system["restricted_style_used"] = False
    design_system["style_safety_status"] = "auto-repaired"
    design_system["pattern"] = _resolve_structure(product_family, output_mode, depth_rules, structure_patterns, {}, PRODUCT_AWARE_FALLBACK, niche_landing_patterns)
    design_system["pattern"] = sanitize_pattern_metadata_for_mode(
        design_system["pattern"],
        output_mode,
        product_family,
        mode_action_model,
        niche_landing_action_notes,
    )
    design_system.setdefault("warnings", []).append("Auto-repair applied after anti-scaffold gate failure.")
    return design_system


def _blocked_output_message(design_system: dict, persist_requested: bool = False) -> str:
    gate = design_system.get("anti_scaffold_gate", {})
    checklist = design_system.get("quality_checklist", [])
    lines = [
        "Output blocked: anti-scaffold gate failed.",
        f"Reason: {gate.get('reason', 'Unknown failure')}",
    ]
    if gate.get("recommended_fix"):
        lines.append(f"Required action: {gate.get('recommended_fix')}")
    if persist_requested:
        lines.append("Persist aborted because anti-scaffold gate failed.")
    return "\n".join(lines)


# ============ DESIGN SYSTEM GENERATOR ============
class DesignSystemGenerator:
    """Generates design system recommendations from aggregated searches."""

    def __init__(self):
        self.reasoning_data = self._load_reasoning()

    def _load_reasoning(self) -> list:
        """Load reasoning rules from CSV."""
        filepath = DATA_DIR / REASONING_FILE
        if not filepath.exists():
            return []
        with open(filepath, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def _multi_domain_search(self, query: str, style_priority: list = None) -> dict:
        """Execute searches across multiple domains."""
        results = {}
        for domain, config in SEARCH_CONFIG.items():
            if domain == "style" and style_priority:
                # For style, also search with priority keywords
                priority_query = " ".join(style_priority[:2]) if style_priority else query
                combined_query = f"{query} {priority_query}"
                results[domain] = search(combined_query, domain, config["max_results"])
            else:
                results[domain] = search(query, domain, config["max_results"])
        return results

    def _find_reasoning_rule(self, category: str) -> dict:
        """Find matching reasoning rule for a category."""
        category_lower = category.lower()

        # Try exact match first
        for rule in self.reasoning_data:
            if rule.get("UI_Category", "").lower() == category_lower:
                return rule

        # Try partial match
        for rule in self.reasoning_data:
            ui_cat = rule.get("UI_Category", "").lower()
            if ui_cat in category_lower or category_lower in ui_cat:
                return rule

        # Try keyword match
        for rule in self.reasoning_data:
            ui_cat = rule.get("UI_Category", "").lower()
            keywords = ui_cat.replace("/", " ").replace("-", " ").split()
            if any(kw in category_lower for kw in keywords):
                return rule

        return {}

    def _apply_reasoning(self, category: str, search_results: dict) -> dict:
        """Apply reasoning rules to search results."""
        rule = self._find_reasoning_rule(category)

        if not rule:
            return dict(PRODUCT_AWARE_FALLBACK)

        # Parse decision rules JSON
        decision_rules = {}
        try:
            decision_rules = json.loads(rule.get("Decision_Rules", "{}"))
        except json.JSONDecodeError:
            pass

        return {
            "pattern": rule.get("Recommended_Pattern", ""),
            "style_priority": [s.strip() for s in rule.get("Style_Priority", "").split("+") if s.strip()],
            "color_mood": rule.get("Color_Mood", ""),
            "typography_mood": rule.get("Typography_Mood", ""),
            "key_effects": rule.get("Key_Effects", ""),
            "anti_patterns": rule.get("Anti_Patterns", ""),
            "decision_rules": decision_rules,
            "severity": rule.get("Severity", "MEDIUM")
        }

    def _select_best_match(self, results: list, priority_keywords: list) -> dict:
        """Select best matching result based on priority keywords."""
        if not results:
            return {}

        if not priority_keywords:
            return results[0]

        # First: try exact style name match
        for priority in priority_keywords:
            priority_lower = priority.lower().strip()
            for result in results:
                style_name = result.get("Style Category", "").lower()
                if priority_lower in style_name or style_name in priority_lower:
                    return result

        # Second: score by keyword match in all fields
        scored = []
        for result in results:
            result_str = str(result).lower()
            score = 0
            for kw in priority_keywords:
                kw_lower = kw.lower().strip()
                # Higher score for style name match
                if kw_lower in result.get("Style Category", "").lower():
                    score += 10
                # Lower score for keyword field match
                elif kw_lower in result.get("Keywords", "").lower():
                    score += 3
                # Even lower for other field matches
                elif kw_lower in result_str:
                    score += 1
            scored.append((score, result))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1] if scored and scored[0][0] > 0 else results[0]

    def _extract_results(self, search_result: dict) -> list:
        """Extract results list from search result dict."""
        return search_result.get("results", [])

    def generate(self, query: str, project_name: str = None) -> dict:
        """Generate complete design system recommendation."""
        normalized_query = normalize_query_for_design_craft(query)
        depth_rules = _load_json_data(PRODUCT_DEPTH_FILE, {})
        structure_patterns = _load_json_data(STRUCTURE_PATTERNS_FILE, {})
        safety_metadata = _load_json_data(LEGACY_PATTERN_SAFETY_FILE, {})
        style_payload_guards = _load_json_data(STYLE_PAYLOAD_GUARDS_FILE, {})
        mode_style_profiles = _load_json_data(MODE_STYLE_PROFILES_FILE, {})
        mode_effect_language = _load_json_data(MODE_EFFECT_LANGUAGE_FILE, {})
        mode_quality_checklists = _load_json_data(MODE_QUALITY_CHECKLISTS_FILE, {})
        niche_landing_patterns = _load_json_data(NICHE_LANDING_PATTERNS_FILE, {})
        mode_action_model = _load_json_data(MODE_ACTION_MODEL_FILE, {})
        niche_landing_action_notes = _load_json_data(NICHE_LANDING_ACTION_NOTES_FILE, {})
        mode_family_fallbacks = _load_json_data(MODE_FAMILY_FALLBACKS_FILE, {})
        extensions = _load_user_extensions()
        depth_rules, structure_patterns = _merge_extension_data(depth_rules, structure_patterns, extensions)
        brain_design = detect_brain_design_context()
        warnings = []
        restricted_fallback_avoided = False

        # Step 1: First search product to get category
        product_result = search(normalized_query, "product", 1)
        product_results = product_result.get("results", [])
        category = "General"
        if product_results:
            category = product_results[0].get("Product Type", "General")
        else:
            warnings.append(PRODUCT_AWARE_FALLBACK["decision_rules"]["warning"])

        explicit_mode = detect_explicit_output_mode(query, normalized_query)
        niche_family = infer_product_family(query, "", normalized_query, extensions, allow_mode_families=False)
        if explicit_mode in {"ui_kit", "component_library", "design_system"} and _contains_any(query, ["dashboard", "admin", "analytics", "pos", "kasir", "crm"]):
            niche_family = "dashboard_admin"
        product_family = resolve_product_family_for_mode(explicit_mode, niche_family)
        output_mode = infer_output_mode(product_family, explicit_mode)
        visible_niche_family, domain_context = resolve_niche_family(output_mode, niche_family, query, mode_family_fallbacks)

        # Step 2: Get reasoning rules for this category
        reasoning = self._apply_reasoning(category, {})
        style_priority = _sanitize_style_priority(reasoning.get("style_priority", []), query)
        family_keywords = FAMILY_STYLE_KEYWORDS.get(product_family, []) + FAMILY_STYLE_KEYWORDS.get(niche_family, [])
        style_priority = family_keywords + [item for item in style_priority if item not in family_keywords]

        # Step 3: Multi-domain search with style priority hints
        search_results = self._multi_domain_search(normalized_query, style_priority)
        search_results["product"] = product_result  # Reuse product search

        # Step 4: Select best matches from each domain using priority
        style_results = self._extract_results(search_results.get("style", {}))
        color_results = self._extract_results(search_results.get("color", {}))
        typography_results = self._extract_results(search_results.get("typography", {}))
        landing_results = self._extract_results(search_results.get("landing", {}))

        best_style = self._select_best_match(style_results, style_priority)
        best_color = color_results[0] if color_results else {}
        best_typography = typography_results[0] if typography_results else {}
        best_landing = landing_results[0] if landing_results else {}

        if (
            best_style
            and product_family in STRICT_FAMILY_STYLE_FALLBACKS
            and not _style_matches_keywords(best_style, family_keywords)
        ):
            best_style = {
                "Style Category": FAMILY_STYLE_FALLBACKS.get(product_family, "Reference-Led Visual Identity"),
                "Type": "Product-family fallback",
                "Keywords": ", ".join(style_priority),
                "Best For": "Product-aware marketplace templates where raw search results are not domain-fit",
                "Performance": "Depends on implementation choices",
                "Accessibility": "Must be validated against final palette and layout"
            }
            warnings.append("Product-family style fallback used because raw search style was not domain-fit.")

        selected_style_name = best_style.get("Style Category", "")
        restricted_style_used = _is_restricted_style_name(selected_style_name)
        if (
            (restricted_style_used or _minimalism_only_style(best_style))
            and _is_full_template_scope(query, output_mode)
            and not _allows_minimalism(query)
        ):
            best_style = {
                "Style Category": FAMILY_STYLE_FALLBACKS.get(product_family, "Reference-Led Visual Identity"),
                "Type": "Product-aware fallback",
                "Keywords": ", ".join(style_priority),
                "Best For": "Marketplace templates that require domain-specific structure and art direction",
                "Performance": "Depends on implementation choices",
                "Accessibility": "Must be validated against final palette and layout"
            }
            restricted_fallback_avoided = True
            warnings.append("Restricted minimal style avoided for full template scope.")

        if not best_style:
            best_style = {
                "Style Category": FAMILY_STYLE_FALLBACKS.get(product_family, "Reference-Led Visual Identity"),
                "Type": "Product-aware fallback",
                "Keywords": ", ".join(style_priority),
                "Best For": "Domain-specific marketplace template output",
                "Performance": "Depends on implementation choices",
                "Accessibility": "Validate contrast, focus, and responsive behavior"
            }

        # Step 5: Build final recommendation
        style_payload = _build_style_payload(output_mode, product_family, niche_family, query, mode_style_profiles, mode_effect_language)
        combined_effects = style_payload.get("key_effects", "")
        resolved_pattern = _resolve_structure(product_family, output_mode, depth_rules, structure_patterns, best_landing, reasoning, niche_landing_patterns)
        resolved_pattern = sanitize_pattern_metadata_for_mode(resolved_pattern, output_mode, product_family, mode_action_model, niche_landing_action_notes)
        structure_name = resolved_pattern.get("name", "")
        if (
            _is_restricted_style_name(structure_name)
            and _is_full_template_scope(query, output_mode)
            and not _allows_minimalism(query)
        ):
            restricted_fallback_avoided = True
            warnings.append("Restricted legacy pattern avoided for full template scope.")
            resolved_pattern = _resolve_structure(product_family, output_mode, depth_rules, structure_patterns, {}, PRODUCT_AWARE_FALLBACK, niche_landing_patterns)
            resolved_pattern = sanitize_pattern_metadata_for_mode(resolved_pattern, output_mode, product_family, mode_action_model, niche_landing_action_notes)
        final_style_name = style_payload.get("name", FAMILY_STYLE_FALLBACKS.get(product_family, "Reference-Led Visual Identity"))
        restricted_style_used = _is_restricted_style_name(final_style_name)
        style_safety_status = "restricted-explicit" if restricted_style_used else "full-template-safe"
        if restricted_fallback_avoided:
            style_safety_status = "restricted fallback avoided"

        design_system = {
            "project_name": project_name or query.upper(),
            "query": query,
            "normalized_query": normalized_query,
            "category": category,
            "product_family": product_family,
            "niche_family": visible_niche_family,
            "domain_context": domain_context,
            "visible_niche_family": visible_niche_family,
            "domain_context": domain_context,
            "output_mode": output_mode,
            "pattern": resolved_pattern,
            "style": style_payload,
            "colors": {
                "primary": best_color.get("Primary (Hex)", "#2563EB"),
                "secondary": best_color.get("Secondary (Hex)", "#3B82F6"),
                "cta": best_color.get("CTA (Hex)", "#F97316"),
                "background": best_color.get("Background (Hex)", "#F8FAFC"),
                "text": best_color.get("Text (Hex)", "#1E293B"),
                "notes": best_color.get("Notes", "")
            },
            "typography": {
                "heading": best_typography.get("Heading Font", "Inter"),
                "body": best_typography.get("Body Font", "Inter"),
                "mood": best_typography.get("Mood/Style Keywords", reasoning.get("typography_mood", "")),
                "best_for": best_typography.get("Best For", ""),
                "google_fonts_url": best_typography.get("Google Fonts URL", ""),
                "css_import": best_typography.get("CSS Import", "")
            },
            "key_effects": combined_effects,
            "anti_patterns": "Mode-incompatible scaffold or generic fallback structure",
            "decision_rules": reasoning.get("decision_rules", {}),
            "severity": reasoning.get("severity", "MEDIUM"),
            "depth_rule": resolved_pattern.get("depth_rule", {}),
            "brain_design": brain_design,
            "style_safety_status": style_safety_status,
            "restricted_fallback_avoided": restricted_fallback_avoided,
            "restricted_style_used": restricted_style_used,
            "legacy_pattern_safety": safety_metadata,
            "quality_checklist": _mode_checklist(mode_quality_checklists, output_mode),
            "_style_payload_guards": style_payload_guards,
            "_mode_effect_language": mode_effect_language,
            "_mode_action_model": mode_action_model,
            "_niche_landing_action_notes": niche_landing_action_notes,
            "_mode_family_fallbacks": mode_family_fallbacks,
            "warnings": warnings
        }
        gate = run_anti_scaffold_gate(design_system)
        auto_repair_attempted = False
        auto_repair_result = "not needed"
        if gate["status"] != "PASS":
            auto_repair_attempted = True
            design_system = _auto_repair_design_system(
                design_system,
                depth_rules,
                structure_patterns,
                mode_style_profiles,
                mode_effect_language,
                mode_quality_checklists,
                niche_landing_patterns,
                mode_action_model,
                niche_landing_action_notes,
            )
            gate = run_anti_scaffold_gate(design_system)
            auto_repair_result = gate.get("status", "")
            resolved_pattern = design_system.get("pattern", resolved_pattern)
        design_system["anti_scaffold_gate"] = gate
        persist_allowed = gate.get("status") == "PASS"
        style_safety_status = design_system.get("style_safety_status", style_safety_status)
        design_system["receipt"] = {
            "detected_mode": output_mode,
            "product_family": product_family,
            "niche_family": niche_family,
            "brain_design_defer_status": "active" if brain_design.get("detected") else "standalone safe mode",
            "style_safety_status": style_safety_status,
            "depth_rule_applied": resolved_pattern.get("depth_rule", {}),
            "structure_pattern_used": resolved_pattern.get("name", ""),
            "anti_scaffold_gate_result": gate.get("status", ""),
            "failure_category": gate.get("failure_category", ""),
            "offending_terms": gate.get("offending_terms", []),
            "auto_repair_attempted": "yes" if auto_repair_attempted else "no",
            "auto_repair_result": auto_repair_result,
            "persist_allowed": "yes" if persist_allowed else "no",
            "restricted_fallback_avoided": "yes" if restricted_fallback_avoided else "no",
            "notes_for_brain_design_integration": brain_design.get("note", "")
        }
        if gate["status"] != "PASS":
            design_system["warnings"].append(f"Anti-scaffold gate: {gate['reason']} Fix: {gate['recommended_fix']}")
        return design_system


# ============ OUTPUT FORMATTERS ============
BOX_WIDTH = 90  # Wider box for more content

def format_ascii_box(design_system: dict) -> str:
    """Format design system as ASCII box with emojis (MCP-style)."""
    project = design_system.get("project_name", "PROJECT")
    pattern = design_system.get("pattern", {})
    style = design_system.get("style", {})
    colors = design_system.get("colors", {})
    typography = design_system.get("typography", {})
    effects = design_system.get("key_effects", "")
    anti_patterns = design_system.get("anti_patterns", "")
    gate = design_system.get("anti_scaffold_gate", {})
    warnings = design_system.get("warnings", [])
    receipt = design_system.get("receipt", {})
    checklist = design_system.get("quality_checklist", [])
    checklist = design_system.get("quality_checklist", [])
    product_family = design_system.get("product_family", "")
    niche_family = design_system.get("visible_niche_family", design_system.get("niche_family", ""))
    domain_context = design_system.get("domain_context", "")
    output_mode = design_system.get("output_mode", "")
    receipt = design_system.get("receipt", {})
    warnings = design_system.get("warnings", [])
    gate = design_system.get("anti_scaffold_gate", {})

    def wrap_text(text: str, prefix: str, width: int) -> list:
        """Wrap long text into multiple lines."""
        if not text:
            return []
        words = text.split()
        lines = []
        current_line = prefix
        for word in words:
            if len(current_line) + len(word) + 1 <= width - 2:
                current_line += (" " if current_line != prefix else "") + word
            else:
                if current_line != prefix:
                    lines.append(current_line)
                current_line = prefix + word
        if current_line != prefix:
            lines.append(current_line)
        return lines

    # Build sections from pattern
    sections = pattern.get("sections", "").split(">")
    sections = [s.strip() for s in sections if s.strip()]

    # Build output lines
    lines = []
    w = BOX_WIDTH - 1

    lines.append("+" + "-" * w + "+")
    lines.append(f"|  TARGET: {project} - RECOMMENDED DESIGN SYSTEM".ljust(BOX_WIDTH) + "|")
    lines.append(f"|  FAMILY: {product_family} / MODE: {output_mode}".ljust(BOX_WIDTH) + "|")
    if niche_family and niche_family != product_family:
        lines.append(f"|  NICHE FAMILY: {niche_family}".ljust(BOX_WIDTH) + "|")
    if domain_context:
        lines.append(f"|  DOMAIN CONTEXT: {domain_context}".ljust(BOX_WIDTH) + "|")
    lines.append("+" + "-" * w + "+")
    lines.append("|" + " " * BOX_WIDTH + "|")

    lines.append("|  OUTPUT RECEIPT:".ljust(BOX_WIDTH) + "|")
    receipt_items = [
        ("Detected mode", receipt.get("detected_mode", output_mode)),
        ("Product family", receipt.get("product_family", product_family)),
        ("Brain Design defer status", receipt.get("brain_design_defer_status", "")),
        ("Style safety status", receipt.get("style_safety_status", "")),
        ("Depth rule applied", str(receipt.get("depth_rule_applied", ""))),
        ("Structure pattern used", receipt.get("structure_pattern_used", "")),
        ("Anti-scaffold gate result", receipt.get("anti_scaffold_gate_result", "")),
        ("Failure category", receipt.get("failure_category", "")),
        ("Offending terms", ", ".join(receipt.get("offending_terms", [])) if isinstance(receipt.get("offending_terms"), list) else receipt.get("offending_terms", "")),
        ("Auto-repair attempted", receipt.get("auto_repair_attempted", "")),
        ("Auto-repair result", receipt.get("auto_repair_result", "")),
        ("Persist allowed", receipt.get("persist_allowed", "")),
        ("Restricted fallback avoided", receipt.get("restricted_fallback_avoided", "")),
    ]
    for label, value in receipt_items:
        for line in wrap_text(f"{label}: {value}", "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
    for line in wrap_text(f"Notes for Brain Design integration: {receipt.get('notes_for_brain_design_integration', '')}", "|     ", BOX_WIDTH):
        lines.append(line.ljust(BOX_WIDTH) + "|")
    lines.append("|" + " " * BOX_WIDTH + "|")

    # Pattern section
    lines.append(f"|  PATTERN: {pattern.get('name', '')}".ljust(BOX_WIDTH) + "|")
    action_model = pattern.get("action_model", {})
    if action_model:
        for line in wrap_text(f"{action_model.get('primary_action_label', 'Primary action')}: {action_model.get('action_goal', '')}", "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
    if output_mode in {"website", "ecommerce", "landing"} and pattern.get('conversion'):
        label = "Conversion goal" if output_mode == "landing" else "Conversion"
        for line in wrap_text(f"{label}: {pattern.get('conversion', '')}", "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
    if output_mode in {"website", "ecommerce", "landing"} and pattern.get('cta_placement'):
        label = "Landing CTA strategy" if output_mode == "landing" else "Primary CTA"
        for line in wrap_text(f"{label}: {pattern.get('cta_placement', '')}", "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
    if output_mode == "dashboard":
        for label, value in [
            ("Workflow Strategy", pattern.get("workflow_strategy", "")),
            ("Data Hierarchy", pattern.get("data_hierarchy", "")),
            ("State Coverage", pattern.get("state_coverage", "")),
        ]:
            for line in wrap_text(f"{label}: {value}", "|     ", BOX_WIDTH):
                lines.append(line.ljust(BOX_WIDTH) + "|")
    unit_label = pattern.get("unit_label", "sections").title()
    lines.append(f"|     {unit_label}:".ljust(BOX_WIDTH) + "|")
    for i, section in enumerate(sections, 1):
        lines.append(f"|       {i}. {section}".ljust(BOX_WIDTH) + "|")
    lines.append("|" + " " * BOX_WIDTH + "|")

    # Style section
    lines.append(f"|  STYLE: {style.get('name', '')}".ljust(BOX_WIDTH) + "|")
    if style.get("style_intent"):
        for line in wrap_text(f"Intent: {style.get('style_intent', '')}", "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
    if style.get("keywords"):
        for line in wrap_text(f"Keywords: {style.get('keywords', '')}", "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
    if style.get("layout_behavior"):
        for line in wrap_text(f"Layout: {style.get('layout_behavior', '')}", "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
    if style.get("effect_language"):
        for line in wrap_text(f"Effect language: {style.get('effect_language', '')}", "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
    if style.get("best_for"):
        for line in wrap_text(f"Best For: {style.get('best_for', '')}", "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
    if style.get("performance") or style.get("accessibility"):
        perf_a11y = f"Performance: {style.get('performance', '')} | Accessibility: {style.get('accessibility', '')}"
        lines.append(f"|     {perf_a11y}".ljust(BOX_WIDTH) + "|")
    lines.append("|" + " " * BOX_WIDTH + "|")

    # Colors section
    lines.append("|  COLORS:".ljust(BOX_WIDTH) + "|")
    lines.append(f"|     Primary:    {colors.get('primary', '')}".ljust(BOX_WIDTH) + "|")
    lines.append(f"|     Secondary:  {colors.get('secondary', '')}".ljust(BOX_WIDTH) + "|")
    lines.append(f"|     CTA:        {colors.get('cta', '')}".ljust(BOX_WIDTH) + "|")
    lines.append(f"|     Background: {colors.get('background', '')}".ljust(BOX_WIDTH) + "|")
    lines.append(f"|     Text:       {colors.get('text', '')}".ljust(BOX_WIDTH) + "|")
    if colors.get("notes"):
        for line in wrap_text(f"Notes: {colors.get('notes', '')}", "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
    lines.append("|" + " " * BOX_WIDTH + "|")

    # Typography section
    lines.append(f"|  TYPOGRAPHY: {typography.get('heading', '')} / {typography.get('body', '')}".ljust(BOX_WIDTH) + "|")
    if typography.get("mood"):
        for line in wrap_text(f"Mood: {typography.get('mood', '')}", "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
    if typography.get("best_for"):
        for line in wrap_text(f"Best For: {typography.get('best_for', '')}", "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
    if typography.get("google_fonts_url"):
        lines.append(f"|     Google Fonts: {typography.get('google_fonts_url', '')}".ljust(BOX_WIDTH) + "|")
    if typography.get("css_import"):
        lines.append(f"|     CSS Import: {typography.get('css_import', '')[:70]}...".ljust(BOX_WIDTH) + "|")
    lines.append("|" + " " * BOX_WIDTH + "|")

    # Key Effects section
    if effects:
        lines.append("|  KEY EFFECTS:".ljust(BOX_WIDTH) + "|")
        for line in wrap_text(effects, "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
        lines.append("|" + " " * BOX_WIDTH + "|")

    # Anti-patterns section
    if anti_patterns:
        lines.append("|  AVOID (Anti-patterns):".ljust(BOX_WIDTH) + "|")
        for line in wrap_text(anti_patterns, "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
        lines.append("|" + " " * BOX_WIDTH + "|")

    if gate:
        lines.append(f"|  ANTI-SCAFFOLD GATE: {gate.get('status', '')}".ljust(BOX_WIDTH) + "|")
        for line in wrap_text(gate.get("reason", ""), "|     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "|")
        lines.append("|" + " " * BOX_WIDTH + "|")

    if warnings:
        lines.append("|  WARNINGS:".ljust(BOX_WIDTH) + "|")
        for warning in warnings:
            for line in wrap_text(warning, "|     ", BOX_WIDTH):
                lines.append(line.ljust(BOX_WIDTH) + "|")
        lines.append("|" + " " * BOX_WIDTH + "|")

    # Pre-Delivery Checklist section
    lines.append("|  PRE-DELIVERY CHECKLIST:".ljust(BOX_WIDTH) + "|")
    checklist_items = [f"[ ] {item}" for item in checklist] or [
        "[ ] Structure follows product family depth, not generic fallback",
        "[ ] Mode-specific quality criteria checked"
    ]
    for item in checklist_items:
        lines.append(f"|     {item}".ljust(BOX_WIDTH) + "|")
    lines.append("|" + " " * BOX_WIDTH + "|")

    lines.append("+" + "-" * w + "+")

    return "\n".join(lines)


def format_markdown(design_system: dict) -> str:
    """Format design system as markdown."""
    project = design_system.get("project_name", "PROJECT")
    pattern = design_system.get("pattern", {})
    style = design_system.get("style", {})
    colors = design_system.get("colors", {})
    typography = design_system.get("typography", {})
    effects = design_system.get("key_effects", "")
    anti_patterns = design_system.get("anti_patterns", "")
    product_family = design_system.get("product_family", "")
    niche_family = design_system.get("visible_niche_family", design_system.get("niche_family", ""))
    domain_context = design_system.get("domain_context", "")
    output_mode = design_system.get("output_mode", "")
    warnings = design_system.get("warnings", [])
    gate = design_system.get("anti_scaffold_gate", {})
    receipt = design_system.get("receipt", {})
    checklist = design_system.get("quality_checklist", [])

    lines = []
    lines.append(f"## Design System: {project}")
    lines.append(f"**Product Family:** {product_family}  ")
    if niche_family and niche_family != product_family:
        lines.append(f"**Niche Family:** {niche_family}  ")
    if domain_context:
        lines.append(f"**Domain Context:** {domain_context}  ")
    lines.append(f"**Output Mode:** {output_mode}")
    lines.append("")

    lines.append("### Output Receipt")
    lines.append(f"- **Detected mode:** {receipt.get('detected_mode', output_mode)}")
    lines.append(f"- **Product family:** {receipt.get('product_family', product_family)}")
    lines.append(f"- **Brain Design defer status:** {receipt.get('brain_design_defer_status', '')}")
    lines.append(f"- **Style safety status:** {receipt.get('style_safety_status', '')}")
    lines.append(f"- **Depth rule applied:** `{receipt.get('depth_rule_applied', '')}`")
    lines.append(f"- **Structure pattern used:** {receipt.get('structure_pattern_used', '')}")
    lines.append(f"- **Anti-scaffold gate result:** {receipt.get('anti_scaffold_gate_result', '')}")
    lines.append(f"- **Failure category:** {receipt.get('failure_category', '')}")
    lines.append(f"- **Offending terms:** {receipt.get('offending_terms', '')}")
    lines.append(f"- **Auto-repair attempted:** {receipt.get('auto_repair_attempted', '')}")
    lines.append(f"- **Auto-repair result:** {receipt.get('auto_repair_result', '')}")
    lines.append(f"- **Persist allowed:** {receipt.get('persist_allowed', '')}")
    lines.append(f"- **Restricted fallback avoided:** {receipt.get('restricted_fallback_avoided', '')}")
    lines.append(f"- **Notes for Brain Design integration:** {receipt.get('notes_for_brain_design_integration', '')}")
    lines.append("")

    # Pattern section
    lines.append("### Pattern")
    lines.append(f"- **Name:** {pattern.get('name', '')}")
    action_model = pattern.get("action_model", {})
    if action_model:
        lines.append(f"- **{action_model.get('primary_action_label', 'Primary action')}:** {action_model.get('action_goal', '')}")
    if output_mode in {"website", "ecommerce", "landing"} and pattern.get('conversion'):
        label = "Conversion Goal" if output_mode == "landing" else "Conversion Focus"
        lines.append(f"- **{label}:** {pattern.get('conversion', '')}")
    if output_mode in {"website", "ecommerce", "landing"} and pattern.get('cta_placement'):
        label = "Landing CTA Strategy" if output_mode == "landing" else "Primary CTA"
        lines.append(f"- **{label}:** {pattern.get('cta_placement', '')}")
    if output_mode == "dashboard":
        lines.append(f"- **Workflow Strategy:** {pattern.get('workflow_strategy', '')}")
        lines.append(f"- **Data Hierarchy:** {pattern.get('data_hierarchy', '')}")
        lines.append(f"- **State Coverage:** {pattern.get('state_coverage', '')}")
    if pattern.get('color_strategy'):
        lines.append(f"- **Color Strategy:** {pattern.get('color_strategy', '')}")
    lines.append(f"- **{pattern.get('unit_label', 'sections').title()}:** {pattern.get('sections', '')}")
    if pattern.get("depth_rule"):
        lines.append(f"- **Depth Rule:** `{pattern.get('depth_rule', {})}`")
    lines.append("")

    # Style section
    lines.append("### Style")
    lines.append(f"- **Name:** {style.get('name', '')}")
    if style.get('style_intent'):
        lines.append(f"- **Intent:** {style.get('style_intent', '')}")
    if style.get('keywords'):
        lines.append(f"- **Keywords:** {style.get('keywords', '')}")
    if style.get('layout_behavior'):
        lines.append(f"- **Layout Behavior:** {style.get('layout_behavior', '')}")
    if style.get('effect_language'):
        lines.append(f"- **Effect Language:** {style.get('effect_language', '')}")
    if style.get('best_for'):
        lines.append(f"- **Best For:** {style.get('best_for', '')}")
    if style.get('performance') or style.get('accessibility'):
        lines.append(f"- **Performance:** {style.get('performance', '')} | **Accessibility:** {style.get('accessibility', '')}")
    lines.append("")

    # Colors section
    lines.append("### Colors")
    lines.append(f"| Role | Hex |")
    lines.append(f"|------|-----|")
    lines.append(f"| Primary | {colors.get('primary', '')} |")
    lines.append(f"| Secondary | {colors.get('secondary', '')} |")
    lines.append(f"| CTA | {colors.get('cta', '')} |")
    lines.append(f"| Background | {colors.get('background', '')} |")
    lines.append(f"| Text | {colors.get('text', '')} |")
    if colors.get("notes"):
        lines.append(f"\n*Notes: {colors.get('notes', '')}*")
    lines.append("")

    # Typography section
    lines.append("### Typography")
    lines.append(f"- **Heading:** {typography.get('heading', '')}")
    lines.append(f"- **Body:** {typography.get('body', '')}")
    if typography.get("mood"):
        lines.append(f"- **Mood:** {typography.get('mood', '')}")
    if typography.get("best_for"):
        lines.append(f"- **Best For:** {typography.get('best_for', '')}")
    if typography.get("google_fonts_url"):
        lines.append(f"- **Google Fonts:** {typography.get('google_fonts_url', '')}")
    if typography.get("css_import"):
        lines.append(f"- **CSS Import:**")
        lines.append(f"```css")
        lines.append(f"{typography.get('css_import', '')}")
        lines.append(f"```")
    lines.append("")

    # Key Effects section
    if effects:
        lines.append("### Key Effects")
        lines.append(f"{effects}")
        lines.append("")

    # Anti-patterns section
    if anti_patterns:
        lines.append("### Avoid (Anti-patterns)")
        newline_bullet = '\n- '
        lines.append(f"- {anti_patterns.replace(' + ', newline_bullet)}")
        lines.append("")

    if gate:
        lines.append("### Anti-Scaffold Gate")
        lines.append(f"- **Status:** {gate.get('status', '')}")
        lines.append(f"- **Reason:** {gate.get('reason', '')}")
        if gate.get("recommended_fix"):
            lines.append(f"- **Recommended Fix:** {gate.get('recommended_fix', '')}")
        lines.append("")

    if warnings:
        lines.append("### Warnings")
        for warning in warnings:
            lines.append(f"- {warning}")
        lines.append("")

    # Pre-Delivery Checklist section
    lines.append("### Pre-Delivery Checklist")
    for item in checklist:
        lines.append(f"- [ ] {item}")
    if not checklist:
        lines.append("- [ ] Structure follows product family depth, not generic fallback")
        lines.append("- [ ] Mode-specific quality criteria checked")
    lines.append("")

    return "\n".join(lines)


# ============ MAIN ENTRY POINT ============
def generate_design_system(query: str, project_name: str = None, output_format: str = "ascii", 
                           persist: bool = False, page: str = None, output_dir: str = None,
                           allow_failed_output: bool = False, allow_failed_persist: bool = False) -> str:
    """
    Main entry point for design system generation.

    Args:
        query: Search query (e.g., "SaaS dashboard", "e-commerce luxury")
        project_name: Optional project name for output header
        output_format: "ascii" (default) or "markdown"
        persist: If True, save design system to design-system/ folder
        page: Optional page name for page-specific override file
        output_dir: Optional output directory (defaults to current working directory)

    Returns:
        Formatted design system string
    """
    generator = DesignSystemGenerator()
    design_system = generator.generate(query, project_name)
    gate = design_system.get("anti_scaffold_gate", {})
    if gate.get("status") != "PASS":
        if not allow_failed_output:
            return _blocked_output_message(design_system, persist_requested=persist)
        design_system.setdefault("warnings", []).append("Unsafe failed output shown only because --allow-failed-output was used.")
    
    # Persist to files if requested
    if persist:
        if gate.get("status") != "PASS" and not allow_failed_persist:
            return _blocked_output_message(design_system, persist_requested=True)
        persist_design_system(design_system, page, output_dir, query)

    if output_format == "markdown":
        return format_markdown(design_system)
    return format_ascii_box(design_system)


# ============ PERSISTENCE FUNCTIONS ============
def persist_design_system(design_system: dict, page: str = None, output_dir: str = None, page_query: str = None) -> dict:
    """
    Persist design system to design-system/<project>/ folder using Master + Overrides pattern.
    
    Args:
        design_system: The generated design system dictionary
        page: Optional page name for page-specific override file
        output_dir: Optional output directory (defaults to current working directory)
        page_query: Optional query string for intelligent page override generation
    
    Returns:
        dict with created file paths and status
    """
    base_dir = Path(output_dir) if output_dir else Path.cwd()
    
    # Use project name for project-specific folder
    project_name = design_system.get("project_name", "default")
    project_slug = project_name.lower().replace(' ', '-')
    
    design_system_dir = base_dir / "design-system" / project_slug
    pages_dir = design_system_dir / "pages"
    
    created_files = []
    
    # Create directories
    design_system_dir.mkdir(parents=True, exist_ok=True)
    pages_dir.mkdir(parents=True, exist_ok=True)
    
    master_file = design_system_dir / "MASTER.md"
    
    # Generate and write MASTER.md
    master_content = format_master_md(design_system)
    with open(master_file, 'w', encoding='utf-8') as f:
        f.write(master_content)
    created_files.append(str(master_file))
    
    # If page is specified, create page override file with intelligent content
    if page:
        page_file = pages_dir / f"{page.lower().replace(' ', '-')}.md"
        page_content = format_page_override_md(design_system, page, page_query)
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(page_content)
        created_files.append(str(page_file))
    
    return {
        "status": "success",
        "design_system_dir": str(design_system_dir),
        "created_files": created_files
    }


def format_master_md(design_system: dict) -> str:
    """Format design system as MASTER.md with hierarchical override logic."""
    project = design_system.get("project_name", "PROJECT")
    pattern = design_system.get("pattern", {})
    style = design_system.get("style", {})
    colors = design_system.get("colors", {})
    typography = design_system.get("typography", {})
    effects = design_system.get("key_effects", "")
    anti_patterns = design_system.get("anti_patterns", "")
    gate = design_system.get("anti_scaffold_gate", {})
    warnings = design_system.get("warnings", [])
    receipt = design_system.get("receipt", {})
    checklist = design_system.get("quality_checklist", [])
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    lines = []
    
    # Logic header
    lines.append("# Design System Master File")
    lines.append("")
    lines.append("> **LOGIC:** When building a specific page, first check `design-system/pages/[page-name].md`.")
    lines.append("> If that file exists, its rules **override** this Master file.")
    lines.append("> If not, strictly follow the rules below.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"**Project:** {project}")
    lines.append(f"**Generated:** {timestamp}")
    lines.append(f"**Category:** {design_system.get('category', 'General')}")
    lines.append(f"**Product Family:** {design_system.get('product_family', '')}")
    visible_niche_family = design_system.get("visible_niche_family", design_system.get("niche_family", ""))
    if visible_niche_family and visible_niche_family != design_system.get("product_family"):
        lines.append(f"**Niche Family:** {visible_niche_family}")
    if design_system.get("domain_context"):
        lines.append(f"**Domain Context:** {design_system.get('domain_context', '')}")
    lines.append(f"**Output Mode:** {design_system.get('output_mode', '')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Brain Design Compatibility Note")
    lines.append("")
    lines.append(f"- **Brain Design defer status:** {receipt.get('brain_design_defer_status', '')}")
    lines.append(f"- **Style safety status:** {receipt.get('style_safety_status', '')}")
    lines.append(f"- **Depth rule applied:** `{receipt.get('depth_rule_applied', '')}`")
    lines.append(f"- **Structure pattern used:** {receipt.get('structure_pattern_used', '')}")
    lines.append(f"- **Anti-scaffold gate result:** {receipt.get('anti_scaffold_gate_result', '')}")
    lines.append(f"- **Failure category:** {receipt.get('failure_category', '')}")
    lines.append(f"- **Offending terms:** {receipt.get('offending_terms', '')}")
    lines.append(f"- **Auto-repair attempted:** {receipt.get('auto_repair_attempted', '')}")
    lines.append(f"- **Auto-repair result:** {receipt.get('auto_repair_result', '')}")
    lines.append(f"- **Persist allowed:** {receipt.get('persist_allowed', '')}")
    lines.append(f"- **Restricted fallback avoided:** {receipt.get('restricted_fallback_avoided', '')}")
    lines.append(f"- **Integration note:** {receipt.get('notes_for_brain_design_integration', '')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Global Rules section
    lines.append("## Global Rules")
    lines.append("")
    
    # Color Palette
    lines.append("### Color Palette")
    lines.append("")
    lines.append("| Role | Hex | CSS Variable |")
    lines.append("|------|-----|--------------|")
    lines.append(f"| Primary | `{colors.get('primary', '#2563EB')}` | `--brand-primary` |")
    lines.append(f"| Secondary | `{colors.get('secondary', '#3B82F6')}` | `--brand-secondary` |")
    lines.append(f"| CTA/Accent | `{colors.get('cta', '#F97316')}` | `--brand-accent` |")
    lines.append(f"| Background | `{colors.get('background', '#F8FAFC')}` | `--surface-page` |")
    lines.append(f"| Text | `{colors.get('text', '#1E293B')}` | `--text-primary` |")
    lines.append("")
    lines.append("Hex values are starting candidates only. When Brain Design provides style DNA, bind these semantic tokens to that direction rather than treating the fallback palette as universal.")
    lines.append("")
    if colors.get("notes"):
        lines.append(f"**Color Notes:** {colors.get('notes', '')}")
        lines.append("")
    
    # Typography
    lines.append("### Typography")
    lines.append("")
    lines.append(f"- **Heading Font:** `{typography.get('heading', 'Inter')}` via `--font-heading`")
    lines.append(f"- **Body Font:** `{typography.get('body', 'Inter')}` via `--font-body`")
    lines.append("- **Fallback note:** `Inter` is only a placeholder fallback; replace it according to style DNA / Brain Design typography direction.")
    if typography.get("mood"):
        lines.append(f"- **Mood:** {typography.get('mood', '')}")
    if typography.get("google_fonts_url"):
        lines.append(f"- **Google Fonts:** [{typography.get('heading', '')} + {typography.get('body', '')}]({typography.get('google_fonts_url', '')})")
    lines.append("")
    if typography.get("css_import"):
        lines.append("**CSS Import:**")
        lines.append("```css")
        lines.append(typography.get("css_import", ""))
        lines.append("```")
        lines.append("")
    
    # Spacing Variables
    lines.append("### Spacing Variables")
    lines.append("")
    lines.append("| Token | Value | Usage |")
    lines.append("|-------|-------|-------|")
    lines.append("| `--space-xs` | `4px` / `0.25rem` | Tight gaps |")
    lines.append("| `--space-sm` | `8px` / `0.5rem` | Icon gaps, inline spacing |")
    lines.append("| `--space-md` | `16px` / `1rem` | Standard padding |")
    lines.append("| `--space-lg` | `24px` / `1.5rem` | Section padding |")
    lines.append("| `--space-xl` | `32px` / `2rem` | Large gaps |")
    lines.append("| `--space-2xl` | `48px` / `3rem` | Section margins |")
    lines.append("| `--space-3xl` | `64px` / `4rem` | Hero padding |")
    lines.append("")

    lines.append("### Shape and Interaction Tokens")
    lines.append("")
    lines.append("| Token | Usage |")
    lines.append("|-------|-------|")
    lines.append("| `--radius-button` | Buttons and action controls; tune per product style DNA |")
    lines.append("| `--radius-card` | Cards, panels, and media containers; not one-size-fits-all |")
    lines.append("| `--radius-input` | Inputs, selects, and filter controls |")
    lines.append("| `--button-padding-x` | Horizontal action padding by density mode |")
    lines.append("| `--button-padding-y` | Vertical action padding by density mode |")
    lines.append("| `--container-max-width` | Main layout width by medium and content density |")
    lines.append("| `--modal-width-md` | Medium dialog width token |")
    lines.append("| `--modal-width-lg` | Large dialog width token |")
    lines.append("| `--focus-ring-color` | Focus ring color derived from `--brand-accent` |")
    lines.append("| `--surface-depth-low` | Static grouping with restrained semantic depth |")
    lines.append("| `--surface-depth-medium` | Elevated hierarchy for active groups |")
    lines.append("| `--surface-depth-high` | Modal/dialog/featured surface depth |")
    lines.append("")
    
    # Shadow Depths
    lines.append("### Shadow Depths")
    lines.append("")
    lines.append("| Level | Value | Usage |")
    lines.append("|-------|-------|-------|")
    lines.append("| `--surface-depth-low` | fallback shadow/elevation token | Subtle grouping |")
    lines.append("| `--surface-depth-medium` | fallback shadow/elevation token | Active cards, dropdowns |")
    lines.append("| `--surface-depth-high` | fallback shadow/elevation token | Modals, featured surfaces |")
    lines.append("")
    
    # Component Specs section
    lines.append("---")
    lines.append("")
    lines.append("## Component Specs")
    lines.append("")
    
    # Buttons
    lines.append("### Buttons")
    lines.append("")
    lines.append("```css")
    lines.append("/* Primary Button */")
    lines.append(".btn-primary {")
    lines.append("  background: var(--brand-accent);")
    lines.append("  color: var(--text-on-accent);")
    lines.append("  padding: var(--button-padding-y) var(--button-padding-x);")
    lines.append("  border-radius: var(--radius-button);")
    lines.append("  font-family: var(--font-body);")
    lines.append("  font-weight: 600;")
    lines.append("  transition: all 200ms ease;")
    lines.append("  cursor: pointer;")
    lines.append("}")
    lines.append("")
    lines.append(".btn-primary:hover {")
    lines.append("  opacity: 0.9;")
    lines.append("  transform: translateY(-1px);")
    lines.append("}")
    lines.append("")
    lines.append("/* Secondary Button */")
    lines.append(".btn-secondary {")
    lines.append(f"  background: transparent;")
    lines.append("  color: var(--brand-primary);")
    lines.append("  border: 2px solid var(--brand-primary);")
    lines.append("  padding: var(--button-padding-y) var(--button-padding-x);")
    lines.append("  border-radius: var(--radius-button);")
    lines.append("  font-family: var(--font-body);")
    lines.append("  font-weight: 600;")
    lines.append("  transition: all 200ms ease;")
    lines.append("  cursor: pointer;")
    lines.append("}")
    lines.append("```")
    lines.append("")
    
    # Cards
    lines.append("### Cards")
    lines.append("")
    lines.append("Choose card variants by role: static information card, clickable navigation card, product card, article card, dashboard metric card, or testimonial card.")
    lines.append("")
    lines.append("```css")
    lines.append(".card {")
    lines.append("  background: var(--surface-card);")
    lines.append("  border-radius: var(--radius-card);")
    lines.append("  padding: var(--card-padding);")
    lines.append("  box-shadow: var(--surface-depth-low);")
    lines.append("  transition: all 200ms ease;")
    lines.append("}")
    lines.append("")
    lines.append(".card--clickable {")
    lines.append("  cursor: pointer;")
    lines.append("}")
    lines.append("")
    lines.append(".card--clickable:hover {")
    lines.append("  box-shadow: var(--surface-depth-medium);")
    lines.append("  transform: translateY(-2px);")
    lines.append("}")
    lines.append("```")
    lines.append("")
    
    # Inputs
    lines.append("### Inputs")
    lines.append("")
    lines.append("```css")
    lines.append(".input {")
    lines.append("  padding: var(--input-padding-y) var(--input-padding-x);")
    lines.append("  border: 1px solid var(--border-input);")
    lines.append("  border-radius: var(--radius-input);")
    lines.append("  font-size: var(--font-size-input);")
    lines.append("  font-family: var(--font-body);")
    lines.append("  transition: border-color 200ms ease;")
    lines.append("}")
    lines.append("")
    lines.append(".input:focus {")
    lines.append("  border-color: var(--focus-ring-color);")
    lines.append("  outline: none;")
    lines.append("  box-shadow: 0 0 0 var(--focus-ring-width) var(--focus-ring-color);")
    lines.append("}")
    lines.append("```")
    lines.append("")
    
    # Modals
    lines.append("### Modals")
    lines.append("")
    lines.append("```css")
    lines.append(".modal-overlay {")
    lines.append("  background: rgba(0, 0, 0, 0.5);")
    lines.append("  backdrop-filter: blur(4px);")
    lines.append("}")
    lines.append("")
    lines.append(".modal {")
    lines.append("  background: var(--surface-modal);")
    lines.append("  border-radius: var(--radius-card);")
    lines.append("  padding: var(--modal-padding);")
    lines.append("  box-shadow: var(--surface-depth-high);")
    lines.append("  max-width: var(--modal-width-md);")
    lines.append("  width: 90%;")
    lines.append("}")
    lines.append("```")
    lines.append("")
    
    # Style section
    lines.append("---")
    lines.append("")
    lines.append("## Style Guidelines")
    lines.append("")
    lines.append(f"**Style:** {style.get('name', 'Reference-Led Visual Identity')}")
    lines.append("")
    if style.get("keywords"):
        lines.append(f"**Keywords:** {style.get('keywords', '')}")
        lines.append("")
    if style.get("best_for"):
        lines.append(f"**Best For:** {style.get('best_for', '')}")
        lines.append("")
    if effects:
        lines.append(f"**Key Effects:** {effects}")
        lines.append("")
    
    # Layout Pattern
    lines.append("### Page Pattern")
    lines.append("")
    lines.append(f"**Pattern Name:** {pattern.get('name', '')}")
    lines.append("")
    action_model = pattern.get("action_model", {})
    if action_model:
        lines.append(f"- **{action_model.get('primary_action_label', 'Primary action')}:** {action_model.get('action_goal', '')}")
    if design_system.get("output_mode") in {"website", "ecommerce", "landing"} and pattern.get('conversion'):
        label = "Conversion Goal" if design_system.get("output_mode") == "landing" else "Conversion Strategy"
        lines.append(f"- **{label}:** {pattern.get('conversion', '')}")
    if design_system.get("output_mode") in {"website", "ecommerce", "landing"} and pattern.get('cta_placement'):
        label = "Landing CTA Strategy" if design_system.get("output_mode") == "landing" else "Primary CTA"
        lines.append(f"- **{label}:** {pattern.get('cta_placement', '')}")
    if design_system.get("output_mode") == "dashboard":
        lines.append(f"- **Workflow Strategy:** {pattern.get('workflow_strategy', '')}")
        lines.append(f"- **Data Hierarchy:** {pattern.get('data_hierarchy', '')}")
        lines.append(f"- **State Coverage:** {pattern.get('state_coverage', '')}")
    lines.append(f"- **{pattern.get('unit_label', 'sections').title()}:** {pattern.get('sections', '')}")
    if pattern.get("depth_rule"):
        lines.append(f"- **Depth Rule:** `{pattern.get('depth_rule', {})}`")
    lines.append("")

    lines.append("### Anti-Scaffold Gate")
    lines.append("")
    lines.append(f"- **Status:** {gate.get('status', '')}")
    lines.append(f"- **Reason:** {gate.get('reason', '')}")
    if gate.get("recommended_fix"):
        lines.append(f"- **Recommended Fix:** {gate.get('recommended_fix', '')}")
    if warnings:
        for warning in warnings:
            lines.append(f"- **Warning:** {warning}")
    lines.append("")
    
    # Anti-Patterns section
    lines.append("---")
    lines.append("")
    lines.append("## Anti-Patterns (Do NOT Use)")
    lines.append("")
    if anti_patterns:
        anti_list = [a.strip() for a in anti_patterns.split("+")]
        for anti in anti_list:
            if anti:
                lines.append(f"- Do not: {anti}")
    lines.append("")
    lines.append("### Additional Forbidden Patterns")
    lines.append("")
    lines.append("- Do not use emojis as icons; use SVG icons such as Heroicons, Lucide, or Simple Icons.")
    lines.append("- Do not place cursor:pointer on static cards; only clickable variants should expose pointer affordance.")
    lines.append("- Do not use layout-shifting hovers; avoid scale transforms that shift layout.")
    lines.append("- Do not use low contrast text; maintain 4.5:1 minimum contrast ratio.")
    lines.append("- Do not use instant state changes for interactive controls; use transitions (150-300ms).")
    lines.append("- Do not ship invisible focus states; focus states must be visible for accessibility.")
    lines.append("- Do not reduce full website templates to generic Hero > Features > CTA scaffolds.")
    lines.append("")
    
    # Pre-Delivery Checklist
    lines.append("---")
    lines.append("")
    lines.append("## Pre-Delivery Checklist")
    lines.append("")
    lines.append("Before delivering any output, verify the mode-specific criteria:")
    lines.append("")
    for item in checklist:
        lines.append(f"- [ ] {item}")
    if not checklist:
        lines.append("- [ ] Product family depth and output mode were preserved")
        lines.append("- [ ] Mode-specific quality criteria checked")
    lines.append("")
    
    return "\n".join(lines)


def format_page_override_md(design_system: dict, page_name: str, page_query: str = None) -> str:
    """Format a page-specific override file with intelligent AI-generated content."""
    project = design_system.get("project_name", "PROJECT")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    page_title = page_name.replace("-", " ").replace("_", " ").title()
    
    # Detect page type and generate intelligent overrides
    page_overrides = _generate_intelligent_overrides(page_name, page_query, design_system)
    
    lines = []
    
    lines.append(f"# {page_title} Page Overrides")
    lines.append("")
    lines.append(f"> **PROJECT:** {project}")
    lines.append(f"> **Generated:** {timestamp}")
    lines.append(f"> **Page Type:** {page_overrides.get('page_type', 'General')}")
    lines.append("")
    lines.append("> ⚠️ **IMPORTANT:** Rules in this file **override** the Master file (`design-system/MASTER.md`).")
    lines.append("> Only deviations from the Master are documented here. For all other rules, refer to the Master.")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Page-specific rules with actual content
    lines.append("## Page-Specific Rules")
    lines.append("")
    
    # Layout Overrides
    lines.append("### Layout Overrides")
    lines.append("")
    layout = page_overrides.get("layout", {})
    if layout:
        for key, value in layout.items():
            lines.append(f"- **{key}:** {value}")
    else:
        lines.append("- No overrides — use Master layout")
    lines.append("")
    
    # Spacing Overrides
    lines.append("### Spacing Overrides")
    lines.append("")
    spacing = page_overrides.get("spacing", {})
    if spacing:
        for key, value in spacing.items():
            lines.append(f"- **{key}:** {value}")
    else:
        lines.append("- No overrides — use Master spacing")
    lines.append("")
    
    # Typography Overrides
    lines.append("### Typography Overrides")
    lines.append("")
    typography = page_overrides.get("typography", {})
    if typography:
        for key, value in typography.items():
            lines.append(f"- **{key}:** {value}")
    else:
        lines.append("- No overrides — use Master typography")
    lines.append("")
    
    # Color Overrides
    lines.append("### Color Overrides")
    lines.append("")
    colors = page_overrides.get("colors", {})
    if colors:
        for key, value in colors.items():
            lines.append(f"- **{key}:** {value}")
    else:
        lines.append("- No overrides — use Master colors")
    lines.append("")
    
    # Component Overrides
    lines.append("### Component Overrides")
    lines.append("")
    components = page_overrides.get("components", [])
    if components:
        for comp in components:
            lines.append(f"- {comp}")
    else:
        lines.append("- No overrides — use Master component specs")
    lines.append("")
    
    # Page-Specific Components
    lines.append("---")
    lines.append("")
    lines.append("## Page-Specific Components")
    lines.append("")
    unique_components = page_overrides.get("unique_components", [])
    if unique_components:
        for comp in unique_components:
            lines.append(f"- {comp}")
    else:
        lines.append("- No unique components for this page")
    lines.append("")
    
    # Recommendations
    lines.append("---")
    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    recommendations = page_overrides.get("recommendations", [])
    if recommendations:
        for rec in recommendations:
            lines.append(f"- {rec}")
    lines.append("")
    
    return "\n".join(lines)


def _generate_intelligent_overrides(page_name: str, page_query: str, design_system: dict) -> dict:
    """
    Generate intelligent overrides based on page type using layered search.
    
    Uses the existing search infrastructure to find relevant style, UX, and layout
    data instead of hardcoded page types.
    """
    try:
        from core import search
    except ImportError:  # pragma: no cover
        from .core import search
    
    page_lower = page_name.lower()
    query_lower = (page_query or "").lower()
    combined_context = f"{page_lower} {query_lower}"
    
    # Search across multiple domains for page-specific guidance
    style_search = search(combined_context, "style", max_results=1)
    ux_search = search(combined_context, "ux", max_results=3)
    landing_search = search(combined_context, "landing", max_results=1)
    
    # Extract results from search response
    style_results = style_search.get("results", [])
    ux_results = ux_search.get("results", [])
    landing_results = landing_search.get("results", [])
    
    # Detect page type from search results or context
    page_type = _detect_page_type(combined_context, style_results)
    
    # Build overrides from search results
    layout = {}
    spacing = {}
    typography = {}
    colors = {}
    components = []
    unique_components = []
    recommendations = []
    
    # Extract style-based overrides
    if style_results:
        style = style_results[0]
        style_name = style.get("Style Category", "")
        keywords = style.get("Keywords", "")
        best_for = style.get("Best For", "")
        effects = style.get("Effects & Animation", "")
        
        # Infer layout from style keywords
        if any(kw in keywords.lower() for kw in ["data", "dense", "dashboard", "grid"]):
            layout["Max Width"] = "1400px or full-width"
            layout["Grid"] = "12-column grid for data flexibility"
            spacing["Content Density"] = "High — optimize for information display"
        elif any(kw in keywords.lower() for kw in ["single", "focused"]):
            layout["Max Width"] = "960px or narrower if the page task requires focus"
            layout["Layout"] = "Focused layout derived from page purpose, not generic minimalism"
            spacing["Content Density"] = "Purpose-led density based on product family"
        else:
            layout["Max Width"] = "1200px (standard)"
            layout["Layout"] = "Full-width sections, centered content"
        
        if effects:
            recommendations.append(f"Effects: {effects}")
    
    # Extract UX guidelines as recommendations
    for ux in ux_results:
        category = ux.get("Category", "")
        do_text = ux.get("Do", "")
        dont_text = ux.get("Don't", "")
        if do_text:
            recommendations.append(f"{category}: {do_text}")
        if dont_text:
            components.append(f"Avoid: {dont_text}")
    
    # Extract landing pattern info for section structure
    if landing_results:
        landing = landing_results[0]
        sections = landing.get("Section Order", "")
        cta_placement = landing.get("Primary CTA Placement", "")
        color_strategy = landing.get("Color Strategy", "")
        
        if sections:
            layout["Sections"] = sections
        if cta_placement:
            recommendations.append(f"CTA Placement: {cta_placement}")
        if color_strategy:
            colors["Strategy"] = color_strategy
    
    # Add page-type specific defaults if no search results
    if not layout:
        layout["Max Width"] = "1200px"
        layout["Layout"] = "Responsive grid"
    
    if not recommendations:
        recommendations = [
            "Refer to MASTER.md for all design rules",
            "Add specific overrides as needed for this page"
        ]
    
    return {
        "page_type": page_type,
        "layout": layout,
        "spacing": spacing,
        "typography": typography,
        "colors": colors,
        "components": components,
        "unique_components": unique_components,
        "recommendations": recommendations
    }


def _detect_page_type(context: str, style_results: list) -> str:
    """Detect page type from context and search results."""
    context_lower = context.lower()
    
    # Check for common page type patterns
    page_patterns = [
        (["dashboard", "admin", "analytics", "data", "metrics", "stats", "monitor", "overview"], "Dashboard / Data View"),
        (["checkout", "payment", "cart", "purchase", "order", "billing"], "Checkout / Payment"),
        (["settings", "profile", "account", "preferences", "config"], "Settings / Profile"),
        (["landing", "marketing", "homepage", "hero", "home", "promo"], "Landing / Marketing"),
        (["login", "signin", "signup", "register", "auth", "password"], "Authentication"),
        (["pricing", "plans", "subscription", "tiers", "packages"], "Pricing / Plans"),
        (["blog", "article", "post", "news", "content", "story"], "Blog / Article"),
        (["product", "item", "detail", "pdp", "shop", "store"], "Product Detail"),
        (["search", "results", "browse", "filter", "catalog", "list"], "Search Results"),
        (["empty", "404", "error", "not found", "zero"], "Empty State"),
    ]
    
    for keywords, page_type in page_patterns:
        if any(kw in context_lower for kw in keywords):
            return page_type
    
    # Fallback: try to infer from style results
    if style_results:
        style_name = style_results[0].get("Style Category", "").lower()
        best_for = style_results[0].get("Best For", "").lower()
        
        if "dashboard" in best_for or "data" in best_for:
            return "Dashboard / Data View"
        elif "landing" in best_for or "marketing" in best_for:
            return "Landing / Marketing"
    
    return "General"


# ============ CLI SUPPORT ============
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate Design System")
    parser.add_argument("query", help="Search query (e.g., 'SaaS dashboard')")
    parser.add_argument("--project-name", "-p", type=str, default=None, help="Project name")
    parser.add_argument("--format", "-f", choices=["ascii", "markdown"], default="ascii", help="Output format")

    args = parser.parse_args()

    result = generate_design_system(args.query, args.project_name, args.format)
    print(result)
