# Autoload Policy

For visual inspection during plugin work, load `.design-brain/VISUAL_INSPECTION_PROTOCOL.md`. Main and the single Engineer use current-source overview, targeted full-resolution crops, and a return to whole-frame context. Record actual observations and unresolved checks; generated images, metadata, screenshot presence and another agent's verdict alone cannot establish visual PASS.

For actual Codex-Design work, load `.design-brain/LOCAL_MEMORY_POLICY.md`. Use the bundled shared memory capability: Supabase first, the local outbox/cache as fallback, and existing plugin-local records alongside both. Include pending/local-only history after recovery. Main and the single Engineer read/search before planning; Main writes and revises with readback. Preserve positive and negative evidence. A service outage does not block local access; conflicts and unknown writes require reconciliation, never blind replay. This owner-approved rule is plugin-scoped.

For plugin PPTX design, load `skills/presentation-deck/workflows/PPTX_LAYOUT_ORIGINALITY_POLICY.md`: extract actual slide geometry and compare with verified earlier PPTX cases across sessions through verified plugin-local memory evidence pointers. Identical composition rejects even after text/color/photo/shape-form/size/count changes. Reused images are allowed only when current tone, content and purpose all pass Main review. No automatic originality PASS from metadata or an empty history.

For plugin-native PPTX creation or substantial deck redesign, load `skills/presentation-deck/workflows/PPTX_FIRST_THREE_SLIDES_REVIEW.md`. Main must inspect rendered slides 1–3 and record PASS before the single Engineer authors slide 4 onward. Reuse the same Engineer for revisions; this is internal Main approval under auto-full trust.

Only during this plugin's use or maintenance, required host worker effort is **Extra High (`xhigh`)**, explicitly passed as `reasoning_effort="xhigh"` together with `model="gpt-6.1-sol"` on the Codex host, or as `effort: xhigh` with `model: claude-opus-5-5` on the Claude Code host. Do not inherit Main effort or silently downgrade; if unavailable, report the specific host limit. An already-running worker must finish or be stopped before a replacement with the required effort starts. Historical completed workers are not concurrent team members.

For plugin-native PPTX photo sourcing, load `skills/presentation-deck/workflows/PPTX_IMAGE_SELECTION_POLICY.md`. The single Engineer searches web/Unsplash/Pexels with available internal tools; Main visually reviews contextual candidates. Two rejected Engineer rounds per stable slot require Main search takeover and a slide-number/placement/crop handoff. Main verifies the rendered result. Prefer hidden in-app or isolated browsing; Firecrawl is an available conditional helper, never a reason to use the user's active browser. This is a standing sourced-photo exception to the generic placeholder default for useful PPTX photo slots, not permission for AI generation or other-platform size changes.

Scope first: activate these design workflows only for actual use or maintenance of the custom plugin `<CODEX_DESIGN_WORKSPACE>`. Unrelated work does not inherit its strict team, worker model, size, creative-trust or approval rules merely from the current directory, installed hook or stored memory.

This policy tells Codex which Design Brain files to load based on task cues.

The user should not need to explicitly mention every memory file. Codex should follow this policy automatically when task cues match.

This is workflow autoload, not internal model training.

## Production Route Authority

Other-platform design templates require a size question when the user has not supplied target platform/dimensions. Do not treat a stored technical preset as consent to use it. Only new native PPTX has the standing automatic size below; old PPTX presets are removed.

For plugin design production, load `.design-brain/runtime/HOST_DESIGN_PRODUCTION_SPECIALIST.md`: Main plus exactly one explicit `gpt-6.1-sol` (Codex host) / `claude-opus-5-5` (Claude Code host) General Design Production Engineer. Main has auto-full trust for creative decisions, internal PASS/REVISE and repairs; ask only material ambiguity. For new native `.pptx` only, autoload `skills/presentation-deck/workflows/PPTX_SIZE_POLICY.md`: 10 × 5.625 inches landscape, with explicit overrides and source-size preservation. Other media and the HTML member of dual delivery do not inherit it.

Before production, load `.design-brain/runtime/PRODUCTION_EXECUTION_POLICY.md`. The selected plugin team is Main plus one host Engineer; native/local tools are available within that team. SDK is an explicitly selected alternative worker route, never an additional concurrent worker. Load `.design-brain/runtime/DESIGN_PRODUCTION_SPECIALIST.md` only for that alternative. SDK capability limits remain route-local. Do not repeat satisfied permission requests or confuse host capacity with selected team size.

