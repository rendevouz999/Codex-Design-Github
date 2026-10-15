#!/usr/bin/env python3
"""Export a clean Design Craft skill ZIP."""

from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
import argparse
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "exports"
ZIP_PATH = EXPORTS / "design-craft-v0.3.0.zip"
STEP_TIMEOUTS = {
    "compile": 60,
    "validate": 60,
    "smoke": 180,
    "manual": 30,
    "zip": 60,
}

EXCLUDED_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "node_modules",
    "exports",
    "design-craft-backups",
    "design-system",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".DS_Store"}
EXCLUDED_NAMES = {".env"}
EXCLUDED_RELATIVE = {"data/user_extensions.local.json"}


def print_step(index: int, total: int, message: str) -> None:
    print(f"[{index}/{total}] {message}...", flush=True)


def print_pass(message: str) -> None:
    print(f"{message} PASS", flush=True)


def print_manual_progress(index: int, total: int, label: str) -> None:
    print(f"  [5.{index}/{total}] {label} ...", flush=True)


def print_manual_pass(index: int, total: int, elapsed: float) -> None:
    print(f"  [5.{index}/{total}] PASS in {elapsed:.2f}s", flush=True)


def _excerpt(text: str, limit: int = 4000) -> str:
    if not text:
        return ""
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return stripped[:limit] + "\n... <truncated>"


