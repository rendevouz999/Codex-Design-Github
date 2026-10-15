# Batch Template Hard Gates

## Purpose

- Mencegah batch output memakai scaffold yang sama.
- Memastikan 1 template = 1 full reference-led cycle.
- Memastikan setiap output punya structure fingerprint, visual-language fingerprint, dan scaffold disposal receipt.

This file is a mandatory quality gate for any request that creates, revises, or reviews more than one design template in a batch.

Use `.design-brain/QUALITY_GATE_FAILURE_TAXONOMY.md` for failure reports. Similarity defects must be labeled by root cause before revising.

The core failure to prevent: multiple templates that look good individually but reveal the same hidden page grammar when viewed together.

## Post-Build Batch Gate

After each template in a batch:

- finish that template's source design
- build the design system
- run the post-build triple audit
- compare against previous templates
- repair before continuing
- lock fingerprint only after audit pass

## Atomic Template Plus Design System Gate

For multi-template Figma/source work, one batch item is not a page alone. It is an inseparable pair:

`Template N + Design System Board N`

Codex is forbidden to start, plan in implementation detail, or build Template N+1 until Template N and Design System Board N are both complete.

The current template pair is complete only when:

- the main template source design is built
- its physically separate design-system board/frame/source section is built and named for that template
- the design system includes functional coverage, not only swatches/type/button samples
- the design system receipt exists and passes the design-system check
- the design-system board is visually inspected or screenshot-inspected when possible
- the post-build audit passes for that template pair
- the fingerprint is locked after the design system is complete

If Template N exists but Design System Board N is missing, thin, invalid, visually rough, or uninspected, Template N is incomplete. Stop and finish that pair before touching Template N+1.

Final batch:

- run global pairwise similarity audit
- compare every pair, N*(N-1)/2
- final status cannot be READY if any pair fails similarity audit
- do not treat recolor-only differences as distinct templates
- run serial provenance audit for multi-template website/Figma/source work
- final status cannot be READY without a build-session ledger proving one completed cycle at a time

## Design Cognition Contract For Batch

For every template in a batch:

- generate Design Cognition Receipt
- Color Role Re-Mapping must be distinct unless a shared family is intentionally requested
- Pattern Divergence is required between templates
- Section Logic must differ enough to avoid sibling scaffolds
- Visual Grammar must not collapse into the same scaffold
- Color exploration must prove the palette roles work together; flat or underexplored color-role systems are a visual-language defect, not a minimalist style.
- Effect and gradient exploration must happen automatically; if they are omitted, the fingerprint must document deliberate restraint and the hierarchy mechanism replacing them.

Batch pairwise audit compares color identity, hero grammar, visual grammar, section order, CTA rhythm, image treatment, and component cadence.

## Non-Negotiable Standard

A batch template is not complete when all requested designs exist.

A batch template is complete only when each output:

- was created from its own reference-led cycle
- is closer to its own selected reference insight than to any previous output
- has a distinct structure fingerprint
- has a distinct visual-language fingerprint
- passes product-type completeness
- passes applied effect/gradient quality when the medium benefits from visual depth
- passes visual/render inspection when possible
- passes pairwise similarity against every accepted previous template

If quality requires slower work, slow down. Do not optimize for output count.

## One Template Equals One Full Project

For batch work, treat every template as a separate project.

Each template requires its own:

- product-family classification
- selected active product-purpose reference group, up to 10 eligible varied references when enough local matches exist
- reference standard extraction: section count/range, section roles, layout-shape inventory, color-role inventory, effect/gradient inventory, and marketplace completeness clues
- buyer decision model
- reference cognition extraction
- section/page/screen structure map
- section layout pattern mix from the Section Layout Extraction Library when active
- visual motif and effect language
- layout gesture, section silhouettes, composition tension, focal path, negative-space shape, depth layering, module scale variation, and breakout behavior
- color-role system
- gradient logic
- surface-depth system
- shadow, glow, blur, border, and overlay rules
- CTA and focal-object emphasis behavior
- media placeholder treatment
- design-system logic and a physically separate design-system artifact when output is a multi-template Figma/source pack
- screenshot or rendered inspection when possible
- pattern lock after build
- scaffold disposal receipt before the next template starts

