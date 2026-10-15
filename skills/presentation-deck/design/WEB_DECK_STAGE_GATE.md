# Web Deck Stage Gate

This gate owns stage fidelity and runtime fidelity for every `web-deck` output. It is the
source-of-truth rule for how a browser-rendered deck is scaled, switched, navigated, revealed, and
printed.

A visible deck is not a finished deck. A deck is finished only after the static audit and the
rendered review have both been run and recorded. This gate is additive to the existing post-build
gates: it does not replace `.design-brain/POST_BUILD_TRIPLE_AUDIT_GATE.md` or
`.design-brain/POST_BUILD_COMPLETION_GATE.md`, and it cannot grant final readiness on its own.

## Gate Position

Run this gate twice inside the existing stages, not as a new mandatory runtime stage:

1. Plan-time check, after the deck plan exists and before any HTML is written.
2. Post-build check, after the deck artifact exists and before Audit Pass 1.

The plan-time check reads the deck plan. The post-build check reads the built artifact through the
two enforcement tools.

## Default Mode

Mode is strict.

Strict means every rule below is a hard rule. There is no exploratory variant of the stage
contract, because a deck that reflows, toggles `display`, or animates against a reduced-motion
request is broken for the audience in the room, not merely off-style.

## Enforcement Tools

- `skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs` is the static enforcement tool. It parses the built
  HTML and CSS and asserts the stage, switching, navigation, deep-link, lifecycle, reduced-motion,
  print, and dependency rules.
- `skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs` is the rendered enforcement tool. It loads the
  deck in a real browser and asserts per-slide overflow, overlap, clipping, and letterbox behavior
  at the required viewports.

Both tools must run. A visible deck with no static audit and no render review is not complete, and
its final status cannot be READY. Their severities and statuses are reconciled once, under
Severity And Status Mapping below.

The tools do not cover the whole gate. These rules are review-verified, because no tool asserts
them:

- the `Space` forward key, which the static audit leaves out of the key list it checks
- the exact public runtime API surface, and `goTo(i)` clamping instead of throwing
- the wheel debounce interval, and the editable-field and modifier-chord exclusions
- the reveal step budget in `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`, which no tool counts
- reveal steps present in the artifact but absent from the plan; the static audit checks the
  plan-to-artifact direction only

## Required Stage Behavior

Check:

- the authored stage is a fixed `1920 x 1080` px element
- slide content is authored at stage size and never reflows for small screens
- fit is one uniform transform on the stage element,
  `scale = min(viewportWidth / 1920, viewportHeight / 1080)`
- the stage is centered, and leftover space is letterbox or pillarbox
- `transform-origin: 0 0` is set, with an explicit translate for centering
- scale and translate are recomputed on `resize`
- no media-query breakpoint changes layout inside the stage
- `clamp()` and viewport units appear only in chrome that lives outside the scaled stage

Fail if:

- the stage has a percentage, `vw`, `vh`, or `auto` authored size
- more than one transform or a non-uniform scale is applied to the stage
- a breakpoint restyles slide content, grid columns, type scale, or spacing inside the stage
- `clamp()`, `vw`, or `vh` is used on slide content
- the scale is computed once and never recomputed on `resize`

## Required Slide Switching Behavior

Check:

- slide switching uses `visibility`, `opacity`, and `pointer-events`, with `z-index` when stacking
  order matters
- every slide stays in the layout at all times
- the inactive state is inert: not focusable, not hit-testable, not announced

Root cause this rule exists: slides are stacked and most slide bodies need `display: flex` or
`display: grid` for their own layout. A later layout rule overrides an earlier `display: none`
state rule, and the deck then shows every slide at once, piled on top of each other. Visibility
and opacity are not in that conflict, so they are the only allowed switch.

Fail if:

- any rule, inline style, or script toggles `display` for a slide
- a slide is removed from or inserted into the DOM to switch slides
- an inactive slide keeps `pointer-events` or focusable controls
- `opacity: 0` is used alone without `visibility` and `pointer-events`