When this policy conflicts with README or quick-start documentation, this policy wins. Use `.design-brain/SOURCE_OF_TRUTH_MAP.md` for the complete rule hierarchy.

## Post-Build Completion Gate Autoload

Autoload the Post-Build Completion Gate when the user asks to build a design template, create a Figma template, create a website template, create multiple templates, create a dashboard/app/presentation/UI kit/source design, generate a marketplace template, or produce any built design artifact.

Required files:

- `.design-brain/POST_BUILD_COMPLETION_GATE.md`
- `.design-brain/DESIGN_SYSTEM_BUILD_REQUIREMENTS.md`
- `.design-brain/POST_BUILD_TRIPLE_AUDIT_GATE.md`
- `.design-brain/templates/DESIGN_SYSTEM_RECEIPT.md`
- `.design-brain/templates/POST_BUILD_AUDIT_RECEIPT.md`
- `.design-brain/templates/BATCH_SIMILARITY_AUDIT_RECEIPT.md`
- `scripts/design_brain_post_build_audit.py`
- `scripts/design_brain_design_system_check.py`
- `scripts/design_brain_batch_similarity_audit.py`
- `scripts/design_brain_sequential_provenance_check.py`

The Post-Build Completion Gate is mandatory behavior, not an optional prompt. Codex must not present a design template as final without a design system receipt, triple audit receipt, repair-loop status, and completion receipt.

## Sequential Layout Originality Gate Autoload

Autoload the Sequential Layout Originality Gate when the user asks for a reference-led template build, marketplace template build, Figma/source template, batch template build, multiple distinct templates, or any output where the layout could be too close to a reference or previous AI output.

Required files:

- `.design-brain/BUILD_SESSION_LIFECYCLE.md`
- `.design-brain/SEQUENTIAL_LAYOUT_ORIGINALITY_GATE.md`
- `.design-brain/LAYOUT_SIMILARITY_AXIS_RULES.md`
- `.design-brain/LAYOUT_FLUIDITY_EXPANSION.md`
- `.design-brain/IDEA_RECOVERY_CORPUS.md`
- `.design-brain/templates/LAYOUT_FINGERPRINT.md`
- `.design-brain/templates/REFERENCE_LAYOUT_AUDIT_RECEIPT.md`
- `.design-brain/templates/AI_PAIRWISE_LAYOUT_AUDIT_RECEIPT.md`
- `scripts/design_brain_layout_similarity_audit.py`
- `scripts/design_brain_build_session.py`
- `scripts/design_brain_sequential_layout_smoke_test.py`
- `scripts/design_brain_sequential_provenance_check.py`

This gate is mandatory behavior, not an optional prompt, unless the user explicitly asks for a quick draft, rough exploration, diagnostic, or non-template task. When skipped, the final response must state that layout originality audit was skipped.

## Design Cognition Contract Autoload

Autoload the Design Cognition Contract when:

- user gives a reference
- user asks to build a template
- user asks to create website, landing, dashboard, deck, app, static, UI kit, Figma/source, or marketplace template
- user asks for a design similar to or inspired by a reference
- user asks for batch templates

Required files:

- `.design-brain/DESIGN_COGNITION_CONTRACT.md`
- `.design-brain/DESIGN_COGNITION_GATE.md`
- `.design-brain/templates/DESIGN_COGNITION_RECEIPT.md`
- `.design-brain/templates/DESIGN_COGNITION_RECEIPT.json`
- `scripts/design_brain_design_cognition_check.py`

The 10 cognition steps are default Brain Design behavior. The user does not need to mention Style DNA, Design Intent Lock, Visual Grammar, Reference Boundary, Color Role Re-Mapping, Visual Mood Reinterpretation, Structural Reconfiguration, Pattern Divergence, Section Logic, or Marketplace Readiness.

## Section Layout Extraction Library Autoload

Autoload the Section Layout Extraction Library when the user asks for website template, Figma/source template, reference-led template, marketplace template, batch template, anti-generic, anti-flat, anti-identical, layout-kaku, or section-level layout variation work.

Required files:

- `.design-brain/SECTION_LAYOUT_EXTRACTION_LIBRARY.md`
- `.design-brain/SECTION_LAYOUT_HYPER_ACCURACY_GATE.md`
- `.design-brain/SECTION_LAYOUT_MATCHING_GATE.md`
- `.design-brain/section-layout-library/README.md`
- `.design-brain/section-layout-library/pattern-schema.json`
- `.design-brain/templates/SECTION_LAYOUT_PATTERN.md`
- `scripts/design_brain_section_layout_extract.py`
- `scripts/design_brain_section_layout_smoke_test.py`