Do not merge all references into one global mood. Do not let template 1 become the subconscious builder for template 2.

## Required Per-Template Cycle

For each template, complete this full cycle before starting the next one:

1. Product family classification
2. Reference selection specific to this template
3. Reference cognition extraction
4. Structure fingerprint
5. Visual-language fingerprint
5a. Section-pattern fingerprint: stable catalog pattern IDs, density limits, compatible-before/after logic, and divergence notes
6. Output contract
7. Build
8. Build that template's own design-system board/frame/source section
9. Screenshot/render/visual inspection of the template and design-system board when possible
10. Quality gate
11. Similarity diagnosis vs reference and previous accepted outputs
12. Pattern lock only after the design-system board passes
13. Scaffold and design-system panel disposal receipt
14. Start next template from a fresh cycle

This is the "One Template = One Full Cycle" gate. If any step is skipped, do not proceed to the next batch item.

### Product-Grade Design-System Batch Gate

For multi-template Figma/source packs, each template pair is not complete until its design-system board is product-grade. Product-grade means the board is a buyer-usable source product kit, not a compact style summary.

Before starting Template N+1, Template N's design-system board must include:

- Product DNA and reference learning boundary for that template.
- Foundations: color, type, spacing, grid, radius, border, surface depth, and effect/gradient rules.
- 8 or more actual template components.
- 4 or more state/variant examples.
- 3 or more product-specific modules tied to that template category.
- 3 or more reusable section patterns.
- Placeholder/media replacement guidance.
- Responsive and editability rules.
- Visual-language rules and usage examples.
- Package/source map and source hygiene receipt.
- Board artifact metrics in the design-system receipt: frame/page ID, screenshot/render path, panel count, component specimen count, product-specific module count, state example count, and dimensions when available.

If the design-system board can be built by swapping only title, color tokens, and two or three generic specimens, diagnose root cause as design-system panel scaffold reuse. The repair is not recolor. Rebuild the board's component taxonomy, product-specific modules, pattern modules, visual-language blocks, package/source map, and documentation rhythm from that template's category.

If the board is shorter than product-grade coverage, visually sparse, or equivalent to "color + type + buttons + cards + rules", block Template N+1 and rebuild the board before continuing.

## Serial Provenance Gate

The gate must inspect how the work was produced, not only the finished screenshot.

Hard failures:

- all templates were generated from one page-level builder, section factory, or data array
- one Figma write operation builds more than one final template source frame
- one Figma write operation builds more than one final design-system board
- multiple template cognition receipts, fingerprints, or design-system receipts are created together with identical line counts or identical field morphology
- Template 2 starts before Template 1 is locked and scaffold-disposed
- Template 3 starts before Template 2 is locked and scaffold-disposed
- post-build audit for a multi-template website/Figma/source build runs without a build-session lifecycle ledger

The existence of distinct fingerprints is not enough. A fingerprint can be fake evidence when it was produced by the same builder that produced sibling templates. The gate must prefer lifecycle order, per-cycle screenshots, per-cycle repairs, scaffold disposal receipts, and build artifacts that show a single-template scope.

Allowed shared code is limited to primitive utilities: color parsing, font loading, text creation, simple shape helpers, spacing constants, screenshot plumbing, and API-safe boilerplate. These utilities must not decide hero grammar, section sequence, module/card/grid cadence, proof/CTA/footer closure, visual motif, or design-system panel order.

## Stronger Anti-Scaffold Rule

