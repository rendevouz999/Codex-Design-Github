# Design Brain

The Codex Design Brain is a local, repo-based orchestration layer for better design work. It stores preferences, critique rules, reusable patterns, review reports, and reflection notes that Codex should read before creating or improving UI, frontend, landing pages, dashboards, components, preview layouts, mockups, design systems, or marketplace-ready templates.

This system does not retrain or modify the Codex model. It gives Codex persistent local context and a controlled workflow:

1. Read design memory and preferences.
2. For template product work, define the product type, buyer, structure, style pack, and preview direction.
3. For reference-based work, extract evidence-backed designer cognition before structure planning.
4. For Figma reference links or template sources, inspect the full page/frame/component/state scheme and infer the product standard before planning.
5. For multiple-template work, run a sequential reference-led cycle for each template.
6. Create the first draft.
7. Critique the result.
8. Revise weak areas.
9. Generate new learning questions when the task is part of long-horizon designer-schema improvement.
10. Research evidence and update workflow rules when the lesson is actionable.
11. Save reusable feedback as lessons.

Rule conflicts are resolved by `.design-brain/SOURCE_OF_TRUTH_MAP.md`. This README explains the system, but active behavior belongs to the owner guard, autoload policy, router, registry, product playbooks, batch gates, and quality gates.

## Source-of-Truth Identity Layer

The Source-of-Truth Identity Layer is the conceptual core of Design Brain. It defines who Design Brain is, how it thinks, how it treats references, how it understands the user/director, and how it decides which memory, journal, or workflow to load.

For template, reference-based, naming, marketplace preview, or critique tasks, use `.design-brain/AUTOLOAD_POLICY.md` and `.design-brain/CONTEXT_PRIORITY.md`.

For Figma website template work, `.design-brain/FIGMA_OUTPUT_TARGET.md` stores the output-target policy. Create a new Figma design file only when a valid configured project/file target exists. If the target is missing, placeholder, or the publish-safe package has no local config, do not call `create_new_file`; ask for a valid target or continue with local planning only.

For Figma reference-link work, `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md` and `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md` force Codex to study the reference as a template system: product purpose, visual direction, section structure, grid/layout, typography hierarchy, color-role system, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, Figma source hygiene, pages, frames, sections, components, variants, states, design-system panels, density rhythm, color/effect logic, and product-family standard. A Figma reference schema receipt must exist before building.

For long-horizon learning after template builds or reference study, `.design-brain/CONTINUOUS_DESIGNER_LEARNING_LOOP.md` keeps the process question-led: build or study, audit the result, generate a new question, research evidence, distill designer schema, and apply the rule in the next design cycle.

Generate a task-specific loading summary with:

```bash
python scripts/design_brain_context_packet.py --task "..." --reference --template-type "..." --niche "..." --dry-run
```

Context packets do not replace journals. They are working summaries that tell Codex what should be loaded.

## Design-Anything Selective Index

Design Brain now routes by product medium before visual style. Use the module selector when the task could be a website, dashboard, ecommerce page, portfolio, PowerPoint/deck, UI kit, brand kit, marketplace preview, mobile app, email/newsletter, static canvas/poster, or document/report:

```bash
python scripts/design_brain_module_select.py --task "..." --template-type "..." --niche "..." --target-buyer "..." --visual-mood "..." --dry-run
```

The selector reads `.design-brain/registry/modules.json`, then returns the craft modules, seed pack, direction pack, validators, and source files to load. Generated selective indexes from `open-design` and `awesome-claude-skills` belong in `.design-brain/external-indexes/` and are not stable memory by default.

## Natural Intent Autopilot

Design Brain is commandless for the user. The user can describe the design task naturally, and Codex should infer the internal workflow.

Examples:

