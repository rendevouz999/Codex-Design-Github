#!/usr/bin/env python3
"""Smoke tests for Design Craft v0.2.7 behavior."""

from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from core import detect_domain  # noqa: E402
from design_system import DesignSystemGenerator, generate_design_system, run_anti_scaffold_gate  # noqa: E402
from search import format_output  # noqa: E402
from core import search as corpus_search  # noqa: E402

TOTAL_CHECKS = 0
LANDING_FORBIDDEN = [
    "Minimal text",
    "white space heavy",
    "single column layout",
    "direct messaging",
    "minimal animations",
    "very subtle hover effects",
    "Minimal & Direct",
]
PRESENTATION_FORBIDDEN = [
    "Parallax",
    "scroll-driven",
    "scroll-triggered",
    "sticky",
    "hover effects",
    "position fixed",
    "position sticky",
]
WEB_CHECKLIST_LEAKS = [
    "hover states",
    "responsive 375/768/1024/1440",
    "375px, 768px, 1024px, 1440px",
    "prefers-reduced-motion",
    "keyboard focus states",
]


def _generate(query: str) -> dict:
    return DesignSystemGenerator().generate(query, "Smoke Test")


def _assert(condition: bool, message: str, failures: list[str]) -> None:
    global TOTAL_CHECKS
    TOTAL_CHECKS += 1
    if not condition:
        failures.append(message)


def _assert_not_contains(text: str, terms: list[str], label: str, failures: list[str]) -> None:
    for term in terms:
        _assert(term.lower() not in text.lower(), f"{label}: leaked forbidden term {term!r}", failures)


def _assert_contains(text: str, terms: list[str], label: str, failures: list[str]) -> None:
    for term in terms:
        _assert(term.lower() in text.lower(), f"{label}: missing required term {term!r}", failures)


def test_product_families(failures: list[str]) -> None:
    cases = [
        ("template website restoran", "restaurant_hospitality"),
        ("template website keuangan", "finance_consulting"),
        ("template website sewa alat", "equipment_rental_service"),
        ("template website perhiasan ecommerce", "jewelry_ecommerce"),
        ("template website kafe", "restaurant_hospitality"),
        ("template website agensi kreatif", "agency_portfolio"),
        ("luxury furniture website template", "luxury_furniture"),
        ("coffee shop website template", "restaurant_hospitality"),
        ("financial consultant website template", "finance_consulting"),
        ("equipment rental website template", "equipment_rental_service"),
        ("jewelry ecommerce website template", "jewelry_ecommerce"),
        ("creative agency portfolio template", "agency_portfolio"),
        ("template website properti", "real_estate_property"),
        ("real estate website template", "real_estate_property"),
        ("online course website template", "education_course"),
        ("template website kursus online", "education_course"),
        ("medical clinic website template", "medical_clinic"),
        ("template website klinik", "medical_clinic"),
        ("beauty salon website template", "beauty_wellness"),
        ("template website klinik kecantikan", "beauty_wellness"),
        ("car rental website template", "car_rental_transport"),
        ("template website sewa mobil", "car_rental_transport"),
        ("email newsletter template", "email_newsletter"),
        ("template website fashion", "fashion_apparel_ecommerce"),
        ("template website toko baju", "fashion_apparel_ecommerce"),
        ("fashion ecommerce website template", "fashion_apparel_ecommerce"),
        ("clothing shop website template", "fashion_apparel_ecommerce"),
        ("template website sewa furniture", "furniture_rental_service"),
        ("furniture rental website template", "furniture_rental_service"),
    ]
    for query, expected in cases:
        result = _generate(query)
        _assert(
            result["product_family"] == expected,
            f"{query!r}: expected family {expected}, got {result['product_family']}",
            failures,
        )


def test_non_landing_products(failures: list[str]) -> None:
    cases = [
        ("dashboard analytics finance", "dashboard_admin", "dashboard"),
        ("dashboard POS kasir", "dashboard_admin", "dashboard"),
        ("mobile app fintech onboarding", "mobile_app", "mobile_app"),
        ("pitch deck finance presentation", "presentation_deck", "presentation"),
    ]
    for query, family, mode in cases:
        result = _generate(query)
        sections = result["pattern"]["sections"].lower()
        _assert(result["product_family"] == family, f"{query!r}: expected {family}, got {result['product_family']}", failures)
        _assert(result["output_mode"] == mode, f"{query!r}: expected mode {mode}, got {result['output_mode']}", failures)
        _assert("hero > features > cta" not in sections, f"{query!r}: used forbidden landing scaffold", failures)
        if mode == "dashboard":
            _assert("kpi summary" in sections and "data table" in sections, f"{query!r}: missing dashboard modules", failures)


