# Browser output workflow

Use this mode of presentation-deck to build a deck that renders and runs in a browser. The module id is `web-deck`, the
runtime command is `/design-web-deck`, the seed pack is `web-deck`, and the direction pack is
`motion-stage`.

Resolve `PLUGIN_ROOT` from this capability's location; `CLAUDE_PLUGIN_ROOT` is an optional host alias. Run the commands below from that root or convert them to absolute paths. The canonical kit, design references and implementation are inside this capability.

Generation and static auditing use Node built-ins. PPTX source extraction needs JSZip, and browser review needs Playwright plus Chromium. Existing host dependencies are supported. For an isolated installation run `npm install --prefix <CAPABILITY_ROOT>/runtime/web`, then run that directory's Playwright CLI with `install chromium`. The local `package.json` declares tested versions without altering a consuming project's dependency manifest.

## Scope Boundary

An explicit PowerPoint/PPTX output takes precedence over generic `animated slides`,
`slide animasi`, or `self running deck` wording. Use `skills/presentation-deck/SKILL.md`
for native animation. Explicit HTML/browser output and PPTX-to-HTML conversion
stay here; explicit PPTX plus HTML requires two artifacts and two receipts.

`web-deck` is a fixed 16:9 stage with motion and runtime navigation. It is the browser output mode of `presentation-deck`, with a stage rather than a scrolling website.

- Static slide artifact requested (PPTX, Keynote, Google Slides, Figma slide template): use the native mode
  and use `skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md`. The Non-Web Mode Rule in
  `.design-brain/adapters/design-craft/SKILL.md` forbids web interaction vocabulary there.
- Scrolling marketing page requested: use the website-template path, not a deck stage.
- Both requested: build two artifacts with two receipts, never one hybrid.

Load `../design/WORKFLOW.md` for the shared design lifecycle. This document owns only browser-specific behavior.

## Lifecycle

Run the stages in order. Do not skip ahead to HTML.

### 1. Route

Confirm web-deck intent against the trigger list in the description and
`.design-brain/registry/modules.json`. A plain `presentation`, `deck`, `ppt`, `powerpoint`, or `keynote`
request without web intent belongs to `presentation-deck`.

### 2. Load The Knowledge Layer

- `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md` for the medium model and slide reasoning.
- `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md` for the stage and runtime rules that must hold.
- `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md` for entrance, accent, and forbidden motion.
- `skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md` for single-file, asset, font, and print delivery.
- `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md` when an existing deck is the input.
- `skills/presentation-deck/resources/web-deck/README.md`, `deck-plan-schema.json`, `stage-base.css`, and `deck-runtime.js`
  for the reusable stage assets.
- `skills/presentation-deck/design/craft/deck-motion.md` and `skills/presentation-deck/design/craft/web-deck-stage-fidelity.md` for the two
  craft axes this medium adds.
- `skills/presentation-deck/resources/seed-packs/web-deck/layouts.md`, `content-patterns.md`, `design-system-scope.md`, and
  `checklist.md` for slide archetypes and density decisions.

### 3. Cognition

Follow `.design-brain/DESIGN_COGNITION_CONTRACT.md` and `.design-brain/DESIGNER_COGNITION_LAYER.md`.
Decide audience, delivery mode, and `densityMode` before layout. `speaker_led` keeps headlines short and
carries the argument in slide notes. `reading_first` carries the argument on the slide itself. A deck
that will be read without a presenter cannot use speaker-led density.

### 4. Convert A Source Deck, When There Is One

For `ppt to web`, `pptx ke html`, or `ubah ppt jadi web`, extract the source outline instead of retyping
slides:

```bash
node skills/presentation-deck/runtime/web/design_brain_deck_source_extract.mjs --help
```

Read the script header for its current flags, then follow `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md` to map
the extracted outline onto web-deck archetypes. Source text and structure carry over. Source visual
styling does not; the direction pack and style pack decide the look.

### 5. Plan

Produce a deck plan that validates against `design-brain.web-deck.deck-plan.v1` in
`skills/presentation-deck/resources/web-deck/deck-plan-schema.json`. Pick `stylePack` from
`.design-brain/TEMPLATE_STYLE_PACKS.json` or `.design-brain/STYLE_PACKS.json`, and `directionPack` from
`.design-brain/direction-packs/directions.json`. Slide archetypes come from the fixed vocabulary in the
schema; do not invent new slide nouns.

