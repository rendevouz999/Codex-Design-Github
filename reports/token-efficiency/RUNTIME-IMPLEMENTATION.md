> **HISTORICAL DONOR BASELINE 2.8.0 (2026-10-17).** Not proof that current Codex-Design 2.9.0 reconciliation passed. See the 2026-10-21 reconciliation report for current source/test evidence.

# Runtime continuity and repair implementation

Date: 17 October 2026. Source baseline: a7c3cb6594ce7ecbd71ca9ebf5ceb4852c5aef36, version 2.8.0. Branch: improvement/token-efficiency-20261017. No claim that missing 2.9.0 navigation files were restored or that Windows is running this tree.

## Implemented scope

- T03: the existing session state now owns a bounded project/session checkpoint with per-slide authoring status, source/evidence hashes, shared dependencies, style/layout decisions, asset slots, constraints, owner and next action. Explicit resume returns current/stale/unknown currency, preserves valid units and never selects another project through a global pointer. Checkpoint labels are not quality PASS. Compaction refreshes state before publishing, binds the packet to persisted state bytes, and removes duplicate full-ticket fields.
- T08: actual native module selection owns the route. Other bare run/run-next calls record requested work instead of fabricated execution PASS. Explicit external execution receipts require current revision-bound input/evidence and retain external_receipt provenance plus schema/currency-only verification scope. This imports accountable external execution claims, not independent semantic proof. Current visual and production validators remain required.
- T04/T10: stable issue identity deduplicates reports; explicit changed-input checked attempts persist in existing tickets and count once. Re-auditing does not count. Post-build receipts report persistent counts and exhausted per-issue budgets without converting failure to PASS. Corrupt ticket data fails closed and remains untouched. Administrative closure leaves unverified quality and source-gate rerun debt; stale execution timestamps cannot clear it.
- T09: the existing audit script supports --completion-phase prepare/audit/finalize. Preparation is PENDING_AUDIT. Audit emits evidence readiness with finalAllowed=false and pending_final phase. Final completion binds the exact artifact and audit, requires all four named audit passes and current specialized visual evidence. Runtime finalize runs this binding only after prior gates, ticket integrity, checkpoint currency, permission and production prerequisites pass.

## Compatibility

Existing sessions without checkpoints return UNKNOWN for resume; recover their actual files rather than rebuilding by default. Legacy completion statuses remain recognized as preparation-presence only; they do not satisfy final binding. Existing completedStages metadata no longer proves a gate ran. External imports preserve the previously manual/native workflow without adding automatic execution of every tool or a second validation engine. The runtime smoke now asserts truthful REQUESTED behavior rather than fake PASS progression. Global legacy summary files are not read or overwritten by compaction.

## Verification observed

Tests were written and observed failing before the corresponding fixes, including later dependency, stale-closure, path-scope and partial-audit regressions.

- New offline unittest suite: 25 tests PASS (test_runtime_continuity_repair.py).
- Existing visual-route regressions: 8 tests PASS, unchanged assertions, including the legacy visual-receipt diagnostic.
- Existing runtime smoke: 22 checks PASS in a temporary tracked-file snapshot with current working-tree contents.
- Existing post-build smoke: 35 checks PASS in that isolated snapshot.
- git diff --check PASS.

Synthetic visual/external-attestation fixtures establish integrity behavior only; no native product rendering, actual design quality or production token savings were measured. No live memory/provider calls, build, installation, deployment, push or guard change occurred. The broader repository test suite and live installed-plugin behavior were not run; the authorization was targeted isolated tests only.

## Remaining limits

Hash currency proves byte identity, not that an agent truly inspected pixels or that every required dependency was recorded. Main remains responsible for the complete dependency list, actual source-gate work, semantic/visual review and final approval. Repair attempt revisions/outcomes are accountable caller-supplied records, not inferred patch detection. Ticket writes are atomic for interruption resistance; this does not introduce multi-writer locking. No automatic whole-project rebuild, retry loop or cross-project selection was added.