This layer sits after Reference Insight / Designer Cognition and before Template Orchestration, Design Simulation, and Layout Fingerprint. It provides section-level layout vocabulary, not a reusable page scaffold. Stable catalog patterns may be selected only when `qualityStatus` is `PASS` and the Hyper-Accuracy Gate has passed.

For website/Figma/source batch work, every template must record a distinct `sectionPatternMix`, `sectionPatternIds`, `sectionDensityLimits`, and `catalogDivergenceNotes` in its layout fingerprint. Reusing the same section pattern mix is a scaffold-risk defect, not a color or copy issue.

## Web Deck Autoload

For explicit native PowerPoint/PPTX creation, editing, filling, animation, or reusable
presentation workspace work, load `skills/presentation-deck/workflows/native.md` and the
plugin's `skills/presentation-deck/SKILL.md`. Generic animation wording does not turn
an explicit PPTX deliverable into a web deck. Explicit PPTX-to-HTML stays web; requests
for both artifacts require both medium workflows and separate completion receipts.

Autoload the Web Deck Medium when the user asks for a web deck, html deck, html presentation, web presentation, browser deck, animated deck, animated slides, animated presentation, interactive deck, slide deck html, single file deck, presenter deck, webinar deck, demo day deck, self running deck, or asks to turn an existing deck into web output with deck to web, ppt to web, pptx to html, or convert deck to html. Indonesian phrasing counts the same: deck html, presentasi web, presentasi html, slide web, slide animasi, presentasi animasi, deck browser, deck interaktif, ppt ke web, ppt ke html, pptx ke html, ubah ppt jadi web, presentasi satu file, slide buat live, deck buat webinar.

Required files:

- `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md`
- `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`
- `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`
- `skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md`
- `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md`
- `skills/presentation-deck/resources/web-deck/`
- `skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs`
- `skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs`

This layer sits after medium identification and before Template Orchestration, Design Simulation, and the Post-Build Completion Gate. It owns the browser-rendered fixed-stage deck only. A bare presentation, deck, slides, PPT, PPTX, PowerPoint, or Keynote request is not web-deck intent and stays with `skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md`.

## Natural Language Intent Detection

Natural language intent detection is a first-class trigger. The user should not need to name workflows explicitly.

When a user asks for design, template, reference, batch, naming, review, or preview work in ordinary language, Codex should infer the intent, load the relevant files below, and use existing scripts as internal tools. Use `.design-brain/NATURAL_INTENT_ROUTER.md`, `.design-brain/DESIGN_AUTOPILOT.md`, `.design-brain/WORKFLOW_TRIGGER_MAP.md`, `.design-brain/RESPONSE_BEHAVIOR.md`, `.design-brain/DESIGNER_COGNITION_LAYER.md`, `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md`, `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md`, `.design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md`, and `.design-brain/CONTINUOUS_DESIGNER_LEARNING_LOOP.md` when the task needs routing clarity.

Do not force the user to remember command names. If intent is clear, proceed with the right workflow internally.

For any request that includes multiple templates, template packs, collections, several variants, or a batch revision, activate `.design-brain/BATCH_TEMPLATE_HARD_GATES.md` and `.design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md`. Multiple-template work must run one complete reference-led cycle per output. Do not use one global batch plan, one shared scaffold, or one all-at-once reference study as the primary workflow.

For multi-template website/Figma/source builds, activate serial provenance as a mandatory gate. The agent must build, audit, repair, lock, and scaffold-dispose Template 1 before reading/building Template 2; repeat the full cycle for every later template. A post-build audit without a build-session ledger is not allowed to return READY for these tasks.

For multi-template website/Figma/source builds, all-at-once production evidence is blocking: one page-level builder for all templates, one `use_figma` script that creates multiple final templates, one batch data object that decides every section sequence, or same-line-count receipt/fingerprint generation across all templates. Treat this as a scaffold failure even when visual screenshots exist.

For batch template work, activate strict quality-first delivery. Do not optimize for output count or early completion claims. Each new template must be compared against all accepted previous templates before final delivery; if cross-template similarity reaches 10 percent, revise the newer template until the pairwise audit passes.

For batch template work, diagnose similarity by root cause before revising. If the defect is structural, rebuild the newer template from a fresh structure fingerprint. If the defect is only color-role similarity, change the palette/color roles and preserve the good structure. If the defect is only copy or naming rhythm, rewrite content and naming without rebuilding.