- Do not reuse the same hero grammar.
- Do not reuse the same section sequence.
- Do not reuse the same card cadence.
- Do not reuse the same CTA closure.
- Do not reuse the same image-placeholder treatment.
- Do not reuse the same gradient, effect, or surface-depth grammar.
- Primitive helper code may be reused.
- Page-level builders, section arrays, and layout scaffolds may not be reused across batch outputs.

## Reference Proximity Rule

For each template, the output should feel derived from that template's own selected reference insight, not from another template in the batch.

Before building, answer:

- Which reference insight is this template moving toward?
- Which earlier accepted template pattern is this template moving away from?
- Which product-specific structure makes this output belong to its own niche?
- Which section grammar would make it too similar to an earlier output?

If the current idea feels more like a variant of a previous Codex-built template than a reinterpretation of the selected reference, stop and rebuild the structure plan.

## Structure Fingerprint Gate

Before any build, write a structure fingerprint. It must include:

- opening strategy
- hero grammar
- navigation model
- section order
- mid-page cadence
- dominant module types
- proof/trust placement
- conversion or CTA closure
- footer closure
- closure silhouette, especially the visible proof/CTA/footer ending shape
- visual motif
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
- effect language
- color-role system
- density rhythm
- design-system panel logic

For template 2 and later, compare this fingerprint against every accepted earlier fingerprint before building.

If the new fingerprint shares the same opening strategy, hero grammar, section sequence, dominant module types, CTA closure, and footer closure with any earlier template, the plan fails before implementation.

If the new fingerprint shares the same section catalog pattern mix or section-pattern ID set with any earlier template, the plan fails before implementation. Repair by selecting different stable PASS patterns and recomposing affected sections, not by recoloring or rewriting copy.

The fingerprint must also include a reference-standard note. If the selected references show richer section depth, more varied layout shapes, stronger color interplay, or visible effects/gradients, the candidate must either reinterpret those standards or document why a restrained alternative has equal product value. "Minimalist" is not a valid explanation by itself.

## Section-Level Closure Silhouette Gate

Full-page difference is not enough. A batch also fails when a single high-visibility section, especially the final proof, CTA, contact, checkout, inquiry, or footer closure, reads like a sibling of another template.

Before final delivery:

- Inspect the zoomed-out silhouettes of every major section, not only the whole-page thumbnail.
- Compare the last 1-2 conversion/footer sections pairwise against accepted templates.
- Name the local closure grammar: split panel, drawer, receipt rail, paper sheet, timeline spine, booking tray, ledger footer, editorial colophon, dashboard command bar, or another product-fit shape.
- If two templates share the same local closure grammar, such as light content/form/FAQ panel on one side plus dark CTA/footer block on the other, the newer template fails even if the page structure, color, copy, and niche differ.
- Repair by recomposing the affected closure section into a new product-specific action model. Do not repair this defect with recolor, copy rewrite, radius changes, or spacing tweaks.
- Add `closureSilhouette` to the structure fingerprint when the output is a multi-template batch or has a prominent conversion/footer ending.

## Visual-Language Fingerprint Gate

Before any build, write a visual-language fingerprint. It must include:

- palette role map: background, surface, text, accent, CTA, highlight, warning/success if relevant, plus whether A+B, A+B+C, or a richer A-G role map works coherently
- gradient logic: where gradients appear, what they prove, how they help differentiation, and why they are not decorative filler
- effect language: shadows, glow, blur, overlays, glass, hairline borders, inner shadows, or deliberate restraint
- surface-depth grammar: flat, layered, floating, inset, editorial shelf, console, product stage, card deck, or another named system
- focal-object treatment: how product, media, hero, CTA, form, dashboard, or proof modules gain emphasis
- image/media placeholder treatment: crop rhythm, text clue wording, overlays, and replacement expectations
- CTA behavior: quiet, urgent, premium, technical, editorial, ecommerce, lead-gen, booking, or another product-fit mode
- density rhythm: where the page is calm, dense, proof-heavy, visual-led, or conversion-led
- design-system evidence: semantic paint/effect styles or documented effect rules when Figma/design-system output is requested

