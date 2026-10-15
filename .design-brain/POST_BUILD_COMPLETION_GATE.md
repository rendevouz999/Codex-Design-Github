# Post-Build Completion Gate

For actual Codex-Design work, load `.design-brain/LOCAL_MEMORY_POLICY.md`. Use the bundled shared memory capability: Supabase first, the local outbox/cache as fallback, and existing plugin-local records alongside both. Include pending/local-only history after recovery. Main and the single Engineer read/search before planning; Main writes and revises with readback. Preserve positive and negative evidence. A service outage does not block local access; conflicts and unknown writes require reconciliation, never blind replay. This owner-approved rule is plugin-scoped.

Applies only to actual custom-plugin design work. Main holds the owner's auto-full trust for internal approval: inspect the single General Design Production Engineer's actual deliverables and evidence, decide PASS or REVISE, and direct repairs without routine user sign-off. Ask when material ambiguity requires the user's intent. Review roles below do not instantiate extra agents. Main may set an appropriate bounded repair budget within authorized scope; SDK-specific hard budgets remain unchanged. Trust never turns missing or failed checks into PASS.

Brain Design output is not complete when the visible template is drawn. It is complete only after the built artifact has a design system, has passed the post-build audits, and has a completion receipt.

For template builds, the completion receipt is required by default. Diagnostic-only audits may omit it only when explicitly marked diagnostic; such runs cannot claim final READY.

## Completion Order

A design output is not complete until:

1. Template build is complete.
2. Design system is built.
3. Triple audit pass 1 is complete.
4. Triple audit pass 2 is complete.
5. Triple audit pass 3 is complete.
6. Critical issues are repaired.
7. Audit is rerun after repair.
8. Completion receipt is generated.

Codex must not say final, done, ready, shipped, or complete before this gate is satisfied.

## Statuses

- READY: design system PASS and all three audit passes PASS with visual render or screenshot verification recorded.
- READY_WITH_LIMITATIONS: source, structure, design system, and audit checks pass, but screenshot/render inspection or design-system artifact evidence was unavailable. The limitation must be stated clearly.
- REVISE_REQUIRED: non-critical issues remain or the artifact needs user-visible refinement before final delivery.
- BLOCKED: critical design system, source, editability, similarity, or layout issues remain.

## Required Repair Loop

Default max repair cycles: 3.

If any audit fails:

1. Classify the issue.
2. Create a repair plan.
3. Repair the artifact/source.
4. Rerun the failed audit pass.
5. If the repair can affect other areas, rerun all three passes.
6. If still failing after max cycles, set final status to REVISE_REQUIRED for non-critical issues or BLOCKED for critical issues.

## Critical Failures

Critical failure examples:

- no design system
- multiple distinct templates share one visible combined design-system board without physically separate per-template design-system frames/pages/sections
- design system is only a receipt, color summary, or sparse style page
- design system lacks artifact evidence but the final response claims fully verified READY
- no auto-layout/source hygiene for Figma template
- flattened important editable text
- obvious overlap or clipped content
- batch templates too similar
- reused scaffold across batch
- no build-session lifecycle ledger for a multi-template website/Figma/source template build
- missing serial provenance proof that each template was completed, locked, and scaffold-disposed before the next template started
- same-shaped batch receipts or fingerprints indicate all-at-once generation from one scaffold
- missing component states
- missing buyer-usable component inventory, product-specific patterns, or editability guidance
- missing product DNA, product-specific modules, reusable section patterns, visual-language rules, placeholder/media guidance, package/source map, or board artifact metrics for marketplace website/Figma/source templates
- compact style-summary board that only shows color, typography, button/card examples, and generic rules
- source not editable
- no final completion receipt
- missing Brand & Reference Usage Memory `check` receipt for reference-led template work
- missing Brand & Reference Usage Memory `record` receipt after completion receipt exists
- candidate output brand, reference usage mode, or reference group key missing from the lifecycle ledger
- source not usable by the template buyer
- visual QA impossible when the user explicitly requested visual/render verification

## Per-Template Design System Verification

For multi-template Figma/source packs, post-build audit must verify every template's design system separately. The audit must record:

- template name
- design-system frame/page/section name and node ID when available
- ownership marker or visible owner label
- component/pattern coverage for that template
- screenshot or visual-inspection evidence for that design-system artifact
- whether any pack-level source board is labeled as audit summary only

