# Build Session Lifecycle

Brain Design tracks every template build as a lifecycle transaction. The Lifecycle ledger is the source of truth for whether a build session is allowed to continue or finish.

## Required Stages

1. `session_started`
2. `route_resolved`
3. `brand_reference_usage_checked`
4. `reference_registered`
5. `design_cognition_passed`
6. `design_simulation_passed`
7. `template_plan_created`
8. `reference_layout_audit_passed`
9. `template_built`
10. `design_system_built`
11. `post_build_audit_passed`
12. `previous_template_similarity_audit_passed`
13. `fingerprint_locked`
14. `scaffold_disposed`
15. `completion_receipt_created`
16. `brand_reference_usage_recorded`
17. `session_ready`

## Rules

- Final delivery is blocked if any required lifecycle stage is missing.
- For a single template, `previous_template_similarity_audit_passed` is `N/A`.
- For batch builds, `previous_template_similarity_audit_passed` is mandatory for Template 2 and beyond.
- Template N+1 cannot start until Template N is `fingerprint_locked`, and that lock is only valid after Template N's design-system board/receipt and post-build audit are complete.
- For batch builds, Template N+1 also cannot start until Template N has a scaffold disposal receipt registered. Locking a fingerprint proves the template was accepted; scaffold disposal proves the next template will not reuse that accepted page builder.
- Only one template may be active in a build session. Starting or registering any stage for a new template while a previous template is not locked and disposed is a lifecycle violation.
- Manual, Figma, generated-source, and code-based template builds must write or import the same receipts.
- Reference registration cannot happen before `brand_reference_usage_checked`.
- Build cannot be registered before the pre-build layout originality audit passes.
- Fingerprint lock cannot happen before design system and post-build audit pass.
- Scaffold disposal cannot happen before fingerprint lock. Disposal records the spent hero grammar, section sequence, module/card/grid cadence, CTA/proof/footer closure, design-system panel order, and temporary builder artifacts that must not be reused.
- `brand_reference_usage_recorded` happens after `completion_receipt_created` and before final delivery.
- `brand_reference_usage_checked` and `brand_reference_usage_recorded` may only be registered from receipt files whose command type and status match the lifecycle step.
- The lifecycle ledger is the source of truth for build completion.
- Final readiness must run `scripts/design_brain_build_session.py verify-final --session <session> --json` after `finalize`.
- `verify-final` blocks delivery when route, brand/reference usage check, reference registration, cognition, simulation, layout audit, build artifact, design system, post-build audit, fingerprint lock, pairwise audit for batch, completion receipt, or brand/reference usage registry record is missing.

## Transaction Order

Route -> brand/reference usage check -> reference registration -> cognition -> simulation -> plan -> layout audit -> build template -> build design-system board -> validate design-system receipt -> post-build audit -> fingerprint lock -> scaffold disposal -> completion receipt -> brand/reference usage record -> verify-final -> next template.

If a stage fails, repair the artifact or receipt, rerun the failed gate, and update the ledger before continuing.

## Serial Provenance Lock

For any request with more than one website/Figma/source template, final readiness is blocked unless the lifecycle proves true serial work:

- Template 1 has its own reference study, cognition, plan, build artifact, design-system board, visual audit, post-build audit, fingerprint lock, and scaffold disposal before Template 2 starts.
- Template 2 repeats the full cycle from its own reference insight and may start only after Template 1 is locked and disposed.
- Template 3 repeats the full cycle from its own reference insight and may start only after Template 2 is locked and disposed, while also comparing against Template 1 and Template 2.
- The same rule continues for any number of requested templates.

All-at-once batch evidence is a hard failure. Examples:

- one Figma script or builder creates multiple final templates in a single page-level data loop
- multiple cognition receipts, fingerprints, or design-system receipts are generated in one operation with identical morphology
- a single page schema, section array, design-system panel order, or component cadence can produce every template by swapping data, colors, copy, or image labels
- post-build audit is run without a build-session ledger for a multi-template template build

The provenance check must fail these cases even when screenshots, fingerprints, or design-system receipts exist.

## Final Verification

`finalize` creates the build-session completion receipt. `verify-final` proves that the receipt and lifecycle ledger are complete. A template build is not final until both commands can pass:

```bash
python scripts/design_brain_build_session.py finalize --session <session> --json
python scripts/design_brain_reference_usage_gate.py record --candidate-brand-name "..." --reference-ids "..." --reference-mode "single|pair|triple" --template-id "..." --require-exhaustion-order --json
python scripts/design_brain_build_session.py register-reference-usage-record --session <session> --template-id "..." --receipt "<record-json>" --json
python scripts/design_brain_build_session.py verify-final --session <session> --json
```

For website local selector work, use the active product-purpose group from `scripts/design_brain_website_reference_select.py`; do not collapse the selector group to the legacy single/pair/triple path just to satisfy older wording.

For real template builds, `verify-final` is the mandatory wrapper check before the final user response.
