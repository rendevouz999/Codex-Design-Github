---
name: design-critic
description: Use this skill when creating, reviewing, or improving UI, frontend, landing pages, dashboards, components, design systems, preview layouts, Figma-like layouts, or marketplace-ready design templates. It provides a senior UI/UX art director critique workflow for visual hierarchy, spacing rhythm, typography scale, composition balance, brand consistency, CTA clarity, accessibility, responsiveness, marketplace presentation quality, and emotional direction.
---

# Design Critic

For visual inspection during plugin work, load `.design-brain/VISUAL_INSPECTION_PROTOCOL.md`. Main and the single Engineer use current-source overview, targeted full-resolution crops, and a return to whole-frame context. Record actual observations and unresolved checks; generated images, metadata, screenshot presence and another agent's verdict alone cannot establish visual PASS.

Use this instruction-only skill as the repo-local senior UI/UX art director workflow for design work. The job is to push the design past a first draft into something practical, polished, production-ready, and intentionally art-directed.

## Source-of-Truth Awareness

Before reviewing template/reference work, check whether the task requires source-of-truth loading:

- designer cognition
- reference insight
- template product workflow
- naming originality
- originality guard
- marketplace quality gate

Use `.design-brain/AUTOLOAD_POLICY.md` and `.design-brain/CONTEXT_PRIORITY.md` to decide what to load.

Design Critic is a craft support layer, not a source-of-truth override. If this skill conflicts with Design Cognition Contract, Design Simulation Layer, Sequential Layout Originality Gate, Build Session Lifecycle, Design System Build Requirements, Post-Build Completion Gate, or completion receipt status, those Brain Design gates win. Treat Design Critic output as repair guidance only.

## Natural Workflow Awareness

When reviewing design work, infer whether the task needed Designer Cognition Layer, reference insight, Sequential Reference-Led Batch Workflow, naming originality, template orchestration, or visual review. Do not wait for the user to mention those workflow names.

If the user says the design is too similar, generic, less premium than expected, structurally repetitive, or based on a reference, activate the relevant Design Brain workflow internally before critique. Treat internal scripts as support tools, not user-facing rituals.

For advanced template work, identify the medium before critique. Website templates, PowerPoint decks, dashboards, UI kits, brand kits, portfolios, and marketplace previews should not share one generic landing-page rubric.

For Figma website template work, identify the website product family before critique using `.design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.md`. Landing page is only valid when the brief explicitly asks for landing, campaign, lead-generation, sales-page, squeeze-page, or waitlist intent.

For website-template work, use `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md` and the local `Template Website` preview corpus as product-type evidence before accepting assumed section depth, density, proof placement, or buyer completeness.

For Figma reference-link work, load `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md` and `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md`. Reject plans that use a Figma reference without studying product purpose, visual direction, section structure, grid/layout, typography hierarchy, color-role system, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, Figma source hygiene, page/frame/component/state scheme, product-family standard, color/effect function, and do-not-copy boundary. Unknown standard must trigger more evidence, corpus/category lookup, or one targeted question, not a minimalist fallback.

For Figma source-template work, load `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md`. Reject designs whose editable structure is primarily manual x/y positioning. Major sections, nav, cards, CTAs, forms, repeated rows, dashboards, and design-system panels must use real auto-layout, with only documented decorative or overlay exceptions.

For editable template-source work, use `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`. Reject generated or final imagery in source-template image zones unless the user explicitly requested images. Reference images should become product-specific text clue placeholders such as `image placeholder: [purpose]` or `profile photo placeholder: [role]`, not forced generated content.

For multiple-template critique, reject the all-at-once batch pattern. Load `.design-brain/BATCH_TEMPLATE_HARD_GATES.md` and check whether each template was produced through its own reference study cycle: buyer decision model, 2-3 execution references, evidence-backed designer cognition, inferred purpose/audience, extracted structure/visual logic, one complete build, and a locked pattern memory before the next template started.