For batch template work, use build-session lifecycle sequencing. Template B cannot start before Template A is fingerprint locked, and that lock is valid only after Template A plus Design System Board A are complete, receipt-backed, checked, and post-build audited. Template C must compare against Template A and Template B. Template D must compare against A, B, and C. The comparison must include axis-based layout similarity, not only overall score.

For batch template work, activate autonomous art-direction quality gates. The user should not need to explicitly request effects, gradients, shadow depth, glow, overlays, color-role divergence, or stronger visual language. Codex must infer these needs from the reference, product family, marketplace standard, and prior accepted batch outputs. If a template is clean but visually flat, under-art-directed, or missing a functional effect/gradient system, it is not complete.

For advanced template work, identify the medium before selecting style. Load `.design-brain/MEDIUM_PRODUCT_PLAYBOOKS.md`, `.design-brain/ADVANCED_STYLE_GRAMMAR_MATRIX.md`, and `.design-brain/HUMAN_CRAFT_HEURISTICS.md` when the task involves website templates, presentation decks, dashboards, UI kits, brand kits, portfolios, or marketplace previews.

When the user asks for a deck that runs in a browser, identify it as the web deck medium before style selection. Load `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md`, `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`, `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`, `skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md`, and `skills/presentation-deck/resources/web-deck/` when the request carries a web, html, browser, animated, interactive, or single-file cue, in English or Indonesian, and also load `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md` when an existing deck, PPT, or PPTX is the input. The user does not need to name these files; `presentasi html`, `slide animasi`, `deck interaktif`, or `ppt ke web` is enough. A bare `presentasi`, `deck`, `slides`, or `ppt` request stays on the static presentation path.

When any craft/style/design-system support is loaded, also apply `.design-brain/DESIGN_CRAFT_NON_OVERRIDE_CONTRACT.md`. Craft advice may improve the output but cannot bypass cognition, simulation, lifecycle, design-system, post-build, or completion receipt gates.

When the user asks Brain Design to learn from approved, valid, accepted, or Google Drive-ready template folders, load `.design-brain/APPROVED_TEMPLATE_CORPUS.md`. Treat `<USER_HOME>/Downloads\Template\Template yang Sudah Masuk Google Drive` as Yusuf's approved-output benchmark for page depth, design-system boards, preview packaging, and marketplace-ready package surfaces. Use it for quality calibration, not copying.

When the user says a design feels `kaku`, stiff, too boxed, same layout, same silhouette, or too similar between template A/B/C/D/E/F, load `.design-brain/LAYOUT_FLUIDITY_EXPANSION.md` with the Sequential Layout Originality Gate. Treat stiffness as a layout-defect root cause, not as a color, copy, or decoration problem.

When the user asks for more layout exploration, section-level layout catalogs, hyper-accurate layout understanding, duplicate layout prevention, or stronger anti-flat section variation, load `.design-brain/SECTION_LAYOUT_EXTRACTION_LIBRARY.md`, `.design-brain/SECTION_LAYOUT_MATCHING_GATE.md`, and `.design-brain/SECTION_LAYOUT_HYPER_ACCURACY_GATE.md`. Use `scripts/design_brain_section_layout_extract.py` to extract incoming candidates, match candidates, validate the catalog, or select stable PASS patterns. Do not select incoming candidates for builds until matching and hyper-accuracy review pass.

For Envato, marketplace-ready, reference-based, batch, Figma website-template, SaaS website-template, UI kit, dashboard-template, or anti-identical template work, load `.design-brain/DESIGN_SIMULATION_LAYER.md` after orchestration and before build. Run or follow `scripts/design_brain_design_simulate.py` with the proposed structure and reference summary. If the verdict is `REVISE` or `BLOCKED`, do not build; revise structure, visual language, source-template scope, or originality strategy and rerun until `PASS`.

For website template work, do not default to a thin landing-page section count. First classify scope as hero/header kit, landing page, full website template, ecommerce, dashboard/admin, portfolio, blog/editorial, or service site. Load `.design-brain/seed-packs/website-template/` for full website templates and `.design-brain/seed-packs/hero-header-kit/` only when the product is explicitly a hero/header kit.

For reference-led website, web-template, Figma website-template, or marketplace website template work, load `.design-brain/WEBSITE_REFERENCE_PROMPT_LOCK.md`. Use the reference only as Style DNA and product-standard evidence. Do not copy layout, composition, section order, hero grammar, color palette, assets, or scaffold. The default minimum is 9 meaningful sections unless the user explicitly asks for a small-scope product.

