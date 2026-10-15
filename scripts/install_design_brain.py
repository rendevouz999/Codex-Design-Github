#!/usr/bin/env python
"""Install Codex Design Brain into another repository.

The installer copies only Design Brain-managed files, avoids generated reports
by default, and never overwrites existing target files unless --force is used.
When --force overwrites a managed file, it creates a timestamped snapshot first.

The Claude Code activation layer (`.claude-plugin/plugin.json`,
`.claude-plugin/marketplace.json`, `hooks/`) is intentionally not
managed and is never installed, even though it ships inside the public-core ZIP.
Those files only activate the package that owns them: plugin.json declares its own
root as the plugin source, and `hooks/hooks.json` expands CLAUDE_PLUGIN_ROOT only for
the plugin that loaded it. Copying them into a target repository would register a
duplicate plugin owned by an unrelated repo and leave a root `skills/` folder that
nothing scans. A target repository activates Brain Design by loading the Design Brain
package itself as a plugin, not by installing these files. The knowledge, craft,
seed-pack, and tooling layers below are installed normally, so every installed
workflow keeps working without the activation layer. The internal presentation
capability is installed under skills/presentation-deck as a required runtime and
knowledge resource; this does not register another plugin.
"""

from __future__ import annotations

import argparse
import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


START_MARKER = "<!-- CODEX_DESIGN_BRAIN_START -->"
END_MARKER = "<!-- CODEX_DESIGN_BRAIN_END -->"

