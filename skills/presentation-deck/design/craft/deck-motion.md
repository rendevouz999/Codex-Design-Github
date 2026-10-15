# Deck Motion Craft

Use this craft module for `web-deck` output once a deck has slides and a motion plan. It is the
review checklist for `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`; the grammar holds the reasoning and
the full timing tables, this file holds the checks.

## Core Principle

Each move must name its role and its job. A deck passes when motion can be described slide by slide
without the words "nice", "modern", or "smooth".

## P0 Motion Checks

`P0` and `P1` here are review buckets carrying the same severity meaning the enforcement tools use.
No tool asserts the motion rules below; they are verified by review. How a tool `P0` or `P1` maps
to a gate status and a receipt status is stated once, in the Severity And Status Mapping section of
`skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`.

- Every move is one of entrance, emphasis, transition, state change, or ambient; unclassifiable
  moves are removed.
- Durations sit inside the role band: entrance `420-620 ms`, emphasis `160-280 ms`, transition
  `380-560 ms`, state change `160-240 ms`, ambient `8000-24000 ms` per cycle.
- Travel, not duration, varies with the move: one `entranceMs` and one `transitionMs` cover the
  whole deck, and a move that needs more than roughly `120 px` to read is replaced by a fade or a
  mask instead of being given a longer duration.
- Chrome motion keeps UI timings (`160-220 ms`) and is not scaled up with the stage.
- One easing set deck-wide, each curve written as a concrete `cubic-bezier` value. Only `settle`
  maps to `tokens.motion.easing`; the other three roles are authored where that token does not
  reach.
- No overshoot curve on text, data, large surfaces, or anything outside the single accent move.
- One transition family in `tokens.motion.transition`, and backward navigation is its mirror image.
- No clashing family pair: `slide` with `rise`, `scale` with `mask`, or `fade` used as both the only
  entrance and the transition.
- The headline is in reveal step 1 on every slide.
- Reveal steps respect the budget: `speaker_led` 1 to 5 steps on any slide, `reading_first` 0 to 2
  with the slide legible before any advance.
- No arrived text block moves, reflows, or is pushed by a later reveal step; unrevealed space is
  reserved in layout and hidden with `opacity` and `visibility`.
- Stagger follows reading order, never reverse, column order, or distance from center.
- One deck-wide stagger step from `tokens.motion.staggerMs`, in the `40-90 ms` band, with the whole
  window (`staggerMs x (steps - 1) + entranceMs`) under `1000 ms`; more than 7 items are clustered
  into one step.
- `motionSignature` records entrance family, transition family, easing set, stagger rhythm, and one
  accent move, plus its `forbidden` list.
- The signature differs from accepted prior decks on at least 3 of the 5 axes, and no motion
  similarity axis in `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md` sits at or above its hard fail
  threshold.
- Nothing from the cliche blacklist is present: bounce headlines, typewriter text, counting numbers,
  floating cards, full-stage 3D flips, confetti, cursor particles, spinning logos, permanent hue
  loops.
- A `prefers-reduced-motion: reduce` state is authored, not merely disabled: cross-fade only, zero
  stagger, no ambient, no accent move, reveal steps intact.
- Both the CSS and the JS motion paths consult the reduced-motion query.
- Only `opacity` and `transform` are animated; no layout or paint property moves during a transition.
- No luminance change over 10 percent of stage area repeats faster than 3 times per second.
- Nothing animates during print.

## P1 Motion Checks

- The first entrance is offset at least `80 ms` from the transition, or the transition carries it.
- Emphasis has at most one target per slide and returns to rest.
- Ambient motion is limited to one surface, and never appears on a `data` or `dashboard` slide.
- `will-change` is applied only to the outgoing and incoming slide and removed when the change ends.
- Blur and `backdrop-filter` are capped at one surface per slide and roughly 25 percent of stage
  area, and no blur radius is animated on a full-stage surface.
- Canvas work is capped at one canvas per deck, `devicePixelRatio` clamped at 2, at most 150
  particles, and the frame loop cancelled when its slide is inactive or the document is hidden.
- A navigation key pressed mid-transition cuts or finishes; it does not queue a backlog.
- The first entrance waits on `document.fonts.ready` with a timeout, so fallback metrics do not
  animate and then reflow.
- The documented drop order is applied on weak hardware: ambient, canvas, blur, stagger, transform.
- Entrance translate offsets stay in the `18-64 px` range at stage scale and never exceed `120 px`.
  The low end belongs to a primitive where another property carries the move, as `blur` does.
- Self-running decks dwell at least `2500 ms` per step plus `180 ms` per newly revealed word.
- Media reveals count as one step and do not also stagger their internal marks.
- Equal-weight items share one stagger step; a changed step is justified by a visible hierarchy.

## Acceptance Criteria

- Each slide has a one-line motion description naming role, duration, easing, and reveal step count.
- Every reveal order matches the traced attention path for that slide.
- The motion signature is recorded in the deck plan and diverges from prior accepted decks on the
  axes in `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`, with every axis score recorded in the
  receipt.
- The reduced-motion state has been reviewed as its own deliverable.
- The slide change holds the `16.7 ms` frame budget on the delivery machine, with effects removed
  rather than durations shortened when it does not.
- Removing all motion still leaves a deck that communicates.
