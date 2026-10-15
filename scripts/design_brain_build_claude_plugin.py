#!/usr/bin/env python
"""Build exports/codex-design.plugin for a Claude account (Customize > Plugins > upload).

Reuses the public-core export rules in design_brain_export_package (collect_files,
should_include, copy_to_staging, generated_manifest, create_zip) and adds what an installed
plugin also needs: agents/, capabilities/ and PRESENTATION_TEMPLATE_GUIDE.md. Secrets under
.design-brain/local-memory/ stay out through the same rules.

A plugin package may hold at most 5,000 files and 200 MB unpacked, so the icon library is packed
into skills/presentation-deck/resources/icons.tar.gz; hooks/brain-design-activate.mjs restores
it in place at SessionStart.

    python scripts/design_brain_build_claude_plugin.py
"""

from __future__ import annotations

import json
import sys
import tarfile
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import design_brain_export_package as ex  # noqa: E402  (needs the path above)

EXTRA_DIRS = ("agents", "capabilities")
EXTRA_FILES = ("PRESENTATION_TEMPLATE_GUIDE.md",)
RESOURCES = "skills/presentation-deck/resources"
MAX_FILES, MAX_BYTES = 5000, 200 * 1024 * 1024


def main() -> int:
    hook = (ROOT / "hooks" / "brain-design-activate.mjs").read_text(encoding="utf-8")
    if "icons.tar.gz" not in hook:
        raise SystemExit("hooks/brain-design-activate.mjs no longer restores icons.tar.gz; the package would ship without icons")
    files = ex.collect_files(ROOT)
    for name in EXTRA_DIRS:
        files += [p for p in sorted((ROOT / name).rglob("*")) if p.is_file() and ex.should_include(p, ROOT)]
    files += [ROOT / name for name in EXTRA_FILES if (ROOT / name).is_file()]
    icons = [p for p in files if ex.rel(p, ROOT).startswith(f"{RESOURCES}/icons/")]
    files = [p for p in files if not ex.rel(p, ROOT).startswith(f"{RESOURCES}/icons/")]

    with tempfile.TemporaryDirectory(prefix="codex-design-plugin-") as tmp:
        staging = Path(tmp)
        ex.copy_to_staging(files, ROOT, staging)
        (staging / RESOURCES).mkdir(parents=True, exist_ok=True)
        with tarfile.open(staging / RESOURCES / "icons.tar.gz", "w:gz", format=tarfile.USTAR_FORMAT) as tar:
            for path in icons:
                tar.add(path, ex.rel(path, ROOT / RESOURCES))
        manifest = ex.generated_manifest(ROOT, staging)
        manifest["mode"] = "claude-account-plugin"
        (staging / "PACKAGE_MANIFEST.generated.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
        )
        staged = [p for p in staging.rglob("*") if p.is_file()]
        size = sum(p.stat().st_size for p in staged)
        if len(staged) > MAX_FILES or size > MAX_BYTES:
            raise SystemExit(f"Too big for a Claude plugin: {len(staged)} files, {size / 1048576:.1f} MB unpacked")
        out = ex.export_root(ROOT) / "codex-design.plugin"
        out.parent.mkdir(parents=True, exist_ok=True)
        ex.create_zip(staging, out)
    print(f"Built {out}: {len(staged)} files, {size / 1048576:.1f} MB unpacked, {len(icons)} icons archived")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