DEFAULT_AGENTS_SECTION = """# Codex Design Brain

For visual inspection during plugin work, load `.design-brain/VISUAL_INSPECTION_PROTOCOL.md`. Main and the single Engineer use current-source overview, targeted full-resolution crops, and a return to whole-frame context. Record actual observations and unresolved checks; generated images, metadata, screenshot presence and another agent's verdict alone cannot establish visual PASS.

This repository contains the Codex Design Brain: a local orchestration layer for better UI and visual design work in Codex App or Codex CLI style workflows. It does not retrain or modify the Codex model. It gives Codex persistent repo-local design memory, preference weights, critique rules, reusable patterns, and a reflection log.

## Source-of-Truth Design Brain

For any template, reference-based, naming, marketplace preview, or design critique task, Codex must treat `.design-brain/` as its external design cognition layer.

Before working, Codex should follow `.design-brain/AUTOLOAD_POLICY.md`.

When rules overlap, resolve them through `.design-brain/SOURCE_OF_TRUTH_MAP.md`. README files and quick-start notes are documentation; active routing, autoload, owner, taxonomy, batch, and quality-gate files own the workflow behavior.

Core identity files:

- `DESIGN_SOUL.md`
- `DESIGN_IDENTITY.md`
- `USER_DESIGN_CONTEXT.md`
- `DESIGN_PRINCIPLES.md`
- `DESIGN_OPERATING_RULES.md`
- `CONTEXT_PRIORITY.md`

Codex must use these files to understand who it is, how it thinks, how the user works, and which memory, journal, or workflow should be loaded.

## Required Design Workflow

For any UI, frontend, landing page, dashboard, design system, component, preview layout, marketplace template, mockup, or Figma-like layout task, Codex must use the design-critic workflow in `.agents/skills/design-critic/SKILL.md`.

Before implementing or reviewing design work:

1. Read `.design-brain/DESIGN_MEMORY.md`.
2. Read `.design-brain/DESIGN_PREFERENCES.json`.
3. Check `.design-brain/PATTERN_LIBRARY.md` for relevant reusable patterns.
4. Use `.design-brain/VISUAL_CRITIQUE_CHECKLIST.md` as the review gate.

Codex must not finish UI work after the first implementation. It must complete at least one self-critique pass, identify weak areas, and make concrete improvements after critique. Keep outputs practical, production-ready, and suitable for real implementation or marketplace presentation.

## Review Reports

For substantial UI or design tasks, create a structured review report before the final response:

```bash
python scripts/design_brain_review.py --task "..." --target "..." --notes "..."
```

Save generated reports in `.design-brain/reviews/` unless a specific output path is needed. The report is a template for Codex to fill after inspecting the target; it is not automatic visual analysis. Use the report to score the design, identify weak areas, apply concrete revisions, and capture reflection lessons when user feedback exists.

## Controlled Self-Improvement

When the user gives useful design feedback, Codex should convert it into a reusable lesson and append it to `.design-brain/REFLECTION_LOG.md` with:

```bash
python scripts/design_brain_reflect.py --task "..." --feedback "..." --went-wrong "..." --lesson "..." --rule "..."
```

This is controlled self-improvement, not automatic model training. Do not automatically change `.design-brain/DESIGN_MEMORY.md`, `.design-brain/DESIGN_PREFERENCES.json`, or preference weights from a single feedback item. Only promote repeated lessons into `DESIGN_MEMORY.md` after multiple similar feedback patterns or explicit user instruction.

## Memory Promotion

`REFLECTION_LOG.md` is feedback history. `DESIGN_MEMORY.md` is stable long-term design taste. Codex may run a promotion proposal report to review repeated reflection patterns:

```bash
python scripts/design_brain_promote.py --min-count 2
```

Codex must not promote lessons into `DESIGN_MEMORY.md` without explicit user instruction. Repeated feedback patterns can become stable memory only after review and approval. Do not use promotion proposals to change `.design-brain/DESIGN_PREFERENCES.json` or preference weights.

## Operational Workflow

Run `python scripts/design_brain_status.py` when unsure about system health or the next safe action. For substantial UI/design tasks, use `.design-brain/QUICK_START.md` and the templates in `.design-brain/templates/`. Keep the review, reflection, and promotion workflow controlled: create review reports, capture useful feedback as reflection, and never auto-promote lessons into stable memory.

## Natural Intent Autopilot

Codex must not require the user to mention internal Design Brain commands.

For design/template/reference/batch/naming/review tasks, Codex should infer intent from natural language and follow the relevant Design Brain workflow automatically.

If the user provides references, activate reference insight and originality guard.
If the user provides a Figma reference link, Figma frame, Figma template file, or `.fig` source, activate `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md` and `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md` before structure planning. Study the product purpose, visual direction, section structure, grid/layout system, typography hierarchy, color-role system, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, Figma source hygiene, page/frame/component/state scheme, product-family standard, and do-not-copy boundary. Produce a Figma reference schema receipt and never use minimalist as the fallback for unknown structure standard.
If the user asks for multiple templates, activate Batch Template Hard Gates plus Sequential Reference-Led Batch Workflow, per-cycle reference study, pattern locking, root-cause similarity diagnosis, scaffold disposal, and similarity guard.
If the user asks for multiple website/Figma/source templates, activate the Serial Provenance Gate. Do not build multiple final templates or multiple final design-system boards from one app builder, one Figma script, one page schema, or one batch data object. Template 2 may start only after Template 1 is complete, repaired, audited, fingerprint locked, and scaffold-disposed; repeat for every later template.
If the user asks for naming, check naming ledger.
If the user asks for marketplace-ready template products, run or follow template orchestration.
If the user provides references or asks for batch templates, activate `.design-brain/DESIGNER_COGNITION_LAYER.md` before structure planning. Codex must infer the designer's attention, emotion, trust, density, proof, and conversion decisions before deciding sections or components.
If the user asks for website templates, activate `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md` and use the configured local reference corpus, such as `<LOCAL_REFERENCE_CORPUS>/Template Website`, by product type.
If the user asks for a new reference-led template or a template brand/name, activate `.design-brain/TEMPLATE_REFERENCE_USAGE_POLICY.md`, `.design-brain/TEMPLATE_REFERENCE_USAGE_REGISTRY.json`, and `scripts/design_brain_reference_usage_gate.py` before Style DNA extraction. Do not reuse generated output brand names, reference brand names, or too-similar name token/prefix/suffix patterns. For website template references, the local selector owns product-purpose group rotation: use up to 10 eligible varied references per active group when enough matches exist, rotate to the next group for the next same-product build, and reset only after the final group is reached.
If the user asks to learn from the provided Figma material links or asks for professional designer schema learning, activate `.design-brain/FIGMA_REFERENCE_LEARNING_CORPUS.md` and use it as study material, not as a shared scaffold.
If the user asks to keep learning after a build, learn previous material more deeply, create new questions, answer via web search, or improve Brain Design toward a professional designer mindset, activate `.design-brain/CONTINUOUS_DESIGNER_LEARNING_LOOP.md`. Treat the latest build/reference/critique as evidence, generate focused questions, search credible web/category evidence when needed, distill designer schema, and update workflow files when protected-change permission is satisfied.
If the user asks for website, web-template, Figma website-template, or standard landing-page template work, competitive standard starts at 8 meaningful sections/blocks. Do not use minimalist, safe, simple, fallback, clean, restrained, or basic as a reason for fewer than 8 sections. Under-8 structure is allowed only when the user explicitly asks for a hero/header kit, micro landing page, narrow campaign, squeeze page, waitlist page, or another intentionally small product.
If the user asks for editable templates, source templates, Figma templates, website templates, or marketplace templates, activate `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`. Unless the user explicitly asks for generated images, image zones must be text clue placeholders such as `image placeholder: [purpose]`; human/profile image zones must use `profile photo placeholder: [role]`. Do not force generated imagery.
If the user asks for a Figma template, editable Figma source template, create new design, or website-template design in this workspace, activate `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md`, `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`, `.design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md`, and `.design-brain/VISUAL_CRITIQUE_CHECKLIST.md`. Real auto-layout plus source-template receipts are mandatory for editable structure.

Internal scripts are tools, not user-facing rituals.

## Sequential Reference-Led Batch Workflow

For any multiple-template or batch design task, Codex must work one template at a time.

Before batch work, load `.design-brain/BATCH_TEMPLATE_HARD_GATES.md`. Use it to decide whether a similarity problem requires structural rebuild, section recomposition, effect redesign, recolor, or copy rewrite.

Do not study all references globally and then generate multiple variants from one shared structure. Do not create one master scaffold for the whole batch.

Quality outranks output count. Codex must not present batch output just because all requested templates exist; each template must be product-complete, visually reviewed when possible, and pairwise-audited against accepted prior templates. If slower work is required for quality, work slower.

Each output should be closer to its own selected reference insight than to any previous Codex-built output. If a new template feels like a variant of an earlier template, stop and rebuild its structure plan.

Treat every page-level scaffold as single-use. Once a template is accepted, permanently remove that scaffold from active working context before the next template: do not reread, copy, mutate, or data-swap its page schema, Figma script outline, section map, card cadence, or design-system panel order. If a temporary scaffold file or scratch builder was created only for that template, delete it after recording the negative pattern lock.

For multi-template website/Figma/source work, post-build READY is blocked unless serial provenance proves each template was completed, audited, locked, and scaffold-disposed before the next template began. Same-line-count receipt/fingerprint generation or one multi-template Figma builder is hard evidence of a shared scaffold and must fail.

## Figma Auto-Layout Enforcement

For Figma template/source work, Codex must build editable sections, nav, cards, CTAs, forms, repeated rows, dashboards, responsive previews, and design-system panels with real Figma auto-layout. Use manual x/y positioning only for documented decorative backgrounds, ambient glows, intentional overlays, mockup callouts, or preview-only effects. Include an auto-layout receipt before calling the Figma template complete.

For each requested template:

1. Select one active reference group from the available corpus, such as `Template Website`, for this template only. When enough product-purpose matches exist, the group should contain up to 10 varied references.
2. Use `.design-brain/DESIGNER_COGNITION_LAYER.md` to identify buyer decision model, evidence-backed designer intent, attention strategy, emotional rhythm, trust strategy, density strategy, and conversion logic.
2a. When a Figma reference or template source is used, use `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md`, `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md`, and complete a reference schema receipt before section planning.
3. For website templates, classify product family and select product-type-matched references from `Template Website`; rotate same-product reference groups instead of reusing group 1 for every build.
4. Convert reference imagery into role-specific text clue placeholders for source-template image zones unless image generation was explicitly requested.
5. Study the references and infer their purpose, target buyer, end audience, structure, visual design logic, and marketplace role.
6. Define reusable abstract thinking logic and the recognizable execution details that must not be copied.
7. Build one complete standard/full template from the new insight.
8. Lock the used opening strategy, hero grammar, trust strategy, density rhythm, component system, CTA logic, visual motif, storytelling arc, and reference group.
9. Delete the spent scaffold from active working context and record a disposal receipt before planning the next template.
10. Audit the next template against all accepted earlier fingerprints and diagnose the root cause: structure, composition, effects, color-only, or copy/naming-only.
11. If structure reaches 10 percent similarity, rebuild the newer template before continuing. If only color is similar, recolor. If only copy/naming repeats, rewrite copy/naming.
12. Start the next template from the next active product-purpose reference group, avoiding at least 90 percent of the previous cycle's recognizable execution pattern.

Use `.design-brain/BATCH_TEMPLATE_HARD_GATES.md`, `.design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md`, and `.design-brain/templates/SEQUENTIAL_REFERENCE_BATCH_CYCLE.md`. Use `scripts/design_brain_sequential_batch.py` as an internal helper when useful.

This is the active batch behavior. Existing scripts remain available, but template orchestration, reference insight, originality checks, review, and visual review should happen inside each cycle.

## Visual Review Workflow

For substantial UI/frontend work, Codex should inspect rendered output when possible. Save screenshots into `.design-brain/screenshots/`, then generate a visual review report:

```bash
python scripts/design_brain_visual_review.py --task "..." --target "..." --screenshot ".design-brain/screenshots/..." --notes "..."
```

Use visual evidence to revise UI, especially hierarchy, spacing, typography, CTA clarity, contrast, responsiveness, and marketplace presentation quality. Do not rely only on code when visual quality matters. Do not claim visual inspection happened unless Codex actually inspected a screenshot, browser view, or rendered output.

## Real Project Pilot Workflow

Before substantial UI work in a real project, create or follow a pilot brief using `.design-brain/PILOT_WORKFLOW.md` and `.design-brain/templates/REAL_PROJECT_PILOT_BRIEF.md`. Verify Design Brain status in the project before relying on the workflow:

```bash
python scripts/design_brain_status.py --root "PROJECT_ROOT"
```

For the first task in a new project, generate a pilot report:

```bash
python scripts/design_brain_pilot.py --project-root "PROJECT_ROOT" --task "..." --target "..." --notes "..."
```

Use review and visual review reports before finalizing UI. Capture useful user feedback with controlled reflection. Never claim visual inspection happened without actual screenshot, browser, or rendered-output evidence.

## Template Product Design Workflow

For any template product task, Codex must run or follow the Template Product Intelligence workflow before designing. This applies to website landing page templates, Figma website templates, dashboard templates, SaaS templates, UI kits, design system templates, branding kit templates, marketplace preview layouts, cover layouts, section breakdowns, perspective mockup overviews, and responsive preview layouts.

Before designing, identify the template type, niche, target buyer, marketplace category, required section/component structure, style pack, preview direction, editability requirements, and marketplace quality criteria. Use:

```bash
python scripts/design_brain_template_plan.py --template-type "..." --niche "..." --target-buyer "..." --visual-mood "..."
```

Read `.design-brain/TEMPLATE_PRODUCT_MEMORY.md`, `.design-brain/TEMPLATE_TAXONOMY.md`, `.design-brain/TEMPLATE_STRUCTURE_RULES.md`, `.design-brain/MARKETPLACE_QUALITY_GATE.md`, `.design-brain/PREVIEW_PRESENTATION_SYSTEM.md`, and `.design-brain/STYLE_PACKS.json`. Avoid generic template output and optimize for editable, reusable, marketplace-ready products.

## Advanced Medium/Product-Type Workflow

Before selecting visual style, Codex should identify the medium and load `.design-brain/MEDIUM_PRODUCT_PLAYBOOKS.md`, `.design-brain/ADVANCED_STYLE_GRAMMAR_MATRIX.md`, and `.design-brain/HUMAN_CRAFT_HEURISTICS.md`.

Use:

```bash
python scripts/design_brain_medium_playbook.py --task "..." --template-type "..." --niche "..." --target-buyer "..."
```

When the task mentions PowerPoint, presentation, pitch deck, deck, slides, Keynote, PPT, or PPTX, Codex must load `skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md` and plan from a slide-role matrix instead of a landing-page section map.

## Design-Anything Selective Index Workflow

For website, landing page, dashboard, ecommerce, portfolio, PowerPoint/deck, UI kit, brand kit, marketplace preview, mobile app, email/newsletter, static canvas/poster, or document/report tasks, Codex should run or follow module selection before choosing style:

```bash
python scripts/design_brain_module_select.py --task "..." --template-type "..." --niche "..." --target-buyer "..." --visual-mood "..." --dry-run
```

The module selector returns the medium module, craft modules, seed pack, direction pack, validators, and source files. Use this to prevent one landing-page workflow from being applied to every design product.

Generated external indexes from `open-design` and `awesome-claude-skills` belong in `.design-brain/external-indexes/` and must not be treated as stable memory unless explicitly promoted.

For reference-based or batch work, use `.design-brain/REFERENCE_DECONSTRUCTION_MATRIX.md`, `.design-brain/ORIGINALITY_SIMILARITY_SCORECARD.md`, and:

```bash
python scripts/design_brain_originality_score.py --reference-summary "..." --proposed-structure "..." --template-type "..." --dry-run
```

## Template Style Routing Workflow

For template tasks, Codex should select only relevant TypeUI-derived style packs. Do not combine all skills. Use TypeUI skills as style references and design constraints, not raw prompts to blindly merge.

```bash
python scripts/design_brain_typeui_ingest.py
python scripts/design_brain_style_select.py --template-type "..." --niche "..." --visual-mood "..." --target-buyer "..."
```

Identify the selected style pack, selected skills, rejected conflicts, structure implications, preview direction, and marketplace quality gate before designing.

## Template Product Orchestration Workflow

For any sellable template product task, Codex should create or follow a template orchestration report before designing.

Codex must not jump straight into visuals or code. It must first determine product type, buyer, niche, style strategy, structure, editable requirements, preview direction, and marketplace quality gate.

Use the orchestrator when the task involves marketplace-ready templates, Figma templates, landing page templates, dashboard templates, UI kits, branding kits, mockup previews, or product covers:

```bash
python scripts/design_brain_template_orchestrate.py --template-type "..." --niche "..." --target-buyer "..." --visual-mood "..." --notes "..."
```

## Design Quality Rules

- Prefer premium, clean, modern, marketplace-ready design.
- Prioritize strong visual hierarchy and one clear primary action.
- Use intentional whitespace, clean alignment, and a consistent spacing system.
- Maintain polished typography with clear scale, readable line length, and purposeful emphasis.
- Keep color, radius, shadow, icon, and component-state choices consistent.
- Ensure responsive behavior, accessible contrast, keyboard/focus states where relevant, and text that does not overflow or overlap.
- Avoid generic visual output, default-looking templates, overcrowded sections, and random decorative elements.
- Avoid childish or overly playful UI unless the user explicitly asks for that tone.
- Use gradients, glass effects, heavy shadows, or decorative visuals only when they support the concept.
- Make the design feel intentional, not auto-generated.

## Reflection

When the user gives design feedback, store reusable lessons in `.design-brain/REFLECTION_LOG.md` using the existing format:

- Date
- Task
- User feedback
- What went wrong
- Design lesson
- Rule to reuse next time

## Web Deck Workflow

For any web deck, HTML presentation, animated slide deck, browser deck, interactive deck, single-file deck, presenter or webinar deck, or deck-to-web conversion, Codex must route to the `web-deck` medium instead of the static presentation medium. `web-deck` owns decks that run in a browser with motion, runtime navigation, and a scaled stage. `presentation-deck` keeps every deck whose final artifact is a PPTX, Keynote, Google Slides, or Figma export, and the Non-Web Mode Rule still forbids runtime vocabulary there. A plain presentation, deck, slides, PPT, PPTX, PowerPoint, or Keynote request stays with `presentation-deck`; only explicit browser, HTML, or animated intent routes to `web-deck`. A web deck is also not a website template: it is a fixed 16:9 stage, not a scrolling page.

Required lifecycle:

Route -> cognition -> plan -> stage gate -> build -> motion grammar check -> static audit -> render review -> design system -> post-build audit -> completion receipt.

Load `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md`, `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`, `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`, and `skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md` before structure planning. Build against the runtime kit in `skills/presentation-deck/resources/web-deck/`: `deck-plan-schema.json` for the plan, `stage-base.css` for the stage, and `deck-runtime.js` for navigation and reveal lifecycle. When the source is an existing PPT/PPTX deck, extract content through `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md` and `skills/presentation-deck/runtime/web/design_brain_deck_source_extract.mjs`, then plan a new structure instead of transcribing the source layout.

Hard rules:

- Author every slide on a fixed 1920x1080 stage. Slide content must not reflow for small screens; the stage is fitted with one uniform scale transform and may letterbox or pillarbox.
- Switch slides with visibility, opacity, and pointer-events, never by toggling `display`. A later `display: flex` rule overrides a display-based hide and reveals every slide at once.
- A `prefers-reduced-motion: reduce` block is mandatory, and JS-driven motion must check the same query before animating.
- Keep chrome such as progress, page number, and controls outside the scaled stage, and hide it in print.
- Keep the deck dependency-free: no CDN script, no build step, no runtime package. Fonts are the only allowed external request.
- Give every deck its own motion signature. Two decks must not share entrance order, accent motion, easing, and transition grammar. Repeated motion grammar is a visual-language defect, the same as a reused scaffold.

Use the web deck tools:

```bash
node skills/presentation-deck/runtime/web/design_brain_web_deck_plan.mjs --demo --out "..."
node skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs "..." --json
node skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs "..." --json
```

The plan tool writes the deck plan and the single-file deck. The audit tool reads the built HTML and enforces the stage, slide-switching, reduced-motion, chrome, dependency, and print rules. The render review tool opens the deck in the repo's existing browser tooling and writes its evidence set into `.design-brain/screenshots/<stamp>-<slug>-web-deck-render/` (one `slides/slide-NNN.png` per slide, one narrow-viewport capture, `deck-print.pdf`, and `render-review.json`) plus a Markdown report in `.design-brain/visual-reviews/`.

A visible web deck is not complete. The static audit must pass on the built HTML and the render review must produce rendered per-slide evidence before the design system, post-build audit, and completion receipt can run. Generate the receipt from `skills/presentation-deck/resources/WEB_DECK_RECEIPT.md`. Do not say done, final, ready, or complete for a web deck without a static audit result and a rendered review.
"""

