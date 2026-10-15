# Brain Design Runtime

Brain Design Runtime is the CLI/JSON operating loop for Brain Design. It wraps the existing Brain Design gates instead of replacing them.

Runtime responsibilities:

- start and resume design sessions
- route slash-like design commands
- call registered Brain Design tools
- enforce permission modes
- record session state
- create and close repair tickets
- compact context
- run doctor/status checks
- block final delivery until required gates pass

Runtime state is generated and local-only. Do not package generated state.

Authorized native production now runs through the existing runtime's [single Design Production Specialist](DESIGN_PRODUCTION_SPECIALIST.md). `start --production-request` invokes its auto-hook; `/design-produce` handles subsequent scoped work. Main keeps creative control and final approval. SDK dependencies live in `.venv-design-production`; no additional service is installed.

Core files:

- `DESIGN_AGENT_RUNTIME.md`
- `COMMAND_REGISTRY.md`
- `TOOL_REGISTRY.md`
- `PERMISSION_MODES.md`
- `HOOKS.md`
- `SESSION_STATE.md`
- `REPAIR_TICKETS.md`
- `CONTEXT_COMPACTION.md`
- `DOCTOR_STATUS.md`
- `hooks.example.json`

