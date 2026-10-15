# Template Product Orchestrator

The Template Product Orchestrator is the recommended entry point before designing any sellable template product. It coordinates product strategy, style routing, template structure, editability requirements, preview direction, marketplace quality checks, and follow-up review commands in one planning report.

## Design Cognition Contract Input

Before orchestration, require a Design Cognition Receipt and run the cognition gate.

Use:

- Style DNA for direction
- Design Intent Lock for product family/output
- Visual Grammar for system design
- Reference Boundary to prevent copying
- Color Role Re-Mapping for palette direction
- Visual Mood Reinterpretation for art direction
- Structural Reconfiguration for layout
- Pattern Divergence for batch difference
- Section Logic for section planning
- Marketplace Readiness for depth and buyer value

No orchestration if the cognition gate fails.

The orchestrator should respect:

- `.design-brain/DESIGN_SOUL.md`
- `.design-brain/DESIGN_IDENTITY.md`
- `.design-brain/USER_DESIGN_CONTEXT.md`
- `.design-brain/DESIGN_PRINCIPLES.md`
- `.design-brain/AUTOLOAD_POLICY.md`

Use it for:

- Marketplace landing page templates
- Figma website templates
- Dashboard and SaaS templates
- UI kits and design system templates
- Branding kit templates
- Mockup previews, product covers, and section breakdowns
- Responsive preview layouts and template overview pages

For Figma website templates, load `.design-brain/FIGMA_OUTPUT_TARGET.md`, `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md`, `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`, `.design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md`, and `.design-brain/VISUAL_CRITIQUE_CHECKLIST.md`. If the user does not provide a different Figma target, create the working design file only when the configured project/file target is valid.

## Why It Runs First

A sellable template is not just a nice visual. It needs a clear buyer, niche, product category, reusable structure, editable placeholders, and preview system. The orchestrator prevents Codex from jumping straight into visuals or code before the product strategy is clear.

## Standard Structure Gate

The orchestrator must reject underbuilt templates before visual design starts.

- Originality from a reference is required, but originality is not enough.
- A clean visual mood is not a reason to reduce the number of sections, screens, pages, states, or reusable modules.
- Do not treat old task-specific omissions such as desktop-only, no components, no cover, no preview, or no mobile as persistent restrictions. Decide output formats from the current request, product category, marketplace standard, and buyer value.
- For website templates, choose the product family and standard count before designing using `.design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.md`.
- For website templates, use `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md` and the local `Template Website` preview corpus to select product-family-matched reference evidence before choosing section map or rhythm.
- For Figma reference links or Figma template sources, use `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md` and produce a reference schema receipt before choosing structure. Study pages, frames, sections, components, variants, states, design-system panels, density rhythm, color/effect function, and product-family standard.
- For Figma source templates, require real auto-layout for editable sections, nav, CTAs, cards, forms, repeated rows, dashboards, responsive groups, and design-system panels before visual polish.
- Landing page must not be the fallback. It is valid only for explicit landing, campaign, lead-generation, sales page, squeeze page, or waitlist intent.
- If the user says Figma website template, website template, web template, SaaS website, business website, ecommerce, portfolio, blog, docs, dashboard, or similar without explicit landing-page language, route to the matching website product family.
- If the standard structure is uncertain, do web/category research before choosing the section map.
- A homepage-only desktop output must still prove product readiness through enough product-specific blocks and an explicit page-map/design-system scope.

Operational depth lock:

- Hero/header kit: 1-3 blocks only when explicitly requested.
- Landing page campaign: 6-10 sections depending on use case.
- Full website template: 8-14 meaningful sections/blocks minimum.
- SaaS/product website: 9-14 sections.
- Corporate/business/finance: 8-12 sections.
- Ecommerce/storefront: 10-16 sections or multi-page/module map.
- Restaurant/hospitality: 8-12 sections.
- Portfolio/agency: 7-12 sections.
- Editorial/blog/CMS: 8-12 sections plus content/archive logic.
- Dashboard/admin, UI kit, presentation deck, and mobile app must use screen/module/state/component/slide/flow coverage instead of website section counts.

## What It Connects

The orchestrator connects:

- Template Product Intelligence for product type, buyer, niche, and marketplace category
- Figma Output Target and Figma Auto-Layout Enforcement when the output is a Figma website template
- Template Style Router for selecting relevant TypeUI-derived style packs
- Template Product Quality Gate for marketplace readiness checks
- Template planner logic for sections, components, editability, and preview direction
- Review and visual review commands for critique after implementation
- Reflection commands for saving useful feedback as controlled lessons

