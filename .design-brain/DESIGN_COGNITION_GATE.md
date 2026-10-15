# Design Cognition Gate

The Design Cognition Gate validates the Design Cognition Receipt before template orchestration/build.

Machine-readable receipts must be JSON and should follow `.design-brain/templates/DESIGN_COGNITION_RECEIPT.json`. The Markdown receipt template is for human authoring only unless a Markdown parser is implemented.

## Failure Rules

FAIL if:

- any of the 11 cognition steps are missing
- Reference Standard is missing
- reference standard does not extract section count/range, section roles, layout-shape inventory, color-role inventory, effect/gradient inventory, marketplace completeness clues, and remix plan
- Color Role Re-Mapping is missing
- output keeps reference dominant color identity without explicit user request
- Reference Boundary does not define forbidden copy items
- Structural Reconfiguration does not change hero grammar, section order, or grid behavior
- Pattern Divergence is missing for batch
- Section Logic uses generic Hero > Features > CTA for a full template
- Marketplace Readiness is vague or generic
- cognition receipt is not generated for a reference-led template build
- JSON cognition receipt is missing or invalid for an automated gate
- fake status-only receipt such as `{"status":"PASS"}` is provided

## Repair Rule

If FAIL:

1. Revise cognition receipt.
2. Do not build.
3. Rerun cognition gate.
4. Continue to orchestration only after PASS.

## Risk Categories

- missing_style_dna
- missing_reference_standard
- missing_design_intent
- missing_visual_grammar
- missing_reference_boundary
- missing_color_role_remapping
- copied_color_identity
- missing_visual_mood_reinterpretation
- missing_structural_reconfiguration
- missing_pattern_divergence
- generic_section_logic
- weak_marketplace_readiness
