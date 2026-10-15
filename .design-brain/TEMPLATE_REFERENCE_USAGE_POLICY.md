# Template Reference Usage Policy

## Purpose

The Brand & Reference Usage Memory Layer prevents Brain Design from repeatedly using the same output brand names, the same reference-template brands, or unsafe manual reference combinations when creating marketplace-ready templates.

This layer is a blocking pre-build gate and a required post-build memory update for reference-led template work, especially Figma website templates.

## Output Brand Memory

Every completed design template must record its new output brand name in `.design-brain/TEMPLATE_REFERENCE_USAGE_REGISTRY.json`.

Future templates must not reuse the same output brand name, and must not use a name that is too close to a previous output brand. The output brand also cannot copy or closely imitate a reference brand.

Use `.design-brain/TEMPLATE_NAMING_LEDGER.md` and `scripts/design_brain_name_check.py` alongside this registry. The naming ledger checks name originality; this layer additionally checks the name against reference brands and used reference groups.

## Reference Brand Memory

Every reference template brand used for Style DNA learning should be registered as a reference record.

Default rule:

`1 reference template brand -> 1 new original design-template brand`

After a reference brand is used as a single reference, it cannot be used as a single reference again.

## Reference Group Memory

Brain Design must record the exact reference set or selector group used for a build.

The group key is normalized by sorting reference IDs and joining them with `+`.

Legacy manual groups are never reused directly:

- `A` cannot be reused as single.
- `A+B` cannot be reused as the same pair.
- `A+B+C` cannot be reused as the same triple.

For website local selector work, product-purpose group rotation is owned by `scripts/design_brain_website_reference_select.py` and `.design-brain/TEMPLATE_REFERENCE_GROUP_ROTATION_REGISTRY.json`. The selector may use up to 10 eligible varied references per active group, move to the next group on the next same-product build, and reset to group 1 only after the final available group has been used.

## Escalation Order

For legacy manual reference usage, single references are preferred before pairs or triples.

1. Use available single references first.
2. If all eligible single references are used, use an unused pair.
3. If all eligible pairs are used, use an unused triple.
4. Use this manual escalation only when not using the website local selector's product-purpose group rotation.

A reference used as a single may later participate in a pair or triple only after all eligible singles are exhausted.

A pair may later participate as part of a triple only after pair options are exhausted.

If singles, pairs, and triples are exhausted, block the build and request new references or explicit user permission to reset the reference stock.

## Style DNA

Style DNA is abstract design logic, not visual copying.

Style DNA may include:

- typography character
- layout rhythm
- color role behavior, not exact hues
- image/media direction and role
- spacing density
- shape language
- effect language
- premium signals
- visual hierarchy
- buyer decision logic
- component behavior
- marketplace positioning
- emotional mood
- section behavior

Style DNA must never mean copying:

- exact layout
- exact composition
- exact section order
- exact hero grammar
- exact grid
- exact color palette
- exact gradient
- exact image placement
- exact component grouping
- exact CTA placement
- exact visual motif
- exact reference brand name

## Blocked Conditions

Block the pre-build gate when any of these are true:

- duplicate output brand name
- output brand too close to an existing output brand
- output brand identical or too close to a reference brand
- selected single reference has already been used
- exact legacy manual reference group has already been used
- pair mode is used before eligible singles are exhausted
- triple mode is used before eligible pairs are exhausted
- registry is missing for reference-led template work
- Style DNA extraction plan is missing
- do-not-copy boundary is missing

## Pass Conditions

The gate may pass when:

- candidate brand is unique
- candidate brand does not copy or closely imitate a reference brand
- selected legacy manual reference group is allowed, or website local selector rotation has produced the active product-purpose group
- reference mode is valid for the chosen path: single, pair, or triple for legacy manual mode; active selector group for website local rotation
- Style DNA extraction plan exists
- do-not-copy boundary exists
- registry update is planned after completion

## CLI Compatibility Examples

Canonical check format:

```bash
python scripts/design_brain_reference_usage_gate.py check --candidate-brand-name "Vistara" --template-id "tpl-001" --template-type "Figma Website Template" --product-family "website" --niche "creative agency" --reference-ids "ref-a" --reference-mode "single" --require-exhaustion-order --json
```

Equivalent alias check format:

```bash
python scripts/design_brain_reference_usage_gate.py check --candidate-name "Vistara" --template-id "tpl-001" --template-type "Figma Website Template" --product-family "website" --niche "creative agency" --references "ref-a" --mode "single" --require-order --json
```

Canonical record format:

```bash
python scripts/design_brain_reference_usage_gate.py record --template-id "tpl-001" --candidate-brand-name "Vistara" --template-type "Figma Website Template" --product-family "website" --niche "creative agency" --reference-ids "ref-a" --reference-mode "single" --completion-receipt-path ".design-brain/receipts/tpl-001-completion.json" --fingerprint-lock-path ".design-brain/fingerprints/tpl-001.json" --do-not-copy-boundary "Do not copy exact layout, palette, motif, or brand name." --json
```

Equivalent alias record format:

```bash
python scripts/design_brain_reference_usage_gate.py record --template-id "tpl-001" --brand-name "Vistara" --template-type "Figma Website Template" --product-family "website" --niche "creative agency" --references "ref-a" --mode "single" --receipt-path ".design-brain/receipts/tpl-001-completion.json" --fingerprint-path ".design-brain/fingerprints/tpl-001.json" --do-not-copy "Do not copy exact layout, palette, motif, or brand name." --json
```

Receipt writing can be added to check, record, suggest-group, or init-reference:

```bash
python scripts/design_brain_reference_usage_gate.py check --candidate-name "Vistara" --references "ref-a" --mode "single" --write-receipt --receipt-output ".design-brain/receipts/reference-usage/tpl-001-check.json" --json
```

## Post-Build Update

After the template build, design system build, post-build audit, fingerprint lock, and completion receipt, run the registry record step.

Final output must not claim `READY` if the brand/reference usage registry was not checked before build and updated after completion.

## Permanent Activation Rule

For reference-led website, Figma, marketplace, source-template, or batch-template work, the Brand & Reference Usage Memory Layer is an active lifecycle gate, not an optional documentation note.

Required evidence:

- pre-build `check` receipt with `status: PASS`
- lifecycle fields for candidate output brand name, reference usage mode, and reference group key
- post-completion `record` receipt with `status: PASS`
- registry entries for the generated output brand, used reference group, and blocked reference brand names

Check-only evidence is incomplete. Once a completion receipt exists, the post-build and lifecycle gates must block final readiness until the registry `record` receipt is registered. A build cannot be described as final, done, ready, shipped, or complete when the registry has not been updated.

The lifecycle registration commands must validate the receipt file before accepting it. Missing files, invalid JSON, wrong command type, or non-PASS receipt status are hard failures.
