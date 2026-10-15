# Motion Discipline Craft

- Motion should clarify cause/effect, hierarchy, or state change.
- Prefer short, subtle transitions over decorative loops.
- Respect reduced-motion expectations when implementation exists.
- Avoid motion that moves text while it is being read.
- For decks, motion should support reveal order and not replace structure.
- For social/video/static-canvas planning, motion notes should describe rhythm, timing, and focal sequence.
- For web decks, one motion language per deck: one transition family, one easing set, one stagger step, and a declared forbidden set.
- For web decks, every move answers what changed; a slide that spends its budget on arrival has none left for decoration.
- For web decks, chrome motion stays outside the scaled stage and keeps true UI timings, so it never scales with the slides.
- For web decks, the reduced-motion state is authored and reviewed, and both the stylesheet and the script consult the same query.
- Timing bands, travel limits, and the cliche blacklist live in `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`; this axis checks discipline, not numbers.
