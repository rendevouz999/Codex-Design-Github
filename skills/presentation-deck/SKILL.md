---
name: presentation-deck
description: Design reusable presentation templates and create or edit decks in Codex Design. Use for PowerPoint/PPTX, slide masters, layouts, brand/style templates, native charts/tables, HTML/browser decks, animated presentations, and PPTX-to-web conversion. One capability owns shared design and native/web output modes.
---

For visual inspection during plugin work, load `.design-brain/VISUAL_INSPECTION_PROTOCOL.md`. Main and the single Engineer use current-source overview, targeted full-resolution crops, and a return to whole-frame context. Record actual observations and unresolved checks; generated images, metadata, screenshot presence and another agent's verdict alone cannot establish visual PASS.


For plugin tasks, load [shared memory and fallback](../../.design-brain/LOCAL_MEMORY_POLICY.md). Main and Engineer retrieve through the Supabase/local adapter before planning; Main saves positive and negative decisions with guarded revisions and readback. The service need not be online. Preserve local-only history after recovery and reconcile unknown writes before retry.

# Presentation design

For native PPTX, [layout history and contextual image reuse](workflows/PPTX_LAYOUT_ORIGINALITY_POLICY.md) requires actual geometry extraction, comparison with previous PPTX products across sessions, and Main visual judgment. Repeated composition rejects despite cosmetic/shape changes; same photos may recur only after current tone/content/purpose checks. Keep the evidence in Quick as well as Default/template workflows.

For native PPTX creation or substantial deck redesign with a slide roster, follow [Main review of the first three slides](workflows/PPTX_FIRST_THREE_SLIDES_REVIEW.md). Author/render slides 1–3 first; Main records PASS before slide 4 onward may be authored. This applies to Default, Quick and deck/template production. Keep the review receipt even when other planning stays in context; no routine user reapproval is required.

For template output on another platform, ask the user for missing platform/size decisions before layout; do not infer consent from a technical preset. Already specified dimensions need no repeated question.

For sourced PPTX images, load [PPTX image selection policy](workflows/PPTX_IMAGE_SELECTION_POLICY.md): Engineer search, Main contextual visual review, Main takeover after two rejected rounds per slot, explicit slide/crop assignment and final render review. Use the single GPT-6.1 Sol (Codex) / Claude Opus 5.5 (Claude Code) Engineer at Extra High (`xhigh`); no extra image reviewer.

For native `.pptx` creation, load [PPTX size policy](workflows/PPTX_SIZE_POLICY.md) before layout: default **10 × 5.625 inches, landscape**, native SVG 960 × 540. This standing user requirement is exclusive to PPTX; all other formats retain their own sizing. Existing PPTX edits preserve source size unless resizing is requested; current explicit user size overrides win.

Resolve `CAPABILITY_ROOT` from this file and `PLUGIN_ROOT` as its parent directory's parent. Do not depend on the current working directory. All presentation-specific design, workflows and execution are owned here; `capability.json` lists modes and resources.

1. Load the plugin's AGENTS and autoload policy, then [the shared design workflow](design/WORKFLOW.md). Preserve decisions and authorization already supplied by the user.
2. Choose the operation: Create Template for reusable Brand/Style/Layout/Deck; Generate for new content or redesign; Edit Existing for source-preserving PPTX edits. Templates require authored systems, reusable layouts and editability, not only successful export.
3. Select output mode. Explicit PowerPoint, including animation, uses [native](workflows/native.md). Explicit HTML/browser or PPTX-to-web uses [web](workflows/web.md). Both require two artifacts and respective QA. Existing route labels are mode aliases within this capability.
4. Load only the selected workflow and relevant design references. Use the bundled runtime and resources. The original donor checkout is not a prerequisite.
5. Inspect, critique and repair the rendered result before design readiness. Keep source files intact. Technical export PASS does not establish visual quality, fidelity or template readiness.

Image placeholders follow the user's source-template policy. Optional image/media services require their actual tools and credentials and are never mandatory for template creation. Google Slides, Keynote and Figma exports require an available target-specific tool; do not promise an untested conversion.

Shared plugin cognition, originality, simulation and completion gates remain authoritative for the tasks that trigger them. General craft/critic primitives stay in their shared owners; presentation decisions and the review procedure live in [design/WORKFLOW.md](design/WORKFLOW.md). Provenance and original license notices are retained under `provenance/`.
