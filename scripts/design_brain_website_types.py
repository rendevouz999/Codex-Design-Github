#!/usr/bin/env python
"""Website-template product type taxonomy helpers."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def taxonomy_path(root: Path | None = None) -> Path:
    base = root or repo_root()
    return base / ".design-brain" / "FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.json"


def aliases_path(root: Path | None = None) -> Path:
    base = root or repo_root()
    return base / ".design-brain" / "ROUTING_ALIASES_ID.json"


def load_taxonomy(root: Path | None = None) -> dict[str, Any]:
    try:
        return json.loads(taxonomy_path(root).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"routingPolicy": {}, "productTypes": []}


def load_aliases(root: Path | None = None) -> dict[str, Any]:
    try:
        return json.loads(aliases_path(root).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"aliases": {}, "phraseAliases": {}}


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def phrase_in_text(phrase: str, text: str) -> bool:
    phrase = normalize(phrase)
    if not phrase:
        return False
    pattern = r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])"
    return bool(re.search(pattern, text))


def normalize_for_routing(text: str, root: Path | None = None) -> str:
    """Return normalized text plus canonical aliases for mixed EN/ID prompts."""

    normalized = normalize(text)
    alias_data = load_aliases(root)
    expansions: list[str] = [normalized]

    for phrase, canonical_values in alias_data.get("phraseAliases", {}).items():
        phrase_norm = normalize(str(phrase))
        if phrase_in_text(phrase_norm, normalized):
            expansions.extend(normalize(str(value)) for value in canonical_values)

    for entry in alias_data.get("aliases", {}).values():
        if not isinstance(entry, dict):
            continue
        terms = [normalize(str(term)) for term in entry.get("terms", [])]
        if any(phrase_in_text(term, normalized) for term in terms):
            expansions.extend(normalize(str(value)) for value in entry.get("canonical", []))

    return normalize(" ".join(value for value in expansions if value))


def explicit_landing_intent(text: str, root: Path | None = None) -> bool:
    normalized = normalize_for_routing(text, root)
    policy = load_taxonomy(root).get("routingPolicy", {})
    terms = policy.get("explicitLandingTerms", [])
    if any(phrase_in_text(str(term), normalized) for term in terms):
        return True
    return bool(
        re.search(
            r"\b(landing|halaman landing|lead[- ]?gen|campaign|sales page|halaman penjualan|squeeze|waitlist)\b",
            normalized,
        )
    )


EMAIL_NEWSLETTER_EXPLICIT_TERMS = (
    "email newsletter",
    "newsletter email",
    "email template",
    "template email",
    "email campaign",
    "marketing email",
    "campaign email",
    "mailchimp",
    "edm",
    "e-mail",
    "newsletter untuk email",
)

EDITORIAL_WEBSITE_TERMS = (
    "blog website",
    "editorial website",
    "magazine website",
    "news website",
    "newsletter website",
    "template website berita majalah",
    "template website blog magazine",
    "website berita",
    "website majalah",
    "cms",
)

EXPLICIT_ECOMMERCE_TERMS = (
    "ecommerce",
    "e-commerce",
    "online store",
    "toko online",
    "product catalog",
    "product catalogue",
    "katalog produk",
    "cart",
    "keranjang",
    "checkout",
    "product page",
    "product listing",
    "sell products",
    "jual produk",
    "store ecommerce",
    "ecommerce store",
    "storefront",
    "product ecommerce",
    "ecommerce product",
    "shop product catalog",
    "catalog template",
    "fashion store",
    "jewelry store",
    "perhiasan ecommerce",
    "coffee bean online store",
    "coffee product ecommerce",
    "toko online kopi",
)

SAFE_MARKETPLACE_TEMPLATE_TERMS = (
    "marketplace template",
    "template marketplace",
    "marketplace-ready template",
    "marketplace ready template",
    "marketplace grade template",
    "marketplace-grade template",
    "editable marketplace template",
    "editable marketplace templates",
    "envato marketplace",
    "creative market",
    "ui8 marketplace",
    "figma marketplace",
    "template buyer",
    "marketplace buyer",
    "template marketplace buyer",
    "marketplace product quality",
    "marketplace quality gate",
    "marketplace preview",
    "marketplace listing preview",
    "sellable marketplace template",
)

TRUE_MARKETPLACE_ECOMMERCE_TERMS = (
    "ecommerce marketplace",
    "e-commerce marketplace",
    "product marketplace",
    "vendor marketplace",
    "multi-vendor marketplace",
    "multivendor marketplace",
    "online marketplace",
    "seller marketplace",
    "buyer seller marketplace",
    "marketplace app",
    "marketplace platform",
    "marketplace storefront",
    "booking marketplace",
    "property marketplace",
    "job marketplace",
    "service marketplace",
    "marketplace with cart",
    "marketplace checkout",
    "product listing marketplace",
)

HOSPITALITY_NOT_SHOP_TERMS = (
    "coffee shop",
    "cafe",
    "kafe",
    "restaurant",
    "restoran",
    "rumah makan",
    "hospitality",
    "reservation",
    "reservasi",
    "venue",
    "hotel",
)

PRICING_NOT_ECOMMERCE_TERMS = (
    "pricing page",
    "pricing table",
    "pricing section",
    "saas pricing",
    "service pricing",
    "hotel booking pricing",
)


def explicit_email_newsletter_intent(text: str, root: Path | None = None) -> bool:
    normalized = normalize_for_routing(text, root)
    return any(phrase_in_text(term, normalized) for term in EMAIL_NEWSLETTER_EXPLICIT_TERMS)


def mask_safe_marketplace_template_context(text: str) -> str:
    masked = normalize(text)
    for phrase in SAFE_MARKETPLACE_TEMPLATE_TERMS:
        if phrase_in_text(phrase, masked):
            masked = re.sub(
                r"(?<![a-z0-9])" + re.escape(normalize(phrase)) + r"(?![a-z0-9])",
                " template distribution context ",
                masked,
            )
    return normalize(masked)


def explicit_ecommerce_intent(text: str, root: Path | None = None) -> bool:
    normalized = normalize_for_routing(text, root)
    ecommerce_text = mask_safe_marketplace_template_context(normalized)
    if has_any_phrase(ecommerce_text, TRUE_MARKETPLACE_ECOMMERCE_TERMS):
        return True
    if has_any_phrase(ecommerce_text, EXPLICIT_ECOMMERCE_TERMS):
        return True
    # Product-family words can support ecommerce, but hospitality phrases block
    # accidental "coffee shop" / restaurant routing.
    product_category_terms = (
        "fashion",
        "perhiasan",
        "jewelry",
        "furniture",
        "furnitur",
        "luxury furniture",
    )
    if has_any_phrase(ecommerce_text, product_category_terms) and not has_any_phrase(normalized, HOSPITALITY_NOT_SHOP_TERMS):
        return True
    return False


def hospitality_website_intent(text: str, root: Path | None = None) -> bool:
    normalized = normalize_for_routing(text, root)
    return has_any_phrase(normalized, HOSPITALITY_NOT_SHOP_TERMS)


def pricing_without_ecommerce_intent(text: str, root: Path | None = None) -> bool:
    normalized = normalize_for_routing(text, root)
    return has_any_phrase(normalized, PRICING_NOT_ECOMMERCE_TERMS) and not explicit_ecommerce_intent(normalized, root)


def editorial_website_intent(text: str, root: Path | None = None) -> bool:
    normalized = normalize_for_routing(text, root)
    return any(phrase_in_text(term, normalized) for term in EDITORIAL_WEBSITE_TERMS) or bool(
        re.search(r"\b(blog|editorial|magazine|news|majalah|berita|publication|cms)\b", normalized)
        and re.search(r"\b(website|web|situs|template website|website template|cms)\b", normalized)
    )


def website_intent(text: str, root: Path | None = None) -> bool:
    normalized = normalize_for_routing(text, root)
    return bool(
        re.search(
            r"\b(website|web|situs|situs web|template website|web template|homepage|figma website|saas|software|app website|"
            r"ecommerce|e-commerce|shop|store|portfolio|agency|studio|blog|editorial|"
            r"magazine|news|majalah|berita|newsletter website|cms|dashboard|admin|docs|documentation|course|lms|community|nonprofit|event|"
            r"travel|hotel|real estate|directory|listing|restoran|restaurant|keuangan|finance|"
            r"properti|kursus|sewa|rental|toko|perhiasan)\b",
            normalized,
        )
    )


def has_any_phrase(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase_in_text(phrase, text) for phrase in phrases)


AGENCY_STUDIO_TERMS = (
    "agency website",
    "creative agency website",
    "agensi kreatif website",
    "studio website",
    "design studio website",
    "branding agency",
    "digital agency",
    "production studio",
    "creative studio",
    "studio service",
    "agency service",
    "agency landing",
    "studio landing",
    "template website agency",
    "agency website template",
    "template website agensi kreatif",
)

PORTFOLIO_CASE_TERMS = (
    "portfolio",
    "portofolio",
    "personal portfolio",
    "personal website",
    "case study",
    "case study site",
    "studi kasus",
    "selected works",
    "projects showcase",
    "designer portfolio",
    "developer portfolio",
    "photographer portfolio",
    "creator portfolio",
)

FINANCE_CONSULTING_TERMS = (
    "finance",
    "financial",
    "financial consultant",
    "financial consulting",
    "consulting",
    "consultant",
    "accounting",
    "investment",
    "advisory",
    "business consultant",
    "tax consultant",
    "wealth management",
    "keuangan",
    "finansial",
    "konsultan",
    "konsultasi",
    "konsultasi keuangan",
    "konsultan keuangan",
    "akuntansi",
    "pajak",
    "investasi",
    "penasihat keuangan",
    "manajemen keuangan",
)

TRAVEL_HOSPITALITY_TERMS = (
    "travel agency",
    "travel booking",
    "tour",
    "hotel",
    "resort",
    "venue",
    "event venue",
    "restaurant",
    "restoran",
    "cafe",
    "kafe",
    "reservation",
    "reservasi",
    "hospitality",
    "trip booking",
    "destination",
    "agen travel",
    "perjalanan",
    "wisata",
    "penginapan",
    "tempat acara",
    "wedding venue",
)


SAAS_PRODUCT_TERMS = (
    "saas",
    "ai saas",
    "saas website",
    "software website",
    "app website",
    "product website",
    "startup website",
    "platform website",
    "ai platform",
    "tech product",
    "product marketing",
    "product ui",
    "demo cta",
    "integrations",
)

STRICT_PORTFOLIO_INTENT_TERMS = (
    "portfolio",
    "personal portfolio",
    "personal website",
    "resume website",
    "cv website",
    "designer portfolio",
    "developer portfolio",
    "photographer portfolio",
    "creator portfolio",
    "personal brand",
    "selected works",
    "projects showcase",
)

STRICT_EDITORIAL_INTENT_TERMS = (
    "blog website",
    "editorial website",
    "magazine website",
    "news website",
    "publication website",
    "cms website",
    "newsletter website",
    "media site",
)

STRICT_DASHBOARD_INTENT_TERMS = (
    "dashboard template",
    "admin template",
    "analytics dashboard template",
    "dashboard website",
    "admin panel",
    "crm dashboard",
    "web app dashboard",
    "saas dashboard",
)

STRICT_DOCS_INTENT_TERMS = (
    "documentation website",
    "docs website",
    "help center",
    "knowledge base",
    "developer docs",
    "api docs",
    "documentation template",
)

EDITORIAL_BLOG_CMS_TERMS = (
    "blog",
    "blog website",
    "editorial",
    "editorial website",
    "magazine",
    "magazine website",
    "news",
    "news website",
    "publication",
    "cms",
    "newsletter website",
    "media site",
    "majalah",
    "berita",
    "berita majalah",
    "publikasi",
    "template website berita majalah",
    "template website blog magazine",
)


def score_record(record: dict[str, Any], text: str, root: Path | None = None) -> int:
    raw_normalized = normalize(text)
    normalized = normalize_for_routing(text, root)
    marketplace_ecommerce_context = has_any_phrase(
        mask_safe_marketplace_template_context(normalized),
        TRUE_MARKETPLACE_ECOMMERCE_TERMS,
    )
    record_id = str(record.get("id", ""))
    if record_id == "landing_page_campaign" and not explicit_landing_intent(normalized, root):
        return -999

    score = 0
    generic_triggers = {
        "figma website template",
        "website template",
        "web template",
        "homepage template",
        "template website",
    }
    for trigger in record.get("routingTriggers", []):
        phrase = normalize(str(trigger))
        if not phrase:
            continue
        if phrase_in_text(phrase, normalized):
            if record_id == "multipurpose_website_template" and phrase in generic_triggers:
                score += 2
            else:
                score += 12 + min(len(phrase.split()), 4)
    if record_id == "multipurpose_website_template" and website_intent(normalized, root):
        score += 2
    saas_context = has_any_phrase(normalized, SAAS_PRODUCT_TERMS)
    if record_id == "saas_product_website" and saas_context:
        score += 80
    if record_id == "agency_studio_website" and has_any_phrase(normalized, AGENCY_STUDIO_TERMS):
        score += 45
    if record_id == "personal_portfolio_case_study" and has_any_phrase(normalized, PORTFOLIO_CASE_TERMS):
        score += 45
    if (
        record_id == "personal_portfolio_case_study"
        and has_any_phrase(normalized, TRAVEL_HOSPITALITY_TERMS)
        and not has_any_phrase(raw_normalized, STRICT_PORTFOLIO_INTENT_TERMS)
    ):
        score -= 90
    if (
        record_id == "personal_portfolio_case_study"
        and saas_context
        and not has_any_phrase(raw_normalized, STRICT_PORTFOLIO_INTENT_TERMS)
    ):
        score -= 140
    if (
        record_id == "personal_portfolio_case_study"
        and has_any_phrase(normalized, AGENCY_STUDIO_TERMS)
        and not has_any_phrase(normalized, PORTFOLIO_CASE_TERMS)
    ):
        score -= 30
    if record_id == "corporate_business_website" and has_any_phrase(normalized, FINANCE_CONSULTING_TERMS):
        score += 45
    if record_id == "professional_service_booking" and has_any_phrase(normalized, FINANCE_CONSULTING_TERMS):
        score -= 18
    if record_id == "event_venue_travel_booking" and has_any_phrase(normalized, TRAVEL_HOSPITALITY_TERMS):
        score += 45
    if record_id == "professional_service_booking" and has_any_phrase(normalized, TRAVEL_HOSPITALITY_TERMS):
        score -= 18
    if record_id == "marketplace_listing_directory" and marketplace_ecommerce_context:
        score += 70
    if record_id == "professional_service_booking" and marketplace_ecommerce_context:
        score -= 30
    if record_id == "editorial_blog_cms" and has_any_phrase(normalized, EDITORIAL_BLOG_CMS_TERMS):
        score += 45
    if record_id == "editorial_blog_cms" and saas_context and not has_any_phrase(raw_normalized, STRICT_EDITORIAL_INTENT_TERMS):
        score -= 120
    if record_id == "dashboard_admin_web_app" and saas_context and not has_any_phrase(raw_normalized, STRICT_DASHBOARD_INTENT_TERMS):
        score -= 80
    if record_id == "documentation_help_center" and saas_context and not has_any_phrase(raw_normalized, STRICT_DOCS_INTENT_TERMS):
        score -= 80
    if record_id == "multipurpose_website_template" and (
        has_any_phrase(normalized, AGENCY_STUDIO_TERMS)
        or has_any_phrase(normalized, PORTFOLIO_CASE_TERMS)
        or has_any_phrase(normalized, FINANCE_CONSULTING_TERMS)
        or has_any_phrase(normalized, TRAVEL_HOSPITALITY_TERMS)
        or has_any_phrase(normalized, EDITORIAL_BLOG_CMS_TERMS)
    ):
        score -= 20
    return score


def select_website_product_type(text: str, root: Path | None = None) -> dict[str, Any]:
    taxonomy = load_taxonomy(root)
    records = [record for record in taxonomy.get("productTypes", []) if isinstance(record, dict)]
    if not records:
        return {}

    scored = sorted(
        ((score_record(record, text, root), index, record) for index, record in enumerate(records)),
        key=lambda item: (-item[0], item[1]),
    )
    landing = [item for item in scored if item[2].get("id") == "landing_page_campaign" and item[0] > 0]
    if explicit_landing_intent(text, root) and landing:
        return landing[0][2]

    specific = [
        item
        for item in scored
        if item[2].get("id") not in {"multipurpose_website_template", "landing_page_campaign"} and item[0] > 0
    ]
    if specific:
        return specific[0][2]

    if scored and scored[0][0] > 0:
        return scored[0][2]

    default_id = str(taxonomy.get("routingPolicy", {}).get("defaultWebsiteType") or "multipurpose_website_template")
    for record in records:
        if record.get("id") == default_id:
            return record
    return records[0]


def matched_phrases(text: str, phrases: list[Any]) -> list[str]:
    normalized = normalize(text)
    result: list[str] = []
    for phrase in phrases:
        value = normalize(str(phrase))
        if phrase_in_text(value, normalized):
            result.append(str(phrase))
    return result


def signal_matches(record: dict[str, Any], text: str) -> list[str]:
    return matched_phrases(text, record.get("requiredSignals", []))


def page_map_matches(record: dict[str, Any], text: str) -> list[str]:
    return matched_phrases(text, record.get("requiredPagesOrScreens", []))


def concise_standard(record: dict[str, Any]) -> str:
    if not record:
        return "No website product type selected."
    return f"{record.get('name', 'Unknown')}: {record.get('standardRange', 'No standard range defined')}"