When multiple outputs feel similar, diagnose the root cause before prescribing changes. Structure similarity requires a rebuild of the newer template. Layout stiffness requires a new spatial gesture, section silhouette sequence, focal path, or composition-tension strategy. Composition similarity requires recomposition. Effect similarity requires a new effect language. Color-only similarity requires recolor only. Copy/naming-only similarity requires rewrite only.

## Design-Anything Module Selection

Before planning or critiquing any substantial template, deck, dashboard, UI kit, brand kit, mobile UI, email/newsletter, poster/static canvas, or document/report, run or mentally follow the module selector first:

```bash
python scripts/design_brain_module_select.py --task "..." --template-type "..." --niche "..." --target-buyer "..." --visual-mood "..." --dry-run
```

Use the selected module to load the right craft files, seed pack, direction pack, and validators. This prevents Design Brain from defaulting every product into a landing-page structure.

## Workflow

1. Read `.design-brain/DESIGN_MEMORY.md`.
2. Read `.design-brain/DESIGN_PREFERENCES.json`.
3. Check `.design-brain/PATTERN_LIBRARY.md` for relevant reusable patterns.
4. For reference/template/batch work, read `.design-brain/DESIGNER_COGNITION_LAYER.md` and identify buyer decision model, evidence-backed designer intent, attention strategy, emotional rhythm, trust strategy, density strategy, conversion logic, and component reasoning.
5. Review the task and identify the target medium, audience, content density, brand mood, primary CTA or slide/action goal, and success criteria.
6. Create or inspect the first design result.
7. Critique the result using `.design-brain/VISUAL_CRITIQUE_CHECKLIST.md`.
8. Identify weak areas and name the concrete cause of each issue.
9. Propose specific revisions that can be implemented directly.
10. Apply revisions when working on code or editable design files.
11. Re-check the revised result against the weakest categories.
12. Save important user feedback into `.design-brain/REFLECTION_LOG.md`.

## Review Report Command

For substantial design tasks, generate a structured review report as an optional but recommended step:

```bash
python scripts/design_brain_review.py --task "..." --target "..." --notes "..."
```

Use this report after inspecting the UI, code, screenshot, mockup, or rendered output. The command creates a template with design memory, preference weights, scoring placeholders, weak areas, revision planning, and a reflection lesson candidate. It does not visually analyze the target by itself.

## Visual Review Workflow

Inspect a screenshot, browser view, or rendered UI whenever visual quality matters. Generate a visual review report when evidence is available:

```bash
python scripts/design_brain_visual_review.py --task "..." --target "..." --screenshot ".design-brain/screenshots/..." --notes "..."
```

If using a URL reference instead of a screenshot, include it with `--url`; the script does not capture the URL by itself. Compare before/after screenshots manually when available, then turn repeated visual issues into reflection lessons with `design_brain_reflect.py`. Never claim screenshot analysis or visual inspection unless actual visual evidence was inspected.

## Real Project Pilot

Use pilot reports for the first substantial UI/design task in a new real project:

```bash
python scripts/design_brain_pilot.py --project-root "PROJECT_ROOT" --task "..." --target "..." --notes "..."
```

Verify Design Brain installation with `design_brain_status.py` before relying on local memory, preferences, review scripts, or reflection tools. Create a baseline review, create a visual review when screenshot, URL, browser, or rendered evidence exists, revise before the final answer, and save useful feedback through controlled reflection. Do not modify stable memory or claim visual inspection without evidence.

## Template Product Critique

Use the Template Product Intelligence layer when creating or reviewing a sellable template product:

```bash
python scripts/design_brain_template_plan.py --template-type "..." --niche "..." --target-buyer "..." --visual-mood "..."
python scripts/design_brain_style_select.py --template-type "..." --niche "..." --target-buyer "..." --visual-mood "..."
```

Before designing, read:

