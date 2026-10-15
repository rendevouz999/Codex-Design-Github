# Platform Playbook

Use this reference after running the design corpus search, or when a platform requires translation from generic design direction into concrete implementation choices.

## Art Direction Pass

Before platform translation, choose one primary style profile and at most one secondary profile from [typeui-style-profiles.md](typeui-style-profiles.md). Do not blend more than two profiles unless the user explicitly asks for an experimental visual direction.

- Primary profile sets structure, typography, spacing, and component behavior.
- Secondary profile may influence imagery, surface treatment, or a single accent behavior.
- If profiles conflict, keep accessibility, platform conventions, and the user's brand assets above style novelty.

## Figma

- Start with variables: color, typography, spacing, radius, shadow, and motion notes.
- Build components before full screens when repeated UI exists. Include variants for size, state, density, and theme.
- Use auto layout, constraints, and named frames. Avoid fixed-position hacks unless the screen requires them.
- Prefer existing design system components when a Figma library is available.
- For handoff, include component names, token names, interaction states, and responsive behavior.

## PowerPoint

- Design the deck as a system: cover, section divider, content, comparison, metric, chart, image, quote, and closing layouts.
- Use a small type scale that survives projection. Avoid dense paragraph blocks; split content across slides when needed.
- Keep one idea per slide. Use contrast, size, and position to reveal the story.
- Define chart colors, callout style, image treatment, footer/page number rules, and title alignment.
- Validate in 16:9 and avoid text near edges. Slide content should still read at thumbnail size.

## Web, CSS, and Tailwind

- Convert the design system into CSS variables or framework theme tokens first.
- Use stable responsive constraints: grid tracks, max widths, aspect ratios, min heights, and clamp only for layout dimensions, not font scaling.
- Build semantic HTML, visible focus states, accessible labels, and keyboard-friendly interactions.
- Use real button/link semantics instead of clickable divs.
- Keep motion between 150ms and 300ms for common UI; avoid layout-shifting hover effects.

## WordPress

- Map global tokens to `theme.json`: palette, gradients only when justified, typography, spacing, border radius, and shadows.
- Use block patterns for hero, feature grid, testimonial, pricing, CTA, post list, and footer sections.
- Keep editor usability in mind: avoid CSS that makes blocks hard to select or rearrange.
- Put reusable layout rules in template parts and global styles; avoid page-specific CSS unless the pattern is unique.
- Check that responsive behavior works inside the block editor and the published front end.

## Dashboards and Data Products

- Prioritize scanability over decoration. Use dense but calm spacing, predictable navigation, and clear grouping.
- Show current state, trend, comparison, and next action where applicable.
- Design filters, sort, search, pagination, loading, empty, and error states as first-class UI.
- Use chart types based on the question: line for trend, bar for comparison, scatter for correlation, funnel for conversion, heatmap for distribution.
- Never rely on color alone. Add labels, legends, patterns, annotations, or direct values.

## Landing Pages and Marketing Templates

- Make the product, brand, venue, person, or offer visible in the first viewport.
- Put the primary CTA near the hero and repeat it after proof or comparison sections.
- Use social proof only when it is specific enough to be credible.
- Make the next section visible below the hero on common desktop and mobile viewports.
- Avoid explaining UI features in decorative text; show the value through the actual product, object, service, or outcome.

## Brand and Logo Work

- Test the mark at 16px, one color, light background, and dark background.
- Keep brand colors to primary, secondary, accent, and neutrals unless the brand system truly needs more.
- Use consistent icon stroke, corner radius, and illustration style.
- Show applications in context: favicon, header, card, slide cover, social avatar, and monochrome usage.

## Visual Review Prompts

Use these questions before final delivery:

- What is the single most important thing the viewer should notice first?
- Does the layout still work if the copy becomes 30 percent longer?
- Would a keyboard user or screen reader user understand the controls?
- Are all reusable decisions expressed as tokens or component rules?
- Does the result look native to the requested platform instead of imported from another medium?
