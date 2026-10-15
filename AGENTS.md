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

**Owner calibration mode for PPTX (owner instruction, 14 October 2026):** for every session on any host that uses this plugin for a PPTX design build, deliver the PPTX output only. The deck itself must be complete (every requested slide, native editability, the plugin's required verification evidence such as native renders, text-frame measurement, originality comparison and the photo ledger), but do not build the full delivery package (delivery zip, START_HERE, Editing_Guide, Design_System document kit, preview kit). Answer every owner correction with the best real solution; never fall back to a safe baseline and never make the design deliberately simpler or minimalist, because minimalism is not a way out. This mode ends only when the owner says exactly `kita mulai jalur produksi`; from then on the full package is allowed again. The shared memory record `policy-pptx-output-only-calibration-20261014` carries the same rule.

## General Design Production Specialist

For authorized plugin design-production jobs, read `.design-brain/runtime/PRODUCTION_EXECUTION_POLICY.md` first. Main owns creative scope, integration and approval under auto-full trust; the default worker is the single host `gpt-6.1-sol` (Codex host) / `claude-opus-5-5` (Claude Code host) General Design Production Engineer. Main and Engineer use native/local tools according to actual capability. SDK is an explicitly selected replacement route with its own budgets/tool allowlist; read `.design-brain/runtime/DESIGN_PRODUCTION_SPECIALIST.md` only then. Do not ask again for permission already granted. `scripts/design_brain_runtime.py plan-production --production-request ... --json` is read-only; its default respects the selected host team and never dispatches automatically. Explicit SDK commands remain `start --production-request ...` or `/design-produce`, with `--dry-run` for offline tests and separate authorization/authentication for paid calls. Preserve the requested output and truthful verification. Plugin policy changes do not create missing capabilities or override host/system instructions.

This repository contains the Codex Design Brain: a local orchestration layer for better UI and visual design work in Codex App or Codex CLI style workflows. It does not retrain or modify the Codex model. It gives Codex persistent repo-local design memory, preference weights, critique rules, reusable patterns, and a reflection log.

## Source-of-Truth Design Brain

For any template, reference-based, naming, marketplace preview, or design critique task, Codex must treat `.design-brain/` as its external design cognition layer.

Before working, Codex should follow `.design-brain/AUTOLOAD_POLICY.md`.

When rules overlap, resolve them through `.design-brain/SOURCE_OF_TRUTH_MAP.md`. README files and quick-start notes are documentation; active routing, autoload, owner, taxonomy, batch, and quality-gate files own the workflow behavior.

Design Craft, TypeUI-derived style files, and design-system skills are support layers only. They may sharpen critique and polish, but they cannot override Brain Design routing, cognition, simulation, build-session lifecycle, design-system, post-build, or completion receipt gates. Use `.design-brain/DESIGN_CRAFT_NON_OVERRIDE_CONTRACT.md` for this boundary.

Brain Design v2.6.0 may run high-value template workflows through `.design-brain/runtime/` as the Design Agent Runtime. The runtime wraps existing gates; it does not replace Design Cognition Contract, Design Simulation Layer, Sequential Layout Originality Gate, Build Session Lifecycle, Design System Build Requirements, or Post-Build Completion Gate. Design Craft remains a support adapter only.

Core identity files:

- `DESIGN_SOUL.md`
- `DESIGN_IDENTITY.md`
- `USER_DESIGN_CONTEXT.md`
- `DESIGN_PRINCIPLES.md`
- `DESIGN_OPERATING_RULES.md`
- `CONTEXT_PRIORITY.md`

Codex must use these files to understand who it is, how it thinks, how the user works, and which memory, journal, or workflow should be loaded.

## Required Design Workflow

For any UI, frontend, landing page, dashboard, design system, component, preview layout, marketplace template, mockup, browser-rendered deck, or Figma-like layout task, Codex must use the design-critic workflow in `.agents/skills/design-critic/SKILL.md`.

Before implementing or reviewing design work:

1. Read `.design-brain/DESIGN_MEMORY.md`.
2. Read `.design-brain/DESIGN_PREFERENCES.json`.
3. Check `.design-brain/PATTERN_LIBRARY.md` for relevant reusable patterns.
4. Use `.design-brain/VISUAL_CRITIQUE_CHECKLIST.md` as the review gate.

Codex must not finish UI work after the first implementation. It must complete at least one self-critique pass, identify weak areas, and make concrete improvements after critique. Keep outputs practical, production-ready, and suitable for real implementation or marketplace presentation.

## Review Reports

For substantial UI or design tasks, create a structured review report before the final response:

```bash
python scripts/design_brain_review.py --task "..." --target "..." --notes "..."
```

Save generated reports in `.design-brain/reviews/` unless a specific output path is needed. The report is a template for Codex to fill after inspecting the target; it is not automatic visual analysis. Use the report to score the design, identify weak areas, apply concrete revisions, and capture reflection lessons when user feedback exists.

## Controlled Self-Improvement

When the user gives useful design feedback, Codex should convert it into a reusable lesson and append it to `.design-brain/REFLECTION_LOG.md` with:

```bash
python scripts/design_brain_reflect.py --task "..." --feedback "..." --went-wrong "..." --lesson "..." --rule "..."
```

This is controlled self-improvement, not automatic model training. Do not automatically change `.design-brain/DESIGN_MEMORY.md`, `.design-brain/DESIGN_PREFERENCES.json`, or preference weights from a single feedback item. Only promote repeated lessons into `DESIGN_MEMORY.md` after multiple similar feedback patterns or explicit user instruction.

## Memory Promotion

`REFLECTION_LOG.md` is feedback history. `DESIGN_MEMORY.md` is stable long-term design taste. Codex may run a promotion proposal report to review repeated reflection patterns:

```bash
python scripts/design_brain_promote.py --min-count 2
```

Codex must not promote lessons into `DESIGN_MEMORY.md` without explicit user instruction. Repeated feedback patterns can become stable memory only after review and approval. Do not use promotion proposals to change `.design-brain/DESIGN_PREFERENCES.json` or preference weights.

## Operational Workflow

Run `python scripts/design_brain_status.py` when unsure about system health or the next safe action. For substantial UI/design tasks, use `.design-brain/QUICK_START.md` and the templates in `.design-brain/templates/`. Keep the review, reflection, and promotion workflow controlled: create review reports, capture useful feedback as reflection, and never auto-promote lessons into stable memory.

## Natural Intent Autopilot

Codex must not require the user to mention internal Design Brain commands.

For design/template/reference/batch/naming/review tasks, Codex should infer intent from natural language and follow the relevant Design Brain workflow automatically.

If the user provides references, activate reference insight and originality guard.
If the user provides a Figma reference link, Figma frame, Figma template file, or `.fig` source, activate `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md` and `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md` before structure planning. Study the product purpose, visual direction, section structure, grid/layout system, typography hierarchy, color-role system, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, Figma source hygiene, page/frame/component/state scheme, product-family standard, and do-not-copy boundary. Produce a Figma reference schema receipt and never use minimalist as the fallback for unknown structure standard.
If the user asks for multiple templates, activate Batch Template Hard Gates plus Sequential Reference-Led Batch Workflow, per-cycle reference study, pattern locking, root-cause similarity diagnosis, scaffold disposal, and similarity guard.
If the user asks for multiple website/Figma/source templates, activate the Serial Provenance Gate. Do not build multiple final templates or multiple final design-system boards from one app builder, one Figma script, one page schema, or one batch data object. Template 2 may start only after Template 1 is complete, repaired, audited, fingerprint locked, and scaffold-disposed; repeat for every later template.
If the user asks for multiple templates, also activate an automatic visual-language gate. Codex must not wait for explicit mentions of effects, gradients, glow, shadows, blur, overlays, surface depth, or color-role divergence. Each template needs a distinct visual-language fingerprint and applied effect/gradient judgment when the medium benefits from it.
If the user asks for naming, check naming ledger.
If the user asks for marketplace-ready template products, run or follow template orchestration.
If the user asks for subagents, stronger visual validation, Claude-level quality, Style DNA, design-system depth, Figma source QA, marketplace readiness, reference-led website templates, anti-minimalist work, or quality-sensitive template work, activate `.design-brain/SUBAGENT_ORCHESTRATION_LAYER.md`. Subagents are not cosmetic role labels; each active subagent needs required inputs, required outputs/receipts, blocking authority, and semantic evidence before final readiness can be claimed.
If the user provides references or asks for batch templates, activate `.design-brain/DESIGNER_COGNITION_LAYER.md` before structure planning. Codex must infer the designer's attention, emotion, trust, density, proof, and conversion decisions before deciding sections or components.
If the user asks for website templates, activate `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md` and use the configured local reference corpus, such as `<LOCAL_REFERENCE_CORPUS>/Template Website`, by product type.
If the user asks for a new reference-led template or a template brand/name, activate `.design-brain/TEMPLATE_REFERENCE_USAGE_POLICY.md`, `.design-brain/TEMPLATE_REFERENCE_USAGE_REGISTRY.json`, and `scripts/design_brain_reference_usage_gate.py` before Style DNA extraction. Do not reuse generated output brand names, reference brand names, or too-similar name token/prefix/suffix patterns. For website template references, the local selector owns product-purpose group rotation: use up to 10 eligible varied references per active group when enough matches exist, rotate to the next group for the next same-product build, and reset only after the final group is reached.
If the user asks to learn from the provided Figma material links or asks for professional designer schema learning, activate `.design-brain/FIGMA_REFERENCE_LEARNING_CORPUS.md` and use it as study material, not as a shared scaffold.
If the user asks to keep learning after a build, learn previous material more deeply, create new questions, answer via web search, or improve Brain Design toward a professional designer mindset, activate `.design-brain/CONTINUOUS_DESIGNER_LEARNING_LOOP.md`. Treat the latest build/reference/critique as evidence, generate focused questions, search credible web/category evidence when needed, distill designer schema, and update workflow files when protected-change permission is satisfied.
If the user asks for website, web-template, Figma website-template, or standard landing-page template work, competitive standard starts at 8 meaningful sections/blocks. Do not use minimalist, safe, simple, fallback, clean, restrained, or basic as a reason for fewer than 8 sections. Under-8 structure is allowed only when the user explicitly asks for a hero/header kit, micro landing page, narrow campaign, squeeze page, waitlist page, or another intentionally small product.
If the user asks for editable templates, source templates, Figma templates, website templates, or marketplace templates, activate `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`. Except for explicitly authorized imagery, including the standing sourced-photo PPTX policy, image zones must be text clue placeholders such as `image placeholder: [purpose]`; human/profile image zones must use `profile photo placeholder: [role]`. Do not force generated imagery.
If the user asks for a Figma template, editable Figma source template, create new design, or website-template design in this workspace, activate `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md`. Real auto-layout is mandatory for editable structure.
If the user asks for a web deck, HTML presentation, animated slides, browser deck, interactive deck, single-file deck, or a PPT/PPTX converted to web, activate the Web Deck Workflow with `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md`, `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`, `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`, `skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md`, and `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md` for existing deck sources. Static PPTX, Keynote, and Google Slides deliverables stay with `skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md`.
If the requested output is native PowerPoint/PPTX, activate `skills/presentation-deck/workflows/native.md` and the plugin's `skills/presentation-deck/SKILL.md`. Explicit PPTX output takes precedence over generic animation wording. PPTX-to-HTML remains web-deck; an explicit request for both outputs requires separate artifacts and receipts. The pinned external PPT Master engine supplies conversion and source-preservation capabilities, not permission to bypass Brain Design gates.

Internal scripts are tools, not user-facing rituals.

## Sequential Reference-Led Batch Workflow

For any multiple-template or batch design task, Codex must work one template at a time.

Before batch work, load `.design-brain/BATCH_TEMPLATE_HARD_GATES.md`. This hard gate decides whether a similarity defect requires structural rebuild, section recomposition, effect redesign, recolor, or copy rewrite.

Do not study all references globally and then generate multiple variants from one shared structure. Do not create one master scaffold for the whole batch.

Quality outranks output count. Codex must not present batch output just because all requested templates exist; each template must be product-complete, visually reviewed when possible, and pairwise-audited against accepted prior templates.

Each output should be closer to its own selected reference insight than to any previous Codex-built output. If a new template feels like a variant of an earlier template, stop and rebuild its structure plan before implementation.

### Anti-Scaffold Enforcement

For batch template work, Codex must also block the implementation habit that creates sibling outputs from one reusable page builder.

- Do not create or reuse one whole-page generator, data-driven scaffold, or section factory across multiple templates.
- Shared code may only be primitive drawing or utility helpers such as color conversion, text creation, spacing constants, and simple shape helpers.
- Each template must have its own structure fingerprint before build: hero grammar, section order, dominant module types, proof/pricing/CTA placement, footer closure, visual rhythm, and unique motif.
- Each template must also have its own visual-language fingerprint before build: color-role system, gradient logic, effect language, surface-depth grammar, CTA behavior, media placeholder treatment, and design-system documentation logic.
- If two templates would be built by passing different content into the same layout function, stop and redesign the implementation plan.
- If screenshots show sibling structure, the batch is not done; rebuild the similar templates from a new structure fingerprint instead of polishing colors or copy.
- After finishing one template, dispose of the page-level scaffold before starting the next. Pattern lock is negative memory, not a reusable builder. Retain only primitive helpers; reset hero grammar, section sequence, module/card/grid cadence, CTA/proof/footer closure, and design-system panel order.
- Treat every page-level scaffold as single-use. Once a template is accepted, permanently remove that scaffold from active working context before the next template: do not reread, copy, mutate, or data-swap its page schema, Figma script outline, section map, card cadence, or design-system panel order. If a temporary scaffold file or scratch builder was created only for that template, delete it after recording the negative pattern lock.
- Before starting template 2 or later, write a scaffold disposal receipt that names what was discarded and confirms the next template will start from a blank structure fingerprint and a fresh reference-led cognition pass.
- For multi-template website/Figma/source work, post-build READY is blocked unless serial provenance proves each template was completed, audited, locked, and scaffold-disposed before the next template began. Same-line-count receipt/fingerprint generation or one multi-template Figma builder is hard evidence of a shared scaffold and must fail.
- If a later template reaches 10 percent similarity on structure-defining axes against an accepted earlier template, keep the earlier template as its own fingerprint and rebuild the later template from a fresh structure, motif, rhythm, and product-logic direction.
- If the only similarity defect is color-role mapping, recolor the newer template and rerun the pairwise audit instead of rebuilding the structure.
- If the only similarity defect is copy or naming rhythm, rewrite copy/naming and rerun the pairwise audit.
- If the defect is visual-language weakness, such as a clean but flat design, missing applied gradients/effects, invisible effect tokens, or generic surface depth, run a functional effect/gradient/surface-depth pass and visually inspect it before continuing.
- Final batch output is blocked until every pairwise comparison is below 10 percent.

For each requested template:

1. Select one active reference group from the available corpus, such as `Template Website`, for this template only. When enough product-purpose matches exist, the group should contain up to 10 varied references.
2. Use `.design-brain/DESIGNER_COGNITION_LAYER.md` to identify buyer decision model, evidence-backed designer intent, attention strategy, emotional rhythm, trust strategy, density strategy, and conversion logic.
2a. When a Figma reference or template source is used, use `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md`, `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md`, and complete a reference schema receipt before section planning.
3. For website templates, classify product family and select product-type-matched references from `Template Website`; rotate same-product reference groups instead of reusing group 1 for every build.
4. Convert reference imagery into role-specific text clue placeholders for source-template image zones unless imagery is explicitly authorized, including the standing sourced-photo PPTX policy. Do not infer AI-generation permission from stock-image authorization.
5. Study the references and infer their purpose, target buyer, end audience, structure, visual design logic, and marketplace role.
6. Define reusable abstract thinking logic and the recognizable execution details that must not be copied.
7. Build one complete standard/full template from the new insight.
8. Lock the used opening strategy, hero grammar, trust strategy, density rhythm, component system, CTA logic, visual motif, storytelling arc, and reference group.
9. Delete the spent scaffold from active working context and record a disposal receipt before planning the next template.
10. Audit the next template against all accepted earlier fingerprints and diagnose the root cause: structure, composition, effects, color-only, or copy/naming-only.
11. Audit visual language separately: effect language, gradient logic, surface depth, color-role mapping, CTA behavior, and media placeholder treatment.
12. If structure reaches 10 percent similarity, rebuild the newer template before continuing. If effect/gradient/surface grammar repeats, redesign the effect language. If only color is similar, recolor. If only copy/naming repeats, rewrite copy/naming.
13. Start the next template from the next active product-purpose reference group, avoiding at least 90 percent of the previous cycle's recognizable execution pattern.

Use `.design-brain/BATCH_TEMPLATE_HARD_GATES.md`, `.design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md`, and `.design-brain/templates/SEQUENTIAL_REFERENCE_BATCH_CYCLE.md`. Use `scripts/design_brain_sequential_batch.py` as an internal helper when useful.

This is the only active batch workflow. Existing scripts remain available, but template orchestration, reference insight, originality checks, review, and visual review should happen inside each cycle.

## Figma Auto-Layout Enforcement

For Figma template/source work, Codex must treat auto-layout as required implementation behavior.

- Build editable sections, nav, cards, CTAs, forms, repeated rows, dashboards, responsive previews, and design-system panels with real Figma auto-layout.
- Use manual x/y positioning only for documented decorative backgrounds, ambient glows, intentional overlays, mockup callouts, or preview-only effects.
- Set padding, gap, alignment, and resizing behavior intentionally instead of drawing every child as a fixed coordinate layer.
- For Figma Plugin API alignment, use Figma enum values, not CSS/Flexbox terms: `END` must be `MAX`, `START` must be `MIN`, and stretch behavior must use child sizing `FILL` rather than an alignment value.
- Use `HUG`, `FILL`, and `FIXED` sizing semantics where editability or resizing matters.
- Include an auto-layout receipt in design notes, review reports, or system guide before calling the Figma template complete.
- If auto-layout cannot be applied because of a Figma API limitation, stop and report the limitation instead of claiming source-template quality.

## Visual Review Workflow

For substantial UI/frontend work, Codex should inspect rendered output when possible. Save screenshots into `.design-brain/screenshots/`, then generate a visual review report:

```bash
python scripts/design_brain_visual_review.py --task "..." --target "..." --screenshot ".design-brain/screenshots/..." --notes "..."
```

Use visual evidence to revise UI, especially hierarchy, spacing, typography, CTA clarity, contrast, responsiveness, and marketplace presentation quality. Do not rely only on code when visual quality matters. Do not claim visual inspection happened unless Codex actually inspected a screenshot, browser view, or rendered output.

## Real Project Pilot Workflow

Before substantial UI work in a real project, create or follow a pilot brief using `.design-brain/PILOT_WORKFLOW.md` and `.design-brain/templates/REAL_PROJECT_PILOT_BRIEF.md`. Verify Design Brain status in the project before relying on the workflow:

```bash
python scripts/design_brain_status.py --root "PROJECT_ROOT"
```

For the first task in a new project, generate a pilot report:

```bash
python scripts/design_brain_pilot.py --project-root "PROJECT_ROOT" --task "..." --target "..." --notes "..."
```

Use review and visual review reports before finalizing UI. Capture useful user feedback with controlled reflection. Never claim visual inspection happened without actual screenshot, browser, or rendered-output evidence.

## Template Product Design Workflow

For any template product task, Codex must run or follow the Template Product Intelligence workflow before designing. This applies to website landing page templates, Figma website templates, dashboard templates, SaaS templates, UI kits, design system templates, branding kit templates, marketplace preview layouts, template cover layouts, section breakdown overviews, perspective mockup overviews, and responsive preview layouts.

Before designing, identify:

- template product type
- niche
- target buyer
- marketplace category
- section/component structure
- selected style pack
- editable areas
- preview/cover direction
- marketplace quality gate

Codex must not design from visuals alone without understanding the product purpose. Codex must optimize for editable, reusable, marketplace-ready products. Use the template planner when useful:

```bash
python scripts/design_brain_template_plan.py --template-type "..." --niche "..." --target-buyer "..." --visual-mood "..."
```

Read `.design-brain/TEMPLATE_PRODUCT_MEMORY.md`, `.design-brain/TEMPLATE_TAXONOMY.md`, `.design-brain/TEMPLATE_STRUCTURE_RULES.md`, `.design-brain/MARKETPLACE_QUALITY_GATE.md`, `.design-brain/PREVIEW_PRESENTATION_SYSTEM.md`, and `.design-brain/STYLE_PACKS.json`. Avoid generic template output and optimize for editable, reusable, marketplace-ready products.

## Design-Anything Selective Index Workflow

For website, landing page, dashboard, ecommerce, portfolio, PowerPoint/deck, UI kit, brand kit, marketplace preview, mobile app, email/newsletter, static canvas/poster, or document/report tasks, Codex should run or follow module selection before choosing style:

```bash
python scripts/design_brain_module_select.py --task "..." --template-type "..." --niche "..." --target-buyer "..." --visual-mood "..." --dry-run
```

The module selector returns the medium module, craft modules, seed pack, direction pack, validators, and source files. Use this to prevent one landing-page workflow from being applied to every design product.

Generated external indexes from `open-design` and `awesome-claude-skills` belong in `.design-brain/external-indexes/` and must not be treated as stable memory unless explicitly promoted.

## Template Style Routing Workflow

For template tasks, Codex should select only relevant TypeUI-derived style packs. Do not combine all skills. Use TypeUI skills as style references and design constraints, not as raw prompts to blindly merge.

Use ingestion and style selection when TypeUI references are needed:

```bash
python scripts/design_brain_typeui_ingest.py
python scripts/design_brain_style_select.py --template-type "..." --niche "..." --visual-mood "..." --target-buyer "..."
```

Codex should select one coherent style pack or a small compatible combination, explain rejected conflicts, and convert selected skills into concrete constraints before designing.

## Template Product Orchestration Workflow

For any sellable template product task, Codex should create or follow a template orchestration report before designing.

Codex must not jump straight into visuals or code. It must first determine:

- product type
- buyer
- niche
- style strategy
- structure
- editable requirements
- preview direction
- marketplace quality gate

Use the orchestrator when the task involves marketplace-ready templates, Figma templates, landing page templates, dashboard templates, UI kits, branding kits, mockup previews, or product covers:

```bash
python scripts/design_brain_template_orchestrate.py --template-type "..." --niche "..." --target-buyer "..." --visual-mood "..." --notes "..."
```

## MiroFish-Style Design Simulation Workflow

For complex/high-value design tasks, especially reference-led templates, marketplace templates, Figma source templates, and batch outputs, Codex must use the Design Simulation Layer after orchestration and before build/finalization.

This Design Simulation Layer is a Brain Design-native implementation inspired by the MiroFish-style workflow pattern: seed material -> context graph -> agent panel -> simulation rounds -> verdict/report.

It does not bundle, copy, import, or execute MiroFish source code. It does not run OASIS or social/public-opinion simulation. It adapts the architectural idea into a local design review and quality-gate workflow.

Use `.design-brain/DESIGN_SIMULATION_LAYER.md`, `.design-brain/design-simulation/agents.json`, `.design-brain/design-simulation/verdict-schema.json`, and `scripts/design_brain_design_simulate.py`.

For website-template, reference-led, Figma/source-template, marketplace, batch, anti-minimalist, or quality-sensitive work, run or follow `.design-brain/SUBAGENT_ORCHESTRATION_LAYER.md` before Design Simulation. Use `.design-brain/design-subagents/agents.json`, `.design-brain/design-subagents/orchestration-receipt-schema.json`, `.design-brain/design-subagents/semantic-validation-rules.json`, `scripts/design_brain_subagent_orchestrate.py`, and `scripts/design_brain_subagent_receipt_validate.py` to decide active roles, missing receipts, semantic receipt quality, and blocking status.

When running the Design Simulation Layer, first resolve the route via Brain Design router/product-family detection. Do not allow the simulation layer to override Brain Design router decisions with simpler keyword inference.

If a simulation verdict reports `routing.routeSource=fallback`, treat the route as lower confidence and prefer fixing router availability or adding a proper router rule before relying on the verdict.

Marketplace wording must be route-safe. `Envato marketplace`, `marketplace-ready template`, `editable marketplace template`, and `marketplace buyer` describe template distribution and must not trigger ecommerce. Only product/vendor/cart/checkout/platform/listing marketplace wording should route to ecommerce/listing.

Release/runtime checks for simulation, package integrity, export, ZIP integrity, temp install, and JSON output must use bounded recursive process-tree timeout handling. A hanging child process is a release failure, not a reason to skip runtime checks.

Use quick simulation smoke for normal release/export gates:

```bash
python scripts/design_brain_design_sim_smoke_test.py --quick --global-timeout 90 --case-timeout 20
```

Use full simulation smoke only for deeper regression runs. Both quick and full smoke must print per-case progress and respect per-case plus global timeouts. Process utility smoke is mandatory before release because simulation tools may spawn nested Python child processes.

Process utility smoke must be repeatable and zombie-aware. POSIX zombie/defunct children count as terminated, not active. Nested runtime checks should use the Brain Design Python executable resolver and honor `BRAIN_DESIGN_PYTHON` when the user needs an explicit interpreter override.

Trigger simulation when:

- user provides reference
- task is template marketplace
- task is batch
- task asks originality / not too similar
- task is Figma/source design
- previous output risk is minimalist/generic/scaffolded

Do not run simulation for:

- tiny edits
- rename requests
- copy tweaks
- minor file hygiene tasks
- simple status checks

Required behavior:

- Create a proposed structure first.
- Create or follow a subagent orchestration receipt when the task requires full or standard subagent mode, and validate receipt contents before final PASS when evidence exists.
- Include reference DNA and do-not-copy boundaries when references exist.
- Run or follow the simulation before building the actual template.
- `PASS`: proceed.
- `REVISE`: apply required repairs, then rerun or document repairs.
- `BLOCKED`: do not build/finalize until root cause is fixed.
- Store accepted structure fingerprints for future anti-identical checks.
- For batch work, compare each new cycle against accepted prior fingerprints before build.

Use this command shape:

```bash
python scripts/design_brain_design_simulate.py --task "..." --template-type "..." --niche "..." --target-buyer "..." --visual-mood "..." --marketplace "Envato" --proposed-structure "..." --reference-summary "..."
```

Do not claim the simulation passed unless the generated `report/design_verdict.json` says `PASS`.

## Reference Insight Memory Workflow

When the user provides a reference, Codex must treat it as a source of insight, not as a layout to copy.

Before designing from a reference, Codex must identify:

- who buys the template and what the buyer needs it to prove
- the evidence-backed designer cognition behind the reference, using `.design-brain/DESIGNER_COGNITION_LAYER.md`
- what the reference is trying to achieve
- what design logic can be learned
- what color-role logic can be learned, including background mood, accent function, CTA pressure, surface separation, and proof/highlight behavior
- what effect logic can be learned, including shadow, glow, blur, overlay, border, and surface depth
- what section, hierarchy, and content flow insights are useful
- what must not be copied
- how to reinterpret the insight into a new structure

Codex must avoid direct cloning, one-to-one section order copying, same composition, same component grouping, copied palettes, exact gradient/glow values, same color-role mapping, and superficial color/text changes. Reference colors are insight about mood and function, not source tokens. Reconstruct a new palette from product type, buyer, marketplace category, accessibility, and intended emotion.

For section count, Codex may infer from the reference but must not match the reference blindly, force every design into a long structure, or compress every design into minimalist structure. Use the normal standard for the product type: complete enough for marketplace quality, concise enough for the product's actual buyer journey.

Store valuable reference lessons with:

```bash
python scripts/design_brain_reference_insight.py --reference-name "..." --lesson "..." --do-not-copy "..." --reinterpretation "..."
```

## Template Build Journal and Naming Memory

When Codex helps create a template product, it should record the result in `TEMPLATE_BUILD_JOURNAL.md` and update `TEMPLATE_NAMING_LEDGER.md` using:

```bash
python scripts/design_brain_build_record.py --template-name "..." --template-type "..." --niche "..."
```

Before choosing a new template name, Codex should check naming similarity:

```bash
python scripts/design_brain_name_check.py --candidate-name "..." --niche "..." --template-type "..." --dry-run
```

## Design Quality Rules

- Prefer premium, clean, modern, marketplace-ready design.
- Prioritize strong visual hierarchy and one clear primary action.
- Use intentional whitespace, clean alignment, and a consistent spacing system.
- Maintain polished typography with clear scale, readable line length, and purposeful emphasis.
- Keep color, radius, shadow, icon, and component-state choices consistent.
- Ensure responsive behavior, accessible contrast, keyboard/focus states where relevant, and text that does not overflow or overlap.
- Avoid generic visual output, default-looking templates, overcrowded sections, and random decorative elements.
- Avoid childish or overly playful UI unless the user explicitly asks for that tone.
- Use gradients, glass effects, heavy shadows, or decorative visuals only when they support the concept.
- Make the design feel intentional, not auto-generated.

## Effect Language Judgment

For reference-based template work, Codex should consider effect language as part of visual insight. Study whether the reference uses drop shadows, glow, blur, overlays, hairline borders, gradient light, glass, or surface depth. Learn the function behind the effect, then reinterpret it into a new effect system instead of copying values.

If the reference has little or no visible effect but still feels premium, Codex should decide whether subtle original effects would improve hierarchy, depth, CTA focus, placeholder clarity, or marketplace polish. Effects are not mandatory; the correct move can be restraint. When effects are used, name them semantically in the design system and apply them only where they improve the structure.

## Reflection

When the user gives design feedback, store reusable lessons in `.design-brain/REFLECTION_LOG.md` using the existing format:

- Date
- Task
- User feedback
- What went wrong
- Design lesson
- Rule to reuse next time

## Brain-Design Owner Guard

The custom Brain Design system in this workspace belongs to Yusuf Muhamad Iqbal, nickname Joe.

Before modifying Brain Design itself, follow `.design-brain/OWNER_GUARD.md`. This applies to protected changes in `.design-brain/`, `scripts/design_brain_*`, `.agents/skills/design-critic/`, `.claude-plugin/`, `skills/`, `hooks/`, and `AGENTS.md` sections that define Design Brain behavior, ownership, or workflow rules.

For protected modifications, ask exactly: `kata sandinya apa?`

If the answer is missing or incorrect, stop the protected action and ask again exactly: `kata sandinya apa?`

Do not give clues, hints, recovery paths, or alternative ways to bypass the owner gate. Normal use of Brain Design for Figma/template work is allowed without the gate unless the request changes the protected Brain Design behavior itself.

## Post-Build Completion Gate

For any design template build, Figma/source template, website template, dashboard/app template, presentation template, UI kit, marketplace template, or batch design output, Codex must run the Post-Build Completion Gate after build. A visible template alone is not complete.

Required post-build order:

1. Build template.
2. Build the design system tied to that template.
3. For multi-template website/Figma/source builds, run Audit Pass 0: serial provenance.
4. Run Audit Pass 1: originality/reference/batch similarity.
5. Run Audit Pass 2: design system, Figma/source hygiene, auto-layout, editability, components, states, layer naming, responsive/source structure.
6. Run Audit Pass 3: visual/layout QA for overlap, overflow, clipping, contrast, alignment, section density, crop, stacking, and responsive defects.
7. Repair failures.
8. Rerun failed audits, or all three audits if the repair can affect multiple areas.
9. Generate a completion receipt.
10. If a build-session lifecycle ledger exists, run final lifecycle verification before the final response.

For batch outputs, compare every template pair before final delivery. For N templates, compare N*(N-1)/2 pairs. The batch is not complete if templates reuse the same scaffold, hero grammar, section order, card cadence, CTA closure, image treatment, or visual language.

Final responses for template builds must include:

- Templates built
- Design systems built
- Audit Pass 1
- Audit Pass 2
- Audit Pass 3
- Batch similarity audit
- Repair cycles
- Remaining issues
- Visual verification
- Final status: READY, READY_WITH_LIMITATIONS, REVISE_REQUIRED, or BLOCKED

Do not say done, final, ready, or complete for design template work before the design system, triple audit, repair loop, completion receipt, and lifecycle `verify-final` check are satisfied.

## Design Cognition Contract

When the user gives a reference or asks for a template build, Codex must automatically apply the 10-step Design Cognition Contract before orchestration/build:

- Style DNA
- Design Intent Lock
- Visual Grammar
- Reference Boundary
- Color Role Re-Mapping
- Visual Mood Reinterpretation
- Structural Reconfiguration
- Pattern Divergence
- Section Logic
- Marketplace Readiness

Do not ask the user to mention these terms. They are default Brain Design behavior. Color Role Re-Mapping must prevent copying the reference palette or dominant color identity. Reference Boundary must define what can be learned and what cannot be copied. Section Logic must prevent generic Hero > Features > CTA scaffolds for full templates.

Automated gates require a JSON Design Cognition Receipt. The Markdown receipt template is for human authoring only unless a Markdown parser is implemented. For reference-led/template tasks, Design Simulation must validate the JSON receipt and cannot PASS when the receipt is missing or invalid. A fake status-only receipt such as `{"status":"PASS"}` is not valid.

## Sequential Layout Originality Gate

For reference-led, marketplace, Figma/source, or batch template builds, Codex must run the Sequential Layout Originality Gate as part of the build lifecycle. This gate is additive: it does not replace Design Cognition Contract, Design Simulation Layer, or Post-Build Completion Gate.

Required lifecycle:

Route -> cognition -> simulation -> plan -> layout audit -> build -> design system -> post-build audit -> fingerprint lock -> next template.

Rules:

- Each template must have a layout fingerprint before build/final.
- Each template must be audited against its own reference layout before build/final.
- For batch work, each new AI template must be audited against every previous locked AI template before continuing.
- Template B cannot start before Template A is fingerprint locked. Template C cannot start before A and B are locked, and so on.
- Similarity must be axis-based: hero grammar, section order, grid system, layout rhythm, component cadence, CTA placement, image treatment, typography behavior, color roles, effect language, navigation/footer pattern, and scaffold risk.
- Recoloring or replacing images is not a valid repair for layout/scaffold similarity. The repair must reconfigure layout, structure, rhythm, component cadence, CTA flow, hero grammar, or visual grammar.
- Optional idea recovery from `<CODEX_DESIGN_WORKSPACE>\Template Website` is local-only inspiration. Do not copy the corpus and do not include it in public ZIP packages.
- Final completion receipts for template builds must include reference layout audit result, AI pairwise layout audit result, fingerprint lock status, idea recovery corpus usage, layout repair cycles, axis failures repaired, and safe-to-proceed status.
- Final lifecycle verification must use `scripts/design_brain_build_session.py verify-final --session <session> --json` after `finalize`; missing route, cognition, simulation, layout audit, build artifact, design system, post-build audit, fingerprint lock, batch pairwise audit, or completion receipt blocks final delivery.

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
