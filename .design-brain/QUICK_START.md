# Codex Design Brain Quick Start

Codex Design Brain is a local, controlled orchestration layer for better UI and visual design work in Codex App or Codex CLI workflows. It does not retrain the model. It gives Codex a repeatable way to read design preferences, critique work, revise output, save useful feedback, and propose stable memory updates only after review.

## What Each Part Does

- `AGENTS.md`: repo-level operating instructions for Codex.
- `DESIGN_MEMORY.md`: stable long-term design taste and reusable design rules.
- `DESIGNER_COGNITION_LAYER.md`: evidence-backed reference reasoning for buyer decision model, attention, emotion, trust, density, conversion, component reasoning, and batch pattern memory.
- `SOURCE_OF_TRUTH_MAP.md`: rule hierarchy when README, routing docs, scripts, learning logs, or workflow files conflict.
- `ROUTING_ALIASES_ID.json`: Indonesian and mixed-language aliases for routing and product-family classification.
- `WEBSITE_TEMPLATE_REFERENCE_CORPUS.md`: local `Template Website` preview-image corpus rules for product-type-specific website reference selection.
- `REFERENCE_CORPUS_CONFIG.md`: fallback paths and no-silent-fail rules for local reference corpus handling.
- `TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`: source-template image policy; use text clue placeholders such as `image placeholder` and `profile photo placeholder` instead of unrequested generated imagery.
- `FIGMA_OUTPUT_TARGET.md`: Figma destination guidance; never create files with placeholder project IDs.
- `FIGMA_REFERENCE_DEEP_STUDY.md`: deep-study rule for Figma reference links and template sources; inspect page/frame/component/state scheme and infer product standard before planning.
- `FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md`: professional Figma template reading order; study product purpose, visual direction, section structure, grid, typography, color roles, image direction, component style, spacing rhythm, content logic, responsive behavior, and Figma hygiene before building.
- `FIGMA_REFERENCE_LEARNING_CORPUS.md`: user-provided Figma material links used as learning references, not shared scaffolds.
- `CONTINUOUS_DESIGNER_LEARNING_LOOP.md`: post-build and reference-study learning loop; generate new questions, research evidence, distill designer schema, and apply the next rule instead of stopping at the first output.
- `FIGMA_AUTO_LAYOUT_ENFORCEMENT.md`: mandatory auto-layout rule for editable Figma template source structure.
- `DESIGN_PREFERENCES.json`: structured preference weights for consistent design direction.
- `TEMPLATE_PRODUCT_MEMORY.md`: marketplace-specific rules for sellable, editable template products.
- `TEMPLATE_TAXONOMY.md`: template product categories, buyer contexts, and marketplace categories.
- `TEMPLATE_STRUCTURE_RULES.md`: required sections, screens, components, states, and editable areas by template type.
- `MARKETPLACE_QUALITY_GATE.md`: scoring gate for commercial template readiness.
- `QUALITY_GATE_FAILURE_TAXONOMY.md`: root-cause categories for failed gates and required action type.
- `PREVIEW_PRESENTATION_SYSTEM.md`: cover, preview, section breakdown, responsive preview, and mockup rules.
- `STYLE_PACKS.json`: structured style packs for template planning.
- `VISUAL_CRITIQUE_CHECKLIST.md`: 1-10 scoring rubric for UI and visual critique.
- `PATTERN_LIBRARY.md`: reusable patterns for heroes, pricing, dashboards, previews, marketplace layouts, and design overviews.
- `reviews/`: generated design review reports for specific tasks.
- `pilots/`: real project pilot reports for first-run project workflows.
- `screenshots/`: screenshots used as visual evidence.
- `visual-reviews/`: generated visual review reports based on screenshots or rendered UI evidence.
- `REFLECTION_LOG.md`: controlled feedback history and reusable lessons.
- `promotion-proposals/`: proposal reports for deciding whether repeated lessons should be promoted to stable memory.
- `proposed-rules/`: proposed rule changes created by learning loops before active promotion.
- `scripts/`: local command utilities for status, review, reflection, and promotion proposal workflows.
- `.agents/skills/design-critic/SKILL.md`: instruction-only local skill that guides critique and revision.

## Normal Workflow

