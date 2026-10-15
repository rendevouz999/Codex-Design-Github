#!/usr/bin/env python
"""Fast, bounded smoke tests for Brain Design v2.5.0 Design Simulation Layer."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

sys.dont_write_bytecode = True

from design_brain_design_cognition_smoke_test import base_receipt
from design_brain_design_simulate import resolve_simulation_route
from design_brain_process_utils import python_command, resolve_python_invocation, run_command as run_process_command


PYTHON_INVOCATION = resolve_python_invocation()


def py_command(args: list[str]) -> list[str]:
    return python_command(args, PYTHON_INVOCATION)


SIMULATION_FILES = [
    ".design-brain/DESIGN_SIMULATION_LAYER.md",
    ".design-brain/design-simulation/agents.json",
    ".design-brain/design-simulation/verdict-schema.json",
    ".design-brain/templates/DESIGN_SIMULATION_VERDICT.md",
    "scripts/design_brain_design_simulate.py",
    "scripts/design_brain_design_sim_smoke_test.py",
    "scripts/design_brain_process_utils.py",
    "scripts/design_brain_process_utils_smoke_test.py",
]


class Smoke:
    def __init__(self, deadline: float, verbose: bool = False) -> None:
        self.checks = 0
        self.deadline = deadline
        self.verbose = verbose

    def remaining(self, case: str) -> float:
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise AssertionError(f"Global smoke timeout reached before: {case}")
        return remaining

    def ok(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Brain Design design simulation smoke tests.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--quick", action="store_true", help="Run fast route-alignment plus limited full simulations. Default.")
    mode.add_argument("--full", action="store_true", help="Run quick smoke plus bounded deeper full simulation cases.")
    mode.add_argument("--route-only", action="store_true", help="Run in-process route-alignment checks only.")
    parser.add_argument("--case-timeout", type=int, default=0, help="Per simulation subprocess timeout.")
    parser.add_argument("--global-timeout", type=int, default=0, help="Global smoke timeout.")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    if not args.quick and not args.full and not args.route_only:
        args.quick = True
    if args.case_timeout <= 0:
        args.case_timeout = 45 if args.full else 20
    if args.global_timeout <= 0:
        args.global_timeout = 300 if args.full else 90
    return args


def root() -> Path:
    return Path(__file__).resolve().parents[1]


def route_args(
    task: str,
    *,
    template_type: str = "",
    niche: str = "",
    target_buyer: str = "",
    visual_mood: str = "",
    proposed_structure: str = "",
    reference_summary: str = "",
) -> argparse.Namespace:
    return SimpleNamespace(
        task=task,
        template_type=template_type,
        niche=niche,
        target_buyer=target_buyer,
        visual_mood=visual_mood,
        marketplace="Envato",
        mode="",
        module="",
        product_family="",
        website_type="",
        output_contract="",
        proposed_structure=proposed_structure
        or "Primary format; Role-specific hierarchy; Key content block; Supporting proof or metadata; States or export notes; Components; Source hygiene; Preview notes; Documentation",
        reference_summary=reference_summary or "Do-not-copy exact layout and color palette; reinterpret mood.",
        prior_fingerprint=[],
        prior_fingerprint_file=[],
        output_dir="",
        json=True,
        dry_run=False,
        agents="",
        cognition_receipt="",
        require_cognition=False,
        allow_missing_cognition=False,
        allow_default_agents=False,
        no_strict_envato=False,
    )


def write_valid_cognition_receipt(directory: Path, mode: str = "website") -> Path:
    receipt = base_receipt()
    receipt["mode"] = mode
    if mode == "dashboard":
        receipt["task"] = "dashboard analytics finance template from reference"
        receipt["productFamily"] = "dashboard_template"
        receipt["designIntentLock"]["productType"] = "editable analytics dashboard template"
        receipt["designIntentLock"]["outputMedium"] = "dashboard source template"
    elif mode == "ui-kit":
        receipt["task"] = "ui kit dashboard components from reference"
        receipt["productFamily"] = "ui_component_system"
        receipt["designIntentLock"]["productType"] = "editable UI kit template"
        receipt["designIntentLock"]["outputMedium"] = "component library source template"
    elif mode == "presentation":
        receipt["task"] = "presentation deck finance template from reference"
        receipt["productFamily"] = "presentation_deck"
        receipt["designIntentLock"]["productType"] = "editable presentation deck template"
        receipt["designIntentLock"]["outputMedium"] = "slide deck source template"
    path = directory / "design-cognition-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path


def strong_restaurant_args(reference_summary: str = "Do-not-copy exact layout and color palette; reinterpret mood.") -> list[str]:
    return [
        "--task",
        "restaurant website template",
        "--template-type",
        "website template",
        "--niche",
        "restaurant",
        "--target-buyer",
        "restaurant owners buying editable marketplace templates",
        "--visual-mood",
        "immersive hospitality with warm image-led hierarchy, typography contrast, gallery, surface depth, visual motif",
        "--proposed-structure",
        "Immersive hero; Signature menu; Dining atmosphere gallery; Reservation flow process; Location and hours; Reviews social proof; Trust service details; CTA reservation; Footer; Cover preview; Thumbnail; Responsive spread; Section breakdown; Package notes; Components auto-layout source hygiene documentation",
        "--reference-summary",
        reference_summary,
    ]


def run_sim(
    smoke: Smoke,
    label: str,
    args: list[str],
    *,
    case_timeout: int,
    expect_success: bool | None = None,
    auto_cognition: bool = True,
    cognition_mode: str = "website",
) -> tuple[int, dict[str, Any], str, float]:
    smoke.remaining(label)
    timeout = max(1, min(case_timeout, int(smoke.remaining(label))))
    with tempfile.TemporaryDirectory(prefix="brain-design-sim-smoke-") as tmp:
        cmd = py_command([
            "scripts/design_brain_design_simulate.py",
            "--json",
            "--output-dir",
            str(Path(tmp) / "artifacts"),
        ] + args)
        if auto_cognition and "--cognition-receipt" not in args:
            cmd += ["--cognition-receipt", str(write_valid_cognition_receipt(Path(tmp), cognition_mode))]
        start = time.monotonic()
        completed = run_process_command(cmd, cwd=root(), timeout=timeout, verbose=smoke.verbose)
        duration = time.monotonic() - start
        if completed.timedOut:
            raise AssertionError(
                f"{label} timed out after {timeout}s; killStrategy={completed.killStrategy}; "
                f"killedPids={completed.killedPids}; command={completed.command}\n"
                f"STDOUT={completed.stdoutExcerpt}\nSTDERR={completed.stderrExcerpt}"
            )
        if expect_success is True and completed.returncode != 0:
            raise AssertionError(f"{label} expected PASS, got {completed.returncode}: {completed.stderr}\n{completed.stdout}")
        if expect_success is False and completed.returncode == 0:
            raise AssertionError(f"{label} expected non-PASS, got PASS: {completed.stdout}")
        try:
            parsed = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                f"{label} stdout is not pure JSON: {exc}\nSTDOUT={completed.stdout}\nSTDERR={completed.stderr}"
            ) from exc
        smoke.ok("Design simulation artifacts written" not in completed.stdout, f"{label} leaked human text into JSON stdout.")
        smoke.ok(bool(parsed.get("artifactDir")), f"{label} missing artifactDir.")
        return completed.returncode, parsed, completed.stderr, duration


def routing(verdict: dict[str, Any]) -> dict[str, Any]:
    value = verdict.get("routing")
    if not isinstance(value, dict):
        raise AssertionError("Verdict missing routing object.")
    return value


def validate_verdict_shape(smoke: Smoke, verdict: dict[str, Any], label: str) -> None:
    schema = json.loads((root() / ".design-brain" / "design-simulation" / "verdict-schema.json").read_text(encoding="utf-8"))
    required = schema.get("required", [])
    missing = [field for field in required if field not in verdict]
    smoke.ok(not missing, f"{label} missing schema fields: {missing}")
    smoke.ok(verdict.get("verdict") in {"PASS", "REVISE", "BLOCKED"}, f"{label} has invalid verdict.")
    smoke.ok(isinstance(verdict.get("agentVotes"), list), f"{label} agentVotes must be an array.")
    smoke.ok(isinstance(verdict.get("recommendedImprovements"), list), f"{label} recommendedImprovements missing.")
    smoke.ok(isinstance(verdict.get("routing"), dict), f"{label} routing must be an object.")
    if verdict.get("verdict") == "PASS":
        smoke.ok(verdict.get("blockers") == [], f"{label} PASS must not contain blockers.")
        smoke.ok(verdict.get("requiredRepairs") == [], f"{label} PASS must not contain requiredRepairs.")
    if verdict.get("verdict") in {"REVISE", "BLOCKED"}:
        smoke.ok(bool(verdict.get("requiredRepairs")), f"{label} REVISE/BLOCKED must contain requiredRepairs.")


def assert_route(smoke: Smoke, index: int, task: str, expected: dict[str, Any], **kwargs: str) -> None:
    print(f"  [1.{index}] {task} ...", flush=True)
    smoke.remaining(task)
    resolved = resolve_simulation_route(route_args(task, **kwargs))
    if "routeSource" in expected:
        smoke.ok(
            resolved.get("routeSource") == expected["routeSource"],
            f"{task}: expected routeSource {expected['routeSource']}, got {resolved.get('routeSource')}",
        )
    if "module" in expected:
        smoke.ok(resolved.get("module") == expected["module"], f"{task}: expected module {expected['module']}, got {resolved.get('module')}")
    if "mode" in expected:
        smoke.ok(resolved.get("mode") == expected["mode"], f"{task}: expected mode {expected['mode']}, got {resolved.get('mode')}")
    if "websiteType" in expected:
        smoke.ok(
            resolved.get("websiteType") == expected["websiteType"],
            f"{task}: expected websiteType {expected['websiteType']}, got {resolved.get('websiteType')}",
        )
    if "not_module" in expected:
        smoke.ok(resolved.get("module") != expected["not_module"], f"{task}: regressed to module {expected['not_module']}")
    if "not_mode" in expected:
        smoke.ok(resolved.get("mode") != expected["not_mode"], f"{task}: regressed to mode {expected['not_mode']}")
    if "module_in" in expected:
        smoke.ok(resolved.get("module") in expected["module_in"], f"{task}: unexpected module {resolved.get('module')}")
    print(f"  [1.{index}] PASS", flush=True)


def run_route_alignment(smoke: Smoke) -> None:
    print("[1/8] Route alignment quick tests ...", flush=True)
    cases: list[tuple[str, dict[str, Any], dict[str, str]]] = [
        ("marketplace template buyer", {"routeSource": "brain_design_router", "not_module": "ecommerce", "not_mode": "ecommerce"}, {}),
        ("Envato marketplace template", {"routeSource": "brain_design_router", "not_module": "ecommerce", "not_mode": "ecommerce"}, {}),
        ("editable marketplace templates", {"routeSource": "brain_design_router", "not_module": "ecommerce", "not_mode": "ecommerce"}, {}),
        ("marketplace-ready template", {"routeSource": "brain_design_router", "not_module": "ecommerce", "not_mode": "ecommerce"}, {}),
        ("marketplace quality gate", {"routeSource": "brain_design_router", "not_module": "ecommerce", "not_mode": "ecommerce"}, {}),
        ("template marketplace preview", {"routeSource": "brain_design_router", "module": "marketplace-preview", "mode": "static-canvas"}, {}),
        (
            "restaurant website template for editable marketplace template buyers with gallery visual motif",
            {
                "routeSource": "brain_design_router",
                "module": "website-template",
                "mode": "website",
                "websiteType": "event_venue_travel_booking",
                "not_module": "portfolio",
                "not_mode": "ecommerce",
            },
            {
                "template_type": "website template",
                "niche": "restaurant",
                "target_buyer": "restaurant owners buying editable marketplace templates",
                "visual_mood": "immersive hospitality with warm image-led hierarchy, typography contrast, gallery, surface depth, visual motif",
            },
        ),
        ("coffee shop website template", {"routeSource": "brain_design_router", "module": "website-template", "mode": "website", "websiteType": "event_venue_travel_booking", "not_mode": "ecommerce"}, {}),
        ("newsletter website template", {"routeSource": "brain_design_router", "module": "website-template", "mode": "website", "websiteType": "editorial_blog_cms", "not_mode": "email-newsletter"}, {}),
        ("ui kit dashboard components", {"routeSource": "brain_design_router", "module": "ui-kit", "mode": "ui-kit", "not_mode": "dashboard"}, {}),
        ("pricing page website template", {"routeSource": "brain_design_router", "module": "website-template", "mode": "website", "not_mode": "ecommerce"}, {}),
        ("ecommerce marketplace website", {"routeSource": "brain_design_router", "module": "ecommerce", "mode": "ecommerce"}, {}),
        ("multi-vendor marketplace app", {"routeSource": "brain_design_router", "module": "ecommerce", "mode": "ecommerce"}, {}),
        ("product marketplace platform", {"routeSource": "brain_design_router", "module": "ecommerce", "mode": "ecommerce"}, {}),
        ("marketplace with cart and checkout", {"routeSource": "brain_design_router", "module": "ecommerce", "mode": "ecommerce"}, {}),
        ("booking marketplace website", {"routeSource": "brain_design_router", "module_in": {"ecommerce", "website-template"}}, {}),
        ("property marketplace website", {"routeSource": "brain_design_router", "module_in": {"ecommerce", "website-template"}}, {}),
        ("social media carousel restaurant", {"routeSource": "brain_design_router", "module": "static-canvas", "mode": "static-canvas", "not_mode": "website"}, {}),
        ("facebook cover restaurant", {"routeSource": "brain_design_router", "module": "static-canvas", "mode": "static-canvas", "not_mode": "website"}, {}),
        ("invoice template design", {"routeSource": "brain_design_router", "module": "document-report", "mode": "document-report", "not_mode": "website"}, {}),
        ("resume template design", {"routeSource": "brain_design_router", "module": "document-report", "mode": "document-report", "not_mode": "website"}, {}),
    ]
    for index, (task, expected, kwargs) in enumerate(cases, start=1):
        assert_route(smoke, index, task, expected, **kwargs)
    print("[1/8] Route alignment quick tests PASS", flush=True)


def run_thin_structure(smoke: Smoke, case_timeout: int) -> float:
    print("[2/8] Thin structure full simulation ...", flush=True)
    _, thin, _, duration = run_sim(
        smoke,
        "thin generic website structure",
        [
            "--task",
            "restaurant website template",
            "--template-type",
            "website template",
            "--niche",
            "restaurant",
            "--target-buyer",
            "restaurant template buyer",
            "--visual-mood",
            "clean minimal",
            "--proposed-structure",
            "Hero\nFeatures\nPricing\nFAQ\nCTA",
            "--reference-summary",
            "Original mood reference only.",
        ],
        case_timeout=case_timeout,
        expect_success=False,
    )
    text = " ".join(thin.get("blockers", []) + thin.get("requiredRepairs", [])).lower()
    smoke.ok(thin["verdict"] in {"BLOCKED", "REVISE"}, "Thin generic website structure must not PASS.")
    for phrase in ("thin structure", "generic scaffold", "section depth", "marketplace value"):
        smoke.ok(phrase in text, f"Thin structure output missing: {phrase}")
    print(f"[2/8] Thin structure full simulation PASS in {duration:.2f}s", flush=True)
    return duration


def run_strong_structure(smoke: Smoke, case_timeout: int) -> tuple[dict[str, Any], float]:
    print("[3/8] Strong structure full simulation ...", flush=True)
    agent_file = root() / ".design-brain" / "design-simulation" / "agents.json"
    agent_count = len(json.loads(agent_file.read_text(encoding="utf-8"))["agents"])
    _, strong, _, duration = run_sim(
        smoke,
        "strong restaurant website structure",
        strong_restaurant_args(),
        case_timeout=case_timeout,
        expect_success=True,
    )
    validate_verdict_shape(smoke, strong, "strong restaurant")
    smoke.ok(strong["verdict"] == "PASS", f"Strong restaurant structure should PASS, got {strong['verdict']}")
    smoke.ok(strong["requiredRepairs"] == [], "Strong PASS verdict must have no requiredRepairs.")
    smoke.ok(strong["agentSource"] == ".design-brain/design-simulation/agents.json", "agents.json source not reported.")
    smoke.ok(strong["agentCount"] == agent_count, "Agent count does not match agents.json.")
    smoke.ok(routing(strong)["routeSource"] == "brain_design_router", "Strong route should defer to Brain Design router.")
    smoke.ok(routing(strong)["module"] == "website-template", "Strong route module mismatch.")
    smoke.ok(routing(strong)["websiteType"] == "event_venue_travel_booking", "Strong restaurant website type mismatch.")
    print(f"[3/8] Strong structure full simulation PASS in {duration:.2f}s", flush=True)
    return strong, duration


def run_copy_risk(smoke: Smoke, case_timeout: int) -> float:
    print("[4/8] Copy-risk full simulations ...", flush=True)
    _, safe, _, safe_duration = run_sim(
        smoke,
        "safe do-not-copy reference",
        strong_restaurant_args("Do-not-copy exact layout and color palette; reinterpret mood."),
        case_timeout=case_timeout,
        expect_success=True,
    )
    smoke.ok(not safe["copyRisk"]["hasCopyRisk"], "Safe do-not-copy phrase triggered copy risk.")
    _, risky, _, risky_duration = run_sim(
        smoke,
        "risky exact-copy reference",
        strong_restaurant_args("Copy exact layout and colors from reference."),
        case_timeout=case_timeout,
        expect_success=False,
    )
    smoke.ok(risky["copyRisk"]["hasCopyRisk"], "Risky copy phrase did not trigger copy risk.")
    smoke.ok(risky["verdict"] in {"BLOCKED", "REVISE"}, "Risky copy phrase must not PASS.")
    duration = safe_duration + risky_duration
    print(f"[4/8] Copy-risk full simulations PASS in {duration:.2f}s", flush=True)
    return duration


def run_json_purity(smoke: Smoke, case_timeout: int) -> float:
    print("[5/8] JSON purity ...", flush=True)
    _, verdict, stderr, duration = run_sim(
        smoke,
        "json purity",
        strong_restaurant_args(),
        case_timeout=case_timeout,
        expect_success=True,
    )
    smoke.ok(isinstance(verdict, dict), "JSON purity command did not return an object.")
    smoke.ok("Design simulation artifacts written" in stderr, "Human artifact note should be sent to stderr in --json mode.")
    print(f"[5/8] JSON purity PASS in {duration:.2f}s", flush=True)
    return duration


def run_cognition_enforcement(smoke: Smoke, case_timeout: int) -> float:
    print("[6/9] Cognition enforcement ...", flush=True)
    total = 0.0
    code, missing, _, duration = run_sim(
        smoke,
        "missing cognition enforcement",
        strong_restaurant_args(),
        case_timeout=case_timeout,
        expect_success=False,
        auto_cognition=False,
    )
    total += duration
    smoke.ok(missing["verdict"] != "PASS", "Missing cognition receipt must not PASS.")
    smoke.ok(missing["cognition"]["status"] == "not_provided", "Missing cognition status should be not_provided.")
    smoke.ok(any("Design Cognition Receipt is required" in item for item in missing["requiredRepairs"]), "Missing cognition repair should be explicit.")

    with tempfile.TemporaryDirectory(prefix="brain-design-fake-cognition-") as tmp:
        fake_path = Path(tmp) / "fake-cognition.json"
        fake_path.write_text('{"status":"PASS"}\n', encoding="utf-8", newline="\n")
        _, fake, _, duration = run_sim(
            smoke,
            "fake status-only cognition enforcement",
            strong_restaurant_args() + ["--cognition-receipt", str(fake_path)],
            case_timeout=case_timeout,
            expect_success=False,
            auto_cognition=False,
        )
    total += duration
    smoke.ok(fake["verdict"] != "PASS", "Fake status-only cognition receipt must not PASS.")
    smoke.ok(fake["cognition"]["status"] == "FAIL", "Fake cognition receipt should validate as FAIL.")
    smoke.ok(bool(fake["cognition"].get("riskCategories") or fake["cognition"].get("missingFields")), "Invalid cognition risks/missing fields should appear.")

    _, valid, _, duration = run_sim(
        smoke,
        "valid cognition allows pass",
        strong_restaurant_args(),
        case_timeout=case_timeout,
        expect_success=True,
        auto_cognition=True,
    )
    total += duration
    smoke.ok(valid["verdict"] == "PASS", "Valid cognition receipt should allow strong structure PASS.")
    smoke.ok(valid["cognition"]["status"] == "PASS", "Valid cognition status should be PASS.")

    _, allowed_missing, _, duration = run_sim(
        smoke,
        "allow missing cognition debug mode",
        strong_restaurant_args() + ["--allow-missing-cognition"],
        case_timeout=case_timeout,
        expect_success=False,
        auto_cognition=False,
    )
    total += duration
    smoke.ok(allowed_missing["verdict"] != "PASS", "--allow-missing-cognition should still be non-PASS.")
    smoke.ok(any("debug" in item.lower() for item in allowed_missing["cognition"].get("warnings", [])), "Allow-missing debug warning should be recorded.")
    print(f"[6/9] Cognition enforcement PASS in {total:.2f}s", flush=True)
    return total


def run_medium_aware(smoke: Smoke, case_timeout: int) -> float:
    print("[7/9] Medium-aware scoring ...", flush=True)
    _, dashboard, _, duration = run_sim(
        smoke,
        "dashboard medium-aware simulation",
        [
            "--task",
            "dashboard analytics finance",
            "--proposed-structure",
            "KPI hierarchy; Chart grid; Data table; Filters search; Empty state; Loading state; Error state; Role permissions; Component source hygiene",
            "--reference-summary",
            "Do-not-copy exact layout and color palette; reinterpret mood.",
        ],
        case_timeout=case_timeout,
        cognition_mode="dashboard",
    )
    smoke.ok(routing(dashboard)["mode"] == "dashboard", "Dashboard medium route mismatch.")
    smoke.ok(dashboard["verdict"] != "BLOCKED", "Dashboard should not be blocked for missing website CTA/proof.")
    print(f"[7/9] Medium-aware scoring PASS in {duration:.2f}s", flush=True)
    return duration


def run_agent_source(smoke: Smoke, case_timeout: int) -> float:
    print("[8/9] Agent source override ...", flush=True)
    with tempfile.TemporaryDirectory(prefix="brain-design-agents-smoke-") as tmp_agents:
        agents_path = Path(tmp_agents) / "agents.json"
        agents_path.write_text(
            json.dumps(
                {
                    "schema": "design-brain.design-simulation.agents.v2",
                    "version": "2.5.0",
                    "agents": [
                        {
                            "id": "test_agent",
                            "name": "Test Agent",
                            "role": "Validates custom agent source loading.",
                            "focus": "source of truth",
                            "evaluation_axes": ["source"],
                            "vote_rules": "Vote PASS when the verdict is otherwise valid.",
                        }
                    ],
                },
                indent=2,
            ),
            encoding="utf-8",
            newline="\n",
        )
        _, custom_agents, _, duration = run_sim(
            smoke,
            "custom agents source",
            strong_restaurant_args() + ["--agents", str(agents_path)],
            case_timeout=case_timeout,
            expect_success=True,
        )
    smoke.ok(custom_agents["agentCount"] == 1, "--agents source did not change agent count.")
    smoke.ok(str(custom_agents["agentSource"]).endswith("agents.json"), "Custom agent source not reported.")
    print(f"[8/9] Agent source override PASS in {duration:.2f}s", flush=True)
    return duration


def run_install_check(smoke: Smoke, case_timeout: int) -> float:
    print("[9/9] Install simulation files ...", flush=True)
    smoke.remaining("install simulation files")
    timeout = max(1, min(case_timeout, int(smoke.remaining("install simulation files"))))
    with tempfile.TemporaryDirectory(prefix="brain-design-install-smoke-") as tmp:
        target = Path(tmp) / "target"
        start = time.monotonic()
        completed = run_process_command(
            py_command(["scripts/install_design_brain.py", "--target", str(target)]),
            cwd=root(),
            timeout=timeout,
            verbose=smoke.verbose,
        )
        duration = time.monotonic() - start
        smoke.ok(not completed.timedOut, f"Installer timed out: {completed.command}")
        smoke.ok(completed.returncode == 0, f"Installer failed: {(completed.stdout + completed.stderr)[-1000:]}")
        for relative in ["AGENTS.md", ".design-brain/AUTOLOAD_POLICY.md"] + SIMULATION_FILES:
            smoke.ok((target / relative).is_file(), f"Installed target missing: {relative}")
    print(f"[9/9] Install simulation files PASS in {duration:.2f}s", flush=True)
    return duration


def run_full_extras(smoke: Smoke, case_timeout: int) -> float:
    print("[10/10] Full-mode bounded extras ...", flush=True)
    total = 0.0
    extra_cases = [
        (
            "presentation medium-aware simulation",
            [
                "--task",
                "presentation pitch deck finance",
                "--proposed-structure",
                "Cover slide; Agenda; Problem slide; Solution slide; Data chart slide; Comparison slide; Team slide; Closing slide; Master slide consistency; Export compatibility",
                "--reference-summary",
                "Do-not-copy exact layout and color palette; reinterpret mood.",
            ],
            None,
            "presentation",
        ),
        (
            "ui kit medium-aware simulation",
            [
                "--task",
                "ui kit dashboard components",
                "--proposed-structure",
                "Token system; Component inventory; Button variants; Input states; Table states; Accessibility states; Naming convention; Source hygiene",
                "--reference-summary",
                "Do-not-copy exact layout and color palette; reinterpret mood.",
            ],
            None,
            "ui-kit",
        ),
        (
            "copy-risk safe anti-copy boundary",
            strong_restaurant_args("Anti-copy boundary: no exact layout reuse."),
            True,
            "website",
        ),
        (
            "copy-risk risky pixel perfect",
            strong_restaurant_args("Make it pixel-perfect same as reference."),
            False,
            "website",
        ),
    ]
    for index, (label, sim_args, expect_success, expected_mode) in enumerate(extra_cases, start=1):
        print(f"  [10.{index}] {label} ...", flush=True)
        _, verdict, _, duration = run_sim(smoke, label, sim_args, case_timeout=case_timeout, expect_success=expect_success, cognition_mode=expected_mode)
        total += duration
        smoke.ok(routing(verdict)["mode"] == expected_mode, f"{label}: expected mode {expected_mode}")
        if expected_mode in {"presentation", "ui-kit"}:
            smoke.ok(verdict["verdict"] != "BLOCKED", f"{label} should not be blocked for website-section criteria.")
        if "pixel perfect" in label:
            smoke.ok(verdict["copyRisk"]["hasCopyRisk"], f"{label}: risky phrase should trigger copy risk.")
        print(f"  [10.{index}] PASS in {duration:.2f}s", flush=True)
    print(f"[10/10] Full-mode bounded extras PASS in {total:.2f}s", flush=True)
    return total


def main() -> int:
    args = parse_args()
    start = time.monotonic()
    smoke = Smoke(deadline=start + args.global_timeout, verbose=args.verbose)
    total_sim_duration = 0.0

    run_route_alignment(smoke)
    if args.route_only:
        duration = time.monotonic() - start
        print(f"PASS: Design Simulation route-only smoke tests ({smoke.checks} checks) in {duration:.2f}s")
        return 0

    total_sim_duration += run_thin_structure(smoke, args.case_timeout)
    strong, strong_duration = run_strong_structure(smoke, args.case_timeout)
    total_sim_duration += strong_duration
    total_sim_duration += run_copy_risk(smoke, args.case_timeout)
    total_sim_duration += run_json_purity(smoke, args.case_timeout)
    total_sim_duration += run_cognition_enforcement(smoke, args.case_timeout)
    total_sim_duration += run_medium_aware(smoke, args.case_timeout)
    total_sim_duration += run_agent_source(smoke, args.case_timeout)
    total_sim_duration += run_install_check(smoke, args.case_timeout)

    graph = strong["designContextGraph"]
    node_ids = {node.get("id") for node in graph.get("nodes", []) if isinstance(node, dict)}
    for required_node in ("UserRequest", "BrainDesignRoute", "RouteSource", "ProductFamily", "Medium", "TemplatePlan", "DesignCognitionReceipt", "ColorRoleRemapping", "ReferenceBoundary", "StructuralReconfiguration", "CopyRisk", "AgentVerdict"):
        smoke.ok(required_node in node_ids, f"Graph missing node: {required_node}")

    if args.full:
        total_sim_duration += run_full_extras(smoke, args.case_timeout)

    duration = time.monotonic() - start
    mode = "full" if args.full else "quick"
    print(
        f"PASS: Design Simulation {mode} smoke tests ({smoke.checks} checks) "
        f"in {duration:.2f}s; full-simulation time {total_sim_duration:.2f}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

