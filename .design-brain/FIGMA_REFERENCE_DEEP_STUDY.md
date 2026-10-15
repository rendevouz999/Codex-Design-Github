# Figma Reference Deep Study

This is the active source-of-truth rule for learning from Figma design-template links.

## Purpose

When a user provides a Figma design, Figma template link, Figma file, Figma frame, or asks Codex to learn from a Figma reference, Codex must study the reference as a complete template system before planning a new design.

The goal is not to copy the Figma reference. The goal is to understand its product family, commercial standard, page/frame scheme, section logic, component system, density rhythm, and editable source behavior so the new template can be reconstructed with original structure and marketplace-ready depth.

For Figma website template work, also apply `.design-brain/WEBSITE_REFERENCE_PROMPT_LOCK.md`. The reference is Style DNA and product-standard evidence, not a visual layout mold.

Use `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md` as the mandatory professional reading protocol. Use `.design-brain/FIGMA_REFERENCE_LEARNING_CORPUS.md` when the task needs the user-provided Figma learning-material links.

## Mandatory Deep-Study Behavior

Before creating a design from a Figma reference, Codex must inspect or infer:

- product purpose and niche before visual styling
- visual direction and art-direction category
- file, page, frame, and node scope studied
- product family and marketplace category
- observed pages, frames, sections, components, variants, states, and design-system areas
- whether the reference is a landing page, full website template, dashboard/admin, ecommerce, portfolio, agency/studio, UI kit, brand kit, deck, or another template product
- visible structure count and density rhythm
- expected standard structure for that product type
- page map, screen map, state map, or component map when the product type requires one
- typography hierarchy and content role system
- color-role logic without copying exact colors
- effect language, surface depth, shadow, blur, glow, border, overlay, or deliberate restraint
- imagery and placeholder logic
- component style, interaction possibility, and reusable state logic
- spacing rhythm and proportion logic
- content logic: headline, CTA, proof, objections, pricing/package, footer completeness
- responsive behavior plan for desktop, tablet, and mobile when relevant
- Figma source hygiene: layer naming, section frames, auto-layout, components, variants, styles, and editability
- visual uniqueness/signature and default-template syndrome risks
- auto-layout/source-template implications when the output is Figma
- what can be learned without copying recognizable execution
- whether the new website template plan reaches at least 9 meaningful sections by default, unless the user explicitly requested a small-scope product

Use available Figma tools and evidence when possible: metadata, design context, screenshots, frame tree, component names, layer names, page names, variants, and rendered visual inspection. If only a link or partial access is available, state what evidence is missing and use category standards or a targeted question instead of defaulting to a minimalist assumption.

## Reference Schema Receipt

Before building from a Figma reference, Codex must produce a short internal or visible receipt containing:

1. Figma reference scope: file/page/node/frame studied.
2. Product family and marketplace role.
3. Observed scheme: pages, frames, sections, components, states, variants, and design-system panels.
4. Standard inference: normal section/page/screen/state depth for the product family.
5. Professional reading: niche, visual direction, section logic, grid, typography, color roles, image direction, component style, spacing rhythm, visual signature, content logic, responsiveness, and Figma source hygiene.
6. Designer cognition: attention, emotion, trust, density, proof, and conversion logic.
7. Color and effect interpretation: what the reference colors/effects are doing, and how the new template will reconstruct them differently.
8. Do-not-copy boundary: exact visual, structural, color, section-order, and component-grouping details that must not be repeated.
9. Reconstruction plan: the new structure, rhythm, and content logic to build instead.
10. Uncertainty handling: category research, local corpus lookup, or targeted user question if the standard is still unclear.

## Anti-Minimalist Fallback Rule

Unknown standard does not mean minimalist.

Codex must not call a rich or unclear Figma reference "minimalist", "simple", "basic", "thin", or "5-section" unless the Figma evidence supports that product scope. If the category standard is unclear, Codex must do one of these before planning:

- classify the product family with the website/template taxonomy
- inspect more Figma pages, frames, or screenshots
- use `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md` and local `Template Website` evidence for website templates
- use medium/product playbooks for dashboard, UI kit, deck, brand kit, ecommerce, portfolio, or marketplace preview work
- ask one targeted question if evidence cannot be accessed

A clean visual style may be restrained. The product structure may not be underbuilt because Codex is unsure.

For website, web-template, Figma website-template, or standard landing-page references, fewer than 8 meaningful sections is not competitive unless the reference and brief explicitly indicate a small-scope product such as a hero/header kit, micro landing page, narrow campaign, squeeze page, or waitlist page. Minimalist visual mood is never evidence by itself.

## Originality Boundary

Learning from a Figma reference is allowed. Copying is not.

Do not copy:

- exact page/frame order
- exact hero grammar
- exact section order
- exact component grouping
- exact card cadence
- exact color palette, hex values, gradients, glow colors, or CTA/background role mapping
- exact typography pairing and scale
- exact media placement
- exact visual motif
- exact design-system panel order
- exact scaffold or page-builder pattern
- exact asset treatment or placeholder behavior

Reconstruct:

- product-standard depth
- buyer confidence logic
- density rhythm
- proof and conversion strategy
- information hierarchy
- editable component needs
- source-template page/screen/state coverage
- color function with a new palette role map
- effect function with a new surface-depth grammar
- desktop, tablet, and mobile responsive behavior
- mini design system that supports color, typography, spacing, button, card, form, icon direction, component states, placeholder rules, and source hygiene

## Multi-Reference And Batch Behavior

For multiple Figma references or multiple requested templates, run this deep study per reference cycle.

Do not study one Figma template and use it as the master scaffold for all outputs. Do not globally summarize several Figma references and then build sibling templates. Each accepted output must have its own reference schema receipt, structure fingerprint, visual-language fingerprint, auto-layout receipt when applicable, and pairwise audit against previous outputs.

## Fail Conditions

Fail the plan or critique when:

- a Figma reference is used without a reference schema receipt
- the reference was not read through the professional template learning order: purpose, visual direction, section structure, grid, typography, color roles, image direction, component style, spacing rhythm, signature, content logic, responsive behavior, and Figma source hygiene
- the plan jumps to a generic hero/features/pricing/FAQ/footer structure
- the plan calls the reference minimalist/simple/basic without evidence
- the standard product structure is uncertain but Codex proceeds with a short safe layout
- nested pages, component sets, variants, states, or design-system frames are ignored
- exact reference colors, gradients, CTA/background roles, or hero grammar are copied
- the output is a Figma source template but auto-layout requirements are missing
- the new design is visually different but below the product category's normal page/screen/section/state depth
