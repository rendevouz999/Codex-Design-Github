# Web Deck Motion Grammar

## Purpose

- Give the `web-deck` medium a motion language with named roles, real timing numbers, and a per-deck
  motion identity, so a browser deck moves on purpose instead of moving because it can.
- Judge whether an entrance, transition, emphasis, state change, or ambient loop has a
  communication job, the same way `.design-brain/EFFECT_LANGUAGE_JUDGMENT.md` judges depth and
  lighting.

Use this file for any `web_deck`, `html_deck`, `browser_presentation`, `animated_slides`, or
`web_slides` work. It does not apply to the static `presentation-deck` medium, where runtime and
motion vocabulary stays forbidden.

## Core Rule

Motion is a hierarchy tool with a time axis. Every move must answer one question: what does the
audience understand after it that they did not understand before it.

Motion is never a substitute for structure. If the slide only becomes interesting while it is
moving, the slide is underbuilt. Restraint is a valid answer, but it must be a decision: the motion
signature is authored for every deck, even when the answer is a single entrance family and one
transition.

All timing numbers below are authored at the fixed `1920 x 1080` stage defined in
`skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`. The deck plan carries exactly one easing token,
`tokens.motion.easing`, and it is the `settle` curve: `skills/presentation-deck/resources/web-deck/stage-base.css`
spends it on the slide transition and on every `.deck-reveal` entrance. The other easing roles
below are authored on the surfaces that one token does not reach, and are verified by review.

## Motion Roles

### 1. Entrance

- Job: bring a block onto a slide that is already live, so the audience knows where to look first.
- Scope: one entrance per content block, played once per slide visit.
- Failure mode when overused: every block arrives with its own move, nothing is first, and the slide
  takes longer to assemble than to read. The speaker waits for the deck instead of the deck waiting
  for the speaker.

### 2. Emphasis

- Job: re-point attention at a block that is already on screen, usually on the speaker's beat.
- Scope: at most one emphasis target per slide, and it must return to rest.
- Failure mode when overused: competing pulses. Two emphasized objects cancel each other and the
  slide reads as decorated rather than argued.

### 3. Transition

- Job: carry the audience from slide to slide and express the relationship between them:
  continuation, progression, position, depth, or chapter break.
- Scope: one transition family per deck, taken from `tokens.motion.transition`.
- Failure mode when overused: the transition becomes the content. A deck where every slide boundary
  is an event has no section hierarchy left, because every move is already at maximum.

### 4. State Change

- Job: confirm a runtime fact. Progress advanced, page number changed, notes pane opened, a control
  gained focus, the deep link updated.
- Scope: the chrome layer and interactive affordances only, outside the scaled stage.
- Failure mode when overused: chrome animation competes with slide content and the audience tracks
  the interface instead of the argument.

### 5. Ambient

- Job: keep one surface alive at very low amplitude, such as a slow gradient drift or a breathing
  accent field.
- Scope: at most one ambient surface in a deck, and never on a slide carrying data or dense text.
- Failure mode when overused: a permanent low-grade distraction that costs frames all deck long,
  reads as a screensaver, and makes deliberate motion unreadable because nothing is ever still.

## Timing Bands

Per role, measured at stage scale:

- Entrance: `420-620 ms` per block. `tokens.motion.entranceMs` neutral default `560`, from the
  `:root` block of `skills/presentation-deck/resources/web-deck/stage-base.css`; authored decks sit at `480-560`.
- Emphasis: `160-280 ms` out, and the same band back to rest. Review-verified; no token carries it.
- Transition: `380-560 ms` slide to slide. `tokens.motion.transitionMs` neutral default `480`.
- State change: `160-240 ms`. `stage-base.css` fixes the chrome timings it owns: `160 ms` for the
  tap-zone fade and `220 ms` for the counter and the control row, both `linear`.
- Ambient: `8000-24000 ms` per cycle, with a delta of at most 4 percent in opacity, scale, or
  position. If the loop is visible as a loop, it is too strong.

### Travel Follows The Single Duration