- `.design-brain/TEMPLATE_PRODUCT_INTELLIGENCE.md`
- `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`
- `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md` when a Figma reference/link/template source is used
- `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md` when a Figma template reference or professional designer learning task is used
- `.design-brain/FIGMA_REFERENCE_LEARNING_CORPUS.md` when the user-provided Figma material links are relevant
- `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md` when output is Figma
- `.design-brain/MEDIUM_PRODUCT_PLAYBOOKS.md`
- `.design-brain/ADVANCED_STYLE_GRAMMAR_MATRIX.md`
- `.design-brain/HUMAN_CRAFT_HEURISTICS.md`
- `.design-brain/TEMPLATE_STYLE_ROUTER.md`
- `.design-brain/TEMPLATE_STYLE_PACKS.json`
- `.design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md`

When reviewing a template product, evaluate:

- whether the template concept is clear
- whether the website product family is explicit when the product is a Figma website template
- whether the selected style pack fits the niche and buyer
- whether section structure supports the product type
- whether the section/page/screen count meets the standard for that product type, not merely a reduced first pass
- whether a Figma reference schema receipt exists when a Figma reference was used
- whether the professional Figma template reading order was completed before structure planning
- whether the receipt studied pages, frames, sections, components, variants, states, design-system panels, and product-family standard before planning
- whether editable placeholders are obvious
- whether image areas use text clue placeholders instead of unrequested generated imagery
- whether Figma outputs include real auto-layout for editable structure and an auto-layout receipt
- whether preview/cover direction can sell the template
- whether the design is reusable across client projects
- whether the product feels marketplace-ready
- whether the design avoids generic AI output
- whether the structure fits the medium and product type
- whether human craft is visible through rhythm, restraint, hierarchy, and buyer specificity

Evaluate whether the design works as a sellable template product, not just as a single attractive screen. Check template type, buyer fit, marketplace category, section logic, component completeness, editability, reusable structure, responsive preview coverage, cover/preview quality, marketplace value, and visual differentiation. A strong template product should be easy for a buyer to adapt, credible in its category, and presented with a premium cover and overview system.

Reject generic template output when the design lacks a clear buyer, repeats interchangeable sections, hides the actual product behind decorative mockups, ignores editable structure, or does not show enough marketplace value.

Reject underbuilt template output even when it looks clean and different from the reference. Do not carry old task-specific omissions such as "no components", "no devices", "no cover/preview", or "desktop only" into new briefs as persistent bans. Product depth, components, responsive/device views, and preview/cover surfaces should be decided from the current request, product category, and marketplace standard.

Reject website, web-template, Figma website-template, and standard landing-page templates with fewer than 8 meaningful sections/blocks unless the brief explicitly asks for a hero/header kit, micro landing page, narrow campaign, squeeze page, waitlist page, or another intentionally small product. Minimalist, clean, safe, simple, fallback, restrained, or basic visual language is not an acceptable reason for under-8 structure.

Reject reference-based output when "minimalist" is used to skip the reference standard. Reference standard means observed structure depth, section roles, layout-shape variety, color-role behavior, effect/gradient behavior, and marketplace completeness. The output can be quiet, but it cannot be thin or flat if the reference/category standard is richer.

Use TypeUI-derived skills as selected style constraints. Never blindly merge all TypeUI skills into one design direction.

## Template Product Orchestration Review

When reviewing a template product, check whether the design followed an orchestration plan:

- style strategy matches niche and buyer
- structure matches template type
- preview direction can sell the product
- editability is clear
- quality gate is satisfied
- output avoids generic AI design

For substantial sellable template tasks, create or follow an orchestration report before judging visual polish:

```bash
python scripts/design_brain_template_orchestrate.py --template-type "..." --niche "..." --target-buyer "..." --visual-mood "..." --notes "..."
```

## Sequential Batch Critique

For batch template creation or revision, use `.design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md` as the source of truth.
Also use `.design-brain/BATCH_TEMPLATE_HARD_GATES.md` as the hard stop for scaffold reuse, root-cause diagnosis, and pre-output delivery checks.

Evaluate each output as its own cycle:

