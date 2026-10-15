# Subagent Orchestration Layer

## General production runtime boundary (2026-10-12)

Activate only for actual custom-plugin work. `PRODUCTION_EXECUTION_POLICY.md` and `HOST_DESIGN_PRODUCTION_SPECIALIST.md` select exactly Main plus one `gpt-6.1-sol` (Codex host) / `claude-opus-5-5` (Claude Code host) **General Design Production Engineer**. All role lists below are review responsibilities divided between those two participants, not permission to spawn a panel. Main has auto-full trust to judge PASS/REVISE and request repairs from the same Engineer. No extra reviewer, recursive delegation or concurrent SDK worker. An explicitly selected SDK route replaces the host worker and retains its own technical limits. Never fabricate separate agent execution to fill receipts.

This layer turns Brain Design subagents into accountable design gates, not cosmetic personas.

Subagents are reasoning roles with evidence requirements, receipt outputs, and blocking authority. Their job is to help Codex build website design templates with stronger reference reading, Style DNA extraction, product architecture, design-system depth, visual validation, originality control, Figma source quality, and marketplace readiness.

## Core Rule

Subagent = reasoning role + evidence producer + gate authority.

Do not treat a subagent as a chat label. Each active subagent must have:

- role definition
- required input contract
- required output/receipt contract
- phase ownership
- blocking authority
- PASS / REVISE_REQUIRED / BLOCK status
- evidence path when claiming completion

## Source Files

- `.design-brain/design-subagents/agents.json`
- `.design-brain/design-subagents/subagent-schema.json`
- `.design-brain/design-subagents/orchestration-receipt-schema.json`
- `.design-brain/design-subagents/semantic-validation-rules.json`
- `.design-brain/design-subagents/semantic-validation-schema.json`
- `.design-brain/templates/SUBAGENT_ORCHESTRATION_RECEIPT.md`
- `scripts/design_brain_subagent_orchestrate.py`
- `scripts/design_brain_subagent_receipt_validate.py`

## Required Core Subagents

1. Reference Visual Analyst
2. Style DNA Extractor
3. Brand & Reference Memory Guardian
4. Template Product Architect
5. Section Flow Strategist
6. Layout Composition Director
7. Design System Director
8. Visual Signature Builder
9. Figma Source QA
10. Originality & Similarity Auditor
11. Visual QA Inspector
12. Marketplace Readiness Judge

## Operating Modes

### Full Orchestration Mode

Required for:

- complete website templates
- Figma website templates
- marketplace-ready templates
- reference-led templates
- batch templates
- new template brands
- homepage plus inner-page products
- Design Craft / Brain Design production workflows

All 12 core review responsibilities are active; Main and the single Engineer perform them without additional agents.

### Standard Mode

Required for:

- single landing page
- homepage concept
- large section redesign
- design-system board work
- smaller marketplace-related template work

Required critical review responsibilities within the same two-person team:

- Brand & Reference Memory Guardian
- Reference Visual Analyst
- Style DNA Extractor
- Template Product Architect
- Design System Director
- Visual QA Inspector
- Marketplace Readiness Judge

### Lightweight Mode

Used for:

- copy updates
- naming tweaks
- color adjustment
- minor component edits
- small prompt-generation tasks

Lightweight work still uses intent/rule/source checks. If it uses a reference, creates a brand, edits Figma source, or claims marketplace readiness, the relevant critical review responsibility remains mandatory. This does not add an agent.

## Phase Pipeline

### Phase 0: Memory & Context Load

Load the user brief, Brain Design rules, reference usage registry, naming ledger, previous template fingerprints, Design Craft adapter output when available, and active build-session context.

Active gate:

- Brand & Reference Memory Guardian

### Phase 1: Reference Understanding

Active gates:

- Reference Visual Analyst
- Style DNA Extractor
- Originality & Similarity Auditor preliminary check

Required output:

- specific visual analysis
- Style DNA receipt
- do-not-copy boundary
- reinterpretation plan
- structural reconfiguration plan

### Phase 2: Product Architecture

Active gates:

- Template Product Architect
- Section Flow Strategist
- Layout Composition Director
- Visual Signature Builder

Required output:

- buyer logic
- product promise
- page/section architecture
- non-generic section flow
- layout grammar
- visual signature system

