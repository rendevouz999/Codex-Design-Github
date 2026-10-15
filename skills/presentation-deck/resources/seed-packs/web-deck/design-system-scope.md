# Web Deck Design System Scope

## Foundations

- Color roles mapped to the plan tokens: `bg`, `surface`, `text`, `muted`, `border`, `accent`, `accentContrast`. Document the job of each role, not just the swatch.
- Type scale roles mapped to `displayFamily`, `bodyFamily`, `displaySize`, `leadSize`, `bodySize`, `captionSize`, authored at stage size in px.
- Spacing scale mapped to `stagePadX`, `stagePadY`, `blockGap`, `itemGap`, plus the 8 px baseline and the 12-column, 100 px column, 48 px gutter grid.
- Stage contract: 1920 x 1080 authored size, uniform-scale fit, letterbox overflow, and the statement that nothing inside a slide reflows.
- Contrast evidence: the measured ratio for `text` on `bg`, `text` on `surface`, `muted` on `bg`, and `accentContrast` on `accent`.
- Media treatment: crop ratios in use, scrim recipe over photography, and placeholder appearance when an asset is missing.

## Motion System

- Motion tokens and their meaning: `entranceMs`, `transitionMs`, `staggerMs`, `easing`, `transition`.
- The slide transition chosen from `fade`, `rise`, `slide`, `scale`, `mask`, and why that one fits the deck.
- Motion signature: the entrance set, the accent set, and the forbidden set. The forbidden set is the part a reviewer can check.
- The reveal step vocabulary used in this deck and how step ids map to markup.
- Reduced-motion behavior: what resolves instantly, what keeps a shortened fade, and what is removed entirely.
- Motion budget: how many animated elements may appear on one slide before the slide reads as a demo reel.

## Runtime Behavior

- Navigation surface: keys bound, pointer-tap zones, wheel debounce window.
- Deep-link format and the slide index base used in the URL hash.
- The `deckslidechange` event payload and what consumes it.
- The public runtime API surface and what is deliberately not exposed.
- Chrome inventory: progress, page number, controls, notes pane, with the on/off state from `chrome` and where each element sits relative to the stage.
- Focus order and visible focus treatment for every chrome control.

## Slide Modules

- One specimen per archetype in use, showing the zone geometry rather than finished copy.
- Zone anatomy for each specimen: column spans, y bands, media zone, and type role per zone.
- Card, metric tile, list row, quote block, panel, and node as reusable modules with their internal spacing.
- Chart rules: palette order, axis and label type roles, direct-labelling rule, units, and source line placement.
- Table rules: header treatment, row rhythm, numeric alignment, and maximum rows per stage.
- Placeholder replacement rules: what a buyer or editor swaps, and what must not be moved.

## Delivery Scope

- `delivery` settings in force: single-file or asset folder, `assetsDir`, `fontSource`, `pdfExport`.
- Font loading plan under the chosen `fontSource`, with the fallback stack and the layout-shift limit it must respect.
- Print specimen: how the deck looks as one slide per page, which chrome disappears, and which reveals are forced open.
- Known print losses, stated plainly rather than discovered by the recipient.
- File weight target, inlined asset budget, and what gets externalised when the budget is exceeded.

## Compact But Complete Rule

A web deck design system may be concise, but it must cover both halves of the medium. Minimum standard:

- Foundations with functional roles and measured contrast.
- Stage and grid geometry.
- Motion tokens plus a motion signature with a forbidden set.
- Runtime behavior and chrome inventory.
- Archetype specimens with zone anatomy.
- Chart and table rules.
- Placeholder replacement rules.
- Delivery and print scope with named losses.

A board that documents color, type, and spacing but says nothing about motion, runtime, or print is a token receipt for a static deck. Fail it: half the medium is missing.
