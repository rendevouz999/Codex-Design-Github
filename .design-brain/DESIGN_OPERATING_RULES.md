# Design Operating Rules

Use these rules to decide which Design Brain files and workflows to load.

## Natural Workflow Inference

Prefer natural workflow inference over explicit command dependency.

Commands and scripts exist to support Codex internally, not to make the user manage the workflow manually. When the user says things like "ini referensi", "buat batch template", "jangan copy layout", "kasih nama", or "review ini", infer the relevant workflow and proceed without asking for internal command names.

If the user gives broad trust or complains that the design work is too restrained, translate that into immediate creative agency: classify the product family, expand to the expected structure standard, vary the composition language, and repair weak visual decisions without waiting for another prompt.

For website, web template, Figma website template, and standard landing-page template work, competitive standard starts at 8 meaningful sections/blocks. Do not use minimalist, safe, simple, fallback, clean, restrained, or basic as a reason for fewer than 8 sections. Under-8 structure is allowed only when the user explicitly asks for a hero/header kit, micro landing page, narrow campaign, squeeze page, waitlist page, or another intentionally small product.

If the user emphasizes quality over output count or complains about duplicate-looking batch output, treat completion timing as subordinate to quality. Do not present multiple templates until cross-template similarity has been audited pairwise and every later template stays below the strict 10 percent similarity gate against accepted earlier fingerprints.

For batch template work, the relevant workflow is Batch Template Hard Gates plus Sequential Reference-Led Batch Workflow. Build one template pair at a time from the next active product-purpose reference group: main template plus that template's own design-system board. Use up to 10 eligible varied references when the local corpus has enough same-purpose matches. Lock the pair only after the design-system board is complete, checked, and receipt-backed, then scaffold-dispose the spent page builder before starting the next one. Do not use one global batch scaffold. For website/Figma/source batches, final READY also requires Serial Provenance Gate PASS.

For batch template work, quality means each output should move toward its own selected reference insight and away from accepted previous template fingerprints. If a new template feels more like a variant of a previous Codex-built template than a reinterpretation of its selected reference, stop and rebuild its structure plan before implementation.

When a batch output feels similar, diagnose the similarity root cause before revising:

1. Structure similarity means same hero grammar, section order, module cadence, proof/CTA rhythm, or footer closure. Rebuild the newer template from a fresh structure fingerprint.
2. Composition similarity means same title/media placement, card grouping, grid rhythm, or balance. Recompose the affected sections.
3. Effect similarity means same glow, shadow, blur, border, gradient light, or placeholder treatment. Redesign the effect language for the product.
4. Color-only similarity means structure and composition are distinct but the palette or color-role mapping feels too close. Change the color system only.
5. Copy/naming-only similarity means the visual system is distinct but words, labels, metaphors, or naming rhythm repeat. Rewrite copy and naming only.

Do not recolor a structure defect. Do not rebuild a strong structure for a color-only defect.

After each template, dispose of the page-level scaffold that produced it. The pattern lock is negative memory, not a reusable builder. Only primitive helpers may survive into the next cycle; hero grammar, section order, module cadence, CTA/proof/footer closure, and design-system panel order must be reset unless explicitly justified by the new reference cognition. If the scaffold exists as a temporary file, scratch script, page schema, data object, or generated builder, delete it or remove it from active context after recording what must not repeat.

## If The User Provides A Reference

1. Read `.design-brain/REFERENCE_INSIGHT_SYSTEM.md`.
2. If the reference is a Figma link, Figma frame, Figma template file, or `.fig` source, read `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md` and `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md`, then complete a Figma reference schema receipt before structure planning.
3. Read `.design-brain/ORIGINALITY_GUARD.md`.
4. Check `.design-brain/REFERENCE_INSIGHT_JOURNAL.md`.
5. Extract reference insight before designing.
6. Identify what must not be copied.
7. Reinterpret structure, hierarchy, flow, and composition.
8. Save valuable insight with `scripts/design_brain_reference_insight.py` when appropriate.

Do not default to a minimalist structure when the reference's product standard is unclear. Classify the product family, inspect more Figma evidence, use local/category corpus, or ask one targeted question.

## If The User Asks For A Template Product

