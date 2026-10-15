# Runtime Permission Modes

Permission modes decide what the runtime may do.

| Mode | Meaning |
|---|---|
| `diagnostic_only` | Read-only checks. Cannot modify source or claim `READY`. |
| `plan_only` | Can create plans, receipts, and runtime state. Cannot build/export/delete. |
| `safe_patch` | Can edit docs/scripts safely. Cannot delete/export. |
| `archive_only` | Can move files to archive with manifest. Cannot permanently delete. |
| `full_build` | Can run build workflow and lifecycle gates. Cannot export. |
| `export_allowed` | Can export ZIP only after source integrity passes. |
| `delete_allowed` | Can permanently delete only with explicit user instruction. |

Rules:

- Every command/tool must pass permission validation.
- `diagnostic_only` cannot produce full final `READY`.
- `safe_patch` can patch docs/scripts but cannot delete.
- `archive_only` moves only to documented archive paths.
- `full_build` must still run cognition, simulation, layout, design system, post-build, completion, and verify-final.
- `export_allowed` is required for ZIP export.
- `delete_allowed` requires explicit user command.