def test_anti_bug_cases(failures: list[str]) -> None:
    _assert(detect_domain("luxury furniture website template") != "ux", "luxury incorrectly detected as UX", failures)

    coffee = _generate("coffee shop website template")
    _assert(coffee["product_family"] == "restaurant_hospitality", "coffee shop routed away from hospitality", failures)

    pricing = _generate("pricing page website template")
    _assert(pricing["output_mode"] != "ecommerce", "pricing page routed to ecommerce without ecommerce context", failures)

    ecommerce_pricing = _generate("ecommerce pricing product page")
    _assert(ecommerce_pricing["output_mode"] == "ecommerce", "ecommerce pricing product page should allow ecommerce mode", failures)


def test_anti_minimalist_depth(failures: list[str]) -> None:
    website_queries = [
        "template website restoran",
        "template website keuangan",
        "template website sewa alat",
        "template website perhiasan ecommerce",
        "luxury furniture website template",
        "coffee shop website template",
        "equipment rental website template",
        "template website properti",
        "template website kursus online",
        "template website klinik kecantikan",
    ]
    for query in website_queries:
        result = _generate(query)
        pattern = result["pattern"]
        style_name = result["style"]["name"].lower()
        gate = run_anti_scaffold_gate(result)
        sections = pattern["sections"].lower()
        minimum = pattern.get("depth_rule", {}).get("min_sections", 0)
        _assert("hero > features > cta" not in sections, f"{query!r}: generic landing scaffold", failures)
        _assert(style_name not in {"minimalism", "flat design", "minimal & direct", "minimal single column"}, f"{query!r}: defaulted to {style_name}", failures)
        _assert(pattern.get("section_count", 0) >= minimum, f"{query!r}: below depth rule", failures)
        _assert(gate["status"] == "PASS", f"{query!r}: gate failed: {gate}", failures)

    minimal_landing = _generate("minimalist landing page")
    _assert(minimal_landing["output_mode"] == "landing", "minimalist landing page should remain landing mode", failures)


def test_portability_and_email(failures: list[str]) -> None:
    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    _assert("C:\\Users\\Admin\\Desktop\\Codex-Design" not in skill_text, "SKILL.md contains hardcoded Codex-Design path", failures)
    _assert("C:\\Users\\Admin" not in skill_text, "SKILL.md contains hardcoded personal path", failures)

    newsletter_site = _generate("newsletter website template")
    _assert(newsletter_site["product_family"] != "email_newsletter", "newsletter website template should not be email_newsletter", failures)

    email = _generate("email newsletter template")
    _assert(email["product_family"] == "email_newsletter", "email newsletter template should use email_newsletter", failures)
    _assert(email["output_mode"] == "email", "email newsletter template should use email output mode", failures)


def test_output_receipt(failures: list[str]) -> None:
    output = generate_design_system("template website properti", output_format="ascii")
    required = [
        "OUTPUT RECEIPT",
        "Detected mode",
        "Product family",
        "Brain Design defer status",
        "Style safety status",
        "Depth rule applied",
        "Structure pattern used",
        "Anti-scaffold gate result",
        "Auto-repair attempted",
        "Auto-repair result",
        "Persist allowed",
        "Restricted fallback avoided",
    ]
    for phrase in required:
        _assert(phrase in output, f"design-system output missing receipt phrase: {phrase}", failures)


def test_raw_search_safety_label(failures: list[str]) -> None:
    result = corpus_search("hero features cta", "landing", 3)
    output = format_output(result)
    _assert("Safety:" in output, "raw landing search should label restricted legacy patterns when returned", failures)