## Required Navigation Behavior

Check:

- forward keys: `ArrowRight`, `PageDown`, `Space`
- backward keys: `ArrowLeft`, `PageUp`
- jump keys: `Home` to the first slide, `End` to the last slide
- coarse pointers get tap zones on the left third and the right third of the viewport
- a wheel gesture advances one slide and is debounced, so one physical gesture is one step
- keyboard handling ignores events whose target is an editable field (`input`, `textarea`,
  `select`, `contenteditable`)
- keyboard handling ignores events carrying a modifier chord (`Ctrl`, `Alt`, `Meta`, and `Shift`
  where the chord is a browser shortcut)
- the public runtime API is exactly the eight members `skills/presentation-deck/resources/web-deck/deck-runtime.js`
  exposes on the single `BrainDeck` global: the `index` and `length` getters, `goTo(i)`, `next()`,
  `prev()`, `reset()`, `init()`, and `fit()`
- `index` reads `-1` on a deck with no slides, and `goTo(i)`, `next()`, `prev()`, `reset()` each
  return the resulting index
- `init()` is idempotent and is called automatically once the document is ready; `fit()` forces a
  stage refit, which is what a host page calls after it resizes the deck's container itself
- `goTo(i)` clamps out-of-range input instead of throwing

Fail if:

- any key in the map is missing or bound to the wrong direction
- tap zones are active for fine pointers, so a mouse click on deck content changes the slide
- wheel stepping is undebounced and a single trackpad flick skips several slides
- typing in a notes field or a form control advances the deck
- a browser shortcut such as copy, refresh, or tab switch also advances the deck

## Required Deep Link Behavior

Check:

- the hash is `#<n>`, 1-based, so `#1` is the first slide
- the hash is read on load and the deck opens on that slide
- an out-of-range or unparseable hash falls back to slide 1 without throwing
- every slide change calls `history.replaceState`, so the address bar stays shareable

Fail if:

- the hash is 0-based or uses a non-numeric scheme
- the hash is ignored on load
- slide changes use `history.pushState` or assign `location.hash`, which poisons the back button
  with one history entry per slide

## Required Lifecycle And Reveal Behavior

Check:

- every slide change dispatches a `deckslidechange` `CustomEvent` with `bubbles: true` and
  `composed: true`
- the payload is `{ index, previousIndex, total, reason }`
- `reason` is one of `init`, `key`, `pointer`, `wheel`, `api`
- the first slide shown dispatches the event with `reason` set to `init`
- reveal steps are driven by a class on the active slide
- reveal step ids match the deck plan `revealOrder` for that slide

Fail if:

- the event name, payload shape, or `reason` vocabulary differs from the contract above
- a slide change happens with no event
- reveals are driven by scroll position, `IntersectionObserver`, or a scroll container
- reveal steps exist in the artifact but not in the plan, or in the plan but not the artifact. The
  static audit raises `reveal-order-agreement` for the plan-to-artifact direction only; the other
  direction is review-verified.

## Required Reduced Motion Behavior

Check:

- the stylesheet contains a `@media (prefers-reduced-motion: reduce)` block
- that block removes or neutralizes entrance animations, transitions, parallax, and looping motion
- reveals still resolve to their final visible state with motion removed
- every JS-driven animation checks the same `prefers-reduced-motion: reduce` query through
  `matchMedia` before animating, and jumps straight to the end state when the query matches

Fail if:

- the reduced-motion block is missing
- the block only shortens durations instead of removing motion
- a reveal never becomes visible when motion is removed
- JS animates without the same check, so the CSS block is bypassed at runtime

## Required Print Behavior

Check:

- `@page { size: 1920px 1080px; margin: 0 }`
- the stage transform is removed in print, so the slide prints at authored size
- every slide is forced visible in print
- every slide carries `break-after: page`
- chrome (progress, page number, controls, notes pane) is hidden in print

