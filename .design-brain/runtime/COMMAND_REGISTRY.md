# Runtime Command Registry

Production extension: `/design-produce` maps to `design_production_tool` and requires `full_build`. The same hook is automatic during `start --production-request`. Controller-only CLI commands are `review-production`, `cancel-production`, `recover-production`, and read-only `production-capabilities`. Refer to `DESIGN_PRODUCTION_SPECIALIST.md` for typed inputs and review/recovery behavior.

Commands are slash-like runtime actions routed by `scripts/design_brain_command_router.py`.

| Command | Purpose | Permission |
|---|---|---|
| `/design-start` | Create a runtime session | diagnostic_only |
| `/design-route` | Resolve route/product family | diagnostic_only |
| `/design-reference-usage` | Check output brand and reference group memory | plan_only |
| `/design-cognition` | Validate Design Cognition Receipt | plan_only |
| `/design-section-layout` | Extract, match, validate, or select section layout catalog patterns | plan_only |
| `/design-subagents` | Plan/verify subagent evidence and blocking status | plan_only |
| `/design-subagent-validate` | Validate subagent receipt content quality | plan_only |
| `/design-simulate` | Run Design Simulation Layer | plan_only |
| `/design-layout-audit` | Run layout originality audit | plan_only |
| `/design-build-session` | Register/verify build-session evidence | full_build |
| `/design-craft` | Run Design Craft support adapter | plan_only |
| `/design-design-system` | Validate design system receipt/evidence | full_build |
| `/design-web-deck` | Plan, audit, or render-review web deck stage and runtime fidelity | plan_only |
| `/design-post-build` | Run post-build audit | full_build |
| `/design-repair` | Create or process repair tickets | safe_patch |
| `/design-completion-receipt` | Record completion receipt evidence | full_build |
| `/design-finalize` | Finalize and verify readiness | full_build |
| `/design-status` | Show session status | diagnostic_only |
| `/design-doctor` | Run runtime doctor | diagnostic_only |
| `/design-resume` | Resume an existing session | diagnostic_only |
| `/design-rewind` | Mark session stage for revision | safe_patch |
| `/design-compact` | Write compact context packet | diagnostic_only |
| `/design-export` | Export package after integrity checks | export_allowed |

Commands return machine-readable runtime results with `status`, `command`, `tool`, `blocking`, `requiredRepairs`, `nextAction`, and `finalAllowed`.

`/design-craft` uses the bundled Design Craft v0.3.0 adapter in `.design-brain/adapters/design-craft` when available. The command is support-only: it may add craft tokens, typography, spacing, component-state, accessibility, and handoff guidance, but cannot approve final delivery or override Brain Design route, structure, simulation, layout, post-build, or completion gates.

`/design-subagents` routes to `scripts/design_brain_subagent_orchestrate.py`. Use it after reference usage/cognition and before simulation/build planning to decide which subagents are active, which receipts are missing, and whether final delivery is blocked by missing critical evidence.

`/design-subagent-validate` routes to `scripts/design_brain_subagent_receipt_validate.py`. Use it when an evidence directory already exists and Brain Design must judge whether the receipt contents are meaningful enough for final PASS, not only present on disk.

`/design-section-layout` routes to `scripts/design_brain_section_layout_extract.py`. Use it after Reference Insight / Designer Cognition and before Template Orchestration to extract incoming section patterns, match/dedupe candidates, validate the catalog, or select stable PASS patterns for `sectionPatternMix` fingerprint evidence.

## /design-reference-usage

`/design-reference-usage` routes to `scripts/design_brain_reference_usage_gate.py` and guards output brand names, reference brand names, and exact reference groups before reference-led template planning.

Canonical check flow:

```bash
python scripts/design_brain_reference_usage_gate.py check --candidate-brand-name "Vistara" --template-id "tpl-001" --template-type "Figma Website Template" --product-family "website" --niche "creative agency" --reference-ids "ref-a" --reference-mode "single" --require-exhaustion-order --json
```

Alias check flow:

```bash
python scripts/design_brain_reference_usage_gate.py check --candidate-name "Vistara" --template-id "tpl-001" --template-type "Figma Website Template" --product-family "website" --niche "creative agency" --references "ref-a" --mode "single" --require-order --json
```

