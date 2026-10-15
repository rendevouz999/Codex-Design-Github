# Quality Gate Failure Taxonomy

## Design Cognition Contract Failures

- cognition_contract_missing: Design Cognition Receipt is missing for a reference-led template build.
- color_identity_copy: output keeps the reference dominant color identity, exact palette, or exact hue family without explicit user request.
- reference_boundary_violation: plan copies or fails to forbid exact layout, palette, section order, hero grammar, component scaffold, image placement, or signature color identity.
- weak_visual_grammar: grid, spacing, type, color roles, surface depth, image treatment, effect logic, or component rhythm are vague.
- missing_structural_reconfiguration: hero grammar, section order, grid behavior, CTA flow, or component layout was not changed from reference/default scaffold.
- weak_pattern_divergence: batch/reference divergence is not concrete enough across hero, section rhythm, visual language, and component cadence.
- generic_section_logic: plan falls back to generic Hero > Features > CTA or filler sections for a full template.
- weak_marketplace_readiness: marketplace value is vague and does not prove depth, editability, source readiness, preview value, commercial usefulness, and non-generic proof.

Use this taxonomy whenever a design, template plan, review, or batch gate fails. The goal is to diagnose the actual failure instead of applying a generic polish pass.

Quality gate output must include:

- `PASS` or `FAIL`
- Failure category
- Evidence
- Root cause
- Required action
- Whether rebuild, recompose, recolor, rewrite, or source-structure repair is needed

## Failure Categories

### A. Routing/Product-Family Failure

- Product type is wrong.
- Website, dashboard, ecommerce, portfolio, deck, UI kit, or preview routes were confused.
- Landing page was used for a full website.

Required action: reroute, reload the correct module, and rebuild the plan.

### B. Section/Page/Screen Depth Failure

- Website has too few meaningful sections.
- Dashboard lacks screens, modules, states, or operational logic.
- Ecommerce lacks product, category, cart, checkout, account, support, or flow logic.

Required action: expand according to product-family standard.

### C. Structure Fingerprint Failure

- Hero grammar repeats.
- Section order repeats.
- Proof, CTA, or footer rhythm repeats.

Required action: rebuild structure, not recolor.

### D. Composition Failure

- Grid, card, media placement, or visual balance is too similar.
- Section names differ but layout behavior is the same.

Required action: recompose affected sections.

### E. Visual-Language Failure

- Design is flat, generic clean, or under-art-directed.
- No clear visual signature, material, effect, or hierarchy system.

Required action: define a semantic visual-language fingerprint.

### F. Color-Role Failure

- Palette is too similar.
- Accent, CTA, highlight, surface, or footer roles repeat the reference or previous batch output.

Required action: recolor the role system only when structure already passes.

### G. Typography/Hierarchy Failure

- Type scale is default.
- Heading, body, label, quote, metric, or CTA hierarchy lacks distinction.

Required action: rebuild type scale and hierarchy rhythm.

### H. Spacing/Rhythm Failure

- All sections use the same cadence.
- Layout is too empty or too dense without product reason.

Required action: set calm, dense, proof, visual-led, and action-led rhythm intentionally.

### I. CTA/Conversion Failure

- CTA is generic.
- Buyer objections are not answered.
- Conversion path does not fit the product family.

Required action: map buyer decision and conversion logic.

### J. Placeholder/Image Direction Failure

- Image placeholder is vague.
- Source template uses final images without explicit request.
- Profile imagery lacks role/context.

Required action: use text clue placeholders by role, such as `image placeholder: [purpose]` and `profile photo placeholder: [role]`.

### K. Figma Source Hygiene Failure

- No auto-layout.
- No component or layer naming logic.
- Important editable content is flattened.

Required action: rebuild source structure with auto-layout, naming, placeholder, responsive/editability, and source hygiene receipts.

### L. Originality/Similarity Failure

- Output is too close to the reference.
- Output is too close to an accepted previous batch output.

Required action: diagnose root cause first, then rebuild, recompose, redesign effects, recolor, or rewrite according to the category.

### M. Visual Evidence Failure

- Review claims visual similarity, spacing, screenshot, or render quality without actual visual evidence.

Required action: mark as not visually inspected or perform screenshot/render review.
