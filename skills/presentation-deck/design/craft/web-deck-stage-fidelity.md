# Web Deck Stage Fidelity Craft

Use this craft module for `web-deck` output after the deck renders in a browser. It audits whether
the fixed stage, the slide switching technique, the chrome layer, and the runtime behavior survive
real viewports, real keys, and real printing. The stage and runtime rules it checks are defined in
`skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`; the automated half runs through
`skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs` and
`skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs`.

## Core Principle

A web deck is a fixed `1920 x 1080` stage that is scaled, never reflowed. Every fidelity failure is
one of three things: the stage fitted wrong, a slide that should be hidden is not, or the chrome
leaked into the stage.

## P0 Stage And Runtime Checks

`P0` and `P1` here are review buckets carrying the same severity meaning the two enforcement tools
use, not a claim that a tool emits a finding for every line. How a tool `P0` or `P1` maps to a gate
status and a receipt status is stated once, in the Severity And Status Mapping section of
`skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`.

- `stage` in the deck plan is exactly `1920 x 1080`, `fit: uniform-scale`, `overflow: letterbox`.
- Fit is one uniform transform on the stage element with
  `scale = min(viewportWidth / 1920, viewportHeight / 1080)`, not a per-element or per-axis scale.
- `transform-origin: 0 0` with an explicit translate for centering, recomputed on `resize`; no
  reliance on margin auto or flex centering to position a transformed stage.
- Slide switching uses `visibility`, `opacity`, `pointer-events`, and `z-index`. No slide is toggled
  with `display`, because a later `display: flex` rule overrides it and exposes every slide at once.
- Exactly one slide is visible, hit-testable, and focusable at any time; inactive slides are
  `aria-hidden` and `inert`.
- No layout reflows for small screens, and no media query changes slide content geometry.
- Content stays inside `tokens.space.stagePadX` and `stagePadY` on every slide, including page
  numbers, captions, chart legends, and footnotes.
- No collision, overlap, or accidental tangent between title, body, cards, media, chart, and chrome
  at full stage size, checked per slide and not from a contact sheet.
- Nothing overflows the `1920 x 1080` box; a slide that needs more room loses content or changes
  archetype, it does not spill.
- Chrome, including progress, page number, controls, and the notes pane, lives outside the scaled
  stage and never inherits the stage transform.
- Chrome flags in the deck plan match what renders: `progress`, `pageNumber`, `deepLink`,
  `notesPane`.
- Keyboard navigation covers ArrowRight, ArrowLeft, PageDown, PageUp, Space, Home, and End.
- Pointer taps on the left and right thirds advance only for coarse pointers; the wheel step is
  debounced.
- Navigation ignores events originating in editable fields and ignores modifier chords.
- Deep link reads `#<n>` as a 1-based index on load, clamps out-of-range values, and writes through
  `history.replaceState` on every slide change so the back button is not polluted.
- Each change dispatches a `deckslidechange` CustomEvent with `bubbles` and `composed` true and a
  detail of `{ index, previousIndex, total, reason }`, where `reason` is `init`, `key`, `pointer`,
  `wheel`, or `api`.
- The public runtime API exposes `index`, `length`, `goTo(i)`, `next()`, `prev()`, and `reset()`.
- Print produces one slide per page: `@page { size: 1920px 1080px; margin: 0 }`, the stage transform
  removed, every slide forced visible with `break-after: page`, and all chrome hidden.
- Zero dependencies, no CDN script, no build step; fonts are the only external request.

## P1 Stage Fidelity Checks

- Letterbox and pillarbox bars use the deck background color, not the browser default, so the deck
  never shows a white frame on a dark slide.
- The page has no horizontal or vertical document scroll at any viewport; the stage is clipped and
  centered, never scrolled to.
- Narrow and short viewports degrade honestly: below a scale of roughly `0.35`, where a `28 px`
  authored body size (the `--deck-type-bodySize` neutral default) renders near `10 px`, the deck
  points to the PDF or print path rather than pretending to be responsive.
- The scale recompute is throttled to one per frame and survives rapid resize, browser zoom,
  device-pixel-ratio changes, and entering or leaving full screen.
- Address-bar collapse on mobile and dynamic viewport units do not leave a stale scale; the fit is
  recomputed on `orientationchange` as well as `resize`.
- Chrome does not cover slide content when the viewport is letterboxed on the short axis; it sits in
  the bar, or it hides.
- Focus order runs slide content first and chrome controls after, with visible focus on every
  control.
- Deep link, progress, and page number agree with the live index after keyboard, pointer, wheel, and
  `goTo()` navigation.
- `goTo()` with an out-of-range, missing, or non-numeric argument is clamped or ignored; it never
  leaves the deck with no visible slide.
- A full-deck pass produces no console errors or warnings, and no unhandled rejection from the
  runtime.
- The deck still navigates after the font request fails or is blocked.
- Print fidelity is checked against the real print preview: one slide per page, no clipped content,
  no chrome, no blank interleaved pages.
- Printed charts, media placeholders, and dark surfaces remain legible, and background graphics are
  requested rather than assumed.
- Thumbnail reading still works: at roughly 20 percent scale, each slide stays distinguishable and
  the headline remains the strongest element.
- `delivery.singleFile`, `assetsDir`, and `fontSource` describe what the artifact actually is; a
  deck claiming `singleFile` has no external reference other than fonts.

## Per-Slide Fidelity Method

1. Render the deck at `1920 x 1080` and inspect the slide at full stage size.
2. Confirm only the active slide is visible, hit-testable, and in the tab ring.
3. Check safe margins, collisions, tangents, and overflow against the stage box.
4. Resize to a wide-short viewport and a narrow-tall viewport, and confirm the letterbox behavior.
5. Navigate with every supported key, a pointer tap, and the wheel, then confirm index, progress,
   page number, and hash all agree.
6. Reload on a deep link and confirm the deck opens on that slide with `reason: init`.
7. Open print preview and confirm one slide per page with no chrome.

## Acceptance Criteria

- Every slide has a recorded pass or fix decision at full stage size.
- The audit tool reports no `display`-toggled slide and no stage dimension drift, which are its
  `slide-switch-no-display-toggle` and `stage-authored-size` P0 findings.
- Navigation, deep link, chrome state, and the `deckslidechange` detail stay consistent across all
  navigation reasons.
- Letterbox behavior and the narrow-viewport fallback are both demonstrated, not assumed.
- Print preview has been inspected, not inferred from the stylesheet.
- The runtime API behaves correctly at the first slide, the last slide, and on invalid input.
