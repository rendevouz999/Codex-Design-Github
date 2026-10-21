"""Regression checks for visual PASS bypasses in runtime and lifecycle routes."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import design_brain_visual_gate as gate
import design_brain_runtime as runtime
import design_brain_build_session as lifecycle


class VisualRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def legacy_receipt(self):
        path = self.root / "post-build.json"
        path.write_text(json.dumps({"finalStatus": "READY", "auditPasses": {"pass3VisualLayoutQA": "PASS"}}))
        return path

    def test_runtime_bootstrap_preserves_spaced_arguments_and_output(self):
        session = self.root / "session with spaces"
        completed = subprocess.run(
            [sys.executable, "-B", runtime.__file__, "start", "--task", "presentation visual task with spaces",
             "--permission-mode", "full_build", "--expected-templates", "1", "--output-dir", str(session), "--json"],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("presentation visual task with spaces", payload["state"]["task"])
        self.assertEqual(session.resolve(), Path(payload["session"]).resolve())
        self.assertTrue((session / "session-state.json").is_file())

    def test_runtime_bootstrap_propagates_child_failure(self):
        completed = subprocess.run(
            [sys.executable, "-B", runtime.__file__, "not-a-valid-command"],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(2, completed.returncode)
        self.assertIn("invalid choice", completed.stderr)

    def test_legacy_visual_pass_without_manifest_is_blocked(self):
        result = gate.validate_post_build_receipt(self.legacy_receipt())
        self.assertEqual("BLOCKED", result["status"])
        self.assertTrue(any("manifests missing" in issue for issue in result["issues"]))

    def test_missing_or_malformed_receipt_is_blocked(self):
        missing = self.root / "missing.json"
        self.assertEqual("BLOCKED", gate.validate_post_build_receipt(missing)["status"])
        missing.write_text("[]")
        self.assertEqual("BLOCKED", gate.validate_post_build_receipt(missing)["status"])

    def test_old_runtime_completed_flags_cannot_claim_ready(self):
        state = {"completedStages": runtime.REQUIRED_STAGES[:], "permissionMode": "full_build", "openRepairTickets": []}
        result = runtime.final_readiness(state)
        self.assertFalse(result["finalAllowed"])
        self.assertIn("unverified stages", result["reason"])
        self.assertIn("post_build_audit", result["reason"])

    def test_route_post_build_without_actual_evidence_never_marks_stage(self):
        state = {"sessionId": "regression", "permissionMode": "full_build", "completedStages": [], "finalReadiness": {"finalAllowed": False}}
        args = argparse.Namespace(command_name="/design-post-build", session=str(self.root), simulate_fail="", visual_receipt="", build_artifact="")
        with patch.object(runtime, "load_state", return_value=state), patch.object(runtime, "append_history"), patch.object(runtime, "save_state") as save:
            result = runtime.command_run(args)
        self.assertEqual("BLOCKED", result["status"])
        self.assertNotIn("post_build_audit", state["completedStages"])
        self.assertEqual(state["toolResults"]["post_build_audit"]["executionState"], "not_verified")
        self.assertEqual(state["toolResults"]["post_build_audit"]["status"], "BLOCKED")
        save.assert_called_once()

    def test_lifecycle_registration_rejects_legacy_receipt_without_mutation(self):
        artifact = self.root / "artifact.svg"
        artifact.write_text("<svg/>")
        item = {"templateId": "one", "buildArtifactPath": str(artifact), "stages": []}
        ledger = {"templates": [item]}
        args = argparse.Namespace(session=str(self.root), template_id="one", receipt=str(self.legacy_receipt()))
        with patch.object(lifecycle, "load_ledger", return_value=ledger), patch.object(lifecycle, "save_ledger") as save:
            with self.assertRaisesRegex(SystemExit, "Cannot register post-build"):
                lifecycle.command_register_post_build(args)
        save.assert_not_called()
        self.assertNotIn("postBuildAuditPath", item)

    def test_final_lifecycle_rechecks_existing_visual_receipt(self):
        artifact = self.root / "artifact.svg"
        artifact.write_text("<svg/>")
        receipt = self.legacy_receipt()
        item = {"templateId": "one", "status": "fingerprint_locked", "postBuildAuditPath": str(receipt), "buildArtifactPath": str(artifact)}
        ledger = {"expectedTemplateCount": 1, "route": {"route": "test"}, "templates": [item]}
        result = lifecycle.verify_ledger_final(self.root, ledger, require_completion_receipt=False)
        self.assertFalse(result["safeToDeliver"])
        self.assertTrue(any("manifests missing" in issue for issue in result["remainingIssues"]))


if __name__ == "__main__":
    unittest.main()
