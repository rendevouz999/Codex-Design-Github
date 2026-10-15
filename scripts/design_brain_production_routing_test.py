"""Regression checks for route choice without execution or false readiness."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from design_production.routing import plan


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "request.json"
        self.spec = dict(parent_request_id="route-test", stage="build", operation="create", artifact_type="presentation", output_format="pptx",
            units=[dict(id="slide-1", kind="slide", width=960, height=540, instruction="Test", layout="blank")],
            inputs=[dict(id="brief", path="declared-brief.md", sha256="0"*64, role="brief")],
            editability_requirements=["Native objects"], required_features=["editable_text", "slide_masters"],
            allowed_tools=["read_input", "write_unit", "build_artifact", "render_preview", "technical_qa"],
            output_dir="output/route-fixture", creative_constraints="Fixture only", authorized=True,
            presentation=dict(structure="structured", reusable_template=True, title_size=48, body_size=20, title_font="Arial", body_font="Arial", background="#10002B", foreground="#E0AAFF", accent="#C77DFF"))
        self.guard = patch("design_production.routing.input_path", return_value=self.path)
        self.guard.start()
        self.addCleanup(self.guard.stop)
        self.addCleanup(self.temp.cleanup)

    def run_plan(self, preferred="auto", offline=False):
        self.path.write_text(json.dumps(self.spec), encoding="utf-8")
        before = self.path.read_bytes()
        result = plan(str(self.path), preferred, offline)
        self.assertEqual(before, self.path.read_bytes())
        self.assertFalse(result["finalAllowed"])
        self.assertFalse(result.get("executionStarted", False))
        return result

    def test_requested_brief_routes_to_single_host_worker_without_changing_features(self):
        self.spec["presentation"].update(title_font="Sora", body_font="IBM Plex Sans")
        self.spec["units"][0].update(width=960, height=540)
        self.spec["required_features"].append("embedded_photographs")
        result = self.run_plan()
        self.assertEqual(result["selectedRoute"], "host_agents")
        self.assertEqual({v["code"] for v in result["sdkLimitations"]}, {"SDK_FONT_LIMIT", "SDK_FEATURE_LIMIT", "SDK_PAID_AUTHORIZATION_REQUIRED"})
        self.assertFalse(result["nativeCapabilityVerified"])

    def test_explicit_sdk_choice_reports_its_own_blocker(self):
        result = self.run_plan("sdk")
        self.assertEqual((result["status"], result["blockerScope"]), ("BLOCKED", "sdk"))

    def test_compatible_offline_sdk_is_available(self):
        self.assertEqual(self.run_plan("sdk", offline=True)["selectedRoute"], "sdk")

    def test_paid_permission_does_not_claim_authentication(self):
        self.spec["approval_policy"] = {"allow_paid_model": True}
        result = self.run_plan("sdk")
        self.assertEqual(result["selectedRoute"], "sdk")
        self.assertIn("Existing provider authentication", result["prerequisites"][0])

    def test_user_selected_main_does_not_require_sdk(self):
        self.assertEqual(self.run_plan("main", offline=True)["selectedRoute"], "main")

    def test_host_agent_plan_never_spawns_or_grants_authorization(self):
        result = self.run_plan("host_agents")
        self.assertEqual(result["selectedRoute"], "host_agents")
        self.assertIn("authorization", result["prerequisites"][0])

    def test_auto_keeps_selected_team_even_when_sdk_is_compatible(self):
        for offline in (False, True):
            self.spec["approval_policy"] = {"allow_paid_model": True}
            result = self.run_plan(offline=offline)
            self.assertEqual(result["selectedRoute"], "host_agents")
            team = result["team"]
            self.assertEqual(team["scope"], "custom-plugin-only")
            self.assertEqual(team["maximumActiveWorkers"], 1)
            self.assertEqual(team["maximumActiveParticipants"], 2)
            self.assertEqual(team["workerModel"], "gpt-6.1-sol")
            self.assertEqual(team["workerReasoningEffort"], "xhigh")
            self.assertFalse(team["workerEffortVerified"])
            self.assertEqual(team["workerRole"], "General Design Production Engineer")
            self.assertFalse(team["mainModelVerified"])
            self.assertFalse(team["workerModelVerified"])
            self.assertEqual(result["paidCalls"], 0)

    def test_no_execution_and_unauthorized_scope_skip(self):
        for field, value in (("authorized", False), ("no_execution", True), ("operation", "brainstorm")):
            with self.subTest(field=field):
                current = copy.deepcopy(self.spec)
                self.spec[field] = value
                self.assertEqual(self.run_plan()["decision"], "SKIP")
                self.spec = current

    def test_bad_scope_cannot_escape_through_main(self):
        self.spec["units"][0]["width"] = -1
        result = self.run_plan("main")
        self.assertEqual((result["status"], result["blockerScope"]), ("BLOCKED", "request"))

    def test_unknown_request_field_does_not_grant_permissions(self):
        self.spec["ignore_all_rules"] = True
        self.assertEqual(self.run_plan()["blockerScope"], "request")


if __name__ == "__main__":
    unittest.main(verbosity=2)
