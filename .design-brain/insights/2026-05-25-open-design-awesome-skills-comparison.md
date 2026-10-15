# Design Brain Comparison: Open Design + Awesome Claude Skills

Date: 2026-05-25

Compared local sources:
- `<CODEX_DESIGN_WORKSPACE>\.design-brain`
- `<CODEX_DESIGN_WORKSPACE>\open-design`
- `<CODEX_DESIGN_WORKSPACE>\awesome-claude-skills`

## Executive Summary

Design Brain is currently a strong design-cognition and critique layer: it remembers taste, routes template work, deconstructs references, checks originality risk, and captures user feedback. It is especially tuned to the user's marketplace-template needs and the recurring failure mode of outputs becoming too identical to references.

Open Design is different: it is a full artifact runtime and design product system. It has a daemon, project/artifact model, interactive discovery forms, skill registry, design-system library, craft modules, seed templates, preview contracts, and partial linting. It teaches an agent how to ship rendered artifacts inside a structured product loop.

Awesome Claude Skills is different again: it is a broad skill marketplace/corpus. Its biggest value for Design Brain is not design taste, but packaging discipline: small `SKILL.md` units, progressive disclosure, scripts/references/assets, black-box helper scripts, validation utilities, and reusable capability patterns such as PPTX, PDF, webapp testing, theme factory, canvas design, and skill creation.

The main upgrade opportunity is to turn Design Brain from "excellent design memory + planning docs" into "design intelligence with modular skill/craft injection, seed artifacts, deterministic checks, and corpus-aware routing."

## Structural Differences

### Design Brain

Observed shape:
- 179 files inside `.design-brain`.
- Mostly Markdown and JSON.
- Core layers: identity, memory, preferences, template taxonomy, medium playbooks, originality scorecard, review templates, reflection, naming ledger, style packs, TypeUI extracted profiles.
- Scripts act as planners, routers, report generators, status checks, originality dry-runs, reference insight writers, and reflection tools.

Strength:
- User-specific and workflow-specific.
- Strong at "do not copy references".
- Strong at marketplace-template reasoning.
- Strong at preserving lessons from feedback.
- Strong at medium/product-type diagnosis after the advanced upgrade.

Gap:
- Few concrete seed templates or layout assets.
- No artifact runtime or preview contract.
- No per-medium `assets/template`, `references/layouts`, and `references/checklist` pack.
- No automatic rendered-output linter comparable to Open Design's lint artifact approach.
- No large reusable design-system library with tokenized `DESIGN.md` + `tokens.css` + component examples.

### Open Design

Observed shape:
- 4,745 non-git files.
- Large app/runtime repo with `apps`, `plugins`, `design-templates`, `design-systems`, `skills`, `craft`, `packages`, `tools`, `prompt-templates`, `docs`, and `e2e`.
- 422 `SKILL.md` files found across the repository.
- `craft/` contains universal craft rulebooks: typography, color, anti-AI-slop, state coverage, animation discipline, accessibility baseline, forms, RTL/bidi, laws of UX.
- `design-systems/` stores brand/product design systems with `DESIGN.md`, `tokens.css`, and `components.html` examples.
- `apps/daemon/src/skills.ts` scans `SKILL.md` frontmatter and supports metadata such as `mode`, `platform`, `scenario`, preview type, design-system requirements, craft requirements, and critique policy.
- `apps/daemon/src/prompts/directions.ts` has deterministic visual direction specs with palette, font stack, references, and posture rules.
- `design-templates/*` often use seed templates, layouts, and P0/P1/P2 checklists.

High-value ideas for Design Brain:
- Add a third axis like `craft/`: universal design craft modules separate from medium playbooks and style packs.
- Let product-type playbooks declare required craft modules.
- Add deterministic direction packs with concrete tokens, fonts, posture, and anti-patterns.
- Add seed artifacts and checklists per medium.
- Add machine-checkable anti-generic rules where possible.
- Add skill/capability registry metadata so Design Brain can load only relevant modules.

Potential mismatch:
- Open Design is HTML-artifact and runtime oriented; Design Brain often needs Figma, template products, design-system frames, PowerPoint thinking, and marketplace outputs.
- Open Design's first-turn discovery form pattern may be too interruption-heavy for this user's preference when enough context already exists.
- Open Design's broad design systems are useful as style references but should not replace the user's originality constraints.

