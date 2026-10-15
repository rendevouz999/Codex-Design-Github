# Originality Guard

The Design Brain must prevent reference copy-paste behavior.

Originality Guard is mandatory for reference-based template work.

Originality is evaluated against both the current reference and past build/naming records. Check `.design-brain/TEMPLATE_BUILD_JOURNAL.md` and `.design-brain/TEMPLATE_NAMING_LEDGER.md` when repetition risk matters.

## Abstract Logic Vs Recognizable Execution

Do not ban abstract reasoning patterns. Reusable thinking such as trust-before-pricing, calm-to-dense rhythm, evidence-before-action, visual proof, attention flow, buyer confidence, progressive disclosure, simplification after complexity, and enrichment where proof is needed can transfer across templates.

Ban recognizable execution patterns: exact composition, exact pacing, exact section treatment, exact component grouping, exact image placement, exact visual motif, exact CTA staging, and the same hero grammar plus same mid-page rhythm plus same conversion closure.

## Anti-Copy Rules

- Do not copy a reference layout directly.
- Do not preserve the same section order unless there is a strong product reason.
- Do not copy the same composition, image placement, spacing rhythm, component arrangement, or visual gimmick.
- Do not copy the full reference palette, exact hex values, gradient sequence, glow color, or the same accent/CTA/background role map.
- Do not merely change colors or text while keeping the structure identical.
- Do not treat a different palette as originality if layout, rhythm, grouping, or CTA logic still follows the reference.
- Do not reuse template names, suffixes, prefixes, or metaphors too closely across similar niches.
- Do not let two outputs in the same batch become siblings from one shared scaffold, even when each output is not too close to its own reference.
- Do not treat design-system consistency as permission to reuse page grammar across different template products.

## Batch Similarity Rules

Reference originality and cross-template originality are separate gates. A template can pass against its reference but still fail because it looks like another template in the same batch.

For batch work, compare every output against prior outputs before continuing:

- opening strategy
- hero grammar
- trust strategy
- density rhythm
- component system
- CTA logic
- visual motif
- storytelling arc
- section order and proof/pricing/footer placement
- focal-object placement

Strict pairwise gate: if the newer output reaches 10 percent similarity against any accepted earlier template, the newer output fails. Keep the earlier accepted template as its own fingerprint and rebuild the newer template from a fresh structure, motif, rhythm, and product-logic direction before presenting it.

If two outputs share the same opening strategy, hero grammar, component system, rhythm map, and CTA logic, redesign the newer output from a new structure fingerprint before presenting it. Later batch cycles must avoid at least 90 percent of the previous cycle's recognizable execution pattern.

## Scaffold Disposal Rule

After each template in a batch and its design-system board are built, its page-level scaffold and design-system panel order become forbidden source material for the next template. This includes the implementation outline, Figma script structure, section order, hero layout, module/card/grid cadence, proof/pricing/CTA sequence, footer closure, and design-system panel order.

Do not proceed from Template N to Template N+1 while Design System Board N is missing, too thin, invalid, or uninspected. A design-system board is part of the current template's originality lock, not a future batch cleanup surface.

Do not reuse a previous template scaffold and modify copy, colors, icon labels, image placeholders, niche terms, or token values. That is a sibling-output failure even when the visual mood changes.

Disposal is permanent for the next cycle's active context. If the scaffold was written as a temporary script, scratch builder, page schema, section map, or data object created only for one template, delete that artifact after recording the negative pattern lock. If it existed only in the implementation plan, stop referencing it and rebuild the next code path from a blank structure fingerprint. Do not delete final designs, user references, screenshots, review reports, reference-insight records, or pattern locks.

Allowed to carry forward:

- primitive utilities
- Figma API stability patterns
- font and color helpers
- screenshot or validation plumbing
- negative pattern locks that describe what must not repeat

Forbidden to carry forward:

- page builders
- section builders
- hero builders
- reusable design-system documentation schemas
- card-grid/list/table cadence
- conversion closure formula
- any previous code path that controls visible information architecture

## Required Explanation

For reference-based work, always explain:

1. Insight learned from the reference
2. Observed evidence and confidence for major designer-cognition claims
3. What abstract logic is reused
4. What recognizable execution is intentionally changed
5. How structure, rhythm, components, color-role mapping, and CTA logic were reinterpreted
6. Why the final template is original
7. How it fits the marketplace/product purpose

## Originality Check Scoring

Score each item from 1-10:

- Reference similarity risk: lower is better
- Structural reinterpretation strength: higher is better
- Naming originality: higher is better
- Marketplace distinctiveness: higher is better

If reference similarity risk is above 6, redesign the structure before presenting the final direction.

If naming originality is below 7, run `scripts/design_brain_name_check.py` and generate a different naming direction.

## Advanced Similarity Axes

When the user says the result feels identical, copy-paste, generic, or too close to the source, compare:

- Section or slide order.
- Composition and focal-object placement.
- Spacing rhythm and density cadence.
- Visual motif, shapes, lines, gradients, or image masks.
- Component grouping, card clusters, metric groups, team/profile groups, and pricing/rate blocks.
- Title and media placement.
- Color-role mapping, including exact palette, accent role, CTA color, background logic, surface tones, glow color, and proof/highlight behavior.
- Naming metaphor.
- Marketplace cover or preview staging.
- Product-type fit.

Use `scripts/design_brain_originality_score.py` for a deterministic dry-run score when the reference and proposed structure can be summarized in text.
