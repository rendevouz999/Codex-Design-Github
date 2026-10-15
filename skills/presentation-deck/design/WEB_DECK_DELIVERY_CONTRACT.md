# Web Deck Delivery Contract

This contract governs how a built web deck is packaged, shipped, opened, printed, and edited. It applies to every web deck, HTML presentation, animated deck, single-file presenter deck, and converted source deck. Planning judgment lives in `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md`; stage fidelity lives in `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`. This file owns the artifact.

## Core Rule

A web deck ships as a self-contained artifact that opens from a double click, with no server, no build step, and no package install.

The only allowed external network request is the declared font source. No CDN script, no CDN stylesheet, no framework, no analytics, no telemetry, no remote image. A deck that needs the network to be legible is not a deliverable.

Every delivery decision is recorded in the plan `delivery` object: `singleFile`, `assetsDir`, `fontSource`, `pdfExport`. The built file and the plan must agree. A mismatch between the two is a delivery defect, not a documentation gap.

## Single File Or Assets Folder

Single file is the default. One `.html` document carrying the markup, the inlined stage CSS, and the inlined runtime JS.

Choose single file when:

- Media slots are text clue placeholders rather than real imagery.
- Icons, logos, and motifs are inline SVG.
- The deck travels by email, chat, USB, or a shared drive.
- The room may be offline.
- The buyer will open the file directly instead of hosting it.

Choose an assets folder when:

- The deck carries real photographic or screenshot media.
- Fonts are self-hosted as `.woff2` files.
- Total media exceeds roughly 2 MB, where base64 inlining inflates the document and slows first paint.
- The buyer will swap images repeatedly, because replacing a file in a folder is far easier than editing an inline data URI.

Rules for both shapes:

- `delivery.singleFile` true requires `delivery.assetsDir` to be `null`.
- `delivery.singleFile` false requires `delivery.assetsDir` to be a relative folder name such as `assets`, never an absolute path and never a parent traversal.
- Stage CSS and runtime JS stay inline in the HTML in both shapes. They are built from `skills/presentation-deck/resources/web-deck/stage-base.css` and `skills/presentation-deck/resources/web-deck/deck-runtime.js` and inlined so the deck survives being moved, renamed, or re-zipped. Splitting them into sibling files for tidiness is not a reason to break self-containment.
- The deck is delivered as the HTML file plus, when it exists, the single assets folder beside it. No nested build output, no source map, no lock file, no temporary export.

## Token Layer

`:root` is the only place color, type, space, and motion values are declared. Every rule downstream consumes `var(--token)`.

Token names are derived mechanically as `--deck-<group>-<key>`, with the key spelled exactly as the `tokens` object in `skills/presentation-deck/resources/web-deck/deck-plan-schema.json` spells it. camelCase is preserved on purpose, so the plan tool, `skills/presentation-deck/resources/web-deck/stage-base.css`, `skills/presentation-deck/resources/web-deck/deck-runtime.js` and the audit tool cannot drift apart. The 22 contract tokens are:

- Color: `--deck-color-bg`, `--deck-color-surface`, `--deck-color-text`, `--deck-color-muted`, `--deck-color-border`, `--deck-color-accent`, `--deck-color-accentContrast`.
- Type: `--deck-type-displayFamily`, `--deck-type-bodyFamily`, `--deck-type-displaySize`, `--deck-type-leadSize`, `--deck-type-bodySize`, `--deck-type-captionSize`.
- Space: `--deck-space-stagePadX`, `--deck-space-stagePadY`, `--deck-space-blockGap`, `--deck-space-itemGap`.
- Motion: `--deck-motion-entranceMs`, `--deck-motion-transitionMs`, `--deck-motion-staggerMs`, `--deck-motion-easing`, `--deck-motion-transition`.

`skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs` fails a deck missing any one of those 22 on a `:root` selector, as `token-layer-root`, P0. Two further custom properties are written by the runtime on `<html>` and are not plan tokens: `--deck-scale`, the current fit scale, and `--deck-progress`, deck position 0 to 1.

Rules:

- There are two `:root` blocks in a delivered deck, by design. `stage-base.css` carries the neutral defaults on a plain `:root`, and the generated deck layer carries the plan values on `:root[data-deck]` so it survives source order. Both satisfy the audit; neither is a second token system.
- Numeric plan values are serialized with their CSS unit by the plan tool: `px` for `type` and `space`, `ms` for `motion`.