1. Start a UI, frontend, landing page, dashboard, component, preview, marketplace template, or Figma-like layout task.
2. Read the Design Brain files: memory, preferences, checklist, and relevant patterns.
3. Build the first draft.
4. Run a review report for substantial work.
5. Critique the design using the report and checklist.
6. Revise concrete weak areas.
7. Save useful user feedback as a reflection lesson.
8. Promote repeated patterns only after review and explicit approval.

## Natural Intent Autopilot

The user does not need to remember command names. Codex should infer the workflow from natural language.

Natural request examples:

- "ini referensi, buat template baru" -> reference insight, originality guard, template product workflow.
- "buat 5 template tapi jangan mirip" -> Designer Cognition Layer plus Sequential Reference-Led Batch Workflow: learn evidence-backed designer logic, build one template, lock its pattern memory, then repeat.
- "kasih nama yang beda dari sebelumnya" -> naming ledger and name check.
- "ambil insight dari referensi ini" -> reference insight system and do-not-copy notes.
- "pelajari link Figma ini sebagai referensi template" -> Figma Reference Deep Study, reference schema receipt, product-family standard inference, and originality guard.
- "lanjut pelajari sampai paham pola pikir designer" -> Continuous Designer Learning Loop, Designer Cognition Layer, reference insight, and web-evidence study when the question affects quality.
- "buat preview cover untuk marketplace" -> template orchestration and marketplace preview direction.
- "ini terlalu mirip struktur sebelumnya" -> design critic, originality guard, and sequential pattern-lock similarity reasoning.
- "buat aku design template di figma" -> load Figma Output Target, verify the target is configured, create a new design file only when valid, then run website-template product workflow.

Use the intent router only as an internal helper when routing is complex:

```bash
python scripts/design_brain_intent_route.py --task "buat batch template marketplace, jangan copy layout referensi" --has-reference --template-count 5 --dry-run
```

Respond naturally first; keep command details optional.

## v2.1.0 Smoke Tests

Use these when changing routing, taxonomy, Figma target rules, or reference corpus behavior:

```bash
python scripts/design_brain_router_smoke_test.py
python scripts/design_brain_module_select.py --task "dashboard POS template" --dry-run
python scripts/design_brain_module_select.py --task "template website restoran" --dry-run
python scripts/design_brain_website_reference_select.py --task "template website restoran" --dry-run
```

## Continuous Designer Learning Workflow

Use this workflow when the user asks to keep learning, learn previous material more deeply, create new questions, search the web for answers, or improve Brain Design toward professional designer thinking.

1. Start from the latest build, reference, critique, or missed pattern.
2. Identify the lesson and the weakest uncertainty.
3. Turn the uncertainty into a focused question.
4. Search credible web evidence when it affects marketplace quality, Figma source quality, responsiveness, accessibility, ecommerce behavior, or design-system behavior.
5. Distill the answer into designer schema: buyer effect, section logic, visual rhythm, source-file logic, marketplace value, and originality boundary.
6. Write proposed rules first unless the user explicitly asks for active workflow changes or repeated/evidence-backed feedback justifies promotion.

## Sequential Reference-Led Batch Workflow

Use this workflow for every multiple-template request.

Do not make one global batch plan and then create variants. Build one template at a time:

1. Select the next active product-purpose reference group for the current template only. Use up to 10 varied references when enough matching candidates exist.
2. For website templates, classify product family and select local references from `Template Website` before reasoning from visuals.
3. Infer buyer decision model, designer intent, attention strategy, emotional rhythm, trust strategy, density strategy, conversion logic, component reasoning, and marketplace role.
4. Define what abstract thinking logic can be reused and what recognizable execution must not be copied.
5. Build one complete standard/full template.
6. Lock the used opening strategy, hero grammar, trust strategy, density rhythm, component system, CTA logic, visual motif, storytelling arc, and reference group.
7. Restart from step 1 for the next template.

Internal helper:

```bash
python scripts/design_brain_sequential_batch.py --task "buat 4 website template yang beda total" --count 4 --reference-root "Template Website" --dry-run
```

For website-template reference selection by product type:

```bash
python scripts/design_brain_website_reference_select.py --task "buat website template SaaS AI" --template-type "website template" --niche "AI SaaS" --dry-run
python scripts/design_brain_reference_corpus_health.py
```

This is the active batch behavior. Existing template plan, orchestration, reference insight, originality, review, and visual review scripts still exist, but they should be applied inside each template cycle.

## Source-of-Truth Context Packets

Create a context packet when a task involves references, template products, naming, marketplace previews, or critique.

