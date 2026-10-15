"""DesignProductionAutoHook: owned and called by design_brain_runtime.py."""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timezone

from .adapters import AuthorizedAdapters
from .contracts import DesignHookDecision, DesignTask, DesignResult, DesignQAReport, MainReviewDecision
from .policy import ROOT, STATE, atomic_json, canonical_hash, digest, input_path, output_root, single_worker, task_id, within
from .profiles import select
from design_brain_permission import can_run


def now():
    return datetime.now(timezone.utc).isoformat()


def job_path(identifier):
    import re
    if not re.fullmatch(r"design-[a-f0-9]{32}", identifier):
        raise ValueError("Invalid task ID")
    return within(STATE / "jobs" / (identifier + ".json"), ROOT)


def load_job(identifier):
    return json.loads(job_path(identifier).read_text(encoding="utf-8"))


def valid_artifacts(record):
    directory = within(Path(record["directory"]), ROOT / "output")
    result = DesignResult.model_validate(record["result"])
    if not result.artifacts:
        raise ValueError("No artifact evidence")
    for entry in result.artifacts:
        path = within(Path(entry.path), directory)
        if not path.is_file() or digest(path) != entry.sha256:
            raise ValueError("Artifact changed or disappeared; a new reviewed revision is required")
    task = DesignTask.model_validate(record["task"])
    for ref in task.inputs:
        if digest(input_path(ref.path)) != ref.sha256:
            raise ValueError("Authoritative input changed after execution")
    return result


def decision(task, mode):
    identifier = task_id(task)
    if task.no_execution or task.operation in {"brainstorm", "prompt", "other"}:
        return DesignHookDecision(eligible=False, reason="No authorized design-production intent", task_id=identifier)
    if not task.authorized:
        return DesignHookDecision(eligible=False, reason="Main has not authorized production scope", task_id=identifier)
    permission = can_run("/design-produce", mode)
    if not permission.allowed:
        raise ValueError(permission.reason)
    profile = select(task)
    required = {"build_artifact", "render_preview", "technical_qa"}
    if task.operation not in {"render", "qa"}:
        required.add("write_unit")
    elif "write_unit" in task.allowed_tools:
        raise ValueError("Read-only render/QA assignment cannot grant write_unit")
    if not required.issubset(task.allowed_tools):
        raise ValueError("Assignment lacks tools required for complete production and QA")
    if task.operation != "create" and task.operation != "assets" and not any(r.role == "editable_source" for r in task.inputs):
        raise ValueError("This operation requires declared editable unit JSON or scoped native PPTX source")
    for ref in task.inputs:
        if digest(input_path(ref.path)) != ref.sha256:
            raise ValueError("Authoritative input SHA256 does not match")
    output_root(task.output_dir)
    return DesignHookDecision(eligible=True, reason="Authorized production stage", task_id=identifier, profile=profile["adapter"])


async def run_bounded(task, identifier, adapter, dry_run):
    from .specialist import execute
    async def watch_cancel():
        while True:
            adapter.check()
            await asyncio.sleep(.1)
    worker = asyncio.create_task(execute(task, identifier, adapter, dry_run))
    watch = asyncio.create_task(watch_cancel())
    try:
        done, _ = await asyncio.wait([worker, watch], timeout=task.timeout_seconds, return_when=asyncio.FIRST_COMPLETED)
        if worker in done:
            return await worker
        if watch in done:
            await watch
        raise TimeoutError("Production execution deadline exceeded")
    finally:
        worker.cancel()
        watch.cancel()
        await asyncio.gather(worker, watch, return_exceptions=True)