- which 2-3 references were selected for that template
- whether Codex inferred buyer decision model, designer intent, attention strategy, emotional rhythm, trust strategy, density strategy, conversion logic, component reasoning, and marketplace role
- whether Codex extracted the reference standard: section count/range, section roles, layout-shape inventory, color-role inventory, effect/gradient inventory, and marketplace completeness clues
- whether major designer-cognition claims included observed evidence, inferred reason, user/buyer effect, reusable logic, originality transformation, and confidence level
- what do-not-copy boundary was defined
- whether the template was completed before starting the next one
- what pattern memory was locked after the build
- whether later templates stayed below 10 percent similarity against every accepted previous template fingerprint
- whether later templates avoided at least 90 percent of the previous opening strategy, hero grammar, trust strategy, density rhythm, component system, CTA logic, visual motif, and storytelling arc
- whether later templates avoided repeating effect language, gradient logic, surface-depth grammar, CTA behavior, color-role map, and media-placeholder treatment
- whether later templates avoided repeating layout gesture, section silhouettes, focal path, negative-space shape, module scale variation, and breakout behavior
- whether later templates avoided repeating local closure silhouettes in final proof, CTA, contact, checkout, inquiry, and footer sections
- whether the newer template is closer to its selected reference insight than to a previous Codex-built output
- whether similarity was diagnosed as structure, composition, effect, visual-language weakness, color-only, or copy/naming-only before revision
- whether an applied effect/gradient pass was visible on the rendered template when the product family or reference logic called for depth, light, material, signal, or surface hierarchy

Fail the critique if multiple templates share one scaffold with different colors, copy, images, niche labels, or superficial card variations.
Fail the critique if output was presented before pairwise batch similarity passed below 10 percent.
Fail the critique if a structural similarity defect was solved only by recoloring.
Fail the critique if a stiff or sibling-like layout was solved only with color, copy, decoration, or effects instead of a changed spatial gesture/silhouette/focal path.
Fail the critique if an attached screenshot or local section view shows two endings share the same closure silhouette, even when the full page structures differ.
Fail the critique if the batch is clean and structurally different but missing a distinct visual-language fingerprint per template.
Fail the critique if colors are flat or underexplored and no color-relationship check explains why the selected A+B, A+B+C, or richer A-G role map works.
Fail the critique if effects/gradients exist only as design-system notes and are not applied visibly to focal modules when the medium benefits from them.
Fail the critique if a Figma template uses manual x/y positioning as the primary editable structure or lacks an auto-layout receipt.
Do not fail the structure if the only defect is color-role similarity; require recolor and re-audit instead.

### Batch Visual-Language Critique

For multi-template work, critique visual language as a first-class axis. Do not wait for the user to mention effects, gradients, glow, shadow, blur, overlays, or surface depth.

For each template, require:

- a visual-language fingerprint distinct from prior accepted templates
- semantic effect roles or deliberate restraint
- gradient logic tied to hierarchy, material, mood, proof, or conversion
- surface-depth grammar for hero, cards, product/media zones, proof modules, forms, dashboards, or CTA areas
- color-role independence, not only different hex values
- color-relationship reasoning: why the selected palette roles work together for mood, CTA hierarchy, contrast, buyer trust, and batch differentiation
- CTA behavior that fits the product and differs from prior templates when possible
- media-placeholder treatment that is product-specific and not a reused crop/box pattern
- screenshot evidence or visual-inspection notes showing the effect/gradient system is visible and useful

Reject a batch item if it is visually neat but emotionally flat, under-art-directed, or only different through section order. Apply an effect/gradient/surface-depth pass before final delivery, or document deliberate restraint with evidence of how hierarchy is created without effects.

### Batch Implementation Critique

For Figma, HTML, or generated design work, inspect the implementation method as part of critique when outputs look similar.

Reject the work if:

