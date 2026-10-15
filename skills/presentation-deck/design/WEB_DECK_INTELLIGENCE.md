# Web Deck Intelligence

Use this file for web decks, HTML presentations, browser-rendered slide systems, animated browser decks, single-file presenter decks, webinar decks, demo-day decks, and PPTX-to-web conversions. Explicit PowerPoint/PPTX output, including PowerPoint animation, uses `skills/presentation-deck/workflows/native.md`. For Google Slides, Keynote, and Figma Slides artifacts, use `skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md`. If both native and browser outputs are requested, deliver each through its own workflow.

## Core Principle

A web deck is a fixed 16:9 stage rendered by a browser runtime. The authored stage is `1920 x 1080` px and it is scaled as one unit to fit the viewport. It is not a scrolling website, and it is not a PPTX export dressed in CSS.

Those two mistakes produce the two failure modes of the medium. A deck built like a website reflows, stacks, grows a nav, and loses the single-frame discipline that makes a slide readable in four seconds. A deck built like a PPTX export ignores reveal order, runtime navigation, and reduced-motion duty, and ships a static image set that happens to live in a browser.

The product value is the slide system plus the runtime behavior around it: how the stage fits, how the audience moves, what appears when, and what the deck does when motion is switched off.

## What Carries Over From Deck Intelligence

Every judgment layer in `skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md` still applies. Do not re-derive it here; load it alongside this file for any web-deck build.

- Slide roles and the slide role matrix. A web deck needs cover, agenda, divider, problem, solution, proof, data, team, closing, and the same role completeness test.
- Pace. Fast-read, slow-read, rest, emphasis, and climax slides. Browser delivery does not excuse a flat tempo.
- Energy distribution. Loud, quiet, functional, emotional, and climactic slides, with intentional contrast.
- Slide economy. An element that does not carry communication value is removed, not animated.
- Thumbnail rhythm. Slide silhouettes must stay distinct and non-monotone as a contact sheet, because a browser overview or a print sheet exposes repetition instantly.
- Density control. Light, medium, dense, visual-break, data-heavy, and image-heavy slides planned across the run.
- Visual silence, attention control, reduction, editorial thinking, visual trust, and the why-first critique.
- Edit stress tests. Longer titles, translated copy, portrait and landscape media, three bullets becoming six, bright and dark logos.

## What Is New In The Web Medium

Four planning primitives exist only here. Each one must be decided in the plan, not discovered during the build.

- Reveal order inside a slide. A slide is a timed sequence, not a single state. Reveal order is planned per slide as `revealOrder` in `skills/presentation-deck/resources/web-deck/deck-plan-schema.json`.
- Runtime navigation. Keyboard, pointer, wheel, deep link, and the public runtime API are part of the design. Navigation affordances must be legible without instruction.
- Motion signature. The identifiable motion behavior of the deck: entrance verbs, distance, duration band, stagger cadence, easing, accent moments, and slide transition. It is declared as `motionSignature` in the plan and governed by `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`.
- Viewport fit. Content never reflows. It scales. A slide that needs reflow to stay readable is a slide that was overfilled, and the fix is editorial, not responsive. Stage discipline is enforced by `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`.

Two further realities shape the plan: reduced motion is a first-class state, not a fallback, and print is a real output path that strips every sequence to its final frame.

## Density Mode Decision

`densityMode` is the first content decision of a web deck build, before slide count, type scale, or layout. It is a required plan field with exactly two values: `speaker_led` and `reading_first`. Ask who reads the deck and whether a human is talking over it. Never average the two modes; a deck that hedges between them is unreadable alone and unspeakable live.

The slide-count, word, headline-word, support-item, light-ratio, and dense-allowance numbers in the two mode sections below are the budgets `skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs` enforces as the P1 findings `slide-count-budget` and `slide-density-budget`, and it only applies them when a deck plan is supplied with `--plan`. Type scale and reveal step counts are not tool-enforced and are verified by review. A second, archetype-specific cap sits beneath the support-item budget: the per-archetype zone capacity the audit reports as `overflow-text-budget`. The lower of the two always applies, so a 6-slot `agenda` or `dashboard` row still stops at 5 items in `reading_first` and at 3 in `speaker_led`.

### Mode `speaker_led`

The slide supports a voice. The audience looks up, reads one idea, and returns to the speaker.

- Slide count: 12 to 20 slides for a 20 to 30 minute talk. Budget 60 to 90 seconds of speech per slide.
- Words per slide: 25 on-stage words maximum, counting the headline, the support items, and any footnote. Headline 8 words maximum.
- Support items: 3 maximum per slide, counting bullets and cards alike, plus 1 chart or 1 media slot.
- Type scale at stage size: `displaySize` 96 to 140 px, `leadSize` 44 to 56 px, `bodySize` 32 to 40 px, `captionSize` 22 to 26 px. The absolute floor for body text is the `28 px` neutral default in `skills/presentation-deck/resources/web-deck/stage-base.css`; a deck authored below the band must state why.
- Reveal steps: 1 to 5 per slide, per the step budget in `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`. Most slides need 1 or 2.
- Density mix: at least 60 percent of slides marked `light`, no more than one `dense` slide per ten.
- Stat and quote slides are expected. A single number at display scale with space around it is a complete slide in this mode.