### Awesome Claude Skills

Observed shape:
- 1,142 non-git files.
- 864 `SKILL.md` files, mostly from app automation plus selected practical skills.
- Strong examples of `scripts/`, `references/`, and `assets/` as progressive-disclosure resources.
- PPTX skill includes deep Office Open XML workflows, template inventory, thumbnail validation, `html2pptx`, rearrange, replace, inventory, pack/unpack, and validation scripts.
- Webapp testing skill uses black-box helper scripts and browser validation.
- Canvas design skill uses a philosophy-first visual process.
- Theme factory packages reusable palettes/font pairings for multiple artifacts.
- Skill creator explains skill design, validation, packaging, and iteration.

High-value ideas for Design Brain:
- Package advanced Design Brain modules as skills with progressive disclosure.
- Add deterministic scripts for repeated tasks instead of re-explaining workflows.
- Add black-box visual validation helpers for Figma screenshots, web previews, PPTX thumbnails, and layout overlap checks.
- Add a theme/direction showcase layer for fast selection and comparison.
- Add import/analyze workflows for PPTX, PDF, screenshots, and web pages using dedicated scripts.

Potential mismatch:
- Many skills are not design-related or are automation connectors.
- Quality varies because it is an awesome-list corpus.
- It does not provide one coherent design taste or originality guard.

## Capability Matrix

| Capability | Design Brain | Open Design | Awesome Claude Skills |
| --- | --- | --- | --- |
| User-specific design memory | Strong | Weak/general | Weak/general |
| Reference deconstruction | Strong | Medium | Weak |
| Originality/similarity scoring | Strong | Medium anti-slop, less reference-specific | Weak |
| Medium/product routing | Strong after advanced upgrade | Strong via skill modes/scenarios | Medium via skill descriptions |
| Design-system library | Small/curated TypeUI and style packs | Large `DESIGN.md` + tokens + components library | Small, scattered |
| Skill registry metadata | Limited | Strong `od` frontmatter | Strong basic `SKILL.md` pattern |
| Seed templates/layout assets | Limited | Strong | Medium depending on skill |
| Craft rule modules | Medium in docs | Strong separated `craft/` axis | Scattered |
| Automated lint/checks | Light dry-runs | Stronger, partial artifact linter | Strong in document/PPTX/PDF helper scripts |
| Artifact runtime | None | Strong | None |
| Figma/template marketplace tuning | Strong | Medium | Weak |
| PowerPoint technical workflow | Medium design intelligence | Deck HTML/runtime focus | Strong PPTX/OOXML tooling |
| Visual validation workflow | Report-based | Runtime + linter + preview | Script-based thumbnails/testing |

## Most Important Differences

1. Design Brain is a thinking system; Open Design is a production loop.
2. Design Brain stores rules; Open Design attaches rules to executable artifact skills.
3. Design Brain has originality guardrails; Open Design has anti-slop/lint guardrails.
4. Design Brain has style packs; Open Design has deterministic direction specs and full design systems.
5. Design Brain has reports; Awesome Claude Skills has reusable helper scripts and packaged task workflows.
6. Design Brain is tuned to this user's taste; the other two are broader and less personal.

## Upgrade Opportunities

### 1. Add a Design Brain Module Registry

Create a registry that indexes Design Brain modules by:
- medium
- product type
- niche
- task intent
- required craft modules
- required validation gates
- source files to load
- scripts to run

This would make Design Brain behave less like a pile of docs and more like a selective runtime.

### 2. Add a `craft/` Axis

Create `.design-brain/craft/` with compact modules:
- typography
- color
- spacing
- layout rhythm
- accessibility
- state coverage
- forms
- data visualization
- motion discipline
- marketplace preview
- originality anti-slop
- Figma auto-layout craft
- PowerPoint slide readability

Each medium playbook should declare which craft modules apply.

### 3. Add Seed Packs Per Medium

Create `.design-brain/seed-packs/`:
- `landing-page/`
- `dashboard/`
- `presentation-deck/`
- `ui-kit/`
- `brand-kit/`
- `marketplace-preview/`
- `portfolio/`
- `ecommerce/`