- multiple templates were produced from one whole-page builder or section schema
- the same function controls hero grammar, section order, card/grid/table placement, CTA rhythm, or footer closure across the batch
- differences are mostly copy, palette, icon, image placeholder, niche label, or token values
- screenshots show two outputs could be mistaken for variants of the same template family
- screenshots show a repeated final-section shape, such as light form/FAQ/content panel plus dark CTA/footer block
- two outputs share the same opening strategy, hero grammar, component system, rhythm map, and CTA logic
- two outputs share the same effect/gradient/surface-depth grammar, CTA behavior, or media-placeholder treatment
- a newer output reaches 10 percent similarity against an accepted earlier template
- there is no scaffold disposal record between completed templates
- the next template reuses the previous template's Figma script outline, page schema, design-system panel order, or section cadence as a convenience
- the previous scaffold remains in active context and is reread, copied, mutated, or data-swapped for the next template
- a later template is visually closer to a previous template than to its own selected reference insight
- no root-cause similarity diagnosis exists before the revision decision
- no applied effect/gradient quality pass exists for a visually rich template category

Primitive helpers are fine. Page-level scaffolds are not. If this gate fails, do not continue polishing; rebuild the similar templates with separate structure fingerprints and fresh reference cycles.

If the only failing axis is color-role mapping, do not rebuild the whole page; change the palette and color roles, then rerun the visual and pairwise audit.

### Scaffold Disposal Critique

After reviewing one batch item, confirm that its implementation scaffold was disposed before the next item started. A valid disposal record names the spent hero grammar, section sequence, module/card/grid grammar, CTA/proof/footer closure, design-system panel order, which temporary scaffold artifacts were deleted or removed from active context, and which primitive helpers were retained.

Treat the pattern lock as negative memory only. If the next template appears to inherit the previous page grammar, reject the batch even if the reference similarity score for each individual template is acceptable.

## Lint And Technical Review Tools

Use these when the risk matches the task:

- `scripts/design_brain_lint_plan.py` before designing to catch generic section order, missing states, weak deck roles, and missing responsive/design-system logic.
- `scripts/design_brain_lint_artifact.py` after HTML/CSS/text output to catch filler copy, default palettes, raw-token misuse, and weak responsive signals.
- `scripts/design_brain_external_corpus_index.py` to create generated selective indexes for local reference repos without promoting them into stable memory.
- `skills/presentation-deck/runtime/design_brain_pptx_inventory.py`, `skills/presentation-deck/runtime/design_brain_pptx_render_contact_sheet.py`, `skills/presentation-deck/runtime/design_brain_pptx_visual_corpus_study.py`, `skills/presentation-deck/runtime/design_brain_pptx_thumbnail_review.py`, and `skills/presentation-deck/runtime/design_brain_pptx_frame_precision_review.py` for presentation template/deck work.
- `skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs` and `skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs` for web deck, HTML presentation, and animated slide work; run both with `node` and treat the render review as the rendered-evidence source.

## Reference Originality Critique

When reviewing reference-based template work, evaluate:

- whether the output copies the reference too closely
- whether insight was extracted before designing
- whether layout and section structure were reinterpreted
- whether naming feels recycled
- whether the final product is original and marketplace-ready

Use `.design-brain/ORIGINALITY_GUARD.md` as the anti-copy gate. A reference should produce a reusable lesson and a new structure, not a cloned layout with different copy or colors.

When similarity risk is high, use `.design-brain/REFERENCE_DECONSTRUCTION_MATRIX.md`, `.design-brain/ORIGINALITY_SIMILARITY_SCORECARD.md`, and `scripts/design_brain_originality_score.py` to compare section/slide order, composition, spacing rhythm, motif, component grouping, title/media placement, color-role mapping, naming, preview staging, and product-type fit.

For reference-based work, reject copied palettes as well as copied layout. The reference palette should be translated into color-role insight, then reconstructed for the new product type, buyer, marketplace category, accessibility, and intended emotion. A different shade of the same accent/CTA/background system is not enough.

For PowerPoint, Google Slides, Keynote, pitch deck, or presentation template tasks, use `skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md`. Critique decks as slide systems with slide roles, master/layout logic, safe margins, footers, chart/table rules, and thumbnail readability.