- "ini referensi, buat template baru" activates reference insight, originality guard, and template product workflow.
- "buat 5 template tapi jangan mirip" activates Designer Cognition Layer and Sequential Reference-Led Batch Workflow: learn evidence-backed designer logic, build one template, lock its pattern memory, then repeat for the next template.
- "kasih nama yang beda dari sebelumnya" activates the naming ledger and name check.
- "buat preview cover untuk marketplace" activates template orchestration and preview presentation rules.
- "lanjut pelajari sampai paham pola pikir designer" activates Continuous Designer Learning Loop, Designer Cognition Layer, reference insight, and web-evidence study when needed.
- "ini terlalu mirip struktur sebelumnya" activates design critic, originality guard, and sequential pattern-lock similarity reasoning.

Use `scripts/design_brain_intent_route.py` when a task needs an explicit routing report:

```bash
python scripts/design_brain_intent_route.py --task "Aku punya referensi, buatkan 5 template landing page yang berbeda strukturnya dan jangan identik" --has-reference --template-count 5 --dry-run
```

The report is an internal context packet. It should not make the user learn workflow names.

## Sequential Reference-Led Batch Workflow

For multiple-template tasks, Design Brain works one complete template at a time.

All-at-once batch planning is invalid. Codex should not study all references once, create one master section scaffold, and produce many variants. That pattern creates templates that feel identical.

Required batch rhythm:

1. Pick the next active product-purpose reference group from the available corpus for template 1. Use up to 10 varied references when enough matching candidates exist.
2. For website templates, classify the product family and select matching references from `Template Website`.
3. Infer buyer decision model, designer intent, attention strategy, emotional rhythm, trust strategy, density strategy, conversion logic, component reasoning, and evidence-backed do-not-copy boundaries.
4. Build template 1 to completion using the correct medium playbook and standard/full structure.
5. Lock template 1's opening strategy, hero grammar, trust strategy, density rhythm, component system, CTA logic, visual motif, storytelling arc, and reference group.
6. Repeat the same process from fresh reference selection for template 2.
7. Continue until the user's requested count is complete.

Use the helper only as an internal planning report:

```bash
python scripts/design_brain_sequential_batch.py --task "buat 5 website template yang tidak identik" --count 5 --reference-root "Template Website" --dry-run
```

The script does not modify memory or journals. It only produces a working plan so Codex keeps the one-template-at-a-time rhythm.

## Files

- `DESIGN_MEMORY.md` stores long-term design taste and reusable rules.
- `DESIGN_PREFERENCES.json` stores weighted design preferences for structured guidance.
- `DESIGN_SOUL.md`, `DESIGN_IDENTITY.md`, `USER_DESIGN_CONTEXT.md`, `DESIGN_PRINCIPLES.md`, `DESIGN_OPERATING_RULES.md`, `AUTOLOAD_POLICY.md`, `DESIGNER_COGNITION_LAYER.md`, `WEBSITE_TEMPLATE_REFERENCE_CORPUS.md`, `TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`, `FIGMA_OUTPUT_TARGET.md`, `FIGMA_REFERENCE_DEEP_STUDY.md`, `FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md`, `FIGMA_REFERENCE_LEARNING_CORPUS.md`, `CONTINUOUS_DESIGNER_LEARNING_LOOP.md`, `FIGMA_AUTO_LAYOUT_ENFORCEMENT.md`, `CONTEXT_PRIORITY.md`, `NATURAL_INTENT_ROUTER.md`, `DESIGN_AUTOPILOT.md`, `WORKFLOW_TRIGGER_MAP.md`, `RESPONSE_BEHAVIOR.md`, and `SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md` define the Source-of-Truth Identity Layer and natural workflow routing.
- `TEMPLATE_PRODUCT_MEMORY.md` stores marketplace-specific rules for sellable template products.
- `TEMPLATE_PRODUCT_INTELLIGENCE.md` defines the template product decision layer.
- `TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md` defines when source templates should use text clue placeholders such as `image placeholder` and `profile photo placeholder` instead of generated/final images.
- `TEMPLATE_TAXONOMY.md` classifies template product types, niches, and marketplace categories.
- `TEMPLATE_STRUCTURE_RULES.md` defines required sections, components, states, and editable areas.
- `TEMPLATE_STYLE_ROUTER.md` explains TypeUI-derived style routing.
- `TEMPLATE_STYLE_PACKS.json` defines scalable style packs and conflict rules.
- `TEMPLATE_PRODUCT_QUALITY_GATE.md` provides the sellable-template quality gate.
- `MARKETPLACE_QUALITY_GATE.md` provides a commercial readiness gate for template products.
- `PREVIEW_PRESENTATION_SYSTEM.md` guides covers, previews, section breakdowns, and mockup overviews.
- `WEB_DECK_INTELLIGENCE.md`, `WEB_DECK_STAGE_GATE.md`, `WEB_DECK_MOTION_GRAMMAR.md`, `WEB_DECK_DELIVERY_CONTRACT.md`, and `DECK_SOURCE_BRIDGE.md` define the Web Deck medium: browser-rendered deck planning, the fixed 16:9 stage gate, motion grammar, delivery/export rules, and reading an existing static deck as planning material.
- `web-deck/` holds the deck plan schema, stage stylesheet, and dependency-free deck runtime used by generated web decks.
- `STYLE_PACKS.json` stores reusable style pack options for template planning.
- `VISUAL_CRITIQUE_CHECKLIST.md` provides a 1-10 review rubric.
- `REFLECTION_LOG.md` captures future user feedback and lessons.
- `PATTERN_LIBRARY.md` stores reusable section and layout patterns.
- `reviews/` stores structured critique reports generated during substantial design tasks.

