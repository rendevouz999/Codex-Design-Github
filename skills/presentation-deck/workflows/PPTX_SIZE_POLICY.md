# Native PPTX size policy

Owner-requested standing default, 12 October 2026. Apply automatically in future sessions in this workspace; do not ask the user to repeat it.

## Scope and precedence

This policy applies only when creating a new native `.pptx`, including reusable PowerPoint templates, quick decks, and the PPTX member of a dual PPTX/HTML delivery. A current explicit user size overrides the default. Editing/importing an existing PPTX preserves its actual source dimensions unless the user requests resizing. A reference or template with a different size is not permission to silently change a new deck's size.

Do not apply this default to HTML/web decks, Google Slides, Keynote, Figma, websites, dashboards, SVG/vector products, social posts, posters, print, PDF or other design templates. For these platforms, use an already explicit size or ask the user about the target platform and size before designing; do not silently impose this or another preferred preset. Their technical registries remain available after that choice. The web deck runtime's 1920 × 1080 stage remains available, not automatic user consent. SVG used internally to author a PPTX follows the PPTX contract; standalone SVG products do not.

## Exact default

| Property | Required value |
| --- | --- |
| PowerPoint preset | On-screen Show (16:9), landscape |
| Physical size | 10 × 5.625 inches |
| PowerPoint points | 720 × 405 pt |
| OOXML `p:sldSz` | `cx="9144000" cy="5143500" type="screen16x9"` |
| Native SVG at 96 units/inch | `width="960" height="540" viewBox="0 0 960 540"` |
| Registered native preset | `ppt169onscreen` |

The ratio alone is insufficient. The former `ppt169` and `ppt43` presets are removed from active selection; `ppt169onscreen` is the sole PPTX preset. Use `--size-inches` only when the user explicitly requests another physical size. Rendered previews may be 1920 × 1080 without changing physical slide size. Existing source files remain data, not another standing preset.

## Authoring and verification

1. Initialize new PPTX work through `runtime/presentation.py init <absolute_project_YYYYMMDD>`. Default and quick modes write `pptx_canvas.json` before slide authoring. `--format` is an explicit registered-size override; `--size-inches WIDTH HEIGHT` accepts an explicitly requested custom size. These options are mutually exclusive.
2. Carry the contract into `spec_lock.md`, design notes, all slide SVGs, masters, layouts, placeholder geometry and any Specialist assignment. Design at the final size from the start. Adapt differently sized template geometry before authoring; do not fix a finished design by editing only `p:sldSz`.
3. The owned runtime checks slide SVG dimensions before check/export and reads actual `p:sldSz` after export/template-preview. Direct advanced exporter callers must pass the matching `expected_viewbox` and read the resulting package. An existing project without this new contract is not silently migrated.
4. Confirm exact physical size, native objects/editability, overflow and a rendered visual review. Size PASS alone does not establish design readiness. A missing renderer is an explicit verification limitation.

For explicit custom sizes, the current registered-preset scaffold helper does not generate custom planning specs. Author those specs with the exact `pptx_canvas.json` viewBox. The normal standing default has full scaffold support; custom source authoring and size verification remain supported.

Evidence: the user's `Presentation_20_Slides_Painting_Conservation.pptx` and the native proof documented in `reports/pptx-exact-size-reference-2026-10-12.md`. Actual OOXML and PowerPoint size readback outrank stale adjacent reports.
