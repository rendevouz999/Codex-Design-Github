# Runtime Tool Registry

`design_production_tool` is registered in the existing Python registry and uses `scripts/design_brain_runtime.py` as its backend. It accepts Main-authored `DesignTask` inputs through `start` or `run --command /design-produce`, requires `full_build`, and returns structured worker results and QA pending Main review. It cannot approve delivery. Complete policy and native adapter scope: `DESIGN_PRODUCTION_SPECIALIST.md`.

Tools are wrappers around existing Brain Design scripts. They normalize results into `PASS`, `REVISE_REQUIRED`, `BLOCKED`, or `ERROR`.

| Tool | Purpose | Input | Output | Blocking Authority | Permission | Script Backend | Failure Behavior |
|---|---|---|---|---|---|---|---|
| route_tool | Resolve route/product family | task text | route result | Blocks wrong workflow route | diagnostic_only | `design_brain_module_select.py` / router helpers | Creates route repair if unresolved |
| reference_usage_tool | Check output brand and reference group usage | candidate brand/reference IDs | usage gate result | Blocks repeated brand/reference reuse | plan_only | `design_brain_reference_usage_gate.py` | Creates reference-usage repair ticket |
| cognition_check_tool | Validate cognition receipt | receipt JSON | cognition PASS/FAIL | Blocks reference-led/template planning | plan_only | `design_brain_design_cognition_check.py` | Creates cognition repair ticket |
| section_layout_tool | Extract, match, validate, or select section layout patterns | reference evidence/catalog query | section layout result | Blocks duplicates and blocks pattern selection when no stable PASS pattern exists | plan_only | `design_brain_section_layout_extract.py` | Keeps weak extraction in `_incoming` until matching and hyper-accuracy PASS |
| subagent_orchestration_tool | Plan/verify subagent evidence | task/mode/evidence | subagent orchestration receipt | Blocks final when critical subagent evidence is missing | plan_only | `design_brain_subagent_orchestrate.py` | Creates subagent orchestration repair ticket |
| subagent_semantic_validator_tool | Validate subagent receipt content quality | evidence directory | semantic validation result | Blocks final when receipt content is fake or weak | plan_only | `design_brain_subagent_receipt_validate.py` | Creates subagent evidence repair ticket |
| simulation_tool | Run pre-build simulation | task/plan/cognition | verdict | Blocks build on REVISE/BLOCKED | plan_only | `design_brain_design_simulate.py` | Creates simulation repair ticket |
| layout_similarity_tool | Audit layout originality | fingerprints | audit receipt | Blocks copied scaffold | plan_only | `design_brain_layout_similarity_audit.py` | Creates layout repair ticket |
| build_session_tool | Manage lifecycle ledger | session evidence | lifecycle state | Blocks next/final if missing | full_build | `design_brain_build_session.py` | Creates lifecycle repair ticket |
| design_craft_adapter_tool | Add craft support | Brain Design request JSON | craft result | Support-only, cannot final approve | plan_only | Bundled `.design-brain/adapters/design-craft/scripts/craft_adapter.py` | Blocks override attempts |
| design_system_check_tool | Validate design system | receipt/build dir | status | Blocks final if missing | full_build | `design_brain_design_system_check.py` | Creates design-system ticket |
| web_deck_tool | Plan web deck stage, slide archetypes, and motion signature | task/style/direction | deck plan | Blocks build on an off-contract deck plan | plan_only | `design_brain_web_deck_plan.mjs` | Creates web-deck plan repair ticket |
| web_deck_audit_tool | Statically audit web deck stage and runtime fidelity | built deck | stage audit result | Blocks web-deck final on a P0 stage or runtime defect | plan_only | `design_brain_web_deck_audit.mjs` | Creates web-deck stage repair ticket |
| web_deck_render_review_tool | Review rendered web deck slides in a browser | built deck/required viewports | render review result | Blocks web-deck final on a P0 rendered defect or when the review cannot run | plan_only | `design_brain_web_deck_render_review.mjs` | Creates web-deck render repair ticket |
| post_build_audit_tool | Run post-build audit | build dir/session | final audit | Blocks final | full_build | `design_brain_post_build_audit.py` | Creates post-build ticket |
| batch_similarity_tool | Compare batch templates | fingerprints | matrix | Blocks similar batch | plan_only | `design_brain_batch_similarity_audit.py` | Creates batch similarity ticket |
| completion_receipt_tool | Create/verify completion receipt | session | receipt/final status | Blocks final | full_build | `design_brain_build_session.py` | Creates completion ticket |
| doctor_tool | Check runtime health | repo root | health report | Blocks export if failing | diagnostic_only | `design_brain_doctor.py` | Reports missing files |
| status_tool | Report current state | session | status JSON | Non-blocking | diagnostic_only | `design_brain_status_runtime.py` | Reports missing state |
| compact_context_tool | Compact session context | session | context packet | Non-blocking but required for resume | diagnostic_only | `design_brain_context_compact.py` | Reports compaction issue |

Design Craft adapter can run only after route/cognition and simulation or accepted plan context are present. It is never final authority.

`design_craft_adapter_tool` must prefer the bundled Design Craft adapter at `.design-brain/adapters/design-craft` so exported/installable Brain Design packs remain portable. A global `~/.codex/skills/design-craft` folder is only a development fallback.

`web_deck_tool`, `web_deck_audit_tool`, and `web_deck_render_review_tool` are medium-scoped to `web-deck` output. `web_deck_tool` runs at plan time, and `web_deck_audit_tool` plus `web_deck_render_review_tool` must both run before a web deck can be called complete. They enforce `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md` only: a PASS means the stage and the runtime are correct, and it cannot clear a failed post-build audit, originality gate, or completion receipt. A visible deck with no static audit and no render review is unverified evidence, not a PASS.

## reference_usage_tool Compatibility

`reference_usage_tool` supports the canonical reference usage gate arguments and compatibility aliases:

- canonical args: `--candidate-brand-name`, `--reference-ids`, `--reference-mode`, `--completion-receipt-path`, `--fingerprint-lock-path`, `--do-not-copy-boundary`
- alias args: `--candidate-name`, `--brand-name`, `--references`, `--mode`, `--receipt-path`, `--completion-receipt`, `--fingerprint-path`, `--fingerprint-lock`, `--do-not-copy`
- reference brand aliases: `--reference-brand-names`, `--reference-brands`, `--ref-brands`
- dry-run support for validating without mutating the registry
- JSON receipt output through `--json`
- receipt file output through `--write-receipt` and optional `--receipt-output`

The tool returns `PASS`, `REVISE_REQUIRED`, or `BLOCKED`. Runtime callers must treat non-PASS reference usage receipts as blocking evidence for reference-led templates.