class DesignProductionAutoHook:
    def dispatch(self, request_path, permission_mode, dry_run=False, session="", on_registered=None):
        source = input_path(str(request_path))
        task = DesignTask.model_validate_json(source.read_bytes())
        hook = decision(task, permission_mode)
        if not hook.eligible:
            return {"status": "PASS", "hook": hook.model_dump(), "invocations": 0, "finalAllowed": False}
        if not dry_run and not task.approval_policy.allow_paid_model:
            raise ValueError("Paid model execution was not authorized; use --dry-run for offline verification")
        identifier = hook.task_id
        fingerprint = canonical_hash(task.model_dump())
        with single_worker():
            path = job_path(identifier)
            if path.exists():
                record = load_job(identifier)
                if record["request_sha256"] != fingerprint or record["dry_run"] != dry_run:
                    raise ValueError("Idempotency conflict: same task ID has different scope or execution mode")
                if record["status"] == "RUNNING":
                    record.update(status="UNKNOWN", error="Interrupted execution; reconcile before a new revision")
                    atomic_json(path, record)
                if record["status"] in {"NEEDS_MAIN_REVIEW", "APPROVED"}:
                    valid_artifacts(record)
                hook = hook.model_copy(update={"duplicate": True})
                return {"status": "PASS" if record["status"] in {"NEEDS_MAIN_REVIEW", "APPROVED"} else "BLOCKED",
                        "hook": hook.model_dump(), "job": record, "invocations": 0, "finalAllowed": False}
            if task.revision:
                previous = task.model_copy(update={"revision": task.revision - 1})
                prior = load_job(task_id(previous))
                review = prior.get("main_review", {})
                if review.get("decision") != "REVISE" or prior["status"] == "APPROVED":
                    raise ValueError("A new revision requires scoped feedback from Main on the previous revision")
                original = DesignTask.model_validate(prior["task"])
                if task.approval_policy.max_revisions != original.approval_policy.max_revisions:
                    raise ValueError("Revision cannot increase its original budget")
                if task.output_dir != original.output_dir or task.units != original.units or task.artifact_type != original.artifact_type:
                    raise ValueError("Revision scope changed; use a separately authorized workflow stage")
                if task.output_format != original.output_format or task.operation != original.operation or not set(task.allowed_tools)<=set(original.allowed_tools) or not set(task.required_features)<=set(original.required_features) or task.timeout_seconds>original.timeout_seconds or task.max_tool_calls>original.max_tool_calls:
                    raise ValueError('Revision cannot expand format, operation, features, tools or execution budget')
            else:
                review = None
            directory = within(output_root(task.output_dir) / identifier, ROOT / "output")
            if directory.exists():
                raise ValueError("Unreconciled output directory already exists; refusing overwrite")
            record = {"task_id": identifier, "task": task.model_dump(), "request_sha256": fingerprint,
                "status": "RUNNING", "directory": str(directory), "dry_run": dry_run, "owner_pid": os.getpid(),
                "started_at": now(), "specialist_model": "gpt-6.1-sol", "main_owner": "external Codex/ChatGPT",
                "agent_count": 0, "invocations": 1, "prior_main_feedback": review, "session": session}
            atomic_json(path, record)  # Save before the first production side effect.
            if on_registered:
                on_registered(identifier)
            adapter = None
            try:
                directory.mkdir(parents=True, exist_ok=False)
                cancel = STATE / "jobs" / (identifier + ".cancel")
                adapter = AuthorizedAdapters(task, directory, cancel)
                effective = task
                if review:
                    effective = task.model_copy(update={"creative_constraints": task.creative_constraints + "\nMain revision feedback:\n" + review["feedback"]})
                output = asyncio.run(run_bounded(effective, identifier, adapter, dry_run))
                qa = adapter.verify()  # Controller trusts adapter evidence, never self-reported model QA.
                issues = output.issues[:]
                status = output.status
                if output.task_id != identifier:
                    raise ValueError("Specialist returned a different task ID")
                if qa.status != "PASS":
                    status = "UNVERIFIED" if qa.status == "UNVERIFIED" else "FAILED"
                elif status == "NEEDS_MAIN_REVIEW":
                    known = {(m.path, m.sha256) for m in adapter.manifests}
                    if any((m.path, m.sha256) not in known for m in output.artifacts):
                        status = "UNVERIFIED"
                        issues.append("Specialist claimed artifact evidence not produced by authorized tools")
                result = DesignResult(task_id=identifier, status=status, artifacts=adapter.manifests, qa=qa, issues=issues)
            except (Exception, asyncio.CancelledError, KeyboardInterrupt) as error:
                label = str(error) if isinstance(error, (ValueError, RuntimeError, TimeoutError, asyncio.CancelledError, KeyboardInterrupt)) else type(error).__name__
                label = (adapter.last_error if adapter and adapter.last_error else label) or "Execution interrupted by controller"
                result = DesignResult(task_id=identifier, status="UNVERIFIED", artifacts=adapter.manifests if adapter else [],
                    qa=DesignQAReport(status="UNVERIFIED", checks=[], issues=[label], evidence=[]), issues=[label])
            record.update(status=result.status, result=result.model_dump(), finished_at=now(),
                          agent_count=adapter.agent_count if adapter else 0,
                          tool_events=adapter.tool_events if adapter else [])
            atomic_json(path, record)
            return {"status": "PASS" if result.status == "NEEDS_MAIN_REVIEW" else "BLOCKED", "hook": hook.model_dump(),
                    "job": record, "invocations": 1, "finalAllowed": False}


def main_review(review_path, permission_mode):
    if not can_run("/design-produce", permission_mode).allowed:
        raise ValueError("Main review requires full_build permission")
    review = MainReviewDecision.model_validate_json(input_path(str(review_path)).read_bytes())
    with single_worker():
        record = load_job(review.task_id)
        if record.get("main_review") == review.model_dump():
            return record
        if record["status"] == "APPROVED":
            raise ValueError("Approved artifacts/reviews are immutable")
        if record["status"] == "RUNNING":
            raise ValueError("Interrupted job needs recovery reconciliation first")
        if review.decision == "APPROVE":
            result = valid_artifacts(record)
            if record["status"] != "NEEDS_MAIN_REVIEW" or result.qa.status != "PASS":
                raise ValueError("Only verified review-pending results can be approved")
            actual = sorted(m.sha256 for m in result.artifacts if m.role == "deliverable")
            if not actual or sorted(review.artifact_hashes) != actual:
                raise ValueError("Main must bind approval to exact deliverable hashes")
        if review.decision == "REVISE" and record["task"]["revision"] >= record["task"]["approval_policy"]["max_revisions"]:
            raise ValueError("Maximum revision rounds reached")
        record.update(status={"APPROVE": "APPROVED", "REVISE": "REVISION_REQUESTED", "BLOCK": "BLOCKED"}[review.decision],
                      main_review=review.model_dump(), reviewed_at=now())
        atomic_json(job_path(review.task_id), record)
        return record


def cancel(identifier):
    record = load_job(identifier)
    if record["status"] != "RUNNING":
        raise ValueError("Only a running job can be cancelled")
    path = STATE / "jobs" / (identifier + ".cancel")
    within(path, ROOT)
    path.write_text("Cancelled by external Main\n", encoding="utf-8")
    return {"task_id": identifier, "status": "CANCEL_REQUESTED"}


def recover(identifier):
    with single_worker():
        record = load_job(identifier)
        if record["status"] not in {"RUNNING", "UNKNOWN"}:
            raise ValueError("Recovery applies only to interrupted/unknown execution")
        record.update(status="BLOCKED", recovery={"at": now(), "action": "No replay; preserve partial output; Main must request a new revision", "prior_pid": record.get("owner_pid")})
        atomic_json(job_path(identifier), record)
        return record
