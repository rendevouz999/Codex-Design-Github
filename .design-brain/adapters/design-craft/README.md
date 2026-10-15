# Design Craft

Design Craft is a craft/support skill for UI and visual design work. It helps with typography, color roles, spacing, component states, accessibility, interaction notes, and platform handoff.

When a Brain Design repository is detected, Design Craft does not decide the product structure. It defers to Brain Design routing, product family, reference insight, structure depth, originality gates, and marketplace quality gates.

## Portable Brain Design Detection

Detect a Brain Design repository by checking for one or more of:

- `.design-brain/`
- `AGENTS.md`
- `scripts/design_brain_module_select.py`
- `scripts/design_brain_router_smoke_test.py`
- `PACKAGE_MANIFEST.generated.json`

Do not assume a fixed local path. If the root is unclear, operate relative to the current working directory and report that uncertainty.

## Verification

```bash
Get-ChildItem scripts\*.py | ForEach-Object { python -m py_compile $_.FullName }
python scripts/validate_data.py
python scripts/smoke_test.py
python scripts/export_design_craft.py
```

The public export is written to `exports/design-craft-v0.3.0.zip`.

## Brain Design Adapter

Design Craft v0.3.0 includes `scripts/craft_adapter.py`, JSON schemas in `schemas/`, and `scripts/craft_adapter_smoke_test.py`. The adapter is support-only: it can return tokens, typography, spacing, component states, accessibility, source handoff, and polish notes, but it cannot change Brain Design decisions or approve final delivery.