## Memory Layers

- `DESIGN_MEMORY.md` is stable long-term taste. Update it only when a lesson repeats across multiple tasks or the user explicitly asks.
- `DESIGN_PREFERENCES.json` contains weighted preferences. Do not adjust weights from one feedback item.
- Template Product Intelligence files specialize the system for marketplace-ready templates without changing core design preference weights.
- `REFLECTION_LOG.md` is the controlled feedback history. Use it to preserve user feedback, extract reusable lessons, and avoid repeating mistakes.
- `reviews/` contains structured critique reports. Reports help Codex score a specific design pass, plan revisions, and identify reflection lesson candidates.

## Template Product Planning

Use `scripts/design_brain_template_orchestrate.py` as the recommended entry point for sellable template product tasks. It creates one orchestration report that combines product diagnosis, style strategy, section structure, editability requirements, preview direction, quality gate, and next review commands.

For multiple-template work, use orchestration per template cycle. Do not use one orchestration report as a reusable scaffold for the whole batch.

```bash
python scripts/design_brain_template_orchestrate.py --template-type "landing-page" --niche "wedding-planning" --target-buyer "wedding planners and event studios" --visual-mood "elegant premium editorial"
```

Use `scripts/design_brain_template_plan.py` before designing marketplace-ready template products:

```bash
python scripts/design_brain_template_plan.py --template-type "SaaS landing page template" --niche "AI automation" --target-buyer "Startup founders and SaaS marketers" --visual-mood "Premium, clean, confident"
```

The planner creates a structured product plan with recommended style packs, required section structure, editable areas, preview direction, marketplace quality checklist, and risks of generic output.

Use `scripts/design_brain_typeui_ingest.py` to normalize TypeUI `DESIGN.md` files into `typeui-skills/raw/` and extract structured JSON into `typeui-skills/extracted/`. Use `scripts/design_brain_style_select.py` to choose a relevant style pack before designing. Do not activate all TypeUI styles at once.

## Reflection Utility

Use `scripts/design_brain_reflect.py` when user feedback contains a reusable design lesson:

```bash
python scripts/design_brain_reflect.py --task "..." --feedback "..." --went-wrong "..." --lesson "..." --rule "..."
```

Use `--dry-run` to preview the entry without changing `REFLECTION_LOG.md`.

## Local Skill

Use `.agents/skills/design-critic/SKILL.md` when creating, reviewing, or improving UI/design work in this repository.

The local skill is instruction-only. It tells Codex how to read this folder, critique output, make concrete revisions, and store reusable lessons from user feedback.
