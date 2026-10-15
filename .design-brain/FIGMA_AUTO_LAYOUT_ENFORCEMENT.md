# Figma Auto-Layout Enforcement

This is the active source-of-truth rule for Figma template construction.

This rule handles how the output is built. When a Figma link, frame, or template source is used as the reference input, load `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md` first to study the reference scheme before deciding the new structure.

This rule is global for every Figma, source-template, editable UI, and Figma-like output. It is not limited to website-template routes.

## Post-Build Source Hygiene Audit

After Figma/source builds, run the post-build source hygiene audit:

- verify auto-layout on major layout frames
- verify section groups
- verify component variants
- verify text editability
- verify image placeholder replaceability
- verify component naming
- verify constraints/responsive behavior
- generate Figma/source hygiene receipt

Do not claim Figma source ready if:

- auto-layout is missing in core components
- layers are unnamed or generic
- text is flattened
- image placeholders are not replaceable
- component states are missing
- design system is missing
- source hierarchy is confusing

## Mandatory Rule

Every Figma design template must be built with real auto-layout for editable structure. Manual coordinate layout is allowed only for documented decorative or overlay exceptions. A Figma template without auto-layout is an unfinished source template.

## What Must Use Auto-Layout

- Page-level content stacks and major section frames.
- Navigation, buttons, CTAs, badges, tabs, menus, filters, forms, and repeated control rows.
- Cards, pricing blocks, metric rows, testimonial blocks, FAQ rows, profile blocks, feature modules, and content grids.
- Dashboard shells, sidebars, topbars, table rows, filter bars, chart legends, status rows, and detail panels.
- Design-system documentation panels, token boards, component notes, and responsive preview groups.
- Mobile/desktop variants whenever resizing, stacking, or editing behavior matters.
- Desktop, tablet, and mobile responsive variants or responsive preview frames for website templates when marketplace/source value depends on responsive behavior.

## Responsive Preview Default

Do not create desktop/tablet/mobile responsive preview boards by default for a single Figma website/template request. Responsive behavior still must be planned and documented, but visible responsive preview boards are opt-in unless the user explicitly asks for them, the task is a preview package, or the delivery contract requires them.

When preview boards are omitted, spend the design effort on stronger source design-system coverage instead of shorter output.

## Design System Auto-Layout Standard

Design-system boards must use auto-layout and must not collapse into minimalist token receipts. A compact board is acceptable only when it includes functional system depth: foundations, component anatomy, variants/states, reusable section modules, usage logic, placeholder behavior, surface/effect roles, and source-editing notes.

## Per-Template Design System Layout Rule

For multi-template Figma/source packs, each template's design-system frame/page/section must be built as its own editable auto-layout artifact. Do not place all template design systems into one combined frame unless that frame is explicitly a pack-level audit summary.

Template N+1 is blocked until Template N's design-system artifact exists, is editable, and passes the per-template design-system receipt/check. A main template page without its design-system board is not a finished batch item.

Each separated design-system artifact should have:

- its own named outer auto-layout frame/page/section
- intentional padding, spacing, resizing behavior, and readable hierarchy
- component specimens and token boards that belong to that template
- no clipped labels, crowded rows, or rough placeholder alignment before final delivery

Final output is blocked until every separated design-system artifact has been screenshot-inspected or visually inspected and tidied.

## Required Figma API Behavior

- Set `layoutMode` on editable frames.
- Set `itemSpacing`, `paddingTop`, `paddingRight`, `paddingBottom`, and `paddingLeft`.
- Set `primaryAxisAlignItems` and `counterAxisAlignItems` intentionally using valid Figma Plugin API enum values.
- Use `.design-brain/FIGMA_API_COMPATIBILITY.md` before Figma execution. Do not use CSS/Flexbox alignment values such as `START`, `END`, or `STRETCH` in Figma API assignments. Use `MIN` for start, `MAX` for end, `CENTER` for center, `SPACE_BETWEEN` only on the primary axis, and child sizing `FILL` for stretch behavior.
- Set child sizing with `layoutSizingHorizontal` and `layoutSizingVertical` using `HUG`, `FILL`, or `FIXED` as appropriate.
- Use named frames that reveal edit purpose, not only visual placement.

## Exception Rule

Absolute positioning may be used for:

- ambient decorative backgrounds
- non-editable gradients, glow layers, texture, or shape motifs
- intentional badge/mockup/callout overlays
- preview-only image compositions

These exceptions must be noted in an auto-layout receipt. They cannot become the main page structure.

## Required Receipt

Every substantial Figma template must include these receipts in the design notes, review report, or system guide:

- Auto-layout receipt: page or section frames using auto-layout, reusable components using auto-layout, responsive/resizing assumptions, and decorative absolute-position exceptions.
- Figma API alignment receipt: confirmation that `primaryAxisAlignItems` and `counterAxisAlignItems` used Figma API values (`MIN`, `CENTER`, `MAX`, `SPACE_BETWEEN`, `BASELINE`) and no invalid conceptual `END` assignment was sent to Figma.
- Layer/component naming receipt: how sections, modules, reusable parts, and design-system notes are named.
- Placeholder receipt: how image and profile slots use `image placeholder: [purpose]` and `profile photo placeholder: [role]`.
- Responsive/editability note: how buyers can resize, stack, or adapt the source.
- Responsive behavior receipt: desktop, tablet, and mobile behavior plan or explicit reason a narrower preview scope is acceptable.
- Source hygiene note: what remains editable and what is decorative or preview-only.
- Per-template design-system receipt for multi-template packs: separate frame/page/section name, owner label, node ID when available, and visual inspection/tidy status.
- Design-system depth receipt: component anatomy, variants/states, reusable section modules, usage rules, and effect/surface tokens included; if absent, the board is a token receipt and not a complete design system.

## Fail Conditions

Fail the design or plan when:

- Figma template work does not mention auto-layout.
- The build uses manual x/y positioning as the primary layout system.
- Editable groups are drawn as flat shapes or screenshots.
- Cards, nav, buttons, pricing, FAQ, testimonials, dashboards, or design-system panels are not built as editable grouped structures.
- The final report claims Figma source-template quality without an auto-layout receipt.
- A reference-led website template ignores desktop/tablet/mobile behavior without an explicit small-scope reason.
- A multi-template pack uses one combined design-system frame as the source of truth for all templates.
- A separated design-system frame is visibly cramped, clipped, or not tidied after screenshot/visual inspection.
- Generated Figma code assigns `primaryAxisAlignItems` or `counterAxisAlignItems` to `END`, `START`, or `STRETCH` instead of the Figma API values defined in `.design-brain/FIGMA_API_COMPATIBILITY.md`.
