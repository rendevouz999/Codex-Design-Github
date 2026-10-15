# Design Cognition Contract

Every reference-led template build must pass these 11 cognition steps before orchestration/build:

1. Style DNA
2. Reference Standard
3. Design Intent Lock
4. Visual Grammar
5. Reference Boundary
6. Color Role Re-Mapping
7. Visual Mood Reinterpretation
8. Structural Reconfiguration
9. Pattern Divergence
10. Section Logic
11. Marketplace Readiness

Layout fluidity is part of Structural Reconfiguration and Pattern Divergence. A plan can fail cognition even when section count is sufficient if the layout gesture, section silhouettes, focal path, and composition tension repeat prior outputs.

Rule: a template plan is not ready for orchestration/build until all 11 points are defined.

Automated enforcement requires a JSON cognition receipt. Use `.design-brain/templates/DESIGN_COGNITION_RECEIPT.json` as the machine-readable template/example and validate it with `scripts/design_brain_design_cognition_check.py`.

`.design-brain/templates/DESIGN_COGNITION_RECEIPT.md` is only the human-readable authoring template unless a Markdown parser is explicitly implemented. Do not treat the Markdown file alone as a valid machine-check receipt.

## 1. Style DNA

Extract typography behavior, layout rhythm, spacing density, color behavior, image direction, shape language, effect language, and premium signal.

Also record the selected reference group key, reference usage mode, candidate output brand, and why the Brand & Reference Usage Memory gate allowed this group. Style DNA is abstract logic only; it cannot justify reusing a spent reference group or blocked brand/name pattern.

## 2. Reference Standard

Extract the reference's standard before planning: section count/range, section roles, layout-shape inventory, color-role inventory, effect/gradient inventory, marketplace completeness clues, and a remix plan. Minimalist fallback must be explicitly rejected unless the product/reference evidence proves a small scope.

## 3. Design Intent Lock

Lock product type, output medium, niche, target buyer, use case, marketplace value, and primary goal.

## 4. Visual Grammar

Define grid behavior, spacing cadence, typography hierarchy, color roles, surface depth, image treatment, effect logic, and component rhythm.

## 5. Reference Boundary

Define what may be learned and what must not be copied. Do not copy exact layout, color palette, section order, composition, hero grammar, component scaffold, image placement, or signature color identity.

Include forbidden execution patterns from the selected reference group: exact hero grammar, section sequence, CTA placement, media sequence, color-role mapping, effect signature, component grouping, and any prior output fingerprint that must not repeat.

## 6. Color Role Re-Mapping

Do not copy exact hue, palette, or dominant color identity from reference. Extract color roles and remap them to a new palette direction that preserves emotional energy, contrast behavior, hierarchy, and market positioning.

## 7. Visual Mood Reinterpretation

Preserve emotional direction and market positioning, but create a new visual expression through changed composition, palette behavior, hierarchy, asset treatment, and depth.

## 8. Structural Reconfiguration

Rebuild section order, hero grammar, grid system, content rhythm, CTA placement, and component layout. Do not repaint the reference scaffold.

Also define a new layout gesture, section silhouette sequence, composition tension, focal path, negative-space shape, depth layering, module scale variation, and breakout behavior. These must be product-fit, editable, and distinct from prior accepted templates.

## 9. Pattern Divergence

Ensure output diverges from reference and previous templates. For batch, each template must differ in hero grammar, section rhythm, grid behavior, image treatment, CTA pattern, and visual language.

For batch and repeated template work, each template must also differ in layout gesture and zoomed-out section silhouette. If two templates can be recognized as siblings after blurring color and text, Pattern Divergence is weak.

## 10. Section Logic

Every section must have a clear buyer journey role. No filler sections. No generic Hero > Features > CTA scaffold for full templates.

## 11. Marketplace Readiness

Template must feel complete, premium, editable, source-clean, commercially useful, sufficiently deep, and not like a basic generic layout.

## Build Rule

If any cognition step is missing or weak, stop before orchestration/build, revise the cognition receipt, and rerun the cognition gate. Design Simulation Layer and Post-Build Completion Gate both consume the cognition receipt.

## Sequential Layout Originality Link

The Design Cognition Contract must feed the Sequential Layout Originality Gate. Reference Boundary, Color Role Re-Mapping, Structural Reconfiguration, Pattern Divergence, Section Logic, and Marketplace Readiness become evidence for the layout fingerprint and the reference-vs-AI audit.

If the layout audit contradicts the cognition receipt, revise cognition, reconfigure the layout plan, and rerun the gate before build.
