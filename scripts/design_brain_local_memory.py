#!/usr/bin/env python3
"""Plugin-local shared workflow memory, stdlib SQLite; no network or auto-ingest.

MAIN writes explicitly with --actor main. This convention is not authentication.
Engineer reads/searches. Read commands never create a missing store. Contents are
bounded authored workflow notes, not a place for credentials or user transcripts.
Stored review_status is a human decision; evidence currency never implies a
creative PASS. Relative evidence paths resolve from the selected plugin root.
"""
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import heapq
import json
from pathlib import Path
import re
import sqlite3
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
STORE = Path(".design-brain/local-memory/memory.sqlite3")
STATUSES = {"unverified", "proposal", "accepted", "rejected", "blocked"}
FIELDS = {"id", "kind", "title", "content", "tags", "review_status", "evidence", "provenance"}
SLUG = re.compile(r"[a-z0-9][a-z0-9._:-]{0,127}")
SCHEMA = """
CREATE TABLE IF NOT EXISTS revisions (
 id TEXT NOT NULL, revision INTEGER NOT NULL CHECK(revision > 0),
 payload TEXT NOT NULL, payload_sha256 TEXT NOT NULL,
 created_at TEXT NOT NULL, actor TEXT NOT NULL CHECK(actor = 'main'),
 PRIMARY KEY(id, revision)
);
CREATE TRIGGER IF NOT EXISTS revisions_no_update BEFORE UPDATE ON revisions
 BEGIN SELECT RAISE(ABORT, 'revision history is immutable'); END;
CREATE TRIGGER IF NOT EXISTS revisions_no_delete BEFORE DELETE ON revisions
 BEGIN SELECT RAISE(ABORT, 'revision history is immutable'); END;
"""


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_digest(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def bounded_text(value, label, maximum):
    need(isinstance(value, str) and bool(value.strip()) and len(value) <= maximum,
         f"{label} must be non-empty text, at most {maximum} characters")
    return value


def store_path(root):
    root = Path(root).resolve()
    need(root.is_dir() and not str(root).startswith("\\\\"), "root must be an existing local directory")
    path = (root / STORE).resolve()
    need(path.is_relative_to(root), "store path escapes root through a symlink/junction")
    return root, path


def evidence_path(root, value):
    bounded_text(value, "evidence.path", 2048)
    path = Path(value)
    need(not str(path).startswith("\\\\") and "://" not in value, "evidence must reference a local file, not a network URL/path")
    if not path.is_absolute():
        path = (root / path).resolve()
        need(path.is_relative_to(root), "relative evidence path escapes root")
    return path


def validate_payload(value, root):
    need(isinstance(value, dict), "record must be a JSON object")
    need(not (set(value) - FIELDS), "record has unsupported fields; supply bounded workflow notes only")
    for field in ("id", "kind"):
        need(isinstance(value.get(field), str) and bool(SLUG.fullmatch(value[field])), f"{field} must be a stable lowercase identifier")
    bounded_text(value.get("title"), "title", 200)
    bounded_text(value.get("content"), "content", 12000)
    need(value.get("review_status") in STATUSES, "invalid review_status")
    tags = value.get("tags")
    need(isinstance(tags, list) and len(tags) <= 32, "tags must be an array with at most 32 items")
    for tag in tags:
        bounded_text(tag, "tag", 64)
    need(len(set(tags)) == len(tags), "duplicate tags")
    evidence = value.get("evidence")
    need(isinstance(evidence, list) and len(evidence) <= 32, "evidence must be an array with at most 32 file references")
    paths = set()
    for item in evidence:
        need(isinstance(item, dict) and set(item) == {"path", "sha256"}, "evidence must contain exactly path and sha256")
        path = evidence_path(root, item.get("path"))
        need(isinstance(item.get("sha256"), str) and bool(re.fullmatch(r"[0-9a-f]{64}", item["sha256"])), "evidence.sha256 must be lowercase SHA-256")
        need(str(path) not in paths, "duplicate evidence path")
        paths.add(str(path))
    if "provenance" in value:
        need(isinstance(value["provenance"], dict) and len(canonical(value["provenance"])) <= 4096, "provenance must be a bounded object")
    need(len(canonical(value)) <= 64000, "record exceeds size limit")
    return value


def evidence_state(root, payload):
    errors = []
    for item in payload["evidence"]:
        path = evidence_path(root, item["path"])
        try:
            if not path.is_file():
                errors.append(f"missing evidence: {item['path']}")
            elif file_digest(path) != item["sha256"]:
                errors.append(f"stale evidence hash: {item['path']}")
        except OSError as exc:
            errors.append(f"unreadable evidence: {item['path']}: {exc}")
    if not payload["evidence"]:
        errors.append("no evidence supplied; decision remains unverified")
    return {"evidence_status": "UNVERIFIED" if errors else "CURRENT", "evidence_errors": errors,
            "creative_approval": "NOT_INFERRED"}


def connect(path, writable=False):
    need(path.is_file(), "NO_STORE: Main must run init explicitly")
    db = sqlite3.connect(path.as_uri() + ("?mode=rw" if writable else "?mode=ro"), uri=True, timeout=3)
    db.row_factory = sqlite3.Row
    try:
        if not writable:
            db.execute("PRAGMA query_only=ON")
    except sqlite3.Error:
        db.close()
        raise
    return db


def check_schema(db):
    need(db.execute("PRAGMA user_version").fetchone()[0] == 1, "unsupported/missing memory schema; do not reset the store")
    columns = {row[1] for row in db.execute("PRAGMA table_info(revisions)")}
    need(columns == {"id", "revision", "payload", "payload_sha256", "created_at", "actor"}, "invalid revisions schema")
    triggers = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='trigger'")}
    need({"revisions_no_update", "revisions_no_delete"} <= triggers, "immutable history triggers missing")


def init(root, actor):
    need(actor == "main", "writes require explicit --actor main; Engineer uses read/search")
    root, path = store_path(root)
    if path.exists():
        with closing(connect(path)) as db, db:
            check_schema(db)
        return {"status": "EXISTS", "store": str(path), "next_action": "Read/search existing records; preserve history."}
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path, timeout=3)) as db, db:
        # SQLite serializes simultaneous initializations; no scripts or deletes
        # are run against an existing unrelated schema.
        db.execute("BEGIN IMMEDIATE")
        tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        need(not tables or db.execute("PRAGMA user_version").fetchone()[0] == 1, "existing unrelated schema blocks initialization")
        for statement in SCHEMA.split(";\n"):
            if statement.strip():
                # Trigger bodies contain internal semicolons but not ';\n'.
                db.execute(statement)
        db.execute("PRAGMA user_version=1")
        check_schema(db)
    return {"status": "INITIALIZED", "store": str(path), "next_action": "Main may put bounded records with expected revision 0."}