def test_landing_mode(failures: list[str]) -> None:
    cases = [
        ("finance landing page", "finance_consulting"),
        ("template landing page keuangan", "finance_consulting"),
        ("restaurant landing page", "restaurant_hospitality"),
        ("landing page restoran", "restaurant_hospitality"),
    ]
    for query, family in cases:
        result = _generate(query)
        _assert(result["output_mode"] == "landing", f"{query!r}: expected landing mode, got {result['output_mode']}", failures)
        _assert(result["product_family"] == family, f"{query!r}: expected family {family}, got {result['product_family']}", failures)
        _assert(result["anti_scaffold_gate"]["status"] == "PASS", f"{query!r}: landing gate failed", failures)


def test_presentation_modes(failures: list[str]) -> None:
    cases = [
        "pptx template finance",
        "template ppt restoran",
        "Google Slides pitch deck finance",
        "Keynote template agency",
    ]
    for query in cases:
        result = _generate(query)
        sections = result["pattern"]["sections"].lower()
        _assert(result["output_mode"] == "presentation", f"{query!r}: expected presentation mode", failures)
        _assert(result["product_family"] == "presentation_deck", f"{query!r}: expected presentation_deck", failures)
        _assert("cover slide" in sections and "cta/closing slide" in sections, f"{query!r}: missing slide system", failures)
        _assert("product-specific hero" not in sections, f"{query!r}: used website section order", failures)


def test_static_brand_menu_social_modes(failures: list[str]) -> None:
    cases = [
        ("logo design restaurant", "brand_kit"),
        ("brand identity restaurant", "brand_kit"),
        ("social media post restaurant", "social_post"),
        ("poster menu restaurant", "menu_design"),
        ("restaurant menu design", "menu_design"),
    ]
    for query, mode in cases:
        result = _generate(query)
        _assert(result["output_mode"] == mode, f"{query!r}: expected mode {mode}, got {result['output_mode']}", failures)
        _assert("product-specific hero" not in result["pattern"]["sections"].lower(), f"{query!r}: used website structure", failures)


def test_ui_kit_component_modes(failures: list[str]) -> None:
    cases = [
        ("ui kit dashboard components", {"ui_kit", "component_library"}),
        ("design system component library", {"design_system", "component_library"}),
        ("dashboard component library", {"component_library"}),
    ]
    for query, allowed_modes in cases:
        result = _generate(query)
        sections = result["pattern"]["sections"].lower()
        _assert(result["output_mode"] in allowed_modes, f"{query!r}: expected one of {allowed_modes}, got {result['output_mode']}", failures)
        _assert("component states" in sections or "state coverage" in sections, f"{query!r}: missing component states", failures)
        _assert("tokens" in sections or "token foundations" in sections, f"{query!r}: missing tokens", failures)


def test_furniture_and_onboarding_edges(failures: list[str]) -> None:
    furniture = _generate("furniture rental website template")
    _assert(furniture["product_family"] in {"furniture_rental_service", "equipment_rental_service"}, "furniture rental should route to rental/service", failures)
    _assert(furniture["product_family"] != "luxury_furniture", "furniture rental incorrectly routed to luxury furniture", failures)

    luxury = _generate("luxury furniture website template")
    _assert(luxury["product_family"] == "luxury_furniture", "luxury furniture should remain luxury_furniture", failures)

    for query in ["saas onboarding website template", "employee onboarding website template"]:
        result = _generate(query)
        _assert(result["output_mode"] != "mobile_app", f"{query!r}: onboarding without app context became mobile_app", failures)
    landing = _generate("onboarding landing page")
    _assert(landing["output_mode"] == "landing", "onboarding landing page should be landing", failures)
    for query in ["mobile app onboarding screens", "fintech app onboarding"]:
        result = _generate(query)
        _assert(result["output_mode"] == "mobile_app", f"{query!r}: explicit app onboarding should be mobile_app", failures)


def test_json_safety_metadata(failures: list[str]) -> None:
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "search.py"), "hero features cta", "--domain", "landing", "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    _assert(completed.returncode == 0, "JSON safety command failed", failures)
    payload = json.loads(completed.stdout)
    restricted = [row for row in payload.get("results", []) if row.get("is_restricted")]
    _assert(bool(restricted), "JSON output should mark restricted results", failures)
    if restricted:
        row = restricted[0]
        for field in ["is_restricted", "safety_scope", "risk_level", "forbidden_when", "recommended_replacement"]:
            _assert(field in row, f"JSON restricted result missing {field}", failures)


