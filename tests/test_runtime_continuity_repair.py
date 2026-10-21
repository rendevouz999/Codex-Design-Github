"""Offline regressions: continuity, truthful runtime bookkeeping, and repair integrity."""
import argparse
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import design_brain_context_compact as compact
import design_brain_repair_ticket as tickets
import design_brain_runtime as runtime
import design_brain_post_build_audit as audit
from design_brain_post_build_smoke_test import Args as AuditArgs
from test_design_brain_visual_inspect import Fixture


def write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def ref(path):
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def bind_audit_inputs(payload, fixture, preparation=None):
    """Build actual file-byte dependency closure for test fixtures, never a fake QA run."""
    manifest = fixture.read()
    refs = [ref(fixture.artifact), ref(fixture.manifest)]
    refs.extend(frame["source"] for frame in manifest["frames"])
    refs.extend(view["file"] for frame in manifest["frames"] for view in frame["views"])
    if manifest.get("review_context"):
        refs.append(manifest["review_context"])
    if manifest["coverage"].get("render_inventory"):
        refs.append(manifest["coverage"]["render_inventory"])
    refs.append(manifest["main_approval"]["deck_overview"]["view"])
    if preparation is not None:
        refs.append(ref(preparation))
    unique = {row["path"]: row for row in refs}
    closure = [unique[path] for path in sorted(unique)]
    payload["auditInputRefs"] = closure
    payload["auditInputMissing"] = []
    payload["auditInputRevision"] = hashlib.sha256(json.dumps(closure, sort_keys=True,
        separators=(",", ":")).encode()).hexdigest()
    return payload


