# Design Brain Installation

Use `scripts/install_design_brain.py` to install Codex Design Brain into another repository without copying generated history by default.

## Dry-Run Install

Preview all actions before writing files:

```bash
python scripts/install_design_brain.py --target "<YOUR_PROJECT_PATH>" --dry-run
```

## Real Install

Install managed files into the target project:

```bash
python scripts/install_design_brain.py --target "<YOUR_PROJECT_PATH>"
```

## Force Install

Use `--force` only when you intentionally want to overwrite Design Brain-managed files. Existing managed files receive timestamped snapshots first:

```bash
python scripts/install_design_brain.py --target "<YOUR_PROJECT_PATH>" --force
```

## Include History

By default, the installer creates a clean fresh `.design-brain/REFLECTION_LOG.md`. It does not copy private reflection history into new projects. To include the current reflection history:

```bash
python scripts/install_design_brain.py --target "<YOUR_PROJECT_PATH>" --include-history
```

## What Is Copied

- The Design Brain section for `AGENTS.md`
- `.design-brain/README.md`
- `.design-brain/MANIFEST.json`
- `.design-brain/INSTALLATION.md`
- `.design-brain/PILOT_WORKFLOW.md`
- `.design-brain/QUICK_START.md`
- `.design-brain/DESIGN_MEMORY.md`
- `.design-brain/DESIGN_PREFERENCES.json`
- `.design-brain/DESIGN_SOUL.md`
- `.design-brain/DESIGN_IDENTITY.md`
- `.design-brain/USER_DESIGN_CONTEXT.md`
- `.design-brain/DESIGN_PRINCIPLES.md`
- `.design-brain/DESIGN_OPERATING_RULES.md`
- `.design-brain/AUTOLOAD_POLICY.md`
- `.design-brain/CONTEXT_PRIORITY.md`
- `.design-brain/REFERENCE_INSIGHT_SYSTEM.md`
- `.design-brain/REFERENCE_INSIGHT_JOURNAL.md`
- `.design-brain/TEMPLATE_BUILD_JOURNAL.md`
- `.design-brain/TEMPLATE_NAMING_LEDGER.md`
- `.design-brain/ORIGINALITY_GUARD.md`
- `.design-brain/TEMPLATE_PRODUCT_INTELLIGENCE.md`
- `.design-brain/TEMPLATE_STYLE_ROUTER.md`
- `.design-brain/TEMPLATE_STYLE_PACKS.json`
- `.design-brain/TEMPLATE_ORCHESTRATOR.md`
- `.design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md`
- `.design-brain/TEMPLATE_PRODUCT_MEMORY.md`
- `.design-brain/TEMPLATE_TAXONOMY.md`
- `.design-brain/TEMPLATE_STRUCTURE_RULES.md`
- `.design-brain/MARKETPLACE_QUALITY_GATE.md`
- `.design-brain/PREVIEW_PRESENTATION_SYSTEM.md`
- `.design-brain/STYLE_PACKS.json`
- `.design-brain/VISUAL_CRITIQUE_CHECKLIST.md`
- `.design-brain/PATTERN_LIBRARY.md`
- `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md`
- `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`
- `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`
- `skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md`
- `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md`
- `skills/presentation-deck/resources/web-deck/` deck plan schema, stage stylesheet, and deck runtime
- `.design-brain/REFLECTION_LOG.md`
- `.design-brain/typeui-skills/README.md`
- `.design-brain/context-packets/README.md`
- `.design-brain/reference-insights/README.md`
- `.design-brain/template-orchestrations/README.md`
- README files for pilots, reviews, screenshots, visual reviews, and promotion proposals
- `.design-brain/templates/`
- `.agents/skills/design-critic/SKILL.md`
- `scripts/install_design_brain.py`
- `scripts/design_brain_typeui_ingest.py`
- `scripts/design_brain_style_select.py`
- `scripts/design_brain_template_plan.py`
- `scripts/design_brain_template_orchestrate.py`
- `scripts/design_brain_context_packet.py`
- `scripts/design_brain_reference_insight.py`
- `scripts/design_brain_name_check.py`
- `scripts/design_brain_build_record.py`
- Design Brain scripts in `scripts/`

## What Is Not Copied By Default

