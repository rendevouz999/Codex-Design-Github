# Mandatory Design System Build

Every built template must include a design system. A design system cannot be generic notes; it must be tied to the actual built template, product family, mode, components, and source/editability requirements.

## Anti-Empty Design System Rule

A design system fails if it is only a style summary, originality receipt, screenshot note, or a few color/component examples. A marketplace template design system must help the buyer edit, extend, and reuse the template.

For Figma/source templates, the design system page or frame must visibly include:

1. Foundation tokens: color roles, typography scale, spacing scale, grid/container rules, radius, border, and elevation/depth.
2. Component inventory tied to the actual template: navigation, buttons, cards, forms, CTA blocks, footer, media placeholders, proof/testimonial modules, and product-specific modules.
3. State coverage: default, hover/active or selected, focus, disabled, error/empty/loading when relevant.
4. Pattern modules: reusable section patterns or page blocks that a buyer can copy, rearrange, or adapt.
5. Placeholder/media guidance: what each image/profile/diagram placeholder is for and what replacement content should be used.
6. Source hygiene guidance: auto-layout behavior, naming conventions, editable text/media slots, and any limitations.
7. Accessibility/editing notes: contrast intent, touch/CTA sizing, readable type roles, and safe replacement rules.
8. Artifact evidence: Figma node summary, design system page/frame ID, component inventory, token source path, and screenshot/render proof when visual verification is claimed.
9. Reference-standard coverage: any structure, component depth, color behavior, effects, gradients, states, or source-system expectations learned from the reference must appear as editable foundations, specimens, patterns, or notes, not only in the main page.

10. Figma website-template best-practice coverage when the output is a website template: typography styles or named typography roles, color styles or named color roles, reusable component/module specimens, button states, card components and states, form/input examples, icon direction, responsive variants or responsive preview notes, clean placeholder image areas, and clearly named layers/sections.

Receipt-only design systems cannot produce final READY. A receipt may be included, but it cannot replace foundations, components, states, patterns, editability documentation, and artifact evidence. If only a receipt exists and no screenshot/render/Figma/source artifact proof is available, the final status must be READY_WITH_LIMITATIONS at best, or BLOCKED/REVISE_REQUIRED in strict final audit mode.

## Minimum Visible Coverage For Marketplace Website Templates

Unless the user explicitly asks for a tiny kit or narrow micro-template, a website/Figma template design system should include at least:

- 6+ color roles or semantic tokens
- 6+ typography roles
- 5+ spacing/layout tokens
- 4+ radius/elevation/depth rules
- 8+ actual template components
- 4+ state examples across interactive components
- 3+ product-specific reusable patterns
- a placeholder/media replacement guide
- an auto-layout/source hygiene receipt
- artifact evidence for source/component/token proof, plus screenshot/render evidence when visual verification is claimed
- a reference-standard note explaining how the design system supports the observed reference/category standard without copying it
- a mini design-system coverage block for color, typography, spacing, button, card, form, icon direction, component states, placeholder rules, source hygiene, and responsive behavior

These are minimums, not a target ceiling. Rich ecommerce, dashboard, editorial, hospitality, travel, furniture, portfolio, or marketplace products often need more.

## Product-Grade Website Design System Contract

For marketplace website, Figma website, editable source-template, and reference-led website-template work, the design system is a source product kit, not a minimalist style guide. It must be built as if the buyer will use it to edit, extend, and package the template without reverse-engineering the homepage.

The design-system board must visibly include these blocks:

1. Product DNA: template name, product category, target buyer, commercial purpose, visual mood, reference insight, and do-not-copy boundary.
2. Foundations: semantic color roles, typography roles, spacing scale, grid/container behavior, radius, border, elevation/depth, and gradient/effect rules when used.
3. Component inventory: reusable real components from the built template, not generic samples. Include navigation, buttons, cards, forms, CTA, footer, badges/tags, media placeholder, proof/testimonial, FAQ, and product/category-specific components.
4. States and variants: default, hover, active/selected, focus, disabled, error, empty/loading when relevant, plus category-specific states such as sale/sold-out/featured, recommended/neutral pricing, selected filter, selected size, or form error.
5. Product-specific modules: category modules that prove the system belongs to this template. Consultant templates need strategy/diagnostic/case/proof/process modules. Ecommerce templates need product cards, filters, cart/quick-add, category/room/shelf/product states, trust modules, and sale/stock states. SaaS templates need pricing, integration, dashboard/proof, workflow, and form/demo modules.
6. Reusable section patterns: buyer-copyable pattern blocks for hero, trust/proof, value/service/feature, showcase/gallery, testimonial, pricing/offer when relevant, FAQ, final CTA, and footer.
7. Placeholder and media rules: each image/profile/product/media slot must use role-specific text clues and replacement guidance such as `image placeholder: product image`, `image placeholder: room scene`, or `profile photo placeholder: client executive`.
8. Responsive and editability rules: desktop/tablet/mobile behavior, stacking rules, crop safety, CTA placement, auto-layout notes, layer naming, editable text/media slots, and Figma sizing semantics.
9. Visual-language rules: motif, shape system, image mask, divider, surface treatment, shadow/blur/glow, CTA behavior, decorative pattern, icon direction, and effect/gradient usage.
10. Usage examples: concrete examples showing component combinations, card grids, forms, product rows, testimonial/proof blocks, media placeholder blocks, pricing/offer blocks, and responsive notes.
11. Package/source map: included pages or sections, extension logic, cover/preview direction, source organization, and buyer-facing packaging notes.
12. Source hygiene receipt: auto-layout, editable text, editable placeholders, reusable components, clear layer names, responsive constraints, non-flattened important content, and final source limitations.

