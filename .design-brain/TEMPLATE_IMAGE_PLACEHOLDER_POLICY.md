# Template Image Placeholder Policy

This policy applies to website templates, Figma templates, deck templates, dashboard templates, marketplace source files, and any other editable template product.

## Core Rule

For source-template work, image areas are editable replacement zones by default.

Do not generate, invent, or force final images just because a reference contains imagery. The correct source-template behavior is to create a clear text clue placeholder.

Use this default wording pattern for image slots:

- `image placeholder: [purpose]`
- `image placeholder: product dashboard screenshot`
- `image placeholder: restaurant hero photo`
- `image placeholder: ecommerce product image`
- `image placeholder: case-study visual`
- `image placeholder: map or location photo`

Use this default wording pattern for human/profile slots:

- `profile photo placeholder: [role]`
- `profile photo placeholder: founder portrait`
- `profile photo placeholder: team member`
- `profile photo placeholder: doctor portrait`

Use role-specific non-photo placeholders when needed:

- `chart placeholder: revenue trend`
- `diagram placeholder: workflow steps`

## Standing PPTX sourced-photo authorization

The owner explicitly authorizes searched real photos for useful native PPTX photo slots while using Codex-Design. Follow `skills/presentation-deck/workflows/PPTX_IMAGE_SELECTION_POLICY.md`: web/Unsplash/Pexels discovery, Main visual review and slide-specific placement, two rejected Engineer rounds then Main takeover. Keep pictures native and replaceable; retain text clue placeholders for unfilled replacement zones. This standing exception does not authorize generated images, force photos into diagrams, or change non-PPTX defaults. The single Engineer uses GPT-6.1 Sol (Codex) / Claude Opus 5.5 (Claude Code) with Extra High (`xhigh`).

## Why

A marketplace template must be reusable. A buyer needs to understand where their own brand, product, team, screenshots, venue, case study, or product photos belong. A forced generated image can make the file look finished but can reduce editability, mislead the buyer, and create unnecessary replacement work.

## Default Behavior

When the user asks for a template, template source, Figma template, website template, batch template, marketplace template, editable layout, or reusable design:

- Use role-based text clue placeholders for image zones.
- Make the placeholder visible, short, and specific to the section purpose.
- Design the surrounding frame, crop area, spacing, mask, ratio, caption, and replacement logic.
- Treat image placeholders as part of the template's product value.
- Use icons, shapes, charts, and simple editable motifs when they clarify function.

## When Real Or Generated Images Are Allowed

Do not use real/generated images in source-template image slots. Use real/generated images only when one of these is true:

- The user explicitly asks to create, generate, or use images.
- The user supplies the image assets and asks to place them.
- The user explicitly asks for a marketplace cover, promotional preview, mockup, or final demo image that uses finished imagery.
- The product category requires non-editable visual material and the user approves that tradeoff.

If using images for a user-requested preview/cover/demo, keep the source-template slots editable and still label replacement areas with text clue placeholders.

## Reference Handling

When a reference contains photos, screenshots, product shots, portraits, maps, or decorative imagery, learn the function behind the image:

- What buyer confidence does the image create?
- What kind of replacement content does the buyer need?
- What ratio, crop, frame, caption, or surrounding proof does the slot need?
- Where does the image help attention, trust, explanation, or conversion?

Then transform it into a new placeholder strategy. Do not copy exact image placement, crop, motif, staging, or section treatment.

## Hard Gate

Before building or reviewing a template, ask:

- Is this a source template or a final preview/demo?
- Did the user explicitly ask for generated images?
- Are image slots labeled with `image placeholder: ...` or another role-specific clue?
- Are human/profile slots labeled with `profile photo placeholder: ...`?
- Would a buyer know exactly what image to replace here?
- Did any generated image sneak into a source template without permission?

If the deliverable is a source template, replace unauthorized or forced images with text clue placeholders. Distinguish image generation from explicitly authorized sourced photography, including the standing PPTX exception above. Do not remove an approved sourced PPTX photo merely because image generation was not requested.

## Bad Patterns

- Generating fake people for team, doctor, founder, teacher, or consultant slots.
- Generating generic product photos when the buyer should replace them.
- Treating reference imagery as an obligation to create similar imagery.
- Using vague placeholders such as `image here` when the section needs a specific clue.
- Making placeholders so visually weak that the template feels unfinished.

## Good Patterns

- `image placeholder: SaaS dashboard screenshot` inside a polished product-frame slot.
- `image placeholder: hero product photo` inside a commerce hero with crop guide.
- `profile photo placeholder: doctor portrait` inside a healthcare trust card.
- `image placeholder: restaurant interior or signature dish` inside a booking hero.
- `image placeholder: project case-study image` inside a portfolio case card.
- `chart placeholder: monthly revenue trend` inside a dashboard proof module.