CLEAN_REFLECTION_LOG = """# Reflection Log

Save reusable lessons from user feedback here. Keep entries concise and practical.

## Entry Format

### Date

YYYY-MM-DD

### Task

What was being designed or improved.

### User Feedback

What the user said or implied.

### What Went Wrong

The design issue, decision mistake, missing constraint, or workflow gap.

### Design Lesson

The reusable insight.

### Rule To Reuse Next Time

A concrete rule future Codex should apply.

---
"""

CLEAN_REFERENCE_INSIGHT_JOURNAL = """# Reference Insight Journal

Store accumulated lessons from user-provided references here. References are insight sources, not layouts to copy.

## Entry Format

## YYYY-MM-DD HH:MM - [Reference Name]

### Reference Name Or Source

...

### Reference Type

...

### Template Category

...

### Observed Design Intent

...

### Visual Mood

...

### Structural Insight

...

### Hierarchy Insight

...

### Section Flow Insight

...

### Marketplace Insight

...

### Reusable Lesson

...

### Do-Not-Copy Notes

...

### How To Reinterpret In Future Template Products

...

---
"""

CLEAN_TEMPLATE_BUILD_JOURNAL = """# Template Build Journal

Record every template product that Codex Design Brain helps plan, design, or review.

## Record Format

## YYYY-MM-DD HH:MM - [Template Name]

### Template Name

...

### Template Type

...

### Niche

...

### Target Buyer

...

### Marketplace Category

...

### Selected Style Packs

...

### Used Reference Insights

...

### Section Structure

...

### Preview / Cover Direction

...

### Editable Areas

...

### What Made It Original

...

### What To Avoid Repeating Next Time

...

### Related Reports

...

---
"""

CLEAN_TEMPLATE_NAMING_LEDGER = """# Template Naming Ledger

Track template names and naming patterns so future template products do not feel recycled.

## Naming Rules

- Never reuse the same naming pattern too closely.
- Avoid repeating the same suffix or prefix across similar niches.
- Avoid names that sound like recycled versions of older templates.
- Generate multiple candidates before choosing.
- Score names for originality, niche fit, memorability, and marketplace clarity.

## Entry Format

## YYYY-MM-DD HH:MM - [Template Name]

### Niche

...

### Template Type

...

### Naming Pattern

...

### Words Used

...

### Prefix / Suffix Used

...

### Metaphor Category

...

### Similarity Risk

...

### Avoid List For Future Names

...

---
"""


@dataclass(frozen=True)
class ManagedFile:
    source: str
    target: str
    clean_reflection: bool = False
    clean_content: str | None = None