def test_component_tokens_and_persist_gate(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        output = generate_design_system(
            "saas dashboard",
            project_name="Token Test",
            output_format="markdown",
            persist=True,
            page="dashboard",
            output_dir=tmp,
        )
        master = Path(tmp) / "design-system" / "token-test" / "MASTER.md"
        _assert(master.exists(), "PASS design system should persist", failures)
        text = master.read_text(encoding="utf-8") if master.exists() else output
        for token in ["--radius-button", "--radius-card", "--font-heading", "--font-body", "--brand-accent"]:
            _assert(token in text, f"persisted design system missing token {token}", failures)
        for forbidden in ["border-radius: 8px", "max-width: 500px"]:
            _assert(forbidden not in text, f"persisted design system contains fixed universal value {forbidden}", failures)
        _assert("Anti-scaffold gate result: PASS" in text or "**Status:** PASS" in text, "persisted output should show PASS gate", failures)


def test_landing_payload_content(failures: list[str]) -> None:
    cases = {
        "landing page restoran": ["Atmosphere/food hero", "Signature offer/menu highlight", "Reservation or promo flow"],
        "restaurant landing page": ["Atmosphere/food hero", "Dining experience/value", "CTA reservation/order"],
        "equipment rental landing page": ["Rental categories", "Availability/delivery/support", "CTA booking/request quote"],
        "finance landing page": ["Financial pain/problem framing", "Consultation process", "Credibility/metrics/compliance trust"],
    }
    for query, required in cases.items():
        output = generate_design_system(query, output_format="ascii")
        _assert_not_contains(output, LANDING_FORBIDDEN, query, failures)
        _assert_contains(output, required, query, failures)
        _assert("ANTI-SCAFFOLD GATE: PASS" in output, f"{query!r}: anti-scaffold gate should pass", failures)


def test_presentation_payload_content(failures: list[str]) -> None:
    for query in ["pptx template finance", "template ppt restoran", "Google Slides pitch deck finance"]:
        output = generate_design_system(query, output_format="ascii")
        _assert_not_contains(output, PRESENTATION_FORBIDDEN, query, failures)
        _assert_contains(output, ["slide", "deck", "master", "data readability"], query, failures)


def test_non_web_payload_cleanup(failures: list[str]) -> None:
    email = generate_design_system("email newsletter template", output_format="ascii")
    _assert_not_contains(email, ["sticky", "scroll-triggered", "website sections", "hover states", "375px, 768px, 1024px, 1440px"], "email newsletter", failures)
    _assert_contains(email, ["email client", "Mobile stack", "Unsubscribe", "Alt text"], "email newsletter", failures)

    for query in ["restaurant menu design", "poster menu restaurant"]:
        output = generate_design_system(query, output_format="ascii")
        _assert_not_contains(output, ["hover states", "scroll effects", "website sections"], query, failures)
        _assert_contains(output, ["category", "price", "print", "readability"], query, failures)

    social = generate_design_system("social media post restaurant", output_format="ascii")
    _assert_not_contains(social, ["scroll-snap", "hover color shift", "large sections"], "social media post", failures)
    _assert_contains(social, ["aspect ratio", "hook", "crop safety", "export"], "social media post", failures)

    brand = generate_design_system("brand identity restaurant", output_format="ascii")
    _assert_not_contains(brand, ["website sections", "hover states", "scroll effects"], "brand identity", failures)
    _assert_contains(brand, ["logo", "clearspace", "color roles", "typography"], "brand identity", failures)


def test_ui_payload_content(failures: list[str]) -> None:
    for query in ["ui kit dashboard components", "design system component library"]:
        output = generate_design_system(query, output_format="ascii")
        _assert_contains(output, ["tokens", "states", "variants", "component"], query, failures)
        _assert_not_contains(output, ["Hero + Features + CTA", "marketing website section flow"], query, failures)


def test_json_safety_extra_fields(failures: list[str]) -> None:
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "search.py"), "hero features cta", "--domain", "landing", "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    _assert(completed.returncode == 0, "JSON safety extra command failed", failures)
    payload = json.loads(completed.stdout)
    restricted = [row for row in payload.get("results", []) if row.get("is_restricted")]
    _assert(bool(restricted), "JSON output should include restricted row", failures)
    if restricted:
        row = restricted[0]
        for field in ["offending_terms", "mode_compatibility", "brain_design_note"]:
            _assert(field in row and bool(row.get(field)), f"restricted JSON missing {field}", failures)


