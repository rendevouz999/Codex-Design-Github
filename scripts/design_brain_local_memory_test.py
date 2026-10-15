"""Offline regression scenarios; all memory stores/evidence live in temp roots."""
from __future__ import annotations

import copy
from contextlib import closing
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest

sys.dont_write_bytecode = True
import design_brain_local_memory as memory


class LocalMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="design-local-memory-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.evidence = self.root / "reports/evidence.txt"
        self.evidence.parent.mkdir()
        self.evidence.write_text("Synthetic verified artifact evidence", encoding="utf-8")
        self.record = {"id": "layout.original", "kind": "layout_case", "title": "Painting conservation composition",
                       "content": "Native picture and text regions. MAIN must inspect actual paired slide renders.",
                       "tags": ["pptx", "painting"], "review_status": "proposal",
                       "evidence": [{"path": "reports/evidence.txt", "sha256": memory.file_digest(self.evidence)}],
                       "provenance": {"source": "synthetic test fixture"}}

    def initialize(self):
        return memory.init(self.root, "main")

    def put(self, value=None, revision=0, actor="main"):
        return memory.put(self.root, value or self.record, revision, actor)

    def cli(self, *args, root=None):
        result = subprocess.run([sys.executable, "-B", memory.__file__, "--root", str(root or self.root), *map(str, args)],
                                capture_output=True, text=True, timeout=10)
        self.assertNotIn("Traceback", result.stderr)
        return result.returncode, json.loads(result.stdout)

    def test_missing_store_read_operations_create_nothing(self):
        before = {str(path.relative_to(self.root)) for path in self.root.rglob("*")}
        for args in (("status",), ("read", "absent"), ("search", "painting"), ("list",), ("history", "absent"), ("verify", "absent")):
            with self.subTest(args=args):
                code, value = self.cli(*args)
                self.assertEqual((code, value["status"]), (2, "NO_STORE"))
        after = {str(path.relative_to(self.root)) for path in self.root.rglob("*")}
        self.assertEqual(before, after)
        self.assertFalse((self.root / memory.STORE).exists())

    def test_init_is_main_only_and_existing_store_is_preserved(self):
        with self.assertRaisesRegex(ValueError, "actor main"):
            memory.init(self.root, "engineer")
        self.assertFalse((self.root / memory.STORE).exists())
        self.assertEqual(self.initialize()["status"], "INITIALIZED")
        self.put()
        before = memory.file_digest(self.root / memory.STORE)
        self.assertEqual(self.initialize()["status"], "EXISTS")
        self.assertEqual(memory.file_digest(self.root / memory.STORE), before)

    def test_offline_search_kind_filters_and_pagination_do_not_claim_full_history(self):
        self.initialize()
        self.put()
        policy = dict(self.record, id="policy.images", kind="policy", title="Current painting image policy")
        self.put(policy)
        second = dict(self.record, id="layout.second", title="Another native layout")
        self.put(second)
        result = memory.browse(self.root, "search", "painting", kinds=["layout_case"], limit=1)
        self.assertEqual(result["records"][0]["id"], "layout.original")
        self.assertEqual((result["total"], result["next_offset"]), (2, 1))
        self.assertIn("not complete layout history", result["coverage"])
        full_list = memory.browse(self.root, kinds=["layout_case"], limit=1, offset=1)
        self.assertEqual(full_list["records"][0]["id"], "layout.second")
        self.assertIsNone(full_list["next_offset"])
        self.assertEqual(memory.browse(self.root, "search", "unmatched") ["status"], "NOT_FOUND")

    def test_updates_preserve_history_idempotency_and_stale_expected_revision(self):
        self.initialize()
        self.assertEqual(self.put()["revision"], 1)
        changed = dict(self.record, content="Revised structural finding with preserved history.", review_status="accepted")
        self.assertEqual(self.put(changed, 1)["revision"], 2)
        self.assertEqual(self.put(changed, 2)["status"], "UNCHANGED")
        with self.assertRaisesRegex(ValueError, "STALE_REVISION"):
            self.put(changed, 1)
        with self.assertRaisesRegex(ValueError, "STALE_REVISION"):
            self.put(self.record, 0)
        history = memory.browse(self.root, "history", record_id=self.record["id"])
        self.assertEqual([row["revision"] for row in history["records"]], [2, 1])
        self.assertEqual(memory.read(self.root, self.record["id"], 1)["record"]["content"], self.record["content"])
        self.assertEqual(memory.status(self.root)["revisions"], 2)

    def test_sqlite_history_is_immutable(self):
        self.initialize()
        self.put()
        with closing(sqlite3.connect(self.root / memory.STORE)) as db, db:
            for command in ("UPDATE revisions SET payload='{}'", "DELETE FROM revisions"):
                with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable"):
                    db.execute(command)
        self.assertEqual(memory.read(self.root, self.record["id"])["record"]["revision"], 1)

    def test_engineer_write_rejected_and_put_does_not_auto_initialize(self):
        with self.assertRaisesRegex(ValueError, "NO_STORE"):
            self.put()
        self.assertFalse((self.root / memory.STORE).exists())
        self.initialize()
        with self.assertRaisesRegex(ValueError, "actor main"):
            self.put(actor="engineer")
        self.assertEqual(memory.status(self.root)["records"], 0)

    def test_evidence_drift_never_silently_grants_approval_or_rewrites_history(self):
        self.initialize()
        accepted = dict(self.record, review_status="accepted")
        self.put(accepted)
        self.evidence.write_text("Changed artifact bytes", encoding="utf-8")
        result = memory.read(self.root, accepted["id"], verify=True)
        self.assertEqual(result["status"], "UNVERIFIED")
        self.assertEqual(result["record"]["review_status"], "accepted")
        self.assertEqual(result["record"]["creative_approval"], "NOT_INFERRED")
        self.assertIn("stale evidence hash", result["record"]["evidence_errors"][0])
        with self.assertRaisesRegex(ValueError, "current non-empty evidence"):
            self.put(accepted, 1)
        self.assertEqual(memory.status(self.root)["revisions"], 1)

    def test_missing_evidence_and_distinct_proposal_accepted_statuses(self):
        self.initialize()
        proposal = dict(self.record, evidence=[])
        value = self.put(proposal)
        self.assertEqual((value["review_status"], value["evidence_status"]), ("proposal", "UNVERIFIED"))
        accepted = dict(proposal, review_status="accepted")
        with self.assertRaisesRegex(ValueError, "current non-empty evidence"):
            self.put(accepted, 1)
        missing = dict(self.record, id="progress.missing", review_status="unverified",
                       evidence=[{"path": "missing.txt", "sha256": "0" * 64}])
        self.assertEqual(self.put(missing)["evidence_status"], "UNVERIFIED")
        self.assertEqual(memory.read(self.root, missing["id"])["record"]["review_status"], "unverified")

    def test_malformed_data_paths_hashes_and_bounds_do_not_write(self):
        self.initialize()
        bad_records = [None, [], {}, dict(self.record, title=""), dict(self.record, content="x" * 12001),
                       dict(self.record, id="../escape"), dict(self.record, review_status="PASS"),
                       dict(self.record, tags=["repeat", "repeat"]), dict(self.record, password="not permitted"),
                       dict(self.record, evidence=[{"path": "", "sha256": "0" * 64}]),
                       dict(self.record, evidence=[{"path": "reports/evidence.txt", "sha256": "bad"}]),
                       dict(self.record, evidence=[{"path": "../outside.txt", "sha256": "0" * 64}]),
                       dict(self.record, evidence=[{"path": "https://example.com/file", "sha256": "0" * 64}])]
        payload = self.root / "record.json"
        for bad in bad_records:
            with self.subTest(bad_type=type(bad).__name__):
                payload.write_text(json.dumps(bad), encoding="utf-8")
                code, result = self.cli("put", "--actor", "main", "--file", payload, "--expected-revision", "0")
                self.assertEqual((code, result["status"]), (1, "BLOCKED"))
        self.assertEqual(memory.status(self.root)["records"], 0)

    def test_missing_corrupt_or_unrelated_store_fails_without_reset(self):
        store = self.root / memory.STORE
        store.parent.mkdir(parents=True)
        store.write_bytes(b"not a SQLite database")
        before = store.read_bytes()
        for command in (("status",), ("init", "--actor", "main"), ("list",)):
            code, result = self.cli(*command)
            self.assertEqual((code, result["status"]), (1, "BLOCKED"))
            self.assertEqual(store.read_bytes(), before)
        store.unlink()
        with closing(sqlite3.connect(store)) as db, db:
            db.execute("CREATE TABLE unrelated(value TEXT)")
        before = memory.file_digest(store)
        code, result = self.cli("init", "--actor", "main")
        self.assertEqual((code, result["status"]), (1, "BLOCKED"))
        self.assertEqual(memory.file_digest(store), before)

    def test_read_commands_leave_database_bytes_and_record_files_unchanged(self):
        self.initialize()
        self.put()
        before = {str(path): memory.file_digest(path) for path in self.root.rglob("*") if path.is_file()}
        for args in (("status",), ("read", self.record["id"]), ("search", "painting"), ("list",), ("history", self.record["id"]), ("verify", self.record["id"])):
            self.cli(*args)
        after = {str(path): memory.file_digest(path) for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_valid_json_with_corrupt_payload_types_or_hashes_is_blocked(self):
        self.initialize()
        self.put()
        corrupt = dict(self.record, id="corrupt.row", title=[])
        encoded = memory.canonical(corrupt)
        with closing(sqlite3.connect(self.root / memory.STORE)) as db, db:
            db.execute("INSERT INTO revisions VALUES (?,?,?,?,?,?)", (corrupt["id"], 1, encoded, memory.digest_text(encoded), "test-time", "main"))
        for args in (("search", "painting"), ("list",), ("read", corrupt["id"]), ("history", corrupt["id"])):
            code, result = self.cli(*args)
            self.assertEqual((code, result["status"]), (1, "BLOCKED"))
        with self.assertRaisesRegex(ValueError, "title must"):
            self.put(dict(self.record, id=corrupt["id"]), 1)
        # A structurally valid payload with a mismatched digest must also fail.
        altered = dict(self.record, id="hash.corrupt")
        with closing(sqlite3.connect(self.root / memory.STORE)) as db, db:
            db.execute("INSERT INTO revisions VALUES (?,?,?,?,?,?)", (altered["id"], 1, memory.canonical(altered), "0" * 64, "test-time", "main"))
        code, result = self.cli("read", altered["id"])
        self.assertEqual((code, result["status"]), (1, "BLOCKED"))
        self.assertIn("integrity mismatch", result["errors"][0])

    def test_relative_evidence_survives_root_relocation(self):
        self.initialize()
        self.put()
        with tempfile.TemporaryDirectory(prefix="design-memory-relocated-") as destination:
            moved = Path(destination) / "plugin"
            shutil.copytree(self.root, moved)
            result = memory.read(moved, self.record["id"], verify=True)
            self.assertEqual(result["status"], "EVIDENCE_CURRENT")
            self.assertEqual(result["record"]["evidence"][0]["path"], "reports/evidence.txt")

    def test_more_than_5000_records_and_revisions_keep_filtered_pages_search_and_history_usable(self):
        self.initialize()
        self.put()
        fixtures = []
        for index in range(5001):
            payload = dict(self.record, id=f"policy.{index:05d}", kind="policy", title="Bulk unrelated workflow note")
            encoded = memory.canonical(payload)
            fixtures.append((payload["id"], 1, encoded, memory.digest_text(encoded), "fixture-time", "main"))
        for revision in range(2, 5003):
            payload = dict(self.record, title=f"Painting conservation composition revision {revision}")
            encoded = memory.canonical(payload)
            fixtures.append((payload["id"], revision, encoded, memory.digest_text(encoded), "fixture-time", "main"))
        with closing(sqlite3.connect(self.root / memory.STORE)) as db, db:
            db.executemany("INSERT INTO revisions VALUES (?,?,?,?,?,?)", fixtures)
        listing = memory.browse(self.root, kinds=["layout_case"], limit=1)
        self.assertEqual((listing["total"], listing["records"][0]["revision"]), (1, 5002))
        search = memory.browse(self.root, "search", "conservation", kinds=["layout_case"], limit=1)
        self.assertEqual((search["total"], search["records"][0]["id"]), (1, self.record["id"]))
        history = memory.browse(self.root, "history", record_id=self.record["id"], offset=5000, limit=2)
        self.assertEqual(history["total"], 5002)
        self.assertEqual([row["revision"] for row in history["records"]], [2, 1])
        self.assertIsNone(history["next_offset"])
        self.assertEqual(memory.browse(self.root, offset=5000, limit=2)["total"], 5002)

    def test_concurrent_writers_with_same_expected_revision_cannot_lose_updates(self):
        self.initialize()
        self.put()
        files = []
        for name in ("A", "B"):
            path = self.root / f"update-{name}.json"
            path.write_text(json.dumps(dict(self.record, title=f"Concurrent update {name}")), encoding="utf-8")
            files.append(path)
        lock = sqlite3.connect(self.root / memory.STORE, timeout=3)
        processes = []
        try:
            lock.execute("BEGIN IMMEDIATE")
            for path in files:
                processes.append(subprocess.Popen([sys.executable, "-B", memory.__file__, "--root", str(self.root),
                                                   "put", "--actor", "main", "--file", str(path), "--expected-revision", "1"],
                                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
            time.sleep(0.15)
            self.assertTrue(all(process.poll() is None for process in processes), "both writers should be queued behind the native SQLite write lock")
            lock.commit()
            results = []
            for process in processes:
                stdout, stderr = process.communicate(timeout=10)
                self.assertNotIn("Traceback", stderr)
                results.append(json.loads(stdout))
            self.assertEqual(sorted(result["status"] for result in results), ["BLOCKED", "STORED"])
            loser = next(result for result in results if result["status"] == "BLOCKED")
            self.assertIn("STALE_REVISION", loser["errors"][0])
            self.assertEqual(memory.status(self.root)["revisions"], 2)
            self.assertIn(memory.read(self.root, self.record["id"])["record"]["title"], ("Concurrent update A", "Concurrent update B"))
        finally:
            lock.close()
            for process in processes:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
