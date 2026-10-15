"""Offline failure/recovery tests; never connect to the owner's Supabase project."""
import copy
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import uuid

import design_brain_memory_adapter as module


class Server:
    def __init__(self):
        self.records, self.receipts = {}, {}
        self.online, self.lose_response, self.denied = True, False, False
        self.put_count = 0

    def call(self, method, request):
        if not self.online:
            raise module.RemoteError("TRANSPORT_UNAVAILABLE", method == "put")
        if self.denied:
            raise module.RemoteError("MEMORY_ACCESS_DENIED")
        namespace = request["p_namespace"]
        if method == "operation":
            return copy.deepcopy(self.receipts.get((namespace, request["p_operation_id"]), {"status": "NOT_FOUND"}))
        if method == "get":
            rows = self.records.get((namespace, request["p_id"]), [])
            revision = request.get("p_revision")
            row = next((r for r in rows if r["revision"] == revision), None) if revision else rows[-1] if rows else None
            return {"status": "READ" if row else "NOT_FOUND", "record": copy.deepcopy(row)}
        if method == "query":
            rows = [copy.deepcopy(row) for (ns, rid), history in sorted(self.records.items()) if ns == namespace
                    for row in (history if request.get("p_history_id") == rid else history[-1:] if not request.get("p_history_id") else [])]
            query, kind = request.get("p_query"), request.get("p_kind")
            rows = [row for row in rows if (not query or query.lower() in row["payload_text"].lower())
                    and (not kind or json.loads(row["payload_text"])["kind"] == kind)]
            offset, limit = request.get("p_offset", 0), request.get("p_limit", 20)
            return {"status": "FOUND", "records": rows[offset:offset+limit], "total": len(rows),
                    "offset": offset, "limit": limit, "next_offset": offset+limit if offset+limit < len(rows) else None}
        if method == "put":
            self.put_count += 1
            op = (namespace, request["p_operation_id"])
            payload = request["p_payload_text"]
            expected = request["p_expected_revision"]
            if op in self.receipts:
                receipt = self.receipts[op]
                if receipt["expected_revision"] != expected or receipt["payload_sha256"] != module.digest(payload):
                    raise module.RemoteError("MEMORY_OPERATION_CONFLICT")
                return copy.deepcopy(receipt)
            value = json.loads(payload)
            rows = self.records.setdefault((namespace, value["id"]), [])
            if expected != len(rows):
                raise module.RemoteError("MEMORY_REVISION_CONFLICT")
            row = {"namespace": namespace, "id": value["id"], "revision": expected+1,
                   "payload_text": payload, "payload_sha256": module.digest(payload), "operation_id": op[1], "created_at": module.now()}
            rows.append(row)
            receipt = {"status": "STORED", "namespace": namespace, "operation_id": op[1],
                       "expected_revision": expected, "payload_sha256": row["payload_sha256"], "record": row}
            self.receipts[op] = receipt
            if self.lose_response:
                self.lose_response = False
                raise module.RemoteError("TRANSPORT_UNAVAILABLE", True)
            return copy.deepcopy(receipt)
        raise AssertionError(method)


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="codex-memory-adapter-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.server = Server()
        self.main = module.Adapter(self.root, "main", self.server.call, {})
        self.reader = module.Adapter(self.root, "engineer", self.server.call, {})
        self.record = {"id": "layout-case", "kind": "layout_case", "title": "Layout judgment",
                       "content": "Rejected repeated composition; preserve reason.", "tags": ["layout"],
                       "review_status": "rejected", "evidence": []}

    def save(self, record=None, revision=0, operation=None):
        return self.main.put(record or self.record, revision, operation or str(uuid.uuid4()))

    def test_create_read_revise_keeps_positive_and_negative_history(self):
        first = self.save()
        self.assertEqual(first["status"], "CONFIRMED")
        revised = dict(self.record, content="Composition repaired; pending actual render review.", review_status="proposal")
        self.save(revised, 1)
        history = self.reader.search(history_id="layout-case")["remote"]["records"]
        self.assertEqual([r["review_status"] for r in history], ["rejected", "proposal"])

    def test_reader_cannot_write_or_create_local_store(self):
        self.reader.status(); self.reader.search("layout"); self.reader.read("layout-case")
        self.assertFalse((self.root/module.DATABASE).exists())
        for action in (lambda: self.reader.put(self.record, 0, str(uuid.uuid4())), self.reader.pull,
                       lambda: self.reader.sync(str(uuid.uuid4()))):
            with self.assertRaises(ValueError): action()

    def test_reader_loads_only_separate_reader_credential(self):
        path = self.root/module.SECRETS["engineer"]
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"read_token": "reader-dummy", "publishable_key": "public-dummy"}))
        writer = self.root/module.SECRETS["main"]
        writer.write_text("malformed writer file must not affect Engineer")
        reader = module.Adapter(self.root, "engineer", environment={})
        self.assertEqual(reader.token, "reader-dummy")
        self.assertIsNone(reader.configuration_error)

    def test_timeout_after_commit_reconciles_receipt_without_second_put(self):
        self.server.lose_response = True
        result = self.save()
        self.assertEqual(result["status"], "UNKNOWN_LOCAL_SAVED")
        self.assertEqual(self.server.put_count, 1)
        replay = self.main.sync(result["operation_id"])
        self.assertEqual(replay["status"], "CONFIRMED")
        self.assertEqual(self.server.put_count, 1)
        self.assertEqual(len(self.server.records[("codex-design", "layout-case")]), 1)

    def test_offline_request_remains_readable_then_syncs_same_operation(self):
        self.server.online = False
        result = self.save()
        self.assertEqual(result["status"], "UNKNOWN_LOCAL_SAVED")
        local = self.reader.search("rejected")["local"]["records"]
        self.assertEqual(local[0]["review_status"], "rejected")
        self.server.online = True
        self.assertEqual(self.main.sync(result["operation_id"])["status"], "CONFIRMED")
        self.assertEqual(self.main.operation(result["operation_id"])["state"], "CONFIRMED")

    def test_stale_offline_draft_conflicts_and_remains_visible_after_recovery(self):
        self.save()
        self.server.online = False
        result = self.save(dict(self.record, content="Offline revision"), 1)
        self.server.online = True
        payload = module.local.canonical(dict(self.record, content="Another device revision"))
        self.server.call("put", {"p_namespace": "codex-design", "p_payload_text": payload,
                                "p_expected_revision": 1, "p_operation_id": str(uuid.uuid4())})
        self.assertEqual(self.main.sync(result["operation_id"])["status"], "CONFLICT_LOCAL_SAVED")
        candidates = self.reader.read("layout-case")["records"]
        self.assertEqual({r["origin"] for r in candidates}, {"supabase", "local-outbox"})
        self.assertTrue(any(r["sync_state"] == "CONFLICT" for r in candidates))
        count = self.server.put_count
        self.main.sync(result["operation_id"])
        self.assertEqual(self.server.put_count, count)

    def test_immutable_operation_blocks_reuse_for_different_payload(self):
        op = str(uuid.uuid4()); self.save(operation=op)
        with self.assertRaises(ValueError): self.save(dict(self.record, content="Changed"), operation=op)
        with closing(sqlite3.connect(self.main.path)) as db, db:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("UPDATE operations SET payload_text='changed'")

    def test_accepted_record_requires_current_evidence_and_drift_is_visible(self):
        accepted = dict(self.record, review_status="accepted")
        with self.assertRaises(ValueError): self.save(accepted)
        source = self.root/"review.md"; source.write_text("verified")
        accepted["evidence"] = [{"path": "review.md", "sha256": module.local.file_digest(source)}]
        self.save(accepted)
        source.write_text("changed")
        self.assertEqual(self.reader.read("layout-case")["records"][0]["evidence_status"], "UNVERIFIED")

    def test_cache_is_preserved_and_reader_bytes_unchanged(self):
        self.save(); self.main.pull()
        before = self.main.path.read_bytes()
        self.server.online = False
        self.assertEqual(self.reader.read("layout-case")["records"][0]["origin"], "supabase-cache")
        self.reader.search(); self.reader.status()
        self.assertEqual(before, self.main.path.read_bytes())

    def test_legacy_local_memory_is_not_hidden_after_cloud_returns(self):
        module.local.init(self.root, "main")
        module.local.put(self.root, self.record, 0, "main")
        self.assertEqual(self.reader.search("layout")["local"]["records"][0]["origin"], "local-legacy")

    def test_key_failure_saved_locally_and_status_never_exposes_credentials(self):
        self.server.denied = True
        result = self.save()
        self.assertEqual(result["remote_error"], "MEMORY_ACCESS_DENIED")
        self.assertNotEqual(result["status"], "CONFIRMED")
        adapter = module.Adapter(self.root, "engineer", environment={"CODEX_DESIGN_SUPABASE_URL": "https://example.supabase.co", "CODEX_DESIGN_MEMORY_READ_TOKEN": "DO-NOT-PRINT"})
        self.assertNotIn("DO-NOT-PRINT", json.dumps(adapter.status()))

    def test_bad_receipt_never_confirms_and_corrupt_cache_never_supplies_content(self):
        original = self.main.confirm
        def bad(request, response):
            response["expected_revision"] = 44
            return original(request, response)
        self.main.confirm = bad
        with self.assertRaises(ValueError): self.save()
        self.assertEqual(self.main.status()["operations"], {"UNKNOWN": 1})
        self.main.confirm = original
        request = self.main.local_records()[0]
        self.main.sync(request["operation_id"])
        with closing(sqlite3.connect(self.main.path)) as db, db: db.execute("UPDATE cache SET payload_sha256='wrong'")
        self.server.online = False
        result = self.reader.read("layout-case")
        self.assertEqual(result["local_error"], "LOCAL_DATA_UNVERIFIED")
        self.assertEqual(result["records"], [])

    def test_broken_cloud_config_preserves_local_access_and_corrupt_local_preserves_cloud_read(self):
        self.save()
        broken = module.Adapter(self.root, "engineer", environment={"CODEX_DESIGN_SUPABASE_URL": "http://invalid"})
        result = broken.read("layout-case")
        self.assertEqual(result["remote_error"], "HTTPS_ORIGIN_INVALID")
        self.assertEqual(result["records"][0]["origin"], "supabase-cache")
        self.main.path.write_bytes(b"corrupt local database")
        result = self.reader.read("layout-case")
        self.assertEqual(result["records"][0]["origin"], "supabase")
        self.assertEqual(result["local_error"], "LOCAL_DATA_UNVERIFIED")

    def test_namespace_and_database_survive_plugin_root_relocation(self):
        self.save()
        relocated = self.root/"relocated"; relocated.mkdir()
        import shutil
        target = relocated/module.DATABASE; target.parent.mkdir(parents=True)
        shutil.copy2(self.main.path, target)
        self.server.online = False
        moved = module.Adapter(relocated, "engineer", self.server.call, {})
        self.assertEqual(moved.read("layout-case")["records"][0]["id"], "layout-case")

    def test_offline_exact_revision_never_substitutes_latest_or_pending(self):
        self.save()
        self.save(dict(self.record, content="Revised later"), 1)
        self.server.online = False
        self.save(dict(self.record, content="Offline pending"), 2)
        old = self.reader.read("layout-case", 1)["records"]
        self.assertEqual(len(old), 1)
        self.assertEqual(old[0]["content"], self.record["content"])
        self.assertEqual(old[0]["revision"], 1)
        self.assertEqual(self.reader.read("layout-case", 999)["records"], [])

    def test_malformed_operation_lookup_never_replays_uncertain_write(self):
        self.server.lose_response = True
        saved = self.save()
        original = self.server.call
        for response in ({}, {"status": "UNKNOWN"}, {"status": "NOT_FOUND", "record": {}}):
            self.main.transport = lambda method, args: response if method == "operation" else original(method, args)
            result = self.main.sync(saved["operation_id"])
            self.assertEqual(result["status"], "UNKNOWN_LOCAL_SAVED")
            self.assertEqual(self.server.put_count, 1)

    def test_receipt_metadata_cannot_forge_confirmation(self):
        self.server.lose_response = True
        saved = self.save()
        request = self.main.operation(saved["operation_id"])
        receipt = self.server.receipts[("codex-design", saved["operation_id"])]
        changes = [("status", "NOT_FOUND"), ("payload_sha256", "0"*64), ("expected_revision", False),
                   ("record.namespace", "other"), ("record.id", "other"), ("record.revision", -99),
                   ("record.revision", True), ("record.operation_id", str(uuid.uuid4()))]
        for field, value in changes:
            bad = copy.deepcopy(receipt)
            if field.startswith("record."): bad["record"][field.split(".")[1]] = value
            else: bad[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.main.confirm(request, bad)
            self.assertEqual(self.main.operation(saved["operation_id"])["state"], "UNKNOWN")
        self.assertEqual(self.main.sync(saved["operation_id"])["status"], "CONFIRMED")

    def test_delayed_accepted_write_rechecks_evidence_before_dispatch(self):
        source = self.root/"review.md"; source.write_text("verified")
        accepted = dict(self.record, review_status="accepted", evidence=[{"path": "review.md", "sha256": module.local.file_digest(source)}])
        self.server.online = False
        saved = self.save(accepted)
        source.write_text("changed"); self.server.online = True
        self.assertEqual(self.main.sync(saved["operation_id"])["status"], "UNVERIFIED_LOCAL_SAVED")
        self.assertEqual(self.server.put_count, 0)

    def test_committed_historical_receipt_reconciles_after_evidence_drift(self):
        source = self.root/"review.md"; source.write_text("verified")
        accepted = dict(self.record, review_status="accepted", evidence=[{"path": "review.md", "sha256": module.local.file_digest(source)}])
        self.server.lose_response = True
        saved = self.save(accepted)
        source.write_text("changed")
        result = self.main.sync(saved["operation_id"])
        self.assertEqual(result["status"], "CONFIRMED")
        self.assertEqual(result["record"]["evidence_status"], "UNVERIFIED")
        self.assertEqual(self.server.put_count, 1)

    def test_legacy_history_preserves_earlier_negative_revision(self):
        module.local.init(self.root, "main")
        module.local.put(self.root, self.record, 0, "main")
        module.local.put(self.root, dict(self.record, review_status="proposal"), 1, "main")
        rows = self.reader.search(history_id=self.record["id"])["local"]["records"]
        self.assertEqual({(r["revision"], r["review_status"]) for r in rows}, {(1, "rejected"), (2, "proposal")})


if __name__ == "__main__":
    unittest.main(verbosity=2)