One `entranceMs` and one `transitionMs` cover every move in the deck, so distance does not buy a
longer duration in this medium; amplitude is what varies. `skills/presentation-deck/resources/web-deck/stage-base.css`
fixes the authored travel per primitive:

- Entrance, `.deck-reveal--*`: `rise` `44 px`, `blur` `18 px` plus a `14 px` radius, `slide`
  `-64 px`, `scale` `0.94`, `mask` a full-width inset wipe.
- Transition, `.deck-stage--*` and `.deck-slide--*`: `rise` `56 px`, `slide` `96 px`, `scale`
  `1.045`, `mask` a full-width inset wipe.
- A move that would need more than roughly `120 px` of travel to read is too far for one shared
  duration. Replace it with a mask or a fade instead of lengthening the token; a block that crosses
  most of the stage draws a line the content does not need.
- A surface larger than 40 percent of stage area takes less travel, not more time: halve the
  amplitude and let the opacity carry it. A chip, label, or badge takes the full amplitude.
- A fade-only reveal is distance-free and still runs for the deck's `entranceMs`. Do not author a
  second, shorter duration for it.

### Stage Scale Versus Small UI

- The stage is projected or shown full screen, so the same pixel distance covers a much larger
  visual angle than it does in a window. Multiply a UI-calibrated duration by `1.4-1.6` when
  authoring on the stage, and keep the travel amplitudes above expressed in stage units. That
  multiplier is where the entrance band comes from: a UI-scale `350 ms` arrival becomes the
  `420-620 ms` stage band.
- Chrome lives outside the scaled stage and keeps true UI timings (`160-220 ms`). Do not scale
  chrome motion with the stage; a progress bar that eases like a slide transition feels broken.
- Small-UI amplitude rules do not transfer either: a `12 px` nudge at stage scale is a readable move,
  not a subtle one. Translate offsets of `18-64 px` are usually enough for an entrance, with the low
  end reserved for a primitive where another property carries the move, as `blur` does at `18 px`.
  Beyond `120 px` the block reads as flying in.

## Easing Vocabulary

Four named roles. Each deck picks one easing set and uses it everywhere. Only `settle` is carried
by a token; the other three are authored where that token does not reach.

- `settle` for arrival, entrance, and reveal. This is `tokens.motion.easing`, neutral default
  `cubic-bezier(0.2, 0.65, 0.3, 1)` in `skills/presentation-deck/resources/web-deck/stage-base.css`. Fast commitment,
  long deceleration, no overshoot; an authored deck stays in that shape, as
  `cubic-bezier(0.22, 0.68, 0.28, 1)` does.
- `exit` for leaving, dismissal, and the outgoing slide: `cubic-bezier(0.4, 0, 1, 1)`. Accelerates
  away, because a departing object does not need to be tracked.
- `snap` for state change, chrome, toggles, and focus: `cubic-bezier(0.2, 0.9, 0.25, 1)`. Short and
  decisive; it confirms rather than performs. `stage-base.css` already ships `linear` for the
  chrome opacity fades it owns, so `snap` is for chrome motion a deck adds itself.
- `drift` for ambient only: `cubic-bezier(0.45, 0.05, 0.55, 0.95)`. Near-symmetric with no accent,
  so the loop never reads as an event.

### When A Spring-Feeling Curve Is Wrong

An overshoot curve such as `cubic-bezier(0.34, 1.56, 0.64, 1)` is wrong for:

- Text blocks. Overshoot forces the eye to re-fixate on a line it had already found.
- Data. A bar or counter that passes its value and comes back has reported a wrong number.
- Institutional, finance, legal, healthcare, and luxury directions, where bounce reads as toy.
- Anything under `prefers-reduced-motion`, where overshoot is exactly the vestibular trigger.
- Any object larger than 25 percent of stage area; big surfaces that rebound look unstable.

Overshoot is allowed only as the single accent move in the motion signature, on a non-text object,
with the overshoot at or below 3 percent of travel distance.

## Stagger

