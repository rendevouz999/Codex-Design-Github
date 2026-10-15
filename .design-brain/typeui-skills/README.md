# TypeUI Skills

This folder stores TypeUI-derived style references for Codex Design Brain.

Public-core does not include TypeUI raw, extracted, or TypeUI-managed imported skill files by default. Add or ingest TypeUI files locally if you want TypeUI style intelligence.

## Folder Roles

- Root skill folders such as `premium/DESIGN.md` are original imported TypeUI files only when they are present in the local checkout.
- `raw/[skill]/DESIGN.md` contains normalized copies used by the ingestion script when TypeUI sources have been added locally.
- `extracted/[skill].json` contains deterministic structured summaries generated from raw TypeUI files.

## Safety Rules

- Do not move or delete original TypeUI `DESIGN.md` files.
- Do not blindly activate every TypeUI skill at once.
- Use TypeUI skills as style references and design constraints.
- Select only the styles that fit the template product type, niche, buyer, and visual mood.
- Extracted JSON files are generated artifacts and can be recreated with `scripts/design_brain_typeui_ingest.py`.

## Commands

Normalize raw files and extract JSON:

```bash
python scripts/design_brain_typeui_ingest.py
```

Select a style direction:

```bash
python scripts/design_brain_style_select.py --template-type "landing-page" --niche "wedding-planning" --visual-mood "elegant premium editorial" --target-buyer "wedding planners and event studios"
```
