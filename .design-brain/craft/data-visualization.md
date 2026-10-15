# Data Visualization Craft

- Match chart type to question: comparison, trend, distribution, composition, ranking, or relationship.
- Label axes, legends, units, dates, and deltas.
- Use restrained chart palettes; reserve accent for the point that matters.
- Do not invent metrics unless clearly marked as placeholder sample data.
- Dashboards need scan hierarchy before visual drama.
- Deck charts need thumbnail-readable labels and one takeaway.
- Tables need sorting/filtering meaning, row actions, and empty/error behavior when interactive.
- For web decks, chart labels, axes, and legends are authored at stage size and read at projection distance, not at browser-UI size.
- For web decks, an animated chart ends on the true values and rests there; a mid-animation frame is never the resting state.
- For web decks, a count-up prints its final number statically as well, so a paused or reduced-motion view still reports it.
- For web decks, draw-on follows the chart's own reading order: axis and scale first, then series, then annotation.
- For web decks, no chart polls a live source; the deck runs from a file, so figures are baked and dated on the slide.