def payload_from_row(row, root):
    payload = json.loads(row["payload"])
    validate_payload(payload, root)
    need(payload["id"] == row["id"] and digest_text(canonical(payload)) == row["payload_sha256"], "stored payload integrity mismatch")
    return payload


def decode_row(row, root, full=False):
    payload = payload_from_row(row, root)
    record = dict(payload) if full else {key: payload[key] for key in ("id", "kind", "title", "tags", "review_status")}
    if not full:
        record["content_excerpt"] = payload["content"][:240]
    record.update(revision=row["revision"], created_at=row["created_at"], actor=row["actor"],
                  payload_sha256=row["payload_sha256"], **evidence_state(root, payload))
    return record


def put(root, value, expected_revision, actor):
    need(actor == "main", "writes require explicit --actor main; Engineer uses read/search")
    need(type(expected_revision) is int and expected_revision >= 0, "expected_revision must be a non-negative integer (0 for new records)")
    root, path = store_path(root)
    value = validate_payload(value, root)
    encoded = canonical(value)
    with closing(connect(path, writable=True)) as db, db:
        check_schema(db)
        db.execute("BEGIN IMMEDIATE")
        current = db.execute("SELECT * FROM revisions WHERE id=? ORDER BY revision DESC LIMIT 1", (value["id"],)).fetchone()
        revision = current["revision"] if current else 0
        # This check precedes idempotency, so a stale caller cannot silently
        # disguise a concurrent update as an unchanged write.
        need(expected_revision == revision, f"STALE_REVISION: expected {expected_revision}, current {revision}; read before retry")
        if current:
            payload_from_row(current, root)
        state = evidence_state(root, value)
        need(value["review_status"] != "accepted" or state["evidence_status"] == "CURRENT", "accepted decision requires current non-empty evidence; save a proposal/unverified record or repair evidence")
        if current and current["payload"] == encoded:
            status = "UNCHANGED"
        else:
            revision += 1
            db.execute("INSERT INTO revisions VALUES (?,?,?,?,?,?)", (value["id"], revision, encoded, digest_text(encoded), datetime.now(timezone.utc).isoformat(), actor))
            status = "STORED"
    return {"status": status, "id": value["id"], "revision": revision, "review_status": value["review_status"],
            **state, "next_action": "MAIN retains review authority; read/verify before using this decision."}


def read(root, record_id, revision=None, verify=False):
    root, path = store_path(root)
    with closing(connect(path)) as db, db:
        check_schema(db)
        if revision is None:
            row = db.execute("SELECT * FROM revisions WHERE id=? ORDER BY revision DESC LIMIT 1", (record_id,)).fetchone()
        else:
            need(type(revision) is int and revision > 0, "revision must be positive")
            row = db.execute("SELECT * FROM revisions WHERE id=? AND revision=?", (record_id, revision)).fetchone()
        if row is None:
            return {"status": "NOT_FOUND", "id": record_id, "next_action": "Main must establish this record; absence proves no prior decision."}
        record = decode_row(row, root, full=True)
    status = "UNVERIFIED" if record["evidence_status"] != "CURRENT" else "EVIDENCE_CURRENT" if verify else "READ"
    return {"status": status, "record": record, "next_action": "Repair stale/missing evidence and obtain Main review." if status == "UNVERIFIED" else "Use the recorded status as context; evidence currency does not grant creative PASS."}