### Reference-Based Template Task

```bash
python scripts/design_brain_context_packet.py --task "Create a marketplace-ready wedding planning landing page template from a visual reference without copying it" --reference --template-type "landing-page" --niche "wedding-planning" --naming --dry-run
```

### Naming Task

```bash
python scripts/design_brain_context_packet.py --task "Choose an original name for a wedding planning landing page template" --template-type "landing-page" --niche "wedding-planning" --naming --dry-run
```

### Critique / Review Task

```bash
python scripts/design_brain_context_packet.py --task "Review a marketplace preview cover inspired by a reference" --reference --review --template-type "marketplace-preview cover" --niche "template product showcase"
```

## Template Product Workflow

Use this workflow before designing marketplace-ready template products such as landing page templates, Figma website templates, dashboards, SaaS templates, UI kits, design systems, branding kits, covers, preview layouts, section breakdowns, perspective mockups, and responsive overviews.

```bash
python scripts/design_brain_template_plan.py --template-type "SaaS landing page template" --niche "AI automation" --target-buyer "Startup founders and SaaS marketers" --visual-mood "Premium, clean, confident"
python scripts/design_brain_typeui_ingest.py
python scripts/design_brain_style_select.py --template-type "SaaS landing page template" --niche "AI automation" --target-buyer "Startup founders and SaaS marketers" --visual-mood "Premium, clean, confident"
```

To save a named plan:

```bash
python scripts/design_brain_template_plan.py --template-type "Dashboard template" --niche "Analytics" --target-buyer "B2B SaaS teams" --visual-mood "Enterprise, spacious, polished" --output ".design-brain/template-plans/analytics-dashboard-plan.md"
```

Before designing, identify the template type, niche, target buyer, marketplace category, required sections/components, style pack, editable areas, preview direction, marketplace quality criteria, and anti-generic risks.

TypeUI-derived skills should be selected, not merged all at once. Use `design_brain_style_select.py` to pick the relevant pack and translate it into constraints.

## Template Product Orchestrator

Use the orchestrator as the recommended entry point for sellable template products. It combines product diagnosis, style routing, structure planning, editability requirements, preview direction, quality gate, and next review commands in one report.

For multiple-template work, run or follow the orchestrator inside each sequential cycle. Do not create one orchestration report and reuse it as the scaffold for every template in the batch.

### Orchestrator Dry Run

```bash
python scripts/design_brain_template_orchestrate.py --template-name "Vowcraft Atelier" --template-type "landing-page" --niche "wedding-planning" --target-buyer "wedding planners and event studios" --visual-mood "elegant premium editorial" --marketplace "Envato Elements / Figma template marketplace" --preview-type "section breakdown overview and perspective mockup" --notes "Plan a marketplace-ready editable wedding planning landing page template" --dry-run
```

### Orchestrator Save Report

```bash
python scripts/design_brain_template_orchestrate.py --template-name "FixPilot Home Care" --template-type "landing-page" --niche "home repair booking service" --target-buyer "home repair companies, handyman services, and maintenance businesses" --visual-mood "professional clean trustworthy" --marketplace "Envato Elements / Figma template marketplace" --preview-type "section breakdown overview and responsive preview" --notes "Plan a marketplace-ready editable home repair landing page template"
```

### Next Review Command

```bash
python scripts/design_brain_review.py --task "FixPilot Home Care" --target "TARGET_FILE_OR_SCREEN" --notes "Use the orchestration report to critique template structure, style fit, editability, preview strength, and marketplace readiness"
```

### Next Visual Review Command

```bash
python scripts/design_brain_visual_review.py --task "FixPilot Home Care" --target "TARGET_FILE_OR_SCREEN" --screenshot ".design-brain/screenshots/fixpilot-home-care-preview.png" --notes "Inspect visual evidence, then review hierarchy, spacing, CTA clarity, responsive preview, and marketplace quality"
```

### Next Reflection Command

```bash
python scripts/design_brain_reflect.py --task "FixPilot Home Care" --feedback "USER_FEEDBACK" --went-wrong "WHAT_WENT_WRONG" --lesson "REUSABLE_TEMPLATE_DESIGN_LESSON" --rule "RULE_TO_REUSE_NEXT_TIME"
```

## Real Project Pilot

Use a pilot report before the first substantial UI task in a real project.

