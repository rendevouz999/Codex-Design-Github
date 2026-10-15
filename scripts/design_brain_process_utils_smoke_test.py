#!/usr/bin/env python
"""Smoke tests for Brain Design bounded process utilities."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

from design_brain_process_utils import (  # noqa: E402
    PythonInvocation,
    excerpt,
    kill_process_tree,
    process_liveness,
    python_child_exec_works,
    python_command,
    resolve_python_invocation,
    run_command,
)


@dataclass
class WorkerProcessResult:
    ok: bool
    returncode: int
    timedOut: bool
    duration: float
    stdout: str
    stderr: str
    stdoutExcerpt: str
    stderrExcerpt: str
    killedPids: list[int]
    killStrategy: str
    lastWorkerStatus: str
    statusPath: str
    stdoutPath: str
    stderrPath: str
    doneButNotExited: bool
    reason: str


class Smoke:
    def __init__(self) -> None:
        self.checks = 0
        self.normal_duration = 0.0
        self.simple_timeout_duration = 0.0
        self.direct_kill_duration = 0.0

    def ok(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(message)


def root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-test Brain Design process utility timeout behavior.")
    parser.add_argument("--repeat", type=int, default=3, help="Worker iterations to run in supervisor mode.")
    parser.add_argument("--timeout", type=float, default=8, help="General timeout for worker commands.")
    parser.add_argument("--max-duration", type=float, default=60, help="Maximum total supervisor duration in seconds.")
    parser.add_argument("--setup-timeout", type=float, default=15, help="Timeout for direct nested ready-file setup.")
    parser.add_argument("--simple-timeout", type=float, default=3, help="Timeout for the simple run_command timeout test.")
    parser.add_argument("--include-nested-run-command", action="store_true", help="Run optional nested run_command timeout stress test.")
    parser.add_argument("--worker-once", action="store_true", help="Run a single worker iteration instead of supervisor mode.")
    parser.add_argument("--worker-max-duration", type=float, default=30, help="Maximum worker runtime in seconds.")
    parser.add_argument("--deterministic-repeat", action="store_true", help="Keep deterministic worker status/output paths visible in supervisor output.")
    parser.add_argument("--cleanup-on-fail", action="store_true", help="Remove worker status/output files even when a worker fails.")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def read_pid(path: Path) -> int:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except Exception:
        return 0


def wait_for_files(paths: list[Path], timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if all(path.exists() for path in paths):
            return True
        time.sleep(0.05)
    return all(path.exists() for path in paths)


def resolved_candidate(candidate: str) -> str | None:
    if not candidate:
        return None
    path = Path(candidate)
    if path.is_absolute():
        return str(path) if path.exists() else None
    found = shutil.which(candidate)
    return str(found) if found else None


def child_exec_sanity_rows(timeout: float) -> list[tuple[str, str, str, bool, str]]:
    rows: list[tuple[str, str, str, bool, str]] = []
    modes = (("plain", []), ("no_site", ["-S"]), ("isolated_no_site", ["-I", "-S"]))
    for label, candidate in (("sys.executable", sys.executable), ("python3", "python3"), ("python", "python")):
        resolved = resolved_candidate(candidate)
        if not resolved:
            rows.append((label, "plain", candidate or "<empty>", False, "not found"))
            continue
        for mode, flags in modes:
            passed = python_child_exec_works(resolved, timeout=timeout, flags=flags)
            command_hint = " ".join([resolved, *flags]) if flags else resolved
            rows.append((label, mode, command_hint, passed, "PASS" if passed else "FAIL"))
    return rows


def print_resolver_context(invocation: PythonInvocation, *, verbose: bool, probe_all: bool = True) -> None:
    env_override = bool(os.environ.get("BRAIN_DESIGN_PYTHON", "").strip())
    supervisor_handoff = bool(os.environ.get("BRAIN_DESIGN_RESOLVED_PYTHON", "").strip())
    flags = " ".join(invocation.flags) if invocation.flags else "<none>"
    if supervisor_handoff:
        print("Using supervisor-resolved Python invocation", flush=True)
    print(f"Resolved Python executable: {invocation.executable}", flush=True)
    print(f"Resolved Python flags: {flags}", flush=True)
    print(f"Selected Python invocation: {' '.join(invocation.commandPrefix)}", flush=True)
    print(f"Python invocation mode: {invocation.mode}", flush=True)
    print(f"Python invocation source: {invocation.source}", flush=True)
    print(f"BRAIN_DESIGN_PYTHON override: {'yes' if env_override else 'no'}", flush=True)
    print("run_command process creation mode: non-isolated", flush=True)
    if os.environ.get("BRAIN_DESIGN_SKIP_PYTHON_PROBES") == "1":
        print("Python invocation probes:", flush=True)
        print(f"- supervisor exact invocation: SKIPPED ({' '.join(invocation.commandPrefix)}; supervisor handoff trusted)", flush=True)
        return
    if not probe_all:
        exact = python_child_exec_works(invocation.executable, timeout=3 if verbose else 2, flags=invocation.flags)
        print("Python invocation probes:", flush=True)
        print(f"- supervisor exact invocation: {'PASS' if exact else 'FAIL'} ({' '.join(invocation.commandPrefix)})", flush=True)
        return
    print("Python invocation probes:", flush=True)
    for label, mode, candidate, passed, detail in child_exec_sanity_rows(timeout=3 if verbose else 2):
        status = "PASS" if passed else "FAIL"
        print(f"- {label} {mode}: {status} ({candidate}; {detail})", flush=True)


def temp_capture_path(prefix: str) -> Path:
    handle = tempfile.NamedTemporaryFile(prefix=prefix, suffix=".log", delete=False)
    path = Path(handle.name)
    handle.close()
    return path


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def unlink_quietly(path: Path) -> None:
    try:
        path.unlink()
    except OSError:
        pass


def worker_status_path() -> Path | None:
    raw = os.environ.get("BRAIN_DESIGN_WORKER_STATUS_PATH", "").strip()
    return Path(raw) if raw else None


def write_worker_status(phase: str) -> None:
    path = worker_status_path()
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{phase}\n{time.time():.6f}\n", encoding="utf-8")
    except OSError:
        pass


def read_worker_status(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return ""
    return lines[0].strip() if lines else ""


def worker_hard_exit_enabled() -> bool:
    return os.environ.get("BRAIN_DESIGN_WORKER_HARD_EXIT", "").strip() == "1"


def supervisor_creation_kwargs() -> dict[str, object]:
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def supervisor_procfs_descendants(pid: int) -> list[int]:
    proc_root = Path("/proc")
    if not proc_root.exists() or pid <= 0:
        return []
    children: dict[int, list[int]] = {}
    for entry in proc_root.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            stat = (entry / "stat").read_text(encoding="utf-8", errors="ignore")
            tail = stat.rsplit(")", 1)[1].strip().split()
            if len(tail) >= 2:
                child_pid = int(entry.name)
                parent_pid = int(tail[1])
                children.setdefault(parent_pid, []).append(child_pid)
        except Exception:
            continue
    result: list[int] = []
    stack = list(children.get(pid, []))
    while stack:
        child = stack.pop()
        if child in result:
            continue
        result.append(child)
        stack.extend(children.get(child, []))
    return result


def supervisor_kill_worker(proc: subprocess.Popen[bytes], started_process_group: bool = False) -> dict[str, object]:
    """Supervisor-native worker kill that does not call runtime helpers under test."""

    started = time.monotonic()
    killed: list[int] = []
    strategies: list[str] = []
    timed_out = False

    if proc.poll() is not None:
        return {"strategy": "already-exited", "killedPids": [], "timedOut": False, "duration": time.monotonic() - started}

    if os.name == "nt":
        try:
            taskkill = subprocess.Popen(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            taskkill_started = time.monotonic()
            while taskkill.poll() is None:
                if time.monotonic() - taskkill_started > 3:
                    try:
                        taskkill.kill()
                    except OSError:
                        pass
                    timed_out = True
                    break
                time.sleep(0.05)
            strategies.append("taskkill")
            killed.append(proc.pid)
        except Exception:
            strategies.append("taskkill-failed")
        if proc.poll() is None:
            try:
                proc.kill()
                killed.append(proc.pid)
                strategies.append("parent-kill")
            except Exception:
                strategies.append("parent-kill-failed")
        return {
            "strategy": "+".join(strategies) if strategies else "none",
            "killedPids": sorted(set(killed)),
            "timedOut": timed_out,
            "duration": time.monotonic() - started,
        }

    if started_process_group:
        try:
            pgid = os.getpgid(proc.pid)
            os.killpg(pgid, signal.SIGKILL)
            killed.append(proc.pid)
            strategies.append("process-group")
        except Exception:
            strategies.append("process-group-failed")

    descendants = supervisor_procfs_descendants(proc.pid)
    for child_pid in sorted(descendants, reverse=True):
        try:
            os.kill(child_pid, signal.SIGKILL)
            killed.append(child_pid)
        except Exception:
            pass
    if descendants:
        strategies.append("procfs-descendants")

    if proc.poll() is None:
        try:
            proc.kill()
            killed.append(proc.pid)
            strategies.append("parent-kill")
        except Exception:
            strategies.append("parent-kill-failed")

    wait_deadline = time.monotonic() + 3
    while proc.poll() is None and time.monotonic() < wait_deadline:
        time.sleep(0.05)
    if proc.poll() is None:
        timed_out = True

    return {
        "strategy": "+".join(strategies) if strategies else "none",
        "killedPids": sorted(set(killed)),
        "timedOut": timed_out,
        "duration": time.monotonic() - started,
    }


def run_worker_subprocess_direct(
    command: list[str],
    timeout: float,
    cwd: Path,
    env: dict[str, str] | None = None,
    status_path: Path | None = None,
    keep_output_on_failure: bool = False,
    verbose: bool = False,
) -> WorkerProcessResult:
    start = time.monotonic()
    deadline = start + timeout
    absolute_deadline = deadline + 5
    stdout_path = temp_capture_path("brain-design-worker-stdout-")
    stderr_path = temp_capture_path("brain-design-worker-stderr-")
    proc: subprocess.Popen[bytes] | None = None
    timed_out = False
    done_but_not_exited = False
    reason = ""
    done_grace_started: float | None = None
    killed_pids: list[int] = []
    kill_strategy = ""
    merged_env = os.environ.copy()
    merged_env["PYTHONDONTWRITEBYTECODE"] = "1"
    if env:
        merged_env.update(env)
    try:
        with stdout_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
            proc = subprocess.Popen(
                [str(part) for part in command],
                cwd=str(cwd),
                env=merged_env,
                stdin=subprocess.DEVNULL,
                stdout=stdout_handle,
                stderr=stderr_handle,
                **supervisor_creation_kwargs(),
            )
            while proc.poll() is None:
                now = time.monotonic()
                last_status = read_worker_status(status_path)
                if last_status == "done":
                    if done_grace_started is None:
                        done_grace_started = now
                    elif now - done_grace_started > 2:
                        timed_out = True
                        done_but_not_exited = True
                        reason = "worker_done_but_not_exited"
                        kill_result = supervisor_kill_worker(proc, started_process_group=True)
                        killed_pids = [int(pid) for pid in kill_result.get("killedPids", [])]
                        kill_strategy = str(kill_result.get("strategy", "supervisor-native"))
                        remaining_wait = max(0.0, min(1.0, absolute_deadline - time.monotonic()))
                        if remaining_wait > 0:
                            try:
                                proc.wait(timeout=remaining_wait)
                            except subprocess.TimeoutExpired:
                                pass
                        break
                else:
                    done_grace_started = None

                if now > deadline:
                    timed_out = True
                    reason = "worker_timeout"
                    kill_result = supervisor_kill_worker(proc, started_process_group=True)
                    killed_pids = [int(pid) for pid in kill_result.get("killedPids", [])]
                    kill_strategy = str(kill_result.get("strategy", "supervisor-native"))
                    remaining_wait = max(0.0, min(1.0, absolute_deadline - time.monotonic()))
                    try:
                        proc.wait(timeout=remaining_wait)
                    except subprocess.TimeoutExpired:
                        kill_result = supervisor_kill_worker(proc, started_process_group=True)
                        killed_pids = sorted(set(killed_pids + [int(pid) for pid in kill_result.get("killedPids", [])]))
                        kill_strategy = kill_strategy or str(kill_result.get("strategy", "supervisor-native"))
                    break
                if now > absolute_deadline:
                    timed_out = True
                    reason = "worker_absolute_deadline"
                    kill_result = supervisor_kill_worker(proc, started_process_group=True)
                    killed_pids = [int(pid) for pid in kill_result.get("killedPids", [])]
                    kill_strategy = str(kill_result.get("strategy", "supervisor-native"))
                    break
                time.sleep(0.05)
    except OSError as exc:
        duration = time.monotonic() - start
        stderr = str(exc)
        if not keep_output_on_failure:
            unlink_quietly(stdout_path)
            unlink_quietly(stderr_path)
        return WorkerProcessResult(
            ok=False,
            returncode=1,
            timedOut=False,
            duration=duration,
            stdout="",
            stderr=stderr,
            stdoutExcerpt="",
            stderrExcerpt=excerpt(stderr),
            killedPids=[],
            killStrategy="not-started",
            lastWorkerStatus=read_worker_status(status_path),
            statusPath=str(status_path or ""),
            stdoutPath=str(stdout_path),
            stderrPath=str(stderr_path),
            doneButNotExited=False,
            reason="not_started",
        )
    duration = time.monotonic() - start
    stdout = read_text_file(stdout_path)
    stderr = read_text_file(stderr_path)
    returncode = 124 if timed_out else (proc.returncode if proc is not None and proc.returncode is not None else 1)
    ok = (not timed_out) and returncode == 0
    if ok or not keep_output_on_failure:
        unlink_quietly(stdout_path)
        unlink_quietly(stderr_path)
    return WorkerProcessResult(
        ok=ok,
        returncode=returncode,
        timedOut=timed_out,
        duration=duration,
        stdout=stdout,
        stderr=stderr,
        stdoutExcerpt=excerpt(stdout),
        stderrExcerpt=excerpt(stderr),
        killedPids=sorted(set(killed_pids)),
        killStrategy=kill_strategy or ("none" if not timed_out else "unknown"),
        lastWorkerStatus=read_worker_status(status_path),
        statusPath=str(status_path or ""),
        stdoutPath=str(stdout_path),
        stderrPath=str(stderr_path),
        doneButNotExited=done_but_not_exited,
        reason=reason or ("ok" if ok else "worker_failed"),
    )


def check_deadline(deadline: float, phase: str) -> None:
    if time.monotonic() > deadline:
        raise AssertionError(f"Process utils worker exceeded max duration during {phase}.")


def install_posix_alarm(deadline_seconds: float) -> None:
    if os.name == "nt" or not hasattr(signal, "SIGALRM"):
        return

    def _alarm(_signum: int, _frame: object) -> None:
        raise TimeoutError("Process utils worker exceeded self deadline.")

    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(max(1, int(deadline_seconds)))


def clear_posix_alarm() -> None:
    if os.name != "nt" and hasattr(signal, "alarm"):
        signal.alarm(0)


def write_direct_nested_scripts(tmp: Path, invocation: PythonInvocation) -> Path:
    grandchild = tmp / "grandchild_sleep.py"
    child = tmp / "child_sleep.py"
    parent = tmp / "spawn_hanging_child.py"
    command_prefix = invocation.commandPrefix
    grandchild.write_text(
        textwrap.dedent(
            f"""
            import os
            import time
            from pathlib import Path

            tmp = Path({str(tmp)!r})
            (tmp / "grandchild.pid").write_text(str(os.getpid()), encoding="utf-8")
            (tmp / "grandchild.ready").write_text("ready", encoding="utf-8")
            time.sleep(999)
            """
        ).lstrip(),
        encoding="utf-8",
        newline="\n",
    )
    child.write_text(
        textwrap.dedent(
            f"""
            import os
            import subprocess
            import time
            from pathlib import Path

            tmp = Path({str(tmp)!r})
            command_prefix = {command_prefix!r}
            proc = subprocess.Popen(
                command_prefix + [str(tmp / "grandchild_sleep.py")],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if (tmp / "grandchild.ready").exists() and (tmp / "grandchild.pid").exists():
                    break
                time.sleep(0.05)
            (tmp / "child.pid").write_text(str(os.getpid()), encoding="utf-8")
            (tmp / "child.ready").write_text("ready", encoding="utf-8")
            time.sleep(999)
            """
        ).lstrip(),
        encoding="utf-8",
        newline="\n",
    )
    parent.write_text(
        textwrap.dedent(
            f"""
            import os
            import subprocess
            import time
            from pathlib import Path

            tmp = Path({str(tmp)!r})
            command_prefix = {command_prefix!r}
            proc = subprocess.Popen(
                command_prefix + [str(tmp / "child_sleep.py")],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                if (tmp / "child.ready").exists() and (tmp / "grandchild.ready").exists() and (tmp / "child.pid").exists() and (tmp / "grandchild.pid").exists():
                    break
                time.sleep(0.05)
            (tmp / "parent.pid").write_text(str(os.getpid()), encoding="utf-8")
            (tmp / "parent.ready").write_text("ready", encoding="utf-8")
            time.sleep(999)
            """
        ).lstrip(),
        encoding="utf-8",
        newline="\n",
    )
    return parent


def run_normal_command_test(base: Path, invocation: PythonInvocation, smoke: Smoke) -> None:
    write_worker_status("normal_command")
    print("[worker] normal command ...", flush=True)
    start = time.monotonic()
    normal = run_command(python_command(["-c", "print('ok-normal')"], invocation), cwd=base, timeout=5)
    smoke.normal_duration = time.monotonic() - start
    smoke.ok(normal.ok, "Normal command should succeed.")
    smoke.ok("ok-normal" in normal.stdout, "Normal command stdout missing.")
    smoke.ok(normal.pipeMode == "tempfile", "Normal command should use tempfile capture mode.")
    smoke.ok(normal.processCreationMode == "non-isolated", "Normal command should use non-isolated default process creation.")
    smoke.ok(normal.pythonExecutableUsed == invocation.executable, "Normal command should report Python executable used.")
    smoke.ok(normal.pythonFlagsUsed == invocation.flags, "Normal command should report Python flags used.")
    smoke.ok(normal.pythonInvocationMode == invocation.mode, "Normal command should report Python invocation mode.")
    print(f"[worker] normal command ... PASS in {smoke.normal_duration:.2f}s", flush=True)


def run_failed_command_test(base: Path, invocation: PythonInvocation, smoke: Smoke) -> None:
    write_worker_status("failed_command")
    print("[worker] failed command ...", flush=True)
    failed = run_command(
        python_command(["-c", "import sys; print('bad-stderr', file=sys.stderr); sys.exit(7)"], invocation),
        cwd=base,
        timeout=5,
    )
    smoke.ok(not failed.ok and failed.returncode == 7, "Failed command should return non-zero.")
    smoke.ok("bad-stderr" in failed.stderrExcerpt, "Failed command stderr excerpt missing.")
    smoke.ok(failed.pipeMode == "tempfile", "Failed command should use tempfile capture mode.")
    print("[worker] failed command ... PASS", flush=True)


def run_simple_timeout_test(args: argparse.Namespace, base: Path, invocation: PythonInvocation, smoke: Smoke) -> None:
    write_worker_status("simple_timeout")
    print("[worker] simple timeout ...", flush=True)
    timeout = min(args.simple_timeout, args.timeout, 4)
    start = time.monotonic()
    timed = run_command(
        python_command(["-c", "import time; time.sleep(999)"], invocation),
        cwd=base,
        timeout=timeout,
    )
    smoke.simple_timeout_duration = time.monotonic() - start
    smoke.ok(timed.timedOut, "Simple hanging command should time out.")
    smoke.ok(timed.pipeMode == "tempfile", "Simple timeout should use tempfile capture mode.")
    smoke.ok(timed.processCreationMode == "non-isolated", "Simple timeout should use non-isolated default process creation.")
    smoke.ok(smoke.simple_timeout_duration < timeout + 5, f"Simple timeout took too long: {smoke.simple_timeout_duration:.2f}s.")
    smoke.ok(bool(timed.killStrategy), "Simple timeout result missing kill strategy.")
    print(
        f"[worker] simple timeout ... PASS in {smoke.simple_timeout_duration:.2f}s "
        f"(kill strategy: {timed.killStrategy})",
        flush=True,
    )


def run_direct_nested_kill_test(args: argparse.Namespace, invocation: PythonInvocation, smoke: Smoke) -> None:
    write_worker_status("direct_nested_kill")
    print("[worker] direct nested kill ...", flush=True)
    start = time.monotonic()
    proc: subprocess.Popen[bytes] | None = None
    with tempfile.TemporaryDirectory(prefix="brain-design-direct-kill-") as tmp_name:
        tmp = Path(tmp_name)
        parent_script = write_direct_nested_scripts(tmp, invocation)
        try:
            proc = subprocess.Popen(
                python_command([str(parent_script)], invocation),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            ready_paths = [
                tmp / "parent.ready",
                tmp / "child.ready",
                tmp / "grandchild.ready",
                tmp / "parent.pid",
                tmp / "child.pid",
                tmp / "grandchild.pid",
            ]
            ready = wait_for_files(ready_paths, timeout=args.setup_timeout)
            parent_ready = (tmp / "parent.ready").exists()
            child_ready = (tmp / "child.ready").exists()
            grandchild_ready = (tmp / "grandchild.ready").exists()
            parent_pid = read_pid(tmp / "parent.pid")
            child_pid = read_pid(tmp / "child.pid")
            grandchild_pid = read_pid(tmp / "grandchild.pid")
            print(f"  ready: parent={str(parent_ready).lower()} child={str(child_ready).lower()} grandchild={str(grandchild_ready).lower()}", flush=True)
            print(f"  pids: parent={parent_pid or (proc.pid if proc else 0)} child={child_pid} grandchild={grandchild_pid}", flush=True)
            smoke.ok(ready, "Direct nested kill setup did not reach ready state.")
            smoke.ok(proc.pid > 0, "Direct nested parent PID was not recorded.")
            smoke.ok(parent_pid > 0, "Direct nested parent script PID was not recorded.")
            smoke.ok(child_pid > 0, "Direct nested child PID was not recorded.")
            smoke.ok(grandchild_pid > 0, "Direct nested grandchild PID was not recorded.")
            parent_active_before = process_liveness(parent_pid).get("alive")
            child_active_before = process_liveness(child_pid).get("alive")
            grandchild_active_before = process_liveness(grandchild_pid).get("alive")
            smoke.ok(bool(parent_active_before), "Direct nested parent was not active before kill.")
            smoke.ok(bool(child_active_before), "Direct nested child was not active before kill.")
            smoke.ok(bool(grandchild_active_before), "Direct nested grandchild was not active before kill.")
            killed_pids, kill_strategy = kill_process_tree(proc)
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                more_pids, more_strategy = kill_process_tree(proc)
                killed_pids = sorted(set(killed_pids + more_pids))
                kill_strategy = kill_strategy or more_strategy
                try:
                    proc.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    pass
            time.sleep(0.8)
            parent_liveness = process_liveness(parent_pid)
            child_liveness = process_liveness(child_pid)
            grandchild_liveness = process_liveness(grandchild_pid)
            print(f"  kill strategy: {kill_strategy}; killed pids: {killed_pids}", flush=True)
            print(f"  parent active={str(parent_liveness.get('alive')).lower()} state={parent_liveness.get('state') or 'missing'} source={parent_liveness.get('source')}", flush=True)
            print(f"  child active={str(child_liveness.get('alive')).lower()} state={child_liveness.get('state') or 'missing'} source={child_liveness.get('source')}", flush=True)
            print(f"  grandchild active={str(grandchild_liveness.get('alive')).lower()} state={grandchild_liveness.get('state') or 'missing'} source={grandchild_liveness.get('source')}", flush=True)
            smoke.ok(bool(kill_strategy), "Direct nested kill result missing kill strategy.")
            smoke.ok(not parent_liveness.get("alive"), f"Parent process still active after direct kill: {parent_liveness}.")
            smoke.ok(not child_liveness.get("alive"), f"Child process still active after direct kill: {child_liveness}.")
            smoke.ok(not grandchild_liveness.get("alive"), f"Grandchild process still active after direct kill: {grandchild_liveness}.")
        finally:
            if proc is not None and proc.poll() is None:
                kill_process_tree(proc)
    smoke.direct_kill_duration = time.monotonic() - start
    print(f"[worker] direct nested kill ... PASS in {smoke.direct_kill_duration:.2f}s", flush=True)


def run_optional_nested_run_command_test(args: argparse.Namespace, base: Path, invocation: PythonInvocation, smoke: Smoke) -> None:
    write_worker_status("optional_nested_run_command")
    print("[worker] optional nested run_command timeout ...", flush=True)
    with tempfile.TemporaryDirectory(prefix="brain-design-nested-run-command-") as tmp_name:
        tmp = Path(tmp_name)
        parent_script = write_direct_nested_scripts(tmp, invocation)
        timeout = max(args.timeout, args.setup_timeout + 5)
        timed = run_command(python_command([str(parent_script)], invocation), cwd=base, timeout=timeout)
        smoke.ok(timed.timedOut, "Optional nested run_command should time out.")
        smoke.ok(bool(timed.killStrategy), "Optional nested run_command missing kill strategy.")
        print(f"[worker] optional nested run_command timeout ... PASS (kill strategy: {timed.killStrategy})", flush=True)


def run_worker_once(args: argparse.Namespace) -> int:
    start = time.monotonic()
    deadline = start + args.worker_max_duration
    install_posix_alarm(args.worker_max_duration + 1)
    smoke = Smoke()
    base = root()
    try:
        write_worker_status("started")
        invocation = resolve_python_invocation()
        write_worker_status("resolved_invocation")
        if args.verbose:
            print(f"Worker hard-exit mode: {'yes' if worker_hard_exit_enabled() else 'no'}", flush=True)
        print_resolver_context(invocation, verbose=args.verbose, probe_all=False)

        check_deadline(deadline, "normal command")
        run_normal_command_test(base, invocation, smoke)

        check_deadline(deadline, "failed command")
        run_failed_command_test(base, invocation, smoke)

        check_deadline(deadline, "simple timeout")
        run_simple_timeout_test(args, base, invocation, smoke)

        check_deadline(deadline, "direct nested kill")
        run_direct_nested_kill_test(args, invocation, smoke)

        if args.include_nested_run_command:
            check_deadline(deadline, "optional nested run_command timeout")
            run_optional_nested_run_command_test(args, base, invocation, smoke)

        check_deadline(deadline, "worker completion")
        write_worker_status("done")
        total = time.monotonic() - start
        print(
            "PASS: Process utils worker "
            f"({smoke.checks} checks) in {total:.2f}s; "
            f"normal={smoke.normal_duration:.2f}s simpleTimeout={smoke.simple_timeout_duration:.2f}s directKill={smoke.direct_kill_duration:.2f}s",
            flush=True,
        )
        return 0
    finally:
        clear_posix_alarm()


def supervisor_worker_env(invocation: PythonInvocation) -> dict[str, str]:
    return {
        "BRAIN_DESIGN_RESOLVED_PYTHON": invocation.executable,
        "BRAIN_DESIGN_RESOLVED_PYTHON_FLAGS": json.dumps(invocation.flags),
        "BRAIN_DESIGN_RESOLVED_PYTHON_MODE": invocation.mode,
        "BRAIN_DESIGN_RESOLVED_PYTHON_SOURCE": invocation.source,
        "BRAIN_DESIGN_SKIP_PYTHON_PROBES": "1",
        "BRAIN_DESIGN_WORKER_HARD_EXIT": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def make_worker_status_path(iteration: int, deterministic: bool) -> Path:
    if deterministic:
        base = Path(tempfile.gettempdir()) / "brain-design-process-smoke-workers"
        base.mkdir(parents=True, exist_ok=True)
        return base / f"worker-{os.getpid()}-{iteration}-{int(time.time() * 1000)}.status"
    return temp_capture_path(f"brain-design-worker-{iteration}-status-")


def run_supervisor(args: argparse.Namespace) -> int:
    start = time.monotonic()
    deadline = start + args.max_duration
    base = root()
    invocation = resolve_python_invocation(stability_passes=2, force_probe=True)
    print_resolver_context(invocation, verbose=args.verbose, probe_all=True)
    repeat = max(1, args.repeat)
    worker_successes = 0
    worker_env = supervisor_worker_env(invocation)

    for iteration in range(1, repeat + 1):
        remaining = deadline - time.monotonic()
        if remaining <= 1:
            print(f"FAIL: Process utils smoke exceeded max duration at iteration {iteration}", file=sys.stderr, flush=True)
            return 1
        worker_timeout = min(args.timeout + 20, args.worker_max_duration + 5, remaining)
        if worker_timeout < 5:
            print(f"FAIL: Not enough global time remains for worker {iteration}", file=sys.stderr, flush=True)
            return 1
        command = [
            *python_command([str(Path(__file__).resolve())], invocation),
            "--worker-once",
            "--timeout",
            str(args.timeout),
            "--setup-timeout",
            str(args.setup_timeout),
            "--simple-timeout",
            str(args.simple_timeout),
            "--worker-max-duration",
            str(min(args.worker_max_duration, max(5, worker_timeout - 1))),
        ]
        if args.include_nested_run_command:
            command.append("--include-nested-run-command")
        if args.verbose:
            command.append("--verbose")
        print(f"[{iteration}/{repeat}] worker ...", flush=True)
        print(f"  worker command: {' '.join(command)}", flush=True)
        worker_status_path = make_worker_status_path(iteration, args.deterministic_repeat)
        worker_iteration_env = dict(worker_env)
        worker_iteration_env["BRAIN_DESIGN_WORKER_STATUS_PATH"] = str(worker_status_path)
        if args.deterministic_repeat or args.verbose:
            print(f"  worker status path: {worker_status_path}", flush=True)
        result = run_worker_subprocess_direct(
            command,
            timeout=worker_timeout,
            cwd=base,
            env=worker_iteration_env,
            status_path=worker_status_path,
            keep_output_on_failure=args.deterministic_repeat and not args.cleanup_on_fail,
            verbose=args.verbose,
        )
        if result.ok:
            worker_successes += 1
            print(f"[{iteration}/{repeat}] worker PASS in {result.duration:.2f}s", flush=True)
            if args.verbose and result.stdoutExcerpt:
                print(result.stdoutExcerpt, flush=True)
            unlink_quietly(worker_status_path)
            continue
        status = "TIMEOUT" if result.timedOut else "FAIL"
        if result.timedOut:
            print(
                f"Worker {iteration} timed out after {worker_timeout:.2f} seconds; "
                f"reason={result.reason}; lastWorkerStatus={result.lastWorkerStatus or '<none>'}",
                file=sys.stderr,
                flush=True,
            )
        print(f"[{iteration}/{repeat}] worker {status} in {result.duration:.2f}s", file=sys.stderr, flush=True)
        print(f"  kill strategy: {result.killStrategy}; killed pids: {result.killedPids}", file=sys.stderr, flush=True)
        print(f"  worker status path: {result.statusPath or worker_status_path}", file=sys.stderr, flush=True)
        print(f"  lastWorkerStatus={result.lastWorkerStatus or '<none>'}", file=sys.stderr, flush=True)
        print(f"  reason={result.reason}; doneButNotExited={str(result.doneButNotExited).lower()}", file=sys.stderr, flush=True)
        if args.deterministic_repeat and not args.cleanup_on_fail:
            print(f"  worker stdout path: {result.stdoutPath}", file=sys.stderr, flush=True)
            print(f"  worker stderr path: {result.stderrPath}", file=sys.stderr, flush=True)
        if result.stdoutExcerpt:
            print(f"  stdout excerpt:\n{excerpt(result.stdoutExcerpt, 2000)}", file=sys.stderr, flush=True)
        if result.stderrExcerpt:
            print(f"  stderr excerpt:\n{excerpt(result.stderrExcerpt, 2000)}", file=sys.stderr, flush=True)
        if args.cleanup_on_fail:
            unlink_quietly(worker_status_path)
        return 1

    total = time.monotonic() - start
    if total > args.max_duration:
        print(f"FAIL: Process utils smoke exceeded max duration {args.max_duration}s: {total:.2f}s", file=sys.stderr, flush=True)
        return 1
    print(f"PASS: Process utils smoke supervisor ({worker_successes}/{repeat} workers) in {total:.2f}s", flush=True)
    return 0


def main() -> int:
    args = parse_args()
    if args.worker_once:
        try:
            code = run_worker_once(args)
        except Exception as exc:
            print(f"FAIL: {exc}", file=sys.stderr, flush=True)
            code = 1
        sys.stdout.flush()
        sys.stderr.flush()
        if worker_hard_exit_enabled():
            os._exit(code)
        return code
    try:
        return run_supervisor(args)
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