### Phase 3: Design System Planning

Active gates:

- Design System Director
- Figma Source QA preliminary check
- Visual Signature Builder review

Required output:

- token roles
- components
- states
- variants
- section modules
- image placeholder rules
- usage examples

### Phase 4: Build Execution

Builder may start only after reference usage, Style DNA, product architecture, section flow, layout composition, design-system plan, and visual signature plan are not BLOCK.

### Phase 5: Post-Build Visual Audit

Active gates:

- Visual QA Inspector
- Originality & Similarity Auditor
- Design System Director post-build audit
- Figma Source QA post-build audit

Required output:

- screenshot evidence
- visual QA report
- originality/similarity audit
- design-system depth check
- Figma source QA

### Phase 6: Final Marketplace Approval

Active gates:

- Marketplace Readiness Judge
- Brand & Reference Memory Guardian final record
- Build Session Final Verification

Final PASS is allowed only when all critical receipts exist, all critical review responsibilities pass, reference usage is recorded, completion receipt exists, fingerprint lock exists, and final screenshot evidence exists.

## Non-Minimalist Design-System Standard

Non-minimalist does not mean crowded. It means the design is not empty, generic, flat, or under-specified.

A marketplace template design system must include:

- product DNA for template category, target buyer, commercial purpose, visual mood, reference insight, and do-not-copy boundary
- token roles for color, surface, border, text, accent, state, and effect/gradient when used
- typography scale for display, heading, subtitle, body, caption, label, numeric/stat, and quote styles
- spacing rhythm for sections, cards, grids, dense modules, airy modules, and responsive changes
- component system with buttons, states, cards, forms, navbar, footer, CTA block, badge/tag, icon container, and image placeholder component
- product-specific modules for the template category, not just generic card specimens
- section modules for hero, trust/proof, value proposition, service/feature, showcase/gallery, testimonial, offer/pricing when relevant, FAQ, final CTA, and footer
- one to three visual signatures such as shape motif, image mask, section divider, floating proof card language, editorial number system, CTA motif, or premium surface treatment
- effect language for shadow depth, border behavior, overlay, blur/glass if used, image gradient overlay, hover behavior, and background texture/pattern if relevant
- usage examples showing component usage, variants, color role behavior, typography hierarchy, and spacing rhythm
- placeholder/media replacement rules, responsive/editability rules, package/source map, and source hygiene receipt
- board artifact metrics: Figma frame/page ID, screenshot/render evidence, panel count, component specimen count, product-specific module count, state example count, and board dimensions when available

If the design system only contains colors, fonts, a basic button, and a basic card, status must be REVISE_REQUIRED or BLOCK for marketplace template work.

If the design-system board is a compact style summary instead of a buyer-usable product kit, status must be BLOCK for marketplace website/Figma/source-template work. Compact boards that can be produced by title/color swaps across batch items are considered design-system scaffold reuse.

## Visual Evidence Rule

Visual QA must inspect screenshots when output exists. Do not claim marketplace-ready final status when no screenshot, Figma inspection, or rendered visual evidence was reviewed.

Visual QA must check:

- hero strength
- hierarchy
- spacing and density
- section rhythm
- visual depth
- color and contrast
- component polish
- marketplace feel
- clipping, overlap, and source-visible roughness

## Semantic Receipt Rule

Final subagent validation must judge the content of receipts, not only whether files exist.

`scripts/design_brain_subagent_orchestrate.py` automatically runs `scripts/design_brain_subagent_receipt_validate.py` when `--final` and `--evidence-dir` are supplied. Placeholder text, invalid JSON, fake smoke files, weak design-system depth, missing screenshot evidence, unsafe originality scores, or marketplace verdicts that do not read critical receipts must block final delivery.

Use `.design-brain/SUBAGENT_RECEIPT_SEMANTIC_VALIDATOR.md` for the validator contract.

## Critical Blocking Rule

Final delivery must be BLOCK when:

- a critical subagent returns BLOCK
- a critical receipt is missing
- screenshot evidence is missing for visual template work
- design-system depth is missing
- reference usage is not recorded when references are used
- originality audit is not PASS
- Figma Source QA is not PASS for Figma source templates
- Marketplace Readiness Judge is not PASS for marketplace-ready claims
