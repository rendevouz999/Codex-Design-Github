# Section Layout Matching Gate

This gate prevents the section layout library from growing by duplicate grammar.
It runs after automated extraction creates a candidate and before that candidate
is written into `_incoming` or promoted into a stable section catalog.

## Default Mode

Mode is exploratory.

Exploratory means the catalog stays open to useful variation, but duplicate
section structures are blocked before they become false vocabulary.

## Matching Order

1. Build `structuralSignature` from the candidate's section-level layout axes.
2. Compare the candidate against stable patterns and `_incoming` candidates.
3. Match primarily inside the same `sectionType`.
4. Warn on related section families only; do not auto-block across section
   types unless the section type is the same.
5. Write match receipts before candidate files when a match risk is found.
6. Keep Hyper-Accuracy Gate authority for any candidate that might become
   stable.

Related section families:

- `features` and `services`
- `cta`, `contact-booking`, and `footer`
- `portfolio-gallery` and `case-study`

## Matching Axes

- `layoutGesture`
- `sectionSilhouette`
- `anatomyLayer`
- `hierarchyLayer`
- `gridRhythmLayer`
- `focalPath`
- `compositionTension`
- `negativeSpaceShape`
- `moduleScaleVariation`
- `breakoutBehavior`
- `contentLimits`

## Thresholds

- `>= 0.90`: `DUPLICATE`
- `0.78 - 0.89`: `NEAR_DUPLICATE`
- `0.55 - 0.77`: `VARIANT`
- `< 0.55`: `NEW_PATTERN`

## Status Behavior

`DUPLICATE`

- Do not create a new pattern file.
- Write a receipt to `_incoming/_matches/`.
- Set `duplicateOf` to the matched pattern.

`NEAR_DUPLICATE`

- Write a receipt to `_incoming/_matches/`.
- Candidate may stay in `_incoming/<section>/` only as review material.
- Stable promotion requires Hyper-Accuracy PASS and an explicit difference
  rationale.

`VARIANT`

- Write candidate to `_incoming/<section>/`.
- Set `variantOf` to the closest matched pattern.
- Stable promotion requires proof that the variant changes buyer comprehension,
  density, focal path, or section rhythm in a useful way.

`NEW_PATTERN`

- Write candidate to `_incoming/<section>/`.
- Treat it as new vocabulary only after Hyper-Accuracy PASS.

## Stable Catalog Rule

Stable catalog validation must fail if two stable patterns in the same section
match at `DUPLICATE` threshold.

Stable patterns may have `matchStatus` of `NEW_PATTERN` or `VARIANT`. Stable
patterns may not have `DUPLICATE` or `NEAR_DUPLICATE` status.

## Required Pattern Fields

Every pattern must include:

- `structuralSignature`
- `matchStatus`
- `matchScore`
- `matchGroupId`
- `duplicateOf`
- `variantOf`
- `matchingEvidence`
- `dedupeDecision`

These fields protect the library. They do not replace Designer Cognition,
Reference Insight, Hyper-Accuracy Gate, Layout Fingerprint, or visual review.