MANAGED_FILES = [
    ManagedFile(".design-brain/README.md", ".design-brain/README.md"),
    ManagedFile(".design-brain/MANIFEST.json", ".design-brain/MANIFEST.json"),
    ManagedFile(".design-brain/INSTALLATION.md", ".design-brain/INSTALLATION.md"),
    ManagedFile(".design-brain/PILOT_WORKFLOW.md", ".design-brain/PILOT_WORKFLOW.md"),
    ManagedFile(".design-brain/QUICK_START.md", ".design-brain/QUICK_START.md"),
    ManagedFile(".design-brain/DESIGN_MEMORY.md", ".design-brain/DESIGN_MEMORY.md"),
    ManagedFile(".design-brain/DESIGN_PREFERENCES.json", ".design-brain/DESIGN_PREFERENCES.json"),
    ManagedFile(".design-brain/DESIGN_SOUL.md", ".design-brain/DESIGN_SOUL.md"),
    ManagedFile(".design-brain/DESIGN_IDENTITY.md", ".design-brain/DESIGN_IDENTITY.md"),
    ManagedFile(".design-brain/USER_DESIGN_CONTEXT.md", ".design-brain/USER_DESIGN_CONTEXT.md"),
    ManagedFile(".design-brain/DESIGN_PRINCIPLES.md", ".design-brain/DESIGN_PRINCIPLES.md"),
    ManagedFile(".design-brain/DESIGN_OPERATING_RULES.md", ".design-brain/DESIGN_OPERATING_RULES.md"),
    ManagedFile(".design-brain/AUTOLOAD_POLICY.md", ".design-brain/AUTOLOAD_POLICY.md"),
    ManagedFile(".design-brain/SOURCE_OF_TRUTH_MAP.md", ".design-brain/SOURCE_OF_TRUTH_MAP.md"),
    ManagedFile(".design-brain/BUILD_SESSION_LIFECYCLE.md", ".design-brain/BUILD_SESSION_LIFECYCLE.md"),
    ManagedFile(".design-brain/DESIGN_CRAFT_NON_OVERRIDE_CONTRACT.md", ".design-brain/DESIGN_CRAFT_NON_OVERRIDE_CONTRACT.md"),
    ManagedFile(".design-brain/ROUTING_ALIASES_ID.json", ".design-brain/ROUTING_ALIASES_ID.json"),
    ManagedFile(".design-brain/DESIGNER_COGNITION_LAYER.md", ".design-brain/DESIGNER_COGNITION_LAYER.md"),
    ManagedFile(".design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md", ".design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md"),
    ManagedFile(
        ".design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.md",
        ".design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.md",
    ),
    ManagedFile(
        ".design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.json",
        ".design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.json",
    ),
    ManagedFile(".design-brain/REFERENCE_CORPUS_CONFIG.md", ".design-brain/REFERENCE_CORPUS_CONFIG.md"),
    ManagedFile(".design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md", ".design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md"),
    ManagedFile(".design-brain/FIGMA_OUTPUT_TARGET.md", ".design-brain/FIGMA_OUTPUT_TARGET.md"),
    ManagedFile(".design-brain/FIGMA_OUTPUT_TARGET.local.example.json", ".design-brain/FIGMA_OUTPUT_TARGET.local.example.json"),
    ManagedFile(".design-brain/FIGMA_REFERENCE_DEEP_STUDY.md", ".design-brain/FIGMA_REFERENCE_DEEP_STUDY.md"),
    ManagedFile(
        ".design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md",
        ".design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md",
    ),
    ManagedFile(
        ".design-brain/FIGMA_REFERENCE_LEARNING_CORPUS.md",
        ".design-brain/FIGMA_REFERENCE_LEARNING_CORPUS.md",
    ),
    ManagedFile(
        ".design-brain/CONTINUOUS_DESIGNER_LEARNING_LOOP.md",
        ".design-brain/CONTINUOUS_DESIGNER_LEARNING_LOOP.md",
    ),
    ManagedFile(".design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md", ".design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md"),
    ManagedFile(".design-brain/CONTEXT_PRIORITY.md", ".design-brain/CONTEXT_PRIORITY.md"),
    ManagedFile(".design-brain/NATURAL_INTENT_ROUTER.md", ".design-brain/NATURAL_INTENT_ROUTER.md"),
    ManagedFile(".design-brain/DESIGN_AUTOPILOT.md", ".design-brain/DESIGN_AUTOPILOT.md"),
    ManagedFile(
        ".design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md",
        ".design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md",
    ),
    ManagedFile(".design-brain/WORKFLOW_TRIGGER_MAP.md", ".design-brain/WORKFLOW_TRIGGER_MAP.md"),
    ManagedFile(".design-brain/RESPONSE_BEHAVIOR.md", ".design-brain/RESPONSE_BEHAVIOR.md"),
    ManagedFile(".design-brain/MEDIUM_PRODUCT_PLAYBOOKS.md", ".design-brain/MEDIUM_PRODUCT_PLAYBOOKS.md"),
    ManagedFile(
        ".design-brain/REFERENCE_DECONSTRUCTION_MATRIX.md",
        ".design-brain/REFERENCE_DECONSTRUCTION_MATRIX.md",
    ),
    ManagedFile(
        ".design-brain/ORIGINALITY_SIMILARITY_SCORECARD.md",
        ".design-brain/ORIGINALITY_SIMILARITY_SCORECARD.md",
    ),
    ManagedFile(".design-brain/HUMAN_CRAFT_HEURISTICS.md", ".design-brain/HUMAN_CRAFT_HEURISTICS.md"),
    ManagedFile(".design-brain/GOOD_BAD_EXAMPLE_LIBRARY.md", ".design-brain/GOOD_BAD_EXAMPLE_LIBRARY.md"),
    ManagedFile(
        ".design-brain/ADVANCED_STYLE_GRAMMAR_MATRIX.md",
        ".design-brain/ADVANCED_STYLE_GRAMMAR_MATRIX.md",
    ),
    ManagedFile(
        "skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md",
        "skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md",
    ),
    ManagedFile(".design-brain/REFERENCE_INSIGHT_SYSTEM.md", ".design-brain/REFERENCE_INSIGHT_SYSTEM.md"),
    ManagedFile(
        ".design-brain/REFERENCE_INSIGHT_JOURNAL.md",
        ".design-brain/REFERENCE_INSIGHT_JOURNAL.md",
        clean_content=CLEAN_REFERENCE_INSIGHT_JOURNAL,
    ),
    ManagedFile(
        ".design-brain/TEMPLATE_BUILD_JOURNAL.md",
        ".design-brain/TEMPLATE_BUILD_JOURNAL.md",
        clean_content=CLEAN_TEMPLATE_BUILD_JOURNAL,
    ),
    ManagedFile(
        ".design-brain/TEMPLATE_NAMING_LEDGER.md",
        ".design-brain/TEMPLATE_NAMING_LEDGER.md",
        clean_content=CLEAN_TEMPLATE_NAMING_LEDGER,
    ),
    ManagedFile(".design-brain/ORIGINALITY_GUARD.md", ".design-brain/ORIGINALITY_GUARD.md"),
    ManagedFile(".design-brain/TEMPLATE_PRODUCT_MEMORY.md", ".design-brain/TEMPLATE_PRODUCT_MEMORY.md"),
    ManagedFile(".design-brain/TEMPLATE_PRODUCT_INTELLIGENCE.md", ".design-brain/TEMPLATE_PRODUCT_INTELLIGENCE.md"),
    ManagedFile(".design-brain/TEMPLATE_TAXONOMY.md", ".design-brain/TEMPLATE_TAXONOMY.md"),
    ManagedFile(".design-brain/TEMPLATE_STRUCTURE_RULES.md", ".design-brain/TEMPLATE_STRUCTURE_RULES.md"),
    ManagedFile(".design-brain/TEMPLATE_STYLE_ROUTER.md", ".design-brain/TEMPLATE_STYLE_ROUTER.md"),
    ManagedFile(".design-brain/TEMPLATE_STYLE_PACKS.json", ".design-brain/TEMPLATE_STYLE_PACKS.json"),
    ManagedFile(".design-brain/TEMPLATE_ORCHESTRATOR.md", ".design-brain/TEMPLATE_ORCHESTRATOR.md"),
    ManagedFile(".design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md", ".design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md"),
    ManagedFile(".design-brain/QUALITY_GATE_FAILURE_TAXONOMY.md", ".design-brain/QUALITY_GATE_FAILURE_TAXONOMY.md"),
    ManagedFile(".design-brain/BATCH_TEMPLATE_HARD_GATES.md", ".design-brain/BATCH_TEMPLATE_HARD_GATES.md"),
    ManagedFile(".design-brain/EFFECT_LANGUAGE_JUDGMENT.md", ".design-brain/EFFECT_LANGUAGE_JUDGMENT.md"),
    ManagedFile(".design-brain/MARKETPLACE_QUALITY_GATE.md", ".design-brain/MARKETPLACE_QUALITY_GATE.md"),
    ManagedFile(".design-brain/PREVIEW_PRESENTATION_SYSTEM.md", ".design-brain/PREVIEW_PRESENTATION_SYSTEM.md"),
    ManagedFile(".design-brain/STYLE_PACKS.json", ".design-brain/STYLE_PACKS.json"),
    ManagedFile(
        ".design-brain/VISUAL_CRITIQUE_CHECKLIST.md",
        ".design-brain/VISUAL_CRITIQUE_CHECKLIST.md",
    ),
    ManagedFile(".design-brain/PATTERN_LIBRARY.md", ".design-brain/PATTERN_LIBRARY.md"),
    ManagedFile(".design-brain/REFLECTION_LOG.md", ".design-brain/REFLECTION_LOG.md", True),
    ManagedFile(".design-brain/typeui-skills/README.md", ".design-brain/typeui-skills/README.md"),
    ManagedFile(".design-brain/reference-insights/README.md", ".design-brain/reference-insights/README.md"),
    ManagedFile(".design-brain/template-orchestrations/README.md", ".design-brain/template-orchestrations/README.md"),
    ManagedFile(".design-brain/pilots/README.md", ".design-brain/pilots/README.md"),
    ManagedFile(".design-brain/screenshots/README.md", ".design-brain/screenshots/README.md"),
    ManagedFile(
        ".design-brain/promotion-proposals/README.md",
        ".design-brain/promotion-proposals/README.md",
    ),
    ManagedFile(".design-brain/proposed-rules/README.md", ".design-brain/proposed-rules/README.md"),
    ManagedFile(
        ".design-brain/templates/TEMPLATE_PRODUCT_BRIEF.md",
        ".design-brain/templates/TEMPLATE_PRODUCT_BRIEF.md",
    ),
    ManagedFile(
        ".design-brain/templates/DESIGN_CONTEXT_PACKET.md",
        ".design-brain/templates/DESIGN_CONTEXT_PACKET.md",
    ),
    ManagedFile(
        ".design-brain/templates/TEMPLATE_STYLE_DECISION_REPORT.md",
        ".design-brain/templates/TEMPLATE_STYLE_DECISION_REPORT.md",
    ),
    ManagedFile(
        ".design-brain/templates/TEMPLATE_ORCHESTRATION_REPORT.md",
        ".design-brain/templates/TEMPLATE_ORCHESTRATION_REPORT.md",
    ),
    ManagedFile(
        ".design-brain/templates/REFERENCE_INSIGHT_ENTRY.md",
        ".design-brain/templates/REFERENCE_INSIGHT_ENTRY.md",
    ),
    ManagedFile(
        ".design-brain/templates/FIGMA_REFERENCE_SCHEMA_RECEIPT.md",
        ".design-brain/templates/FIGMA_REFERENCE_SCHEMA_RECEIPT.md",
    ),
    ManagedFile(
        ".design-brain/templates/TEMPLATE_BUILD_RECORD.md",
        ".design-brain/templates/TEMPLATE_BUILD_RECORD.md",
    ),
    ManagedFile(
        ".design-brain/templates/TEMPLATE_NAME_CHECK.md",
        ".design-brain/templates/TEMPLATE_NAME_CHECK.md",
    ),
    ManagedFile(".design-brain/templates/DESIGN_TASK_BRIEF.md", ".design-brain/templates/DESIGN_TASK_BRIEF.md"),
    ManagedFile(
        ".design-brain/templates/USER_FEEDBACK_TO_REFLECTION.md",
        ".design-brain/templates/USER_FEEDBACK_TO_REFLECTION.md",
    ),
    ManagedFile(
        ".design-brain/templates/MEMORY_PROMOTION_REQUEST.md",
        ".design-brain/templates/MEMORY_PROMOTION_REQUEST.md",
    ),
    ManagedFile(
        ".design-brain/templates/SCREENSHOT_REVIEW_BRIEF.md",
        ".design-brain/templates/SCREENSHOT_REVIEW_BRIEF.md",
    ),
    ManagedFile(
        ".design-brain/templates/REAL_PROJECT_PILOT_BRIEF.md",
        ".design-brain/templates/REAL_PROJECT_PILOT_BRIEF.md",
    ),
    ManagedFile(
        ".design-brain/templates/PILOT_RESULT_REPORT.md",
        ".design-brain/templates/PILOT_RESULT_REPORT.md",
    ),
    ManagedFile(
        ".design-brain/templates/NATURAL_INTENT_DECISION.md",
        ".design-brain/templates/NATURAL_INTENT_DECISION.md",
    ),
    ManagedFile(
        ".design-brain/templates/SEQUENTIAL_REFERENCE_BATCH_CYCLE.md",
        ".design-brain/templates/SEQUENTIAL_REFERENCE_BATCH_CYCLE.md",
    ),
    ManagedFile(
        ".design-brain/templates/DESIGNER_LEARNING_CYCLE.md",
        ".design-brain/templates/DESIGNER_LEARNING_CYCLE.md",
    ),
    ManagedFile(
        ".design-brain/templates/PROPOSED_RULE_CHANGE.md",
        ".design-brain/templates/PROPOSED_RULE_CHANGE.md",
    ),
    ManagedFile(".agents/skills/design-critic/SKILL.md", ".agents/skills/design-critic/SKILL.md"),
    ManagedFile("scripts/install_design_brain.py", "scripts/install_design_brain.py"),
    ManagedFile("scripts/design_brain_sequential_batch.py", "scripts/design_brain_sequential_batch.py"),
    ManagedFile("scripts/design_brain_intent_route.py", "scripts/design_brain_intent_route.py"),
    ManagedFile("scripts/design_brain_website_types.py", "scripts/design_brain_website_types.py"),
    ManagedFile("scripts/design_brain_website_reference_select.py", "scripts/design_brain_website_reference_select.py"),
    ManagedFile("scripts/design_brain_reference_corpus_health.py", "scripts/design_brain_reference_corpus_health.py"),
    ManagedFile("scripts/design_brain_router_smoke_test.py", "scripts/design_brain_router_smoke_test.py"),
    ManagedFile("scripts/design_brain_package_integrity.py", "scripts/design_brain_package_integrity.py"),
    ManagedFile("scripts/design_brain_export_package.py", "scripts/design_brain_export_package.py"),
    ManagedFile("scripts/design_brain_verify_release.py", "scripts/design_brain_verify_release.py"),
    ManagedFile("scripts/design_brain_typeui_ingest.py", "scripts/design_brain_typeui_ingest.py"),
    ManagedFile("scripts/design_brain_style_select.py", "scripts/design_brain_style_select.py"),
    ManagedFile("scripts/design_brain_template_plan.py", "scripts/design_brain_template_plan.py"),
    ManagedFile("scripts/design_brain_template_orchestrate.py", "scripts/design_brain_template_orchestrate.py"),
    ManagedFile("scripts/design_brain_medium_playbook.py", "scripts/design_brain_medium_playbook.py"),
    ManagedFile("scripts/design_brain_originality_score.py", "scripts/design_brain_originality_score.py"),
    ManagedFile("scripts/design_brain_context_packet.py", "scripts/design_brain_context_packet.py"),
    ManagedFile("scripts/design_brain_reference_insight.py", "scripts/design_brain_reference_insight.py"),
    ManagedFile("scripts/design_brain_name_check.py", "scripts/design_brain_name_check.py"),
    ManagedFile("scripts/design_brain_build_record.py", "scripts/design_brain_build_record.py"),
    ManagedFile("scripts/design_brain_pilot.py", "scripts/design_brain_pilot.py"),
    ManagedFile("scripts/design_brain_status.py", "scripts/design_brain_status.py"),
    ManagedFile("scripts/design_brain_review.py", "scripts/design_brain_review.py"),
    ManagedFile("scripts/design_brain_visual_review.py", "scripts/design_brain_visual_review.py"),
    ManagedFile(".design-brain/VISUAL_INSPECTION_PROTOCOL.md", ".design-brain/VISUAL_INSPECTION_PROTOCOL.md"),
    ManagedFile("scripts/design_brain_visual_inspect.py", "scripts/design_brain_visual_inspect.py"),
    ManagedFile("scripts/design_brain_visual_gate.py", "scripts/design_brain_visual_gate.py"),
    ManagedFile("scripts/test_design_brain_visual_inspect.py", "scripts/test_design_brain_visual_inspect.py"),
    ManagedFile("scripts/test_design_brain_visual_post_build.py", "scripts/test_design_brain_visual_post_build.py"),
    ManagedFile("scripts/test_design_brain_visual_routes.py", "scripts/test_design_brain_visual_routes.py"),
    ManagedFile("scripts/design_brain_reflect.py", "scripts/design_brain_reflect.py"),
    ManagedFile("scripts/design_brain_promote.py", "scripts/design_brain_promote.py"),
    ManagedFile("PUBLIC_PACKAGE_NOTES.md", "PUBLIC_PACKAGE_NOTES.md"),
]