```bash
node skills/presentation-deck/runtime/web/design_brain_web_deck_plan.mjs --demo --out <path>
```

The `--demo` run shows the expected plan and output shape. For real work, drive the tool from the task
plan. `scripts/design_brain_lint_plan.py` still applies to the Brain Design plan document and needs a
working Python interpreter; when none is available, state that in the final response.

### 6. Stage Gate

The stage contract is not negotiable, and `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md` is the authority:

- Authored stage is fixed `1920 x 1080`. Slide content never reflows for small screens.
- Fit is one uniform transform, `scale = min(viewportWidth / 1920, viewportHeight / 1080)`, centered,
  with `transform-origin: 0 0`, an explicit translate, and recomputation on `resize`.
- Slide switching uses `visibility`, `opacity`, `pointer-events`, and `z-index`. Never toggle `display`;
  a later `display: flex` rule would override it and reveal every slide at once.
- Navigation covers ArrowRight, ArrowLeft, PageDown, PageUp, Space, Home, and End, taps on the left and
  right thirds for coarse pointers, and a debounced wheel step. Ignore events from editable fields and
  modifier chords.
- Deep link reads `#<n>` as 1-based on load and uses `history.replaceState` on every slide change.
- Each change dispatches a `deckslidechange` `CustomEvent` that bubbles and is composed, carrying
  `index`, `previousIndex`, `total`, and `reason`.
- Chrome lives outside the scaled stage and is hidden in print.
- A `@media (prefers-reduced-motion: reduce)` block is mandatory, and JS-driven motion checks the same
  query before animating.
- Print uses `@page { size: 1920px 1080px; margin: 0 }`, drops the stage transform, forces every slide
  visible with `break-after: page`, and hides chrome.
- Public runtime API is `index`, `length`, `goTo(i)`, `next()`, `prev()`, and `reset()`.
- Zero dependencies, no CDN script, no build step. Fonts are the only allowed external request.

### 7. Build And Apply Motion Grammar

Build the deck from the plan, then check it against `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md` and
`skills/presentation-deck/design/craft/deck-motion.md`. Motion must come from the plan `motionSignature`, serve the
argument of each slide, and respect the forbidden list. Reveal animations are driven by a class on the
active slide, never by scroll position.

### 8. Audit

```bash
node skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs <deck.html> --json
```

The audit is a blocking gate. A deck that toggles `display` for slides, omits the reduced-motion block,
breaks the stage transform, or loads a third-party script fails here. Fix the deck and re-run. Do not
explain a failure away.

### 9. Render Review

```bash
node skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs --help
```

Read the script header for its current flags, then run it to inspect real rendered slides. Judge type
legibility at stage scale, safe-area respect, overflow, contrast, and motion behavior from the rendered
evidence, not from the source. `skills/presentation-deck/design/craft/web-deck-stage-fidelity.md` is the rubric.
A completed run leaves its evidence directory under `.design-brain/screenshots/` and its Markdown report
under `.design-brain/visual-reviews/`. Cite both paths in the receipt.

The tool-chain self-check is:

```bash
node skills/presentation-deck/tests/design_brain_web_deck_smoke_test.mjs
```

### 10. Receipt

Fill `skills/presentation-deck/resources/WEB_DECK_RECEIPT.md`. The deck is not final until the receipt records the
plan, stage-gate result, motion signature, audit result, render-review result, and the chosen delivery
mode. `.design-brain/POST_BUILD_COMPLETION_GATE.md` and
`.design-brain/POST_BUILD_TRIPLE_AUDIT_GATE.md` still apply to this medium.

## Owner Guard

Building, converting, auditing, and reviewing decks is normal design work and needs no password.
Changing the Web Deck rules themselves, meaning `.design-brain/WEB_DECK_*`,
`skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md`, `skills/presentation-deck/resources/web-deck/`,
`scripts/design_brain_web_deck_*`, or this skill, is a protected modification. Ask the owner exactly
`kata sandinya apa?` first, give no hints, and stop if the answer does not verify against the verifier
in `.design-brain/OWNER_GUARD.md`.
