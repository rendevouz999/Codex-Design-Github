#!/usr/bin/env python
"""Bounded subprocess helpers for Brain Design release/runtime checks."""

from __future__ import annotations

import os
import json
import signal
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

try:  # pragma: no cover - depends on local environment
    import psutil  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    psutil = None


@dataclass
class ProcessResult:
    ok: bool
    returncode: int
    timedOut: bool
    command: str
    duration: float
    stdout: str
    stderr: str
    stdoutExcerpt: str
    stderrExcerpt: str
    killedPids: list[int]
    killStrategy: str
    pipeMode: str
    waitTimedOut: bool
    processCreationMode: str
    pythonExecutableUsed: str
    pythonFlagsUsed: list[str]
    pythonInvocationMode: str
    pythonInvocationSource: str
    effectiveTimeout: float
    pollInterval: float


@dataclass(frozen=True)
class PythonInvocation:
    executable: str
    flags: list[str]
    commandPrefix: list[str]
    mode: str
    source: str
    probeCommand: list[str]


def format_command(cmd: Sequence[str | os.PathLike[str]]) -> str:
    return " ".join(str(part) for part in cmd)


def excerpt(text: str, max_chars: int = 4000) -> str:
    value = text or ""
    if len(value) <= max_chars:
        return value
    return value[-max_chars:]


def _read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _unlink_quietly(path: Path) -> None:
    try:
        path.unlink()
    except OSError:
        pass


def _temp_capture_path(prefix: str) -> Path:
    handle = tempfile.NamedTemporaryFile(prefix=prefix, suffix=".log", delete=False)
    path = Path(handle.name)
    handle.close()
    return path


_PYTHON_INVOCATION_CACHE: dict[tuple[str, str, str], PythonInvocation] = {}


_PYTHON_MODES: tuple[tuple[str, list[str]], ...] = (
    ("plain", []),
    ("no_site", ["-S"]),
    ("isolated_no_site", ["-I", "-S"]),
)


def _parse_invocation_flags(raw: str) -> list[str]:
    if not raw.strip():
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except Exception:
        pass
    return [part for part in raw.split(os.pathsep) if part]


def python_invocation_from_env() -> PythonInvocation | None:
    """Return a supervisor-resolved invocation handoff when present."""

    executable = os.environ.get("BRAIN_DESIGN_RESOLVED_PYTHON", "").strip()
    if not executable:
        return None
    flags = _parse_invocation_flags(os.environ.get("BRAIN_DESIGN_RESOLVED_PYTHON_FLAGS", ""))
    mode = os.environ.get("BRAIN_DESIGN_RESOLVED_PYTHON_MODE", "").strip() or (
        "no_site" if flags == ["-S"] else "isolated_no_site" if flags == ["-I", "-S"] else "plain"
    )
    source = os.environ.get("BRAIN_DESIGN_RESOLVED_PYTHON_SOURCE", "").strip() or "supervisor_env"
    command_prefix = [executable, *flags]
    return PythonInvocation(
        executable=executable,
        flags=flags,
        commandPrefix=command_prefix,
        mode=mode,
        source=source,
        probeCommand=[*command_prefix, "-c", "print('BD_PY_OK')"],
    )


def _probe_timeout(default: float = 8) -> float:
    raw = os.environ.get("BRAIN_DESIGN_PYTHON_PROBE_TIMEOUT", "").strip()
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return max(1.0, value)


def _creation_kwargs(isolate_process_group: bool = False) -> dict[str, object]:
    if not isolate_process_group:
        return {}
    if os.name == "nt":
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def _creation_mode(isolate_process_group: bool = False) -> str:
    return "isolated" if isolate_process_group else "non-isolated"


def _resolve_candidate_path(candidate: str) -> str | None:
    path = Path(candidate)
    if path.is_absolute():
        return str(path) if path.exists() else None
    resolved = shutil.which(candidate)
    return str(resolved) if resolved else None


def _current_python_is_valid() -> bool:
    if sys.version_info.major != 3 or not sys.executable:
        return False
    executable = Path(sys.executable)
    return (not executable.is_absolute()) or executable.exists()


def _python_command_details(cmd: Sequence[str | os.PathLike[str]]) -> tuple[str, list[str], str]:
    if not cmd:
        return "", [], ""
    first = str(cmd[0])
    name = Path(first).name.lower()
    if name.startswith("python") or name in {"py", "py.exe"}:
        flags: list[str] = []
        for part in [str(value) for value in cmd[1:]]:
            if part in {"-S", "-I"}:
                flags.append(part)
                continue
            break
        if flags == ["-S"]:
            mode = "no_site"
        elif flags == ["-I", "-S"]:
            mode = "isolated_no_site"
        elif flags:
            mode = "custom"
        else:
            mode = "plain"
        return first, flags, mode
    return "", [], ""