- `tokens.motion.staggerMs` is one deck-wide step delay in the `40-90 ms` band, neutral default
  `90` in `skills/presentation-deck/resources/web-deck/stage-base.css`. One token means one step for every sequence in
  the deck; never author a second step for a longer row.
- The stagger window is `staggerMs x (steps - 1) + entranceMs` and stays under `1000 ms`. At the
  neutral defaults a five-step slide lands at `920 ms`. The slide must feel arrived before the
  speaker's second sentence.
- Beyond 7 items a stagger reads as a wave rather than a sequence. Group the items into 2 or 3
  clusters and stagger the clusters, not the items. The five-step budget below already forces this:
  a seven-item row is one clustered step, not seven.
- A stagger must follow reading order, which is the order the audience will read and the order the
  content is authored in. Never stagger by distance from center, by column, by random offset, or in
  reverse. A stagger that fights reading order is worse than no stagger.
- Never stagger inside a single paragraph, a sentence, a set of table rows, or a chart's own marks.
- Equal-weight items get an equal step. Changing the step mid-sequence implies a hierarchy the
  layout does not show.
- `tokens.motion.staggerMs` carries the chosen step and the whole deck uses it, so stagger rhythm is
  a signature trait rather than a per-slide improvisation.

## Slide Transition Grammar

The five families in `tokens.motion.transition` and what each one says:

- `fade` states equivalence and continuation. The lowest-claim transition, and the right default for
  `reading_first` decks, dense sequences, and any deck where the slide boundary should disappear.
- `rise` states progression and accumulation. The argument is building and each slide adds to the
  last.
- `slide` states sequence and position. It reinforces the arrow keys and gives the audience a sense
  of place in a linear narrative. Backward navigation must mirror it.
- `scale` states depth of focus: entering a detail, or stepping back to an overview. Strongest when
  the deck actually alternates between overview and detail.
- `mask` states a chapter break or a withheld reveal. A clipped edge or shape uncovers the next
  slide, which is the most expensive claim in the set, so it needs real chapters behind it.

### Pairs That Clash

- `slide` with `rise`: two travel axes in one deck, so direction stops meaning anything.
- `scale` with `mask`: both claim the chapter-break job and read as one doubled effect.
- `fade` as the transition while `fade` is also the only entrance: slide boundaries vanish and the
  deck becomes one long dissolve.
- `slide` forward with `scale` backward: backward navigation must be the inverse of forward inside
  the same family, mirrored in direction, or the deck loses reversibility.
- Any transition family paired with an entrance that travels on the same axis at the same moment:
  the incoming slide and its first block move together and the hierarchy is lost. Offset the first
  entrance by at least `80 ms` after the transition, or let the transition carry it.

One family per deck. A second family is legal only as the signature accent move, reserved for
`section-divider` entry, and used at most twice in a deck.

## Reveal Order Authoring

- `revealOrder` step ids map one to one onto the attention path: what the eye takes first, second,
  and third. Trace the path first and author the steps from it; never derive the path from whatever
  markup order happens to exist.
- Step 1 always contains the headline. A slide whose headline arrives in step 2 or later fails the
  gate, because a slide must be identifiable the moment it appears.
- Step budget, and this file owns it: `densityMode: speaker_led` allows 1 to 5 steps on any slide.
  `densityMode: reading_first` allows 0 to 2, default 0, because everything needed to understand
  the slide must be legible without advancing and a reader may never advance. The budget does not
  vary with the `density` marking: a `light` slide carrying five sequenced steps is legal, and a
  `dense` slide that needs only one is better.
- `skills/presentation-deck/runtime/web/design_brain_web_deck_plan.mjs` rejects a `revealOrder` longer than 12, the number of
  `data-deck-step` stagger slots `stage-base.css` declares. 12 is the tool's hard limit; the
  5-step budget above is the editorial cap, verified by review, and it is what keeps the stagger
  window under `1000 ms`. `skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs` checks that every planned step
  id exists in the artifact (`reveal-order-agreement`, P1); it never counts steps.