For template 2 and later, compare this visual-language fingerprint against every accepted earlier fingerprint before building. If two templates share the same effect grammar, gradient placement, surface-depth system, CTA behavior, media-placeholder treatment, and color-role map, the plan fails even when the structure is different.

Do not wait for the user to mention gradients or effects. If the product family or reference insight benefits from depth, light, material, signal, editorial polish, or tactile surface cues, apply a functional effect/gradient pass automatically. If the correct design move is restraint, document why restraint is the visual-language choice and how hierarchy is created without effects.

## Root-Cause Similarity Diagnosis

When two templates feel similar, diagnose the cause before revising.

Use this decision ladder:

1. Structure similarity:
   - Same hero grammar, section order, card cadence, proof placement, CTA rhythm, or footer closure.
   - Same layout gesture, zoomed-out section silhouettes, closure silhouette, focal path, breakout behavior, or negative-space shape.
   - Required action: rebuild the newer template from a fresh structure fingerprint.

2. Composition similarity:
   - Different section names but same title/media placement, grid rhythm, card grouping, or visual balance.
   - Required action: recompose the affected sections; do not solve with color alone.

3. Effect similarity:
   - Same glow, shadow, blur, border, gradient light, surface depth, or placeholder treatment.
   - Required action: redesign the effect language semantically for the product.

4. Visual-language weakness:
   - The template is clean, different, and structurally acceptable, but feels flat, under-art-directed, generic, or lacks functional gradient/effect/surface hierarchy.
   - Required action: run an effect/gradient pass, add or sharpen semantic effect tokens, apply the system to focal modules, and screenshot-inspect the result before continuing.

5. Color similarity only:
   - Structure and composition are distinct, but palette or color-role mapping feels too close.
   - Required action: change the color-role system only. Do not rebuild good structure unnecessarily.

6. Copy/naming similarity only:
   - Structure, composition, effects, and color are distinct, but wording or naming rhythm repeats.
   - Required action: rewrite names, labels, metaphors, and content tone only.

Do not use a large rebuild for a color-only defect. Do not use recolor for a structure defect.

## Pairwise Batch Gate

For template 2 and later:

- Compare the current template against every accepted earlier template.
- Keep the earlier accepted template as the fingerprint unless it has its own quality defect.
- If the current template reaches 10 percent similarity on structure-defining axes, rebuild the current template.
- Do not present final batch output until every pairwise comparison passes.

Structure-defining axes include:

- section/page/screen order
- hero grammar
- composition grammar
- layout gesture
- section silhouette sequence
- focal path
- negative-space shape
- breakout behavior
- module/card/grid grouping
- CTA/proof/footer closure
- closure silhouette, especially final proof/CTA/contact/footer sections
- visual motif
- effect language
- gradient logic
- surface-depth system
- color-role mapping
- CTA behavior
- media placeholder treatment
- design-system panel logic

Color-role mapping is important, but color-only similarity should trigger recolor, not structural rebuild.

## Per-Template Design System Separation Gate

For multi-template Figma/source packs, design-system separation is a batch originality gate, not only documentation hygiene.

Each accepted template must have its own visibly separate design-system frame, page, or source section. It must be named for that template and contain template-specific product DNA, tokens, component specimens, states, product-specific modules, reusable section patterns, placeholder guidance, visual-language rules, package/source map, and source/editability notes.

A combined pack-level board may document references, governance, similarity, or receipts, but it cannot count as any template's design system. If the combined board exists, label it as audit summary only.

If the design-system frames look like duplicated panels with only color/name swaps, diagnose root cause as design-system panel logic similarity and revise the component examples, product-specific modules, reusable section patterns, token emphasis, package/source map, and documentation rhythm to match each template's fingerprint.

Before final delivery, screenshot-inspect the separated design-system frames. If any frame is cramped, clipped, misaligned, or visually rough, repair it before presenting output.

## Reference Separation Gate