- Type and space tokens are px values authored at stage size. Do not author them in viewport units; the stage transform handles scaling.
- No hex, `rgb()`, `hsl()`, or named color literal anywhere outside `:root`. An accent used at 12 percent opacity is a derived value from the accent token, not a second hex.
- No duration, delay, or easing literal inside a keyframe, transition, or JS timing value for anything on the scaled stage. Stage motion reads from the motion tokens so the reduced-motion block and the audit tool can reason about one source. The chrome layer is the one exception, and only for the timings `stage-base.css` already fixes: `160 ms` on the tap zones, `220 ms` on the counter and the control row, and the `0s` visibility delays that keep a leaving slide painted. Chrome motion a deck adds itself takes a token.
- A web deck ships one declared palette. Do not add a `prefers-color-scheme` branch: a deck is an authored artifact with an intended look, not a themable site. A dark and a light variant are two decks or one documented token swap, declared in the design system.
- Derived tokens are allowed when they are declared in `:root` beside their source, such as a stage safe-area inset computed from the stage padding tokens.
- A buyer changing the whole deck palette must only need to edit the `:root` block. If a color change requires hunting through slide rules, the token layer failed.

## Font Policy

A display face carries most of the visual identity of a deck. Treat font delivery as a first-class decision, recorded as `delivery.fontSource`.

Allowed sources:

- `google`: Google Fonts, loaded from `fonts.googleapis.com` with `fonts.gstatic.com` preconnected. This is the default for a sent link and for any deck built on a machine with network access.
- `self-host`: `.woff2` files inside `delivery.assetsDir`, referenced with a relative path. This is the correct source for an offline room, a corporate host that blocks external font domains, or a licensed face.
- `system-stack`: no downloaded face at all. Allowed only when the user requires a single offline file with no assets folder, or when a licensing constraint forbids embedding.

Rules:

- No system font as the display face when a downloadable face is available. A system stack as the headline voice is the most recognizable mark of an unfinished deck.
- When `system-stack` is unavoidable, the display role must earn presence through weight, scale, tracking, case, and composition rather than a borrowed face, and the limitation must be stated in the receipt.
- Every family token declares a full fallback stack: the intended face, a metric-compatible substitute, then a generic family. A family token that resolves to a single name is a defect.
- Use `font-display: swap` for any downloaded face so a slow font never produces a blank stage.
- Cap the type system at 2 families and 4 total weights. Prefer one variable face with a weight axis over four static files.
- Subset self-hosted faces to the characters the deck actually uses, including the punctuation and any non-Latin range the copy needs.
- Never deliver a deck whose headline face exists only on the build machine. Open the file from a second profile or a clean browser before shipping.
- Verify the deck at the fallback stack as well. If the layout breaks when the intended face is unavailable, the fallback metrics are wrong.

## Asset Handling And Placeholders

- Relative paths only, forward slashes, no leading slash, no parent traversal, no absolute drive path, no `file://` URL, no local build path. Every reference must resolve after the folder is zipped, emailed, and extracted somewhere else.
- Media slots in a source deck use role-specific text clue placeholders exactly as required by `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`. The `media[].placeholder` string from the plan is the visible delivered text.
- Use the established wording patterns: `image placeholder: product dashboard screenshot`, `profile photo placeholder: founder portrait`, `chart placeholder: revenue trend`, `diagram placeholder: workflow steps`. Vague wording such as `image here` fails.
- Each slot declares its aspect through `media[].aspect` and keeps the frame, crop box, caption, and replacement logic fully designed while empty. A placeholder slot must look intentional, not unfinished.
- Do not generate or embed real imagery in a source deck unless the user explicitly asked, supplied the assets, or requested a preview, cover, or demo artifact. When a requested preview uses finished imagery, the source slots stay labeled and editable.
- Inline SVG for logos, icons, motifs, and diagrams; raster only for photographic or screenshot content.
- Every real image carries meaningful `alt`. Every placeholder frame exposes its clue text to assistive technology rather than hiding it in a background image.
- Video and audio are allowed only when the user asked for them, always with `assetsDir` delivery, never autoplaying with sound, and always with a still frame that carries the slide if playback fails.

## Size Budget

Weight is a delivery feature. A deck that takes eight seconds to paint has already lost the first slide.

