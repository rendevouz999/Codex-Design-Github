# Claude Code Adaptation Boundary

`<CODEX_DESIGN_WORKSPACE>\downloads\claude-code-main.zip` was used only as an architecture reference.

Brain Design adapted these general patterns:

- command registry
- tool registry
- permission modes
- session state
- hooks
- repair tickets
- doctor/status
- context compaction
- support-tool adapter boundaries

Brain Design did not copy:

- Claude Code source implementation
- auth logic
- telemetry or tracing
- terminal UI implementation
- internal bridge/device trust logic
- proprietary service integrations
- Claude Code package files

The Brain Design runtime is an original CLI/JSON/receipt-based implementation that wraps existing Brain Design gates.
