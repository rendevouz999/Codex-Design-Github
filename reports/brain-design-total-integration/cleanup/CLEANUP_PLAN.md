# Brain Design Cleanup Plan

Generated: 2026-05-30

## Scope

This cleanup is source stabilization only. It does not export a package ZIP and does not bump Brain Design version.

## Safety Rules

- Preserve files by moving them to archive locations unless explicitly marked as generated cache.
- Do not delete old backups.
- Do not move manifest-owned mandatory files.
- Keep report files for this stabilization in `reports/brain-design-total-integration/`.
- Keep public package behavior unchanged except for stronger source-integrity checks.

## Archive Targets

- External source archives: `<CODEX_DESIGN_WORKSPACE>-Archive\external-sources\`
- Backup-file archives: `<CODEX_DESIGN_WORKSPACE>-Archive\brain-design-backups\`
- Deprecated helper archives: `<CODEX_DESIGN_WORKSPACE>-Archive\brain-design-deprecated-scripts\`
- Generated evidence archive: `<CODEX_DESIGN_WORKSPACE>-Archive\brain-design-generated-evidence\`
- Local evidence archive marker: `.design-brain/evidence/archive/README.md`

## Move Plan

| Source | Action | Reason |
| --- | --- | --- |
| `downloads/MiroFish` | Move to external source archive | Forbidden external source in active workspace; package integrity blocker. |
| `*.bak-*`, `*.backup-*`, `*.orig`, `*.old`, `*.tmp` in active Brain Design scope | Move to backup archive | Keep recoverable but remove from active source/integrity scope. |
| `.design-brain/context-packets` generated runs | Move to generated evidence archive | Evidence history, not active workflow owner. |
| `.design-brain/pptx-precision-reviews` generated reports | Move to generated evidence archive | Historical review evidence, not active package file. |
| `.design-brain/reference-insights` generated dated reports | Move generated dated files, keep active README/docs | Evidence history, not active package owner. |
| old one-off helper scripts not manifest-owned | Move only after reference check | Avoid breaking active workflow. |

## No Permanent Deletions Planned

No source files are planned for permanent deletion. Cache cleanup later may remove `__pycache__` and `*.pyc` only.
