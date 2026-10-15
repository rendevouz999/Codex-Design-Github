# Figma Output Target

This file stores the default Figma destination for Codex-Design template work.

## Configuration Priority

1. Task-supplied Figma project/file/link for the current request.
2. Local private config: `.design-brain/FIGMA_OUTPUT_TARGET.local.json`.
3. This shared documentation file.

If the active project ID is missing, empty, or still a placeholder such as `<YOUR_FIGMA_PROJECT_ID>` or `PASTE_YOUR_FIGMA_PROJECT_ID_HERE`, the Figma target status is `not configured`. Codex must not call `create_new_file` with a placeholder project ID.

Use `.design-brain/FIGMA_OUTPUT_TARGET.local.example.json` as the safe template for private local IDs. Copy it to `.design-brain/FIGMA_OUTPUT_TARGET.local.json` and keep the real values uncommitted.

## Default Project

Public/shared packages are not configured with a real private Figma project ID.

- Project URL: not configured
- Project ID: not configured
- Plan key: not configured
- Validation file: not configured

Put private project IDs only in `.design-brain/FIGMA_OUTPUT_TARGET.local.json`, which must stay uncommitted and excluded from public ZIP exports.

## When To Use

Use the configured local project automatically when the user asks to build, create, or design a Figma website template and does not provide a different Figma file or project link.

Natural requests that should use this target include:

- "buat aku design template di figma"
- "buat design template website"
- "buat website template di Figma"
- "bikin template website baru"
- "create new design untuk template website"

Default interpretation: a natural "design template website" request in this workspace means a Figma design file for a marketplace-ready website template, not a local HTML page, unless the user explicitly asks for code, a browser app, a presentation deck, or another medium.

## Default Behavior

1. Load `.design-brain/AUTOLOAD_POLICY.md` and the relevant Design Brain workflow files.
2. Treat the task as Template Product Design plus website-template product-family classification.
3. Load `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md` and `.design-brain/REFERENCE_CORPUS_CONFIG.md`; use the configured local visual reference corpus only when candidates are actually found.
4. Create a new Figma design file only when a configured project ID or user-supplied Figma target is available.
5. Use `design` as the Figma editor type unless the user explicitly asks for FigJam or Slides.
6. Name new files with a clear product title, niche, and date when possible, for example `2026-05-28 - AI Finance Website Template`.
7. Load `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md` and build editable source structure with real auto-layout.
8. Continue with Design Brain quality gates: product depth, reference insight, originality, image placeholder policy, auto-layout receipt, visual-language judgment, critique, and visible-output verification.

If the Figma target is `not configured`, Codex may still prepare the local design plan and quality contract, but must ask for a valid project/file target or use a target/link provided in the task before trying to create a Figma file.

## Overrides

- If the user supplies a different Figma project, file, branch, or node link, use the supplied target for that task.
- If the user asks for a local website, code implementation, PowerPoint, Slides, FigJam, or non-Figma artifact, do not force this Figma target.
- If file creation fails because of permission, plan, project, or tool access, report the exact error and ask only for the missing access or target.

## Guardrail

This target is an output destination, not a design scaffold. It must not weaken reference analysis, product-family classification, marketplace structure depth, originality checks, batch anti-scaffold rules, or visual review requirements.

Figma output is also not permission to build a flat manual canvas. Editable templates must use auto-layout for major structure, with absolute positioning reserved only for documented decorative or overlay exceptions.
