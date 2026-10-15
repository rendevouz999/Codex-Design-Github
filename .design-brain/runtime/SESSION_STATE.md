# Runtime Session State

Generated session files live under `.design-brain/runtime/state/`.

Current session files:

- `.design-brain/runtime/state/current-session.json`
- `.design-brain/runtime/state/session-history.jsonl`
- `.design-brain/runtime/state/current-context.md`
- `.design-brain/runtime/state/open-repair-tickets.json`

Per-session files:

- `.design-brain/runtime/state/<session-id>/session-state.json`
- `.design-brain/runtime/state/<session-id>/history.jsonl`
- `.design-brain/runtime/state/<session-id>/compact-context.md`
- `.design-brain/runtime/state/<session-id>/repair-tickets.json`

State records:

- session id
- `requiredStages`
- task
- permission mode
- route/product family
- expected template count
- current template id
- completed stages
- missing stages
- active tool
- tool results
- open repair tickets
- final readiness
- compact context path
