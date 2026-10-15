# Sequential Reference-Led Batch Workflow

This is the required workflow for any task that asks Codex to create, revise, or review multiple design templates in one request.

The goal is to prevent batch outputs from becoming siblings of one shared layout. Codex must not study all references globally, create one master structure, and then generate variants. Each template in the batch needs its own reference study cycle, its own evidence-backed designer cognition, its own product logic, and its own finished build.

Also use `.design-brain/BATCH_TEMPLATE_HARD_GATES.md` with this workflow. The hard gates decide whether a similarity problem requires structural rebuild, section recomposition, effect redesign, recolor, or copy rewrite.

Indonesian natural batch language counts. Requests like `buat tiga template website restoran`, `buat beberapa design template website restoran`, `buatkan 3 gambar design nya saja`, `buat 5 variasi template`, or `buat dua landing page berbeda` activate batch mode. Phrases such as `satu per satu`, `1 per 1`, `masing-masing`, `tiap`, `per template`, `per desain`, or `per gambar` activate sequential batch mode even when the wording says `gambar design`.

Quality is more important than output count or early completion claims. A batch is not done because all requested files exist; it is done only when every template is product-complete, visually inspected, and different enough from every accepted prior template.

## Atomic Pair Rule

For Figma/source-template batch work, each cycle is `Template N + Design System Board N`. The design system is not a later pack-cleanup task and not a combined board that can be filled after all pages are drawn.

Do not begin Template N+1 until Template N and Design System Board N are both built, visually checked when possible, receipt-backed, post-build audited, and locked. If the page exists but its design-system board is missing or too thin, the current template is not complete and the next template is blocked.

## Non-Negotiable Serial Cycle Lock

When the user asks for more than one website/Figma/source template, Codex must work as if each template is a separate commissioned product. The next template is forbidden until the current template is finished, repaired, audited, locked, and disposed.

Required sequence:

1. Read only the active reference or active reference group for Template 1.
2. Build Template 1 from interpretation, reconfiguration, and original product logic.
3. Build Template 1's own design-system board.
4. Screenshot-inspect and repair Template 1 and its design-system board.
5. Run the required audits and lock Template 1's fingerprint.
6. Record scaffold disposal for Template 1.
7. Only then begin Reference 2 / Template 2 from a blank structure fingerprint.

Repeat the same cycle for Template 3, Template 4, and every later template. There is no shortcut for packs of 3, 10, or 100 templates.

This rule constrains implementation, not only planning. Do not create all cognition receipts together, all fingerprints together, all Figma frames together, or all design-system boards together from one batch object. A single `use_figma` script may create overview/governance helpers, but it must not build multiple final source templates or multiple final design-system boards in one page-level builder pass.

If the work log shows same-shaped receipt generation such as `template-a.json +114`, `template-b.json +114`, `template-c.json +114`, or identical fingerprint line counts across all templates, treat that as all-at-once scaffold evidence until a lifecycle ledger proves true serial cycles. The correct response is BLOCK/REBUILD, not PASS.

## Core Principle

Batch design is not one planning phase followed by many outputs.

Batch design is repeated single-template design:

1. Select one product-purpose reference group for one template only. The group should contain up to 10 varied references when enough matching local candidates exist.
2. Study that active group deeply.
3. Infer purpose, buyer, audience, marketplace role, and buyer decision model.
4. Extract designer cognition, structure, and visual logic without copying.
5. Build one complete template from the new insight.
6. Build that template's own complete design-system board/source section.
7. Inspect, audit, and lock the whole pair so recognizable execution cannot be reused.
8. Permanently dispose of the spent scaffold and design-system panel order from active working context.
9. Start again from step 1 for the next template.

Required full cycle for each template:

1. Product family classification
2. Reference selection specific to this template
3. Reference cognition extraction
3a. Reference standard extraction: section count/range, section roles, layout-shape inventory, color-role inventory, effect/gradient inventory, and marketplace completeness clues
4. Structure fingerprint
5. Visual-language fingerprint
5a. Section-pattern fingerprint from the Section Layout Extraction Library: selected stable pattern IDs, density limits, compatible-before/after logic, and catalog divergence from earlier accepted templates
6. Output contract
7. Build
8. Build that template's own design-system board/frame/source section
9. Screenshot/render/visual inspection of the template and design-system board when possible
10. Quality gate
11. Similarity diagnosis vs reference and previous accepted outputs
12. Pattern lock only after the design-system board passes
13. Scaffold and design-system panel disposal receipt
14. Start next template from a fresh cycle

## Non-Negotiable Rules

- Do not create a global batch scaffold.
- Do not plan all template structures at once unless it is only to reserve obvious conflicts.
- Do not reuse the same hero grammar, section order, mid-page cadence, CTA rhythm, pricing/proof placement, or footer structure across the batch.
- Do not treat color, copy, niche, or icon changes as structural diversity.
- Do not finish all reference analysis before building any template.
- Do not treat design systems as a final pack-level cleanup after all template pages are built.
- Do not start the next template while the current template's design-system board is missing, receipt-only, minimalist-thin, invalid, or uninspected.
- Do not let one template's successful pattern become the default for the next template.
- Do not use the same reference group for every template unless the user explicitly requires it or the same-product group rotation has exhausted all groups and reset.
- Do not use minimalist, clean, quiet, or premium as a shortcut for skipping the reference's observed structure standard, layout shape variety, color exploration, or effect/gradient logic.
- Do not call a batch complete until each template has been checked against the locked patterns from previous cycles.
- Do not present batch output while any pairwise cross-template comparison reaches 10 percent similarity.
- Do not continue building later templates to chase quantity when the current template has not passed quality and differentiation gates.
- Do not keep, reread, mutate, or data-swap a spent page-level scaffold after its template has been accepted.
- Do not ban abstract design logic such as trust-before-pricing, calm-to-dense rhythm, evidence-before-action, visual proof, attention flow, buyer confidence, progressive disclosure, or simplify-after-complexity. Ban recognizable execution patterns only.
- Do not solve structural similarity with color changes.
- Do not rebuild a strong structure when the only similarity defect is color-role mapping.
- Do not let a template become closer to a previous Codex-built output than to its own selected reference insight.
- Do not wait for the user to explicitly request effects, gradients, glow, shadow, blur, overlays, or stronger visual detail. Infer and apply the correct effect-language choice from the reference and product family.
- Do not accept a template that is merely clean and different if it is visually flat, under-art-directed, or missing a functional visual-language system.
- Do not accept a template whose colors feel flat or underexplored when the reference standard shows richer color relationships.

## Implementation Gate

This workflow must constrain implementation, not only planning. Batch failures often happen when Codex studies references correctly but then uses one convenient coding scaffold to draw every page.

Before building any batch item, write a short structure fingerprint for that item:

- hero grammar
- navigation model
- section order
- dominant module types
- mid-page cadence
- proof, pricing, CTA, and footer placement
- closure silhouette for final proof, CTA, contact, checkout, inquiry, and footer sections
- visual rhythm and density
- layout gesture
- section silhouettes
- section pattern mix
- section pattern IDs
- section density limits
- catalog divergence notes
- composition tension
- focal path
- negative-space shape
- depth layering
- module scale variation
- breakout behavior
- unique motif or interaction implication
- effect language
- color-role system
- gradient logic
- surface-depth grammar
- shadow/glow/blur/border/overlay rules
- CTA and focal-object behavior
- media placeholder treatment
- design-system panel logic
- reference-standard note: observed section count/range, section roles, shape inventory, color behavior, effect/gradient behavior, and which parts will be reinterpreted without copying

For template 2 and later, compare this planned fingerprint against every accepted earlier template fingerprint before implementation. If the plan already shares opening strategy, hero grammar, section sequence, module cadence, CTA/proof/footer closure, closure silhouette, and design-system panel order with an accepted template, stop and replan before drawing anything.