class Isolated(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.session = self.root / "session"
        self.session.mkdir()
        for module in (runtime, compact):
            patcher = patch.object(module, "STATE_ROOT", self.root / "global")
            patcher.start()
            self.addCleanup(patcher.stop)
        self.state = {"sessionId": "session", "projectRoot": str(self.root), "task": "create native pptx", "permissionMode": "full_build", "completedStages": [], "toolResults": {}}
        runtime.save_state(self.session, self.state)

    def args(self, **kwargs):
        return argparse.Namespace(session=str(self.session), command_name="/design-cognition", simulate_fail="", visual_receipt="", build_artifact="", stage_result="", **kwargs)

    def test_all_repeat_start_paths_preserve_state_bytes(self):
        before = (self.session / "session-state.json").read_bytes()
        for request in ("", str(self.root / "unopened-test-only.json")):
            args = argparse.Namespace(output_dir=str(self.session), task="create native PPTX",
                permission_mode="full_build", production_request=request,
                workflow_profile="efficient-v1", expected_templates=1, expected_slides=2)
            with self.assertRaises(ValueError):
                runtime.command_start(args)
            self.assertEqual((self.session / "session-state.json").read_bytes(), before)

    def test_post_build_pass3_attempt_counts_as_layout_repair(self):
        ticket = tickets.create_ticket(session_id="session", source_gate="post_build_pass3",
            issue="slide content overlap", session=self.session)
        check = self.root / "checked-pass3.txt"
        check.write_text("Synthetic inspection failed on the revised layout.")
        tickets.record_repair_attempt(ticket["ticketId"], session=self.session,
            attempt_id="pass3-patch-1", before_revision="layout-before",
            after_revision="layout-after", outcome="FAIL", evidence=[ref(check)])
        result = tickets.repair_accounting(self.session)
        self.assertEqual((result["repairCycles"], result["layoutRepairCycles"]), (1, 1))

    def test_routing_is_requested_not_executed(self):
        result = runtime.command_run(self.args())
        self.assertEqual(result["status"], "REQUESTED")
        state = runtime.load_state(self.session)
        self.assertNotIn("cognition", state["completedStages"])
        self.assertEqual(state["toolResults"]["cognition"]["executionState"], "requested")

    def test_route_uses_actual_selection(self):
        args = self.args()
        args.command_name = "/design-route"
        result = runtime.command_run(args)
        self.assertEqual(result["status"], "PASS")
        self.assertNotEqual(runtime.load_state(self.session)["route"], "website-template")
        self.assertEqual(result["executionSource"], "native_router")

    def test_legacy_completed_labels_do_not_establish_readiness(self):
        self.state["completedStages"] = runtime.REQUIRED_STAGES[:]
        result = runtime.final_readiness(self.state)
        self.assertFalse(result["finalAllowed"])
        self.assertIn("unverified", result["reason"])

    def test_external_result_requires_revision_bound_evidence(self):
        path = write(self.root / "gate.json", {"stage": "cognition", "status": "PASS", "executionState": "executed"})
        args = self.args()
        args.stage_result = str(path)
        result = runtime.command_run(args)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertNotIn("cognition", runtime.load_state(self.session)["completedStages"])

    def test_external_result_rejects_outside_project_references(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            outside = Path(elsewhere) / "unrelated.txt"
            outside.write_text("not this project's evidence")
            path = write(self.root / "gate.json", {"stage": "cognition", "status": "PASS", "executionState": "executed", "inputs": [ref(outside)], "evidence": [ref(outside)]})
            args = self.args()
            args.stage_result = str(path)
            self.assertEqual(runtime.command_run(args)["status"], "BLOCKED")

    def test_legacy_checkpoint_missing_action_gets_safe_string(self):
        _, path = self.checkpoint()
        runtime.command_checkpoint(argparse.Namespace(session=str(self.session), file=str(path), initialize=False))
        state = runtime.load_state(self.session)
        state["checkpoint"]["nextAction"] = None
        write(self.session / "session-state.json", state)
        result = compact.compact_session(self.session)
        self.assertIsInstance(result["summary"]["nextAction"], str)

    def test_current_external_result_records_provenance_and_invalidates_on_change(self):
        source = self.root / "source.svg"
        source.write_text("slide1")
        evidence = self.root / "measurement.json"
        evidence.write_text('{"overflow":false}')
        path = write(self.root / "gate.json", {"stage": "cognition", "status": "PASS", "executionState": "executed", "inputs": [ref(source)], "evidence": [ref(evidence)]})
        args = self.args()
        args.stage_result = str(path)
        result = runtime.command_run(args)
        self.assertEqual(result["status"], "RECORDED")
        self.assertEqual(result["executionSource"], "external_attestation")
        self.assertNotIn("cognition", runtime.verified_stages(runtime.load_state(self.session)))
        source.write_text("changed")
        state = runtime.load_state(self.session)
        self.assertNotIn("cognition", runtime.verified_stages(state))

    def test_compact_refreshes_before_publishing(self):
        tickets.create_ticket(session_id="session", source_gate="cognition", issue="missing text", session=self.session)
        payload = runtime.command_compact(argparse.Namespace(session=str(self.session)))
        self.assertEqual(len(payload["summary"]["openRepairTickets"]), 1)
        self.assertNotIn("openTickets", payload["summary"])

    def test_compact_uses_readiness_blocker(self):
        self.state.update(permissionMode="diagnostic_only", completedStages=runtime.REQUIRED_STAGES[:], missingStages=[], finalReadiness={"finalAllowed": False, "reason": "diagnostic_only cannot claim final READY"})
        write(self.session / "session-state.json", self.state)
        result = compact.compact_session(self.session)
        self.assertNotEqual(result["summary"]["nextAction"], "Finalize delivery.")
        self.assertIn("diagnostic_only", result["summary"]["nextAction"])

    def test_direct_compactor_refreshes_ticket_changes(self):
        tickets.create_ticket(session_id="session", source_gate="layout", issue="new issue", session=self.session)
        result = compact.compact_session(self.session)
        self.assertEqual(len(result["summary"]["openRepairTickets"]), 1)

    def test_resume_inherits_changed_shared_dependency(self):
        _, path = self.checkpoint()
        shared = self.session / "spec_lock.md"
        shared.write_text("theme-one")
        payload = json.loads(path.read_text())
        payload["dependencies"]["source"] = [{"path": shared.name, "sha256": ref(shared)["sha256"]}]
        write(path, payload)
        runtime.command_checkpoint(argparse.Namespace(session=str(self.session), file=str(path), initialize=False))
        shared.write_text("theme-two")
        result = runtime.command_resume(argparse.Namespace(session=str(self.session)))
        self.assertEqual(result["checkpoint"]["slides"][0]["currency"], "stale")
        self.assertEqual(result["affectedSlideIds"], [1, 2])
        self.assertFalse(result["finalAllowed"])

    def test_old_execution_receipt_cannot_clear_new_close_rerun_debt(self):
        ticket = tickets.create_ticket(session_id="session", source_gate="cognition", issue="gap", session=self.session)
        tickets.close_ticket(ticket["ticketId"], self.session)
        source = self.root / "slide.svg"
        source.write_text("slide")
        path = write(self.root / "old-gate.json", {"stage": "cognition", "status": "PASS", "executionState": "executed", "executedAt": "2020-01-01T00:00:00+00:00", "inputs": [ref(source)], "evidence": [ref(source)]})
        args = self.args()
        args.stage_result = str(path)
        runtime.command_run(args)
        self.assertTrue(tickets.load_tickets(tickets.ticket_file(self.session))[0]["rerunGateRequired"])

    def checkpoint(self):
        # Canonical destination schema: integer slide IDs, complete roster,
        # slide-local file refs and shared dependencies. All evidence is synthetic.
        source = self.session / "slide1.svg"
        source.write_text("slide-one")
        payload = runtime.initial_checkpoint(self.state, self.session, 2)
        payload["slides"][0]["status"] = "accepted"
        payload["slides"][0]["artifacts"] = [{"path": source.name, "sha256": ref(source)["sha256"]}]
        payload["activeConstraints"] = ["native editable", "first-three review before slide4"]
        payload["nextAction"] = {"actor": "engineer", "target": "slide 2",
            "action": "Author the remaining slide using current assets",
            "expectedOutput": "fresh native slide 2 artifact", "checks": ["originality", "native render"]}
        path = write(self.session / "checkpoint-input.json", payload)
        return source, path

    def test_resume_is_session_and_revision_bound(self):
        source, path = self.checkpoint()
        runtime.command_checkpoint(argparse.Namespace(session=str(self.session), file=str(path), initialize=False))
        result = runtime.command_resume(argparse.Namespace(session=str(self.session)))
        self.assertEqual(result["checkpoint"]["slides"][0]["currency"], "current")
        self.assertEqual(result["checkpoint"]["nextSlide"], 2)
        self.assertEqual(result["checkpoint"]["activeConstraints"], ["native editable", "first-three review before slide4"])
        source.write_text("changed")
        result = runtime.command_resume(argparse.Namespace(session=str(self.session)))
        self.assertEqual(result["checkpoint"]["slides"][0]["currency"], "stale")
        self.assertEqual(result["checkpoint"]["nextSlide"], 1)
        self.assertFalse(result["finalAllowed"])

    def test_resume_does_not_select_global_other_project(self):
        write(self.root / "global" / "context-summary.json", {"sessionId": "other-project", "finalAllowed": True})
        result = runtime.command_resume(argparse.Namespace(session=str(self.session)))
        self.assertEqual(result["checkpoint"]["status"], "UNKNOWN")
        self.assertFalse(result["finalAllowed"])

    def test_checkpoint_rejects_cross_session_and_outside_project(self):
        _, path = self.checkpoint()
        payload = json.loads(path.read_text())
        payload["sessionId"] = "other-session"
        write(path, payload)
        with self.assertRaises(ValueError):
            runtime.command_checkpoint(argparse.Namespace(session=str(self.session), file=str(path), initialize=False))

    def test_corrupt_tickets_preserve_file_and_block(self):
        path = self.session / "repair-tickets.json"
        path.write_text("broken-json")
        with self.assertRaises(ValueError):
            tickets.create_ticket(session_id="session", source_gate="layout", issue="bad", session=self.session)
        self.assertEqual(path.read_text(), "broken-json")
        runtime.save_state(self.session, self.state)
        self.assertFalse(self.state["finalReadiness"]["finalAllowed"])
        self.assertIn("recovery", self.state["finalReadiness"]["reason"].lower())

    def test_repeated_issue_deduplicated_and_audits_do_not_count(self):
        args = dict(session_id="session", source_gate="layout", issue="Text overlap", session=self.session)
        one = tickets.create_ticket(**args, input_revision="rev1")
        two = tickets.create_ticket(**args, input_revision="rev1")
        self.assertEqual(one["ticketId"], two["ticketId"])
        self.assertEqual(len(tickets.load_tickets(tickets.ticket_file(self.session))), 1)
        self.assertEqual(tickets.repair_accounting(self.session, 3)["repairCycles"], 0)

    def test_repair_attempt_requires_change_and_is_idempotent(self):
        ticket = tickets.create_ticket(session_id="session", source_gate="layout_audit", issue="Text overlap", session=self.session, input_revision="rev1")
        evidence = self.root / "check.json"
        evidence.write_text("checked")
        kwargs = dict(session=self.session, attempt_id="patch-1", before_revision="rev1", after_revision="rev2", outcome="FAIL", evidence=[ref(evidence)])
        tickets.record_repair_attempt(ticket["ticketId"], **kwargs)
        tickets.record_repair_attempt(ticket["ticketId"], **kwargs)
        accounting = tickets.repair_accounting(self.session, 1)
        self.assertEqual(accounting["repairCycles"], 1)
        self.assertEqual(accounting["layoutRepairCycles"], 1)
        self.assertTrue(accounting["budgetExhausted"])
        kwargs.update(attempt_id="same-input", before_revision="rev2", after_revision="rev2")
        with self.assertRaises(ValueError):
            tickets.record_repair_attempt(ticket["ticketId"], **kwargs)

    def test_admin_close_does_not_claim_quality_or_skip_rerun(self):
        ticket = tickets.create_ticket(session_id="session", source_gate="layout", issue="bad", session=self.session)
        result = tickets.close_ticket(ticket["ticketId"], self.session)
        self.assertTrue(result["rerunGateRequired"])
        self.assertEqual(result["qualityStatus"], "unverified")
        runtime.save_state(self.session, self.state)
        self.assertIn("rerun", self.state["finalReadiness"]["reason"])


    def test_audit_with_artifact_keeps_exact_input_revision(self):
        build = self.root / "artifact-audit"
        build.mkdir()
        artifact = build / "synthetic-test.pptx"
        artifact.write_bytes(b"test-only mechanical artifact, no quality verdict")
        audit.prepare_completion(build, artifact)
        args = AuditArgs(build)
        args.visual_artifact = str(artifact)
        receipt = audit.run_post_build_audit(args)
        self.assertIn(ref(artifact), receipt["auditInputRefs"])
        self.assertEqual(sum(x["path"] == str(artifact.resolve()) for x in receipt["auditInputRefs"]), 1)
        self.assertTrue(audit.audit_inputs_current(receipt))
        artifact.write_bytes(b"changed test-only artifact")
        self.assertFalse(audit.audit_inputs_current(receipt))

    def test_audit_reports_deduplicated_persistent_attempt_counts(self):
        build = self.root / "build"
        build.mkdir()
        args = AuditArgs(build)
        args.max_repair_cycles = 1
        first = audit.run_post_build_audit(args)
        second = audit.run_post_build_audit(args)
        records = tickets.load_tickets(tickets.ticket_file(build))
        self.assertEqual(first["repairCycles"], 0)
        self.assertEqual(second["repairCycles"], 0)
        self.assertEqual(len(records), len({item["issueId"] for item in records}))
        evidence = self.root / "actual-check.txt"
        evidence.write_text("offline changed-input check failed")
        tickets.record_repair_attempt(records[0]["ticketId"], session=build, attempt_id="patch-one", before_revision="before", after_revision="after", outcome="FAIL", evidence=[ref(evidence)])
        third = audit.run_post_build_audit(args)
        self.assertEqual(third["repairCycles"], 1)
        self.assertTrue(third["repairAccounting"]["budgetExhausted"])
        self.assertEqual(third["finalStatus"], "BLOCKED")
        fourth = audit.run_post_build_audit(args)
        self.assertEqual(fourth["repairCycles"], 1)

    def test_compact_persists_pointer_before_state_hash(self):
        result = runtime.command_compact(argparse.Namespace(session=str(self.session)))
        state = runtime.load_state(self.session)
        self.assertEqual(state["compactContextPath"], result["contextPath"])
        self.assertEqual(result["summary"]["stateSha256"], ref(self.session / "session-state.json")["sha256"])

    def test_pending_completion_is_preparation_not_final(self):
        path = self.root / "artifact.pptx"
        path.write_text("pptx-fixture")
        payload = audit.prepare_completion(self.root, path)
        self.assertEqual(payload["finalStatus"], "PENDING_AUDIT")
        self.assertTrue(audit.completion_receipt_exists(self.root))
        with self.assertRaises(ValueError):
            audit.finalize_completion(self.root, self.root / "missing-audit.json", path)

    def test_final_completion_binds_current_audit_and_artifact(self):
        fixture = Fixture()
        self.addCleanup(fixture.close)
        artifact = fixture.artifact
        receipt = fixture.write_receipt()
        payload = json.loads(receipt.read_text())
        payload.update(auditPhase="evidence", completionPhase="pending_final", finalAllowed=False, buildDir=str(self.root), artifact=ref(artifact), remainingIssues=[], limitations=[])
        payload["auditPasses"].update(pass0SerialProvenance="PASS", pass1OriginalityBatchSimilarity="PASS", pass2DesignSystemSourceHygiene="PASS")
        audit.prepare_completion(self.root, artifact)
        write(receipt, bind_audit_inputs(payload, fixture, self.root / "completion-preparation.json"))
        final = audit.finalize_completion(self.root, receipt, artifact)
        self.assertEqual(final["phase"], "final")
        self.assertEqual(final["audit"], ref(receipt))
        self.assertEqual(final["preparation"], ref(self.root / "completion-preparation.json"))
        self.assertTrue(audit.validate_final_completion(self.root / "completion-receipt.json", receipt, artifact))
        artifact.write_text("new deck")
        self.assertFalse(audit.validate_final_completion(self.root / "completion-receipt.json", receipt, artifact))
        with self.assertRaises(ValueError):
            audit.finalize_completion(self.root, receipt, artifact)

    def test_auxiliary_audited_input_drift_invalidates_final_without_artifact_change(self):
        fixture = Fixture()
        self.addCleanup(fixture.close)
        receipt = fixture.write_receipt()
        artifact = fixture.artifact
        audit.prepare_completion(self.root, artifact)
        payload = json.loads(receipt.read_text())
        payload.update(auditPhase="evidence", completionPhase="pending_final", finalAllowed=False, buildDir=str(self.root), artifact=ref(artifact), remainingIssues=[], limitations=[])
        payload["auditPasses"].update(pass0SerialProvenance="PASS",
            pass1OriginalityBatchSimilarity="PASS", pass2DesignSystemSourceHygiene="PASS")
        write(receipt, bind_audit_inputs(payload, fixture, self.root / "completion-preparation.json"))
        audit.finalize_completion(self.root, receipt, artifact)
        final_path = self.root / "completion-receipt.json"
        self.assertTrue(audit.validate_final_completion(final_path, receipt, artifact))
        artifact_before = ref(artifact)
        view = fixture.root / "test-only-final-deck-overview.png"
        view.write_bytes(view.read_bytes() + b"changed-support-byte")
        self.assertEqual(ref(artifact), artifact_before)
        self.assertFalse(audit.validate_final_completion(final_path, receipt, artifact))
        with self.assertRaises(ValueError):
            audit.finalize_completion(self.root, receipt, artifact)

    def test_design_system_input_changed_after_audit_invalidates_final(self):
        fixture = Fixture()
        self.addCleanup(fixture.close)
        receipt = fixture.write_receipt()
        artifact = fixture.artifact
        audit.prepare_completion(self.root, artifact)
        payload = json.loads(receipt.read_text())
        payload.update(auditPhase="evidence", completionPhase="pending_final", finalAllowed=False,
            buildDir=str(self.root), artifact=ref(artifact), remainingIssues=[], limitations=[])
        payload["auditPasses"].update(pass0SerialProvenance="PASS",
            pass1OriginalityBatchSimilarity="PASS", pass2DesignSystemSourceHygiene="PASS")
        payload = bind_audit_inputs(payload, fixture, self.root / "completion-preparation.json")
        design = write(self.root / "design-system-source-test.json", {"fixtureOnly": True, "revision": 1})
        refs = sorted([*payload["auditInputRefs"], ref(design)], key=lambda item: item["path"])
        payload["auditInputRefs"] = refs
        payload["auditInputRevision"] = hashlib.sha256(json.dumps(refs, sort_keys=True,
            separators=(",", ":")).encode()).hexdigest()
        write(receipt, payload)
        audit.finalize_completion(self.root, receipt, artifact)
        self.assertTrue(audit.validate_final_completion(self.root / "completion-receipt.json", receipt, artifact))
        write(design, {"fixtureOnly": True, "revision": 2})
        self.assertFalse(audit.validate_final_completion(self.root / "completion-receipt.json", receipt, artifact))

    def test_final_completion_rejects_partial_audit_pass_set(self):
        fixture = Fixture()
        self.addCleanup(fixture.close)
        receipt = fixture.write_receipt()
        payload = json.loads(receipt.read_text())
        payload.update(auditPhase="evidence", completionPhase="pending_final", finalAllowed=False, buildDir=str(self.root), artifact=ref(fixture.artifact), remainingIssues=[], limitations=[])
        write(receipt, bind_audit_inputs(payload, fixture))
        with self.assertRaises(ValueError):
            audit.finalize_completion(self.root, receipt, fixture.artifact)

    def test_runtime_finalizes_only_current_full_attested_chain(self):
        # Synthetic accountabilities exercise integrity, never actual product QA.
        fixture = Fixture()
        self.addCleanup(fixture.close)
        receipt = fixture.write_receipt()
        audit.prepare_completion(self.root, fixture.artifact)
        payload = json.loads(receipt.read_text())
        payload.update(auditPhase="evidence", completionPhase="pending_final", finalAllowed=False, buildDir=str(self.root), artifact=ref(fixture.artifact), remainingIssues=[], limitations=[])
        payload["auditPasses"].update(pass0SerialProvenance="PASS", pass1OriginalityBatchSimilarity="PASS", pass2DesignSystemSourceHygiene="PASS")
        write(receipt, bind_audit_inputs(payload, fixture, self.root / "completion-preparation.json"))
        source = self.root / "test-only.svg"
        source.write_text("synthetic continuity fixture; not product source")
        for stage in runtime.REQUIRED_STAGES:
            if stage in {"completion_receipt", "verify_final", "post_build_audit"}:
                continue
            args = self.args()
            args.command_name = next(command for command, mapped in runtime.COMMAND_TO_STAGE.items() if mapped == stage)
            path = write(self.root / f"{stage}.json", {"stage": stage, "status": "PASS", "executionState": "executed", "inputs": [ref(source)], "evidence": [ref(source)], "scope": "Synthetic test attestation only"})
            args.stage_result = str(path)
            expected = "PASS" if stage == "route" else "RECORDED"
            self.assertEqual(runtime.command_run(args)["status"], expected)
            if stage != "route":
                self.assertNotIn(stage, runtime.verified_stages(runtime.load_state(self.session)))
        args = self.args()
        args.command_name = "/design-post-build"
        args.visual_receipt = str(receipt)
        args.build_artifact = str(fixture.artifact)
        self.assertEqual(runtime.command_run(args)["status"], "PASS")
        result = runtime.command_finalize(argparse.Namespace(session=str(self.session)))
        self.assertFalse(result["finalAllowed"])
        self.assertIn("unverified", result["requiredRepairs"][0])
        source.write_text("changed")
        self.assertFalse(runtime.command_finalize(argparse.Namespace(session=str(self.session)))["finalAllowed"])


if __name__ == "__main__":
    unittest.main()
