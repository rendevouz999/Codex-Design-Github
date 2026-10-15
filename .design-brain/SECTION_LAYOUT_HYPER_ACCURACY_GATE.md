# Section Layout Hyper-Accuracy Gate

This gate prevents Brain Design from turning weak reference guesses into stable
section layout patterns.

Every stable section pattern must prove that the section was understood from
multiple layers, not merely labeled by a filename or a visible section heading.

## Gate Position

Run this gate after section extraction and the Section Layout Matching Gate, and
before a pattern can enter:

`.design-brain/section-layout-library/<section>/patterns/`

Candidate extraction output belongs in `_incoming` until this gate passes.
Exact duplicates should already have been blocked into `_incoming/_matches/`
before this gate sees them.

## Required Evidence Layers

A pattern may pass only when it has evidence for all layers:

1. Purpose layer: what buyer/user job the section performs.
2. Anatomy layer: the visible elements and their roles.
3. Hierarchy layer: first, second, and third attention route.
4. Grid and rhythm layer: layout type, spacing rhythm, and density behavior.
5. Density limit layer: safe element counts and grouping rules.
6. Originality layer: what may be learned and what must not be copied.
7. Usage rule layer: where this pattern belongs and what it should not follow.

The gate must not pass a pattern that only says "hero with text and image",
"cards grid", "pricing section", or another surface label.

## Quality Status

Valid statuses:

- `PASS`
- `REVIEW_REQUIRED`
- `BLOCKED`

Stable catalog patterns under `patterns/` must be `PASS`.

Incoming patterns may be `REVIEW_REQUIRED` when automated evidence is useful but
not visually verified. They must not be selected for template builds unless the
caller explicitly requests incoming review material.

`BLOCKED` patterns must stay out of the stable catalog. Common reasons:

- copied or copy-risk section composition
- weak evidence
- missing density limit
- no original transformation rule
- no buyer/commercial purpose
- too generic to improve future layout decisions

## Confidence Rules

- `high`: visual or source evidence supports the inference, and all layers are
  specific enough for a future agent to use safely.
- `medium`: evidence is useful but still needs human/Codex visual confirmation.
- `low`: the pattern is only a weak clue and cannot drive a build decision.

Only high-confidence PASS patterns may enter stable section folders.

## Promotion Checklist

Before promoting from `_incoming` into a stable section folder:

- Confirm the section type is correct.
- Confirm the commercial purpose is product-specific.
- Confirm the anatomy is more precise than a generic component name.
- Confirm the hierarchy describes attention movement.
- Confirm the grid/rhythm description names an actual layout behavior.
- Confirm density limits prevent both minimalism and clutter.
- Confirm anti-copy boundary names the risky reference details.
- Confirm usage rules say when not to use the pattern.
- Confirm adjacent-section compatibility is not a page scaffold.
- Confirm `matchStatus` is `NEW_PATTERN` or `VARIANT`, not `DUPLICATE` or
  `NEAR_DUPLICATE`.
- Confirm variants explain why `variantOf` is commercially useful instead of
  repeating an existing section grammar.
- Confirm the pattern can be transformed into a new original execution.

If any answer is vague, keep the pattern in `_incoming`.

## Stable Pattern Receipt

Every stable PASS pattern should include a `hyperAccuracyReceipt` object:

```json
{
  "status": "PASS",
  "reviewedAt": "YYYY-MM-DD",
  "evidenceType": "fig-extract + visual inspection",
  "reviewNotes": "Specific section-level reason this pattern is safe to use.",
  "nonCopyBoundary": "Exact reference details that must not be copied."
}
```

Automated extraction may create the object with `status: REVIEW_REQUIRED`, but it
must not promote that pattern to stable folders.