def python_child_exec_works(candidate: str, timeout: float = 5.0, flags: Sequence[str] | None = None) -> bool:
    """Return whether a Python executable can safely run as a child process."""

    runtime_flags = [str(flag) for flag in (flags or [])]
    stdout_path = _temp_capture_path("brain-design-python-probe-stdout-")
    stderr_path = _temp_capture_path("brain-design-python-probe-stderr-")
    proc: subprocess.Popen[bytes] | None = None
    start = time.monotonic()
    try:
        with stdout_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
            proc = subprocess.Popen(
                [candidate, *runtime_flags, "-c", "print('BD_PY_OK')"],
                stdin=subprocess.DEVNULL,
                stdout=stdout_handle,
                stderr=stderr_handle,
            )
            while proc.poll() is None:
                if time.monotonic() - start > timeout:
                    kill_process_tree(proc)
                    try:
                        proc.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        kill_process_tree(proc)
                    return False
                time.sleep(0.05)
        stdout = _read_text_file(stdout_path)
    except OSError:
        return False
    finally:
        _unlink_quietly(stdout_path)
        _unlink_quietly(stderr_path)
    return proc is not None and proc.returncode == 0 and "BD_PY_OK" in stdout


def _candidate_python_sources(cli_executable: str | os.PathLike[str] | None = None) -> list[tuple[str, str]]:
    env_value = os.environ.get("BRAIN_DESIGN_PYTHON", "").strip()
    if env_value:
        return [("env", env_value)]
    candidates: list[tuple[str, str]] = []
    if cli_executable:
        candidates.append(("cli", str(cli_executable)))
    candidates.extend(
        [
            ("sys_executable", sys.executable),
            ("python3", "python3"),
            ("python", "python"),
        ]
    )
    result: list[tuple[str, str]] = []
    seen: set[str] = set()
    for source, candidate in candidates:
        if not candidate:
            continue
        normalized = candidate.lower() if os.name == "nt" else candidate
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append((source, candidate))
    return result


def _probe_python_invocation(candidate: str, source: str, timeout: float, stability_passes: int = 1) -> tuple[PythonInvocation | None, list[str]]:
    resolved = _resolve_candidate_path(candidate)
    if not resolved:
        return None, [f"{source} {candidate}: not found"]
    failures: list[str] = []
    for mode, flags in _PYTHON_MODES:
        probe_command = [resolved, *flags, "-c", "print('BD_PY_OK')"]
        passed = True
        for pass_index in range(max(1, stability_passes)):
            if not python_child_exec_works(resolved, timeout=timeout, flags=flags):
                failures.append(f"{source} {resolved} {mode}: failed exact child probe pass {pass_index + 1}/{max(1, stability_passes)}")
                passed = False
                break
        if passed:
            return (
                PythonInvocation(
                    executable=resolved,
                    flags=list(flags),
                    commandPrefix=[resolved, *flags],
                    mode=mode,
                    source=source,
                    probeCommand=probe_command,
                ),
                failures,
            )
    return None, failures


def resolve_python_invocation(
    cli_executable: str | os.PathLike[str] | None = None,
    timeout: float | None = None,
    stability_passes: int = 1,
    force_probe: bool = False,
) -> PythonInvocation:
    """Resolve the Python executable and flags that runtime commands must use."""

    if not force_probe:
        handed_off = python_invocation_from_env()
        if handed_off is not None:
            return handed_off
    probe_timeout = _probe_timeout() if timeout is None else timeout
    env_value = os.environ.get("BRAIN_DESIGN_PYTHON", "").strip()
    cli_value = str(cli_executable) if cli_executable else ""
    cache_key = (env_value, cli_value, str(max(1, stability_passes)))
    if cache_key in _PYTHON_INVOCATION_CACHE:
        return _PYTHON_INVOCATION_CACHE[cache_key]
    failures: list[str] = []
    for source, candidate in _candidate_python_sources(cli_executable):
        if source == "sys_executable" and not _current_python_is_valid():
            failures.append(f"sys.executable {sys.executable or '<empty>'}: invalid current Python 3 executable")
            continue
        invocation, probe_failures = _probe_python_invocation(candidate, source, probe_timeout, stability_passes=max(1, stability_passes))
        failures.extend(probe_failures)
        if invocation is not None:
            _PYTHON_INVOCATION_CACHE[cache_key] = invocation
            return invocation
        if source == "env":
            detail = "; ".join(failures) if failures else f"{candidate}: no passing invocation mode"
            raise RuntimeError(f"BRAIN_DESIGN_PYTHON is set but no Python invocation mode works: {detail}")
    detail = "; ".join(failures) if failures else "no candidates"
    raise RuntimeError(f"No working Python invocation found for Brain Design subprocess checks. Tried: {detail}")


