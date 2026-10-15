# Design Subagents

This folder defines Brain Design subagents as accountable workflow gates.

- `agents.json` defines the required subagent panel, activation modes, required inputs, required outputs, and blocking authority.
- `subagent-schema.json` validates the agent definition file.
- `orchestration-receipt-schema.json` validates run receipts produced by `scripts/design_brain_subagent_orchestrate.py`.
- `semantic-validation-rules.json` defines what meaningful receipt content must prove.
- `semantic-validation-schema.json` validates semantic validation results from `scripts/design_brain_subagent_receipt_validate.py`.

Subagents are not decorative personas. They are evidence-producing design roles that can require revision or block final delivery.

Final subagent gates must validate receipt contents. A placeholder file, smoke-only text, empty JSON, weak design-system depth check, missing screenshot evidence, unsafe originality score, or marketplace verdict that does not read critical receipts is not acceptable final evidence.
