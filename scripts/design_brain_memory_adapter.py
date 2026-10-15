"""Portable Supabase memory with durable local outbox and explicit reconciliation.

No credentials in arguments or output. Readers never create or modify local files.
The existing design_brain_local_memory store remains readable alongside this store.
"""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

sys.dont_write_bytecode = True
import design_brain_local_memory as local

ROOT = Path(__file__).resolve().parents[1]
CONFIG = Path("capabilities/design-memory/supabase.project.json")
DATABASE = Path(".design-brain/local-memory/adapter.sqlite3")
SECRETS = {"main": Path(".design-brain/local-memory/supabase-writer.secret.json"),
           "engineer": Path(".design-brain/local-memory/supabase-reader.secret.json")}
SCHEMA = """
CREATE TABLE IF NOT EXISTS operations (
 operation_id TEXT PRIMARY KEY, namespace TEXT NOT NULL, record_id TEXT NOT NULL,
 expected_revision INTEGER NOT NULL, payload_text TEXT NOT NULL, payload_sha256 TEXT NOT NULL,
 state TEXT NOT NULL, result TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS immutable_request BEFORE UPDATE OF
 operation_id,namespace,record_id,expected_revision,payload_text,payload_sha256,created_at ON operations
 BEGIN SELECT RAISE(ABORT,'operation request is immutable'); END;
CREATE TABLE IF NOT EXISTS cache (
 namespace TEXT NOT NULL,id TEXT NOT NULL,revision INTEGER NOT NULL,payload_text TEXT NOT NULL,
 payload_sha256 TEXT NOT NULL,operation_id TEXT,created_at TEXT,pulled_at TEXT NOT NULL,
 PRIMARY KEY(namespace,id,revision)
);
PRAGMA user_version=1;
"""


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class RemoteError(Exception):
    def __init__(self, code, uncertain=False):
        self.code, self.uncertain = code, uncertain
        super().__init__(code)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Adapter:
    def __init__(self, root=ROOT, actor="engineer", transport=None, environment=None):
        self.root = Path(root).resolve()
        local.need(self.root.is_dir(), "plugin root does not exist")
        self.actor, self.transport = actor, transport
        env = os.environ if environment is None else environment
        local.need(actor in SECRETS, "unknown actor")
        config_file, secret_file = self.root / CONFIG, self.root / SECRETS[actor]
        self.configuration_error = None
        try:
            config = json.loads(config_file.read_text(encoding="utf-8")) if config_file.exists() else {}
            secrets = json.loads(secret_file.read_text(encoding="utf-8")) if secret_file.exists() else {}
            local.need(isinstance(config, dict) and isinstance(secrets, dict), "invalid configuration")
        except (ValueError, OSError, RecursionError):
            config, secrets = {}, {}
            self.configuration_error = "LOCAL_CONFIG_INVALID"
        self.namespace = env.get("CODEX_DESIGN_MEMORY_NAMESPACE", config.get("namespace", "codex-design"))
        if not (isinstance(self.namespace, str) and bool(local.SLUG.fullmatch(self.namespace))):
            self.namespace, self.configuration_error = "codex-design", "NAMESPACE_INVALID"
        value = env.get("CODEX_DESIGN_SUPABASE_URL", config.get("url", ""))
        self.url = value.rstrip("/") if isinstance(value, str) else ""
        if not isinstance(value, str): self.configuration_error = "HTTPS_ORIGIN_INVALID"
        self.api_key = env.get("CODEX_DESIGN_SUPABASE_PUBLISHABLE_KEY", secrets.get("publishable_key", config.get("publishable_key", "")))
        token_name = "write_token" if actor == "main" else "read_token"
        self.token = env.get("CODEX_DESIGN_MEMORY_" + token_name.upper(), secrets.get(token_name, ""))
        self.path = (self.root / DATABASE).resolve()
        local.need(self.path.is_relative_to(self.root), "adapter store escapes plugin root")
        if self.url:
            try:
                url = urllib.parse.urlsplit(self.url)
                local.need(url.scheme == "https" and bool(url.hostname) and not url.username
                           and not url.password and not url.query and not url.fragment and url.path in ("", "/"), "invalid origin")
            except ValueError:
                self.configuration_error = "HTTPS_ORIGIN_INVALID"

    def db(self, write=False):
        if write:
            local.need(self.actor == "main", "writes require --actor main")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            exists = self.path.exists()
            db = sqlite3.connect(self.path, timeout=5)
            if not exists:
                db.executescript(SCHEMA)
        else:
            if not self.path.exists():
                return None
            db = sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True, timeout=5)
            db.execute("PRAGMA query_only=ON")
        db.row_factory = sqlite3.Row
        try:
            local.need(db.execute("PRAGMA user_version").fetchone()[0] == 1, "adapter database schema mismatch")
        except Exception:
            db.close()
            raise
        return db

    def rpc(self, method, payload):
        if self.transport:
            return self.transport(method, dict(payload, p_namespace=self.namespace))
        if self.configuration_error:
            raise RemoteError(self.configuration_error)
        if not (self.url and self.api_key and self.token):
            raise RemoteError("NOT_CONFIGURED")
        body = json.dumps(dict(payload, p_namespace=self.namespace, p_access_key=self.token)).encode("utf-8")
        request = urllib.request.Request(self.url + "/rest/v1/rpc/codex_design_memory_" + method,
                                         data=body, headers={"apikey": self.api_key, "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.build_opener(NoRedirect).open(request, timeout=12) as response:
                raw = response.read(8 * 1024 * 1024 + 1)
                if len(raw) > 8 * 1024 * 1024:
                    raise RemoteError("RESPONSE_TOO_LARGE", method == "put")
                result = json.loads(raw)
                if not isinstance(result, dict):
                    raise RemoteError("INVALID_RESPONSE", method == "put")
                return result
        except urllib.error.HTTPError as error:
            # Never print response bodies: providers/proxies may echo credentials.
            raw = error.read(16000)
            code = "HTTP_" + str(error.code)
            for known in ("MEMORY_REVISION_CONFLICT", "MEMORY_OPERATION_CONFLICT", "MEMORY_ACCESS_DENIED", "MEMORY_INPUT_INVALID"):
                if known.encode() in raw:
                    raise RemoteError(known)
            raise RemoteError(code, method == "put" and error.code >= 500) from None
        except RecursionError:
            raise RemoteError("INVALID_RESPONSE", method == "put") from None
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
            raise RemoteError("TRANSPORT_UNAVAILABLE", method == "put") from None

    def decoded(self, row, origin, state=None):
        local.need(isinstance(row, dict) and row.get("namespace") == self.namespace, "memory namespace mismatch")
        value = json.loads(row["payload_text"])
        local.validate_payload(value, self.root)
        local.need(row.get("id", row.get("record_id")) == value["id"], "memory row identity mismatch")
        local.need(isinstance(row.get("operation_id"), str) and str(uuid.UUID(row["operation_id"])) == row["operation_id"], "invalid operation identity")
        if origin == "local-outbox":
            local.need(type(row.get("expected_revision")) is int and row["expected_revision"] >= 0, "invalid expected revision")
        else:
            local.need(type(row.get("revision")) is int and row["revision"] > 0, "invalid memory revision")
        local.need(digest(row["payload_text"]) == row["payload_sha256"], "memory payload checksum mismatch")
        return dict(value, origin=origin, revision=row.get("revision"),
                    expected_revision=row.get("expected_revision"), operation_id=row.get("operation_id"),
                    sync_state=state or "CONFIRMED", payload_sha256=row["payload_sha256"],
                    **local.evidence_state(self.root, value))

    def local_records(self, record_id=None, all_revisions=False):
        rows = []
        db = self.db()
        if db is not None:
            with closing(db):
                query = "SELECT * FROM cache WHERE namespace=? ORDER BY id,revision" if all_revisions else "SELECT c.* FROM cache c JOIN (SELECT id,MAX(revision) revision FROM cache WHERE namespace=? GROUP BY id) h USING(id,revision) WHERE c.namespace=?"
                parameters = (self.namespace,) if all_revisions else (self.namespace, self.namespace)
                for row in db.execute(query, parameters):
                    item = dict(row)
                    if record_id is None or item["id"] == record_id:
                        rows.append(self.decoded(item, "supabase-cache"))
                for row in db.execute("SELECT * FROM operations WHERE namespace=? AND state!='CONFIRMED' ORDER BY created_at", (self.namespace,)):
                    item = dict(row)
                    if record_id is None or item["record_id"] == record_id:
                        rows.append(self.decoded(item, "local-outbox", item["state"]))
        # Preserve records created before cloud wiring. Never silently merge IDs.
        legacy = self.root / local.STORE
        if legacy.exists():
            if record_id:
                if all_revisions:
                    offset = 0
                    while True:
                        page = local.browse(self.root, command="history", record_id=record_id, limit=100, offset=offset)
                        for item in page["records"]:
                            value = local.read(self.root, record_id, revision=item["revision"])["record"]
                            rows.append(dict(value, origin="local-legacy", sync_state="LOCAL_ONLY"))
                        if page["next_offset"] is None: break
                        offset = page["next_offset"]
                else:
                    result = local.read(self.root, record_id)
                    if "record" in result:
                        rows.append(dict(result["record"], origin="local-legacy", sync_state="LOCAL_ONLY"))
            else:
                offset = 0
                while True:
                    page = local.browse(self.root, limit=100, offset=offset)
                    for row in page["records"]:
                        value = local.read(self.root, row["id"])["record"]
                        rows.append(dict(value, origin="local-legacy", sync_state="LOCAL_ONLY"))
                    if page["next_offset"] is None:
                        break
                    offset = page["next_offset"]
        return rows

    def read(self, record_id, revision=None):
        rows, remote_error, local_error = [], None, None
        try:
            result = self.rpc("get", {"p_id": record_id, "p_revision": revision})
            if result.get("status") == "READ":
                value = self.decoded(result["record"], "supabase")
                local.need(value["id"] == record_id and (revision is None or value["revision"] == revision), "read result does not match requested ID/revision")
                rows.append(value)
            else:
                local.need(result.get("status") == "NOT_FOUND" and not result.get("record"), "invalid read response")
        except RemoteError as error:
            remote_error = error.code
        except (ValueError, KeyError, TypeError):
            remote_error = "INVALID_REMOTE_RESPONSE"
        try:
            fallback = self.local_records(record_id, all_revisions=revision is not None)
            if revision is not None:
                fallback = [row for row in fallback if row["origin"] == "supabase-cache" and row["revision"] == revision]
        except (ValueError, KeyError, TypeError, sqlite3.Error, OSError):
            fallback, local_error = [], "LOCAL_DATA_UNVERIFIED"
        # Cached copies are only current alternatives when cloud is unavailable.
        rows += [row for row in fallback if remote_error or row["origin"] != "supabase-cache"]
        return {"status": "FOUND" if rows else "UNAVAILABLE" if remote_error or local_error else "NOT_FOUND", "records": rows, "remote_error": remote_error, "local_error": local_error,
                "coverage": "Compare origins and pending revisions; local-only data is not silently promoted or discarded."}

    def search(self, query=None, kind=None, limit=20, offset=0, history_id=None):
        local.need(1 <= limit <= 100 and offset >= 0, "limit must be 1..100 and offset non-negative")
        remote, remote_error, local_error = None, None, None
        try:
            remote = self.rpc("query", {"p_query": query, "p_kind": kind, "p_limit": limit,
                                       "p_offset": offset, "p_history_id": history_id})
            self.check_page(remote, limit, offset)
            remote = dict(remote, records=[self.decoded(row, "supabase") for row in remote["records"]])
            local.need(all((not history_id or row["id"] == history_id) and (not kind or row["kind"] == kind) for row in remote["records"]), "query scope mismatch")
        except RemoteError as error:
            remote_error = error.code
        except (ValueError, KeyError, TypeError):
            remote, remote_error = None, "INVALID_REMOTE_RESPONSE"
        try:
            fallback = self.local_records(history_id, all_revisions=bool(history_id))
        except (ValueError, KeyError, TypeError, sqlite3.Error, OSError):
            fallback, local_error = [], "LOCAL_DATA_UNVERIFIED"
        tokens = query.casefold().split() if query else []
        fallback = [row for row in fallback if (not kind or row["kind"] == kind)
                    and (not tokens or any(token in (row["title"] + " " + row["content"] + " " + " ".join(row["tags"])).casefold() for token in tokens))
                    and (remote_error or row["origin"] != "supabase-cache")]
        return {"status": "RESULTS", "remote": remote, "remote_error": remote_error, "local_error": local_error,
                "local": {"records": fallback[offset:offset+limit], "total": len(fallback),
                          "next_offset": offset+limit if offset+limit < len(fallback) else None},
                "coverage": "Page both sources. Search rank and available cache do not prove complete historical coverage."}

    @staticmethod
    def check_page(page, limit, offset):
        local.need(isinstance(page, dict) and page.get("status") == "FOUND" and isinstance(page.get("records"), list), "invalid page")
        total = page.get("total")
        local.need(type(total) is int and total >= 0 and page.get("limit") == limit and page.get("offset") == offset, "invalid page bounds")
        local.need(len(page["records"]) == min(limit, max(0, total-offset)), "incomplete page")
        local.need(page.get("next_offset") == (offset+limit if offset+limit < total else None), "invalid pagination")

    def cache_row(self, db, row):
        value = self.decoded(row, "supabase")
        old = db.execute("SELECT payload_sha256 FROM cache WHERE namespace=? AND id=? AND revision=?",
                         (self.namespace, value["id"], row["revision"])).fetchone()
        local.need(old is None or old[0] == row["payload_sha256"], "same remote revision has conflicting payload")
        db.execute("INSERT OR IGNORE INTO cache VALUES (?,?,?,?,?,?,?,?)",
                   (self.namespace, value["id"], row["revision"], row["payload_text"], row["payload_sha256"],
                    row.get("operation_id"), row.get("created_at"), now()))

    def operation(self, operation_id):
        db = self.db()
        if db is None:
            return None
        with closing(db):
            row = db.execute("SELECT * FROM operations WHERE namespace=? AND operation_id=?", (self.namespace, operation_id)).fetchone()
            if row is None:
                return None
            value = dict(row)
            self.decoded(value, "local-outbox", value["state"])
            local.need(value["expected_revision"] >= 0 and value["state"] in ("QUEUED", "UNKNOWN", "CONFLICT", "CONFIRMED"), "invalid local operation state")
            return value

    def mark(self, operation_id, state, result):
        with closing(self.db(True)) as db, db:
            db.execute("UPDATE operations SET state=?,result=?,updated_at=? WHERE operation_id=? AND namespace=? AND state!='CONFIRMED'",
                       (state, local.canonical(result), now(), operation_id, self.namespace))

    def confirm(self, request, result):
        row = result.get("record")
        local.need(result.get("status") in ("STORED", "UNCHANGED")
                   and result.get("payload_sha256") == request["payload_sha256"]
                   and isinstance(row, dict) and row["payload_sha256"] == request["payload_sha256"]
                   and row["payload_text"] == request["payload_text"]
                   and result.get("namespace") == self.namespace
                   and result.get("operation_id") == request["operation_id"]
                   and type(result.get("expected_revision")) is int
                   and result.get("expected_revision") == request["expected_revision"], "remote receipt does not match immutable request")
        value = self.decoded(row, "supabase")
        local.need(value["id"] == request["record_id"], "remote receipt record ID mismatch")
        local.need(value["revision"] == request["expected_revision"] + (1 if result["status"] == "STORED" else 0), "remote receipt revision mismatch")
        local.need(result["status"] != "STORED" or row["operation_id"] == request["operation_id"], "stored revision operation mismatch")
        with closing(self.db(True)) as db, db:
            self.cache_row(db, row)
            db.execute("UPDATE operations SET state='CONFIRMED',result=?,updated_at=? WHERE operation_id=? AND namespace=?",
                       (local.canonical(result), now(), request["operation_id"], self.namespace))
        return {"status": "CONFIRMED", "operation_id": request["operation_id"], "record": value}

    def send(self, request, reconcile=False):
        local.need(self.actor == "main", "writes require --actor main")
        if request["state"] == "CONFLICT":
            return {"status": "CONFLICT", "operation_id": request["operation_id"], "next_action": "Read current shared record; resolve explicitly in a new operation."}
        if request["state"] == "CONFIRMED":
            return {"status": "CONFIRMED", "operation_id": request["operation_id"], "result": json.loads(request["result"])}
        try:
            if reconcile:
                receipt = self.rpc("operation", {"p_operation_id": request["operation_id"]})
                if receipt.get("status") in ("STORED", "UNCHANGED"):
                    return self.confirm(request, receipt)
                if receipt.get("status") != "NOT_FOUND" or receipt.get("record") is not None:
                    raise RemoteError("INVALID_OPERATION_RESPONSE", True)
            elif request["state"] == "UNKNOWN":
                return {"status": "UNKNOWN_LOCAL_SAVED", "operation_id": request["operation_id"], "next_action": "Use sync with this operation ID."}
            value = json.loads(request["payload_text"])
            if value["review_status"] == "accepted" and local.evidence_state(self.root, value)["evidence_status"] != "CURRENT":
                return {"status": "UNVERIFIED_LOCAL_SAVED", "operation_id": request["operation_id"],
                        "next_action": "Evidence changed before dispatch; Main must verify and prepare an explicit corrected operation."}
            self.mark(request["operation_id"], "UNKNOWN", {"reason": "dispatch may start; reconcile on interruption"})
            result = self.rpc("put", {"p_payload_text": request["payload_text"], "p_expected_revision": request["expected_revision"], "p_operation_id": request["operation_id"]})
            return self.confirm(request, result)
        except RemoteError as error:
            state = "CONFLICT" if error.code in ("MEMORY_REVISION_CONFLICT", "MEMORY_OPERATION_CONFLICT") else "UNKNOWN" if error.uncertain or request["state"] == "UNKNOWN" else "QUEUED"
            self.mark(request["operation_id"], state, {"error": error.code})
            latest = self.operation(request["operation_id"])
            if latest["state"] == "CONFIRMED":
                return {"status": "CONFIRMED", "operation_id": request["operation_id"], "result": json.loads(latest["result"])}
            return {"status": state + "_LOCAL_SAVED", "operation_id": request["operation_id"], "remote_error": error.code,
                    "next_action": "Cloud success is unconfirmed; inspect status and use explicit sync with the same operation ID."}

    def put(self, record, expected_revision, operation_id):
        local.need(self.actor == "main", "writes require --actor main")
        local.need(type(expected_revision) is int and expected_revision >= 0, "expected revision must be non-negative")
        local.need(str(uuid.UUID(operation_id)) == operation_id, "operation ID must be canonical UUID")
        local.validate_payload(record, self.root)
        local.need(record["review_status"] != "accepted" or local.evidence_state(self.root, record)["evidence_status"] == "CURRENT", "accepted record requires current local evidence")
        payload = local.canonical(record)
        with closing(self.db(True)) as db, db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute("SELECT * FROM operations WHERE operation_id=?", (operation_id,)).fetchone()
            if existing:
                local.need(existing["namespace"] == self.namespace and existing["payload_text"] == payload and existing["expected_revision"] == expected_revision,
                           "operation ID already belongs to another immutable request")
            else:
                db.execute("INSERT INTO operations VALUES (?,?,?,?,?,?,'QUEUED',NULL,?,?)",
                           (operation_id, self.namespace, record["id"], expected_revision, payload, digest(payload), now(), now()))
        return self.send(self.operation(operation_id))

    def sync(self, operation_id):
        local.need(self.actor == "main", "sync requires --actor main")
        request = self.operation(operation_id)
        local.need(request is not None, "operation not found; do not invent or replay an ID")
        return self.send(request, reconcile=True)

    def pull(self):
        local.need(self.actor == "main", "cache refresh requires --actor main")
        total, offset = 0, 0
        while True:
            page = self.rpc("query", {"p_query": None, "p_kind": None, "p_limit": 100, "p_offset": offset, "p_history_id": None})
            self.check_page(page, 100, offset)
            with closing(self.db(True)) as db, db:
                for row in page["records"]:
                    self.cache_row(db, row)
            total += len(page["records"])
            following = page.get("next_offset")
            if following is None:
                break
            local.need(type(following) is int and following > offset, "invalid remote pagination")
            offset = following
        return {"status": "CACHED", "count": total, "coverage": "Current records observed during paging; repeat if concurrent writes change coverage. Historical revisions remain on Supabase."}

    def status(self):
        states, local_error = {}, None
        try:
            db = self.db()
            if db is not None:
                with closing(db):
                    states = {row[0]: row[1] for row in db.execute("SELECT state,COUNT(*) FROM operations WHERE namespace=? GROUP BY state", (self.namespace,))}
        except (ValueError, sqlite3.Error, OSError):
            local_error = "LOCAL_DATA_UNVERIFIED"
        try:
            remote = self.rpc("query", {"p_limit": 1})
            self.check_page(remote, 1, 0)
            remote_status = "AVAILABLE"
        except RemoteError as error:
            remote_status = error.code
        except (ValueError, KeyError, TypeError):
            remote_status = "INVALID_REMOTE_RESPONSE"
        return {"namespace": self.namespace, "remote": remote_status, "operations": states, "local_error": local_error,
                "local_store_exists": self.path.exists(), "legacy_local_exists": (self.root/local.STORE).exists(),
                "actor": self.actor, "credentials": "never included", "creative_approval": "NOT_INFERRED"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--actor", choices=("main", "engineer"), default="engineer")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    read = sub.add_parser("read"); read.add_argument("id"); read.add_argument("--revision", type=int)
    for name in ("search", "list", "history"):
        command = sub.add_parser(name)
        if name == "search": command.add_argument("query")
        if name == "history": command.add_argument("id")
        command.add_argument("--kind"); command.add_argument("--limit", type=int, default=20); command.add_argument("--offset", type=int, default=0)
    put = sub.add_parser("put"); put.add_argument("--file", type=Path, required=True)
    put.add_argument("--expected-revision", type=int, required=True); put.add_argument("--operation-id", required=True)
    sync = sub.add_parser("sync"); sync.add_argument("operation_id")
    sub.add_parser("pull")
    args = parser.parse_args(argv)
    try:
        adapter = Adapter(args.root, args.actor)
        if args.command == "put":
            local.need(args.file.stat().st_size <= 64000, "record input exceeds 64 KB")
            result = adapter.put(json.loads(args.file.read_text(encoding="utf-8-sig")), args.expected_revision, args.operation_id)
        elif args.command == "read": result = adapter.read(args.id, args.revision)
        elif args.command in ("search", "list", "history"):
            result = adapter.search(getattr(args, "query", None), args.kind, args.limit, args.offset, getattr(args, "id", None))
        elif args.command == "sync": result = adapter.sync(args.operation_id)
        else: result = getattr(adapter, args.command)()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, sqlite3.Error, RemoteError, KeyError, TypeError, RecursionError) as error:
        # Do not include unexpected provider/config payloads or credential values.
        print(json.dumps({"status": "ERROR", "error": error.code if isinstance(error, RemoteError) else type(error).__name__,
                          "next_action": "Inspect local configuration/data and preserve uncertain operations; no completion is inferred."}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
