# Subagent Receipt Semantic Validator

This layer closes the gap between "evidence file exists" and "evidence is strong enough to trust."

The validator is mandatory for final subagent gates when evidence exists. It reads subagent receipt files and checks their semantic quality, not only their presence.

## Core Rule

Final PASS requires meaningful evidence.

An output cannot pass final review only because files such as `visual-qa-report.json`, `design-system-depth-check.json`, or `marketplace-readiness-verdict.json` exist. The evidence must contain structured proof that the subagent actually inspected the relevant design quality axis.

## Source Files

- `.design-brain/design-subagents/semantic-validation-rules.json`
- `.design-brain/design-subagents/semantic-validation-schema.json`
- `scripts/design_brain_subagent_receipt_validate.py`
- `scripts/design_brain_subagent_semantic_smoke_test.py`

## Mandatory Semantic Checks

The validator checks:

- JSON receipt files are valid JSON and not empty placeholders.
- Critical final receipts explicitly PASS or provide enough evidence to support PASS.
- Reference analysis covers typography, layout, hierarchy, color, spacing, media/effects, and copying risk.
- Style DNA includes transferable logic, reinterpretation, and do-not-copy boundaries.
- Product architecture proves buyer logic, product promise, page or section scope, marketplace value, and conversion logic.
- Design-system depth includes color roles, typography styles, spacing rhythm, components, states or variants, section modules, usage examples, and effect or surface-depth language.
- Figma source QA proves auto-layout, components, variants, layer naming, tokens/styles, and editability.
- Originality audit includes similarity evidence and blocks results above 10 percent on structure-defining axes.
- Visual QA proves screenshot or rendered visual inspection and blocks weak, clipped, overlapped, generic, flat, or cramped output.
- Marketplace verdict reads the critical receipts and blocks final delivery if critical proof is missing.

## Blocking Behavior

The validator returns:

- `PASS` when all active subagent evidence is meaningful.
- `REVISE_REQUIRED` when evidence exists but is incomplete or weak.
- `BLOCK` when critical evidence is missing, fake, invalid, contradictory, or unsafe for final delivery.

For final gates, a critical subagent with semantic status other than `PASS` blocks final delivery.

## Runtime Behavior

`scripts/design_brain_subagent_orchestrate.py` calls the semantic validator automatically when `--final` and `--evidence-dir` are supplied, unless `--skip-semantic-validation` is explicitly used for debugging.

Use the validator directly when auditing an evidence directory:

```bash
python scripts/design_brain_subagent_receipt_validate.py --evidence-dir ".design-brain/evidence/subagents/template-1" --mode full --final --marketplace --has-reference --figma-source --json
```