Fail if:

- browser print or PDF export produces a single page, a cropped slide, or blank pages
- chrome prints on top of slide content
- the printed order differs from the deck order

## Required Dependency Behavior

Check:

- zero runtime dependencies
- no CDN script tag, no import map, no remote module
- no build step: the artifact runs from the filesystem as delivered
- fonts are the only allowed external request, and the deck plan `delivery.fontSource` records
  which source is used
- local assets resolve relative to the artifact, matching the deck plan `delivery.assetsDir`

Fail if:

- any script source points at a remote origin
- the deck needs a bundler, transpiler, or dev server to run
- an external request is made for anything other than fonts
- `delivery.singleFile` is true but the artifact references sibling asset files

## Required Visual Verification

Per slide, at stage size (`1920 x 1080`):

- no content overflows the stage
- no unintended overlap between text blocks, media, and chrome
- no clipped text, clipped media, or cut descenders
- reveal end states are inside the stage, not only their start states
- contrast and type size stay readable at projection distance

Plus at least one narrow-viewport check:

- load the deck at a narrow viewport and confirm the stage letterboxes or pillarboxes
- confirm the slide internal layout is identical to the stage-size layout, only smaller
- confirm no horizontal page scrollbar appears

Fail if:

- any slide overflows, overlaps, or clips at stage size
- the narrow-viewport check shows reflowed content, rewrapped headlines, stacked columns, or a
  changed type scale
- the render review was skipped and the deck is claimed verified from source heuristics only

## Severity And Status Mapping

This is the one place the three vocabularies are reconciled. Every other web-deck file references
this section instead of restating it.

| Tool outcome | Tool status | Gate status | Receipt final status |
| --- | --- | --- | --- |
| no finding, both tools run | `PASS`, exit `0` | `PASS` | `READY` |
| `P1` only, repaired, rerun clean | `PASS`, exit `0` | `PASS` | `READY` |
| `P1` only, left unrepaired | `PASS`, exit `0` | `REVISE` | `REVISE_REQUIRED` |
| `P1` only, named and accepted by the user as a limitation | `PASS`, exit `0` | `REVISE` | `READY_WITH_LIMITATIONS` |
| no `FAIL`, but a render-review check reported `SKIP` | `PASS`, exit `0`, `counts.skipped` above `0` | `PASS` once every `SKIP` reason is review-verified, otherwise `REVISE` | `READY` once review-verified, otherwise `REVISE_REQUIRED` |
| any `P0` | `BLOCKED` for the audit, `FAIL` for the render review, exit `2` | `BLOCKED` | `BLOCKED` |
| tool error, or chromium not installed | exit `1`, receipt value `NOT_RUN` | `BLOCKED` | `BLOCKED` |

How to read it:

- `P0` and `P1` are per-finding severities, and only the two enforcement tools emit them.
  `skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs` reports a deck status of `PASS` or `BLOCKED` with exit
  `0` or `2`. `skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs` reports per-check `PASS`, `FAIL`,
  or `SKIP` and a run result of `PASS` or `FAIL` on the same exit codes. Neither tool ever emits
  `REVISE`, and the static audit never emits `FAIL`.
- `SKIP` is a per-check render-review status, not a severity and never a finding. It means the check
  did not apply to this deck, such as `nav-advance` on a single-slide deck or `deep-link-load` on a
  deck with fewer than three slides, or that the check did not run at all. It lands in
  `counts.skipped`, never in `counts.passed`, and it does not move the run result. Read each `SKIP`
  reason against the section it belongs to: a reason that holds is review-verified work, and a
  `SKIP` that only means nobody drove the check is a missing record, which is the `REVISE` case.
  The static audit has no `SKIP` status; run without `--plan` it reports its plan-relative checks as
  skipped in prose only, so supply the sidecar plan before reading its `PASS` as whole-gate coverage.
