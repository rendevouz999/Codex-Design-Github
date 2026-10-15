# Section Layout Extraction Library

This layer turns reference study into a section-level layout vocabulary.

It does not create reusable page scaffolds. It extracts single-section layout
patterns, records why each pattern works, and lets future template builds choose
section patterns with enough accuracy, density control, and originality to avoid
flat or sibling-like layouts.

## Position In Workflow

Use this layer after Reference Insight and Designer Cognition, before Template
Orchestration, Design Simulation, and Layout Fingerprint.

Required order for reference-led website, Figma/source-template, marketplace,
batch, anti-generic, anti-flat, anti-identical, or layout-stiffness work:

1. Product family classification.
2. Reference Insight and Designer Cognition.
3. Section Layout Extraction Library lookup or extraction.
4. Section Layout Matching Gate.
5. Hyper-Accuracy Gate.
6. Template Orchestration and Design Simulation.
7. Layout Fingerprint and Layout Similarity Audit.
8. Build, visual review, post-build audit, and completion receipt.

If this layer conflicts with `.design-brain/WEBSITE_REFERENCE_PROMPT_LOCK.md`,
the prompt lock still owns the no-copy boundary and minimum website-template
completeness floor. This layer only expands section-level layout options.

## Core Rule

The catalog is layout vocabulary, not a scaffold.

Allowed:

- Select a section pattern because its purpose, anatomy, density, hierarchy, and
  buyer effect match the new product.
- Recombine patterns from different section categories into a new structure.
- Transform the section silhouette, focal path, component logic, color roles, and
  media placeholder treatment for a new original template.

Forbidden:

- Copying a reference section directly.
- Reusing one catalog pattern mix across multiple templates.
- Treating catalog sections as a fixed page builder.
- Using a section pattern with `qualityStatus` other than `PASS`.
- Ignoring density limits and then calling a crowded or empty section premium.

## Catalog Shape

The physical catalog lives in:

`.design-brain/section-layout-library/`

Required section folders:

- `hero`
- `navigation`
- `trust-band`
- `features`
- `services`
- `process`
- `stats-proof`
- `portfolio-gallery`
- `case-study`
- `pricing-packages`
- `testimonials`
- `faq-objection`
- `contact-booking`
- `cta`
- `footer`
- `dashboard-preview`
- `commerce-grid`
- `blog-resources`

Each folder contains:

- `README.md` for the section role and density standard.
- `index.json` with stable catalog metadata.
- `patterns/` for hyper-accuracy PASS patterns only.

Candidate patterns from automated extraction must go to:

`.design-brain/section-layout-library/_incoming/`

They may not move into a stable section folder until the Hyper-Accuracy Gate
passes.

Duplicate and near-duplicate evidence is recorded in:

`.design-brain/section-layout-library/_incoming/_matches/`

## Required Pattern Schema

Each section pattern must include:

- `patternId`
- `sectionType`
- `sourceRefs`
- `productFamilies`
- `commercialPurpose`
- `purposeLayer`
- `anatomyLayer`
- `hierarchyLayer`
- `gridRhythmLayer`
- `densityLimitLayer`
- `originalityLayer`
- `usageRuleLayer`
- `layoutGesture`
- `sectionSilhouette`
- `compositionTension`
- `focalPath`
- `negativeSpaceShape`
- `depthLayering`
- `moduleScaleVariation`
- `breakoutBehavior`
- `contentLimits`
- `antiCopyBoundary`
- `compatibleBeforeAfter`
- `structuralSignature`
- `matchStatus`
- `matchScore`
- `matchGroupId`
- `duplicateOf`
- `variantOf`
- `matchingEvidence`
- `dedupeDecision`
- `confidence`
- `qualityStatus`

Use `.design-brain/section-layout-library/pattern-schema.json` as the
machine-readable schema, `.design-brain/SECTION_LAYOUT_MATCHING_GATE.md` as the
dedupe gate, and `.design-brain/SECTION_LAYOUT_HYPER_ACCURACY_GATE.md` as the
quality gate.

## Density Limit Standards

- Hero: 1 primary message, 1-2 CTA, 1 proof cue, 1 controlled media system.
- Features/services: 3-6 primary modules; 7-8 only when grouped with hierarchy.
- Process: 3-6 steps.
- Pricing/packages: 2-4 tiers.
- Testimonials: 2-6 visible items; wall or carousel only with hierarchy.
- FAQ/objection: 5-8 useful objections.
- Footer/contact/CTA: product-fit closure, not a repeated generic dark footer
  slab.

These limits are standards, not excuses for minimalism. If the reference category
needs richer detail, group the content with hierarchy instead of making the
section either empty or noisy.

## Selection Rules

Before a template build, select section patterns by:

- product family
- section role
- buyer decision point
- density need
- layout gesture
- section silhouette
- compatibility with adjacent sections
- prior template pattern locks

The selected mix must be recorded in the layout fingerprint:

- `sectionPatternMix`
- `sectionPatternIds`
- `sectionDensityLimits`
- `catalogDivergenceNotes`

For batch work, Template N+1 must not reuse Template N's recognizable section
pattern mix, hero grammar, section silhouette sequence, closure grammar, or
focal-path behavior.

## Automation

Use:

```bash
python scripts/design_brain_section_layout_extract.py extract --source "Template Website" --new-source "references/new" --mode hybrid --output .design-brain/section-layout-library
python scripts/design_brain_section_layout_extract.py validate --catalog .design-brain/section-layout-library
python scripts/design_brain_section_layout_extract.py match --candidate candidate.json --catalog .design-brain/section-layout-library --json
python scripts/design_brain_section_layout_extract.py select --product-family saas --section hero --density balanced --exclude-fingerprint previous.json
```

Extraction is evidence gathering. Selection is blocked unless a pattern is
stable and `qualityStatus` is `PASS`.

Matching runs during extraction. Exact duplicates are not written as new
patterns; near duplicates create match receipts; variants keep `variantOf`; new
patterns enter `_incoming` as review material.