If the plan shares the same `sectionPatternMix` or recognizable section-pattern vocabulary with an accepted template, select different section catalog patterns or recompose those section roles before build. This is a structure defect, not a color or copy defect.

## Local Section Silhouette Check

Zoomed-out page audits can miss a repeated local section. Before presenting batch output, inspect the screenshot of each major section and compare high-visibility local endings:

- final CTA
- proof-to-action block
- contact or inquiry block
- pricing-to-purchase block
- checkout/order block
- newsletter/footer block

If two templates end with the same visible grammar, the newer one must be recomposed. A common failure is `light form/FAQ/content panel + dark CTA/footer panel`; changing the color, text, spacing, or order inside that shape does not count as a repair. The repaired section needs a different action model, such as receipt rail, folded brief sheet, command bar, booking tray, editorial colophon, timeline spine, ledger footer, or product-specific equivalent.

Before implementation, also write a visual-language fingerprint. This is separate from structure. It must explain how the template will use or deliberately avoid gradients, effects, surface depth, color-role emphasis, focal-object treatment, CTA emphasis, and media-placeholder treatment. If this fingerprint cannot be made distinct from accepted earlier templates, replan before drawing.

Before implementation, also run a color-relationship check: does the selected palette work as A+B, A+B+C, or a richer A-G role map for background, surface, CTA, accent, neutral, proof, status, and highlight roles? If the answer is vague, the palette is not ready.

Before the structure fingerprint, write a Designer Cognition Extraction using `.design-brain/DESIGNER_COGNITION_LAYER.md`:

- buyer decision model
- designer intent
- attention strategy
- emotional rhythm
- trust strategy
- density strategy
- conversion or action logic
- component reasoning
- repeated designer pattern
- evidence records with confidence levels
- reusable thinking pattern
- original execution plan

Implementation rules:

- Whole-page generators, shared section assemblers, and one data-driven layout schema for multiple templates are forbidden.
- Shared helpers are allowed only when they are primitive utilities: color parsing, text creation, font loading, simple shape creation, spacing values, or screenshot/report plumbing.
- A reusable function becomes a forbidden scaffold when it decides hero layout, section sequence, module grammar, CTA rhythm, card/grid/table placement, or footer structure for more than one template.
- If two templates can be produced by changing only data, color tokens, copy, image labels, or niche names inside the same builder, the implementation plan has failed.
- Build and inspect each complete template pair before starting the next: main template plus its own design-system board. Do not queue all Figma writes from one batch data object.
- Do not write all batch receipts in one file-generation pass and treat them as independent proof. Receipts are valid only when each belongs to a completed cycle and the previous cycle has been locked and disposed before the next begins.
- If visual review reveals sibling layouts, rebuild at least one of the similar templates from a fresh structure fingerprint before final delivery.
- If visual review reveals stiffness, boxed stacking, repeated zoomed-out silhouettes, repeated closure silhouette, or the same focal path, treat it as layout similarity even when colors, copy, and product niches differ.
- If a later template reaches 10 percent similarity against an accepted earlier template, keep the earlier template as the fingerprint and rebuild the later template before starting the next cycle.
- If pairwise review shows only color-role similarity while structure, composition, and effect language are distinct, recolor the newer template instead of rebuilding the structure.
- If pairwise review shows only copy or naming rhythm similarity, rewrite the newer template copy/name without rebuilding.

## Autonomous Effect And Gradient Gate

Effect and gradient judgment is automatic for batch template work. The user should not need to mention it.

For each template, before calling the build complete:

1. Read the reference effect language: shadow, glow, blur, overlays, gradients, hairline borders, glass, image scrims, surface depth, or deliberate flatness.
2. Translate the function into a new semantic effect system that fits the product, not a copied value set.
3. Apply the system visibly to the page: hero, product stage, CTA, media placeholder, proof module, form, dashboard panel, comparison block, or another focal module.
4. Add or document semantic effect/paint roles in the design system when design-system output is requested.
5. Screenshot-inspect the result. If the page is still flat, generic, or the effects are invisible/decorative, revise before the next cycle.