CRAFT_MODULES = [
    "accessibility",
    "anti-ai-slop",
    "color",
    "data-visualization",
    "deck-motion",
    "figma-auto-layout",
    "form-validation",
    "layout-composition",
    "marketplace-originality",
    "motion-discipline",
    "pptx-frame-precision",
    "pptx-readability",
    "responsive-behavior",
    "spacing-rhythm",
    "state-coverage",
    "typography",
    "web-deck-stage-fidelity",
]
SEED_PACKS = [
    "brand-kit",
    "dashboard",
    "document-report",
    "ecommerce",
    "email-newsletter",
    "hero-header-kit",
    "landing-page",
    "marketplace-preview",
    "mobile-app",
    "portfolio",
    "presentation-deck",
    "static-canvas",
    "ui-kit",
    "web-deck",
    "website-template",
]
SEED_FILES = ["layouts.md", "checklist.md", "content-patterns.md", "design-system-scope.md"]
MANAGED_FILES.extend(
    [
        ManagedFile(".design-brain/registry/README.md", ".design-brain/registry/README.md"),
        ManagedFile(".design-brain/registry/modules.json", ".design-brain/registry/modules.json"),
        ManagedFile(".design-brain/craft/README.md", ".design-brain/craft/README.md"),
        ManagedFile(".design-brain/direction-packs/README.md", ".design-brain/direction-packs/README.md"),
        ManagedFile(".design-brain/direction-packs/directions.json", ".design-brain/direction-packs/directions.json"),
        ManagedFile(".design-brain/seed-packs/README.md", ".design-brain/seed-packs/README.md"),
        ManagedFile(".design-brain/external-indexes/README.md", ".design-brain/external-indexes/README.md"),
        ManagedFile("scripts/design_brain_modules.py", "scripts/design_brain_modules.py"),
        ManagedFile("scripts/design_brain_module_select.py", "scripts/design_brain_module_select.py"),
        ManagedFile("scripts/design_brain_external_corpus_index.py", "scripts/design_brain_external_corpus_index.py"),
        ManagedFile("scripts/design_brain_lint_plan.py", "scripts/design_brain_lint_plan.py"),
        ManagedFile("scripts/design_brain_lint_artifact.py", "scripts/design_brain_lint_artifact.py"),
        ManagedFile("skills/presentation-deck/runtime/design_brain_pptx_inventory.py", "skills/presentation-deck/runtime/design_brain_pptx_inventory.py"),
        ManagedFile("skills/presentation-deck/runtime/design_brain_pptx_thumbnail_review.py", "skills/presentation-deck/runtime/design_brain_pptx_thumbnail_review.py"),
        ManagedFile("skills/presentation-deck/runtime/design_brain_pptx_frame_precision_review.py", "skills/presentation-deck/runtime/design_brain_pptx_frame_precision_review.py"),
        ManagedFile("skills/presentation-deck/runtime/design_brain_pptx_render_contact_sheet.py", "skills/presentation-deck/runtime/design_brain_pptx_render_contact_sheet.py"),
        ManagedFile("skills/presentation-deck/runtime/design_brain_pptx_visual_corpus_study.py", "skills/presentation-deck/runtime/design_brain_pptx_visual_corpus_study.py"),
        ManagedFile("skills/presentation-deck/runtime/design_brain_pptx_group_align_check.py", "skills/presentation-deck/runtime/design_brain_pptx_group_align_check.py"),
        ManagedFile("skills/presentation-deck/runtime/design_brain_pptx_visual_balance.py", "skills/presentation-deck/runtime/design_brain_pptx_visual_balance.py"),
    ]
)
MANAGED_FILES.extend(
    ManagedFile(f".design-brain/craft/{name}.md", f".design-brain/craft/{name}.md")
    for name in CRAFT_MODULES
    if name not in {"pptx-readability", "pptx-frame-precision", "deck-motion", "web-deck-stage-fidelity"}
)
MANAGED_FILES.extend(
    ManagedFile(
        f".design-brain/seed-packs/{seed}/{filename}",
        f".design-brain/seed-packs/{seed}/{filename}",
    )
    for seed in SEED_PACKS
    if seed not in {"presentation-deck", "web-deck"}
    for filename in SEED_FILES
)