- Text must not move while it is being read. Once a text block has arrived it is positionally frozen
  for the rest of the slide. Later steps may add blocks beside or below it, never reflow it.
- Reserve the space for unrevealed content in the initial layout and hide it with `opacity` and
  `visibility`. Never reveal by inserting a block into flow, because that pushes arrived text.
- Reveal is driven by a class on the active slide, not by scroll position and not by a timer, so the
  speaker owns the pace.
- Backward navigation lands on a fully revealed slide. Only `reason: init` on the entry slide starts
  a slide at step 1; re-entering a visited slide must not replay the sequence.
- A self-running deck may advance reveal steps on its own, but the dwell per step is at least
  `2500 ms` plus `180 ms` per word of newly revealed copy, and manual control stays available.
- Media counts as a reveal step. A chart that animates its marks occupies one step and does not also
  get a stagger across its series.

## Motion Signature

Every deck gets one motion signature, recorded in `motionSignature` in the deck plan and built from
five axes:

1. Entrance family: the one or two moves blocks are allowed to arrive with
   (`motionSignature.entrance`).
2. Transition family: one value from `tokens.motion.transition`.
3. Easing set: which of `settle`, `exit`, `snap`, and `drift` are in play, and at what amplitude.
4. Stagger rhythm: step size, cluster strategy, and whether stagger is used at all.
5. One accent move: the single memorable gesture in the deck (`motionSignature.accent`), used no
   more than twice, and never on a `data` or `dashboard` slide.

### Diverging Signatures Between Decks

- Two decks from this system must differ on at least 3 of the 5 axes, scored against the thresholds
  in Motion Similarity Axis Rules below.
- Reusing a transition family is allowed only when entrance family, easing set, stagger rhythm, and
  accent move all differ.
- Signature divergence is the motion-level form of the requirement
  `.design-brain/ORIGINALITY_SIMILARITY_SCORECARD.md` applies to layout and color. A deck that
  moves exactly like an accepted prior deck is a repeat even when its slides look different.
- Record the moves this deck must not use in `motionSignature.forbidden`, including anything carried
  over from a prior deck that must not repeat.

### Motion Similarity Axis Rules

Motion originality is judged axis by axis, the way layout originality is judged in
`.design-brain/LAYOUT_SIMILARITY_AXIS_RULES.md`. An overall score is useful context and cannot hide
a high-risk axis. No script computes these axes: they are scored by review against the reference
and against every earlier deck in the session, and recorded in
`skills/presentation-deck/resources/WEB_DECK_RECEIPT.md`.

Axes:

1. `entranceFamilySimilarity`
2. `transitionFamilySimilarity`
3. `easingCurveSimilarity`
4. `staggerRhythmSimilarity`
5. `accentMoveSimilarity`
6. `revealGrammarSimilarity`
7. `motionAmplitudeSimilarity`
8. `durationBandSimilarity`
9. `roleMotionMappingSimilarity`
10. `chromeMotionSimilarity`
11. `reducedMotionStateSimilarity`
12. `overallMotionSignatureRisk`

Scoring uses the same scale as the layout axes: `0.00` no meaningful similarity, `0.25` low, `0.50`
moderate, `0.70` high, `0.85` near clone, `1.00` identical.

Hard fail thresholds:

- `entranceFamilySimilarity >= 0.70`
- `transitionFamilySimilarity >= 0.75`
- `revealGrammarSimilarity >= 0.70`
- `accentMoveSimilarity >= 0.70`
- `roleMotionMappingSimilarity >= 0.72`
- `overallMotionSignatureRisk >= 0.65`
- any near-clone axis `>= 0.85`

Report with every motion-originality judgment:

- `signatureDefiningAxisSimilarity`: max risk across entrance family, transition family, accent
  move, reveal grammar, and role-to-motion mapping.
- `timingLanguageAxisSimilarity`: max risk across easing curve, stagger rhythm, amplitude, and
  duration band.
