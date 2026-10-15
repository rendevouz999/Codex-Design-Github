#!/usr/bin/env python
"""Export Brain Design v2.8.0 Web Deck Medium + Activation Layer package.

The public-core ZIP contains exactly the paths reachable from ROOT_FILES and ROOT_DIRS, so
every shipped layer must be listed there. The Claude Code activation layer is listed:
the ZIP unpacks to a standalone package root, which is the root `.claude-plugin/plugin.json`
declares as its own source, so the unpacked package activates when it is loaded as a plugin.
`scripts/install_design_brain.py` deliberately does not copy those files into another
repository; shipping them and installing them are separate decisions, and
`.design-brain/MANIFEST.json`, `.design-brain/INSTALLATION.md`, and `PUBLIC_PACKAGE_NOTES.md`
describe the same split. The imported design-system skill under the root `skills/` folder stays
out of public-core through the existing TypeUI-derived filter below.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import py_compile
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

from design_brain_package_integrity import (
    COGNITION_MANDATORY_FILES,
    CRAFT_CONTRACT_MANDATORY_FILES,
    DESIGN_CRAFT_ADAPTER_MANDATORY_FILES,
    FINAL_ZIP_NAME,
    LAYOUT_MANDATORY_FILES,
    MANDATORY_FILES,
    PACKAGE_VERSION,
    POST_BUILD_MANDATORY_FILES,
    PPTX_NATIVE_MANDATORY_FILES,
    REFERENCE_USAGE_MANDATORY_FILES,
    RELEASE_REPORT_MANDATORY_FILES,
    RUNTIME_MANDATORY_FILES,
    SIMULATION_MANDATORY_FILES,
    SUBAGENT_MANDATORY_FILES,
    WEB_DECK_MANDATORY_FILES,
)
from design_brain_process_utils import python_command, resolve_python_invocation, run_command as run_process_command


PYTHON_INVOCATION = resolve_python_invocation()


def py_command(args: list[str]) -> list[str]:
    return python_command(args, PYTHON_INVOCATION)


ROOT_FILES = [
    "AGENTS.md",
    "README.md",
    "CHANGELOG.txt",
    "package.json",
    "package-lock.json",
    "tsconfig.json",
    "playwright.config.ts",
    ".gitignore",
    "PUBLIC_PACKAGE_NOTES.md",
]

ROOT_DIRS = [".design-brain", "scripts", ".agents", "tests", "registry", "templates", "reports", ".claude-plugin", "skills", "hooks"]

EXCLUDED_DIR_NAMES = {
    ".git",
    ".codex",
    ".design-brain-backups",
    "__pycache__",
    "node_modules",
    ".venv",
    "exports",
    "dist",
    "build",
    "Template Website",
    "references",
    "mirofish",
    "MiroFish",
    "mirofish-cli",
    "OASIS",
}

EXCLUDED_PREFIXES = {
    ".design-brain/local-memory",
    ".design-brain/tmp",
    ".design-brain/exports",
    ".design-brain/runtime/state",
    ".design-brain/context-packets",
    ".design-brain/pilots",
    ".design-brain/reference-insights",
    ".design-brain/template-plans",
    ".design-brain/template-orchestrations",
    ".design-brain/reviews",
    ".design-brain/screenshots",
    ".design-brain/visual-reviews",
    ".design-brain/pptx-precision-reviews",
    ".design-brain/promotion-proposals",
    ".design-brain/evidence/visual-reviews",
    ".design-brain/evidence/fig-extracts",
    ".design-brain/evidence/web-research",
    ".design-brain/evidence/figma-material-study",
    ".design-brain/evidence/deck-source-extracts",
    ".design-brain/external-indexes",
    ".design-brain/typeui-skills/raw",
    ".design-brain/typeui-skills/extracted",
    ".design-brain/adapters/design-craft/exports",
    ".design-brain/adapters/design-craft/design-craft-backups",
}

EXCLUDED_EXACT = {
    ".design-brain/pptx-native/engine.local.json",
    ".design-brain/FIGMA_OUTPUT_TARGET.local.json",
    ".design-brain/runtime/hooks.local.json",
    ".design-brain/idea-recovery-corpus.local.json",
    ".design-brain/learning/template_website/REFERENCE_INVENTORY.jsonl",
    ".design-brain/learning/template_website/EVIDENCE_LEDGER.jsonl",
    ".design-brain/learning/template_website/PATTERN_DATABASE.json",
    ".design-brain/adapters/design-craft/data/user_extensions.local.json",
}

TEXT_EXTENSIONS = {".md", ".py", ".json", ".jsonl", ".txt", ".ts", ".tsx", ".js", ".mjs", ".toml", ".yml", ".yaml"}


def typeui_marker() -> str:
    return "TYPEUI_SH_" + "MANAGED_START"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Brain Design package ZIP.")
    parser.add_argument("--mode", choices=("public-core",), default="public-core")
    parser.add_argument("--skip-tests", action="store_true", help="Emergency/debug only; default export runs all checks.")
    parser.add_argument("--skip-runtime-checks", action="store_true", help="Emergency/debug alias for --skip-tests.")
    parser.add_argument("--command-timeout", type=int, default=120, help="Default timeout for smoke/install subprocess checks.")
    parser.add_argument("--integrity-timeout", type=int, default=180, help="Timeout for source/ZIP integrity subprocess checks.")
    parser.add_argument("--full-runtime", action="store_true", help="Run bounded full simulation smoke in addition to quick release checks.")
    parser.add_argument("--process-smoke-repeat", type=int, default=5, help="Repeat count for process utils smoke.")
    parser.add_argument("--include-typeui-derived", action="store_true", help="Internal/private export only: include TypeUI-derived managed files.")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def export_root(root: Path) -> Path:
    if root.parent.name.lower() == "work":
        return root.parent.parent / "exports"
    return root / "exports"


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def safe_rmtree(path: Path, allowed_root: Path) -> None:
    if not is_within(path, allowed_root):
        raise RuntimeError(f"Refusing to remove outside allowed root: {path}")
    if path.exists():
        shutil.rmtree(path)


def print_step(label: str) -> None:
    print(label, flush=True)


def run_process(root: Path, label: str, args: list[str], timeout: int, verbose: bool = False) -> str:
    result = run_process_command(args, cwd=root, timeout=timeout, label=label, verbose=verbose)
    if verbose and result.stdout:
        print(result.stdout, flush=True)
    if verbose and result.stderr:
        print(result.stderr, flush=True)
    if result.timedOut:
        print(f"{label} killed process tree with {result.killStrategy}; killed pids: {result.killedPids}", flush=True)
        raise SystemExit(124)
    if not result.ok:
        raise SystemExit(result.returncode or 1)
    return result.stdout or ""


def clean_cache(root: Path) -> None:
    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        parts = current_path.relative_to(root).parts if current_path != root else ()
        if any(part in {".git", "node_modules", ".venv", "exports", ".design-brain-backups"} for part in parts):
            dirs[:] = []
            continue
        for dirname in list(dirs):
            if dirname == "__pycache__":
                shutil.rmtree(current_path / dirname)
                dirs.remove(dirname)
        for filename in files:
            path = current_path / filename
            if path.suffix == ".pyc" or path.name in {".DS_Store", "Thumbs.db"}:
                path.unlink()


def compile_scripts(root: Path) -> None:
    for path in sorted((root / "scripts").glob("*.py")):
        py_compile.compile(str(path), doraise=True)


def under_prefix(relative: str, prefixes: set[str]) -> bool:
    return any(relative == prefix or relative.startswith(prefix + "/") for prefix in prefixes)


def is_backup_or_temp_file(path: Path) -> bool:
    name = path.name
    return (
        fnmatch.fnmatch(name, "*.bak-*")
        or fnmatch.fnmatch(name, "*.backup-*")
        or name.endswith(".orig")
        or name.endswith(".tmp")
        or name.endswith(".old")
    )


def is_typeui_derived_file(path: Path, root: Path) -> bool:
    relative = rel(path, root)
    if relative == ".agents/skills/design-system/SKILL.md":
        return True
    if fnmatch.fnmatch(relative, ".design-brain/typeui-skills/*/DESIGN.md"):
        return True
    if under_prefix(relative, {".design-brain/typeui-skills/raw", ".design-brain/typeui-skills/extracted"}):
        return True
    if path.suffix.lower() in TEXT_EXTENSIONS:
        try:
            return typeui_marker() in path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return False
    return False


def should_include(path: Path, root: Path, include_typeui_derived: bool = False) -> bool:
    relative = rel(path, root)
    if under_prefix(relative, {".design-brain/local-memory"}):
        return False  # Live shared memory is never public package content, including notes/backups.
    parts = Path(relative).parts
    if is_backup_or_temp_file(path):
        return False
    bundled_design_craft_reference = relative.startswith(".design-brain/adapters/design-craft/references/")
    if any(part in EXCLUDED_DIR_NAMES for part in parts) and not bundled_design_craft_reference:
        return False
    if relative in EXCLUDED_EXACT or under_prefix(relative, EXCLUDED_PREFIXES):
        return Path(relative).name.lower() == "readme.md"
    if not include_typeui_derived and is_typeui_derived_file(path, root):
        return False
    if path.suffix == ".pyc" or path.name in {".DS_Store", "Thumbs.db"}:
        return False
    if path.name == ".env" or path.name.startswith(".env."):
        return False
    return True


def collect_files(root: Path, include_typeui_derived: bool = False) -> list[Path]:
    files: dict[str, Path] = {}
    for item in ROOT_FILES:
        path = root / item
        if path.is_file() and should_include(path, root, include_typeui_derived):
            files[item] = path
    for directory_name in ROOT_DIRS:
        directory = root / directory_name
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file() and should_include(path, root, include_typeui_derived):
                files[rel(path, root)] = path
    return [files[name] for name in sorted(files)]


def sanitize_text(text: str) -> str:
    return text.replace("C:\\Users\\Admin\\Desktop\\Codex-Design", "<CODEX_DESIGN_WORKSPACE>")


def copy_to_staging(files: list[Path], root: Path, staging: Path) -> None:
    for src in files:
        dst = staging / rel(src, root)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if rel(src, root).startswith("skills/presentation-deck/"):
            # Capability integrity and provenance hashes cover original bytes,
            # including license line endings and native binary resources.
            shutil.copy2(src, dst)
        elif src.suffix.lower() in TEXT_EXTENSIONS:
            dst.write_text(sanitize_text(src.read_text(encoding="utf-8", errors="ignore")), encoding="utf-8", newline="\n")
        else:
            shutil.copy2(src, dst)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generated_manifest(root: Path, staging: Path, include_typeui_derived: bool = False) -> dict[str, object]:
    staged_names = sorted(
        rel(path, staging)
        for path in staging.rglob("*")
        if path.is_file() and rel(path, staging) != "PACKAGE_MANIFEST.generated.json"
    )
    sha_map = {name: sha256(staging / name) for name in staged_names}
    files = {name: {"sha256": sha_map[name]} for name in staged_names}
    return {
        "packageVersion": PACKAGE_VERSION,
        "brainDesignVersion": PACKAGE_VERSION,
        "outputFileName": FINAL_ZIP_NAME,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "mode": "public-core",
        "includedFileCount": len(staged_names) + 1,
        "mandatoryFilesPresent": all((staging / path).is_file() for path in MANDATORY_FILES if path != "PACKAGE_MANIFEST.generated.json"),
        "simulationFilesPresent": all((staging / path).is_file() for path in SIMULATION_MANDATORY_FILES),
        "postBuildFilesPresent": all((staging / path).is_file() for path in POST_BUILD_MANDATORY_FILES),
        "cognitionFilesPresent": all((staging / path).is_file() for path in COGNITION_MANDATORY_FILES),
        "layoutLifecycleFilesPresent": all((staging / path).is_file() for path in LAYOUT_MANDATORY_FILES),
        "subagentFilesPresent": all((staging / path).is_file() for path in SUBAGENT_MANDATORY_FILES),
        "subagentSemanticValidatorPresent": all((staging / path).is_file() for path in SUBAGENT_MANDATORY_FILES if "semantic" in path or "receipt_validate" in path),
        "runtimeFilesPresent": all((staging / path).is_file() for path in RUNTIME_MANDATORY_FILES),
        "designCraftAdapterFilesPresent": all((staging / path).is_file() for path in DESIGN_CRAFT_ADAPTER_MANDATORY_FILES),
        "referenceUsageFilesPresent": all((staging / path).is_file() for path in REFERENCE_USAGE_MANDATORY_FILES),
        "webDeckFilesPresent": all((staging / path).is_file() for path in WEB_DECK_MANDATORY_FILES),
        "releaseReportFilesPresent": all((staging / path).is_file() for path in RELEASE_REPORT_MANDATORY_FILES),
        "includeTypeUIDerived": include_typeui_derived,
        "excludedRules": [
            "Excludes .git, backups, pycache, pyc, env files, node_modules, local corpus, exports, runtime state, temp simulation runs, and MiroFish/OASIS/Claude Code source directories.",
            "Includes Brain Design core files plus Design Cognition Contract, Design Simulation Layer, Post-Build Completion Gate, Sequential Layout Originality Gate, bundled Design Craft adapter, and Design Agent Runtime docs, schemas, scripts, smoke tests, installer, and integrity checker.",
        ],
        "files": files,
        "sha256": sha_map,
        "selfHashPolicy": "PACKAGE_MANIFEST.generated.json is intentionally excluded from its own sha256 map.",
    }


def create_zip(staging: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, strict_timestamps=False) as zip_file:
        for path in sorted(p for p in staging.rglob("*") if p.is_file()):
            zip_file.write(path, rel(path, staging))


def actual_install_check(root: Path, verbose: bool, timeout: int) -> None:
    with tempfile.TemporaryDirectory(prefix="brain-design-export-install-") as tmp:
        target = Path(tmp) / "target"
        run_process(root, "[6.1/9] Actual temp install", py_command(["scripts/install_design_brain.py", "--target", str(target)]), timeout, verbose)
        missing = [
            path
            for path in ["AGENTS.md", ".design-brain/AUTOLOAD_POLICY.md"]
            + SIMULATION_MANDATORY_FILES
            + POST_BUILD_MANDATORY_FILES
            + COGNITION_MANDATORY_FILES
            + LAYOUT_MANDATORY_FILES
            + SUBAGENT_MANDATORY_FILES
            + CRAFT_CONTRACT_MANDATORY_FILES
            + RUNTIME_MANDATORY_FILES
            + DESIGN_CRAFT_ADAPTER_MANDATORY_FILES
            + REFERENCE_USAGE_MANDATORY_FILES
            + WEB_DECK_MANDATORY_FILES
            + PPTX_NATIVE_MANDATORY_FILES
            + RELEASE_REPORT_MANDATORY_FILES
            if not (target / path).is_file()
        ]
        if missing:
            print("Actual temp install missing files:", flush=True)
            for path in missing:
                print(f"- {path}", flush=True)
            raise SystemExit(1)
        print("[6.1/9] Actual temp install assertions PASS", flush=True)


def main() -> int:
    args = parse_args()
    root = repo_root()
    exports = export_root(root)
    exports.mkdir(parents=True, exist_ok=True)
    staging = exports / f"_staging-brain-design-v{PACKAGE_VERSION}"
    zip_path = exports / FINAL_ZIP_NAME

    print_step("[1/9] Cleaning cache")
    clean_cache(root)
    print_step("[1/9] Cleaning cache PASS")

    print_step("[2/9] Compiling scripts")
    compile_scripts(root)
    print_step("[2/9] Compiling scripts PASS")

    skip_tests = args.skip_tests or args.skip_runtime_checks
    if not skip_tests:
        run_process(root, "[3/9] Router smoke", py_command(["scripts/design_brain_router_smoke_test.py"]), args.command_timeout, args.verbose)
        run_process(
            root,
            "[4/9] Process utils smoke",
            py_command(["scripts/design_brain_process_utils_smoke_test.py", "--repeat", str(args.process_smoke_repeat), "--timeout", "8", "--max-duration", str(max(120, args.process_smoke_repeat * 18))]),
            min(args.command_timeout, 120),
            args.verbose,
        )
        run_process(
            root,
            "[5/9] Design simulation quick smoke",
            py_command([
                "scripts/design_brain_design_sim_smoke_test.py",
                "--quick",
                "--global-timeout",
                "90",
                "--case-timeout",
                "20",
            ]),
            min(args.command_timeout, 120),
            args.verbose,
        )
        run_process(root, "[5.5/9] Post-build smoke", py_command(["scripts/design_brain_post_build_smoke_test.py"]), min(args.command_timeout, 120), args.verbose)
        run_process(root, "[5.75/9] Design cognition smoke", py_command(["scripts/design_brain_design_cognition_smoke_test.py"]), min(args.command_timeout, 120), args.verbose)
        run_process(root, "[5.8/9] Sequential layout smoke", py_command(["scripts/design_brain_sequential_layout_smoke_test.py"]), min(args.command_timeout, 120), args.verbose)
        run_process(root, "[5.82/9] Subagent orchestration smoke", py_command(["scripts/design_brain_subagent_smoke_test.py"]), min(args.command_timeout, 120), args.verbose)
        run_process(root, "[5.83/9] Subagent semantic validation smoke", py_command(["scripts/design_brain_subagent_semantic_smoke_test.py"]), min(args.command_timeout, 120), args.verbose)
        run_process(root, "[5.85/9] Runtime doctor", py_command(["scripts/design_brain_doctor.py", "--json"]), min(args.command_timeout, 120), args.verbose)
        run_process(root, "[5.9/9] Design Craft adapter bridge smoke", py_command(["scripts/design_brain_craft_adapter_bridge_smoke_test.py"]), min(args.command_timeout, 120), args.verbose)
        run_process(root, "[5.95/9] Design Agent Runtime smoke", py_command(["scripts/design_brain_runtime_smoke_test.py"]), min(args.command_timeout, 120), args.verbose)
        if args.full_runtime:
            run_process(
                root,
                "[5/9] Design simulation full smoke",
                py_command([
                    "scripts/design_brain_design_sim_smoke_test.py",
                    "--full",
                    "--global-timeout",
                    "300",
                    "--case-timeout",
                    "45",
                ]),
                max(args.command_timeout, 300),
                args.verbose,
            )
        run_process(
            root,
            "[6/9] Source integrity",
            py_command([
                "scripts/design_brain_package_integrity.py",
                "--runtime-timeout",
                str(args.integrity_timeout),
                "--command-timeout",
                str(args.command_timeout),
                "--process-smoke-repeat",
                str(args.process_smoke_repeat),
            ])
            + (["--full-runtime"] if args.full_runtime else []),
            args.integrity_timeout,
            args.verbose,
        )
        actual_install_check(root, args.verbose, args.command_timeout)
    else:
        print_step("[3/9] Tests skipped by --skip-tests")
        print_step("[4/9] Process utils smoke skipped by --skip-tests")
        print_step("[5/9] Design simulation smoke skipped by --skip-tests")
        print_step("[5.5/9] Post-build smoke skipped by --skip-tests")
        print_step("[5.75/9] Design cognition smoke skipped by --skip-tests")
        print_step("[5.8/9] Sequential layout smoke skipped by --skip-tests")
        print_step("[5.82/9] Subagent orchestration smoke skipped by --skip-tests")
        print_step("[5.85/9] Runtime doctor skipped by --skip-tests")
        print_step("[5.9/9] Design Craft adapter bridge smoke skipped by --skip-tests")
        print_step("[5.95/9] Design Agent Runtime smoke skipped by --skip-tests")
        print_step("[6/9] Source integrity skipped by --skip-tests")
        print_step("[6/9] Actual temp install skipped by --skip-tests")

    print_step("[7/9] Creating ZIP staging")
    safe_rmtree(staging, exports)
    staging.mkdir(parents=True, exist_ok=True)
    files = collect_files(root, args.include_typeui_derived)
    copy_to_staging(files, root, staging)
    manifest = generated_manifest(root, staging, args.include_typeui_derived)
    manifest_text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    (staging / "PACKAGE_MANIFEST.generated.json").write_text(manifest_text, encoding="utf-8", newline="\n")
    (root / "PACKAGE_MANIFEST.generated.json").write_text(manifest_text, encoding="utf-8", newline="\n")
    create_zip(staging, zip_path)
    print_step(f"[7/9] Creating ZIP PASS: {zip_path}")

    if not skip_tests:
        try:
            run_process(
                root,
                "[8/9] ZIP integrity",
                py_command([
                    "scripts/design_brain_package_integrity.py",
                    "--zip",
                    str(zip_path),
                    "--runtime-timeout",
                    str(args.integrity_timeout),
                    "--command-timeout",
                    str(args.command_timeout),
                    "--process-smoke-repeat",
                    str(args.process_smoke_repeat),
                ])
            + (["--full-runtime"] if args.full_runtime else []),
            args.integrity_timeout,
            args.verbose,
        )
        except SystemExit:
            if zip_path.exists():
                zip_path.unlink()
                print_step("[8/9] Removed ZIP after failed integrity check")
            raise
    else:
        print_step("[8/9] ZIP integrity skipped by --skip-tests")

    print_step("[9/9] Cleaning staging")
    safe_rmtree(staging, exports)
    clean_cache(root)
    print_step("[9/9] Cleaning staging PASS")
    print(f"Exported: {zip_path}", flush=True)
    print(f"Included files: {manifest['includedFileCount']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