For reference-led template, website-template, Figma marketplace template, or batch template work that creates a new template brand, load `.design-brain/TEMPLATE_REFERENCE_USAGE_POLICY.md`, `.design-brain/TEMPLATE_REFERENCE_USAGE_REGISTRY.json`, `.design-brain/templates/BRAND_REFERENCE_USAGE_RECORD.md`, and `.design-brain/TEMPLATE_NAMING_LEDGER.md`. Run or follow `scripts/design_brain_reference_usage_gate.py` for candidate brand and reference-brand safety before Reference Insight / Style DNA. For website local reference selection, use `scripts/design_brain_website_reference_select.py`: build up to 10 eligible product-purpose references per active group, rotate groups for later same-product builds, and reset only after the final available group.

For competitive website or landing-page template work, use at least 9 meaningful sections/blocks unless the user explicitly asks for a hero/header kit, micro landing, narrow campaign, squeeze page, waitlist page, or another intentionally small product. Never use minimalist, clean, safe, simple, fallback, restrained, or basic as the reason for fewer than 9 sections.

For website template work, treat `Template Website` as the default local visual reference corpus and use `.design-brain/REFERENCE_CORPUS_CONFIG.md` for fallback paths and health rules. Load `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md` and select references by website product family before assuming structure, density, proof, or section count. If no local candidates are found, do not claim local-reference-led selection happened.

For Figma reference or Figma template-link work, load `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md` and `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md`. Inspect the Figma scheme as a template system before planning: product purpose, visual direction, section structure, grid/layout, typography hierarchy, color-role system, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, Figma source hygiene, pages, frames, sections, components, variants, states, design-system panels, density rhythm, color/effect function, and product-family standard. Produce a Figma reference schema receipt before building. If the standard is unclear, classify, inspect more evidence, use corpus/category research, or ask one targeted question; do not default to minimalist.

For Figma website template work, load `.design-brain/FIGMA_OUTPUT_TARGET.md`. If the user asks naturally to create or design a website template in Figma and does not provide another Figma target, create a new Figma design file only when the configured target is valid. If the configured target is missing or still a placeholder, ask for a valid project/file target or continue with a local plan without trying to create a Figma file.

For every Figma, source-template, editable UI, or Figma-like template output, load `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md`, `.design-brain/FIGMA_API_COMPATIBILITY.md`, `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`, `.design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md`, and `.design-brain/VISUAL_CRITIQUE_CHECKLIST.md`. The output must include an auto-layout receipt, Figma API alignment enum receipt, layer/component naming receipt, placeholder receipt, responsive/editability note, and source hygiene note.

For any editable template-source work, load `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`. Source templates default to text clue placeholders, not generated/final images, unless imagery is explicitly authorized, including the standing sourced-photo PPTX policy. Stock-image authorization is not AI-generation intent. Use `image placeholder: [purpose]` for image zones and `profile photo placeholder: [role]` for human/profile zones.

For long-horizon design learning, post-build learning, professional designer schema learning, or user requests to keep studying until the logic is truly understood, load `.design-brain/CONTINUOUS_DESIGNER_LEARNING_LOOP.md`. Treat the task as an ongoing question-led cycle: build or study -> generate new questions -> search web evidence when needed or requested -> answer with sources -> update the designer schema -> apply the rule in the next design. Do not optimize for speed when the stated goal is quality of understanding.

## Trigger A: Reference-Based Design

Activated when the user provides an image, screenshot, website reference, Figma reference, template reference, or says:

- use this as reference
- ambil insight
- jangan identik
- buat seperti arah ini
- not copy
- reinterpret

Load:

- `.design-brain/DESIGN_SOUL.md`
- `.design-brain/DESIGN_IDENTITY.md`
- `.design-brain/USER_DESIGN_CONTEXT.md`
- `.design-brain/DESIGN_PRINCIPLES.md`
- `.design-brain/DESIGNER_COGNITION_LAYER.md`
- `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md` when the reference is a Figma link, Figma frame, Figma template, or `.fig` source
- `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md` when the reference is a Figma template or the user asks for professional designer schema learning
- `.design-brain/FIGMA_REFERENCE_LEARNING_CORPUS.md` when the user asks to use the provided Figma material links as learning references
- `.design-brain/CONTINUOUS_DESIGNER_LEARNING_LOOP.md` when the task is part of ongoing designer-schema learning, post-build learning, or web-evidence-based study
- `.design-brain/REFERENCE_INSIGHT_SYSTEM.md`
- `.design-brain/TEMPLATE_REFERENCE_USAGE_POLICY.md`
- `.design-brain/TEMPLATE_REFERENCE_USAGE_REGISTRY.json`
- `.design-brain/templates/BRAND_REFERENCE_USAGE_RECORD.md`
- `.design-brain/WEBSITE_REFERENCE_PROMPT_LOCK.md` when the task is website-template or Figma website-template work
- `.design-brain/REFERENCE_DECONSTRUCTION_MATRIX.md`
- `.design-brain/EFFECT_LANGUAGE_JUDGMENT.md`
- `.design-brain/REFERENCE_INSIGHT_JOURNAL.md`
- `.design-brain/ORIGINALITY_GUARD.md`
- `.design-brain/ORIGINALITY_SIMILARITY_SCORECARD.md`
- `.design-brain/TEMPLATE_BUILD_JOURNAL.md`
- `.design-brain/TEMPLATE_NAMING_LEDGER.md`
Run or follow `scripts/design_brain_reference_usage_gate.py check` before extracting Style DNA when the task will create a template brand from the reference group.

## Trigger B: Template Product Design

Activated when the task mentions:

- template
- marketplace
- Envato
- Figma template
- landing page template
- dashboard template
- UI kit
- PowerPoint
- presentation
- pitch deck
- slides
- Keynote
- brand kit
- cover
- preview
- design overview
- mockup preview

Load:

- `.design-brain/DESIGN_SOUL.md`
- `.design-brain/DESIGN_IDENTITY.md`
- `.design-brain/USER_DESIGN_CONTEXT.md`
- `.design-brain/DESIGN_PRINCIPLES.md`
- `.design-brain/DESIGNER_COGNITION_LAYER.md`
- `.design-brain/TEMPLATE_ORCHESTRATOR.md`
- `.design-brain/TEMPLATE_PRODUCT_INTELLIGENCE.md`
- `.design-brain/APPROVED_TEMPLATE_CORPUS.md` when the task should follow Yusuf's approved-output benchmark or learn from approved local template folders
- `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`
- `.design-brain/FIGMA_OUTPUT_TARGET.md` when the output medium is Figma or the user asks to create a design/template in Figma
- `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md` when a Figma reference/link/template source is used as input
- `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md` when the output medium is Figma or the user asks for a Figma/source template
- `.design-brain/FIGMA_API_COMPATIBILITY.md` when the output medium is Figma or the build will call the Figma Plugin API
- `.design-brain/CONTINUOUS_DESIGNER_LEARNING_LOOP.md` when the user asks to keep learning from templates, references, web evidence, or previous output quality
- `.design-brain/MEDIUM_PRODUCT_PLAYBOOKS.md`
- `.design-brain/ADVANCED_STYLE_GRAMMAR_MATRIX.md`
- `.design-brain/HUMAN_CRAFT_HEURISTICS.md`
- `.design-brain/TEMPLATE_STYLE_ROUTER.md`
- `.design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md`
- `.design-brain/TEMPLATE_BUILD_JOURNAL.md`
- `.design-brain/TEMPLATE_NAMING_LEDGER.md`
- `.design-brain/TEMPLATE_REFERENCE_USAGE_POLICY.md` when references are used
- `.design-brain/TEMPLATE_REFERENCE_USAGE_REGISTRY.json` when references are used
- `.design-brain/templates/BRAND_REFERENCE_USAGE_RECORD.md` when references are used

If the task mentions PowerPoint, presentation, pitch deck, slides, Keynote, PPT, or PPTX, also load `skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md`.

If the task mentions web deck, html deck, html presentation, web presentation, browser deck, animated deck, animated slides, interactive deck, single file deck, presenter/webinar deck, or converting a deck/PPT/PPTX to web or html, also load `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md`, `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`, `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`, `skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md`, `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md`, and `skills/presentation-deck/resources/web-deck/`. Keep the static deck path for requests without a web, html, browser, animated, or interactive cue.

If the task mentions website template, full website, HTML template, PHP template, business website, agency website, or service website, also load `.design-brain/seed-packs/website-template/`.

If the task mentions website template, full website, HTML template, PHP template, business website, agency website, service website, ecommerce, portfolio, blog, docs, dashboard/admin, event, travel, hospitality, or utility pages, also load `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md`.