- `hardFailAxes`: axes that block final readiness.
- `softRiskAxes`: axes that require revision without blocking on their own.
- `overallMotionSignatureRisk`: aggregate motion identity risk.

The 3-of-5 divergence rule above is the same test written as a threshold: at least 3 of
`entranceFamilySimilarity`, `transitionFamilySimilarity`, `easingCurveSimilarity`,
`staggerRhythmSimilarity`, and `accentMoveSimilarity` must sit at or below `0.25`. A hard fail axis
blocks even when the aggregate looks moderate.

Repair requirements, per axis:

- Entrance family similar: change which elements move and which stay, and pick a different
  `.deck-reveal--*` set.
- Transition family similar: change the family in `tokens.motion.transition` and the relationship
  it claims between slides.
- Easing curve similar: re-derive `tokens.motion.easing` from a different acceleration shape, not
  from the same curve with shifted control points.
- Stagger rhythm similar: change the step, change the cluster strategy, or drop stagger entirely.
- Accent move similar: replace the accent gesture and the slide role it lands on.
- Reveal grammar similar: re-trace the attention path and re-author `revealOrder` from it.
- Role-to-motion mapping similar: change which slide roles get motion and which stay still.
- Amplitude or duration band similar: the weakest repair in the set. Re-timing never clears a
  similar entrance family, transition family, accent move, or reveal grammar on its own, exactly as
  recolor is not a repair for layout similarity.

Axis statuses are `PASS`, `REVISE_REQUIRED`, and `BLOCKED`, as in
`.design-brain/LAYOUT_SIMILARITY_AXIS_RULES.md`. They reach the gate and the receipt through the
one mapping in `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`: a hard fail axis enters it as a `P0`, a soft
risk axis as a `P1`.

### Cliche Blacklist

Any of these counts as a motion-originality defect, and belongs in `motionSignature.forbidden`
rather than in the deck:

- Bounce-in or elastic headlines.
- Typewriter text, letter-by-letter display type, and word-by-word body copy.
- Numbers counting up on every metric, especially on `data` and `dashboard` slides.
- Infinite floating or hovering cards.
- Parallax on every background, and fake scroll-parallax inside a fixed stage.
- Full-stage 3D cube, flip, or page-curl rotations.
- Confetti, sparkle bursts, and neon pulse loops.
- Blur-to-focus on every image, and a slow zoom on every photograph.
- Mouse-trailing particles and cursor-following glow.
- A spinning or self-drawing logo on the cover.
- Gradient hue rotation as a permanent background loop.

## Accessibility

- Treat `prefers-reduced-motion: reduce` as an authored design state, not a switch that deletes
  motion. The reduced state has its own look and is reviewed as a deliverable.
- In the reduced state: transitions become a `100-120 ms` opacity cross-fade with zero translate,
  scale, and mask; the stagger step becomes `0`; ambient loops are removed entirely; the accent move
  is removed; emphasis becomes a static change in weight, border, or surface.
- Reveal steps survive reduced motion as discrete opacity steps, because they carry the speaker's
  pacing and the meaning of the slide rather than decoration.
- Both the CSS and the JS path must consult the query. A `@media` block alone leaves JS-driven
  motion running.
- Focus order across slides: only the active slide is reachable. Inactive slides are hidden through
  `visibility`, marked `aria-hidden`, and made `inert`, so nothing offstage enters the tab ring.
  Inside a slide, focus order follows reveal order, and chrome controls come after slide content.
- Announce slide changes through one visually hidden `aria-live="polite"` region updated on the
  `deckslidechange` event, in the form `Slide 7 of 24, <headline>`. Coalesce key-repeat bursts and
  announce only the settled slide.
- No keyboard traps. Escape closes the notes pane and returns focus to its trigger, Tab always has a
  path out of any overlay, and navigation keys stay inactive inside editable fields and under
  modifier chords.
- Motion is never the only carrier of a state change. Page number, progress, and the deep link hash
  state the position statically.
- Flash safety: no luminance change covering more than 10 percent of stage area may repeat faster
  than 3 times per second.

