# Figma Auto-Layout Craft

Auto-layout is mandatory for Figma template source files. A template that relies on manual x/y positioning for editable structure is not complete, even when the visual screenshot looks polished.

Use real Figma auto-layout for:

- top-level section stacks and page content wrappers
- navigation bars, button groups, CTA rows, tabs, menus, and form rows
- cards, metric rows, pricing grids, FAQ rows, testimonials, profile blocks, and repeated content modules
- dashboard shells, filters, tables, chart legends, status rows, and detail panels
- design-system frames, token panels, component documentation, and responsive preview groups
- mobile and desktop variants that need predictable resizing behavior

Required implementation behavior:

- Set `layoutMode` on editable frames instead of manually placing every child by coordinate.
- Define padding, gap, primary/counter-axis alignment, and resizing behavior intentionally.
- Use `HUG`, `FILL`, and `FIXED` sizing semantics to make editing predictable.
- Name auto-layout frames by role, such as `Hero content stack`, `Pricing card auto-layout`, or `FAQ row`.
- Keep editable text, icons, cards, and image placeholders as real layers, not flattened screenshots.
- Keep design system tokens visible: color, type, spacing, radius, shadow, grid, and layout behavior.
- Include a short auto-layout receipt in the design notes, quality report, or system guide that names which groups use auto-layout.

Allowed exceptions:

- decorative background layers
- ambient glows, texture washes, crop overlays, and non-editable motifs
- intentional overlap systems such as badges, floating annotations, or mockup callouts
- exported preview imagery that is clearly not meant to be edited as source structure

Every exception must be intentional and documented. If a Figma API limitation blocks auto-layout, stop and report the limitation instead of claiming the template is complete.