After a deck template looks visually complete, run a per-frame precision pass before calling it polished. Inspect each slide at normal size for overlap, near-collision, tangent spacing, title/content clearance, safe-margin drift, footer clearance, baseline drift, and placeholder stress. A contact sheet can prove rhythm but cannot prove local placement accuracy.

For web deck, HTML presentation, animated slide, browser deck, interactive deck, or deck-to-web tasks, use `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md`, `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`, and `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md` instead of the static deck rubric. Critique the deck as a runtime stage: stage fit at the authored 1920x1080 size and at smaller and taller viewports, reveal order against the planned step sequence, motion signature divergence from every previously built deck, runtime navigation across keyboard, pointer, wheel, and deep link, the reduced-motion path, and the print path that produces one slide per page. Static PPTX, Keynote, and Google Slides deliverables stay on the presentation-deck rubric.

A web deck critique requires rendered evidence. Open the deck in a browser or inspect the per-slide captures from `skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs` before judging stage fit, reveal timing, overlap, chrome placement, or motion quality. Reading the HTML, CSS, and runtime source proves structure, not rendered placement; pair it with `skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs` for the static contract, and never claim a web deck passed on code reading alone.

For valuable references, store insight with:

```bash
python scripts/design_brain_reference_insight.py --reference-name "..." --lesson "..." --do-not-copy "..." --reinterpretation "..."
```

Before committing to a template name, check it with:

```bash
python scripts/design_brain_name_check.py --candidate-name "..." --niche "..." --template-type "..." --dry-run
```

After a template product direction is accepted, record it with:

```bash
python scripts/design_brain_build_record.py --template-name "..." --template-type "..." --niche "..."
```

## Senior Art Director Review Criteria

Evaluate:

- Visual hierarchy: one clear focal point, obvious content priority, and no competing hero elements.
- Spacing rhythm: consistent spacing scale, breathable sections, and no cramped or accidental gaps.
- Typography scale: readable body text, clear heading levels, useful emphasis, and no mismatched type moods.
- Composition balance: stable layout weight, clean grouping, intentional negative space, and strong preview framing.
- Brand consistency: color, shape, tone, imagery, and interaction details match the intended audience and product.
- CTA clarity: primary action is visible, specific, and visually distinct without making the screen noisy.
- Accessibility: sufficient contrast, legible sizing, focus states, semantic controls, and usable hit targets when implemented in code.
- Responsive behavior: layout, text, controls, and imagery adapt cleanly across mobile, tablet, and desktop.
- Marketplace presentation quality: the result feels complete, inspectable, sellable, and ready to present.
- Emotional direction: the design mood is deliberate and appropriate, not generic or accidental.
- Medium fit: the structure matches website, deck, dashboard, UI kit, brand kit, portfolio, or preview logic.
- Originality risk: the output avoids copied order, composition, rhythm, motif, grouping, naming, and preview staging.
- Visual language: color roles, gradients, effects, surface depth, CTA emphasis, and media-placeholder treatment are intentional, visible when needed, and not recycled from another template in the batch.
- Human craft: the result shows intentional tension, rhythm variation, restraint, and product-specific judgement.
- Product-type completeness: the expected sections, slides, states, components, or preview assets are present.
- Standard structure depth: the output meets the normal section/page/screen count for its product type; it is not forced long, not forced minimalist, and not copied one-to-one from the reference. If the standard is uncertain, research the category before approval.

## Critique Rules

- Do not accept a first draft without a critique pass.
- Make at least one concrete improvement after critique when editing is possible.
- Prefer specific visual fixes over vague advice.
- Treat premium feel, hierarchy, whitespace, and consistency as high-weight criteria.
- Avoid generic template-looking output.
- Avoid mistaking visual restraint for product readiness.
- Avoid treating effects and gradients as optional user-requested extras. They are automatic art-direction decisions for template work.
- Avoid documenting effect styles without applying them to the page or screenshot-checking their impact.
- Avoid random decorative elements, inconsistent spacing, overcrowding, weak alignment, and playful roundness unless the brand requires them.
- Keep the output practical and production-ready. Do not overcomplicate the workflow or add speculative tooling.

