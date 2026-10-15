# Web Deck Layouts

Use this seed pack when the product is a web deck, HTML deck, browser presentation, animated slide set, single-file deck, or presenter deck rendered in a browser.

## Core Rule

A web deck is a fixed 16:9 stage, not a scrolling page. Slide content never reflows for small screens: the whole stage is scaled by one uniform transform, so layout geometry is authored once at 1920x1080 and stays true at every viewport.

The archetype vocabulary is closed. Use `cover`, `agenda`, `section-divider`, `problem`, `solution`, `feature`, `data`, `dashboard`, `timeline`, `roadmap`, `case-study`, `testimonial`, `team`, `pricing`, `portfolio`, `closing`. Do not invent new slide nouns; a new need is a variation of an existing archetype.

Every composition sketch below is a starting geometry, not a mandatory template. Structural Reconfiguration and Pattern Divergence still apply: two decks that use the same archetype must not resolve to the same silhouette.

## Stage Grid

- Stage: 1920 x 1080 px, origin top-left, `transform-origin: 0 0`.
- Stage padding: `stagePadX` 96, `stagePadY` 96. Content box 1728 x 888, from x 96 to 1824 and y 96 to 984.
- Columns: 12 columns of 100 px with 48 px gutters. Span n = 148n - 48.
- Span widths: 1 = 100, 2 = 248, 3 = 396, 4 = 544, 5 = 692, 6 = 840, 7 = 988, 8 = 1136, 9 = 1284, 10 = 1432, 11 = 1580, 12 = 1728.
- Column left edges: 96, 244, 392, 540, 688, 836, 984, 1132, 1280, 1428, 1576, 1724.
- Vertical rhythm: 8 px baseline. `blockGap` 48 between zones, `itemGap` 24 inside a list or card stack.
- Full-bleed media may break `stagePadY` and run 0 to 1080; text never does.

## Type Scale Roles

- `displaySize` 96: slide headline, section numeral, hero metric.
- `leadSize` 44: subtitle, quote body, single-idea support line.
- `bodySize` 28: list items, card body, axis labels, table cells.
- `captionSize` 18: eyebrow, footnote, source, page meta, attribution role.
- A single hero metric may uplift to 140-180. Nothing else exceeds `displaySize`.
- Minimum rendered text on stage is `captionSize`. Below that, legibility fails on a projector.

## Reveal Step Vocabulary

`revealOrder` lists step ids in reveal sequence, and the ids must match the step attributes in the generated markup. Reusable ids: `media`, `eyebrow`, `headline`, `lead`, `rule`, `item-n`, `metric-n`, `node-n`, `card-n`, `panel-n`, `footnote`, `cta`.

- Keep 3-6 steps per slide. More than six steps turns a slide into a sequence of slides.
- Background media reveals first so text never lands on an empty surface.
- Supporting detail reveals last. Never reveal a footnote before the claim it footnotes.

## Archetypes

### cover

- Purpose: name the deck, the claim, and the context in one hold.
- Zones: eyebrow cols 1-4 at y 96; display headline cols 1-7, y 300-620; subtitle cols 1-6 below the headline; meta row (presenter, context, date) cols 1-8 at y 912.
- Media: either a full-bleed backdrop behind the stage with a left-weighted scrim, or an edge-to-edge image column cols 8-12 running y 0 to 1080.
- Type: `displaySize` headline, `leadSize` subtitle, `captionSize` eyebrow and meta.
- Density: light.
- Reveal: `media -> eyebrow -> headline -> lead -> footnote`.

### agenda

- Purpose: set the sequence and the reading order before any argument starts.
- Zones: title block cols 1-5, y 96-300; numbered rows cols 6-12 starting y 240, row height 96, `itemGap` 24. Five rows occupy y 240-816.
- Media: none. An agenda that needs an image is hiding a weak sequence.
- Type: `leadSize` row label, `captionSize` row index in accent, `displaySize` title.
- Density: light at 3-4 rows, medium at 5-6. Never more than six rows.
- Reveal: `headline -> rule -> item-1 -> item-2 -> item-n` with `staggerMs` between rows.

### section-divider