Valid outcomes include strong effects, subtle effects, or deliberate restraint. Invalid outcomes are accidental flatness, uninspected restraint, copied glow/shadow grammar, decorative gradients with no hierarchy role, and design-system documentation that names effects that are not applied on the page.

## Root-Cause Similarity Gate

Similarity must be diagnosed before revision.

Use this sequence:

1. Structure: same hero grammar, section order, module cadence, proof/CTA rhythm, footer closure, closure silhouette, or design-system panel logic. Action: rebuild the newer template from a fresh structure fingerprint.
2. Layout stiffness: same layout gesture, section silhouettes, focal path, negative-space shape, breakout behavior, or stiff centered stack. Action: rebuild the spatial concept or recompose the affected sections before styling.
3. Composition: same title/media placement, card grouping, grid rhythm, or visual balance. Action: recompose affected sections.
4. Effects: same glow, shadow, blur, border, gradient light, surface depth, or placeholder treatment. Action: redesign the effect language.
5. Visual-language weakness: the template is different but too flat, generic, or under-art-directed. Action: run a functional effect/gradient/surface-depth pass and screenshot-inspect the result.
6. Color only: distinct structure and composition, but palette or color roles feel identical. Action: change palette/color roles only.
7. Copy/name only: distinct visual system, but content tone or naming rhythm repeats. Action: rewrite copy/naming only.

This gate prevents two opposite mistakes: recoloring a scaffold, and destroying a good structure when only the palette is too close.

## Scaffold Disposal Gate

After one template is built, the page-level scaffold used to produce it must be discarded before starting the next template.

This is a required reset, not an optional note. The only reusable implementation code allowed to survive the reset is primitive utility code such as color parsing, font loading, text creation, simple shape helpers, spacing constants, screenshot plumbing, and API-safe Figma boilerplate. Any structure that decided the previous template's hero, section order, module grammar, card/grid/table placement, proof/pricing/CTA rhythm, footer closure, or design-system panel order becomes spent scaffolding and must not be reused.

The pattern lock is negative memory, not a template for the next build. It records what must not repeat.

Disposal means the scaffold is removed from the next cycle's active working context. Do not reread, copy, mutate, or data-swap it for template 2. If the scaffold exists as a temporary file, scratch script, generated builder object, schema note, or page-level data array created only to build one template, delete it after extracting the negative pattern lock. Do not delete user-provided references, final Figma frames, screenshots, review reports, reference-insight records, or pattern locks.

Every cycle after template 1 requires a scaffold disposal receipt before new reference study begins. The receipt must name the spent scaffold, the discarded structure decisions, any temporary artifacts deleted, and the primitive helpers retained.

Before starting the next template, explicitly confirm:

- Previous page scaffold disposed.
- Previous hero grammar disposed.
- Previous section sequence disposed.
- Previous section pattern mix disposed.
- Previous module/card/grid grammar disposed.
- Previous CTA/proof/footer closure disposed.
- Previous design-system panel order disposed unless the user explicitly requires identical documentation structure.
- Temporary scaffold artifacts deleted or removed from active context.
- No previous scaffold will be reread as an implementation source.
- Only primitive utilities retained.
- Next template starts from a blank structure fingerprint and a fresh reference-led cognition pass.

If this disposal cannot be honestly confirmed, stop and redesign the implementation plan before building the next template.

## Reference Pool Rule

Use two reference pools:

- Pattern Learning Pool: all relevant references used to detect repeated designer thinking patterns.
- Reference Groups: product-purpose-matched groups of up to 10 varied references, created from the Pattern Learning Pool.
- Execution Influence Pool: the active reference group used to guide one specific output direction.

For website-template work, the primary local corpus is the configured reference folder, such as `<LOCAL_REFERENCE_CORPUS>/Template Website`. Classify the product family first with `.design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.md`, then use `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md` and `scripts/design_brain_website_reference_select.py` to select product-type-matched references from that folder and rotate the active reference group.

Use `.design-brain/REFERENCE_CORPUS_CONFIG.md` for local corpus path rules. If no local candidates are found, do not claim local-reference-led selection happened; use provided references or ask for corpus configuration.