V2_MANAGED_FILES = [
    ".design-brain/VERSION.md",
    ".design-brain/MIGRATION_LOG.md",
    "skills/presentation-deck/design/00_input_system/asset-rules.md",
    "skills/presentation-deck/design/00_input_system/marketplace-target-rules.md",
    "skills/presentation-deck/design/00_input_system/output-format-rules.md",
    "skills/presentation-deck/design/00_input_system/reference-classification.md",
    "skills/presentation-deck/design/00_input_system/scoring-priority-system.md",
    "skills/presentation-deck/design/00_input_system/target-buyer-library.md",
    "skills/presentation-deck/design/00_input_system/template-brief-schema.md",
    "skills/presentation-deck/design/01_powerpoint_technical/editable-template-rules.md",
    "skills/presentation-deck/design/01_powerpoint_technical/export-compatibility-rules.md",
    "skills/presentation-deck/design/01_powerpoint_technical/placeholder-system.md",
    "skills/presentation-deck/design/01_powerpoint_technical/pptx-openxml-structure.md",
    "skills/presentation-deck/design/01_powerpoint_technical/slide-layout-rules.md",
    "skills/presentation-deck/design/01_powerpoint_technical/slide-master-rules.md",
    "skills/presentation-deck/design/01_powerpoint_technical/theme-color-font-rules.md",
    "skills/presentation-deck/design/02_design_principles/color-system.md",
    "skills/presentation-deck/design/02_design_principles/composition-patterns.md",
    "skills/presentation-deck/design/02_design_principles/grid-spacing-alignment.md",
    "skills/presentation-deck/design/02_design_principles/premium-vs-generic.md",
    "skills/presentation-deck/design/02_design_principles/slide-rhythm.md",
    "skills/presentation-deck/design/02_design_principles/typography-system.md",
    "skills/presentation-deck/design/02_design_principles/visual-hierarchy.md",
    "skills/presentation-deck/design/02_design_principles/visual-polish-rules.md",
    "skills/presentation-deck/design/03_slide_archetypes/agenda-slide.md",
    "skills/presentation-deck/design/03_slide_archetypes/case-study-slide.md",
    "skills/presentation-deck/design/03_slide_archetypes/closing-slide.md",
    "skills/presentation-deck/design/03_slide_archetypes/cover-slide.md",
    "skills/presentation-deck/design/03_slide_archetypes/dashboard-slide.md",
    "skills/presentation-deck/design/03_slide_archetypes/data-slide.md",
    "skills/presentation-deck/design/03_slide_archetypes/feature-slide.md",
    "skills/presentation-deck/design/03_slide_archetypes/portfolio-slide.md",
    "skills/presentation-deck/design/03_slide_archetypes/pricing-slide.md",
    "skills/presentation-deck/design/03_slide_archetypes/problem-slide.md",
    "skills/presentation-deck/design/03_slide_archetypes/roadmap-slide.md",
    "skills/presentation-deck/design/03_slide_archetypes/section-divider-slide.md",
    "skills/presentation-deck/design/03_slide_archetypes/solution-slide.md",
    "skills/presentation-deck/design/03_slide_archetypes/team-slide.md",
    "skills/presentation-deck/design/03_slide_archetypes/testimonial-slide.md",
    "skills/presentation-deck/design/03_slide_archetypes/timeline-slide.md",
    "skills/presentation-deck/design/04_marketplace_standard/buyer-usability-rules.md",
    "skills/presentation-deck/design/04_marketplace_standard/documentation-requirements.md",
    "skills/presentation-deck/design/04_marketplace_standard/envato-presentation-requirements.md",
    "skills/presentation-deck/design/04_marketplace_standard/file-organization.md",
    "skills/presentation-deck/design/04_marketplace_standard/marketplace-originality-rules.md",
    "skills/presentation-deck/design/04_marketplace_standard/preview-image-rules.md",
    ".design-brain/05_reference_breakdowns/good-bad-reference-pairs.md",
    ".design-brain/05_reference_breakdowns/plagiarism-transformation-method.md",
    ".design-brain/05_reference_breakdowns/redesign-from-reference-method.md",
    ".design-brain/05_reference_breakdowns/reference-analysis-template.md",
    ".design-brain/05_reference_breakdowns/reference-to-original-concept-pipeline.md",
    "skills/presentation-deck/design/06_quality_control/accessibility-checklist.md",
    "skills/presentation-deck/design/06_quality_control/design-review-checklist.md",
    "skills/presentation-deck/design/06_quality_control/final-export-checklist.md",
    "skills/presentation-deck/design/06_quality_control/generic-design-detector.md",
    "skills/presentation-deck/design/06_quality_control/marketplace-readiness-checklist.md",
    "skills/presentation-deck/design/06_quality_control/powerpoint-technical-checklist.md",
    "skills/presentation-deck/design/06_quality_control/premium-polish-scorecard.md",
    ".design-brain/07_visual_pipeline/chromium-visual-review.md",
    ".design-brain/07_visual_pipeline/desktop-mobile-preview-rules.md",
    ".design-brain/07_visual_pipeline/overlap-detection-rules.md",
    ".design-brain/07_visual_pipeline/playwright-setup.md",
    ".design-brain/07_visual_pipeline/screenshot-review-checklist.md",
    ".design-brain/07_visual_pipeline/visual-regression-rules.md",
    ".design-brain/08_feedback_memory/README.md",
    ".design-brain/08_feedback_memory/accepted-design-patterns.md",
    ".design-brain/08_feedback_memory/client-style-preferences.md",
    ".design-brain/08_feedback_memory/feedback-log.md",
    ".design-brain/08_feedback_memory/premium-lessons.md",
    ".design-brain/08_feedback_memory/rejected-design-patterns.md",
    "skills/presentation-deck/design/09_prompt_system/design-system-builder-prompt.md",
    "skills/presentation-deck/design/09_prompt_system/master-agent-instruction.md",
    "skills/presentation-deck/design/09_prompt_system/natural-intent-router.md",
    "skills/presentation-deck/design/09_prompt_system/pptx-qa-prompt.md",
    "skills/presentation-deck/design/09_prompt_system/reference-analyzer-prompt.md",
    "skills/presentation-deck/design/09_prompt_system/slide-planner-prompt.md",
    "skills/presentation-deck/design/09_prompt_system/visual-review-prompt.md",
    ".design-brain/evidence/README.md",
    ".design-brain/evidence/visual-reviews/README.md",
    ".design-brain/evidence/fig-extracts/README.md",
    "scripts/design_brain_v2_upgrade.py",
    "scripts/design_brain_fig_extract.mjs",
    "package.json",
    "package-lock.json",
    "tsconfig.json",
    "playwright.config.ts",
    "tests/visual-review.spec.ts",
]
MANAGED_FILES.extend(ManagedFile(path, path) for path in V2_MANAGED_FILES)

SIMULATION_MANAGED_FILES = [
    ".design-brain/DESIGN_SIMULATION_LAYER.md",
    ".design-brain/design-simulation/README.md",
    ".design-brain/design-simulation/agents.json",
    ".design-brain/design-simulation/verdict-schema.json",
    ".design-brain/templates/DESIGN_SIMULATION_VERDICT.md",
    "scripts/design_brain_design_simulate.py",
    "scripts/design_brain_design_sim_smoke_test.py",
    "scripts/design_brain_process_utils.py",
    "scripts/design_brain_process_utils_smoke_test.py",
]
MANAGED_FILES.extend(ManagedFile(path, path) for path in SIMULATION_MANAGED_FILES)

