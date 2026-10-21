# Runtime Context Compaction and Explicit Resume

The existing session-state.json owns continuity. A checkpoint preserves work; it never proves visual PASS or final readiness. This is the 2.8.0-source continuity implementation, not restoration of unavailable 2.9.0 files.

## Project and session identity

Start a runtime session with an explicit --project-root when the design project differs from the plugin root. Save progress with:

    python scripts/design_brain_runtime.py checkpoint --session <session-dir> --checkpoint <checkpoint.json> --json
    python scripts/design_brain_runtime.py resume --session <session-dir> --json

Both commands require the exact session directory. Resume never chooses a global current-session/current-context pointer or another project's checkpoint. Existing sessions without a checkpoint return UNKNOWN and a recovery action; inspect their real artifacts and save a checkpoint rather than restarting all slides automatically.

Checkpoint input is a JSON object with sessionId and canonical absolute projectRoot matching the session. It accepts slides, sources, artifacts, evidence, constraints, decisions, owner and nextAction. Maximum input size is 1 MiB; slide and individual reference lists are bounded to 500 items. No silent truncation occurs. Source/evidence references use path and sha256; relative paths resolve inside projectRoot and paths escaping it are rejected.

Compaction is not a final readiness proof. It is a continuity tool.

The runtime status, compatibility status and compactor all use `progress_projection()` from design_brain_runtime. It recomputes current hashes, tickets, missing gates and final readiness. The full checkpoint (including constraints, accepted identities, unknown operations and invalid data needing reconciliation) stays in per-session context-summary.json. `nextActionDetail` is the shared owner/target/output/checks object; the legacy `nextAction` string is its display. Do not replay an unknown operation or reuse visual PASS. Before continuing, prepare-context with a new per-role context epoch and read applicable full sources; prior manifests are not read receipts.