Hard block: if a marketplace website design-system board can be summarized as only color swatches, typography, buttons, cards, and generic rules, it is not a design system. It is a style summary and must fail.

Hard block: if the board does not visibly show product-specific modules, reusable section patterns, state examples, visual-language rules, placeholder/media guidance, package/source map, and source hygiene, final status cannot be READY.

Hard block: for Figma/source website templates, the receipt must include board metrics or equivalent artifact evidence: design-system frame/page ID, screenshot/render path, panel count, component specimen count, product-specific module count, state example count, and board dimensions when available. Missing board metrics means the audit is receipt-only and cannot pass strict final READY.

For reference benchmarks, KineticCast and QRYON-style boards are the expected depth class: not identical visually, but similarly product-grade in coverage. A compact receipt board around one screen of swatches/type/buttons is below standard for full marketplace website templates.

## Physical Separation Rule For Multi-Template Packs

When a Figma/source output contains multiple distinct templates, "each template has its own design system" means each template needs a physically separate design-system frame, page, or section that is visibly owned by that template. Separate variables, styles, or notes are not enough if the buyer sees only one combined board.

For every template in a multi-template pack, the design-system artifact must include:

- a top-level frame, page, or clearly separated source section named for that template
- template ownership metadata or an equivalent visible owner label
- token examples and component specimens that match that template's visual-language fingerprint
- product-specific pattern modules and placeholder guidance for that template
- a screenshot or visual inspection note for the specific design-system frame when final readiness is claimed

A pack-level source board, reference map, similarity matrix, or governance receipt is allowed, but it must be labeled as an audit summary only. It cannot satisfy the per-template design-system requirement, and it must not visually imply that all templates share one builder.

## Minimum Requirements

### 1. Color Roles and Tokens

- background
- surface
- surface elevated
- primary text
- secondary text
- muted text
- accent
- CTA/action
- border/divider
- success, warning, error, and info when relevant

### 2. Typography

- display
- h1, h2, h3
- body large, body/base, body small
- label/caption
- button/CTA text
- nav/menu text
- form text when relevant

### 3. Spacing

- spacing scale
- section vertical rhythm
- component padding
- card gap
- grid gap
- container width

### 4. Layout and Grid

- frame size
- responsive/container rules
- column/grid system
- section rhythm
- breakpoint behavior or responsive notes

### 5. Radius, Elevation, and Depth

- card radius
- button radius
- input radius
- shadow/elevation levels
- surface depth rule

### 6. Components

- button primary, secondary, tertiary
- cards
- navigation/header
- footer
- CTA block
- image/media placeholder
- form/input when relevant
- testimonial/proof component when relevant
- product card when ecommerce
- pricing card when pricing
- dashboard card/table/chart when dashboard
- slide components when presentation
- menu/item components when restaurant/menu

### 7. States

- default
- hover
- focus
- active/selected
- disabled
- error
- loading
- empty when relevant

### 8. Figma and Source Rules

- text editable
- placeholders editable
- source components reusable
- layer names clear
- auto-layout applied where appropriate
- no flattened important content
- source hygiene receipt required
- artifact evidence required for final READY:
  - Figma node summary path or design system page/frame ID
  - source component inventory or component inventory list
  - token source path
  - screenshot/render path when visual verification is claimed

### 9. Per-Template or Shared

- For a single template: one design system required.
- For batch templates with distinct visual directions: each template must have its own physically separate design-system frame/page/section or a clearly separated token variant inside an intentionally shared family.
- A shared design system is allowed only if the batch is intentionally one coherent family and differences are documented as variants.

## Product-Specific Requirements

- Restaurant/hospitality: menu item, reservation CTA, gallery/media, location/hours.
- Ecommerce: product card, category nav, cart/checkout when relevant, trust/shipping.
- Dashboard: KPI card, chart, table, filter, empty/loading/error states.
- Presentation: slide master, cover, section divider, content slide, data/chart slide, closing slide.
- Brand/static: logo, typography, color applications, export notes.
- UI kit/design system: tokens, component variants, state matrix, naming convention, accessibility states.

## Failure Conditions

Fail the design system check if:

- design system is missing
- tokens are generic and not tied to the template
- tokens/components ignore the reference/category standard and collapse into a minimal color-font-card board
- typography/spacing/components/states are absent
- product-specific components are absent
- source hygiene notes are missing
- important text or placeholders are not editable
- auto-layout/source hygiene is missing for Figma/source templates
- the design system is receipt-only and lacks buyer-usable foundations, components, states, patterns, or editability guidance
- artifact evidence is missing but the final response claims fully verified READY
- the design system feels visually empty because it has too few concrete component specimens or product-specific reusable modules
- multiple distinct templates are represented by one combined design-system board without separate per-template frames/pages/sections
- a later template starts while the previous template's design-system board is missing, invalid, receipt-only, or not visually checked
- the only separate artifact is a pack-level audit summary, reference map, or similarity receipt
- a per-template design-system frame is cramped, clipped, visually rough, or not screenshot-inspected before final output
- a reference-led Figma website template lacks button states, card components, form/input examples, placeholder guidance, responsive behavior notes, or named typography/color roles