```bash
python scripts/install_design_brain.py --target "<YOUR_PROJECT_PATH>" --dry-run
python scripts/install_design_brain.py --target "<YOUR_PROJECT_PATH>"
python scripts/design_brain_status.py --root "<YOUR_PROJECT_PATH>"
python scripts/design_brain_pilot.py --project-root "<YOUR_PROJECT_PATH>" --task "Improve homepage hero section" --target "src/app/page.tsx" --url "http://localhost:3000" --notes "Focus on hierarchy, CTA clarity, and marketplace-ready visual quality"
python scripts/design_brain_review.py --task "Improve homepage hero section" --target "src/app/page.tsx" --notes "Use the pilot report and critique hierarchy, spacing, CTA clarity, responsiveness, and marketplace quality"
python scripts/design_brain_visual_review.py --task "Improve homepage hero section" --target "src/app/page.tsx" --url "http://localhost:3000" --notes "Inspect rendered output separately, then fill the visual report"
python scripts/design_brain_reflect.py --task "Improve homepage hero section" --feedback "USER_FEEDBACK" --went-wrong "WHAT_WENT_WRONG" --lesson "REUSABLE_LESSON" --rule "RULE_TO_REUSE"
```

## Command Recipes

### Status

```bash
python scripts/design_brain_status.py
python scripts/design_brain_status.py --json
python scripts/design_brain_status.py --root "<YOUR_PROJECT_PATH>"
```

### Real Project Pilot

```bash
python scripts/design_brain_pilot.py --project-root "<YOUR_PROJECT_PATH>" --task "Improve homepage hero section" --target "src/app/page.tsx" --url "http://localhost:3000" --notes "Focus on hierarchy, CTA clarity, and marketplace-ready visual quality"
python scripts/design_brain_pilot.py --project-root "<YOUR_PROJECT_PATH>" --task "Improve homepage hero" --target "src/app/page.tsx" --url "http://localhost:3000" --output "<YOUR_PROJECT_PATH>/.design-brain/pilots/homepage-hero-pilot.md"
```

### Install Into Project

```bash
python scripts/install_design_brain.py --target "<YOUR_PROJECT_PATH>" --dry-run
python scripts/install_design_brain.py --target "<YOUR_PROJECT_PATH>"
```

### Review

```bash
python scripts/design_brain_review.py --task "Landing page hero redesign" --target "src/app/page.tsx" --notes "Focus on hierarchy, CTA clarity, and marketplace-ready quality"
```

### Template Product Plan

```bash
python scripts/design_brain_template_plan.py --template-type "Figma website template" --niche "Creative agency" --target-buyer "Freelance designers and small studios" --visual-mood "Editorial, premium, modern"
```

### Template Product Orchestration

```bash
python scripts/design_brain_template_orchestrate.py --template-type "Figma website template" --niche "Creative agency" --target-buyer "Freelance designers and small studios" --visual-mood "Editorial, premium, modern" --preview-type "marketplace cover and responsive section breakdown"
```

### Template Style Selection

```bash
python scripts/design_brain_typeui_ingest.py
python scripts/design_brain_style_select.py --template-type "landing-page" --niche "wedding-planning" --visual-mood "elegant premium editorial" --target-buyer "wedding planners and event studios"
```

### Visual Review From Screenshot

```bash
python scripts/design_brain_visual_review.py --task "Homepage visual review" --target "src/app/page.tsx" --screenshot ".design-brain/screenshots/homepage-desktop.png" --notes "Check hero hierarchy, spacing, CTA clarity, and marketplace feel"
```

### Visual Review From URL Reference

```bash
python scripts/design_brain_visual_review.py --task "Homepage URL visual review" --target "src/app/page.tsx" --url "http://localhost:3000" --notes "Inspect the rendered page separately, then fill this report"
```

### Manual Before/After Screenshot Comparison

```bash
python scripts/design_brain_visual_review.py --task "Pricing before/after comparison" --target "src/app/pricing.tsx" --screenshot ".design-brain/screenshots/pricing-section-after.png" --notes "Compare against pricing-section-before.png manually and record changes"
```

### Reflect Dry Run

```bash
python scripts/design_brain_reflect.py --task "Landing page hero redesign" --feedback "The hero feels too crowded and generic" --went-wrong "Too many competing visual elements and weak spacing hierarchy" --lesson "Premium landing pages need one dominant focal point and more intentional whitespace" --rule "For hero sections, prioritize one clear focal point, one primary CTA, and spacious composition." --dry-run
```