def resolve_python_executable(cli_executable: str | os.PathLike[str] | None = None, timeout: float | None = None) -> str:
    """Backward-compatible executable-only resolver."""

    return resolve_python_invocation(cli_executable=cli_executable, timeout=timeout).executable


def python_command(args: Sequence[str | os.PathLike[str]], invocation: PythonInvocation | None = None) -> list[str]:
    """Build a Python command using the resolved executable and runtime flags."""

    selected = invocation or resolve_python_invocation()
    return [*selected.commandPrefix, *[str(part) for part in args]]


def process_liveness(pid: int) -> dict[str, object]:
    """Return zombie-aware process liveness information."""

    info: dict[str, object] = {
        "pid": pid,
        "exists": False,
        "alive": False,
        "state": "",
        "isZombie": False,
        "source": "none",
    }
    if pid <= 0:
        return info

    if os.name != "nt":
        proc_status = Path("/proc") / str(pid) / "status"
        if proc_status.exists():
            try:
                for line in proc_status.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if line.startswith("State:"):
                        state = line.split(":", 1)[1].strip()
                        is_zombie = state.upper().startswith("Z") or "zombie" in state.lower()
                        info.update({"exists": True, "alive": not is_zombie, "state": state, "isZombie": is_zombie, "source": "procfs-status"})
                        return info
            except PermissionError:
                info.update({"exists": True, "alive": True, "state": "permission-denied", "isZombie": False, "source": "procfs-status"})
                return info
            except Exception:
                pass

        proc_stat = Path("/proc") / str(pid) / "stat"
        if proc_stat.exists():
            try:
                stat = proc_stat.read_text(encoding="utf-8", errors="ignore")
                tail = stat.rsplit(")", 1)[1].strip().split()
                state = tail[0] if tail else ""
                is_zombie = state.upper() == "Z"
                info.update({"exists": True, "alive": not is_zombie, "state": state, "isZombie": is_zombie, "source": "procfs-stat"})
                return info
            except PermissionError:
                info.update({"exists": True, "alive": True, "state": "permission-denied", "isZombie": False, "source": "procfs-stat"})
                return info
            except Exception:
                pass

    if psutil is not None:
        try:
            process = psutil.Process(pid)
            status = process.status()
            is_zombie = status == getattr(psutil, "STATUS_ZOMBIE", "zombie") or str(status).lower() == "zombie"
            info.update({"exists": True, "alive": not is_zombie, "state": str(status), "isZombie": is_zombie, "source": "psutil"})
            return info
        except Exception as exc:
            if exc.__class__.__name__ == "NoSuchProcess":
                return info
            if exc.__class__.__name__ == "AccessDenied":
                info.update({"exists": True, "alive": True, "state": "permission-denied", "isZombie": False, "source": "psutil"})
                return info

    if os.name == "nt":
        stdout_path = _temp_capture_path("brain-design-tasklist-stdout-")
        proc: subprocess.Popen[bytes] | None = None
        try:
            with stdout_path.open("wb") as stdout_handle:
                proc = subprocess.Popen(
                    ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                    stdin=subprocess.DEVNULL,
                    stdout=stdout_handle,
                    stderr=subprocess.DEVNULL,
                )
                started = time.monotonic()
                while proc.poll() is None:
                    if time.monotonic() - started > 3:
                        try:
                            proc.kill()
                        except OSError:
                            pass
                        break
                    time.sleep(0.05)
            output = _read_text_file(stdout_path)
            alive = str(pid) in output and "No tasks" not in output
            info.update({"exists": alive, "alive": alive, "state": "running" if alive else "", "isZombie": False, "source": "tasklist"})
            return info
        except Exception:
            pass
        finally:
            _unlink_quietly(stdout_path)

    proc_status = Path("/proc") / str(pid) / "status"
    if proc_status.exists():
        try:
            for line in proc_status.read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.startswith("State:"):
                    state = line.split(":", 1)[1].strip()
                    is_zombie = state.upper().startswith("Z") or "zombie" in state.lower()
                    info.update({"exists": True, "alive": not is_zombie, "state": state, "isZombie": is_zombie, "source": "procfs-status"})
                    return info
        except PermissionError:
            info.update({"exists": True, "alive": True, "state": "permission-denied", "isZombie": False, "source": "procfs-status"})
            return info
        except Exception:
            pass

    proc_stat = Path("/proc") / str(pid) / "stat"
    if proc_stat.exists():
        try:
            stat = proc_stat.read_text(encoding="utf-8", errors="ignore")
            tail = stat.rsplit(")", 1)[1].strip().split()
            state = tail[0] if tail else ""
            is_zombie = state.upper() == "Z"
            info.update({"exists": True, "alive": not is_zombie, "state": state, "isZombie": is_zombie, "source": "procfs-stat"})
            return info
        except PermissionError:
            info.update({"exists": True, "alive": True, "state": "permission-denied", "isZombie": False, "source": "procfs-stat"})
            return info
        except Exception:
            pass

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return info
    except PermissionError:
        info.update({"exists": True, "alive": True, "state": "permission-denied", "isZombie": False, "source": "kill0"})
        return info
    info.update({"exists": True, "alive": True, "state": "unknown", "isZombie": False, "source": "kill0"})
    return info