Do not average all references into one bland template. Do not let the Pattern Learning Pool become a shared visual scaffold. The active group exists to widen layout thinking and expose visual variety, not to combine 10 layouts literally.

## Image Placeholder Rule

For editable source-template cycles, follow `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`.

- Reference imagery teaches image-slot function, not a requirement to generate a finished image.
- Unless the user explicitly asks for generated images, represent image needs with role-specific text clue placeholders such as `image placeholder: product dashboard screenshot`, `image placeholder: ecommerce product image`, or `profile photo placeholder: founder portrait`.
- Pattern memory should record image/media behavior as placeholder logic, crop/ratio rules, and replacement clues, not as copied imagery.

## Batch Pattern Memory

After each template cycle, record:

- opening strategy
- hero grammar
- layout gesture
- section silhouettes
- composition tension
- focal path
- negative-space shape
- depth layering
- module scale variation
- breakout behavior
- trust strategy
- density rhythm
- component system
- CTA logic
- visual motif
- storytelling arc
- effect language
- color-role system
- gradient logic
- surface-depth grammar
- CTA behavior
- media placeholder treatment
- design-system panel order

The next template must avoid repeating at least 90 percent of the previous cycle's recognizable execution pattern. If two batch outputs share the same opening strategy, hero grammar, component system, rhythm map, and CTA logic, the batch has failed even if colors, copy, imagery, and niche labels differ.

## Pairwise 10 Percent Gate

For every batch after the first template:

1. Treat template 1 as the first accepted fingerprint once it passes its own product-quality and reference-originality gates.
2. Compare template 2 against template 1 before presenting either as a completed batch.
3. If template 2 reaches 10 percent similarity against template 1, keep template 1 and rebuild template 2 from a fresh structure fingerprint.
4. When template 2 passes, lock it as its own accepted fingerprint.
5. For template 3 and later, compare the current template against every accepted earlier fingerprint, not only the immediately previous template.
6. Do not deliver final output until every pairwise comparison is below 10 percent and each template still meets its product-type standard.
7. If the only failing axis is color-role mapping, recolor the newer template and rerun the pairwise audit.
8. If the only failing axis is copy/naming, rewrite the newer template and rerun the pairwise audit.

## Cycle Workflow

Run this cycle once per requested template.

### Step 1: Select Active Reference Group

Choose the next active reference group from the available local corpus, for example `Template Website`, that fits the next template's medium, quality bar, or strategic direction. When enough product-purpose matches exist, the group should contain up to 10 varied references.

The references may be close in product type, opposite in rhythm, or useful for a specific design move. The selection should be intentional, not random.

For website-template cycles, select from `Template Website` by product family, not by assumption or random filename order. For same-product sequential builds, rotate group 1 -> group 2 -> group 3 until the product-purpose group list is exhausted, then reset to group 1.

### Step 2: Study Reference Purpose

For each selected reference, infer:

- what the template is trying to sell or enable
- who the likely buyer is
- who the end audience is
- what business goal the page or template supports
- what marketplace category it belongs to
- what level of completeness it suggests

### Step 2A: Extract Designer Cognition

Before mapping sections, answer:

- what the designer wants the viewer to feel or believe first
- where attention moves first, second, and third
- where the design creates calm, density, contrast, trust, or action pressure
- where visual proof replaces text
- where detail is added or removed, and why
- how the design convinces the template buyer that the product is complete and commercially useful
- what visible evidence supports each claim

### Step 3: Study Structure

Map the reference structure:

- hero strategy
- navigation model
- section order
- proof placement
- product/service explanation flow
- conversion path
- repeated modules
- inner page or state implications
- preview or marketplace packaging logic

### Step 4: Study Visual Design

Extract visual logic:

- composition rhythm
- density and whitespace
- typography hierarchy
- image/media behavior
- card/grid/list/table grammar
- color-role system
- motion or interaction implication
- premium vs generic signals
- any memorable section shape or pacing idea