Each seed pack should include:
- `layouts.md`
- `checklist.md`
- `content-patterns.md`
- `design-system-scope.md`
- optional Figma JS snippets or HTML examples

This would reduce ad-hoc design decisions and improve consistency.

### 4. Add Deterministic Direction Packs

Upgrade style packs into concrete direction specs:
- palette tokens
- font pairing
- spacing posture
- surface rules
- imagery rules
- motif budget
- best-fit mediums
- do-not-use cases

The current Advanced Style Grammar Matrix is a good foundation, but it should become selectable structured data.

### 5. Add Automated Visual/Artifact Linting

Add scripts that check:
- too many accent uses
- one-note palette
- repeated section order
- raw hex outside tokens
- missing mobile frame/logic
- missing dashboard states
- missing deck slide roles
- text overflow risk
- inaccessible contrast
- default AI patterns such as purple/blue gradients, vague cards, filler metrics, generic CTAs

Design Brain already has originality scoring; it needs more rendered-output checks.

### 6. Add PPTX Technical Intelligence From Awesome Skills

For PowerPoint work:
- template inventory
- thumbnail grid validation
- OOXML-safe editing path
- slide index mapping
- placeholder inventory
- layout-to-content matching
- chart/table validation
- speaker notes/comments support

Design Brain's presentation intelligence is conceptually strong, but it can be upgraded with deterministic PPTX scripts.

### 7. Add Corpus Ingestion And Skill Selection

Build a script to ingest external design/skill repos and produce compact profiles:
- `open-design` skill modes and craft modules
- design-system names and categories
- reusable skill patterns
- anti-patterns and P0 checklist ideas
- relevant candidate modules for Design Brain import

This should be selective. Do not bulk-copy all external skills into Design Brain.

## Recommended Priority

1. **Design Brain Module Registry**: highest leverage because it lets the system load the right material without flooding context.
2. **Craft Axis**: second highest because it separates universal craft from product/medium rules.
3. **Seed Packs + Checklists**: directly improves output quality and reduces generic design.
4. **Automated Linting**: catches repeat failures before final delivery.
5. **PPTX Technical Tooling**: important for the user's PowerPoint-template direction.
6. **External Corpus Ingestion**: useful once the first four foundations exist.

## Principle For Importing From These Repos

Use these repos as teachers, not as material to blindly merge.

Design Brain should absorb:
- architecture patterns
- metadata schemas
- validation workflows
- seed/checklist discipline
- craft module separation
- deterministic direction thinking

Design Brain should not absorb:
- every skill
- every brand system
- runtime assumptions that only work for HTML artifacts
- generic discovery behavior that slows the user's preferred workflow
- source layouts or style outputs as copyable templates

## Practical Next Upgrade Plan

Phase 1:
- Add `.design-brain/registry/` with a module registry JSON.
- Add `.design-brain/craft/README.md` plus initial craft modules.
- Update `design_brain_context_packet.py` and `design_brain_medium_playbook.py` so they recommend craft modules.

Phase 2:
- Add seed packs for landing page, dashboard, presentation deck, marketplace preview.
- Update template orchestrator to reference seed packs and P0/P1/P2 checklists.

Phase 3:
- Add `design_brain_lint_artifact.py` and `design_brain_lint_template_plan.py`.
- Add checks for generic AI patterns, section repetition, missing states, and text/contrast risks.

Phase 4:
- Add `design_brain_external_corpus_index.py` to summarize external repos without permanently loading everything.
- Add PowerPoint inventory/thumbnail helpers inspired by the PPTX skill workflow.

## Bottom Line

Yes, there are meaningful differences.

Design Brain is already stronger than both repos at user-specific template judgment, reference reinterpretation, and originality control. But Open Design is stronger at runtime architecture, skill metadata, design-system libraries, seed templates, craft modules, and artifact validation. Awesome Claude Skills is stronger at reusable skill packaging, deterministic helper scripts, and document/PPTX tooling.

The best upgrade path is not replacing Design Brain. The best path is to keep its identity and originality layer, then add Open Design-style module architecture and Awesome Claude Skills-style reusable scripts/assets.
