# Accessibility Craft

- Treat WCAG 2.2 AA as the practical baseline.
- Use semantic controls where implementation exists: buttons, links, labels, inputs, tables.
- Ensure visible focus states and hit areas that are large enough for the platform.
- Do not communicate status by color alone.
- Keep text contrast readable on surfaces and imagery.
- For slide and preview thumbnails, accessibility includes small-size readability.
- For Figma templates, name editable layers and avoid flattening important text into images.
- For web decks, only the active slide is reachable: inactive slides stay out of the tab ring, out of the accessibility tree, and out of the hit test.
- For web decks, a slide change is announced once, and the page number, progress, and `#<n>` hash report the same position without motion.
- For web decks, every runtime control and tap zone carries an accessible name or stays out of the accessibility tree; an icon with no name is a defect.
- For web decks, a slide headline is a real heading element, so the announced slide and the document outline agree.
- For web decks, focus is never trapped by a notes pane or overlay, and navigation keys stay inactive in editable fields and under modifier chords.
- `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md` owns the mechanism behind these; this axis checks only that they hold in the artifact.
