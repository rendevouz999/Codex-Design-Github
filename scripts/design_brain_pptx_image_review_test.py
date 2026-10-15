"""Scenario regressions for the read-only PPTX image receipt workflow.

All assets/evidence are synthetic bytes, not real visually reviewed deck imagery.
Run: python -B scripts/design_brain_pptx_image_review_test.py
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

sys.dont_write_bytecode = True
import design_brain_pptx_image_review as review


class ImageReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pptx-image-review-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve() / "images"
        self.base.mkdir()
        self.path = self.base / "image_review.json"
        self.asset = self.ref("original.jpg", b"synthetic asset bytes")
        self.visual = self.ref("review/context.png", b"synthetic visual evidence")
        self.license = self.ref("review/license.txt", b"synthetic source/terms evidence")
        self.native = self.ref("review/native-qa.txt", b"synthetic Main native QA evidence")
        self.record = {"filename": "original.jpg", "provider": "pexels", "status": "sourced",
                       "source_page_url": "https://www.pexels.com/photo/fixture/",
                       "license_name": "Pexels License", "license_url": "https://www.pexels.com/license/",
                       "license_tier": "no-attribution", "attribution_required": False,
                       "attribution_text": "original.jpg via Pexels"}
        self.save_sources()
        self.data = {"schema_version": 2, "deck_id": "stable-deck", "canvas_inches": {"width": 12, "height": 6},
                     "deck_purpose": "Explain sensor operation", "visual_tone": "Precise technical documentary",
                     "source_manifest": "image_sources.json", "slots": []}
        self.slot = {"slot_id": "cover-subject", "slide_number": 3, "slide_title": "A concrete subject",
                     "message": "Show the relevant subject", "image_brief": "Subject at right; clear crop",
                     "rounds": [], "rendering_defects": []}
        self.data["slots"].append(self.slot)
        self.handoff = {"reviewer": "main", "reason": "Subject supports the slide message",
                        "round_id": "engineer-1", "candidate_id": "e1", "slide_number": 3,
                        "asset": self.asset, "source_filename": "original.jpg",
                        "placement_inches": {"x": 7, "y": 1, "width": 4, "height": 3},
                        "crop_fit": "fill", "focal_crop_direction": "Keep subject at the left third",
                        "protected_subject_areas": "Preserve complete subject", "text_safe_area": "Text stays outside image",
                        "semantic_role": "Show subject in use", "alt_text": "Fixture subject in use",
                        "replacement_instructions": "Replace native picture; preserve crop intent",
                        "provenance_review": {"reviewer": "main", "decision": "approved",
                                              "intended_use": "editable-commercial-template",
                                              "reason": "MAIN checked source and current terms for this use",
                                              "source_record_sha256": review.json_digest(self.record),
                                              "license_evidence": [self.license]}}

    def ref(self, name, content):
        path = self.base / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return {"path": str(path), "sha256": review.file_digest(path)}

    def save_sources(self):
        (self.base / "image_sources.json").write_text(json.dumps({"items": [self.record]}), encoding="utf-8")

    def round(self, round_id, verdict="reject", owner="engineer", candidate=None):
        candidate = candidate or round_id + "-candidate"
        value = {"round_id": round_id, "slide_number": 3, "search_owner": owner,
                 "provider": "pexels", "query": "concrete subject", "candidate_ids": [candidate],
                 "reviewer": "main", "verdict": verdict, "reason": "Subject or crop does not fit this slide",
                 "slide_context_seen": True, "visual_evidence": [self.visual]}
        if verdict == "accept":
            value.update(fit_review={key: {"verdict": "pass", "reason": "MAIN verified current " + key + " fit"} for key in ("tone", "content", "purpose")},
                         selected_candidate_id=candidate, asset_sha256=self.asset["sha256"],
                         placement_sha256=review.placement_digest(self.data, self.slot, self.handoff))
        if verdict == "blocked":
            value.update(blocked_kind="network", candidate_ids=[], visual_evidence=[], slide_context_seen=False)
        self.slot["rounds"].append(value)
        return value

    def accepted(self, takeover=False):
        if takeover:
            self.round("engineer-1")
            self.round("engineer-2")
        round_id, candidate = ("main-1", "m1") if takeover else ("engineer-1", "e1")
        self.handoff.update(round_id=round_id, candidate_id=candidate)
        self.slot["handoff"] = self.handoff
        return self.round(round_id, "accept", "main" if takeover else "engineer", candidate)

    def final(self):
        self.accepted()
        path = self.base.parent / "fixture.pptx"
        with ZipFile(path, "w") as archive:
            archive.writestr("ppt/presentation.xml", '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldIdLst><p:sldId id="256"/><p:sldId id="257"/><p:sldId id="258"/></p:sldIdLst><p:sldSz cx="10972800" cy="5486400"/></p:presentation>')
        self.data["deck"] = {"path": str(path), "sha256": review.file_digest(path)}
        self.slot["final_review"] = {"reviewer": "main", "verdict": "pass", "reason": "MAIN inspected render, credit and replaceability",
                                     "round_id": self.handoff["round_id"], "candidate_id": self.handoff["candidate_id"],
                                     "slide_number": 3, "asset_sha256": self.asset["sha256"],
                                     "placement_sha256": review.placement_digest(self.data, self.slot, self.handoff),
                                     "deck_sha256": self.data["deck"]["sha256"], "screenshot": self.visual,
                                     "native_picture_editable": True, "native_picture_evidence": [self.native]}

    def check(self, stage="progress"):
        self.path.write_text(json.dumps(self.data), encoding="utf-8")
        return review.validate(self.path, stage)

    def blocked(self, stage="progress", contains=None):
        result = self.check(stage)
        self.assertEqual(result["status"], "BLOCKED", result)
        if contains:
            self.assertIn(contains, " ".join(result["errors"]))

    def test_two_rejections_require_main_and_other_slots_remain_independent(self):
        self.round("engineer-1")
        self.round("engineer-2")
        second = copy.deepcopy(self.slot)
        second.update(slot_id="detail", slide_number=8, rounds=[])
        self.data["slots"].append(second)
        result = self.check()
        self.assertEqual(result["status"], "MAIN_SEARCH_REQUIRED")
        self.assertEqual([(r["engineer_rejected_rounds"], r["next_search_owner"]) for r in result["slots"]], [(2, "main"), (0, "engineer")])
        self.blocked("handoff", "accepted round missing")

    def test_identical_round_duplicates_count_once_but_conflicts_fail(self):
        first = self.round("engineer-1")
        self.slot["rounds"].append(copy.deepcopy(first))
        self.assertEqual(self.check()["slots"][0]["engineer_rejected_rounds"], 1)
        self.slot["rounds"][-1]["reason"] = "Conflicting revision"
        self.blocked(contains="conflicting duplicate")

    def test_third_engineer_round_cannot_reject_accept_or_hide_as_blocked(self):
        for verdict in ("reject", "accept", "blocked"):
            with self.subTest(verdict=verdict):
                self.slot["rounds"] = []
                self.round("engineer-1")
                self.round("engineer-2")
                self.round("engineer-3", verdict)
                self.blocked(contains="MAIN_SEARCH_REQUIRED")

    def test_takeover_selection_must_belong_to_main_round_and_not_prior_reject(self):
        accepted = self.accepted(takeover=True)
        self.assertEqual(self.check("handoff")["status"], "PASS")
        accepted["selected_candidate_id"] = "engineer-1-candidate"
        self.blocked(contains="absent from this round")
        accepted["candidate_ids"].append("engineer-1-candidate")
        self.blocked(contains="previously rejected")

    def test_blocked_provider_events_do_not_consume_rejections(self):
        self.round("outage-1", "blocked")
        self.round("engineer-1")
        self.round("outage-2", "blocked")
        self.accepted()
        # The acceptance uses a fresh ID; reusing a rejected ID conflicts.
        self.slot["rounds"][-1]["round_id"] = "engineer-accept"
        self.handoff["round_id"] = "engineer-accept"
        self.assertEqual(self.check("handoff")["status"], "PASS")
        self.assertEqual(self.check()["slots"][0]["engineer_rejected_rounds"], 1)

    def test_rendering_defect_never_counts_and_later_unsuitability_keeps_history(self):
        self.accepted()
        self.slot["rendering_defects"] = [{"event_id": "crop-repair", "reviewer": "main", "status": "resolved",
                                          "reason": "Correct subject clipped by layout; repaired crop", "visual_evidence": [self.visual]}]
        self.assertEqual(self.check()["slots"][0]["engineer_rejected_rounds"], 0)
        self.round("engineer-later-reject", candidate="e1")
        self.assertEqual(self.check()["slots"][0]["engineer_rejected_rounds"], 1)
        self.blocked("handoff", "accepted round missing")

    def test_stable_slot_history_survives_slide_query_provider_changes(self):
        self.round("engineer-1")
        self.slot["slide_number"] = 9
        row = self.round("engineer-2")
        row.update(slide_number=9, provider="unsplash", query="different query")
        result = self.check()
        self.assertEqual(result["status"], "MAIN_SEARCH_REQUIRED")
        self.assertEqual(result["slots"][0]["slot_id"], "cover-subject")
        self.data["slots"].append(copy.deepcopy(self.slot))
        self.blocked(contains="duplicate stable slot_id")

    def test_round_id_cannot_be_reused_for_different_slot(self):
        self.round("engineer-1")
        second = copy.deepcopy(self.slot)
        second["slot_id"] = "second-slot"
        self.data["slots"].append(second)
        self.blocked(contains="conflicting duplicate round_id")

    def test_main_must_attest_real_visual_context_and_evidence_is_hashed(self):
        row = self.round("engineer-1")
        row["reviewer"] = "extra-reviewer"
        self.blocked(contains="reviewer must be main")
        row["reviewer"] = "main"
        row["slide_context_seen"] = False
        self.blocked(contains="slide context")
        row["slide_context_seen"] = True
        Path(self.visual["path"]).write_bytes(b"changed screenshot")
        self.blocked(contains="file hash mismatch")

    def test_handoff_is_possible_before_export_and_valid_on_override_canvas(self):
        self.accepted()
        self.assertNotIn("deck", self.data)
        self.assertEqual(self.check("handoff")["status"], "PASS")
        self.assertEqual(self.data["canvas_inches"]["width"], 12)
        self.handoff["placement_inches"]["width"] = 6
        self.blocked("handoff", "outside declared actual canvas")

    def test_asset_missing_modified_or_relative_is_blocked(self):
        self.accepted()
        original = self.asset["path"]
        self.asset["path"] = "original.jpg"
        self.blocked("handoff", "must be absolute")
        self.asset["path"] = original
        Path(original).write_bytes(b"different image")
        self.blocked("handoff", "hash mismatch")
        Path(original).unlink()
        self.blocked("handoff", "file missing")

    def test_current_handoff_cannot_reuse_old_asset_crop_or_slide_review(self):
        self.accepted()
        self.handoff["focal_crop_direction"] = "Crop to the other edge"
        self.blocked("handoff", "binding is stale")
        self.slot["slide_number"] = 4
        self.handoff["slide_number"] = 4
        self.blocked("handoff", "slide renumbering")

    def test_changed_deck_identity_or_slide_purpose_invalidates_acceptance(self):
        self.accepted()
        for target, key in ((self.data, "deck_id"), (self.slot, "slide_title"),
                            (self.slot, "message"), (self.slot, "image_brief")):
            with self.subTest(key=key):
                original = target[key]
                target[key] = "Changed purpose or identity"
                self.blocked("handoff", "binding is stale")
                target[key] = original

    def test_adopted_filename_requires_canonical_source_record(self):
        self.accepted()
        self.record["filename"] = "other.jpg"
        self.save_sources()
        self.blocked("handoff", "no exact filename record")

    def test_unknown_manual_licenses_missing_urls_and_unapproved_use_block(self):
        self.accepted()
        valid = copy.deepcopy(self.record)
        changes = [("license_name", "manual-unverified"), ("license_tier", "unknown"),
                   ("source_page_url", ""), ("license_url", "file:///license"), ("status", "manual")]
        for key, value in changes:
            with self.subTest(key=key):
                self.record = dict(valid, **{key: value})
                self.save_sources()
                self.blocked("handoff")
        self.record = valid
        self.save_sources()
        self.handoff["provenance_review"]["decision"] = "manual-unverified"
        self.blocked("handoff", "not approved")

    def test_changed_provenance_or_license_evidence_invalidates_decision(self):
        self.accepted()
        self.record["license_name"] = "Updated terms"
        self.save_sources()
        self.blocked("handoff", "stale against image_sources.json")
        self.handoff["provenance_review"]["source_record_sha256"] = review.json_digest(self.record)
        Path(self.license["path"]).write_bytes(b"changed terms evidence")
        self.blocked("handoff", "hash mismatch")

    def test_attribution_required_needs_consistent_flag_and_canonical_credit(self):
        self.accepted()
        self.record.update(license_tier="attribution-required", attribution_required=True, attribution_text="")
        self.save_sources()
        self.blocked("handoff", "attribution_text")

    def test_final_requires_current_render_and_native_picture_attestation(self):
        self.final()
        self.assertEqual(self.check("final")["status"], "PASS")
        final = self.slot["final_review"]
        final["native_picture_editable"] = False
        self.blocked("final", "attestation missing")
        final["native_picture_editable"] = True
        final["deck_sha256"] = "0" * 64
        self.blocked("final", "deck_sha256 is stale")

    def test_final_deck_changes_and_actual_canvas_mismatch_block(self):
        self.final()
        path = Path(self.data["deck"]["path"])
        with ZipFile(path, "a") as archive:
            archive.writestr("changed.txt", "deck revision")
        self.blocked("final", "hash mismatch")
        self.data["deck"]["sha256"] = review.file_digest(path)
        self.slot["final_review"]["deck_sha256"] = self.data["deck"]["sha256"]
        with ZipFile(path, "w") as archive:
            archive.writestr("ppt/presentation.xml", '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldSz cx="9144000" cy="5143500"/></p:presentation>')
        self.data["deck"]["sha256"] = review.file_digest(path)
        self.blocked("final", "actual PPTX canvas")

    def test_final_missing_render_or_open_crop_defect_blocks(self):
        self.final()
        self.slot["final_review"]["screenshot"] = {"path": "missing.png", "sha256": "0" * 64}
        self.blocked("final", "file missing")
        self.slot["final_review"]["screenshot"] = self.visual
        self.slot["rendering_defects"] = [{"event_id": "open-crop", "reviewer": "main", "status": "open",
                                          "reason": "Correct asset but crop cuts subject", "visual_evidence": [self.visual]}]
        self.blocked("final", "unresolved rendering defect")

    def test_final_assigned_slide_must_exist_in_actual_deck(self):
        self.final()
        self.slot["slide_number"] = 4
        self.handoff["slide_number"] = 4
        self.slot["rounds"][-1]["slide_number"] = 4
        binding = review.placement_digest(self.data, self.slot, self.handoff)
        self.slot["rounds"][-1]["placement_sha256"] = binding
        self.slot["final_review"].update(slide_number=4, placement_sha256=binding)
        self.blocked("final", "slide does not exist")

    def test_schema_boolean_and_nonfinite_canvas_cannot_pass(self):
        self.data["schema_version"] = True
        self.blocked(contains="integer 2")
        self.data["schema_version"] = 2
        self.data["canvas_inches"]["width"] = float("nan")
        self.blocked(contains="finite positive")

    def test_malformed_empty_and_missing_manifest_emit_json_blocked_without_traceback(self):
        for content in ("", "{", "null", "[]", "{}", '{"schema_version":2,"deck_id":"deck","canvas_inches":{"width":12,"height":6},"slots":[null]}'):
            with self.subTest(content=content):
                self.path.write_text(content, encoding="utf-8")
                result = subprocess.run([sys.executable, "-B", review.__file__, str(self.path), "--stage", "handoff"],
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(json.loads(result.stdout)["status"], "BLOCKED")
                self.assertNotIn("Traceback", result.stderr)
        self.path.unlink()
        self.assertEqual(review.validate(self.path)["status"], "BLOCKED")

    def test_each_image_fit_failure_or_missing_finding_blocks_acceptance(self):
        accepted = self.accepted()
        baseline = copy.deepcopy(accepted["fit_review"])
        for criterion in ("tone", "content", "purpose"):
            for replacement in ({"verdict": "reject", "reason": "Mismatch"},
                                {"verdict": "pass", "reason": ""}, None):
                accepted["fit_review"] = copy.deepcopy(baseline)
                accepted["fit_review"][criterion] = replacement
                self.blocked("handoff", criterion)
        accepted["fit_review"] = baseline
        self.assertEqual(self.check("handoff")["status"], "PASS")

    def test_changed_deck_purpose_or_tone_invalidates_previous_acceptance(self):
        self.accepted()
        for field in ("deck_purpose", "visual_tone"):
            original = self.data[field]
            self.data[field] = "Different current direction"
            self.blocked("handoff", "binding is stale")
            self.data[field] = original

    def test_same_image_can_pass_a_fresh_different_context(self):
        accepted = self.accepted()
        original_asset = copy.deepcopy(self.handoff["asset"])
        self.data["deck_id"] = "different-deck"
        self.data["deck_purpose"] = "Teach sensor maintenance"
        self.data["visual_tone"] = "Practical instructional documentary"
        self.slot["message"] = "Explain safe access to the sensor"
        self.handoff["placement_inches"]["x"] = 1
        accepted["reason"] = "MAIN viewed reused image and current context"
        accepted["placement_sha256"] = review.placement_digest(self.data, self.slot, self.handoff)
        self.assertEqual(self.handoff["asset"], original_asset)
        self.assertEqual(self.check("handoff")["status"], "PASS")

    def test_legacy_approval_cannot_silently_skip_new_fitness_checks(self):
        self.accepted()
        self.data["schema_version"] = 1
        self.blocked("handoff", "fresh Main")

    def test_validator_does_not_write_artifacts(self):
        self.final()
        self.path.write_text(json.dumps(self.data), encoding="utf-8")
        before = {str(path): review.file_digest(path) for path in self.base.parent.rglob("*") if path.is_file()}
        self.assertEqual(review.validate(self.path, "final")["status"], "PASS")
        after = {str(path): review.file_digest(path) for path in self.base.parent.rglob("*") if path.is_file()}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main(verbosity=2)
