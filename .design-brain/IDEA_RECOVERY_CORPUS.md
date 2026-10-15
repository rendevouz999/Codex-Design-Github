# Idea Recovery Corpus

Purpose: when AI lacks layout ideas, Brain Design may consult a local inspiration corpus for layout grammar recovery.

Default local path:

`<CODEX_DESIGN_WORKSPACE>\Template Website`

## Rules

- This corpus is optional and local-only.
- Do not include the corpus in public ZIP packages.
- Do not copy corpus layout.
- Use the corpus only to discover alternative layout grammar, section rhythm, grid direction, hero treatment, or composition ideas.
- Any idea taken from the corpus must pass Reference Boundary, Color Role Re-Mapping, Structural Reconfiguration, and Pattern Divergence.
- Corpus-inspired layout must be fingerprinted as `sourceType: corpus_inspiration`.
- Candidate output must be audited against the user reference and previous AI templates.
- Public-core packages may include only the example config, never the local corpus or local config.