- `PASS`, `REVISE`, and `BLOCKED` are this gate's statuses and nothing else uses them.
- `READY`, `READY_WITH_LIMITATIONS`, `REVISE_REQUIRED`, and `BLOCKED` are receipt final statuses,
  set in `skills/presentation-deck/resources/WEB_DECK_RECEIPT.md`. Only `BLOCKED` is shared with this gate.
- One `P0` is enough for `BLOCKED`. There is no count at which `P1` findings become a `P0`: volume
  is a revision argument, not an escalation rule.
- `NOT_RUN` is never a pass. A deck with no render review cannot reach `READY` at any finding count.
- `READY_WITH_LIMITATIONS` needs a named limitation the user accepted. It is not a place to park a
  `P1` finding nobody repaired.
- The `P0` and `P1` headings in `skills/presentation-deck/resources/seed-packs/web-deck/checklist.md`,
  `skills/presentation-deck/design/craft/deck-motion.md`, and `skills/presentation-deck/design/craft/web-deck-stage-fidelity.md` carry
  the same severity meaning as a review bucket. They are not a claim that a tool emits a finding
  for every line; only the checks the two tools actually run produce tool findings.
- The motion similarity axes in `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md` and the layout axes in
  `.design-brain/LAYOUT_SIMILARITY_AXIS_RULES.md` report `PASS`, `REVISE_REQUIRED`, or `BLOCKED`.
  A hard fail axis enters this table as a `P0`; a soft risk axis enters as a `P1`.

## Status Behavior

`PASS`

- Every required behavior above is satisfied, the static audit exits clean with no `P0` and no
  unrepaired `P1`, and the render review records per-slide and narrow-viewport results.
- The deck may proceed to Audit Pass 1 and to the Web Deck receipt.

`REVISE`

- `P1` findings remain: a missing chrome print rule, an undebounced wheel step, a reveal id
  mismatch, one slide over its archetype text budget, a density budget overrun, or a missing
  narrow-viewport record.
- Repair, rerun the failed tool, and re-enter this gate. Final status cannot be READY while the
  gate reads REVISE.

`BLOCKED`

- A `P0` stage or runtime defect remains: `display` toggling for slides, reflowing slide content, a
  missing reduced-motion block, a remote script, a missing `deckslidechange` event, a missing
  contract token on `:root`, or a render review that could not run at all.
- Do not deliver. Do not call the deck done, ready, or shipped.

## Repair Rule

Default max repair cycles: 3.

1. Classify the defect against the section it failed.
2. Create a repair plan that names the broken rule, not the visible symptom.
3. Repair the artifact.
4. Rerun the failed tool.
5. If the repair touches the stage, the switch mechanism, or motion, rerun both tools.
6. If the defect survives the max cycles, set the gate status from the mapping above: REVISE for a
   surviving `P1`, BLOCKED for a surviving `P0`.

A recolor, a font swap, or a copy edit is never a valid repair for a stage or runtime defect.

## What This Gate Cannot Override

This gate owns stage and runtime fidelity only. It cannot override:

- the route decision or the medium choice, which stay with `.design-brain/NATURAL_INTENT_ROUTER.md`
  and `.design-brain/SOURCE_OF_TRUTH_MAP.md`
- Design Cognition, Design Simulation, or the layout originality gates
- `.design-brain/ORIGINALITY_GUARD.md` and the motion-signature divergence requirement
- `.design-brain/POST_BUILD_TRIPLE_AUDIT_GATE.md` and
  `.design-brain/POST_BUILD_COMPLETION_GATE.md`, which still decide final status
- the Non-Web Mode Rule for the static presentation mode, which keeps runtime and motion
  vocabulary out of PPTX, Keynote, and Google Slides output

A PASS here means the stage and the runtime are correct. It does not mean the deck is original,
well composed, or marketplace-ready, and it cannot be used to pass a failed audit pass.