If the task mentions Figma, Figma template, create new design, design template in Figma, or a natural website-template design request in this workspace without another target link, also load `.design-brain/FIGMA_OUTPUT_TARGET.md`, `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md`, and `.design-brain/FIGMA_API_COMPATIBILITY.md`. Create a new Figma design file only when a valid configured project/file target exists; otherwise ask for a valid target or continue with local planning only. Require real auto-layout for editable structure and normalize Figma API alignment enums before calling `use_figma`.

If the task mentions hero header, hero banner, header kit, or website header, load `.design-brain/seed-packs/hero-header-kit/` and keep the scope as a kit.

If the task mentions Figma design links, local `.fig` files, Figma template files, or asks to extract/study Figma template sources, load `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md`, `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md`, `.design-brain/templates/FIGMA_REFERENCE_SCHEMA_RECEIPT.md`, `.design-brain/evidence/fig-extracts/README.md`, the latest `.design-brain/evidence/fig-extracts/latest.json`, and the relevant extraction report. Use extracted structure as evidence only, not as copyable layout.

## Trigger B2: Multiple Template / Batch Design

Activated when the task asks for:

- multiple templates
- several template variants
- a template pack or collection
- batch template creation
- batch revision
- multiple Figma files, landing pages, decks, covers, previews, websites, dashboards, or UI kits

Load:

- `.design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md`
- `.design-brain/BUILD_SESSION_LIFECYCLE.md`
- `.design-brain/SEQUENTIAL_LAYOUT_ORIGINALITY_GATE.md`
- `.design-brain/LAYOUT_SIMILARITY_AXIS_RULES.md`
- `.design-brain/BATCH_TEMPLATE_HARD_GATES.md`
- `.design-brain/templates/SEQUENTIAL_REFERENCE_BATCH_CYCLE.md`
- `.design-brain/DESIGNER_COGNITION_LAYER.md`
- `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md` when the batch contains website-template outputs
- `.design-brain/REFERENCE_INSIGHT_SYSTEM.md`
- `.design-brain/TEMPLATE_REFERENCE_USAGE_POLICY.md`
- `.design-brain/TEMPLATE_REFERENCE_USAGE_REGISTRY.json`
- `.design-brain/templates/BRAND_REFERENCE_USAGE_RECORD.md`
- `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md` when any cycle uses a Figma reference/link/template source
- `.design-brain/REFERENCE_DECONSTRUCTION_MATRIX.md`
- `.design-brain/EFFECT_LANGUAGE_JUDGMENT.md`
- `.design-brain/ORIGINALITY_GUARD.md`
- `.design-brain/ORIGINALITY_SIMILARITY_SCORECARD.md`
- `.design-brain/TEMPLATE_PRODUCT_INTELLIGENCE.md`
- `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`
- `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md` when any batch output is a Figma template
- `.design-brain/EFFECT_LANGUAGE_JUDGMENT.md`
- medium-specific playbook or seed pack

Required behavior:

1. Build one template per cycle.
2. For each cycle, select the next active product-purpose reference group from the available corpus when possible. When enough matching candidates exist, the group should contain up to 10 varied references and rotate for the next same-product build.
3. For website-template cycles, classify the website product family and select references from `Template Website` using `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md` before reasoning from visuals.
4. Translate reference imagery into text clue placeholders unless imagery is explicitly authorized, including the standing sourced-photo PPTX policy.
5. Infer buyer decision model, designer intent, attention strategy, emotional rhythm, trust strategy, density strategy, conversion logic, and component reasoning with visible evidence.
6. Infer each reference's purpose, target buyer, end audience, structure, visual logic, reusable thinking logic, and do-not-copy boundary.
7. Build one complete standard template from that cycle's insight.
8. For Figma outputs, build editable structure with real auto-layout, normalize Figma Plugin API alignment enums before `use_figma`, and record an auto-layout/API-alignment receipt before review.
9. Define and apply a visual-language fingerprint: color-role logic, gradient logic, effect language, surface depth, shadow/glow/blur/border rules, media-placeholder treatment, CTA behavior, and density rhythm.
10. Screenshot-inspect whether the effect/gradient system is visible and functional. If it is absent, decorative, copied, or too weak to affect hierarchy, revise before continuing.
11. Lock opening strategy, hero grammar, trust strategy, density rhythm, component system, CTA logic, visual motif, effect language, gradient logic, surface-depth system, and storytelling arc.
12. Run the hard-gate similarity diagnosis: structure defects require rebuild, composition/effect defects require recomposition or effect redesign, color-only defects require recolor, copy-only defects require rewrite.
13. Restart the reference study for the next template while staying below 10 percent similarity against accepted prior fingerprints.

Forbidden behavior:

- one global reference analysis for the whole batch
- one master structure reused across outputs
- one late similarity pass after all templates are already built
- Figma template source built primarily with manual x/y positioning instead of auto-layout

## Trigger C: Naming/Title Task

Load:

- `.design-brain/TEMPLATE_NAMING_LEDGER.md`
- `.design-brain/TEMPLATE_REFERENCE_USAGE_REGISTRY.json`
- `.design-brain/USER_DESIGN_CONTEXT.md`
- `.design-brain/DESIGN_PRINCIPLES.md`
- `.design-brain/ORIGINALITY_GUARD.md`

## Trigger D: Review/Critique Task

Load:

- `.agents/skills/design-critic/SKILL.md`
- `.design-brain/VISUAL_CRITIQUE_CHECKLIST.md`
- `.design-brain/DESIGNER_COGNITION_LAYER.md` when reference, template, or batch reasoning matters
- `.design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md`
- `.design-brain/ORIGINALITY_GUARD.md`
- `.design-brain/ORIGINALITY_SIMILARITY_SCORECARD.md` when similarity risk matters
- `.design-brain/EFFECT_LANGUAGE_JUDGMENT.md` when visual polish or reference effects matter
- `.design-brain/HUMAN_CRAFT_HEURISTICS.md`
- `.design-brain/REFERENCE_INSIGHT_JOURNAL.md` when reference-based

## Trigger E: Small Edit

Do not load the full workflow unless reference, template, naming, marketplace, or originality risk is involved.

## Trigger F: Design Agent Runtime

Autoload the Design Agent Runtime when the user asks for:

- full Brain Design workflow execution
- gate automation from route through final verification
- runtime status, doctor, resume, rewind, compact, repair, or finalization
- Design Craft as a Brain Design tool adapter
- package/runtime integrity involving Brain Design gates

Load:

- `.design-brain/runtime/DESIGN_AGENT_RUNTIME.md`
- `.design-brain/runtime/COMMAND_REGISTRY.md`
- `.design-brain/runtime/TOOL_REGISTRY.md`
- `.design-brain/runtime/PERMISSION_MODES.md`
- `.design-brain/runtime/HOOKS.md`
- `.design-brain/runtime/SESSION_STATE.md`
- `.design-brain/runtime/REPAIR_TICKETS.md`
- `.design-brain/runtime/CONTEXT_COMPACTION.md`
- `.design-brain/runtime/DOCTOR_STATUS.md`
- `scripts/design_brain_runtime.py`
- `scripts/design_brain_command_router.py`
- `scripts/design_brain_tool_registry.py`
- `scripts/design_brain_permission.py`
- `scripts/design_brain_repair_ticket.py`
- `scripts/design_brain_doctor.py`
- `scripts/design_brain_status_runtime.py`
- `scripts/design_brain_context_compact.py`

Required behavior:

1. Runtime wraps existing gates and does not replace them.
2. Runtime finalization is blocked until required gates pass and repair tickets are closed.
3. Design Craft adapter is support-only and cannot override Brain Design decisions.
4. Runtime state and `hooks.local.json` are local-only and must not be packaged.

## Design Brain v2.0.0 Controlled Autoload

Do not autoload every v2 file into every task.

- Presentation task: load `00_input_system`, `01_powerpoint_technical`, relevant `03_slide_archetypes`, `04_marketplace_standard`, and `06_quality_control`.
- Reference task: load `05_reference_breakdowns/reference-analysis-template.md`, `05_reference_breakdowns/plagiarism-transformation-method.md`, and good/bad reference rules when examples exist.
- Visual preview task: load `07_visual_pipeline` and save evidence into `.design-brain/evidence/visual-reviews/`.
- FIG extraction task: use `scripts/design_brain_fig_extract.mjs`, save generated evidence into `.design-brain/evidence/fig-extracts/`, and keep it separate from stable memory.
- Feedback task: load `08_feedback_memory` only; do not edit `DESIGN_MEMORY.md` unless the user explicitly says "save this as stable memory".
- PPTX task: run native PPTX validation in addition to screenshots.

## Unified Presentation Capability

`skills/presentation-deck/SKILL.md` is the only presentation skill entry. `skills/presentation-deck/design/WORKFLOW.md` owns shared presentation design; native and web workflow documents own only their output-specific execution. `web-deck` remains a routing/medium alias for browser mode, not a separate skill. General Brain cognition, originality, lifecycle and completion gates remain shared. The capability executes its adopted internal modules and never needs a donor checkout.