### Mode `reading_first`

The slide is read without a narrator: a sent link, a leave-behind, a proposal, an async update, a PDF handout.

- Slide count: 18 to 32 slides. The deck must answer the obvious follow-up question on the slide, not in the room.
- Words per slide: 55 to 90 on-stage words. 90 is the enforced ceiling; 55 is a floor for the reading use, verified by review rather than by tool. Headline 12 words maximum, written as a takeaway, not a label.
- Support items: 5 maximum per slide, counting bullets and cards alike, plus 2 charts or a chart with a caption block.
- Type scale at stage size: `displaySize` 64 to 88 px, `leadSize` 34 to 40 px, `bodySize` 24 to 28 px, `captionSize` 18 to 20 px. Body never below 24 px.
- Reveal steps: 0 to 2 per slide, per the step budget in `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`. Default to no reveal, because nobody is driving the build.
- Density mix: `medium` is the default marking, `dense` is allowed up to one slide in four, and every `dense` slide needs a `light` neighbor.
- Section dividers and a working agenda matter more here, because the reader navigates and skims instead of following a voice.

### What The Mode Changes Downstream

- Caption and label sizes set the floor for every chart axis, legend, source line, and footnote.
- A `speaker_led` deck can carry an unexplained visual; a `reading_first` deck cannot, so every media slot needs a caption that states the point.
- A `reading_first` deck must be complete at print, which caps reveal usage.
- A deck asked to serve both uses is built `reading_first` and presented from it, or split into two decks. State the tradeoff instead of silently splitting the difference.

## Reveal And Build Order Model

Progressive disclosure within a slide is a planning primitive, equal to layout. Plan it per slide before build, as an ordered list of step ids in `revealOrder`.

- Step one is the anchor the audience must read first, usually the headline or the single number. It is present on arrival and it never animates away.
- Reveal order follows the intended attention path, not DOM order and not top-to-bottom by default. If the attention path starts at a chart and ends at a conclusion line, the chart reveals first even though the conclusion sits higher in the layout.
- Every step must change what the audience can answer. A step that re-states a visible idea is decoration, and decoration animated is still decoration.
- Steps carry argument joints: claim, then evidence, then consequence. A comparison reveals the baseline before the delta. A timeline reveals the present before the projection.
- Hard cap: 5 steps per slide in `speaker_led`, 2 in `reading_first`. The budget is owned by `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`; do not restate a different number here. A slide needing a sixth step is a slide holding two arguments. `skills/presentation-deck/runtime/web/design_brain_web_deck_plan.mjs` rejects more than 12 steps, the number of stagger slots the stylesheet declares; 5 is the editorial cap this module requires and it is verified by review, not by tool.
- A reveal is a crutch when it hides density instead of sequencing meaning. Diagnostic questions: does the final state of this slide read as one idea, or as a wall that was only tolerable because it arrived in pieces? Does any step introduce a new subject instead of advancing the current one? Does the speaker need the build to stop the audience reading ahead to a contradiction? Three yes answers mean split the slide.
- A reveal is also a crutch when it compensates for a weak layout. If the slide is only interesting while things are moving, the composition failed and motion is masking it.
- Reveals are driven by a class on the active slide, never by scroll position. Scroll-driven reveal belongs to the website medium.
- Every slide must be correct and complete in its fully revealed state, because deep link, print, reduced motion, and a reader who taps ahead all land there.
- Reduced motion resolves every step immediately. The deck must lose nothing but the timing.

## Presenter Reality

The same slide plan behaves differently in three delivery situations. Decide which one the deck is for, and state it in the plan and the receipt.

### Live Presentation

- The speaker is the narrator. `speaker_led` density, generous reveal use, a visible motion signature, confident display scale.
- Navigation must survive a clicker, which sends arrow keys or page keys. Pointer taps and wheel steps are secondary.
- Legibility is judged from the back of a room. Test the stage at a small viewport, because a projector at a poor resolution behaves like a scaled-down stage.
- Chrome is minimal. A progress indicator helps the speaker; a dot row distracts the audience.
- Speaker notes live in `slides[].notes` and surface through the optional notes pane.
- Room risk is real. Plan for no network, a stale browser, and a display that clips edges. Keep content inside the safe area and keep fonts available offline.

### Sent Link