def test_action_payload_sanitization(failures: list[str]) -> None:
    menu = generate_design_system("restaurant menu design", output_format="ascii")
    _assert_not_contains(menu, ["Contact Sales", "Login", "logo carousel", "tab switching", "Conversion", "CTA Placement"], "restaurant menu action payload", failures)
    _assert_contains(menu, ["Menu reading path", "category", "price", "print", "readability"], "restaurant menu action payload", failures)

    landing = generate_design_system("landing page restoran", output_format="ascii")
    _assert_not_contains(landing, ["Narrative increases time-on-page", "Final climax CTA", "End of each chapter", "Parallax Storytelling"], "restaurant landing action payload", failures)
    _assert_contains(landing, ["Reserve", "table", "dining", "signature menu", "location"], "restaurant landing action payload", failures)

    social = generate_design_system("social media post restaurant", output_format="ascii")
    _assert_not_contains(social, ["86% higher engagement with video", "Bottom section", "scroll-snap", "hover color shift", "large sections"], "social action payload", failures)
    _assert_contains(social, ["hook", "aspect ratio", "crop", "export"], "social action payload", failures)

    email = generate_design_system("email newsletter template", output_format="ascii")
    _assert_not_contains(email, ["full website", "website sections", "sticky", "scroll-triggered", "Contact Sales + Login"], "email action payload", failures)
    _assert_contains(email, ["email client", "mobile stack", "unsubscribe", "alt text"], "email action payload", failures)

    system = generate_design_system("design system component library", output_format="ascii")
    _assert_not_contains(system, ["full website", "Conversion Strategy", "CTA Placement"], "design system action payload", failures)
    _assert_contains(system, ["tokens", "components", "states", "variants"], "design system action payload", failures)


def test_dashboard_master_action_language(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        generate_design_system(
            "saas dashboard",
            project_name="TestProject",
            output_format="markdown",
            persist=True,
            page="dashboard",
            output_dir=tmp,
        )
        master = Path(tmp) / "design-system" / "testproject" / "MASTER.md"
        _assert(master.exists(), "dashboard MASTER.md should persist", failures)
        text = master.read_text(encoding="utf-8") if master.exists() else ""
        _assert_not_contains(text, ["Conversion Strategy", "CTA Placement", "Contact Sales", "marketing CTA"], "dashboard MASTER.md", failures)
        _assert_contains(text, ["Workflow Strategy", "Data Hierarchy", "State Coverage", "KPI", "filters"], "dashboard MASTER.md", failures)


def test_json_action_safety_fields(failures: list[str]) -> None:
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "search.py"), "logo carousel contact sales", "--domain", "landing", "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    _assert(completed.returncode == 0, "JSON action safety command failed", failures)
    payload = json.loads(completed.stdout)
    rows = payload.get("results", [])
    _assert(bool(rows), "JSON action safety should return rows", failures)
    if rows:
        row = rows[0]
        for field in ["safety_metadata", "action_model", "forbidden_payload_terms", "sanitized_fields", "requires_sanitization"]:
            _assert(field in row, f"JSON action safety missing {field}", failures)
        _assert(any(item.get("requires_sanitization") for item in rows), "logo carousel/contact sales should require sanitization", failures)


