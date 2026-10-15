# FIG Extracts Evidence

- Rule category: workflow
- Last reviewed: 2026-05-26
- Source references used:
  - Local corpus: `<LOCAL_REFERENCE_CORPUS>/Template Website`
  - openfig-core npm package documentation for `.fig` parsing
  - fig-kiwi npm package documentation for legacy Kiwi archive parsing
  - fzstd npm package documentation for Zstandard decompression

## Purpose

This folder stores generated `.fig` extraction evidence for template study.

Each extraction run should be treated as reference evidence, not stable memory.
Use the extracted node summaries, layer names, text content, raw assets, and
structure reports to understand template scope, section count, frame hierarchy,
and product intent.

## Rules

- Do not copy exact layouts, text, colors, images, or component arrangements from extracted files.
- Use extracted files to learn product structure, hierarchy, density, page/screen coverage, and marketplace scope.
- Keep extraction reports generated and append-only.
- Do not promote lessons into `DESIGN_MEMORY.md` unless the user explicitly says "save this as stable memory".
- Use `npm run fig:extract -- --source "Template Website"` to refresh the corpus when new `.fig` files are added.