- Purpose: mark a gear change and give the audience a breath.
- Zones: section numeral cols 1-3, section title cols 4-10, both inside a centered band y 420-660; one caption line naming what follows at y 700.
- Media: optional full-bleed image at reduced contrast, or a flat accent surface with no image at all.
- Type: `displaySize` numeral and title, `captionSize` caption.
- Density: light, always. A divider that carries content is not a divider.
- Reveal: `media -> eyebrow -> headline -> lead`.

### problem

- Purpose: make the cost of the current state concrete before any solution appears.
- Zones: headline cols 1-6, y 96-320; two or three friction blocks cols 1-6 stacked from y 368 to 888; evidence media cols 8-12, y 96-888.
- Media: one 3:4 or 16:10 evidence frame. Role is proof, not decoration.
- Type: `displaySize` headline, `bodySize` friction blocks, `captionSize` source line.
- Density: medium.
- Reveal: `headline -> lead -> item-1 -> item-2 -> media`.

### solution

- Purpose: answer the problem slide in the same visual breath, from the opposite side.
- Zones: media cols 1-5 y 96-888; headline cols 7-12 y 96-320; three reasoning steps cols 7-12 stacked y 368-888.
- Media: mirror the problem slide axis. If `problem` put media right, `solution` puts it left.
- Type: `displaySize` headline, `bodySize` steps, `captionSize` step index.
- Density: medium.
- Reveal: `media -> headline -> item-1 -> item-2 -> item-3`.

### feature

- Purpose: show capability breadth without turning the slide into a specification list.
- Zones: headline cols 1-8, y 96-280. Three-up cards at cols 1-4, 5-8, 9-12 (544 each), card band y 352-824. Four-up cards at cols 1-3, 4-6, 7-9, 10-12 (396 each).
- Media: one icon or crop per card, top-aligned inside the card, 1:1 at 96 px or 16:9 at full card width.
- Type: `leadSize` card title, `bodySize` card body, `captionSize` card index.
- Density: medium at three-up, dense at four-up.
- Reveal: `headline -> card-1 -> card-2 -> card-3`.

### data

- Purpose: carry one chart and one takeaway. Not two charts, not a dashboard.
- Zones: takeaway headline cols 1-12, y 96-232; plot area cols 1-8, y 296-840; readout column cols 9-12 with up to three stacked values; source line cols 1-8 at y 888.
- Media: the chart is the media. No decorative image.
- Type: `displaySize` lead value in the readout, `bodySize` axis and series labels, `captionSize` units and source.
- Density: medium.
- Reveal: `headline -> media -> metric-1 -> metric-2 -> footnote`.

### dashboard

- Purpose: show an operational surface at a glance, with scanning order designed.
- Zones: headline cols 1-7, y 96-200; KPI row of four tiles at cols 1-3, 4-6, 7-9, 10-12, y 240-424; primary panel cols 1-7 and secondary panel cols 8-12, both y 472-888.
- Media: panels hold charts or tables, never photography.
- Type: `displaySize` KPI value, `captionSize` KPI label and delta, `bodySize` panel content.
- Density: dense. Permitted only when `densityMode` is `reading_first`, or when the deck is presented on a single large display.
- Reveal: `headline -> metric-1 -> metric-2 -> panel-1 -> panel-2`.

### timeline

- Purpose: show what happened in order, with the gaps between events visible.
- Zones: headline cols 1-6, y 96-256; axis rule at y 560 spanning cols 1-12; four to six nodes spaced on the axis; labels alternate above (y 360-536) and below (y 584-760).
- Media: none, or one 1:1 crop per node at 96 px on the axis.
- Type: `leadSize` node label, `bodySize` node detail, `captionSize` node date.
- Density: medium at four nodes, dense at six. Never more than six.
- Reveal: `headline -> rule -> node-1 -> node-2 -> node-n`, strictly left to right.

### roadmap

- Purpose: show what comes next in committed phases, with scope per phase.
- Zones: headline cols 1-6, y 96-240; phase scale cols 1-12 at y 264; three lanes at y 288-472, 496-680, 704-888, each 184 high.
- Media: none. A roadmap earns clarity from structure, not imagery.
- Type: `leadSize` phase label, `bodySize` lane items, `captionSize` phase window.
- Density: medium. Three or four lanes maximum.
- Reveal: `headline -> rule -> item-1 -> item-2 -> item-3`.

### case-study

