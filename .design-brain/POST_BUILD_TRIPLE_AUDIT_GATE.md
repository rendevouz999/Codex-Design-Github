# Post-Build Triple Audit Gate

After every build, Brain Design must run three audit passes. If any pass fails, Codex must repair and rerun the failed audit before final delivery.

For multi-template website/Figma/source builds, Brain Design must run Audit Pass 0 before these three passes. Pass 0 is the Serial Provenance Gate. If it fails, final delivery is blocked even when design-system, screenshot, visual QA, or pairwise similarity checks appear to pass.

## Audit Pass 0: Serial Provenance / Anti-Scaffold

Check:

- build-session ledger exists
- each template has a separate cycle number
- each template has its own reference study, cognition, plan, build artifact, design-system board, audit, and fingerprint lock
- Template N+1 starts only after Template N is complete, repaired, audited, fingerprint locked, and scaffold-disposed
- build artifacts have single-template scope
- final Figma writes do not create multiple final templates from one app builder/script/schema
- cognition receipts, fingerprints, and design-system receipts are not same-shaped batch outputs

Fail if:

- the batch has no build-session ledger
- multiple final templates or design-system boards are produced by one page-level builder
- receipt/fingerprint files share identical morphology that suggests same scaffold generation
- Template 2 or later starts before the prior template has a scaffold disposal receipt
- fingerprints exist but were generated together from one shared batch object

## Audit Pass 1: Originality / Reference / Batch Similarity

Check:

- reference similarity risk
- copy/scaffold risk
- hero grammar
- section order
- grid rhythm
- card cadence
- CTA placement
- image treatment
- typography behavior
- color role behavior
- effect language
- premium signal
- batch pairwise similarity

Also compare the build against the Design Cognition Receipt: Reference Boundary, Color Role Re-Mapping, Structural Reconfiguration, Pattern Divergence, Section Logic, and Marketplace Readiness must be honored.

For batch, compare every pair:

- Template 1 vs Template 2
- Template 1 vs Template 3
- Template 2 vs Template 3
- all pairwise combinations for N templates

Fail if:

- templates are only recolors
- templates reuse the same hero grammar
- templates reuse the same section order
- templates reuse the same card rhythm
- templates use the same CTA closure
- templates use the same image treatment
- templates feel like the same scaffold

## Audit Pass 2: Design System / Figma / Source Hygiene

Check:

- design system exists
- tokens exist
- typography system exists
- spacing system exists
- components exist
- component states exist
- auto-layout applied
- constraints/responsive notes
- layer naming
- frame nesting
- text editable
- placeholder editable
- important content not flattened
- variants/components reusable
- source ready for marketplace buyer

Fail if:

- missing design system
- auto-layout absent in core frames/components
- layers unnamed/generic
- text flattened
- images not replaceable
- components not reusable
- design system not tied to template

## Audit Pass 3: Visual QA / Layout Defect / Content QA

Check:

- text overlap
- content overflow
- clipping
- objects outside frame
- broken alignment
- uneven spacing
- poor contrast
- inconsistent hierarchy
- image crop issue
- CTA unclear
- section too empty
- section too dense
- z-index/stacking issue
- inconsistent style usage
- broken responsive behavior
- accidental duplicates
- missing footer/header consistency

Fail if:

- visible overlap
- clipped content
- severe contrast failure
- alignment break
- broken source frame
- unreadable text
- content exceeds frame
- critical responsive issue

## Repair Rule

If any pass fails:

1. Create repair plan.
2. Apply repair.
3. Rerun failed audit pass.
4. If repair affects other areas, rerun all three passes.
5. Max repair cycles default 3.
6. If still failing, final status = REVISE_REQUIRED or BLOCKED.

## Layout Originality Cross-Check

Post-build audit must compare final output against the build-session lifecycle when present. If the built template violates the passed layout originality receipt, copied its reference scaffold, or became too similar to a previous AI output, Audit Pass 1 fails and repair is required.

Layout similarity failure is repaired through structural reconfiguration, not recolor or image replacement.
