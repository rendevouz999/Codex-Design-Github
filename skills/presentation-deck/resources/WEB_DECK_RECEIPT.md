# Web Deck Receipt

Status vocabulary: the tools emit `P0` / `P1` findings, the stage gate emits `PASS` / `REVISE` /
`BLOCKED`, and this receipt emits the final status on the last line. The one mapping between them
is the Severity And Status Mapping section of `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`. Do not derive
a different one here.

- Deck ID:
- Deck title:
- Deck artifact path:
- Deck plan path:
- Density mode: speaker_led / reading_first
- Style pack:
- Direction pack:
- Motion signature ID:
- Slide count:
- Archetype mix:
- Reveal step count (max per slide, against the `densityMode` budget):
- Stage gate result: PASS / REVISE / BLOCKED
- Stage gate evidence:
- Static audit result: PASS / BLOCKED / NOT_RUN
- Static audit findings: _ P0, _ P1
- Static audit evidence:
- Render review result: PASS / FAIL / NOT_RUN
- Render review findings: _ P0, _ P1
- Render review evidence:
- Per-slide overflow/overlap/clipping check: PASS / FAIL / NOT_RUN
- Narrow-viewport letterbox check: PASS / FAIL / NOT_RUN
- Reduced-motion check: PASS / FAIL / NOT_RUN
- Print/PDF check: PASS / FAIL / NOT_RUN
- Deep-link check: PASS / FAIL / NOT_RUN
- Dependency check: PASS / FAIL / NOT_RUN
- Motion similarity axes, scored per `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`:
  - entranceFamilySimilarity:
  - transitionFamilySimilarity:
  - easingCurveSimilarity:
  - staggerRhythmSimilarity:
  - accentMoveSimilarity:
  - revealGrammarSimilarity:
  - motionAmplitudeSimilarity:
  - durationBandSimilarity:
  - roleMotionMappingSimilarity:
  - chromeMotionSimilarity:
  - reducedMotionStateSimilarity:
  - signatureDefiningAxisSimilarity:
  - timingLanguageAxisSimilarity:
  - overallMotionSignatureRisk:
  - hardFailAxes:
  - softRiskAxes:
- Originality notes (motion signature divergence, at least 3 of the 5 signature axes at or below
  `0.25`):
- Visual verification status: screenshot/render verified / source heuristic only / not visually verified
- Repair cycles:
- Remaining issues:
- Final status: READY / READY_WITH_LIMITATIONS / REVISE_REQUIRED / BLOCKED
- Completion statement:
