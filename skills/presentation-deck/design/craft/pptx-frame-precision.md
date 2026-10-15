# PPTX Frame Precision Craft

Use this craft module after a PowerPoint, Google Slides, Keynote, Figma Slides, or Figma-to-PPTX template has a complete visual draft. The goal is not to decide whether the deck mood is premium. The goal is to audit exact slide geometry so small placement errors do not survive into a sellable template.

## Core Principle

Each slide frame must pass a precision audit by itself before the deck is called finished. A good contact sheet can hide local collisions. Inspect every frame at normal size and thumbnail size.

## P0 Precision Checks

- Element collision: no headline, subtitle, card, chart, image, label, footer, or decorative object touches or visually overlaps another group.
- Tangent spacing: avoid near-touching edges where elements almost align or almost collide; increase separation or make the overlap deliberate.
- Title-to-content clearance: after the last line of a title, leave enough vertical breathing room before cards, bullets, charts, or images.
- Safe margins: all content stays inside slide-safe margins, including tiny labels, page numbers, and chart legends.
- Group boundaries: every content group has a visible parent rhythm; cards, bullets, and charts should not feel squeezed under the title or pushed against the frame edge.
- Footer clearance: footer rules, page numbers, section labels, and divider lines must not compete with slide content or sit too close to it.
- Placeholder resilience: the layout should still work if a title becomes one line longer, a bullet wraps, or an image crop changes.

## P1 Precision Checks

- Baseline rhythm: major text groups should share a deliberate baseline or vertical rhythm, not accidental drift.
- Column relation: left and right columns should have a clear relationship: aligned top, aligned center, or intentionally offset with enough contrast.
- Density balance: a heavy top cluster should not leave a dead lower half unless silence is clearly the slide concept.
- Chart fit: chart panels need internal padding, readable labels, and enough room for data marks, legends, and captions.
- Card fit: list cards need consistent height, padding, radius, and text alignment; numbers should not crowd text.
- Optical balance: dark panels, large titles, images, and accent bars should not pull the slide weight accidentally.
- Crop and mask accuracy: image or placeholder masks should not create awkward slivers, clipped details, or unintentional empty zones.

## Per-Slide Audit Method

1. Inspect the slide at full size.
2. Trace the first-look path: what the eye sees first, second, and third.
3. Draw invisible bounding boxes around title, body, cards, chart, image, footer, and motifs.
4. Check whether any boxes collide, nearly touch, or compete.
5. Check whether the title can grow by one line without breaking the layout.
6. Zoom out to thumbnail size and confirm the same hierarchy still reads.
7. Mark the slide as pass only when both composition and geometry pass.

## Common Failure Signals

- A multi-line headline ends so low that the first card or body block feels attached to it.
- A right-side panel begins at a height that visually crashes into the title rather than forming a clean second column.
- A dark chart block visually outweighs the slide because its padding, position, or height is not controlled.
- Footer/page number is technically inside the margin but visually too close to a divider or slide edge.
- The slide looks acceptable in a contact sheet but feels cramped when inspected at 100 percent.

## Slide 04 Learning Example

When a problem/evidence slide uses a large multi-line title on the left and a chart panel on the right, the audit must check title descent, card start position, and panel top alignment. If the title runs close to the first list card, the content feels overlapped even if the layers do not mathematically intersect. The fix is usually to lower the card stack, reduce title size/line-height, widen the title column, or align the right panel to a cleaner content baseline.

## Acceptance Criteria

- Every slide has a documented pass/fix decision.
- No slide is accepted only because the overall deck mood looks good.
- The weakest slide is inspected at normal size, not only in a contact sheet.
- Long-title, wrapped-bullet, and image-swap stress tests are considered before final delivery.
- Any overlap, near-collision, cramped title/content relationship, or accidental tangent is fixed or explicitly justified.