POST_BUILD_MANAGED_FILES = [
    ".design-brain/POST_BUILD_COMPLETION_GATE.md",
    ".design-brain/DESIGN_SYSTEM_BUILD_REQUIREMENTS.md",
    ".design-brain/POST_BUILD_TRIPLE_AUDIT_GATE.md",
    ".design-brain/post-build/design-system-receipt-schema.json",
    ".design-brain/post-build/post-build-audit-schema.json",
    ".design-brain/post-build/batch-similarity-schema.json",
    ".design-brain/templates/DESIGN_SYSTEM_RECEIPT.md",
    ".design-brain/templates/POST_BUILD_AUDIT_RECEIPT.md",
    ".design-brain/templates/BATCH_SIMILARITY_AUDIT_RECEIPT.md",
    "scripts/design_brain_post_build_audit.py",
    "scripts/design_brain_design_system_check.py",
    "scripts/design_brain_batch_similarity_audit.py",
    "scripts/design_brain_build_session.py",
    "scripts/design_brain_sequential_provenance_check.py",
    "scripts/design_brain_post_build_smoke_test.py",
]
MANAGED_FILES.extend(ManagedFile(path, path) for path in POST_BUILD_MANAGED_FILES)

COGNITION_MANAGED_FILES = [
    ".design-brain/DESIGN_COGNITION_CONTRACT.md",
    ".design-brain/DESIGN_COGNITION_GATE.md",
    ".design-brain/design-cognition/design-cognition-receipt-schema.json",
    ".design-brain/templates/DESIGN_COGNITION_RECEIPT.md",
    ".design-brain/templates/DESIGN_COGNITION_RECEIPT.json",
    "scripts/design_brain_design_cognition_check.py",
    "scripts/design_brain_design_cognition_smoke_test.py",
]
MANAGED_FILES.extend(ManagedFile(path, path) for path in COGNITION_MANAGED_FILES)

RUNTIME_MANAGED_FILES = [
    ".design-brain/runtime/README.md",
    ".design-brain/runtime/DESIGN_AGENT_RUNTIME.md",
    ".design-brain/runtime/COMMAND_REGISTRY.md",
    ".design-brain/runtime/TOOL_REGISTRY.md",
    ".design-brain/runtime/PERMISSION_MODES.md",
    ".design-brain/runtime/HOOKS.md",
    ".design-brain/runtime/SESSION_STATE.md",
    ".design-brain/runtime/REPAIR_TICKETS.md",
    ".design-brain/runtime/CONTEXT_COMPACTION.md",
    ".design-brain/runtime/DOCTOR_STATUS.md",
    ".design-brain/runtime/hooks.example.json",
    ".design-brain/runtime/schemas/command-registry-schema.json",
    ".design-brain/runtime/schemas/tool-registry-schema.json",
    ".design-brain/runtime/schemas/session-state-schema.json",
    ".design-brain/runtime/schemas/repair-ticket-schema.json",
    ".design-brain/runtime/schemas/hook-config-schema.json",
    ".design-brain/runtime/schemas/runtime-result-schema.json",
    ".design-brain/runtime/schemas/permission-mode-schema.json",
    ".design-brain/runtime/schemas/compact-context-schema.json",
    "scripts/design_brain_runtime.py",
    "scripts/design_brain_command_router.py",
    "scripts/design_brain_tool_registry.py",
    "scripts/design_brain_permission.py",
    "scripts/design_brain_repair_ticket.py",
    "scripts/design_brain_doctor.py",
    "scripts/design_brain_status_runtime.py",
    "scripts/design_brain_context_compact.py",
    "scripts/design_brain_runtime_smoke_test.py",
    "scripts/design_brain_craft_adapter_bridge_smoke_test.py",
]
MANAGED_FILES.extend(ManagedFile(path, path) for path in RUNTIME_MANAGED_FILES)

REFERENCE_USAGE_MANAGED_FILES = [
    ".design-brain/TEMPLATE_REFERENCE_USAGE_POLICY.md",
    ".design-brain/TEMPLATE_REFERENCE_USAGE_REGISTRY.json",
    ".design-brain/lifecycle/brand-reference-usage-schema.json",
    ".design-brain/templates/BRAND_REFERENCE_USAGE_RECORD.md",
    "scripts/design_brain_reference_usage_gate.py",
    "scripts/design_brain_reference_usage_smoke_test.py",
    "scripts/design_brain_reference_usage_receipt_check.py",
]
MANAGED_FILES.extend(ManagedFile(path, path) for path in REFERENCE_USAGE_MANAGED_FILES)

SECTION_LAYOUT_MANAGED_FILES = [
    ".design-brain/SECTION_LAYOUT_EXTRACTION_LIBRARY.md",
    ".design-brain/SECTION_LAYOUT_HYPER_ACCURACY_GATE.md",
    ".design-brain/SECTION_LAYOUT_MATCHING_GATE.md",
    ".design-brain/section-layout-library/README.md",
    ".design-brain/section-layout-library/pattern-schema.json",
    ".design-brain/templates/SECTION_LAYOUT_PATTERN.md",
    "scripts/design_brain_section_layout_extract.py",
    "scripts/design_brain_section_layout_matching_smoke_test.py",
    "scripts/design_brain_section_layout_smoke_test.py",
]
MANAGED_FILES.extend(ManagedFile(path, path) for path in SECTION_LAYOUT_MANAGED_FILES)

SUBAGENT_MANAGED_FILES = [
    ".design-brain/SUBAGENT_ORCHESTRATION_LAYER.md",
    ".design-brain/SUBAGENT_RECEIPT_SEMANTIC_VALIDATOR.md",
    ".design-brain/design-subagents/README.md",
    ".design-brain/design-subagents/agents.json",
    ".design-brain/design-subagents/subagent-schema.json",
    ".design-brain/design-subagents/orchestration-receipt-schema.json",
    ".design-brain/design-subagents/semantic-validation-schema.json",
    ".design-brain/design-subagents/semantic-validation-rules.json",
    ".design-brain/templates/SUBAGENT_ORCHESTRATION_RECEIPT.md",
    "scripts/design_brain_subagent_orchestrate.py",
    "scripts/design_brain_subagent_receipt_validate.py",
    "scripts/design_brain_subagent_smoke_test.py",
    "scripts/design_brain_subagent_semantic_smoke_test.py",
]
MANAGED_FILES.extend(ManagedFile(path, path) for path in SUBAGENT_MANAGED_FILES)

WEB_DECK_MANAGED_FILES = [
    "skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md",
    "skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md",
    "skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md",
    "skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md",
    "skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md",
    "skills/presentation-deck/resources/web-deck/README.md",
    "skills/presentation-deck/resources/web-deck/deck-plan-schema.json",
    "skills/presentation-deck/resources/web-deck/stage-base.css",
    "skills/presentation-deck/resources/web-deck/deck-runtime.js",
    "skills/presentation-deck/resources/WEB_DECK_RECEIPT.md",
    "skills/presentation-deck/runtime/web/design_brain_web_deck_plan.mjs",
    "skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs",
    "skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs",
    "skills/presentation-deck/runtime/web/design_brain_deck_source_extract.mjs",
    "skills/presentation-deck/tests/design_brain_web_deck_smoke_test.mjs",
]
MANAGED_FILES.extend(ManagedFile(path, path) for path in WEB_DECK_MANAGED_FILES)

PPTX_NATIVE_MANAGED_FILES = [
    "skills/presentation-deck/workflows/native.md",
    "skills/presentation-deck/provenance/adoption.json",
    "skills/presentation-deck/resources/routing.json",
    "skills/presentation-deck/resources/receipt-schema.json",
    "skills/presentation-deck/provenance/ppt-master-LICENSE",
    "skills/presentation-deck/runtime/presentation.py",
    "skills/presentation-deck/runtime/routing.py",
    "skills/presentation-deck/tests/design_brain_pptx_smoke_test.py",
]
MANAGED_FILES.extend(ManagedFile(path, path) for path in PPTX_NATIVE_MANAGED_FILES)

GENERATED_DIRS = [
    ".design-brain/local-memory",
    ".design-brain/pilots",
    ".design-brain/context-packets",
    ".design-brain/reference-insights",
    ".design-brain/template-plans",
    ".design-brain/template-orchestrations",
    ".design-brain/reviews",
    ".design-brain/screenshots",
    ".design-brain/visual-reviews",
    ".design-brain/pptx-precision-reviews",
    ".design-brain/promotion-proposals",
    ".design-brain/proposed-rules",
    ".design-brain/external-indexes",
    ".design-brain/evidence",
    ".design-brain/evidence/visual-reviews",
    ".design-brain/evidence/fig-extracts",
    ".design-brain/evidence/deck-source-extracts",
    ".design-brain/runtime/state",
]