## Reflection Rule

When the user gives feedback that can improve future design work, use the reflection utility to append a concise entry to `.design-brain/REFLECTION_LOG.md`:

```bash
python scripts/design_brain_reflect.py --task "..." --feedback "..." --went-wrong "..." --lesson "..." --rule "..."
```

Save the lesson, reuse it in future critique and revision, and keep adaptation controlled. Do not change `DESIGN_MEMORY.md` or `DESIGN_PREFERENCES.json` from one feedback item unless the user explicitly asks. Promote a lesson into stable memory only when repeated feedback shows a pattern.

Each reflection entry should include:

- Date
- Task
- User feedback
- What went wrong
- Design lesson
- Rule to reuse next time

## Promotion Proposal Rule

Review repeated feedback through the promotion proposal utility:

```bash
python scripts/design_brain_promote.py --min-count 2
```

Use promotion proposals to identify repeated lessons that may belong in `DESIGN_MEMORY.md`. Never silently rewrite stable memory. Promotion into `DESIGN_MEMORY.md` requires explicit user instruction, and the utility must not change `DESIGN_PREFERENCES.json` or preference weights.

## Operational Tools

- `python scripts/design_brain_status.py`: check required files, JSON validity, reflection count, review count, proposal count, latest reports, and recommended next action.
- `python scripts/design_brain_sequential_batch.py --task "..." --count 5 --reference-root "Template Website" --dry-run`: create an internal per-template reference cycle plan for batch work.
- `python scripts/design_brain_typeui_ingest.py`: normalize TypeUI DESIGN.md files and extract deterministic JSON rules.
- `python scripts/design_brain_medium_playbook.py --task "..." --template-type "..." --niche "..." --target-buyer "..."`: select the correct medium/product-type playbook before visual planning.
- `python scripts/design_brain_originality_score.py --comparison-mode batch --reference-summary "accepted template fingerprint" --proposed-structure "newer template fingerprint" --template-type "..." --dry-run`: enforce the 10 percent pairwise gate before presenting batch work.
- `python scripts/design_brain_originality_score.py --reference-summary "..." --proposed-structure "..." --template-type "..." --dry-run`: score similarity risk before presenting reference-based work.
- `python scripts/design_brain_style_select.py --template-type "..." --niche "..." --target-buyer "..." --visual-mood "..."`: select relevant TypeUI-derived style packs for a template product.
- `python scripts/design_brain_template_plan.py --template-type "..." --niche "..." --target-buyer "..." --visual-mood "..."`: create a marketplace-ready template product plan before designing template products.
- `python scripts/design_brain_template_orchestrate.py --template-type "..." --niche "..." --target-buyer "..." --visual-mood "..."`: create an end-to-end orchestration report for sellable template products.
- `python scripts/design_brain_reference_insight.py --reference-name "..." --lesson "..." --do-not-copy "..." --reinterpretation "..."`: store reusable reference insight without copying the reference.
- `python scripts/design_brain_name_check.py --candidate-name "..." --niche "..." --template-type "..." --dry-run`: check naming originality against the local naming ledger.
- `python scripts/design_brain_build_record.py --template-name "..." --template-type "..." --niche "..."`: record accepted template product direction and update the naming ledger.
- `python scripts/design_brain_pilot.py --project-root "..." --task "..." --target "..." --notes "..."`: create a real project pilot report before the first substantial UI task in a project.
- `python scripts/design_brain_review.py --task "..." --target "..." --notes "..."`: create a structured design review report for substantial UI/design work.
- `python scripts/design_brain_visual_review.py --task "..." --target "..." --screenshot "..." --notes "..."`: create a visual evidence review report from a screenshot or URL reference.
- `python scripts/design_brain_reflect.py --task "..." --feedback "..." --went-wrong "..." --lesson "..." --rule "..."`: append a controlled reflection lesson after useful user feedback.
- `python scripts/design_brain_promote.py --min-count 2`: create a manual promotion proposal for repeated reflection patterns without editing stable memory.
