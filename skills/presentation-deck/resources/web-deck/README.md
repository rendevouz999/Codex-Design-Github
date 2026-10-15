# Web Deck Runtime Kit

This folder stores the canonical data and runtime assets for the `web-deck`
medium. It is the shared contract between the knowledge modules, the plan tool,
and the audit tool.

Read `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md` for authoring judgment and
`skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md` for the stage rules these files encode.

## Contents

- `deck-plan-schema.json`: JSON Schema 2020-12 for the deck plan,
  `$id` `design-brain.web-deck.deck-plan.v1`. It fixes the required keys, the
  token groups, the slide item shape, and the archetype enum.
- `stage-base.css`: the stage, slide-visibility, chrome, reduced-motion, and
  print layer. It is the structural half of the runtime contract.
- `deck-runtime.js`: navigation, deep linking, reveal stepping, the
  `deckslidechange` event, and the public runtime API. It is the behavioral
  half of the same contract.

## How The Tools Consume This Folder

- `skills/presentation-deck/runtime/web/design_brain_web_deck_plan.mjs` validates its plan against
  `deck-plan-schema.json` before emitting a deck, then inlines `stage-base.css`
  and `deck-runtime.js` into the generated file.
- `skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs` reads the generated deck and checks
  it against the same stage and runtime rules these assets implement.
- `skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs` drives the generated deck in
  a browser and reviews the rendered result.
- `skills/presentation-deck/runtime/web/design_brain_deck_source_extract.mjs` emits an extracted deck plan
  that must validate against `deck-plan-schema.json` before re-design starts.

## Inline, Do Not Link

`stage-base.css` and `deck-runtime.js` are the canonical runtime kit. A
generated deck inlines both into the output file. Do not emit a `<link>` or
`<script src>` back to this folder: a web deck ships as a self-contained file,
and a deck that depends on repo paths breaks the moment it is sent to anyone.

Edit the assets here, not the copy inside a generated deck. A generated deck is
output, not source.

## Originality Rule

Both assets are original Brain Design work. No third-party slide runtime,
presentation framework, animation library, or vendor bundle is included,
copied, imported, or loaded. The medium has zero runtime dependencies and no
build step; web fonts are the only permitted external request.