def _procfs_descendants(pid: int) -> list[int]:
    children: dict[int, list[int]] = {}
    proc_root = Path("/proc")
    if not proc_root.exists():
        return []
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


def kill_process_tree(proc: subprocess.Popen[bytes]) -> tuple[list[int], str]:
    """Best-effort full process tree kill for release checks."""

    if proc.poll() is not None:
        return [], "already-exited"

    killed: list[int] = []
    if psutil is not None:
        try:
            parent = psutil.Process(proc.pid)
            descendants = parent.children(recursive=True)
            for child in reversed(descendants):
                try:
                    killed.append(int(child.pid))
                    child.kill()
                except Exception:
                    pass
            try:
                killed.append(int(parent.pid))
                parent.kill()
            except Exception:
                pass
            gone, alive = psutil.wait_procs([*descendants, parent], timeout=2)
            for process in alive:
                try:
                    killed.append(int(process.pid))
                    process.kill()
                except Exception:
                    pass
            return sorted(set(killed)), "psutil"
        except Exception:
            pass

    if os.name == "nt":
        try:
            taskkill = subprocess.Popen(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            started = time.monotonic()
            while taskkill.poll() is None:
                if time.monotonic() - started > 3:
                    try:
                        taskkill.kill()
                    except OSError:
                        pass
                    break
                time.sleep(0.05)
            killed.append(proc.pid)
        except Exception:
            pass
        try:
            proc.kill()
            killed.append(proc.pid)
        except Exception:
            pass
        return sorted(set(killed)), "taskkill"

    descendants = _procfs_descendants(proc.pid)
    if descendants:
        for child_pid in sorted(descendants, reverse=True):
            try:
                os.kill(child_pid, signal.SIGKILL)
                killed.append(child_pid)
            except Exception:
                pass
        try:
            os.kill(proc.pid, signal.SIGKILL)
            killed.append(proc.pid)
        except Exception:
            pass
        return sorted(set(killed)), "procfs"
    try:
        proc.kill()
        killed.append(proc.pid)
        return sorted(set(killed)), "parent-only"
    except Exception:
        pass
    try:
        if os.getpgid(proc.pid) == proc.pid:
            os.killpg(proc.pid, signal.SIGKILL)
            killed.append(proc.pid)
            return sorted(set(killed)), "process-group"
    except Exception:
        try:
            proc.kill()
            killed.append(proc.pid)
        except Exception:
            pass
    return sorted(set(killed)), "parent-only-fallback"


def run_command(
    cmd: Sequence[str | os.PathLike[str]],
    *,
    cwd: str | Path,
    timeout: float,
    env: dict[str, str] | None = None,
    label: str = "",
    verbose: bool = False,
    isolate_process_group: bool = False,
) -> ProcessResult:
    """Run a command with process-tree timeout and captured output."""

    start = time.monotonic()
    command_text = format_command(cmd)
    creation_mode = _creation_mode(isolate_process_group)
    poll_interval = 0.05
    python_executable_used, python_flags_used, python_invocation_mode = _python_command_details(cmd)
    python_invocation_source = ""
    try:
        selected = resolve_python_invocation()
        if [str(part) for part in cmd[: len(selected.commandPrefix)]] == selected.commandPrefix:
            python_invocation_mode = selected.mode
            python_invocation_source = selected.source
    except Exception:
        pass
    merged_env = os.environ.copy()
    merged_env["PYTHONDONTWRITEBYTECODE"] = "1"
    if env:
        merged_env.update(env)
    if label:
        print(f"{label} ...", flush=True)
        print(f"  command: {command_text}", flush=True)

    stdout_path = _temp_capture_path("brain-design-run-stdout-")
    stderr_path = _temp_capture_path("brain-design-run-stderr-")
    timed_out = False
    killed_pids: list[int] = []
    kill_strategy = ""
    wait_timed_out = False
    proc: subprocess.Popen[bytes] | None = None
    try:
        with stdout_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
            proc = subprocess.Popen(
                [str(part) for part in cmd],
                cwd=str(cwd),
                env=merged_env,
                stdin=subprocess.DEVNULL,
                stdout=stdout_handle,
                stderr=stderr_handle,
                **_creation_kwargs(isolate_process_group),
            )
            while True:
                if proc.poll() is not None:
                    break
                if time.monotonic() - start > timeout:
                    timed_out = True
                    killed_pids, kill_strategy = kill_process_tree(proc)
                    try:
                        proc.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        wait_timed_out = True
                        more_pids, more_strategy = kill_process_tree(proc)
                        killed_pids = sorted(set(killed_pids + more_pids))
                        kill_strategy = kill_strategy or more_strategy
                        try:
                            proc.wait(timeout=1)
                        except subprocess.TimeoutExpired:
                            pass
                    break
                time.sleep(poll_interval)
    except OSError as exc:
        duration = time.monotonic() - start
        stderr = str(exc)
        _unlink_quietly(stdout_path)
        _unlink_quietly(stderr_path)
        return ProcessResult(
            ok=False,
            returncode=1,
            timedOut=False,
            command=command_text,
            duration=duration,
            stdout="",
            stderr=stderr,
            stdoutExcerpt="",
            stderrExcerpt=excerpt(stderr),
            killedPids=[],
            killStrategy="not-started",
            pipeMode="tempfile",
            waitTimedOut=False,
            processCreationMode=creation_mode,
            pythonExecutableUsed=python_executable_used,
            pythonFlagsUsed=python_flags_used,
            pythonInvocationMode=python_invocation_mode,
            pythonInvocationSource=python_invocation_source,
            effectiveTimeout=timeout,
            pollInterval=poll_interval,
        )
    duration = time.monotonic() - start
    stdout = _read_text_file(stdout_path)
    stderr = _read_text_file(stderr_path)
    _unlink_quietly(stdout_path)
    _unlink_quietly(stderr_path)
    returncode = 124 if timed_out else (proc.returncode if proc is not None and proc.returncode is not None else 1)
    ok = (not timed_out) and returncode == 0

    result = ProcessResult(
        ok=ok,
        returncode=returncode,
        timedOut=timed_out,
        command=command_text,
        duration=duration,
        stdout=stdout,
        stderr=stderr,
        stdoutExcerpt=excerpt(stdout),
        stderrExcerpt=excerpt(stderr),
        killedPids=killed_pids,
        killStrategy=kill_strategy or ("none" if not timed_out else "unknown"),
        pipeMode="tempfile",
        waitTimedOut=wait_timed_out,
        processCreationMode=creation_mode,
        pythonExecutableUsed=python_executable_used,
        pythonFlagsUsed=python_flags_used,
        pythonInvocationMode=python_invocation_mode,
        pythonInvocationSource=python_invocation_source,
        effectiveTimeout=timeout,
        pollInterval=poll_interval,
    )

    if label:
        if result.ok:
            print(f"{label} PASS in {duration:.2f}s", flush=True)
        elif result.timedOut:
            print(f"{label} TIMEOUT after {timeout}s in {duration:.2f}s", flush=True)
            print(f"  timed out command: {command_text}", flush=True)
            print(f"  kill strategy: {result.killStrategy}; killed pids: {result.killedPids}", flush=True)
            if result.waitTimedOut:
                print("  bounded wait after kill timed out; returning best-effort timeout result.", flush=True)
            if result.stdoutExcerpt:
                print(f"  stdout excerpt:\n{result.stdoutExcerpt}", flush=True)
            if result.stderrExcerpt:
                print(f"  stderr excerpt:\n{result.stderrExcerpt}", flush=True)
        else:
            print(f"{label} FAIL in {duration:.2f}s (code {returncode})", flush=True)
            if result.stdoutExcerpt:
                print(f"  stdout excerpt:\n{result.stdoutExcerpt}", flush=True)
            if result.stderrExcerpt:
                print(f"  stderr excerpt:\n{result.stderrExcerpt}", flush=True)
    elif verbose:
        if stdout:
            print(stdout, flush=True)
        if stderr:
            print(stderr, file=sys.stderr, flush=True)
    return result
