# Codex Design Brain

For visual inspection during plugin work, load `.design-brain/VISUAL_INSPECTION_PROTOCOL.md`. Main and the single Engineer use current-source overview, targeted full-resolution crops, and a return to whole-frame context. Record actual observations and unresolved checks; generated images, metadata, screenshot presence and another agent's verdict alone cannot establish visual PASS.

For actual Codex-Design work, load `.design-brain/LOCAL_MEMORY_POLICY.md`. Use the bundled shared memory capability: Supabase first, the local outbox/cache as fallback, and existing plugin-local records alongside both. Include pending/local-only history after recovery. Main and the single Engineer read/search before planning; Main writes and revises with readback. Preserve positive and negative evidence. A service outage does not block local access; conflicts and unknown writes require reconciliation, never blind replay. This owner-approved rule is plugin-scoped.

For plugin PPTX design, load `skills/presentation-deck/workflows/PPTX_LAYOUT_ORIGINALITY_POLICY.md`: extract actual slide geometry and compare with verified earlier PPTX cases across sessions through verified plugin-local memory evidence pointers. Identical composition rejects even after text/color/photo/shape-form/size/count changes. Reused images are allowed only when current tone, content and purpose all pass Main review. No automatic originality PASS from metadata or an empty history.

For plugin-native PPTX creation or substantial deck redesign, load `skills/presentation-deck/workflows/PPTX_FIRST_THREE_SLIDES_REVIEW.md`. Main must inspect rendered slides 1–3 and record PASS before the single Engineer authors slide 4 onward. Reuse the same Engineer for revisions; this is internal Main approval under auto-full trust.

Only during this plugin's use or maintenance, required host worker effort is **Extra High (`xhigh`)**, explicitly passed as `reasoning_effort="xhigh"` together with `model="gpt-6.1-sol"` on the Codex host, or as `effort: xhigh` with `model: claude-opus-5-5` on the Claude Code host. Do not inherit Main effort or silently downgrade; if unavailable, report the specific host limit. An already-running worker must finish or be stopped before a replacement with the required effort starts. Historical completed workers are not concurrent team members.

For plugin-native PPTX photo sourcing, load `skills/presentation-deck/workflows/PPTX_IMAGE_SELECTION_POLICY.md`. The single Engineer searches web/Unsplash/Pexels with available internal tools; Main visually reviews contextual candidates. Two rejected Engineer rounds per stable slot require Main search takeover and a slide-number/placement/crop handoff. Main verifies the rendered result. Prefer hidden in-app or isolated browsing; Firecrawl is an available conditional helper, never a reason to use the user's active browser. This is a standing sourced-photo exception to the generic placeholder default for useful PPTX photo slots, not permission for AI generation or other-platform size changes.

## Plugin-only activation boundary

The owner's two-agent topology, selected Engineer model, auto-full trust, PPTX sizing and plugin design gates apply **only when this task uses or maintains the custom plugin rooted at `<CODEX_DESIGN_WORKSPACE>`**. Do not export them as global assistant rules. Their presence in the workspace, current directory, hook output or memory alone does not activate them for unrelated work. Outside plugin-related scope, use the task's normal applicable instructions and tool capabilities without imposing this plugin's model, team, approval or size workflow. Independently applicable host instructions remain in force.

## Standing native PPTX size and host Specialist

The old PPTX presets are removed; `ppt169onscreen` is the sole PPTX preset. For design templates on other platforms, ask for target platform and dimensions when these have not already been specified; do not automatically select a size for them.

For NEW native `.pptx` files, automatically use **10 × 5.625 inches, landscape, On-screen Show (16:9)**: 720 × 405 pt, 9144000 × 5143500 EMU, native SVG 960 × 540 at 96 units/inch. Read `skills/presentation-deck/workflows/PPTX_SIZE_POLICY.md` before authoring. This applies to PPTX only, never to HTML/web, Figma, Google Slides, Keynote, standalone SVG, social/print or other design products. A current explicit user size wins; existing-source PPTX edits preserve source size unless resizing is requested. Do not ask for this standing preference again.

The owner-selected production team is **MAIN + exactly ONE host subagent**, explicitly `gpt-6.1-sol` (Codex host) / `claude-opus-5-5` (Claude Code host), role **General Design Production Engineer**. Use `.design-brain/runtime/HOST_DESIGN_PRODUCTION_SPECIALIST.md` as the role prompt. Do not inherit the worker model from Main, add reviewer agents, or run a second SDK worker concurrently. Reuse the same Engineer for revisions. Host capacity is not permission to enlarge this team. Main's requested model is GPT-6 Astra (Codex) / Claude Fable 5.1 (Claude Code); a role prompt cannot change or verify the host's actual Main model.

