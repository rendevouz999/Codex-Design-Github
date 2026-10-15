# Web Deck Checklist

`P0` and `P1` below are review buckets carrying the same severity meaning the two enforcement tools
use, not a claim that a tool emits a finding for every line. How a tool `P0` or `P1` becomes a gate
`PASS` / `REVISE` / `BLOCKED` and a receipt final status is stated once, in the Severity And Status
Mapping section of `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`.

## P0

- Request routed to `web-deck` on explicit web-deck intent, not on a bare `deck`, `slides`, `ppt`, or `powerpoint` request.
- Direction resolved through `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md` before planning: convert, author new, or static stays authoritative.
- Deck plan validates against `skills/presentation-deck/resources/web-deck/deck-plan-schema.json`.
- Stage is authored at exactly 1920 x 1080 px and declared as such in `stage`.
- Fit is one uniform transform on the stage element, `scale = min(viewportWidth / 1920, viewportHeight / 1080)`, centered, with letterbox or pillarbox allowed.
- Stage transform uses `transform-origin: 0 0` with an explicit translate, recomputed on `resize`.
- No slide content reflows for small screens. There are no breakpoints inside a slide.
- Slide switching uses `visibility`, `opacity`, `pointer-events`, and `z-index`. No slide is toggled with `display`.
- Keyboard navigation covers ArrowRight, ArrowLeft, PageDown, PageUp, Space, Home, and End.
- Keyboard handling ignores events from editable fields and ignores modifier chords.
- Pointer taps on the left and right thirds are bound for coarse pointers only.
- Wheel stepping is debounced so one gesture advances one slide.
- Deep link reads `#<n>` as a 1-based index on load and calls `history.replaceState` on every slide change.
- Each slide change dispatches a `deckslidechange` CustomEvent with `bubbles` and `composed`, carrying `{ index, previousIndex, total, reason }` where `reason` is `init`, `key`, `pointer`, `wheel`, or `api`.
- Public runtime API exposes `index`, `length`, `goTo(i)`, `next()`, `prev()`, and `reset()`.
- Reveal animations are driven by a class on the active slide, never by scroll position.
- A `@media (prefers-reduced-motion: reduce)` block exists, and JS-driven motion checks the same query before animating.
- Chrome (progress, page number, controls) lives outside the scaled stage and is hidden in print.
- Print rules exist: `@page { size: 1920px 1080px; margin: 0 }`, stage transform removed, every slide forced visible with `break-after: page`, chrome hidden.
- Print produces one slide per page with every reveal step resolved to its final state.
- Zero runtime dependencies. No CDN script, no build step, no imported bundle. Web fonts are the only external request.
- `delivery.singleFile` is honored: a single-file deck inlines CSS, JS, and critical assets and opens with no sibling files.
- Smallest readable text on stage is `captionSize`, and body text stays legible at thumbnail scale.
- Text contrast meets WCAG 2.2 AA against the surface behind it, including over media scrims.
- Focus is visible and keyboard order is sane for every interactive control in the chrome.
- Every slide declares `archetype`, `role`, `density`, and `revealOrder`, and `revealOrder` ids match the step attributes in the markup.
- `skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs` reports status `PASS` on the generated file, meaning zero `P0` findings. A `P1` finding still exits `0`, so a clean exit code is not a clean audit; read the finding list.

## P1

- Density matches `densityMode`: `speaker_led` keeps one claim plus up to 3 support items and 25 on-stage words; `reading_first` allows up to 5 support items, 90 on-stage words, and a footnote layer. The budgets live in `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md` and are enforced by `skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs` when a plan is supplied.
- Dense slides are justified. `dashboard` may default to dense; any other dense slide names its reason.
- No slide needs an internal scroll region to fit its content.
- Reveal steps stay inside the budget in `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`, 1 to 5 per slide for `speaker_led` and 0 to 2 for `reading_first`, and supporting detail never reveals before the claim it supports.
- Motion signature is declared with entrance, accent, and forbidden lists, and the forbidden list is actually enforced in the output.
- Transition, entrance, stagger, and easing come from `tokens.motion`, not from per-slide ad hoc values.
- Motion serves reading order. No motion exists only to look animated.
- Archetype rhythm varies: no three consecutive slides share archetype, axis, media side, and column split.
- Silhouette alternates between light and dense slides across the deck.
- Paired archetypes are mirrored deliberately so `problem` and `solution` read as one turn.
- At least six distinct archetypes in a 12-slide deck; at least ten for a template product.
- Speaker notes exist per slide when `chrome.notesPane` is true, and the notes pane is hidden from print and from the stage.
- Media placeholders are role-based, with a declared `purpose`, `aspect`, and `placeholder` string.
- Crop ratio is consistent within a slide, and portrait eye lines are consistent across a card row.
- Charts carry direct labels, units, a source line, and one takeaway.
- Fonts resolve under `delivery.fontSource`, with a system fallback stack that does not shift layout past one line.
- `delivery.pdfExport` is set true only after the print path was checked in a real browser print preview.
- `skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs` was run and its findings were resolved or recorded.
- Deck was checked at a narrow viewport, a tall viewport, and a 4K viewport to confirm the scale stays uniform and nothing clips.
- Originality: no third-party slide tool, framework, plugin, repo, author handle, or template pack is named, linked, bundled, or hinted at anywhere in the output.
- Originality: layout gesture, silhouette sequence, focal path, and motion signature diverge from prior accepted decks, with the motion side scored against the named axes in `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`.
- Converted decks carry a degradation report naming every substituted font, dropped effect, unreadable chart, and slide-count delta.
- Receipt is written from `skills/presentation-deck/resources/WEB_DECK_RECEIPT.md` and states which artifact is authoritative.

## Hard Gate

- Do not ship a deck that toggles `display` for slide visibility. Later layout rules override it and every slide shows at once.
- Do not ship a deck without a `prefers-reduced-motion` path.
- Do not ship a deck that loads any external script or stylesheet other than fonts.
- Do not ship a deck whose print output is not one slide per page.
- Do not call a single-file deck single-file when it depends on repo paths or sibling assets.
- Do not route a static-artifact deliverable to `web-deck` because the deck looks better in a browser.
- Do not treat a passing audit as a design review. The audit proves the contract, not the craft.