Canonical record flow:

```bash
python scripts/design_brain_reference_usage_gate.py record --template-id "tpl-001" --candidate-brand-name "Vistara" --reference-ids "ref-a" --reference-mode "single" --completion-receipt-path ".design-brain/receipts/tpl-001-completion.json" --fingerprint-lock-path ".design-brain/fingerprints/tpl-001.json" --do-not-copy-boundary "Do not copy exact layout, palette, motif, or brand name." --json
```

Alias record flow:

```bash
python scripts/design_brain_reference_usage_gate.py record --template-id "tpl-001" --brand-name "Vistara" --references "ref-a" --mode "single" --receipt-path ".design-brain/receipts/tpl-001-completion.json" --fingerprint-path ".design-brain/fingerprints/tpl-001.json" --do-not-copy "Do not copy exact layout, palette, motif, or brand name." --json
```

Add `--write-receipt` to check, record, suggest-group, or init-reference to create a JSON receipt. Use `--receipt-output` for an explicit path; otherwise the tool writes to `.design-brain/receipts/reference-usage/{templateId}-{command}-{timestamp}.json`.

`--json` must return JSON only. `BLOCKED` stops the build until the candidate brand, reference mode, or reference group is revised. `REVISE_REQUIRED` means weak name similarity needs a safer output brand before marketplace work continues.

## /design-web-deck

`/design-web-deck` routes to the Web Deck tool chain (`web_deck_tool`, `web_deck_audit_tool`, `web_deck_render_review_tool`) and enforces `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md` for `web-deck` output. It adds no required stage: it records the non-required `web_deck` stage in the session ledger, so running it never marks a required stage complete. The plan-time check runs inside build planning, and the static audit plus render review run inside the post-build stage before Audit Pass 1.

Build and audit are two steps, and the second one reads the deck plan the first one leaves behind.

Plan and build flow:

```bash
node skills/presentation-deck/runtime/web/design_brain_web_deck_plan.mjs --plan <deck-plan.json> --out <deck.html> --json
```

`--plan` builds from a deck plan validated against `skills/presentation-deck/resources/web-deck/deck-plan-schema.json`, which is what real work does. `--demo` replaces `--plan` and synthesizes a valid plan instead, to show the expected plan and output shape; a `--demo` build also writes a sidecar deck plan beside the deck at `<out-path-without-.html>.deck-plan.json` and reports that path as `planOut`. `--dry-run` validates and reports without writing the deck or the sidecar. The complete flag set is `--plan`, `--demo`, `--out`, `--json`, `--dry-run`, `--help`.

Static audit flow, plan-relative:

```bash
node skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs <deck.html> --plan <deck.deck-plan.json> --json
```

The deck path is positional and the complete flag set is `--plan`, `--json`, `--help`. Always pass the plan. Without it the audit still checks the stage, switching, navigation, deep-link, lifecycle, reduced-motion, print, and dependency rules, but the plan-relative checks do not run (`slide-count-budget`, `slide-density-budget`, `reveal-order-agreement`) and the report states `Plan: not supplied, plan-relative checks skipped`. After a `--demo` build the plan to pass is the sidecar; after a `--plan` build it is the same plan file the deck was built from.

Render review flow:

```bash
node skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs <deck.html> --json
```

The render review resolves the plan itself: it looks for `<stem>.deck-plan.json` beside the deck first, so the sidecar is picked up with no flag, and `--plan FILE` is only needed for a plan kept elsewhere. Remaining flags are `--out DIR`, which takes every output including the Markdown report, `--phone-width PX` for the narrow-viewport pass, `--keep-shots`, `--json`, and `--help`.

When an existing deck is the input, extract it first through `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md` and `skills/presentation-deck/runtime/web/design_brain_deck_source_extract.mjs`, whose `--out` takes a folder, not a file.

`--json` must return JSON only. The command is medium-scoped: a P0 stage or runtime defect blocks `web-deck` final delivery, but a PASS here cannot grant final readiness, which stays with the post-build and completion gates.
