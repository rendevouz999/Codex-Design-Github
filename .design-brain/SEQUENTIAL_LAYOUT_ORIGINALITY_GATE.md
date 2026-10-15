# Sequential Layout Originality Gate

Purpose: prevent AI-built templates from copying reference layouts or becoming too similar to previous AI-built templates in the same batch.

Also load `.design-brain/LAYOUT_FLUIDITY_EXPANSION.md`. The gate must catch layouts that feel `kaku`: stiff, over-regular, boxed, or sibling-like because their spatial gesture and section silhouettes repeat.

## Mandatory Cycle

Template A:

Reference A -> Plan A -> Layout Audit A vs Reference A -> Build A -> Design System A -> Post-Build Audit A -> Fingerprint Lock A

Template B:

Reference B -> Plan B -> Layout Audit B vs Reference B -> Layout Audit B vs Template A -> Build B -> Design System B -> Post-Build Audit B -> Fingerprint Lock B

Template C:

Reference C -> Plan C -> Layout Audit C vs Reference C -> Layout Audit C vs Template A + B -> Build C -> Design System C -> Post-Build Audit C -> Fingerprint Lock C

Template D:

Reference D -> Plan D -> Layout Audit D vs Reference D -> Layout Audit D vs Template A + B + C -> Build D -> Design System D -> Post-Build Audit D -> Fingerprint Lock D

## Rules

- A new template cannot proceed if it is too similar to its reference.
- A new template cannot proceed if it is too similar to any previous AI output in the session.
- Similarity must be axis-based, not only overall.
- Recolor is not a valid repair for layout similarity.
- Image replacement alone is not a valid repair for layout similarity.
- Repair must reconfigure layout, structure, rhythm, component cadence, CTA placement, hero grammar, layout gesture, section silhouettes, composition tension, focal path, breakout behavior, or visual grammar.
- If AI lacks layout ideas, it may use the local idea recovery corpus, but it must not copy corpus layouts.
- Fingerprint lock is required before the next batch template can start.
- A plan that feels polished but stiff must be revised before build. Stiffness is a layout defect, not a style preference.

## Active Triggers

This gate is active for reference-led template builds, batch template builds, marketplace templates, Figma/source templates, and tasks asking for multiple distinct templates.

It may be skipped only for explicit quick draft, rough exploration, diagnostic, or non-template tasks. When skipped, the final response must state that the layout originality audit was skipped.