TYPEUI_HISTORY_DIRS = [
    ".design-brain/typeui-skills/raw",
    ".design-brain/typeui-skills/extracted",
    ".design-brain/context-packets",
    ".design-brain/reference-insights",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install Codex Design Brain into a target repo.")
    parser.add_argument("--target", required=True, help="Target repository folder.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing files.")
    parser.add_argument("--force", action="store_true", help="Overwrite managed files with snapshots.")
    parser.add_argument(
        "--include-history",
        action="store_true",
        help="Copy current reflection/reference/build/naming history and optional imported files instead of clean fresh journals.",
    )
    return parser.parse_args()


def source_root() -> Path:
    return Path(__file__).resolve().parents[1]


def manifest_managed_files(root: Path, known_targets: set[str]) -> list[ManagedFile]:
    """Read managed files from MANIFEST.json so installer and manifest stay in sync."""
    manifest_path = root / ".design-brain" / "MANIFEST.json"
    if not manifest_path.exists():
        return []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid MANIFEST.json: {exc}") from exc
    paths: list[str] = []
    for key in ("mandatory_files", "managed_files", "dev_files", "public_docs_assets"):
        values = manifest.get(key, [])
        if isinstance(values, list):
            paths.extend(str(value).replace("\\", "/") for value in values if isinstance(value, str))
    managed: list[ManagedFile] = []
    for path in sorted(set(paths)):
        if not path or "*" in path or path.endswith("/") or path in known_targets:
            continue
        if (root / path).is_file():
            managed.append(ManagedFile(path, path))
    return managed


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def snapshot_file(path: Path, dry_run: bool) -> Path:
    snapshot_path = path.with_name(f"{path.name}.bak-{timestamp()}")
    if not dry_run:
        shutil.copy2(path, snapshot_path)
    return snapshot_path


def extract_design_brain_agents_content(text: str) -> str:
    if START_MARKER in text and END_MARKER in text:
        marked = text.split(START_MARKER, 1)[1].split(END_MARKER, 1)[0]
        return marked.strip()

    heading = "# Codex Design Brain"
    start = text.find(heading)
    if start == -1:
        return DEFAULT_AGENTS_SECTION.strip()

    remainder = text[start:]
    next_heading = remainder.find("\n# ", 1)
    if next_heading == -1:
        return remainder.strip()
    return remainder[:next_heading].strip()


def design_brain_agents_section(root: Path) -> str:
    content = extract_design_brain_agents_content(read_text(root / "AGENTS.md"))
    return f"{START_MARKER}\n{content}\n{END_MARKER}\n"


def merge_agents(target_path: Path, section: str, force: bool, dry_run: bool) -> str:
    if not target_path.exists():
        write_text(target_path, section, dry_run)
        return "CREATE AGENTS.md with Design Brain section"

    existing = read_text(target_path)
    if START_MARKER in existing and END_MARKER in existing:
        before = existing.split(START_MARKER, 1)[0]
        rest = existing.split(START_MARKER, 1)[1]
        after = rest.split(END_MARKER, 1)[1]
        current_section = START_MARKER + rest.split(END_MARKER, 1)[0] + END_MARKER + "\n"
        if current_section.strip() == section.strip():
            return "SKIPPED existing AGENTS.md marked section"
        if not force:
            return "SKIPPED existing AGENTS.md marked section (use --force to update)"
        if force:
            snapshot = snapshot_file(target_path, dry_run)
            action = f"UPDATE existing marked AGENTS.md section with snapshot {snapshot.name}"
        write_text(target_path, before + section + after.lstrip("\n"), dry_run)
        return action

    merged = existing.rstrip() + "\n\n" + section
    write_text(target_path, merged, dry_run)
    return "APPEND marked Design Brain section to existing AGENTS.md"


def source_content(root: Path, managed: ManagedFile, include_history: bool) -> str:
    if managed.clean_reflection and not include_history:
        return CLEAN_REFLECTION_LOG
    if managed.clean_content is not None and not include_history:
        return managed.clean_content
    return read_text(root / managed.source)


def copy_managed_file(
    root: Path,
    target_root: Path,
    managed: ManagedFile,
    force: bool,
    dry_run: bool,
    include_history: bool,
) -> str:
    destination = target_root / managed.target
    if any(path.replace("\\", "/").startswith(".design-brain/local-memory/")
           for path in (managed.source, managed.target)):
        return "PRESERVED local memory: plugin updates do not copy or replace runtime history"
    if destination.exists() and not force:
        return f"SKIPPED existing: {managed.target}"

    if managed.source.startswith("skills/presentation-deck/"):
        if destination.exists() and force:
            snapshot_file(destination, dry_run)
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / managed.source, destination)
        return f"COPIED capability: {managed.target}"

    content = source_content(root, managed, include_history)
    if destination.exists() and force:
        snapshot = snapshot_file(destination, dry_run)
        write_text(destination, content, dry_run)
        return f"OVERWROTE with snapshot {snapshot.name}: {managed.target}"

    write_text(destination, content, dry_run)
    return f"CREATED: {managed.target}"


def ensure_generated_dirs(target_root: Path, dry_run: bool) -> list[str]:
    actions: list[str] = []
    for relative in GENERATED_DIRS:
        path = target_root / relative
        if path.exists():
            actions.append(f"EXISTS dir: {relative}")
        else:
            if not dry_run:
                path.mkdir(parents=True, exist_ok=True)
            actions.append(f"CREATED dir: {relative}")
    return actions


def copy_optional_typeui_history(root: Path, target_root: Path, force: bool, dry_run: bool, include_history: bool) -> list[str]:
    actions: list[str] = []
    for relative in TYPEUI_HISTORY_DIRS:
        source_dir = root / relative
        target_dir = target_root / relative
        if not include_history:
            if target_dir.exists():
                actions.append(f"EXISTS optional dir: {relative}")
            else:
                if not dry_run:
                    target_dir.mkdir(parents=True, exist_ok=True)
                actions.append(f"CREATED empty optional dir: {relative}")
            continue

        if not source_dir.exists():
            if not dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
            actions.append(f"CREATED optional dir without source history: {relative}")
            continue

        for source_file in source_dir.rglob("*"):
            if not source_file.is_file():
                continue
            target_file = target_dir / source_file.relative_to(source_dir)
            display = str(Path(relative) / source_file.relative_to(source_dir)).replace("\\", "/")
            if target_file.exists() and not force:
                actions.append(f"SKIPPED existing optional history: {display}")
                continue
            if target_file.exists() and force:
                snapshot = snapshot_file(target_file, dry_run)
                if not dry_run:
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, target_file)
                actions.append(f"OVERWROTE optional history with snapshot {snapshot.name}: {display}")
                continue
            if not dry_run:
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_file)
            actions.append(f"CREATED optional history: {display}")
    return actions


def main() -> int:
    args = parse_args()
    root = source_root()
    target_root = Path(args.target).expanduser().resolve()

    if target_root == root:
        print("ERROR: Target cannot be the Design Brain source root. Choose another repository.")
        return 1

    actions: list[str] = []

    actions.append(f"Source: {root}")
    actions.append(f"Target: {target_root}")
    actions.append(f"Dry run: {args.dry_run}")
    actions.append(f"Force: {args.force}")
    actions.append(f"Include history: {args.include_history}")

    if not args.dry_run:
        target_root.mkdir(parents=True, exist_ok=True)

    section = design_brain_agents_section(root)
    actions.append(merge_agents(target_root / "AGENTS.md", section, args.force, args.dry_run))

    managed_files = list(MANAGED_FILES)
    known_targets = {managed.target.replace("\\", "/") for managed in managed_files}
    managed_files.extend(manifest_managed_files(root, known_targets))

    known_targets = {managed.target for managed in managed_files}
    capability_files = list((root / "skills/presentation-deck").rglob("*"))
    capability_files.extend((root / "scripts/design_production").rglob("*"))
    capability_files.extend([root / "scripts/design_brain_production_smoke_test.py", root / "scripts/design_brain_production_capability_test.py", root / ".design-brain/runtime/DESIGN_PRODUCTION_SPECIALIST.md", root / ".design-brain/runtime/design-production-contracts.json"])
    for path in capability_files:
        if path.is_file() and "__pycache__" not in path.parts:
            relative = path.relative_to(root).as_posix()
            if relative not in known_targets:
                managed_files.append(ManagedFile(relative, relative))
                known_targets.add(relative)

    # Independent bundled assets dominate install time. Bound copy concurrency
    # and retain deterministic action order; existing-file/snapshot policy stays
    # in copy_managed_file. Duplicate targets stay in the serial path.
    asset_targets = set()
    asset_files = []
    serial_files = []
    for managed in managed_files:
        if managed.source.startswith("skills/presentation-deck/resources/") and managed.target not in asset_targets:
            asset_targets.add(managed.target)
            asset_files.append(managed)
        else:
            serial_files.append(managed)

    for managed in serial_files:
        actions.append(
            copy_managed_file(
                root=root,
                target_root=target_root,
                managed=managed,
                force=args.force,
                dry_run=args.dry_run,
                include_history=args.include_history,
            )
        )

    def copy_asset(managed: ManagedFile) -> str:
        return copy_managed_file(root, target_root, managed, args.force, args.dry_run, args.include_history)

    with ThreadPoolExecutor(max_workers=8) as pool:
        actions.extend(pool.map(copy_asset, asset_files))

    actions.extend(ensure_generated_dirs(target_root, args.dry_run))
    actions.extend(copy_optional_typeui_history(root, target_root, args.force, args.dry_run, args.include_history))

    print("Codex Design Brain Installer")
    print("============================")
    for action in actions:
        print(f"- {action}")
    if args.dry_run:
        print("No files were written because --dry-run was provided.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