1. Read `.design-brain/TEMPLATE_PRODUCT_INTELLIGENCE.md`.
2. Run or follow `scripts/design_brain_template_orchestrate.py`.
3. Select relevant style packs only.
4. Use `.design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md`.
5. Plan editable areas, preview direction, and marketplace value.

## If The Task Uses Template References Or Creates A New Template Brand

1. Read `.design-brain/TEMPLATE_REFERENCE_USAGE_POLICY.md`.
2. Check `.design-brain/TEMPLATE_REFERENCE_USAGE_REGISTRY.json`.
3. Check `.design-brain/TEMPLATE_NAMING_LEDGER.md`.
4. Run or follow `scripts/design_brain_reference_usage_gate.py check --candidate-brand-name "..." --reference-ids "..." --reference-mode "single|pair|triple" --require-exhaustion-order` for brand/reference-brand safety when using the legacy manual gate.
5. If the gate blocks the candidate brand, choose a new name before reference insight or build.
6. If the legacy gate blocks the manual reference set, choose a safer set before extracting Style DNA. For website local selector work, follow the selector's active product-purpose group rotation instead of collapsing to a single/pair/triple.
7. Record the allowed group in the build session with `scripts/design_brain_build_session.py register-reference-usage-check`.
8. After completion receipt, run or follow `scripts/design_brain_reference_usage_gate.py record` and then `scripts/design_brain_build_session.py register-reference-usage-record` before final delivery.

## If The Output Is A Figma Template

1. Read `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md`.
2. Build editable sections, nav, cards, CTAs, forms, repeated rows, dashboards, responsive groups, and design-system panels with real auto-layout.
3. Use manual x/y positioning only for documented decorative or overlay exceptions.
4. Include an auto-layout receipt before calling the template complete.

## If The User Asks For Multiple Templates

1. Read `.design-brain/BATCH_TEMPLATE_HARD_GATES.md`.
2. Read `.design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md`.
3. Use `.design-brain/templates/SEQUENTIAL_REFERENCE_BATCH_CYCLE.md` as the working shape.
4. For template 1, select the next active product-purpose reference group and study purpose, audience, structure, visual logic, and do-not-copy boundaries. Use up to 10 varied references when enough matching candidates exist.
5. Build template 1 to completion using the relevant medium playbook and standard template structure.
6. Build design-system board/source section 1 for template 1 before starting template 2.
7. Inspect and validate template 1 plus design-system board 1; if the design system is missing, receipt-only, minimalist-thin, invalid, or visually rough, stop and finish it.
8. Lock the hero, section order, module grammar, visual rhythm, conversion closure, color-role system, effect language, design-system panel logic, and reference group used.
9. Dispose of the scaffold used for template 1: do not copy its page schema, hero builder, section sequence, card/grid cadence, CTA/proof/footer closure, or design-system panel order into template 2.
10. Record a scaffold disposal receipt before template 2 starts: name the scaffold, confirm it is permanently removed from active context, list any temporary scaffold artifacts deleted, and list primitive helpers retained.
11. Audit template 2 against template 1 and diagnose the similarity root cause. If similarity reaches 10 percent on structure-defining axes, keep template 1 as the accepted fingerprint and rebuild template 2 from a fresh structure fingerprint. If the only issue is color, recolor template 2 instead of rebuilding.
12. Start each later template from a blank structure fingerprint and repeat steps 4-11 until the request is complete.
13. Check all outputs pairwise against locked and disposed patterns before final delivery.

## If The User Asks For Naming

1. Read `.design-brain/TEMPLATE_NAMING_LEDGER.md`.
2. Run or follow `scripts/design_brain_name_check.py`.
3. Avoid repeated prefixes, suffixes, metaphors, and naming rhythms.

## If A Template Direction Is Accepted

Save a record with `scripts/design_brain_build_record.py`.

This updates:

- `.design-brain/TEMPLATE_BUILD_JOURNAL.md`
- `.design-brain/TEMPLATE_NAMING_LEDGER.md`

## If The User Gives Feedback

Save reusable lessons with `scripts/design_brain_reflect.py`.

Do not automatically promote feedback into stable memory.

## If The Task Is Small

Do not overload the workflow. Use only relevant rules.

Small copy edits, tiny CSS fixes, or direct implementation details do not require the full source-of-truth workflow unless reference, template, naming, marketplace, or originality risk is involved.
