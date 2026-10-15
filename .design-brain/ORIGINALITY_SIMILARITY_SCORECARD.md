# Originality Similarity Scorecard

Use this scorecard before presenting reference-based or batch template work. The purpose is to catch copy-paste structure before the user has to point it out.

For batch work, score two kinds of similarity:

1. Current template vs its active product-purpose reference group.
2. Current template vs locked patterns from previous batch cycles.

Do not wait until the whole batch is complete. Check similarity after each template before starting the next cycle.

Text heuristics are not visual proof. If no screenshot, render, browser view, or Figma screenshot was inspected, the output must say: `Visual similarity not verified; only textual/structural heuristic checked.`

For cross-template batch audits, use a stricter gate than reference audits:

- Compare the current template against every accepted earlier template.
- If the current template reaches 10 percent similarity against any earlier template, the current template fails.
- The earlier template remains the accepted fingerprint unless it has its own quality defect.
- Diagnose the similarity root cause before revising.
- Rebuild the current template from a fresh structure fingerprint when structure-defining axes fail.
- If the only failing axis is color-role mapping, recolor the current template and rerun the audit.
- If the only failing axis is copy/naming rhythm, rewrite the current template copy/name and rerun the audit.

## Score Meaning

- 0-2: low similarity risk.
- 3-5: moderate similarity risk; revise if the reference is recognizable.
- 6-8: high similarity risk; redesign structure before final.
- 9-10: direct clone risk; do not present.

## Similarity Axes

Score each axis from 0 to 10:

| Axis | What To Compare |
| --- | --- |
| Section or slide order | Same sequence of content roles. |
| Composition | Same hero/slide arrangement, alignment, and balance. |
| Spacing rhythm | Same dense/open cadence, card gaps, margins, and section heights. |
| Visual motif | Same decorative shape, line, pattern, gradient, or image treatment. |
| Component grouping | Same card groups, metric clusters, profile blocks, pricing rows, or proof bands. |
| Title and media placement | Same title side, image side, avatar position, mockup angle, or slide title logic. |
| Color-role mapping | Same accent used for the same action, highlight, and background roles. |
| Naming and metaphor | Same words, suffixes, prefixes, and concept metaphors. |
| Marketplace preview staging | Same cover, mockup wall, detail crop, or overview composition. |
| Product-type fit | Wrongly reusing a structure from another medium. |

## Root-Cause Action Map

| Failing Cause | Required Action |
| --- | --- |
| Structure similarity | Rebuild the newer template from a fresh structure fingerprint. |
| Composition similarity | Recompose the affected sections and layout grammar. |
| Effect similarity | Redesign glow, shadow, blur, border, gradient light, surface depth, and placeholder treatment. |
| Color-role similarity only | Change palette and color-role mapping only; preserve good structure. |
| Copy/naming similarity only | Rewrite copy, labels, metaphors, and naming rhythm only. |

## Pass Rules

- Average similarity risk must be 5 or below.
- No individual axis should be above 7.
- For batch cross-template comparisons, average similarity must stay below 10 percent and no structure-defining axis should reach 10 percent.
- If section/slide order is above 6, reorder and restructure.
- If composition is above 6, change the layout grammar.
- If visual motif is above 6, replace the motif with a new system.
- If product-type fit is above 6, run the medium playbook before continuing.
- Do not use recolor to solve section, composition, component grouping, or CTA/footer similarity.
- Do not rebuild a strong structure when color-role mapping is the only failing axis.

## Required Output

When originality matters, record:

- Overall similarity risk.
- Highest-risk axes.
- What was intentionally changed.
- Required reinterpretation before final.
- Pass/fail.
- Visual verification status and evidence path/note, or the explicit limitation that visual similarity was not verified.