- No narrator. `reading_first` density, reveals near zero, takeaway headlines, captions on every visual.
- Navigation must be self-explanatory to someone who has never used a web deck: a visible next affordance, working deep links, and a page number so the reader knows how much is left.
- The reader arrives on any slide, at any viewport, often on a laptop at half the stage width. Every slide must be a legitimate entry point.
- Everything in the file is shipped, including notes. Treat `notes` as public on a sent link.

### PDF Handout

- The deck is printed to PDF and becomes a static document. Every reveal collapses, every transition disappears, and no hover state ever occurs.
- Slide count becomes page count, and a 32-page handout reads differently from a 32-slide run. Check the handout as a document, not as a deck.
- `reading_first` is mandatory when the PDF is the primary artifact. A `speaker_led` deck printed as a handout produces a stack of orphan headlines, and that must be stated as a limitation instead of delivered as a document.
- Any slide whose meaning depends on sequence must still read as a single frame.

## Web Deck Originality Risks

Layout originality rules still apply in full. This medium adds a second fingerprint: motion.

- Cliche motion sets. Bounce entrances on everything, long springs, typewriter headlines, counting-up numbers on every stat slide, parallax on every background, full-slide 3D flips, particle fields, confetti, and gradient blobs drifting behind every section. Each one reads as a default, and a deck built from defaults has no motion identity.
- Reveal-everything decks. Giving every element its own step is the motion equivalent of bolding every word. It signals that no attention path was chosen.
- Identical entrance on every slide. One entrance verb repeated 24 times is motion monotone, and it flattens pace exactly the way uniform slide density flattens it. Entrance behavior should vary with slide role: a cover arrives differently from a data slide, and a divider should reset energy instead of repeating it.
- Template-feeling chrome. A generic progress bar, a dot row, and a corner page number is the stock signature of the medium. Chrome is part of the design or it is absent.
- Motion replacing structure. Motion used to make a weak layout feel designed, to disguise unclear hierarchy, or to manufacture interest a composition failed to create. Remove the motion and judge the still frame; if the still frame is dull, fix the composition.
- Copied motion signature. Reusing the entrance verbs, distance, duration band, stagger cadence, easing curve, accent moment placement, and slide transition of a reference deck or of an earlier deck in the session is an originality defect of the same class as a copied layout fingerprint. Re-timing and recoloring are not repairs, exactly as recolor is not a repair for layout similarity. A real repair changes which elements move and which stay, the reveal grammar, the accent moment, the transition family, and the relationship between motion and slide role.
- Motion signature drift inside one deck. Five unrelated motion languages across one deck is not variety; it is an unplanned system.
- Audit motion similarity axis by axis against the reference and against every earlier deck in the session, using the named axes and thresholds in the Motion Similarity Axis Rules section of `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`, the way layout similarity is audited in `.design-brain/SEQUENTIAL_LAYOUT_ORIGINALITY_GATE.md` and `.design-brain/LAYOUT_SIMILARITY_AXIS_RULES.md`. A high single axis cannot hide behind a comfortable overall score.

## Deck Design System Scope For A Web Deck

A web deck design system is a buyer-usable kit, built to the standard in `.design-brain/DESIGN_SYSTEM_BUILD_REQUIREMENTS.md`. Scope it to this medium:

- Token layer. Color roles, type roles at stage size, space scale, and motion tokens, declared once in `:root` and nowhere else. The token key set is fixed by `skills/presentation-deck/resources/web-deck/deck-plan-schema.json`, and the CSS custom properties are `--deck-<group>-<key>` with the plan's exact camelCase spelling, listed in full in `skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md`.
- Archetype set. Every slide archetype used by the deck, each with a named layout, a stated role, a safe area, a declared density marking, and a documented content capacity.
- Motion tokens. `entranceMs`, `transitionMs`, `staggerMs`, `easing`, and `transition`, plus the reduced-motion resolution of each one. A motion value hardcoded in a keyframe instead of a token is a system defect.
- Chrome specification. Which chrome flags are on, what each one looks like, where it sits outside the scaled stage, how it behaves on focus, and how it disappears in print.
- Media placeholder rules. Role-specific text clue placeholders per `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`, each with a declared aspect, crop intent, caption rule, and replacement guidance.
- State and empty-data rules. Long headline, translated copy at twice the length, a one-item list, an empty chart, a zero or negative value, a missing logo, an unreplaced placeholder, and a slide deleted by the buyer. Each state needs a defined visual outcome.
- Accessibility rules. Contrast intent per color pairing, keyboard-only operation, visible focus on every control, accessible names on chrome, and the reduced-motion contract.
- Editability rules. Which parts a buyer edits, how to add or remove a slide, and the documented limits, as specified in `skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md`.

## Reference Learning Order

When studying one or many web-deck references, work in this order:

1. Use context: live talk, sent link, or handout. Everything else depends on this answer.
2. Density mode: does the reference speak or read, and does its word count agree with its claim?
3. Story flow and slide roles: is the journey complete, and are the roles useful and distinct?
4. Stage discipline: does the content fit `1920 x 1080` without reflow, and does it stay inside the safe area at a small viewport?
5. Visual system: color roles, type roles at stage size, space scale, and media treatment.
6. Reveal logic: how many steps per slide, in what order, and does each step advance the argument?
7. Motion signature: which verbs, distances, durations, stagger cadence, easing, and accent moments identify this deck, and would copying them be detectable?
8. Runtime behavior: navigation affordances, deep link, reduced motion, and print.
9. Thumbnail rhythm: do the slide silhouettes stay varied as a contact sheet?
10. Delivery readiness: single file or assets, fonts, weight, editability, and what a buyer has to change.

A reference may teach pace, discipline, hierarchy, and emotional control. It must not supply the slide order, the composition grammar, or the motion signature.

## External Source Anchors

- MDN: the `prefers-reduced-motion` media query exposes a user or operating-system preference for reduced motion, and pages are expected to honor it.
- MDN: a CSS transform such as `scale` applies to an element and its descendants without re-laying out the children, which is what lets a fixed stage scale as one unit.
- W3C WCAG 2.2: success criterion 1.4.3 Contrast (Minimum) sets contrast ratio thresholds for text, with a lower threshold for large text.
- W3C WCAG 2.2: success criterion 2.1.1 Keyboard requires all functionality to be operable through a keyboard interface.
- W3C WCAG 2.2: success criterion 2.2.2 Pause, Stop, Hide requires a mechanism to pause, stop, or hide moving content.
- Microsoft PowerPoint: slide size is a fixed canvas with 16:9 widescreen as the standard, which is the same single-frame constraint a web deck stage inherits.

## Non-Override Rule

This module is judgment and planning intelligence for one medium. It is not a gate and it cannot relax one.

It must not override:

1. user explicit instruction
2. owner guard
3. `.design-brain/DESIGN_COGNITION_CONTRACT.md`
4. `.design-brain/DESIGN_SIMULATION_LAYER.md`
5. `.design-brain/SEQUENTIAL_LAYOUT_ORIGINALITY_GATE.md`
6. `.design-brain/BUILD_SESSION_LIFECYCLE.md`
7. `.design-brain/DESIGN_SYSTEM_BUILD_REQUIREMENTS.md`
8. `.design-brain/POST_BUILD_COMPLETION_GATE.md`
9. completion receipt status

If web-deck judgment conflicts with any of those, the gate wins and the judgment becomes a repair suggestion only. A motion or reveal decision can never be the reason a required gate is skipped, and no density mode, stage choice, or motion signature can raise a final status above what the gates allow.

## Acceptance Criteria

- `densityMode` is declared, justified by the real use context, and consistent with slide count, type scale, word count, and reveal count.
- The deck has at least 10 distinct slide-role layouts for a serious template.
- Each slide carries one primary idea, and its fully revealed state still reads as one idea.
- The stage is the authored `1920 x 1080`, content never reflows, and nothing crosses the safe area at a small viewport.
- `revealOrder` exists per slide, follows the intended attention path, and stays inside the step budget for its `densityMode`: 5 steps in `speaker_led`, 2 in `reading_first`.
- No slide depends on motion to be understood, and every slide is complete in its final state.
- Reduced motion resolves every reveal and transition without losing content.
- The motion signature is declared, role-aware, varied across slide roles, and audited against the reference and every earlier deck in the session.
- Entrance behavior is not identical on every slide, and no cliche motion set is present.
- Chrome is designed, lives outside the scaled stage, is keyboard-operable, and is hidden in print.
- Navigation is self-explanatory for the declared delivery situation, and deep links resolve to a legitimate entry point.
- Print produces one slide per page, and the degradation list is stated instead of discovered by the buyer.
- Pace, energy distribution, slide economy, and thumbnail rhythm pass the standards in `skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md`.
- Density mix matches the declared mode, with planned light and rest slides.
- Media slots use role-specific text clue placeholders with declared aspect and caption rules.
- Empty-data, long-copy, translated-copy, missing-logo, and deleted-slide states have defined outcomes.
- The design system covers tokens, archetypes, motion tokens, chrome, placeholders, states, accessibility, and editability.
- A buyer can change text, swap a media slot, and add or remove a slide without touching CSS or JS and without breaking the stage.
- The deck opens from a double click with no server, no build step, and no CDN script.
- Delivery passes `skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md`, stage fidelity passes `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`, and motion passes `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`.
- For a converted source deck, the conversion is judged by `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md` and rebuilt as a web deck instead of mirrored slide for slide.
- The deck works as a communication instrument under a speaker, as a link, and as a document, or the unsupported uses are named as limitations.
