"""Focused, offline acceptance through the real plugin runtime (no paid model calls)."""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
import uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from design_production.contracts import DesignResult, DesignTask, MainReviewDecision
from design_production.policy import ROOT, STATE, atomic_json, digest, single_worker, task_id
from design_production.adapters import AuthorizedAdapters
from design_production.hook import decision, job_path, load_job, run_bounded
from design_brain_process_utils import run_command

class Acceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = ROOT / "output/design-production-acceptance" / uuid.uuid4().hex
        cls.directory.mkdir(parents=True)
        cls.brief = cls.directory / "brief.md"
        cls.brief.write_text("Offline integration fixture. Editable labeled rectangle; Main reviews all results.", encoding="utf-8")
        cls.evidence = []

    def spec(self, **changes):
        value = dict(parent_request_id="acceptance-"+uuid.uuid4().hex, stage="build", operation="create", artifact_type="social_graphic",
            units=[dict(id="unit-1", kind="artboard", width=1080, height=1080, instruction="Offline fixture only")],
            inputs=[dict(id="brief", path=str(self.brief), sha256=digest(self.brief), role="brief")],
            output_format="svg", editability_requirements=["Editable text and shapes"],
            allowed_tools=["read_input", "discover_capabilities", "write_unit", "build_artifact", "render_preview", "technical_qa"],
            output_dir=str(self.directory / "artifacts"), creative_constraints="Preserve job dimensions and editable text. This is a mock fixture.",
            authorized=True, no_execution=False, revision=0,
            approval_policy=dict(approver="main", require_render=True, require_native_editability=True, max_revisions=2, allow_paid_model=False),
            timeout_seconds=150, max_tool_calls=40)
        value.update(changes)
        return value

    def write(self, value):
        path = self.directory / (uuid.uuid4().hex + ".json")
        atomic_json(path, value)
        return path

    def cli(self, *args, expected=0):
        result = run_command([sys.executable, "-B", str(ROOT / "scripts/design_brain_runtime.py"), *map(str, args), "--json"],
                             cwd=ROOT, timeout=180, isolate_process_group=True)
        self.assertFalse(result.timedOut, result.stderrExcerpt)
        try:
            value = json.loads(result.stdout)
        except ValueError:
            self.fail(result.stdoutExcerpt + result.stderrExcerpt)
        self.assertEqual(result.returncode, expected, value)
        return value

    def start(self, spec, expected=0, mode="full_build"):
        path = self.write(spec)
        result = self.cli("start", "--task", "Authorized design production", "--permission-mode", mode,
                          "--production-request", path, "--dry-run", expected=expected)
        if result.get("job"):
            self.evidence.append({"session": result["session"], "task_id": result["job"]["task_id"],
                                  "status": result["job"]["status"], "profile": result["hook"]["profile"]})
        return result, path

    def test_01_real_entrypoint_svg_and_main_review(self):
        spec = self.spec()
        result, path = self.start(spec)
        job = result["job"]
        self.assertEqual(result["invocations"], 1)
        self.assertEqual(job["agent_count"], 1)
        self.assertEqual(job["status"], "NEEDS_MAIN_REVIEW")
        self.assertEqual(job["result"]["qa"]["status"], "PASS")
        self.assertEqual([e["tool"] for e in job["tool_events"]][-3:], ["build_artifact", "render_preview", "technical_qa"])
        self.assertFalse(result["state"]["finalReadiness"]["finalAllowed"])
        duplicate = self.cli("run", "--session", result["session"], "--command", "/design-produce", "--production-request", path, "--dry-run")
        self.assertEqual(duplicate["invocations"], 0)
        self.assertTrue(duplicate["hook"]["duplicate"])
        changed = dict(spec, creative_constraints="Changed scope must conflict")
        conflict = self.cli("run", "--session", result["session"], "--command", "/design-produce", "--production-request", self.write(changed), "--dry-run", expected=2)
        self.assertIn("Idempotency conflict", conflict["error"])
        review = dict(task_id=job["task_id"], decision="APPROVE", reviewer="main", feedback="Inspected fixture and exact deliverable hashes.",
                      artifact_hashes=[m["sha256"] for m in job["result"]["artifacts"] if m["role"] == "deliverable"])
        approved = self.cli("review-production", "--session", result["session"], "--review", self.write(review))
        self.assertEqual(approved["job"]["status"], "APPROVED")
        self.assertFalse(approved["finalAllowed"], "Original Main workflow gates must still block delivery")
        from design_brain_runtime import final_readiness, REQUIRED_STAGES
        state = dict(result["state"], completedStages=REQUIRED_STAGES[:])
        self.assertTrue(final_readiness(state)["finalAllowed"])
        deliverable = Path(next(m["path"] for m in job["result"]["artifacts"] if m["role"] == "deliverable"))
        original = deliverable.read_bytes()
        try:
            deliverable.write_bytes(original + b'\n<!-- fixture tamper -->')
            self.assertFalse(final_readiness(state)["finalAllowed"])
        finally:
            deliverable.write_bytes(original)
        with self.assertRaises(ValueError):
            DesignResult.model_validate({**job["result"], "status": "APPROVED"})
        with self.assertRaises(ValueError):
            MainReviewDecision.model_validate({**review, "reviewer": "specialist"})

    def test_02_nonproduction_and_permissions(self):
        for change in ({"operation": "other"}, {"operation": "brainstorm"}, {"operation": "prompt"}, {"no_execution": True}, {"authorized": False}):
            with self.subTest(change=change):
                result, _ = self.start(self.spec(**change))
                self.assertEqual(result["invocations"], 0)
                self.assertFalse(result["hook"]["eligible"])
        denied, _ = self.start(self.spec(), expected=2, mode="plan_only")
        self.assertIn("requires full_build", denied["error"])
        old = self.cli("start", "--task", "Existing diagnostic workflow")
        self.assertNotIn("productionJobs", old["state"])
        status = self.cli("status", "--session", old["session"])
        self.assertEqual(status["state"]["permissionMode"], "diagnostic_only")
        self.cli("finalize", "--session", old["session"], expected=2)

    def test_03_pptx_native_regression(self):
        spec = self.spec(artifact_type="presentation", output_format="pptx",
                         units=[dict(id="slide-1", kind="slide", width=1280, height=720, instruction="Offline native regression fixture")])
        result, _ = self.start(spec)
        self.assertEqual(result["hook"]["profile"], "native_pptx")
        self.assertEqual(result["job"]["result"]["qa"]["status"], "PASS")
        files = result["job"]["result"]["artifacts"]
        self.assertTrue(any(m["format"] == "pptx" and m["editable"] for m in files))
        self.assertTrue(any("native-preview" in m["path"] for m in files))

    def test_04_profiles_and_unsupported(self):
        cap = self.cli("production-capabilities")
        self.assertEqual(cap["maximumSpecialists"], 1)
        for category in ("vector", "editorial_svg"):
            kind = "graphic" if category == "vector" else "page"
            result, _ = self.start(self.spec(artifact_type=category, units=[dict(id="unit-1", kind=kind, width=600, height=900, instruction="Editable fixture")]))
            self.assertEqual(result["hook"]["profile"], "editable_svg")
        result, _ = self.start(self.spec(artifact_type="photoshop", output_format="psd"), expected=2)
        self.assertIn("UNSUPPORTED", result["error"])
        result, _ = self.start(self.spec(required_features=["smart_objects"]), expected=2)
        self.assertIn("UNSUPPORTED native feature", result["error"])

    def test_05_tool_and_path_policy(self):
        with self.assertRaises(ValueError):
            DesignTask.model_validate(self.spec(allowed_tools=["shell"]))
        task = DesignTask.model_validate(self.spec())
        directory = self.directory / "policy-test"
        directory.mkdir()
        adapter = AuthorizedAdapters(task, directory, directory / "cancel")
        for name, args in (("shell", {"command": "echo unsafe"}), ("read_input", {"input_id": "secrets"}),
                           ("read_input", {"input_id": "brief", "path": "C:/Users"}),
                           ("write_unit", {"unit_id": "../escape", "nodes": []})):
            with self.subTest(name=name), self.assertRaises(ValueError):
                asyncio.run(adapter.invoke(name, args))
        for path in ("C:/Windows", str(ROOT / "scripts"), str(ROOT / "output/../../escape")):
            with self.subTest(path=path), self.assertRaises(ValueError):
                decision(DesignTask.model_validate(self.spec(output_dir=path)), "full_build")
        with self.assertRaises(ValueError):
            decision(DesignTask.model_validate(self.spec(inputs=[dict(id="brief", path=str(ROOT / "AGENTS.md"), sha256="0"*64, role="brief")])), "full_build")
        with self.assertRaises(ValueError):
            decision(DesignTask.model_validate(self.spec(inputs=[dict(id="brief", path=str(self.brief), sha256="0"*64, role="brief")])), "full_build")

    def test_06_lock_and_recovery(self):
        with single_worker():
            result, _ = self.start(self.spec(), expected=2)
            self.assertIn("BUSY", result["error"])
        spec = self.spec()
        task = DesignTask.model_validate(spec)
        identifier = task_id(task)
        atomic_json(job_path(identifier), dict(task_id=identifier, status="RUNNING", request_sha256=__import__('design_production.policy', fromlist=['canonical_hash']).canonical_hash(task.model_dump()), dry_run=True, task=task.model_dump(), owner_pid=999999))
        result, _ = self.start(spec, expected=2)
        self.assertEqual(result["job"]["status"], "UNKNOWN")
        self.assertEqual(result["invocations"], 0)
        recovered = self.cli("recover-production", "--session", result["session"], "--task-id", identifier)
        self.assertEqual(recovered["job"]["status"], "BLOCKED")

    def test_07_uncertainty_and_cancellation(self):
        task = DesignTask.model_validate(self.spec())
        directory = self.directory / "uncertainty"
        directory.mkdir()
        adapter = AuthorizedAdapters(task, directory, directory / "cancel")
        self.assertEqual(adapter.verify().status, "UNVERIFIED")
        adapter.cancel_path.write_text("cancel")
        with self.assertRaises(asyncio.CancelledError):
            asyncio.run(adapter.invoke("discover_capabilities", {}))
        adapter = AuthorizedAdapters(task, directory, directory / "missing-cancel")
        adapter.deadline = time.monotonic()-1
        with self.assertRaises(TimeoutError):
            asyncio.run(adapter.invoke("discover_capabilities", {}))

    def test_08_revision_budget_and_source_preservation(self):
        spec = self.spec()
        result, _ = self.start(spec)
        hashes = [(m["path"], m["sha256"]) for m in result["job"]["result"]["artifacts"]]
        review = dict(task_id=result["job"]["task_id"], decision="REVISE", reviewer="main", artifact_hashes=[], feedback="Keep scope; rerun the approved fixture for revision verification.")
        self.cli("review-production", "--session", result["session"], "--review", self.write(review))
        revised = dict(spec, revision=1)
        new = self.cli("run", "--session", result["session"], "--command", "/design-produce", "--production-request", self.write(revised), "--dry-run")
        self.assertEqual(new["job"]["status"], "NEEDS_MAIN_REVIEW")
        self.assertIn("Keep scope", new["job"]["prior_main_feedback"]["feedback"])
        for file, expected in hashes:
            self.assertEqual(digest(Path(file)), expected)
        with self.assertRaises(ValueError):
            DesignTask.model_validate(dict(spec, revision=3))

    def test_09_runtime_cancellation(self):
        spec = self.spec()
        identifier = task_id(DesignTask.model_validate(spec))
        request = self.write(spec)
        command = [sys.executable, "-B", str(ROOT / "scripts/design_brain_runtime.py"), "start", "--task", "Cancellation fixture",
                   "--permission-mode", "full_build", "--production-request", str(request), "--dry-run", "--json"]
        process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        try:
            deadline = time.monotonic()+15
            while not job_path(identifier).exists() and time.monotonic()<deadline:
                time.sleep(.05)
            record = load_job(identifier)
            self.cli("cancel-production", "--session", record["session"], "--task-id", identifier)
            stdout, stderr = process.communicate(timeout=20)
            result = json.loads(stdout)
            self.assertEqual(result["job"]["status"], "UNVERIFIED", stderr)
            self.assertFalse(result["finalAllowed"])
        finally:
            if process.poll() is None:
                from design_brain_process_utils import kill_process_tree
                kill_process_tree(process)

    def test_10_timeout_kills_owned_adapter(self):
        task = DesignTask.model_validate(self.spec(timeout_seconds=10))
        directory = self.directory / "timeout-process"
        directory.mkdir()
        adapter = AuthorizedAdapters(task, directory, directory / "cancel")
        owned = []
        popen = subprocess.Popen
        def capture(*args, **kwargs):
            child = popen(*args, **kwargs)
            owned.append(child)
            return child
        async def delayed(*args):
            await adapter.process([sys.executable, "-c", "import time; time.sleep(30)"], 30)
        with patch("design_production.specialist.execute", delayed), patch("design_production.adapters.subprocess.Popen", capture):
            adapter.deadline = time.monotonic() + 1
            with self.assertRaises(TimeoutError):
                asyncio.run(run_bounded(task, task_id(task), adapter, True))
        self.assertTrue(owned)
        self.assertTrue(all(child.poll() is not None for child in owned))

    def test_11_edit_existing_source(self):
        spec = self.spec()
        original, _ = self.start(spec)
        source = next(m for m in original["job"]["result"]["artifacts"] if m["format"] == "json" and m["editable"])
        spec = self.spec(operation="edit", inputs=spec["inputs"] + [dict(id="existing", role="editable_source", path=source["path"], sha256=source["sha256"])])
        edited, _ = self.start(spec)
        self.assertEqual(edited["job"]["status"], "NEEDS_MAIN_REVIEW")
        self.assertEqual(digest(Path(source["path"])), source["sha256"])
        changed = next(m for m in edited["job"]["result"]["artifacts"] if m["format"] == "json" and m["editable"])
        self.assertNotEqual(changed["sha256"], source["sha256"], "Editing must change the output, not merely copy the source")

    def test_12_reparse_and_execution_budget(self):
        from design_production.policy import output_root
        target = self.directory / "real-target"
        target.mkdir()
        link = self.directory / "link"
        if os.name == "nt":
            quote = lambda value: "'" + str(value).replace("'", "''") + "'"
            command = f"New-Item -ItemType Junction -Path {quote(link)} -Target {quote(target)} | Out-Null"
            subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], check=True, capture_output=True, timeout=15)
        else:
            link.symlink_to(target, target_is_directory=True)
        with self.assertRaises(ValueError):
            output_root(str(link / "escape"))
        task = DesignTask.model_validate(self.spec(max_tool_calls=3))
        directory = self.directory / "budget"
        directory.mkdir()
        adapter = AuthorizedAdapters(task, directory, directory / "cancel")
        for _ in range(3):
            asyncio.run(adapter.invoke("discover_capabilities", {}))
        with self.assertRaises(ValueError):
            asyncio.run(adapter.invoke("discover_capabilities", {}))

    @classmethod
    def tearDownClass(cls):
        atomic_json(cls.directory / "entrypoint-evidence.json", {"paid_model_calls": 0, "cases": cls.evidence})
        print("\nEVIDENCE: " + str(cls.directory / "entrypoint-evidence.json"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
