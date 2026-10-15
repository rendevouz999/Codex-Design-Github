# Runtime Context Compaction

Runtime context compaction writes compact context summaries for resume-safe design sessions.

Context compaction writes a short packet for long-running design sessions.

The packet includes:

- active workflow
- current session
- current template
- active constraints
- route/product family
- latest gate results
- finished gates
- failed gates
- open tickets
- next action
- final blocking reason

Outputs:

- `.design-brain/runtime/state/current-context.md`
- `.design-brain/runtime/state/context-summary.json`
- per-session `compact-context.md`

Compaction is not a final readiness proof. It is a continuity tool.
