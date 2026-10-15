# Claude Code Architecture Study For Brain Design Runtime

Date: 2026-05-30
Reference ZIP: `<CODEX_DESIGN_WORKSPACE>\downloads\claude-code-main.zip`
Use: architecture study only

## Files And Folders Studied

The ZIP was inspected in-place with Python `zipfile`; no Claude Code source was copied into Brain Design.

Studied reference areas:

- `docs/architecture.md`
- `docs/commands.md`
- `docs/tools.md`
- `docs/subsystems.md`
- `docs/exploration-guide.md`
- `prompts/07-tool-system.md`
- `prompts/08-command-system.md`
- `prompts/10-context-and-prompts.md`
- file inventory only for `src/commands/`, `src/tools/`, `src/hooks/`, `src/tasks/`, `src/skills/`, `src/plugins/`, `src/bridge/`, and `src/context/`

## Relevant Architecture Patterns

- CLI command routing through a command registry.
- Tool registry where each tool has a name, purpose, inputs, permissions, backend, and failure behavior.
- Central permission check before tool execution.
- Session state that can be inspected, resumed, compacted, or finalized.
- Tool-loop style execution where each stage writes a normalized result.
- Hooks around important execution boundaries.
- Doctor/status commands for environment and runtime health.
- Task/agent delegation as a model for support-only adapter tools.
- Context compaction to preserve essential session state across long runs.
- History/resume/rewind ideas as runtime session operations.

## Patterns Not Adapted

- React/Ink terminal UI.
- Proprietary or internal auth flows.
- Telemetry, tracing, analytics, or internal rate-limit notices.
- Remote bridge, IDE auth, JWT/device trust, or private service integrations.
- Anthropic-internal gates or employee-only features.
- Raw Claude Code source implementation.
- Claude Code command names unrelated to design workflow.
- Claude Code tools unrelated to Brain Design gates.

## Mapping To Brain Design

- Command registry becomes Brain Design slash-like design commands such as `/design-route`, `/design-cognition`, `/design-simulate`, `/design-finalize`, and `/design-doctor`.
- Tool registry wraps existing Brain Design scripts: router, cognition checker, simulation, layout audit, build session lifecycle, design system check, post-build audit, batch similarity, doctor/status, and compaction.
- Permission modes become Brain Design workflow safety modes: `diagnostic_only`, `plan_only`, `safe_patch`, `archive_only`, `full_build`, `export_allowed`, and `delete_allowed`.
- Session state becomes `.design-brain/runtime/state/<session-id>/session-state.json`.
- Repair tickets become JSON records that block final readiness until closed and rerun.
- Context compaction becomes a local markdown/json summary of current design workflow state.
- Doctor/status become lightweight release/readiness commands for the runtime layer.

## Mapping To Design Craft

- Design Craft becomes a support-only adapter tool.
- The adapter receives Brain Design decisions as immutable inputs: route, product family, cognition, simulation verdict, layout audit status, and design-system requirement.
- It can return craft support: tokens, typography, spacing, component states, accessibility, source handoff, and polish notes.
- It cannot change route, product family, section structure, cognition status, simulation verdict, layout originality status, post-build status, or final readiness.

## Legal And Safety Note

No Claude Code source code, auth, telemetry, UI, tracing, or proprietary implementation detail was copied into Brain Design. The ZIP was used only to identify architectural patterns at a high level. Brain Design runtime implementation is original, CLI/JSON-based, and specific to template-production gates.

## Decision

Proceed with pattern-only adaptation:

- Command registry: yes.
- Tool registry: yes.
- Permission modes: yes.
- Hooks: yes.
- Session state: yes.
- Repair ticket queue: yes.
- Doctor/status: yes.
- Context compaction: yes.
- Raw Claude Code implementation: no.