def browse(root, command="list", query=None, kinds=None, record_id=None, limit=20, offset=0, full=False):
    need(type(limit) is int and 1 <= limit <= 100 and type(offset) is int and offset >= 0, "limit must be 1..100; offset must be non-negative")
    if command == "search":
        bounded_text(query, "query", 256)
    root, path = store_path(root)
    with closing(connect(path)) as db, db:
        check_schema(db)
        if command == "history":
            rows = db.execute("SELECT * FROM revisions WHERE id=? ORDER BY revision DESC", (record_id,))
        else:
            rows = db.execute("SELECT r.* FROM revisions r JOIN (SELECT id,MAX(revision) revision FROM revisions GROUP BY id) c USING(id,revision) ORDER BY r.id")
        tokens = query.casefold().split() if query else []
        total = 0

        def matches():
            nonlocal total
            for row in rows:
                payload = payload_from_row(row, root)
                if kinds and payload["kind"] not in kinds:
                    continue
                score = sum(4 * (token in payload["title"].casefold()) + 3 * any(token in tag.casefold() for tag in payload["tags"]) + (token in payload["content"].casefold()) for token in tokens)
                if command == "search" and not score:
                    continue
                total += 1
                yield score, row

        if command == "search":
            best = heapq.nsmallest(offset + limit, matches(), key=lambda item: (-item[0], item[1]["id"]))
            selected = best[offset:offset + limit]
        else:
            selected = []
            for item in matches():
                if offset <= total - 1 < offset + limit:
                    selected.append(item)
        output = [decode_row(row, root, full=full) for _, row in selected]
    return {"status": "FOUND" if output else "NOT_FOUND", "records": output, "total": total,
            "offset": offset, "limit": limit, "next_offset": offset + limit if offset + limit < total else None,
            "coverage": "Relevance search is not complete layout history. List every applicable kind=layout_case page before originality review.",
            "next_action": "Continue next_offset until null; read/verify relevant records and Main decisions."}


def status(root):
    root, path = store_path(root)
    if not path.is_file():
        return {"status": "NO_STORE", "store": str(path), "next_action": "Main must explicitly initialize; read operations created nothing."}
    with closing(connect(path)) as db, db:
        check_schema(db)
        need(db.execute("PRAGMA quick_check").fetchone()[0] == "ok", "SQLite integrity check failed; preserve store for recovery")
        records, revisions = db.execute("SELECT COUNT(DISTINCT id),COUNT(*) FROM revisions").fetchone()
    return {"status": "AVAILABLE", "store": str(path), "schema_version": 1, "records": records, "revisions": revisions,
            "next_action": "Read/search/list records; verify evidence before relying on stored decisions. No creative approval is inferred."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "status", "put", "read", "verify", "search", "list", "history"):
        command = commands.add_parser(name)
        if name in ("init", "put"):
            command.add_argument("--actor", required=True, choices=("main", "engineer"))
        if name == "put":
            command.add_argument("--file", type=Path, required=True)
            command.add_argument("--expected-revision", type=int, required=True)
        if name in ("read", "verify", "history"):
            command.add_argument("id")
        if name in ("read", "verify"):
            command.add_argument("--revision", type=int)
        if name == "search":
            command.add_argument("query")
        if name in ("search", "list", "history"):
            command.add_argument("--limit", type=int, default=20)
            command.add_argument("--offset", type=int, default=0)
            if name != "history":
                command.add_argument("--kind", action="append")
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            result = init(args.root, args.actor)
        elif args.command == "status":
            result = status(args.root)
        elif args.command == "put":
            need(args.file.is_file() and args.file.stat().st_size <= 64000, "record input must be an existing JSON file at most 64000 bytes")
            result = put(args.root, json.loads(args.file.read_text(encoding="utf-8-sig")), args.expected_revision, args.actor)
        elif args.command in ("read", "verify"):
            result = read(args.root, args.id, args.revision, args.command == "verify")
        else:
            result = browse(args.root, args.command, query=getattr(args, "query", None), kinds=getattr(args, "kind", None), record_id=getattr(args, "id", None), limit=args.limit, offset=args.offset)
    except (OSError, ValueError, TypeError, KeyError, sqlite3.Error, RecursionError) as exc:
        result = {"status": "NO_STORE" if str(exc).startswith("NO_STORE:") else "BLOCKED", "errors": [str(exc)],
                  "next_action": "Main must reconcile the store/input/evidence and current revision; never reset or blindly replay a write."}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return {"BLOCKED": 1, "NO_STORE": 2, "NOT_FOUND": 3, "UNVERIFIED": 4}.get(result["status"], 0)


if __name__ == "__main__":
    raise SystemExit(main())