- Purpose: connect context, action, result, and proof as one narrative.
- Zones: client eyebrow plus headline cols 1-6, y 96-320; three narrative blocks (context, action, result) cols 1-6 stacked y 368-760; result metric band cols 1-6, y 808-888; media cols 8-12 y 96-888.
- Media: one case crop or screenshot at 3:4. Role is proof.
- Type: `displaySize` result metric, `leadSize` headline, `bodySize` narrative blocks, `captionSize` client and sector.
- Density: medium.
- Reveal: `media -> eyebrow -> headline -> item-1 -> metric-1`.

### testimonial

- Purpose: let one external voice carry the slide.
- Zones: accent rule cols 1-2 at y 320; quote body cols 3-10, y 320-680; attribution cols 3-7, y 736-800; portrait cols 11-12 as a 1:1 crop at 200 px, or omitted.
- Media: at most one portrait. Never a logo wall on the same slide.
- Type: quote at `leadSize` uplifted to 56-64, attribution name at `bodySize`, role and company at `captionSize`.
- Density: light. One quote per slide.
- Reveal: `rule -> headline -> lead -> media`.

### team

- Purpose: make the people credible without becoming a staff directory.
- Zones: headline cols 1-6, y 96-224; four profile cards at cols 1-3, 4-6, 7-9, 10-12, card band y 288-864; portrait 4:5 at 396 x 495 top-aligned in each card, name and role below.
- Media: one portrait per card, consistent crop and eye line across all cards.
- Type: `leadSize` name, `bodySize` role, `captionSize` credential line.
- Density: medium at three or four cards. Six cards means two rows and a smaller portrait, not a tighter gutter.
- Reveal: `headline -> card-1 -> card-2 -> card-3 -> card-4`.

### pricing

- Purpose: make the offer comparable and the recommended tier obvious.
- Zones: headline cols 1-8, y 96-216; three tier cards at cols 1-4, 5-8, 9-12, card band y 272-888; the highlighted tier bleeds to y 240-888 and uses the accent surface; feature rows inside each card at `itemGap` 24.
- Media: none. A price card with a photograph reads as an advertisement.
- Type: `displaySize` price, `leadSize` tier name, `bodySize` feature rows, `captionSize` billing note and footnote.
- Density: medium. Two to four tiers only.
- Reveal: `headline -> card-1 -> card-2 -> card-3 -> footnote`.

### portfolio

- Purpose: let the work argue for itself.
- Zones: headline cols 1-4, y 96-240. Symmetric option: three 4:3 frames at span 4 (544 x 408) across y 288-696 with captions below. Asymmetric option: hero frame cols 1-7 (988 x 600) plus two stacked frames cols 8-12 (692 x 288 each), all inside y 288-888.
- Media: the media is the content. Keep crop ratio consistent inside one slide.
- Type: `bodySize` project title, `captionSize` sector and year. No headline competing with the work.
- Density: medium. Six frames maximum; beyond that, split into two portfolio slides.
- Reveal: `headline -> media -> item-1 -> item-2`.

### closing

- Purpose: land the single thing to remember and the single thing to do next.
- Zones: headline cols 1-8, y 320-560; next-step line cols 1-6, y 608-680; contact row cols 1-10 at y 888; optional deep-link or scan block cols 11-12 as a 1:1 at 240 px.
- Media: none, or one muted full-bleed backdrop echoing the cover.
- Type: `displaySize` headline, `leadSize` next step, `captionSize` contact row.
- Density: light.
- Reveal: `media -> headline -> lead -> cta -> footnote`.

## Density Rule

- `speaker_led`: at most one claim plus three supporting items per slide. Body text exists to be glanced at, not read.
- `reading_first`: up to six supporting items and a visible footnote layer, because the deck will be opened without a presenter.
- `dashboard` is the only archetype allowed to default to `dense`. Every other dense slide needs a stated reason.
- If a slide needs a scroll region to fit, the slide is two slides.

## Variation Rule

- Do not run three slides of the same archetype in a row without changing the axis, the media side, or the column split.
- Alternate silhouette weight: a dense slide follows a light one.
- Mirror paired archetypes deliberately. `problem` and `solution` should read as one turn, not as two copies.
- A deck of 12 slides should use at least six distinct archetypes, and a template product should demonstrate at least ten.