The final status cannot be READY if a combined governance/source board is used as the design system for all templates, if a per-template design-system artifact is visually rough or clipped, or if a pack-level board makes the templates look like one shared builder.

For marketplace website/Figma/source templates, final READY is also blocked when a design-system board is below product-grade depth. The board must include product DNA, foundations, component inventory, states/variants, product-specific modules, reusable section patterns, placeholder/media rules, responsive/editability rules, visual-language rules, usage examples, package/source map, and source hygiene receipt. The design-system receipt must include board metrics: panel count, component specimen count, product-specific module count, state example count, screenshot/render path, and frame/page ID.

## Batch Flow

For batch outputs, every template must pass this gate before the next template is considered complete.

For Figma/source-template batches, each item is an atomic pair: template plus that template's own design-system board. The next template cannot start while the current pair has a missing, invalid, receipt-only, visually rough, or uninspected design-system board.

Template 1:

- build template
- build design-system board 1
- run post-build triple audit
- repair if needed
- lock fingerprint

Template 2:

- build template
- build design-system board 2
- run post-build triple audit
- pairwise audit vs Template 1
- repair if needed
- lock fingerprint

Template N:

- build template
- build design-system board N
- run post-build triple audit
- pairwise audit vs all previous templates
- repair if needed
- lock fingerprint

Final batch:

- global pairwise similarity audit
- serial provenance audit
- global source hygiene audit
- per-template design-system separation audit
- global visual/layout QA
- final completion receipt

## Serial Provenance Audit

For any multi-template website/Figma/source build, post-build audit must run a serial provenance check before it can return READY.

The check must verify:

- a build-session lifecycle ledger exists
- each template has a single-template cycle record
- Template N+1 starts only after Template N is fingerprint locked
- Template N+1 starts only after Template N has a scaffold disposal receipt
- each build artifact is scoped to one final template
- receipt morphology does not suggest all-at-once generation from one shared builder

If this audit is missing, limited, or failed, final status is BLOCKED. Screenshots, design-system receipts, and pairwise similarity scores cannot override a failed provenance audit.

## Completion Receipt Requirement

For any design template build, final response must include:

- Templates built
- Design systems built
- Per-template design-system separation result for multi-template outputs
- Audit Pass 1 result
- Audit Pass 2 result
- Audit Pass 3 result
- Batch similarity audit result
- Repair cycles
- Remaining issues
- Visual verification status
- Final status

## Cognition Receipt Comparison

Post-build audit must compare final output against the Design Cognition Receipt:

- Did build follow Color Role Re-Mapping?
- Did build preserve Reference Boundary?
- Did build implement Structural Reconfiguration?
- Did build follow Section Logic?
- Did build satisfy Marketplace Readiness?

If final build violates cognition receipt, audit fails and repair is required.

Post-build audit may require a valid JSON Design Cognition Receipt with `--require-cognition`. For reference-led/template builds, missing or invalid cognition means final status cannot be READY. A fake status-only receipt is invalid because the audit uses the Design Cognition checker rather than trusting the raw status field.

## Build Session and Layout Originality Inputs

When a build-session ledger exists, Post-Build Completion Gate must verify:

- Build session ID
- route resolved
- candidate output brand name, reference usage mode, reference group key, and PASS brand/reference usage `check` receipt for reference-led work
- PASS brand/reference usage `record` receipt when the lifecycle has a completion receipt
- cognition receipt registered
- simulation verdict registered
- reference layout audit result
- AI pairwise layout audit result
- build artifact registered
- fingerprint lock status
- idea recovery corpus used: yes/no
- corpus inspiration IDs when used
- layout repair cycles
- axis failures repaired
- safe to proceed to next template

Final status cannot be READY if reference layout audit failed, AI pairwise layout audit failed, fingerprint lock is missing, design system is missing, or post-build audit failed.

Final delivery must also pass the Build Session Lifecycle `verify-final` check when the build used a lifecycle session.

For reference-led work, direct post-build readiness is not enough unless the Brand & Reference Usage Memory Layer has both phases recorded. The `check` phase protects the next build from starting with a reused name/reference; the `record` phase protects all future builds from reusing the completed output's brand or reference group.