- Single-file deck with placeholder media: target under 250 KB, hard ceiling 1 MB.
- Deck with an assets folder: HTML document under 400 KB, each raster asset under 400 KB, total package under 10 MB.
- Full-bleed raster media: 1920 px wide maximum. Use 2x only where the slot renders small.
- Do not inline a raster above 100 KB as a data URI. Promote it to `delivery.assetsDir` and switch `singleFile` to false.
- Self-hosted font files: under 120 KB per subset face.
- Above any ceiling, report the actual number and the reason before delivering. Silently shipping a 40 MB deck is a delivery defect; shipping a documented 12 MB deck the user approved is not.

## Deck Chrome Outside The Stage

Chrome is the runtime furniture around the slide: progress, page number, navigation controls, and the notes pane. It is governed by the plan `chrome` flags: `progress`, `pageNumber`, `deepLink`, `notesPane`.

- Chrome lives outside the scaled stage element, in its own fixed layer. It is never a child of the transformed stage.
- Chrome is sized in px or viewport units at render scale, not in stage px, so it stays legible when the stage scales down and never grows absurd when the stage scales up.
- Chrome never overlaps the slide safe area and never covers content at any viewport ratio, including a tall pillarboxed window.
- Every control is keyboard reachable, has a visible focus state, and carries an accessible name. A pointer-only control row is a defect.
- All chrome is hidden in print.
- Defaults: progress on, page number on, notes pane off for a sent link and on only when the user asks for a live presenting aid.
- Chrome must be designed into the visual system, not bolted on. A stock bar plus dot row plus corner number is the template-feeling chrome named in `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md`, and chrome must never be the only thing identifying the deck.

## Deep Links And Speaker Notes

- The deck reads `#<n>` on load as a 1-based slide number and calls `history.replaceState` on every slide change, per the runtime contract. Out-of-range numbers clamp to the nearest valid slide; non-numeric fragments are ignored and the deck opens at slide 1.
- Sharing a specific slide means sharing the URL with its fragment. Verify that a copied URL reopens the same slide in a new tab before delivery.
- Deep linking means every slide is a possible first impression. A slide that only makes sense after the previous one fails the sent-link use.
- Speaker notes come from `slides[].notes`. Delivery options are a hidden notes pane toggled by a key, or omission of notes from the delivered file entirely.
- Notes are shipped inside the file. Anyone who opens the source can read them. Never place pricing floors, internal numbers, client names, negotiation posture, or any confidential line in `notes` on a deck delivered as a public or forwarded link. State this warning to the user whenever notes are populated.
- When a public link and private notes are both required, deliver two files: the public deck with notes stripped, and the presenter deck with notes present.
- Notes are excluded from print unless the user asked for a notes handout, which is a separate print path and a separate statement in the receipt.

## Print To PDF

A web deck must survive the browser print path and become a clean one-slide-per-page PDF.

- The print block sets `@page { size: 1920px 1080px; margin: 0 }`, removes the stage transform, forces every slide visible, applies `break-after: page`, and hides all chrome.
- Verify the result, do not assume it. Print to PDF and count the pages against the slide count. A blank page, a doubled slide, or a cropped edge is a build defect.
- Buyer instructions to include in the delivery note: use the browser print dialog, landscape orientation, margins none, background graphics enabled, scale at default.
- What degrades, and must be stated rather than hidden: every reveal collapses to its final state; slide transitions, loops, and video disappear; hover and focus states never appear; chrome and progress are gone; the notes pane is absent; a downloaded font must be fully loaded before the dialog opens or the PDF falls back.
- Consequence for planning: a deck whose argument only works while things move fails the handout test. When `delivery.pdfExport` is true, `densityMode` should be `reading_first` and reveal counts should be near zero.
- When `delivery.pdfExport` is true, the PDF is a named deliverable and must be checked page by page. When it is false, the print block is still mandatory, because a reader will press print regardless.

## Share And Deploy

- Primary check: open the delivered file from the file system by double click, in a clean browser profile, with the network disabled when `fontSource` is `self-host` or `system-stack`. The deck must be fully usable.
- A deck that only works through a local server is not delivered. No module script that a `file://` origin rejects, no fetch of a sibling JSON, no import map.
- Static hosting is the second path: upload the HTML document and the assets folder together, preserving relative paths and folder name. No rewrite rules, no base path configuration.
- File transfer: a single-file deck must stay under the attachment limit of the channel the user named. State the file size when handing over.
- Naming: `<deckId>.html`, lowercase slug from the plan `deckId`. No spaces, no version suffix soup, no date stamp unless the user asked.
- Nothing in the deck phones home. No pixel, no beacon, no font loaded from a host other than the declared source, no external favicon.

## Editability Rules