## Performance Rules For A Browser Deck

- Animate `opacity` and `transform` only. Never animate `top`, `left`, `width`, `height`, `margin`,
  `padding`, `box-shadow` spread, or `background-position`; each of those re-runs layout or paint
  every frame at stage size.
- The frame budget is `16.7 ms`, measured during a slide change on the delivery machine and not at
  idle. If a transition cannot hold it, remove a layer rather than shorten the duration; a short
  janky move reads worse than a longer clean one.
- `will-change: opacity, transform` is justified only on the outgoing and incoming slide, applied
  just before the change and removed when it ends. A blanket declaration on every slide promotes
  each one to its own layer, and one full-stage layer costs roughly `8 MB` of GPU memory
  (`1920 x 1080 x 4` bytes), so a 24-slide deck can reserve close to `200 MB` for nothing.
- `filter: blur()` and `backdrop-filter` are the dominant cost at stage scale, because a blurred
  surface is re-rasterized whenever it or its radius changes. Never animate a blur radius on a
  full-stage surface; cross-fade the opacity of a pre-blurred layer instead. Cap `backdrop-filter`
  at one surface per slide and roughly 25 percent of stage area.
- Canvas and particle budget: at most one canvas in a deck, sized to its own CSS box with
  `devicePixelRatio` clamped at 2, at most 150 particles at stage width, and the animation frame
  cancelled whenever its slide is inactive or `document.hidden` is true. No loop runs behind slides
  that do not show it.
- Navigation stays responsive during a transition. A key pressed mid-transition finishes or cuts to
  the target; it never queues a backlog of slide changes.
- Gate the first entrance on `document.fonts.ready` with a short timeout, so the opening slide does
  not animate fallback metrics and then reflow, and so a failed font request cannot stall the deck.
- Nothing animates in print. The stage transform is removed, every slide is forced visible, and all
  motion is inert.

### Drop Order On Weak Hardware

Degrade in this order and stop as soon as the frame budget holds:

1. Ambient loops.
2. Canvas and particle layers.
3. Blur and `backdrop-filter` surfaces.
4. Stagger, collapsed into a single group entrance.
5. Transform in the transition, falling back to an opacity-only fade.

Reveal steps are never dropped. They carry meaning, not polish.

## What Not To Animate

- Body paragraphs, quotes, and any copy longer than a line, beyond a single entrance.
- Table rows, table headers, and the internal marks of a chart that already animated once.
- Numbers whose accuracy is the message.
- Logos, legal lines, footnotes, source credits, and page numbers.
- Focus rings and error states.
- The slide background while text on it is being read.
- Anything in the chrome layer other than its own state change.
- Anything at all during print, or under reduced motion beyond the authored reduced state.

## Acceptance Criteria

- Every move in the deck maps to one of the five motion roles and has a stated job.
- All durations fall inside the band for their role, and travel distances match their duration tier.
- One easing set is used deck-wide, with every curve recorded as a concrete `cubic-bezier` value.
- Stagger follows reading order, stays inside the `1000 ms` window, and clusters beyond 7 items.
- One transition family is chosen, backward navigation mirrors it, and no clashing pair is present.
- Every slide's `revealOrder` matches its traced attention path, keeps the headline in step 1, and
  respects the step budget for its `densityMode`.
- No arrived text block moves or reflows during a later reveal step.
- The motion signature records all five axes, differs from accepted prior decks on at least 3 of
  them, lists its forbidden moves, and no motion similarity axis sits at or above its hard fail
  threshold.
- No item from the cliche blacklist appears anywhere in the deck.
- The reduced-motion state is authored, reviewed, and honored by both the CSS and the JS path.
- Slide changes are announced once through a live region, and no offstage slide is focusable.
- Only compositor properties are animated, `will-change` is scoped and cleaned up, and the slide
  change holds the frame budget on the delivery machine.
- The documented drop order has been applied until the deck holds frames on the weakest target
  machine.
- Deleting the motion still leaves a deck that communicates; the motion improves the deck instead of
  carrying it.