def run_process(args: list[str], timeout: int, label: str, verbose: bool = False) -> tuple[int, str, str]:
    start = time.monotonic()
    proc = subprocess.Popen(
        args,
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        print(f"FAIL: manual_subprocess_timeout_not_killed guard triggered for {label} after {timeout}s: {' '.join(args)}", flush=True)
        if stdout:
            print(_excerpt(stdout), flush=True)
        if stderr:
            print(_excerpt(stderr), file=sys.stderr, flush=True)
        raise SystemExit(1)
    elapsed = time.monotonic() - start
    if verbose:
        if stdout:
            print(_excerpt(stdout), flush=True)
        if stderr:
            print(_excerpt(stderr), file=sys.stderr, flush=True)
    return proc.returncode or 0, stdout or "", stderr or ""


def clean_cache() -> None:
    for directory in ROOT.rglob("__pycache__"):
        if directory.is_dir():
            shutil.rmtree(directory)
    for file_path in ROOT.rglob("*.pyc"):
        file_path.unlink()
    for junk_name in [".DS_Store", "Thumbs.db"]:
        for file_path in ROOT.rglob(junk_name):
            file_path.unlink()


def run_command(args: list[str], timeout: int, label: str, verbose: bool = False) -> None:
    returncode, stdout, stderr = run_process(args, timeout, label, verbose)
    if not verbose and stdout and ("FAIL" in stdout or "PASS" in stdout):
        print(_excerpt(stdout), flush=True)
    if not verbose and stderr:
        print(_excerpt(stderr), file=sys.stderr, flush=True)
    if returncode != 0:
        if stdout and not verbose:
            print(_excerpt(stdout), flush=True)
        if stderr and not verbose:
            print(_excerpt(stderr), file=sys.stderr, flush=True)
        print(f"FAIL: {label}: {' '.join(args)}")
        raise SystemExit(returncode)


def assert_command_output(args: list[str], required: list[str], forbidden: list[str], label: str, timeout: int, verbose: bool = False) -> str:
    returncode, stdout, stderr = run_process(args, timeout, label, verbose)
    text = stdout + stderr
    if returncode != 0:
        print(_excerpt(text), flush=True)
        raise SystemExit(returncode)
    lower = text.lower()
    failures = [f"missing {term}" for term in required if term.lower() not in lower]
    failures.extend(f"forbidden {term}" for term in forbidden if term.lower() in lower)
    if failures:
        print(f"FAIL: {label}")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    return text


def compile_scripts() -> None:
    for script in sorted((ROOT / "scripts").glob("*.py")):
        run_command([sys.executable, "-m", "py_compile", str(script)], STEP_TIMEOUTS["compile"], f"compile {script.name}")


def should_include(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    rel_posix = relative.as_posix()
    parts = set(relative.parts)
    if parts & EXCLUDED_DIRS:
        return False
    if rel_posix in EXCLUDED_RELATIVE:
        return False
    if path.name in EXCLUDED_NAMES or any(path.name.endswith(suffix) for suffix in EXCLUDED_SUFFIXES):
        return False
    if path.name.startswith(".env."):
        return False
    return path.is_file()


def build_zip() -> None:
    EXPORTS.mkdir(exist_ok=True)
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(ROOT.rglob("*")):
            if should_include(path):
                zf.write(path, path.relative_to(ROOT).as_posix())


def verify_zip() -> None:
    forbidden = ["__pycache__/", ".pyc", ".env", ".DS_Store", "data/user_extensions.local.json"]
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        names = zf.namelist()
    failures = [name for name in names if any(marker in name for marker in forbidden)]
    if failures:
        ZIP_PATH.unlink(missing_ok=True)
        print("FAIL: ZIP contains forbidden files")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)


def run_action_payload_checks(verbose: bool = False, command_timeout: int = 30, manual_timeout: int = 180) -> None:
    manual_deadline = time.monotonic() + manual_timeout
    static_cases = [
        ("poster restaurant", ["MODE: poster_design", "ANTI-SCAFFOLD GATE: PASS"], ["Output blocked", "CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "logo carousel", "tab switching"]),
        ("flyer restaurant", ["MODE: print_collateral", "ANTI-SCAFFOLD GATE: PASS"], ["Output blocked", "CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "logo carousel", "tab switching"]),
        ("banner restaurant", ["MODE: banner_design", "ANTI-SCAFFOLD GATE: PASS"], ["Output blocked", "CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "logo carousel", "tab switching"]),
        ("thumbnail restaurant", ["MODE: thumbnail_design", "ANTI-SCAFFOLD GATE: PASS"], ["Output blocked", "CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "logo carousel", "tab switching"]),
        ("restaurant flyer design", ["MODE: print_collateral", "ANTI-SCAFFOLD GATE: PASS"], ["Output blocked", "CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "logo carousel", "tab switching"]),
        ("restaurant banner design", ["MODE: banner_design", "ANTI-SCAFFOLD GATE: PASS"], ["Output blocked", "CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "logo carousel", "tab switching"]),
        ("restaurant thumbnail design", ["MODE: thumbnail_design", "ANTI-SCAFFOLD GATE: PASS"], ["Output blocked", "CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "logo carousel", "tab switching"]),
        ("restaurant social banner", ["MODE: social_post", "ANTI-SCAFFOLD GATE: PASS"], ["Output blocked", "CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "logo carousel", "tab switching"]),
        ("social media carousel restaurant", ["MODE: social_post", "ANTI-SCAFFOLD GATE: PASS", "aspect ratio", "hook", "crop", "carousel"], ["Output blocked", "CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "website sections", "full website"]),
        ("social carousel restaurant", ["MODE: social_post", "ANTI-SCAFFOLD GATE: PASS", "aspect ratio", "hook", "crop", "carousel"], ["Output blocked", "CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "website sections", "full website"]),
        ("instagram story restaurant", ["MODE: social_post", "ANTI-SCAFFOLD GATE: PASS", "aspect ratio", "hook", "crop", "story"], ["Output blocked", "CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "website sections", "full website"]),
        ("restaurant instagram story", ["MODE: social_post", "ANTI-SCAFFOLD GATE: PASS", "aspect ratio", "hook", "crop", "story"], ["Output blocked", "CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "website sections", "full website"]),
        ("facebook cover restaurant", ["ANTI-SCAFFOLD GATE: PASS", "cover", "crop", "export"], ["Output blocked", "MODE: website", "CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "website sections", "full website", "cart", "checkout"]),
        ("book cover design", ["MODE: cover_design", "ANTI-SCAFFOLD GATE: PASS", "cover", "title", "focal visual", "export"], ["Output blocked", "MODE: website", "CTA Placement", "Conversion Strategy", "Contact Sales", "Login", "website sections", "full website", "cart", "checkout"]),
    ]
    document_cases = [
        ("brochure design finance", ["MODE: brochure_design", "cover", "service", "contact", "print"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website"]),
        ("restaurant brochure design", ["MODE: brochure_design", "cover", "service", "contact", "print"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website"]),
        ("restaurant order ticket design", ["MODE: ticket_receipt_design", "item list", "quantity", "total", "receipt"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website"]),
        ("invoice template design", ["MODE: invoice_template", "item table", "totals", "payment", "PDF"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website"]),
        ("resume template design", ["MODE: resume_template", "profile", "experience", "skills", "PDF"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website"]),
        ("letterhead design finance", ["MODE: letterhead_design", "logo", "contact", "safe margin", "print"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website", "Contact Sales", "Login"]),
        ("price list design restaurant", ["price", "category", "readability", "print"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website", "Contact Sales", "Login"]),
        ("table tent menu restaurant", ["table", "fold", "print", "readability"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website", "Contact Sales", "Login"]),
        ("product catalog design fashion", ["MODE: catalog_design", "catalog", "product grid", "spread", "print"], ["MODE: ecommerce", "MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "cart", "checkout"]),
        ("fashion lookbook design", ["MODE: lookbook_design", "lookbook", "editorial", "image spread", "visual rhythm"], ["MODE: ecommerce", "MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "cart", "checkout"]),
        ("booklet design finance", ["MODE: booklet_design", "cover", "spread", "print"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website", "cart", "checkout"]),
        ("certificate template design", ["MODE: certificate_design", "recipient", "signature", "PDF"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website", "cart", "checkout"]),
        ("gift voucher design restaurant", ["MODE: voucher_coupon_design", "offer", "code", "redemption", "print"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website", "cart", "checkout", "Contact Sales", "Login"]),
        ("coupon design restaurant", ["MODE: voucher_coupon_design", "offer", "code", "redemption", "print"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website", "cart", "checkout", "Contact Sales", "Login"]),
        ("postcard design restaurant", ["MODE: postcard_design", "front/back", "message", "print"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website", "cart", "checkout"]),
        ("sticker design restaurant", ["MODE: sticker_design", "shape", "die-cut", "print"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website", "cart", "checkout"]),
        ("restaurant voucher design", ["MODE: voucher_coupon_design", "offer", "code", "redemption", "print"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website", "cart", "checkout", "Contact Sales", "Login"]),
        ("gift card design restaurant", ["MODE: voucher_coupon_design", "offer", "code", "redemption", "card"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website", "cart", "checkout", "Contact Sales", "Login"]),
        ("loyalty card design restaurant", ["MODE: voucher_coupon_design", "offer", "code", "redemption", "card"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "full website", "cart", "checkout", "Contact Sales", "Login"]),
        ("packaging label design coffee", ["MODE: packaging_label_design", "product name", "barcode", "dieline", "print"], ["MODE: website", "MODE: ecommerce", "website sections", "CTA Placement", "Conversion Strategy", "cart", "checkout"]),
        ("label design coffee", ["label", "brand/product", "material", "print"], ["MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "cart", "checkout"]),
        ("price tag design fashion", ["MODE: price_tag_design", "price", "SKU", "barcode", "print"], ["MODE: ecommerce", "MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "cart", "checkout"]),
        ("hang tag design fashion", ["MODE: hang_tag_design", "brand", "material", "barcode", "front/back"], ["MODE: ecommerce", "MODE: website", "website sections", "CTA Placement", "Conversion Strategy", "cart", "checkout"]),
    ]
    fallback_cases = [
        ("email newsletter template", [ "generic_email_newsletter"], ["NICHE FAMILY: full_website_template"]),
        ("design system component library", ["generic_design_system"], ["NICHE FAMILY: full_website_template"]),
        ("pptx template", ["generic_presentation_deck"], ["NICHE FAMILY: full_website_template"]),
        ("logo design", ["generic_brand_identity"], ["NICHE FAMILY: full_website_template"]),
        ("social media post", ["generic_social_post"], ["NICHE FAMILY: full_website_template"]),
        ("mobile app onboarding screens", ["generic_mobile_app"], ["NICHE FAMILY: full_website_template"]),
    ]
    action_cases = [
        ("restaurant menu design", ["Menu reading path", "category", "price", "print", "readability"], ["Contact Sales", "Login", "logo carousel", "tab switching", "Conversion", "CTA Placement"]),
        ("landing page restoran", ["Reserve", "table", "dining", "signature menu", "location"], ["Narrative increases time-on-page", "Final climax CTA", "End of each chapter", "Parallax Storytelling"]),
        ("social media post restaurant", ["hook", "aspect ratio", "crop", "export"], ["86% higher engagement with video", "Bottom section", "scroll-snap", "hover color shift", "large sections"]),
        ("email newsletter template", ["email client", "mobile stack", "unsubscribe", "alt text"], ["full website", "website sections", "sticky", "scroll-triggered", "Contact Sales + Login"]),
        ("design system component library", ["tokens", "components", "states", "variants"], ["full website", "Conversion Strategy", "CTA Placement"]),
    ]
    all_cases = static_cases + document_cases + fallback_cases + action_cases
    total = len(all_cases)
    for index, (query, required, forbidden) in enumerate(all_cases, start=1):
        remaining = manual_deadline - time.monotonic()
        if remaining <= 0:
            print(f"FAIL: manual edge checks exceeded total timeout of {manual_timeout}s")
            raise SystemExit(1)
        current_timeout = max(1, min(command_timeout, int(remaining)))
        print_manual_progress(index, total, query)
        start = time.monotonic()
        assert_command_output(
            [sys.executable, "scripts/search.py", query, "--design-system"],
            required,
            forbidden,
            f"{query} manual edge payload",
            current_timeout,
            verbose,
        )
        print_manual_pass(index, total, time.monotonic() - start)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a clean Design Craft ZIP")
    parser.add_argument("--skip-tests", action="store_true", help="Emergency/debug only: skip validation and smoke checks")
    parser.add_argument("--verbose", action="store_true", help="Print full command output")
    parser.add_argument("--manual-timeout", type=int, default=180, help="Total timeout in seconds for all manual edge checks")
    parser.add_argument("--command-timeout", type=int, default=30, help="Per-command timeout in seconds for manual edge checks")
    args = parser.parse_args()
    total_steps = 8 if not args.skip_tests else 4
    step = 1
    print_step(step, total_steps, "Cleaning cache")
    clean_cache()
    print_pass("Cleaning cache")
    step += 1
    print_step(step, total_steps, "Compiling scripts")
    compile_scripts()
    clean_cache()
    print_pass("Compiling scripts")
    step += 1
    if not args.skip_tests:
        print_step(step, total_steps, "Running validate_data.py")
        run_command([sys.executable, "scripts/validate_data.py"], STEP_TIMEOUTS["validate"], "validate_data.py", args.verbose)
        print_pass("Running validate_data.py")
        step += 1
        print_step(step, total_steps, "Running smoke_test.py")
        run_command([sys.executable, "scripts/smoke_test.py"], STEP_TIMEOUTS["smoke"], "smoke_test.py", args.verbose)
        print_pass("Running smoke_test.py")
        step += 1
        print_step(step, total_steps, "Running craft_adapter_smoke_test.py")
        run_command([sys.executable, "scripts/craft_adapter_smoke_test.py"], STEP_TIMEOUTS["smoke"], "craft_adapter_smoke_test.py", args.verbose)
        print_pass("Running craft_adapter_smoke_test.py")
        step += 1
        print_step(step, total_steps, "Running manual edge checks")
        run_action_payload_checks(args.verbose, args.command_timeout, args.manual_timeout)
        print_manual_progress(1, 2, "saas dashboard non-persist check")
        start = time.monotonic()
        run_command([sys.executable, "scripts/search.py", "saas dashboard", "--design-system"], args.command_timeout, "dashboard non-persist check", args.verbose)
        print_manual_pass(1, 2, time.monotonic() - start)
        print_manual_progress(2, 2, "hero features cta json safety check")
        start = time.monotonic()
        run_command([sys.executable, "scripts/search.py", "hero features cta", "--domain", "landing", "--json"], args.command_timeout, "json safety check", args.verbose)
        print_manual_pass(2, 2, time.monotonic() - start)
        print_pass("Running manual edge checks")
        step += 1
    else:
        print("WARN: --skip-tests used; validation/smoke/manual checks were skipped.", flush=True)
    master = ROOT / "design-system" / "testproject" / "MASTER.md"
    if master.exists():
        text = master.read_text(encoding="utf-8")
        required_tokens = ["--radius-button", "--radius-card", "--font-heading", "--font-body", "--brand-accent"]
        missing = [token for token in required_tokens if token not in text]
        forbidden = [term for term in ["border-radius: 8px;", "max-width: 500px;", "Conversion Strategy", "CTA Placement", "Contact Sales", "marketing CTA"] if term in text]
        required_action = [term for term in ["Workflow Strategy", "Data Hierarchy", "State Coverage", "KPI", "filters"] if term not in text]
        if missing or forbidden:
            print("FAIL: persisted MASTER.md token validation failed")
            for token in missing:
                print(f"- missing token {token}")
            for term in forbidden:
                print(f"- forbidden universal value {term}")
            raise SystemExit(1)
        if required_action:
            print("FAIL: persisted MASTER.md action validation failed")
            for term in required_action:
                print(f"- missing action term {term}")
            raise SystemExit(1)
    clean_cache()
    design_system_dir = ROOT / "design-system"
    if design_system_dir.exists():
        shutil.rmtree(design_system_dir)
    print_step(step, total_steps, "Creating ZIP")
    build_zip()
    print_pass("Creating ZIP")
    step += 1
    print_step(step, total_steps, "Inspecting ZIP hygiene")
    verify_zip()
    print_pass("Inspecting ZIP hygiene")
    print(f"PASS: exported {ZIP_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