def test_static_collateral_queries_do_not_block(failures: list[str]) -> None:
    cases = [
        ("poster restaurant", {"poster_design"}),
        ("flyer restaurant", {"print_collateral"}),
        ("banner restaurant", {"banner_design"}),
        ("thumbnail restaurant", {"thumbnail_design"}),
        ("restaurant flyer design", {"print_collateral"}),
        ("restaurant banner design", {"banner_design"}),
        ("restaurant thumbnail design", {"thumbnail_design"}),
        ("restaurant social banner", {"social_post"}),
    ]
    forbidden = ["CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "logo carousel", "tab switching"]
    for query, allowed_modes in cases:
        result = _generate(query)
        output = generate_design_system(query, output_format="ascii")
        _assert("Output blocked" not in output, f"{query!r}: static/collateral query was blocked", failures)
        _assert(result["anti_scaffold_gate"]["status"] == "PASS", f"{query!r}: gate did not pass", failures)
        _assert(result["output_mode"] in allowed_modes, f"{query!r}: expected mode {allowed_modes}, got {result['output_mode']}", failures)
        _assert(result["output_mode"] != "website", f"{query!r}: should not route to website", failures)
        _assert_not_contains(output, forbidden, query, failures)


def test_social_carousel_story_routing(failures: list[str]) -> None:
    cases = [
        ("social media carousel restaurant", ["carousel", "aspect ratio", "hook", "crop"]),
        ("social carousel restaurant", ["carousel", "aspect ratio", "hook", "crop"]),
        ("instagram story restaurant", ["story", "aspect ratio", "hook", "crop"]),
        ("restaurant instagram story", ["story", "aspect ratio", "hook", "crop"]),
    ]
    forbidden = ["CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "website sections", "full website", "scroll-snap", "hover color shift", "large sections"]
    for query, required_terms in cases:
        result = _generate(query)
        output = generate_design_system(query, output_format="ascii")
        _assert("Output blocked" not in output, f"{query!r}: social carousel/story query was blocked", failures)
        _assert(result["anti_scaffold_gate"]["status"] == "PASS", f"{query!r}: gate did not pass", failures)
        _assert(result["output_mode"] == "social_post", f"{query!r}: expected social_post, got {result['output_mode']}", failures)
        _assert(result.get("visible_niche_family") == "generic_social_post", f"{query!r}: expected generic_social_post visible family", failures)
        _assert(result.get("domain_context") == "restaurant_hospitality", f"{query!r}: expected restaurant domain context", failures)
        _assert_not_contains(output, forbidden, query, failures)
        _assert_contains(output, required_terms, query, failures)


def test_non_web_fallback_family_labels(failures: list[str]) -> None:
    cases = [
        ("email newsletter template", "generic_email_newsletter"),
        ("design system component library", "generic_design_system"),
        ("pptx template", "generic_presentation_deck"),
        ("logo design", "generic_brand_identity"),
        ("social media post", "generic_social_post"),
        ("mobile app onboarding screens", "generic_mobile_app"),
    ]
    for query, expected_family in cases:
        output = generate_design_system(query, output_format="ascii")
        result = _generate(query)
        _assert("NICHE FAMILY: full_website_template" not in output, f"{query!r}: leaked full_website_template label", failures)
        _assert(expected_family in output, f"{query!r}: missing fallback family {expected_family}", failures)
        _assert(result["output_mode"] != "website", f"{query!r}: non-web fallback routed to website", failures)


def test_document_collateral_modes(failures: list[str]) -> None:
    cases = [
        ("brochure design finance", "brochure_design", ["cover", "service", "contact", "print"]),
        ("restaurant brochure design", "brochure_design", ["cover", "service", "contact", "print"]),
        ("restaurant order ticket design", "ticket_receipt_design", ["item list", "quantity", "total", "receipt"]),
        ("invoice template design", "invoice_template", ["item table", "totals", "payment", "PDF"]),
        ("resume template design", "resume_template", ["profile", "experience", "skills", "PDF"]),
    ]
    for query, expected_mode, required_terms in cases:
        result = _generate(query)
        output = generate_design_system(query, output_format="ascii")
        _assert(result["output_mode"] == expected_mode, f"{query!r}: expected {expected_mode}, got {result['output_mode']}", failures)
        _assert(result["output_mode"] != "website", f"{query!r}: document/collateral routed to website", failures)
        _assert_not_contains(output, ["website sections", "CTA Placement", "Conversion Strategy", "full website"], query, failures)
        _assert_contains(output, required_terms, query, failures)


def test_v026_document_collateral_modes(failures: list[str]) -> None:
    cases = [
        ("letterhead design finance", {"letterhead_design"}, ["logo", "contact", "safe margin", "print"]),
        ("price list design restaurant", {"price_list_design", "menu_design"}, ["price", "category", "readability"]),
        ("table tent menu restaurant", {"table_tent_design", "menu_design"}, ["table", "print", "readability"]),
    ]
    forbidden = ["website sections", "CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "full website"]
    for query, allowed_modes, required_terms in cases:
        result = _generate(query)
        output = generate_design_system(query, output_format="ascii")
        _assert(result["output_mode"] in allowed_modes, f"{query!r}: expected {allowed_modes}, got {result['output_mode']}", failures)
        _assert(result["output_mode"] != "website", f"{query!r}: routed to website", failures)
        _assert("NICHE FAMILY: full_website_template" not in output, f"{query!r}: leaked full website family label", failures)
        _assert_not_contains(output, forbidden, query, failures)
        _assert_contains(output, required_terms, query, failures)
    table_output = generate_design_system("table tent menu restaurant", output_format="ascii")
    _assert(("fold" in table_output.lower()) or ("panel" in table_output.lower()), "table tent output missing fold/panel logic", failures)


def test_catalog_lookbook_modes(failures: list[str]) -> None:
    cases = [
        ("product catalog design fashion", "catalog_design", ["catalog", "product grid", "spread", "print"]),
        ("fashion lookbook design", "lookbook_design", ["lookbook", "editorial", "image spread", "visual rhythm"]),
    ]
    forbidden = ["MODE: ecommerce", "MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "cart", "checkout", "full website"]
    for query, expected_mode, required_terms in cases:
        result = _generate(query)
        output = generate_design_system(query, output_format="ascii")
        _assert(result["output_mode"] == expected_mode, f"{query!r}: expected {expected_mode}, got {result['output_mode']}", failures)
        _assert(result.get("domain_context") == "fashion_apparel_ecommerce", f"{query!r}: expected fashion domain context", failures)
        _assert("NICHE FAMILY: full_website_template" not in output, f"{query!r}: leaked full website family label", failures)
        _assert_not_contains(output, forbidden, query, failures)
        _assert_contains(output, required_terms, query, failures)


def test_v027_cover_modes(failures: list[str]) -> None:
    cases = [
        ("facebook cover restaurant", {"cover_design", "social_post"}, ["cover", "crop", "export"]),
        ("book cover design", {"cover_design"}, ["cover", "title", "focal visual", "export"]),
    ]
    forbidden = ["Output blocked", "MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "full website", "cart", "checkout"]
    for query, allowed_modes, required_terms in cases:
        result = _generate(query)
        output = generate_design_system(query, output_format="ascii")
        _assert("Output blocked" not in output, f"{query!r}: cover query was blocked", failures)
        _assert(result["anti_scaffold_gate"]["status"] == "PASS", f"{query!r}: gate did not pass", failures)
        _assert(result["output_mode"] in allowed_modes, f"{query!r}: expected {allowed_modes}, got {result['output_mode']}", failures)
        _assert(result["output_mode"] != "website", f"{query!r}: routed to website", failures)
        _assert("NICHE FAMILY: full_website_template" not in output, f"{query!r}: leaked full website family label", failures)
        _assert_not_contains(output, forbidden, query, failures)
        _assert_contains(output, required_terms, query, failures)


def test_v027_voucher_coupon_card_modes(failures: list[str]) -> None:
    cases = [
        "gift voucher design restaurant",
        "coupon design restaurant",
        "restaurant voucher design",
        "gift card design restaurant",
        "loyalty card design restaurant",
    ]
    forbidden = ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "full website", "cart", "checkout"]
    for query in cases:
        result = _generate(query)
        output = generate_design_system(query, output_format="ascii")
        _assert(result["output_mode"] == "voucher_coupon_design", f"{query!r}: expected voucher_coupon_design, got {result['output_mode']}", failures)
        _assert(result.get("domain_context") == "restaurant_hospitality", f"{query!r}: expected restaurant domain context", failures)
        _assert_not_contains(output, forbidden, query, failures)
        _assert_contains(output, ["offer", "code", "redemption", "print"], query, failures)
        _assert(("expiry" in output.lower()) or ("terms" in output.lower()) or ("card" in output.lower()), f"{query}: missing expiry/terms/card anatomy", failures)


def test_v027_sticker_postcard_certificate_booklet_modes(failures: list[str]) -> None:
    cases = [
        ("sticker design restaurant", "sticker_design", ["shape", "die-cut", "print"]),
        ("postcard design restaurant", "postcard_design", ["front/back", "message", "print"]),
        ("certificate template design", "certificate_design", ["recipient", "signature", "PDF"]),
        ("booklet design finance", "booklet_design", ["cover", "spread", "print"]),
    ]
    forbidden = ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website", "cart", "checkout"]
    for query, expected_mode, required_terms in cases:
        result = _generate(query)
        output = generate_design_system(query, output_format="ascii")
        _assert(result["output_mode"] == expected_mode, f"{query!r}: expected {expected_mode}, got {result['output_mode']}", failures)
        _assert(result["output_mode"] != "website", f"{query!r}: routed to website", failures)
        _assert_not_contains(output, forbidden, query, failures)
        _assert_contains(output, required_terms, query, failures)


def test_v027_label_and_tag_modes(failures: list[str]) -> None:
    cases = [
        ("packaging label design coffee", {"packaging_label_design"}, ["product name", "barcode", "dieline", "print"]),
        ("label design coffee", {"label_design", "packaging_label_design"}, ["label", "material", "print"]),
        ("price tag design fashion", {"price_tag_design"}, ["price", "SKU", "barcode", "print"]),
        ("hang tag design fashion", {"hang_tag_design"}, ["brand", "material", "barcode", "front/back"]),
    ]
    forbidden = ["MODE: website", "MODE: ecommerce", "website sections", "CTA Placement", "Conversion Strategy", "cart", "checkout", "full website"]
    for query, allowed_modes, required_terms in cases:
        result = _generate(query)
        output = generate_design_system(query, output_format="ascii")
        _assert(result["output_mode"] in allowed_modes, f"{query!r}: expected {allowed_modes}, got {result['output_mode']}", failures)
        _assert(result["output_mode"] not in {"website", "ecommerce"}, f"{query!r}: routed to website/ecommerce", failures)
        _assert_not_contains(output, forbidden, query, failures)
        _assert_contains(output, required_terms, query, failures)


def test_export_timeout_progress_guard(failures: list[str]) -> None:
    text = (ROOT / "scripts" / "export_design_craft.py").read_text(encoding="utf-8")
    for phrase in ["STEP_TIMEOUTS", "timeout=", "TimeoutExpired", "proc.kill", "stdin=subprocess.DEVNULL", "subprocess.Popen", "print_step", "print_manual_progress", "--skip-tests", "--verbose", "--manual-timeout", "--command-timeout", "manual_deadline"]:
        _assert(phrase in text, f"export script missing timeout/progress guard: {phrase}", failures)


def main() -> int:
    failures: list[str] = []
    test_product_families(failures)
    test_non_landing_products(failures)
    test_anti_bug_cases(failures)
    test_anti_minimalist_depth(failures)
    test_portability_and_email(failures)
    test_output_receipt(failures)
    test_raw_search_safety_label(failures)
    test_landing_mode(failures)
    test_presentation_modes(failures)
    test_static_brand_menu_social_modes(failures)
    test_ui_kit_component_modes(failures)
    test_furniture_and_onboarding_edges(failures)
    test_json_safety_metadata(failures)
    test_component_tokens_and_persist_gate(failures)
    test_landing_payload_content(failures)
    test_presentation_payload_content(failures)
    test_non_web_payload_cleanup(failures)
    test_ui_payload_content(failures)
    test_json_safety_extra_fields(failures)
    test_action_payload_sanitization(failures)
    test_dashboard_master_action_language(failures)
    test_json_action_safety_fields(failures)
    test_static_collateral_queries_do_not_block(failures)
    test_social_carousel_story_routing(failures)
    test_non_web_fallback_family_labels(failures)
    test_document_collateral_modes(failures)
    test_v026_document_collateral_modes(failures)
    test_catalog_lookbook_modes(failures)
    test_v027_cover_modes(failures)
    test_v027_voucher_coupon_card_modes(failures)
    test_v027_sticker_postcard_certificate_booklet_modes(failures)
    test_v027_label_and_tag_modes(failures)
    test_export_timeout_progress_guard(failures)

    if failures:
        print("FAIL: Design Craft smoke tests")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS: Design Craft smoke tests")
    print(f"Total checks: {TOTAL_CHECKS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
