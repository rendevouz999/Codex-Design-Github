# Runtime Hooks

## Executable production hook

`scripts/design_brain_runtime.py::command_start` calls `command_production` automatically when Main supplies an authorized `--production-request`. The implementation is `scripts/design_production/hook.py::DesignProductionAutoHook.dispatch`. `/design-produce` reuses this boundary for subsequent assigned stages/revisions. This is an executable integration; it does not rely on the illustrative hook configuration below. The Node prompt hook only routes Main to this workflow and never starts a model from unscoped conversation text.

Main remains external; this path uses one `gpt-6.1-sol` SDK Agent and one OS-locked execution. Main review, cancellation, and recovery are controller commands, never Specialist tools. See [Design Production Specialist](DESIGN_PRODUCTION_SPECIALIST.md).

Hooks are named checkpoints around the runtime loop. They are configured in `hooks.example.json`; local overrides may use ignored `hooks.local.json`.

Hooks:

- before_route
- after_route
- before_cognition
- after_cognition
- before_simulation
- after_simulation
- before_layout_audit
- after_layout_audit
- before_build
- after_build
- before_craft
- after_craft
- before_design_system
- after_design_system
- before_web_deck_audit
- after_web_deck_audit
- before_web_deck_render_review
- after_web_deck_render_review
- before_post_build
- after_post_build
- before_final
- after_repair
- before_export

## before_final Required Checks

- build session `verify-final`
- completion receipt exists
- design system evidence is sufficient
- post-build pass
- layout audit pass
- web deck static audit and render review pass for `web-deck` output
- open repair tickets = 0

If any check fails, final status is blocked.

The web deck checks apply only when the medium is `web-deck`. They enforce `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`, run inside the existing design-system and post-build stages, and add no stage to the required stage order.