A buyer must be able to change content without breaking the stage, without reading the runtime, and without a designer.

- One slide is one section element with a stable `id` taken from `slides[].id`. Slide order in the document is slide order in the deck.
- The runtime discovers slide count at load. No count is hardcoded in CSS or JS. Deleting a slide element leaves a working, correctly renumbered deck; duplicating one adds a working slide.
- Reveal steps are declarative attributes or classes on slide children, matching the step ids in `revealOrder`. Adding or removing a child must not require editing index math in JS.
- Text lives between tags. Never in a background image, never in CSS `content`, never baked into a raster.
- No fixed heights on text blocks. A headline at 150 percent of its planned length must stay inside the safe area; test that state and document the practical line limit per archetype.
- Swapping a media slot means replacing one placeholder element or one file in `delivery.assetsDir`. The crop, aspect, and frame hold without further edits.
- Place a short comment header at the top of the document marking where tokens live, where slides begin, how to add a slide, and how to replace an image. Four orientation lines, not a manual.
- The full edit guidance belongs in the design system and the receipt per `.design-brain/DESIGN_SYSTEM_BUILD_REQUIREMENTS.md`, including the documented limits of what cannot be changed safely.
- Run the buyer edit stress test before delivery: change the palette from `:root` only, double a headline length, replace a bullet list of three with six, delete a slide, add a slide by duplication, and swap a landscape media slot for a portrait one.

## Delivery Defects That Block Completion

Any one of these blocks final READY. Repair the artifact; do not reclassify the defect as a limitation. Each one is a `P0` and therefore a BLOCKED gate and a BLOCKED receipt, under the single severity and status mapping in `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`.

- An absolute path, drive letter, `file://` URL, parent traversal, or build-machine path anywhere in the file.
- An external script or stylesheet from a CDN, or any external request other than the declared font source.
- A color, type, space, or motion value declared outside the `:root` token layer, other than the chrome timings `stage-base.css` fixes.
- A contract token missing from `:root`, which the static audit raises as the P0 `token-layer-root`.
- A system font used as the display face without a user-required offline or licensing constraint.
- A family token with no fallback stack, or a deck that breaks when the intended face is unavailable.
- `display` toggling used for slide switching instead of the visibility, opacity, and pointer-events contract.
- A missing `@media (prefers-reduced-motion: reduce)` block, or JS motion that animates without checking the same query.
- A missing print block, or a print result that is not one slide per page.
- Chrome rendered inside the scaled stage, overlapping the safe area, visible in print, or unreachable by keyboard.
- Generated or stock imagery in a source deck without an explicit user request.
- A media slot with vague, missing, or non-role-specific placeholder text.
- A hardcoded slide count, or a runtime that breaks when the buyer deletes or duplicates a slide.
- Confidential content left in `slides[].notes` on a deck delivered as a public or forwarded link.
- A deck that only opens correctly through a local server.
- A payload over the stated ceiling with no number reported and no user approval.
- `chrome.deepLink` true with no fragment read on load or no `history.replaceState` on change.
- `delivery.assetsDir` populated while `singleFile` is true, or `null` while assets exist on disk.
- A plan `delivery` object that disagrees with the built file.
- Any third-party slide tool, plugin, repository slug, author handle, or template-pack name in the delivered file, its comments, or its metadata.
- A motion signature that hard-fails a motion similarity axis against the reference or an accepted prior deck: `entranceFamilySimilarity`, `transitionFamilySimilarity`, `revealGrammarSimilarity`, `accentMoveSimilarity`, `roleMotionMappingSimilarity`, or `overallMotionSignatureRisk`, scored to the thresholds in `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`. Re-timing it is not a repair.

## Decision Rule

Never validate a web deck by screenshot alone. The artifact must also be opened from the file system, driven by keyboard, deep-linked, printed, and checked with reduced motion active before delivery is claimed.

This contract is a delivery gate for one medium. It cannot override user explicit instruction, the owner guard, `.design-brain/DESIGN_COGNITION_CONTRACT.md`, `.design-brain/DESIGN_SIMULATION_LAYER.md`, `.design-brain/SEQUENTIAL_LAYOUT_ORIGINALITY_GATE.md`, `.design-brain/BUILD_SESSION_LIFECYCLE.md`, `.design-brain/DESIGN_SYSTEM_BUILD_REQUIREMENTS.md`, `.design-brain/POST_BUILD_COMPLETION_GATE.md`, or completion receipt status. A clean delivery check never raises a final status that those gates hold down.
