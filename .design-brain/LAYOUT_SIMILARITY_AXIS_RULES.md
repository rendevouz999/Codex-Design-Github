# Layout Similarity Axis Rules

Layout originality must be judged axis by axis. Overall score is useful context, but it cannot hide a high-risk axis.

## Axes

1. `heroGrammarSimilarity`
2. `sectionOrderSimilarity`
3. `gridSystemSimilarity`
4. `layoutRhythmSimilarity`
5. `cardCadenceSimilarity`
6. `componentPatternSimilarity`
7. `ctaPlacementSimilarity`
8. `imageTreatmentSimilarity`
9. `spacingCadenceSimilarity`
10. `typographyBehaviorSimilarity`
11. `colorRoleSimilarity`
12. `effectLanguageSimilarity`
13. `navigationFooterPatternSimilarity`
14. `layoutGestureSimilarity`
15. `sectionSilhouetteSimilarity`
16. `sectionPatternMixSimilarity`
17. `closureSilhouetteSimilarity`
18. `compositionTensionSimilarity`
19. `focalPathSimilarity`
20. `negativeSpaceShapeSimilarity`
21. `depthLayeringSimilarity`
22. `moduleScaleVariationSimilarity`
23. `breakoutBehaviorSimilarity`
24. `overallScaffoldRisk`

## Scoring

- `0.00` means no meaningful similarity.
- `0.25` means low similarity.
- `0.50` means moderate similarity.
- `0.70` means high similarity.
- `0.85` means near clone.
- `1.00` means identical.

## Hard Fail Thresholds

- `heroGrammarSimilarity >= 0.70`
- `sectionOrderSimilarity >= 0.70`
- `gridSystemSimilarity >= 0.70`
- `layoutGestureSimilarity >= 0.70`
- `sectionSilhouetteSimilarity >= 0.70`
- `sectionPatternMixSimilarity >= 0.70`
- `closureSilhouetteSimilarity >= 0.70`
- `compositionTensionSimilarity >= 0.72`
- `focalPathSimilarity >= 0.75`
- `moduleScaleVariationSimilarity >= 0.74`
- `componentPatternSimilarity >= 0.70`
- `ctaPlacementSimilarity >= 0.75`
- `overallScaffoldRisk >= 0.65`
- any near-clone axis `>= 0.85`

The human-facing "10 percent similarity" standard means no structure-defining axis may feel more than lightly similar. The machine gate treats high axis similarity as failure even when aggregate score is lower.

The script reports:

- `structureDefiningAxisSimilarity`: max risk across hero, section order, grid, component, and CTA axes.
- `visualLanguageAxisSimilarity`: max risk across image, typography, color role, and effect axes.
- `hardFailAxes`: axes that block final readiness.
- `softRiskAxes`: axes that require revision but are not necessarily scaffold blockers by themselves.
- `scaffoldRisk` / `overallScaffoldRisk`: aggregate scaffold identity risk.

Hard fail axes block even when the aggregate score looks moderate.

## Statuses

- `PASS`
- `REVISE_REQUIRED`
- `BLOCKED`

## Repair Requirements

- If hero grammar is similar, change hero composition, media treatment, headline placement, and CTA logic.
- If section order is similar, reorder the buyer journey and section roles.
- If grid is similar, change grid architecture.
- If layout gesture is similar, change the spatial concept: editorial rail, dashboard shell, split ledger, full-bleed gallery, product stage, timeline spine, or another product-fit gesture.
- If section silhouettes are similar, recompose the visible shape sequence of major sections.
- If section pattern mix is similar, select a different catalog vocabulary and recompose the affected section roles before styling.
- If closure silhouette is similar, recompose the local proof/CTA/contact/checkout/footer ending into a different product-specific action model; do not solve it with color, copy, radius, or spacing changes.
- If composition tension is similar, change asymmetry, overlap, offset, density split, or restrained quiet logic.
- If focal path is similar, change the first-second-third attention route.
- If module scale variation is similar, change the large/small rhythm and repeated-module proportions.
- If negative-space shape is similar, change how empty space works: runway, margin well, editorial pause, product breathing room, proof separation, or scan buffer.
- If breakout behavior is similar, change where and how the layout escapes the container rhythm.
- If component cadence is similar, redesign component anatomy.
- If color role is similar, apply Color Role Re-Mapping.
- If visual grammar is similar, redefine visual grammar, surface depth, effects, and rhythm.