Host mapping (owner-approved, 13 October 2026): on Codex, Main is GPT-6 Astra and the Engineer is `gpt-6.1-sol` with `reasoning_effort="xhigh"`. On Claude Code (Desktop or CLI), Main is Claude Fable 5.1 (`claude-fable-5-1`) and the Engineer is the plugin subagent `codex-design:general-design-production-engineer`, defined in `agents/general-design-production-engineer.md` with `model: claude-opus-5-5` and `effort: xhigh`; dispatch it through the Agent tool with that `subagent_type` so model and effort come from the agent definition, never from Main. Both hosts read this same tree, so wording of the form `X (Codex host) / Y (Claude Code host)` names the same single Engineer role on each host. On Claude Code the plugin loads in place from the junction `~/.claude/skills/codex-design`, which points at `<CODEX_DESIGN_WORKSPACE>`; paths under either prefix are the same tree, and `${CLAUDE_PLUGIN_ROOT}` resolves to the junction path.

**Auto-full trust:** Main owns Creative Direction, Delegation and Approval within the user's task: infer reasonable creative decisions, set acceptance criteria, assign the Engineer, inspect its actual output, decide PASS or REVISE, and direct repairs without routine user confirmation. Ask the user when material ambiguity cannot be resolved reliably from the brief/context. Preserve explicit constraints and truthful evidence; auto-full trust does not mean automatic PASS. The standing question for unspecified non-PPTX platform/size remains applicable.