## Pre-Build Design Simulation Gate

After orchestration produces a proposed structure, run the MiroFish-style Design Simulation Layer before building. This converts the plan into a design context graph, sends it through a fixed critique panel, and writes a structured verdict.

```bash
python scripts/design_brain_design_simulate.py \
  --task "..." \
  --template-type "..." \
  --niche "..." \
  --target-buyer "..." \
  --visual-mood "..." \
  --marketplace "Envato" \
  --proposed-structure "PROPOSED_STRUCTURE_SUMMARY" \
  --reference-summary "REFERENCE_DNA_AND_DO_NOT_COPY_BOUNDARY"
```

The simulation verdict must be read before build:

- `PASS`: build may start.
- `REVISE`: revise structure, visual language, preview system, source-template scope, or originality strategy and rerun.
- `BLOCKED`: do not build; the plan is too thin, generic, similar, legally risky, or not marketplace-ready.

For batch template work, pass accepted prior fingerprints with `--prior-fingerprint-file` so the newer template cannot reuse the same scaffold.

## Usage

```bash
python scripts/design_brain_template_orchestrate.py --template-name "Vowcraft Atelier" --template-type "landing-page" --niche "wedding-planning" --target-buyer "wedding planners and event studios" --visual-mood "elegant premium editorial" --marketplace "Envato Elements / Figma template marketplace" --preview-type "section breakdown overview and perspective mockup" --notes "Plan a marketplace-ready editable wedding planning landing page template"
```

Use `--dry-run` to print the report without saving.

## Style Routing Rule

Do not blindly combine all TypeUI skills. Pick a focused style strategy:

- One dominant style
- One or two supporting styles
- A clear preview direction
- Explicit conflicts to avoid

TypeUI-derived skills are style references and design constraints, not raw prompts to merge indiscriminately.

## Product Strategy Rule

Do not treat visual style as product strategy. The template must answer:

- Who buys this?
- What product category is it?
- For website templates, which of the 16 Figma website product families is it?
- What sections or components are required?
- What is the standard section/page/screen count for this product type?
- If a Figma reference is used, what exact file/page/frame/component/state scheme was observed before deciding the standard?
- Which required buyer-journey questions must each section answer?
- What can the buyer edit?
- What preview proves the value?
- What quality gate makes it marketplace-ready?

Run the orchestrator before designing, then use review and visual review reports before finalizing.

## Multiple Template Rule

For multiple-template or batch tasks, the orchestrator is not a single global batch planner. Use `.design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md` first.

Run or mentally follow orchestration inside each template cycle:

1. Select and study the next active product-purpose reference group for the current template. Use up to 10 varied references when enough matching candidates exist.
2. Infer purpose, buyer, audience, structure, visual logic, and do-not-copy boundaries.
3. Orchestrate the current template only.
4. Build the current template to completion.
5. Lock the used pattern before starting the next template.

Do not reuse one orchestration report as the structural scaffold for every template in a batch.

## Reference, Naming, And Build Memory

If the user provides a reference, run the Reference Insight workflow before orchestration:

```bash
python scripts/design_brain_reference_insight.py --reference-name "..." --lesson "..." --do-not-copy "..." --reinterpretation "..." --dry-run
```

The reference insight should define what was learned, what must not be copied, and how the structure should be reinterpreted. Do not start orchestration from copied reference layout.

When a reference is provided, reference insight workflow must happen before orchestration.

Before choosing the final template name, run the naming check:

```bash
python scripts/design_brain_name_check.py --candidate-name "..." --niche "..." --template-type "..." --dry-run
```

After a template product direction is accepted, save a build record:

```bash
python scripts/design_brain_build_record.py --template-name "..." --template-type "..." --niche "..."
```

Build records and naming ledger entries make future template work less repetitive and help prevent recycled names, suffixes, metaphors, section structures, and preview systems.

When a name is chosen, the naming ledger must be checked before finalizing.

## Sequential Layout Originality Step

Before build, orchestration must produce or import a candidate layout fingerprint. For reference-led work, it must also identify the reference layout fingerprint. For batch work, it must load previous locked AI fingerprints from the active build session.

No orchestration result is ready for build until the candidate passes the reference-vs-AI layout audit and, for Template 2 and beyond, every AI-vs-previous-AI pairwise layout audit.
