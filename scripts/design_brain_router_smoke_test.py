#!/usr/bin/env python
"""Deterministic v2.2.4 router smoke tests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from design_brain_intent_route import detect_intents
from design_brain_modules import WEB_DECK_EXPLICIT_TERMS, select_module
from design_brain_reference_corpus_health import build_report as corpus_health_report
from design_brain_website_types import select_website_product_type


ROOT = Path(__file__).resolve().parents[1]


MODULE_TESTS = [
    ("dashboard POS template", "dashboard"),
    ("admin analytics dashboard", "dashboard"),
    ("ecommerce fashion website template", "ecommerce"),
    ("shop product catalog template", "ecommerce"),
    ("portfolio creative agency template", "portfolio"),
    ("mobile app fintech onboarding", "mobile-app"),
    ("presentation pitch deck finance", "presentation-deck"),
    ("ui kit dashboard components", "ui-kit"),
    ("brand kit restaurant identity", "brand-kit"),
    ("marketplace preview cover", "marketplace-preview"),
    ("template marketplace preview", "marketplace-preview"),
    ("template website restoran", "website-template"),
    ("landing page campaign", "landing-page"),
    ("hero header website", "hero-header-kit"),
    ("template website travel agency booking", "website-template"),
    ("agency website template", "website-template"),
    ("template website agensi kreatif", "website-template"),
    ("restaurant website template", "website-template"),
    ("template website keuangan", "website-template"),
    ("template website konsultan keuangan", "website-template"),
    ("template website berita majalah", "website-template"),
    ("template website blog magazine", "website-template"),
    ("editorial website template", "website-template"),
    ("magazine website template", "website-template"),
    ("blog website template", "website-template"),
    ("news website template", "website-template"),
    ("newsletter website template", "website-template"),
    ("email newsletter template", "email-newsletter"),
    ("newsletter email template", "email-newsletter"),
    ("email campaign template", "email-newsletter"),
    ("mailchimp newsletter template", "email-newsletter"),
    ("coffee shop website template", "website-template"),
    ("template website coffee shop", "website-template"),
    ("cafe website template", "website-template"),
    ("template website kafe", "website-template"),
    ("coffee bean online store template", "ecommerce"),
    ("coffee product ecommerce website", "ecommerce"),
    ("ecommerce pricing product page", "ecommerce"),
    ("ecommerce marketplace website", "ecommerce"),
    ("multi-vendor marketplace app", "ecommerce"),
    ("product marketplace platform", "ecommerce"),
    ("marketplace with cart and checkout", "ecommerce"),
    ("booking marketplace website", "ecommerce"),
    ("restaurant website template for editable marketplace template buyers with gallery and visual motif", "website-template"),
    ("web deck for webinar", "web-deck"),
    ("html presentation single file", "web-deck"),
    ("animated slides for demo day", "web-deck"),
    ("presentasi web interaktif", "web-deck"),
    ("ppt ke web", "web-deck"),
    ("powerpoint template", "presentation-deck"),
    ("keynote slides template", "presentation-deck"),
    ("buat template powerpoint", "presentation-deck"),
    ("pitch deck template", "presentation-deck"),
    ("presentation template for Envato", "presentation-deck"),
    ("google slides template", "presentation-deck"),
    ("keynote template", "presentation-deck"),
    ("ppt template", "presentation-deck"),
    ("deck untuk investor", "presentation-deck"),
    ("slide deck template", "presentation-deck"),
    ("buat website template", "website-template"),
    ("html template untuk marketplace", "website-template"),
    ("landing page saas", "landing-page"),
]


WEBSITE_PRODUCT_TESTS = [
    ("template website restoran", "event_venue_travel_booking"),
    ("restaurant website template", "event_venue_travel_booking"),
    ("template website keuangan", "corporate_business_website"),
    ("financial consulting website template", "corporate_business_website"),
    ("template website sewa alat", "professional_service_booking"),
    ("rental equipment website template", "professional_service_booking"),
    ("template website perhiasan ecommerce", "ecommerce_storefront"),
    ("jewelry ecommerce website", "ecommerce_storefront"),
    ("template website properti", "marketplace_listing_directory"),
    ("online course website template", "education_course_lms"),
    ("template website blog editorial", "editorial_blog_cms"),
    ("developer docs website", "documentation_help_center"),
    ("admin dashboard web app", "dashboard_admin_web_app"),
    ("template website", "multipurpose_website_template"),
    ("template website personal portfolio", "personal_portfolio_case_study"),
    ("template website case study", "personal_portfolio_case_study"),
    ("template website financial consultant", "corporate_business_website"),
    ("template website konsultan keuangan", "corporate_business_website"),
    ("template website travel agency booking", "event_venue_travel_booking"),
    ("website agen travel", "event_venue_travel_booking"),
    ("agency website template", "agency_studio_website"),
    ("template website agensi kreatif", "agency_studio_website"),
    ("template website berita majalah", "editorial_blog_cms"),
    ("template website blog magazine", "editorial_blog_cms"),
    ("editorial website template", "editorial_blog_cms"),
    ("magazine website template", "editorial_blog_cms"),
    ("blog website template", "editorial_blog_cms"),
    ("news website template", "editorial_blog_cms"),
    ("newsletter website template", "editorial_blog_cms"),
    ("coffee shop website template", "event_venue_travel_booking"),
    ("template website coffee shop", "event_venue_travel_booking"),
    ("cafe website template", "event_venue_travel_booking"),
    ("template website kafe", "event_venue_travel_booking"),
    ("hotel booking pricing website", "event_venue_travel_booking"),
    ("restaurant website template for editable marketplace template buyers with gallery and visual motif", "event_venue_travel_booking"),
    ("booking marketplace website", "marketplace_listing_directory"),
    ("property marketplace website", "marketplace_listing_directory"),
]


WEBSITE_PRODUCT_ALLOWED_TESTS = [
    (
        "creative agency portfolio template",
        {"personal_portfolio_case_study", "agency_studio_website"},
        "not multipurpose_website_template",
    ),
]

MODULE_NEGATIVE_TESTS = [
    ("pricing page website template", {"ecommerce"}),
    ("saas pricing page website template", {"ecommerce"}),
    ("service pricing website template", {"ecommerce"}),
    ("hotel booking pricing website", {"ecommerce"}),
    ("marketplace template buyer", {"ecommerce"}),
    ("Envato marketplace template", {"ecommerce"}),
    ("editable marketplace templates", {"ecommerce"}),
    ("marketplace-ready template", {"ecommerce"}),
    ("marketplace quality gate", {"ecommerce"}),
    ("template marketplace preview", {"ecommerce"}),
    ("restaurant website template for editable marketplace template buyers with gallery and visual motif", {"portfolio", "ecommerce"}),
    ("powerpoint pitch deck template", {"web-deck"}),
    ("presentasi ppt untuk investor", {"web-deck"}),
    ("template website restoran", {"web-deck"}),
]


BATCH_INTENT_TESTS = [
    ("buat tiga template website restoran", {"batch"}, set()),
    ("buat beberapa design template website restoran", {"batch"}, set()),
    ("tolong buatkan 4 gambar design nya saja 1 per 1", {"batch", "sequential_batch"}, set()),
    ("buatkan 3 gambar design nya saja", {"batch"}, set()),
    ("buat 5 variasi template", {"batch"}, set()),
    ("buat dua landing page berbeda", {"batch"}, set()),
    ("buat satu template website restoran", set(), {"batch", "sequential_batch"}),
    ("buat deck html animasi", {"web_deck"}, set()),
    ("convert this deck to web presentation", {"web_deck"}, set()),
]


PLACEHOLDERS = {
    "",
    "<" + "YOUR_FIGMA_PROJECT_ID" + ">",
    "PASTE_" + "YOUR_FIGMA_PROJECT_ID" + "_HERE",
}


def is_placeholder_project_id(value: str) -> bool:
    return value.strip() in PLACEHOLDERS


def result_line(label: str, task: str, expected: str, actual: str, ok: bool | None = None) -> bool:
    passed = (expected == actual) if ok is None else ok
    status = "PASS" if passed else "FAIL"
    print(f"{status} | {label} | {task!r} | expected={expected!r} actual={actual!r}")
    return passed


def intent_names(task: str) -> set[str]:
    args = argparse.Namespace(
        task=task,
        has_reference=False,
        template_count=None,
        needs_naming=False,
        needs_review=False,
    )
    return {rule.name for rule in detect_intents(args)}


def run_module_tests() -> list[bool]:
    rows: list[bool] = []
    for task, expected in MODULE_TESTS:
        actual = select_module(task=task, root=ROOT).get("id", "")
        rows.append(result_line("module", task, expected, actual))
    for trigger in WEB_DECK_EXPLICIT_TERMS:
        actual = select_module(task=trigger, root=ROOT).get("id", "")
        rows.append(result_line("web-deck-trigger", trigger, "web-deck", actual))
    for task, forbidden in MODULE_NEGATIVE_TESTS:
        actual = select_module(task=task, root=ROOT).get("id", "")
        expected = "not " + ",".join(sorted(forbidden))
        rows.append(result_line("module-negative", task, expected, actual, ok=actual not in forbidden))
    return rows


def run_website_product_tests() -> list[bool]:
    rows: list[bool] = []
    for task, expected in WEBSITE_PRODUCT_TESTS:
        actual = select_website_product_type(task, ROOT).get("id", "")
        rows.append(result_line("website-product", task, expected, actual))
    for task, allowed, expected_label in WEBSITE_PRODUCT_ALLOWED_TESTS:
        actual = select_website_product_type(task, ROOT).get("id", "")
        rows.append(result_line("website-product", task, expected_label, actual, ok=actual in allowed))
    return rows


def run_batch_intent_tests() -> list[bool]:
    rows: list[bool] = []
    for task, required, forbidden in BATCH_INTENT_TESTS:
        actual = intent_names(task)
        ok = required.issubset(actual) and actual.isdisjoint(forbidden)
        expected = f"includes={sorted(required)} excludes={sorted(forbidden)}"
        rows.append(result_line("batch-intent", task, expected, ",".join(sorted(actual)), ok=ok))
    return rows


def run_figma_placeholder_test() -> bool:
    example_path = ROOT / ".design-brain" / "FIGMA_OUTPUT_TARGET.local.example.json"
    data: dict[str, Any] = json.loads(example_path.read_text(encoding="utf-8"))
    actual = "placeholder" if is_placeholder_project_id(str(data.get("defaultProjectId", ""))) else "configured"
    return result_line("figma-target", "local example placeholder", "placeholder", actual)


def run_reference_corpus_health_test() -> bool:
    report = corpus_health_report(ROOT)
    valid_status = report.get("status") in {"ok", "warning"}
    valid_shape = "candidateCount" in report and "checkedPaths" in report and report.get("message")
    actual = "valid" if valid_status and valid_shape else "invalid"
    print(
        f"{'PASS' if actual == 'valid' else 'FAIL'} | reference-corpus-health | candidateCount={report.get('candidateCount')} status={report.get('status')!r}"
    )
    return actual == "valid"


def run_manifest_package_sanity_tests() -> list[bool]:
    rows: list[bool] = []
    manifest_path = ROOT / ".design-brain" / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    mandatory = list(manifest.get("mandatory_files", []))
    managed = list(manifest.get("managed_files", []))
    dev = list(manifest.get("dev_files", []))
    missing_mandatory = [path for path in mandatory if not (ROOT / path).exists()]
    missing_managed = [
        path
        for path in managed
        if isinstance(path, str)
        and path
        and not path.endswith("/")
        and not (ROOT / path).exists()
    ]
    rows.append(result_line("package-sanity", "manifest mandatory files exist", "none missing", ",".join(missing_mandatory), ok=not missing_mandatory))
    rows.append(result_line("package-sanity", "manifest managed files exist", "none missing", ",".join(missing_managed[:6]), ok=not missing_managed))
    required_dev = {"package-lock.json", "tsconfig.json", "playwright.config.ts", "tests/visual-review.spec.ts"}
    rows.append(result_line("package-sanity", "dev visual review files declared", str(sorted(required_dev)), str(sorted(required_dev.intersection(set(dev)))), ok=required_dev.issubset(set(dev))))
    return rows


def main() -> int:
    results = []
    results.extend(run_module_tests())
    results.extend(run_website_product_tests())
    results.extend(run_batch_intent_tests())
    results.append(run_figma_placeholder_test())
    results.append(run_reference_corpus_health_test())
    results.extend(run_manifest_package_sanity_tests())

    passed = sum(1 for item in results if item)
    total = len(results)
    failed = total - passed
    print(f"\nSummary: {passed}/{total} passed, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