- Generated review reports in `.design-brain/reviews/*.md`
- Generated pilot reports in `.design-brain/pilots/*.md`
- Generated context packets in `.design-brain/context-packets/*.md`
- Generated reference insight files in `.design-brain/reference-insights/*.md`
- Generated template product plans in `.design-brain/template-plans/*.md`
- Generated template orchestration reports in `.design-brain/template-orchestrations/*.md`
- Generated visual review reports in `.design-brain/visual-reviews/*.md`
- Generated promotion proposals in `.design-brain/promotion-proposals/*.md`
- Screenshot files in `.design-brain/screenshots/*`
- Raw TypeUI files in `.design-brain/typeui-skills/raw/*`
- Extracted TypeUI JSON in `.design-brain/typeui-skills/extracted/*`
- Private reflection history, unless `--include-history` is provided
- Reference insight journal history, template build journal history, and naming ledger history, unless `--include-history` is provided
- Claude Code activation files in `.claude-plugin/`, `skills/`, and `hooks/`, which activate Brain Design only when this package itself is loaded as a plugin
- Generated web deck render reviews in `.design-brain/evidence/web-deck-reviews/*`

## AGENTS.md Merge Behavior

If target `AGENTS.md` does not exist, the installer creates it with a marked Design Brain section.

If target `AGENTS.md` exists, the installer appends:

```html
<!-- CODEX_DESIGN_BRAIN_START -->
...
<!-- CODEX_DESIGN_BRAIN_END -->
```

If the marked section already exists and already matches the installer, it is skipped. If the marked section exists but differs, run with `--force` to update only that section. Content outside the markers is preserved.

## Write Boundaries

- Dry-run first when installing into an important project.
- Existing target files are skipped unless `--force` is provided.
- `--force` overwrites only Design Brain-managed files.
- `--force` creates `.bak-YYYYMMDD-HHMMSS` snapshots before overwriting.
- The installer never overwrites files outside Design Brain-managed paths.
- The installer does not change `DESIGN_PREFERENCES.json` values.
- The installer does not auto-promote memory.

## Verify Install

After installing, run the status checker against the target root:

```bash
python scripts/design_brain_status.py --root "<YOUR_PROJECT_PATH>"
```

## After Installation: Run A Pilot

For the first substantial UI task in a target project, create a pilot report before editing:

```bash
python scripts/design_brain_pilot.py --project-root "<YOUR_PROJECT_PATH>" --task "Improve homepage hero section" --target "src/app/page.tsx" --url "http://localhost:3000" --notes "Focus on hierarchy, CTA clarity, and marketplace-ready visual quality"
```

Use the pilot report to plan project inspection, screenshots, review reports, visual review reports, revision, and controlled reflection.

If the script is run from inside the installed target project, default output goes to that target project's `.design-brain/pilots/`. If the source Design Brain script is used to inspect another project, use `--output` when you want the report saved in that other project.

## After Installation: Plan Template Products

For marketplace-ready template product work, create an orchestration report before designing:

```bash
python scripts/design_brain_template_orchestrate.py --template-type "SaaS landing page template" --niche "AI automation" --target-buyer "Startup founders and SaaS marketers" --visual-mood "Premium, clean, confident" --preview-type "marketplace cover and responsive section breakdown"
```

The orchestrator coordinates product diagnosis, style routing, structure planning, editable requirements, preview direction, quality gate, and follow-up review commands.

For a narrower plan-only report, use:

```bash
python scripts/design_brain_template_plan.py --template-type "SaaS landing page template" --niche "AI automation" --target-buyer "Startup founders and SaaS marketers" --visual-mood "Premium, clean, confident"
```

The planner uses the Template Product Intelligence files to identify section structure, editable areas, style packs, preview direction, marketplace quality criteria, and risks of generic output. It does not change `DESIGN_MEMORY.md` or `DESIGN_PREFERENCES.json`.

To intentionally copy raw and extracted TypeUI skill references into another project, use `--include-history`. Without it, the installer creates empty `.design-brain/typeui-skills/raw/` and `.design-brain/typeui-skills/extracted/` folders.

## Reference Insight And Naming Memory

New installations receive clean reference, build, and naming journals by default:

- `.design-brain/REFERENCE_INSIGHT_JOURNAL.md`
- `.design-brain/TEMPLATE_BUILD_JOURNAL.md`
- `.design-brain/TEMPLATE_NAMING_LEDGER.md`

Generated files in `.design-brain/reference-insights/` are not copied by default. Use `--include-history` only when intentionally carrying project/product learning history into another repository.