- Every batch item must have its own reference cognition.
- Never use one reference to generate multiple supposedly different templates unless the user explicitly asks for that.
- Never let one reference pool become a generic batch moodboard.
- If a template cannot name its own reference insight and the earlier pattern it must avoid, it fails the gate.

## Section Depth Gate

- Full website/template output must not collapse into a minimalist 4-6 section scaffold.
- Enforce product-family section, screen, state, or module depth standards before visual polish.
- Do not use "minimal", "clean", "safe", "simple", or "premium" as an excuse for shallow structure.

## Evidence Gate

- Do not claim visual similarity pass without screenshot/render inspection.
- If no visual inspection was done, mark similarity as structural/textual heuristic only.
- Do not claim reference-led local selection happened when the local corpus has zero candidates.

## Failure Handling

- If any gate fails, do not continue to the next batch item.
- Diagnose the root cause before fixing: routing, depth, structure, composition, visual language, color role, typography, spacing, CTA, placeholder, source hygiene, originality, or visual evidence.
- Fix root cause, re-run the gate, then proceed.

## Scaffold Disposal Gate

After each template is accepted, dispose of the page-level scaffold before starting the next one.

Discard:

- hero builder
- section schema
- card/grid cadence
- proof/pricing/CTA rhythm
- footer closure
- design-system panel order
- page-level data arrays
- generated scratch builders
- implementation outline that controls page grammar

Retain only primitive helpers:

- color parsing
- font loading
- text creation
- simple shape creation
- spacing constants
- API boilerplate
- screenshot/report plumbing

Pattern locks are negative memory. They record what must not repeat; they are not reusable builders.

## Pre-Output Quality Gate

Before presenting a batch output, confirm:

- each template has its own reference-led cycle record
- each template has a structure fingerprint
- each template has a visual-language fingerprint
- every prior accepted fingerprint has been checked
- each scaffold disposal receipt exists after each accepted template
- each new template started only after the previous template was locked and scaffold-disposed
- receipt morphology does not show same-line-count, same-field, all-at-once generation across the batch
- no build artifact or Figma write receipt shows multiple final templates created by one page-level scaffold
- rendered screenshots or visual inspection were performed when possible
- effect/gradient quality was inspected and revised when the first pass felt flat, decorative, copied, or too weak
- product-type section depth is complete
- Figma outputs include real auto-layout for editable structure and an auto-layout receipt
- multi-template Figma/source outputs have physically separated per-template design-system artifacts, not one shared board
- every separated design-system artifact was visually inspected and tidied before final output
- similarity root cause has been diagnosed if anything feels close
- effect similarity was solved with a new semantic effect language, not only opacity tweaks
- color-only similarity was solved with palette/role changes
- structure similarity was solved with rebuild, not recolor
- layout stiffness was solved with a new spatial gesture, section silhouette sequence, focal path, or controlled composition tension, not with decoration
- local closure similarity was solved with a new action-model silhouette, not with recolor, copy, radius, or spacing tweaks

If any item is missing, the batch is not done.

## v2.5 Sequential Layout Originality Gate

Batch work must run through a build-session lifecycle. Template B cannot start until Template A is fingerprint locked. Template C must compare against Template A and Template B. Template D must compare against A, B, and C.

Every new batch template must have:

- reference layout fingerprint
- candidate layout fingerprint
- reference-vs-AI layout audit
- AI-vs-previous-AI pairwise layout audit for Template 2 and beyond
- design system receipt
- post-build audit receipt
- fingerprint lock

Pairwise comparison must be axis-based: hero grammar, section order, grid, layout gesture, section silhouettes, closure silhouette, composition tension, focal path, negative-space shape, depth layering, module scale variation, breakout behavior, rhythm, component cadence, CTA placement, image treatment, typography behavior, color roles, effect language, navigation/footer pattern, and scaffold risk. Recolor or image replacement is not a valid repair when any structure-defining axis fails.
