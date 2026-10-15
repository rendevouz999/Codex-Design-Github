# Deck Source Bridge

Use this file when a static deck source and the web-deck medium meet in the same task: turning an existing PPTX, Keynote, Google Slides, or Figma deck into a web deck, or taking a web deck back out as a static handout.

This module only decides direction and governs what crosses the boundary. Authoring rules stay in `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md`, static slide-system rules stay in `skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md`, and format survivability rules stay in `skills/presentation-deck/design/01_powerpoint_technical/export-compatibility-rules.md`.

## Direction Decision

Resolve direction before any planning step. There are three outcomes and no fourth.

- Convert: a named source artifact exists and the request asks for that content in the browser. Extract, then author a web deck from the extracted deck plan.
- Author new: web-deck intent with no source artifact. Skip extraction entirely and go straight to Design Cognition.
- Static stays authoritative: the deliverable is still a static file. Route to `presentation-deck` and do not build a web deck.

### Convert Signals

- The request names a real artifact or path (`.pptx`, `.key`, `.fig`, an exported PDF) or a hosted slide link, together with web-deck intent.
- A convert trigger appears: `deck to web`, `ppt to web`, `pptx to html`, `convert deck to html`, `ppt ke web`, `ppt ke html`, `pptx ke html`, `ubah ppt jadi web`.
- The content is referred to as already existing ("my deck", "this proposal", "slide ini"), not briefed as new.

### Author Signals

- Web-deck intent with a brief, topic, audience, outline, or slide count but no artifact.
- A deck is mentioned only as taste reference or market evidence, not as content to move.
- The source is a template being studied for product standard, not a specific deck being relocated.

### Ambiguity Rule

If both a source artifact and a fresh brief are present, ask which one owns the content before extracting. Do not silently merge an extracted deck plan with a new outline: slide count, order, and headline voice drift, and the degradation report stops being verifiable.

## Extraction Tool

Use `skills/presentation-deck/runtime/web/design_brain_deck_source_extract.mjs`. It reads the source deck and writes an extracted deck plan plus an extraction report.

- Extraction output is evidence, not a build scaffold. It records what the source says, not what the web deck should become.
- Never hand extraction output to `skills/presentation-deck/runtime/web/design_brain_web_deck_plan.mjs` as a finished plan.
- Design Cognition runs after extraction and before any layout decision. The 11 steps in `.design-brain/DESIGN_COGNITION_CONTRACT.md` are not skippable because the source already has slides.
- Treat each run like `.design-brain/evidence/fig-extracts/` output: generated, append-only, and never promoted into `DESIGN_MEMORY.md` without an explicit request.

## Carried Across

- Slide order and slide count, as a starting sequence that re-design is allowed to change.
- Slide titles and body text, verbatim, as raw content to re-edit into takeaway form.
- Bullet structure: nesting depth, item count per slide, and whether a block is a list or a paragraph.
- Speaker notes, mapped into the per-slide `notes` field of the deck plan.
- Image assets with their geometry: intrinsic pixel size, crop box, aspect ratio, and on-slide position recorded as a media role and prominence cue.
- Chart data where readable: series, categories, values, units, and axis labels.
- Detected slide role per slide, mapped onto the web-deck archetype vocabulary.
- Source font names, color values, and theme indices, recorded as inventory for the token remap.

## Not Carried Across

- Master and placeholder geometry. A PPTX layout tree is not a stage grid.
- Absolute shape coordinates. Replaying them produces a pixel clone.
- Static-format effects: WordArt, bevels, 3-D rotation, soft and inner shadows, picture artistic effects, and theme-indexed gradient fills.
- SmartArt. Carry the text and the relationship type; rebuild the diagram natively on the stage.
- Fonts that cannot be licensed or served for web. Record the name, then remap under `delivery.fontSource`.
- Animation and transition timings. Static-deck motion is per-shape and click-driven; the web deck takes its signature from `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`.
- Embedded video and audio in container-specific codecs. Re-encode or substitute a media placeholder.
- Hidden slides, revision marks, comments, and macro content.
- Tables as rendered grids. Carry the cell data and rebuild the table.

## Re-Design Rule

Extraction yields a deck plan for re-design. It never yields a pixel clone.

- A converted deck passes the same stage, motion, density, accessibility, and originality gates as an authored deck.
- Slide count, order, archetype choice, and type scale are re-decided on the stage, not inherited.
- Fidelity to the source is measured in meaning preserved, not in pixels matched.
- Color and type are remapped through Color Role Re-Mapping; a source palette is an inventory, not a target.
- If the request genuinely asks for a visual replica, that is a static-artifact request. Say so and route to the static path.

## Degradation Report

Both directions lose something. Name every loss in the build receipt (`skills/presentation-deck/resources/WEB_DECK_RECEIPT.md`), one line per loss, with the slide index when the loss is local.

Static to web, report:

- Any slide whose role could not be mapped to an archetype, and the fallback used.
- Any chart whose data was unreadable and is now a media placeholder.
- Every substituted font, with the source name and the web replacement.
- Every dropped effect, with the slide index and the design decision that replaced it.
- Any text that no longer fits the stage at the chosen type scale, and whether it was re-edited or re-laid.
- Any SmartArt or diagram rebuilt from text, with the relationship type assumed.
- Slide count delta against the source, with the reason for each split or merge.

Web to static, report the losses listed under the reverse direction below.

## When The Static Artifact Stays Authoritative

- The recipient must open, edit, or re-export the deck in PowerPoint, Keynote, or Google Slides.
- Delivery is an attachment to a submission, tender, grant, or compliance process that specifies a file format.
- The content must be co-edited by people with no browser build step.
- The product is a slide template for marketplace sale; buyers need masters, layouts, and placeholders.
- Playback is offline, kiosk, or on a controlled display with no usable browser.

In these cases a web deck may still ship as a live-presenting companion, but the static file remains the version of record. State which artifact is authoritative in the receipt.

## Reverse Direction: Web Deck To Static Handout

A web deck leaves the browser only through the print path defined in `skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md`.

- Print uses the deck's own rules: `@page { size: 1920px 1080px; margin: 0 }`, stage transform removed, every slide forced visible with `break-after: page`, chrome hidden. One slide per page.
- Before export, resolve every reveal step to its final state. A slide printed mid-reveal loses content silently.
- Known losses: motion, runtime navigation, deep links, the notes pane, hover and focus states, data interaction, lazily loaded media, and any overflow region that scrolled inside a slide.
- Known risks: web fonts absent from the print subset, background colors dropped when the browser prints backgrounds off, letterboxing reintroduced if the stage transform survives, and charts rasterized at screen resolution.
- The output is a PDF handout, not an editable deck. To hand over an editable static deck, build it in `presentation-deck`. Never describe a printed web deck as an editable deck.
- Set `delivery.pdfExport` true only after the print path has been checked in a real browser print preview.

## Hard Gate

- Do not call a conversion complete without a degradation report.
- Do not ship a converted deck that replays source shape coordinates.
- Do not skip Design Cognition because the source already had slides.
- Do not build a web deck when the deliverable must stay an editable static file.
- Do not present a printed web deck as an editable static deck.
