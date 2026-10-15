#!/usr/bin/env python
"""Run the Brain Design release verification chain without leaving pycache behind."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

from design_brain_package_integrity import FINAL_ZIP_NAME
from design_brain_process_utils import python_command, resolve_python_invocation, run_command


PYTHON_INVOCATION = resolve_python_invocation()


def py_command(args: list[str]) -> list[str]:
    return python_command(args, PYTHON_INVOCATION)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def export_root(root: Path) -> Path:
    if root.parent.name.lower() == "work":
        return root.parent.parent / "exports"
    return root / "exports"


def clean_cache(root: Path) -> None:
    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        if ".git" in current_path.parts or "node_modules" in current_path.parts:
            continue
        for dirname in list(dirs):
            if dirname == "__pycache__":
                shutil.rmtree(current_path / dirname, ignore_errors=True)
                dirs.remove(dirname)
        for filename in files:
            path = current_path / filename
            if path.suffix == ".pyc":
                path.unlink(missing_ok=True)


def run(root: Path, args: list[str]) -> None:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    print("$ " + " ".join(args))
    completed = run_command(args, cwd=root, timeout=180, env=env)
    if completed.timedOut:
        raise SystemExit(124)
    if completed.returncode != 0:
        print((completed.stdout + completed.stderr)[-1600:])
        raise SystemExit(completed.returncode)


def main() -> int:
    root = repo_root()
    scripts = sorted(str(path) for path in (root / "scripts").glob("*.py"))
    run(root, py_command(["-m", "py_compile", *scripts]))
    clean_cache(root)
    run(root, py_command(["scripts/design_brain_router_smoke_test.py"]))
    run(root, py_command(["scripts/design_brain_process_utils_smoke_test.py", "--repeat", "3"]))
    run(root, py_command(["scripts/design_brain_design_sim_smoke_test.py", "--quick", "--global-timeout", "90", "--case-timeout", "20"]))
    run(root, py_command(["scripts/design_brain_post_build_smoke_test.py"]))
    run(root, py_command(["scripts/design_brain_design_cognition_smoke_test.py"]))
    run(root, py_command(["scripts/design_brain_sequential_layout_smoke_test.py"]))
    run(root, ["node", "skills/presentation-deck/tests/design_brain_web_deck_smoke_test.mjs"])
    run(root, py_command(["scripts/design_brain_status.py"]))
    run(root, py_command(["scripts/design_brain_package_integrity.py", "--runtime-timeout", "180", "--command-timeout", "60", "--process-smoke-repeat", "3"]))
    with tempfile.TemporaryDirectory(prefix="brain-install-source-") as tmp:
        run(root, py_command(["scripts/install_design_brain.py", "--target", str(Path(tmp) / "target"), "--dry-run"]))
    run(root, py_command(["scripts/design_brain_export_package.py", "--mode", "public-core", "--command-timeout", "120", "--integrity-timeout", "180", "--process-smoke-repeat", "3"]))
    zip_path = export_root(root) / FINAL_ZIP_NAME
    run(root, py_command(["scripts/design_brain_package_integrity.py", "--zip", str(zip_path), "--runtime-timeout", "180", "--command-timeout", "60", "--process-smoke-repeat", "3"]))
    clean_cache(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
