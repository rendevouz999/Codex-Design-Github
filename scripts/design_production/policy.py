"""Executable boundaries; the model never chooses filesystem paths or executables."""
from __future__ import annotations

import hashlib
import json
import os
import re
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / ".design-brain/runtime/state/design-production"
TOOLS = {"read_input", "discover_capabilities", "write_unit", "build_artifact", "render_preview", "technical_qa"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def task_id(task) -> str:
    key = [task.parent_request_id, task.stage, task.artifact_type, [x.id for x in task.units], task.revision]
    return "design-" + canonical_hash(key)[:32]


def within(path: Path, base: Path) -> Path:
    path = path.absolute()
    base = base.absolute()
    if not path.is_relative_to(base) or path == base:
        raise ValueError("Path escapes authorized boundary")
    # Reject junctions/reparse points as well as symlinks, including existing ancestors.
    for item in [base, *base.parents, path, *path.parents]:
        if item.exists() or item.is_symlink():
            stat = item.lstat()
            if item.is_symlink() or getattr(stat, "st_file_attributes", 0) & 0x400:
                raise ValueError("Symlinks and reparse points are not authorized")
    resolved = path.resolve()
    if not resolved.is_relative_to(base.resolve()) or resolved == base.resolve():
        raise ValueError("Resolved path escapes authorized boundary")
    return resolved


def input_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    for directory in ("output", "exports", "reports"):
        if path.absolute().is_relative_to(ROOT / directory):
            result = within(path, ROOT / directory)
            if any(p.startswith(".") or ":" in p for p in result.relative_to(ROOT / directory).parts):
                raise ValueError("Hidden files and alternate streams are forbidden")
            if any(re.search(r"(?:^|[_ .-])(secret|credentials?|tokens?|passwords?|cookies?|browser-profile)(?:$|[_ .-])", p, re.I) for p in result.relative_to(ROOT / directory).parts):
                raise ValueError("Credential/secret files are outside the production boundary")
            if result.suffix.lower() not in {".json", ".txt", ".md", ".svg", ".png", ".jpg", ".jpeg", ".pptx"}:
                raise ValueError("Input format not enabled for this adapter")
            if not result.is_file() or result.stat().st_size > (20_000_000 if result.suffix.lower() == '.pptx' else 2_000_000):
                raise ValueError("Input missing or exceeds 2 MB")
            if result.suffix.lower() == '.pptx':
                from .package_guard import validate_pptx
                validate_pptx(result)
            return result
    raise ValueError("Stage authorized inputs under project output/, exports/, or reports/")


def output_root(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    path = within(path, ROOT / "output")
    if any(p.startswith(".") or ":" in p for p in path.relative_to(ROOT / "output").parts):
        raise ValueError("Hidden output paths and alternate streams are forbidden")
    return path


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


@contextmanager
def single_worker():
    """An OS-owned lock releases on process death; no stale PID unlock heuristic."""
    STATE.mkdir(parents=True, exist_ok=True)
    lock = STATE / "worker.lock"
    within(lock, ROOT)
    with lock.open("a+b") as stream:
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise ValueError("BUSY: the single production worker is already executing") from error
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)