### Step 5: Define Do-Not-Copy Boundary

State what cannot be copied:

- exact layout
- section order
- component grouping
- title/media placement
- color-role mapping
- distinctive motifs
- spacing rhythm if it would make the output recognizably similar

### Step 6: Translate Insight Into A New Template

Before building, define a new template concept:

- product type and niche
- target buyer
- target end audience
- marketplace category
- section map
- visual system
- editable modules
- preview/cover implication if relevant
- what makes this template structurally different from previous outputs
- why this template is closer to its selected references than to previous Codex-built templates

### Step 7: Build One Complete Template

Build only this template in the current cycle. Finish it to the standard expected for the medium: website, Figma template, PowerPoint deck, dashboard, UI kit, WordPress theme, CSS template, marketplace cover, or another platform.

Use the relevant medium playbook and template quality gate. Standard/full structure still applies; do not reduce the template to a thin layout unless the user explicitly asks for a small kit.

### Step 8: Lock The Pattern

After the template is built, record a local working lock in the task context:

- opening strategy used
- hero grammar used
- trust strategy used
- density rhythm used
- component system used
- CTA logic used
- visual motif used
- storytelling arc used
- effect language used
- color-role system used
- design-system panel order used
- reference group used
- must not repeat in later cycles

Future cycles must avoid these locked patterns unless there is a strong reason and a visible structural change.

### Step 9: Dispose The Scaffold

After locking the pattern, dispose of the implementation scaffold used for this template before starting the next cycle. Treat this as a hard gate between cycles.

Do not copy the previous Figma script and edit its data, copy, colors, media labels, or section names for the next template. Do not carry forward the same design-system panel order as a convenience. Start the next template from a blank structure fingerprint and rebuild its code path from that template's own reference cognition.

Allowed to retain: primitive helper utilities, Figma API stability patterns, font loading, color parsing, simple text/shape helpers, and verified technical fixes that do not determine layout grammar.

Forbidden to retain: hero builder, section builder, page schema, card-grid cadence, proof/CTA/footer closure, previous design-system documentation order, or any code path that would make the next output a sibling.

Permanent disposal rule: once the current template is accepted, the scaffold is spent. Remove it from active context immediately. If it was stored as a temporary scaffold file or scratch builder, delete that artifact after recording what must not repeat. If it only existed in the current prompt or code plan, stop referencing it and rebuild the next implementation path from a blank structure fingerprint.

## Batch Completion Gate

Before final delivery, compare all templates:

- every pairwise cross-template comparison stays below 10 percent similarity
- no two templates share the same hero structure
- no two templates share the same mid-page cadence
- no two templates use the same proof/pricing/CTA sequence
- no two templates rely on the same card grid as the main body
- no two templates share the same opening strategy, hero grammar, component system, rhythm map, and CTA logic
- each later template avoids at least 90 percent of the previous cycle's recognizable execution pattern
- no two templates feel like recolored siblings
- no two templates share the same effect/gradient/surface-depth grammar
- no two templates use the same CTA behavior, focal-object treatment, and media-placeholder treatment
- no template is merely clean and different while missing visible art direction
- each template has a different business goal, buyer journey, or product logic
- each template can be explained through its own reference insight cycle
- each template has screenshot evidence or visual inspection notes for effect/gradient quality when possible
- quality and differentiation gates were passed before output was presented

## Relationship To Existing Tools

Existing scripts remain internal tools. They must be used inside each cycle, not as a replacement for the cycle.

- Use module selection to identify medium and quality gates.
- Use template orchestration per template, not once for the whole batch.
- Use reference insight per template, not only once for the whole batch.
- Use originality scoring against the current cycle's references and against previous locked patterns.
- Use review and visual review after each build when evidence exists.

## Forbidden Batch Behavior

These batch shortcuts are forbidden:

- one global reference study for the entire batch
- one master batch plan that assigns surface-level archetypes
- one shared section scaffold reused across all outputs
- one final similarity check after all templates are already built

If any instruction conflicts with this workflow, this workflow wins for batch template work.