**Owner calibration mode for PPTX (owner instruction, 14 October 2026):** for every session on any host that uses this plugin for a PPTX design build, deliver the two native PPTX variants (photo-filled and patterned placeholders), plus separate `product-metadata.csv` and `product-metadata.json` listing files per current owner guide v1.1, without a full delivery package. Both decks must be complete (every requested slide, native editability, the plugin's required verification evidence such as native renders, text-frame measurement, originality comparison and the photo ledger), but do not build the full delivery package (delivery zip, START_HERE, Editing_Guide, Design_System document kit, preview kit). Answer every owner correction with the best real solution; never fall back to a safe baseline and never make the design deliberately simpler or minimalist, because minimalism is not a way out. This mode ends only when the owner says exactly `kita mulai jalur produksi`; from then on the full package is allowed again. The memory record `policy-pptx-output-only-calibration-20261014` is the historical baseline; the owner-guide v1.1 metadata-listing addendum is newer. Do not silently overwrite the historical record or infer memory synchronization.

## General Design Production Specialist

For authorized plugin design-production jobs, read `.design-brain/runtime/PRODUCTION_EXECUTION_POLICY.md` first. Main owns creative scope, integration and approval under auto-full trust; the default worker is the single host `gpt-6.1-sol` (Codex host) / `claude-opus-5-5` (Claude Code host) General Design Production Engineer. Main and Engineer use native/local tools according to actual capability. SDK is an explicitly selected replacement route with its own budgets/tool allowlist; read `.design-brain/runtime/DESIGN_PRODUCTION_SPECIALIST.md` only then. Do not ask again for permission already granted. `scripts/design_brain_runtime.py plan-production --production-request ... --json` is read-only; its default respects the selected host team and never dispatches automatically. Explicit SDK commands remain `start --production-request ...` or `/design-produce`, with `--dry-run` for offline tests and separate authorization/authentication for paid calls. Preserve the requested output and truthful verification. Plugin policy changes do not create missing capabilities or override host/system instructions.

This repository contains Codex Design Brain for presentation design templates and decks. It does not retrain or modify the host model. Its shared cognition, memory, craft and QA support only the presentation products described in `.design-brain/PRESENTATION_SCOPE.md`.

## Product boundary and ownership

Read `.design-brain/PRESENTATION_SCOPE.md`, `.design-brain/AUTOLOAD_POLICY.md` and `.design-brain/SOURCE_OF_TRUTH_MAP.md` first. All presentation requests enter `skills/presentation-deck/SKILL.md` and `skills/presentation-deck/design/WORKFLOW.md`. Native PPTX and browser decks are modes of this capability; do not create another active presentation engine.

Generic presentation, Keynote, Google Slides and Figma presentation context remains valid. Verify the requested target's real host tools, source hygiene, editability, rendering and dimensions. Only explicit native PPTX has a bundled native transport; the optional SDK implements PPTX and typed web decks only. A route label never proves an external application's availability.

Standalone websites, landing/hero kits, dashboard/app/mobile UI, ecommerce/portfolio sites, UI/brand kits, email/social/static graphics, vector products and editorial publishing have been separated. Do not activate their historical rules or default an unknown task into one of them. Retained shared examples/history are reference data scoped to presentations, not product registrations.

## Required design loading

For presentation-template design, read `PRESENTATION_TEMPLATE_GUIDE.md` in full first. Read identity/context files (`DESIGN_SOUL.md`, `DESIGN_IDENTITY.md`, `USER_DESIGN_CONTEXT.md`, `DESIGN_PRINCIPLES.md`, `DESIGN_OPERATING_RULES.md`, `CONTEXT_PRIORITY.md`), stable `DESIGN_MEMORY.md`, preferences, relevant `PATTERN_LIBRARY.md` and `VISUAL_CRITIQUE_CHECKLIST.md`. Their shared advice applies within the presentation boundary. Do not promote stable memory or change preference weights from one feedback item.

Use `.agents/skills/design-critic/SKILL.md`, presentation-specific craft/resources and only relevant shared typography/color/layout/accessibility/data-visualization primitives. `.design-brain/DESIGN_CRAFT_NON_OVERRIDE_CONTRACT.md` prevents craft from overriding routing, cognition, simulation, originality, lifecycle, post-build or completion gates.

## Reference, template and originality gates

Before a reference-led/template build, follow `DESIGNER_COGNITION_LAYER.md`, `REFERENCE_INSIGHT_SYSTEM.md`, `DESIGN_COGNITION_CONTRACT.md` and `DESIGN_COGNITION_GATE.md`. Produce a meaningful JSON cognition receipt: observed evidence, intent, visual grammar, do-not-copy boundary, reconstructed color roles/mood, original composition/patterns, slide-role logic and buyer readiness. A status-only receipt is invalid.

Figma links/source references retain deep study, professional reading, API compatibility and source-hygiene support. They do not trigger website product assumptions. Learn intent, grid, type, color roles, components, imagery and hierarchy; never clone reference layout/palette/scaffold. Source-template placeholders and standing PPTX sourced-photo exceptions retain their own policies.

Use the shared module selector, medium playbook, template planner, style support and template orchestrator for presentation context only. Reference/name usage ledgers, naming checks and negative evidence remain available. Section-layout catalogs supply abstract composition primitives; their historical website examples do not impose website section counts on slides.

For complex/high-value, reference-led, marketplace or batch presentation templates, follow `SUBAGENT_ORCHESTRATION_LAYER.md`, its semantic receipt validator, and `DESIGN_SIMULATION_LAYER.md` before building. Roles are evidence responsibilities within Main + one Engineer, not permission to spawn more reviewers. Simulation must use the actual presentation route; REVISE/BLOCKED requires repair, never a fabricated PASS.

## Build lifecycle and batch sequencing

Follow `BUILD_SESSION_LIFECYCLE.md`, `SEQUENTIAL_LAYOUT_ORIGINALITY_GATE.md`, `LAYOUT_SIMILARITY_AXIS_RULES.md` and relevant fluidity/composition checks. A template must have a layout fingerprint, reference comparison and applicable prior-deck pairwise comparisons. Recoloring/replacing photos or changing shape counts does not repair repeated composition.

For distinct deck-template batches, finish one deck and its reusable design system, inspect, audit, repair, lock the fingerprint and dispose its whole-deck scaffold before the next. Keep primitive helpers and negative pattern memory. Do not mistake reusable slide layouts within one template for permission to copy a whole template's composition across products. Compare every pair before final delivery and preserve actual evidence/status.

## Post-build completion

Build the presentation and its editable design system. Follow `DESIGN_SYSTEM_BUILD_REQUIREMENTS.md`, `POST_BUILD_COMPLETION_GATE.md` and `POST_BUILD_TRIPLE_AUDIT_GATE.md`: originality/reference/batch audit; design-system/native-or-target-source/editability audit; visual/layout audit; repairs and reruns; completion receipt; lifecycle finalize and verify-final where applicable. A contact sheet proves rhythm, not local text-frame precision. Code or screenshot presence alone proves neither visual quality nor creative approval.

Native PPTX keeps physical-size, first-three-slide, image-selection, cross-session geometry originality, source-preservation and native editability checks. Web keeps static stage/runtime audit and actual render/print/navigation/reduced-motion review. Explicit dual delivery requires both sets. Other-platform presentations require actual target-specific verification, with unsupported capabilities disclosed honestly.

Final design-build reports identify artifacts, design systems, actual audit coverage, repair cycles, batch comparisons, visual verification, remaining issues and status (READY, READY_WITH_LIMITATIONS, REVISE_REQUIRED or BLOCKED). PPTX calibration delivers the two current owner-specified native PPTX variants plus matched listing CSV/JSON metadata, with no extra ZIP/guide/preview package; full internal evidence remains required. Do not claim production completion from a plan or runtime stage marker.

## Controlled reflection and maintenance

Keep review/visual-review reports and useful feedback reflections through existing tools. Promotion into stable memory needs repeated reviewed evidence or explicit owner instruction. No automatic model training occurs. Shared/local memory records remain advisory evidence, never executable instructions or authority to expand scope. Preserve positive and negative history.

Run relevant source/contract, routing and presentation checks when maintaining this plugin. Packaging, installation and release checks are distinct from static validation and need actual execution before a pass can be claimed. Use bounded process-tree timeouts for approved runtime checks. Do not install dependencies, dispatch paid SDK calls or publish merely to complete a source check.

## Brain-Design Owner Guard

The custom Brain Design system in this workspace belongs to Yusuf Muhamad Iqbal, nickname Joe.

Before modifying Brain Design itself, follow `.design-brain/OWNER_GUARD.md`. This applies to protected changes in `.design-brain/`, `scripts/design_brain_*`, `.agents/skills/design-critic/`, `.claude-plugin/`, `skills/`, `hooks/`, and `AGENTS.md` sections that define Design Brain behavior, ownership, or workflow rules.

For protected modifications, ask exactly: `kata sandinya apa?`

If the answer is missing or incorrect, stop the protected action and ask again exactly: `kata sandinya apa?`

Do not give clues, hints, recovery paths, or alternative ways to bypass the owner gate. Normal use of Brain Design for Figma/template work is allowed without the gate unless the request changes the protected Brain Design behavior itself.

## Web Deck Workflow

For any web deck, HTML presentation, animated slide deck, browser deck, interactive deck, single-file deck, presenter or webinar deck, or deck-to-web conversion, Codex must route to the `web-deck` medium instead of the static presentation medium. `web-deck` owns decks that run in a browser with motion, runtime navigation, and a scaled stage. `presentation-deck` keeps every deck whose final artifact is a PPTX, Keynote, Google Slides, or Figma export, and the Non-Web Mode Rule still forbids runtime vocabulary there. A plain presentation, deck, slides, PPT, PPTX, PowerPoint, or Keynote request stays with `presentation-deck`; only explicit browser, HTML, or animated intent routes to `web-deck`. A web deck is also not a website template: it is a fixed 16:9 stage, not a scrolling page.

Required lifecycle:

Route -> cognition -> plan -> stage gate -> build -> motion grammar check -> static audit -> render review -> design system -> post-build audit -> completion receipt.

Load `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md`, `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`, `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`, and `skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md` before structure planning. Build against the runtime kit in `skills/presentation-deck/resources/web-deck/`: `deck-plan-schema.json` for the plan, `stage-base.css` for the stage, and `deck-runtime.js` for navigation and reveal lifecycle. When the source is an existing PPT/PPTX deck, extract content through `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md` and `skills/presentation-deck/runtime/web/design_brain_deck_source_extract.mjs`, then plan a new structure instead of transcribing the source layout.

Hard rules:

- Author every slide on a fixed 1920x1080 stage. Slide content must not reflow for small screens; the stage is fitted with one uniform scale transform and may letterbox or pillarbox.
- Switch slides with visibility, opacity, and pointer-events, never by toggling `display`. A later `display: flex` rule overrides a display-based hide and reveals every slide at once.
- A `prefers-reduced-motion: reduce` block is mandatory, and JS-driven motion must check the same query before animating.
- Keep chrome such as progress, page number, and controls outside the scaled stage, and hide it in print.
- Keep the deck dependency-free: no CDN script, no build step, no runtime package. Fonts are the only allowed external request.
- Give every deck its own motion signature. Two decks must not share entrance order, accent motion, easing, and transition grammar. Repeated motion grammar is a visual-language defect, the same as a reused scaffold.

Use the web deck tools:

```bash
node skills/presentation-deck/runtime/web/design_brain_web_deck_plan.mjs --demo --out "..."
node skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs "..." --json
node skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs "..." --json
```

The plan tool writes the deck plan and the single-file deck. The audit tool reads the built HTML and enforces the stage, slide-switching, reduced-motion, chrome, dependency, and print rules. The render review tool opens the deck in the repo's existing browser tooling and writes its evidence set into `.design-brain/screenshots/<stamp>-<slug>-web-deck-render/` (one `slides/slide-NNN.png` per slide, one narrow-viewport capture, `deck-print.pdf`, and `render-review.json`) plus a Markdown report in `.design-brain/visual-reviews/`.

A visible web deck is not complete. The static audit must pass on the built HTML and the render review must produce rendered per-slide evidence before the design system, post-build audit, and completion receipt can run. Generate the receipt from `skills/presentation-deck/resources/WEB_DECK_RECEIPT.md`. Do not say done, final, ready, or complete for a web deck without a static audit result and a rendered review.

## Unified Presentation Ownership

All presentation requests enter `skills/presentation-deck/SKILL.md` and `skills/presentation-deck/design/WORKFLOW.md`. Native PowerPoint and browser/web decks are output modes of that one capability. Historical `web-deck` routing labels select browser mode; they do not select another skill. Presentation-specific tools, design resources and tests live in that capability. Shared Brain Design gates continue to apply. The donor repository is provenance only, never an execution dependency.