### Reflect Append

```bash
python scripts/design_brain_reflect.py --task "Landing page hero redesign" --feedback "The hero feels too crowded and generic" --went-wrong "Too many competing visual elements and weak spacing hierarchy" --lesson "Premium landing pages need one dominant focal point and more intentional whitespace" --rule "For hero sections, prioritize one clear focal point, one primary CTA, and spacious composition."
```

### Promotion Proposal Dry Run

```bash
python scripts/design_brain_promote.py --min-count 2 --dry-run
```

### Promotion Proposal Save

```bash
python scripts/design_brain_promote.py --min-count 2
```

## Template Files

- `.design-brain/templates/DESIGN_TASK_BRIEF.md`: fill before starting a substantial design task.
- `.design-brain/templates/TEMPLATE_PRODUCT_BRIEF.md`: fill before designing a marketplace-ready template product.
- `.design-brain/templates/TEMPLATE_ORCHESTRATION_REPORT.md`: fill or compare against generated orchestration reports for sellable template products.
- `.design-brain/templates/DESIGN_CONTEXT_PACKET.md`: summarize source-of-truth files and workflows to load for a specific task.
- `.design-brain/templates/SEQUENTIAL_REFERENCE_BATCH_CYCLE.md`: structure one reference-led cycle for one template inside a batch.
- `.design-brain/templates/DESIGNER_LEARNING_CYCLE.md`: structure one question-led learning cycle after a build, reference study, or critique.
- `.design-brain/templates/REAL_PROJECT_PILOT_BRIEF.md`: fill before piloting Design Brain in a real project.
- `.design-brain/templates/PILOT_RESULT_REPORT.md`: summarize what happened after a pilot task.
- `.design-brain/templates/USER_FEEDBACK_TO_REFLECTION.md`: convert feedback into a reflection command.
- `.design-brain/templates/MEMORY_PROMOTION_REQUEST.md`: request explicit approval before promoting repeated lessons into stable memory.

## Install Into Another Project

Preview installation first:

```bash
python scripts/install_design_brain.py --target "<YOUR_PROJECT_PATH>" --dry-run
```

Install after reviewing the dry-run:

```bash
python scripts/install_design_brain.py --target "<YOUR_PROJECT_PATH>"
```

Verify the target project:

```bash
python scripts/design_brain_status.py --root "<YOUR_PROJECT_PATH>"
```

Generated reports, screenshots, and private reflection history are not copied by default.

## Design Brain v2.0.0 Presentation Workflow

For professional presentation-template work:

1. Resolve buyer, marketplace, output format, reference role, no-copy boundary, asset rules, and scoring priority.
2. Define the design system before slide planning.
3. Select slide archetypes from buyer and use case.
4. Validate editability: placeholders, text, shapes, theme colors, theme fonts, masters/layouts, and export behavior.
5. Run Chromium visual QA when renderable and save evidence to `.design-brain/evidence/visual-reviews/`.
6. For PPTX, run native PPTX checks; screenshots alone are not enough.
7. Apply the generic detector hard gate before final delivery.

## Website Template Structure Workflow

For website template work:

1. Classify scope before visual style: hero/header kit, landing page, full website, ecommerce, dashboard/admin, portfolio, blog/editorial, or service site.
2. Use structure-count standards from `.design-brain/seed-packs/website-template/` or `.design-brain/seed-packs/hero-header-kit/`.
3. Do not use a restrained mood as a reason to reduce required sections, pages, states, or buyer-journey steps.
4. For full websites, define both homepage block map and inner page map.
5. For landing pages, include enough proof, detail, objection handling, conversion closure, and footer trust for the specific goal.
6. For ecommerce and dashboard/admin products, include transactional or operational screens and states.

## FIG Template Corpus Workflow

For local `.fig` template study:

```bash
npm run fig:extract -- --source "Template Website"
```

Use `.design-brain/evidence/fig-extracts/latest.json` to find the newest run.
Each run stores raw sources, ZIP contents, `canvas.fig`, decoded node summaries,
layer names, text content, and structure notes.

Rules:

1. Treat decoded `.fig` files as product-structure evidence, not copyable layouts.
2. Use frame hierarchy, layer names, and text content to infer buyer journey and template scope.
3. Keep evidence in `.design-brain/evidence/fig-extracts/`; do not promote it into stable memory automatically.
