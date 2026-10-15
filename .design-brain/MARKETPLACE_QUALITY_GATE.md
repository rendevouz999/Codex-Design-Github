# Marketplace Quality Gate

Use this gate before calling a template product marketplace-ready.

If any gate fails, use `.design-brain/QUALITY_GATE_FAILURE_TAXONOMY.md` and output: PASS/FAIL, failure category, evidence, root cause, required action, and whether rebuild, recompose, recolor, rewrite, or source repair is needed.

## Post-Build Marketplace Readiness

Marketplace readiness requires post-build evidence:

- design system exists and is tied to the template
- source hygiene is checked
- auto-layout/editability/placeholder rules are checked for source templates
- visual/layout defects are checked
- batch products pass pairwise similarity audit
- completion receipt records READY, READY_WITH_LIMITATIONS, REVISE_REQUIRED, or BLOCKED

## Design Cognition Marketplace Readiness

Marketplace readiness must be grounded in the Design Cognition Receipt. Style DNA, Design Intent Lock, Visual Grammar, Reference Boundary, Color Role Re-Mapping, Visual Mood Reinterpretation, Structural Reconfiguration, Pattern Divergence, Section Logic, and Marketplace Readiness are required before orchestration/build. If the receipt is missing or vague, the marketplace gate fails.

## Score Each Area From 1 To 10

| Area | Score | What To Check |
| --- | --- | --- |
| Product clarity | /10 | Template type, niche, buyer, and promise are obvious. |
| Buyer fit | /10 | The design solves a real buyer need and fits the category. |
| Section completeness | /10 | Required screens, sections, components, and states are included. |
| Visual differentiation | /10 | It avoids generic template patterns and has a memorable point of view. |
| Editability | /10 | Text, images, components, styles, and sections are easy to reuse. |
| Preview quality | /10 | Cover and marketplace previews sell the product clearly. |
| Responsive readiness | /10 | Desktop, tablet, and mobile behavior is considered or shown. |
| Typography quality | /10 | Type scale, hierarchy, and content density feel polished. |
| Spacing and alignment | /10 | Layout rhythm is consistent, clean, and intentional. |
| Component consistency | /10 | Repeated elements share clear rules and states. |
| Accessibility basics | /10 | Contrast, sizing, states, and readability are practical. |
| Commercial polish | /10 | The product feels premium enough to sell. |
| Medium fit | /10 | The template follows the correct logic for website, deck, dashboard, UI kit, brand kit, or preview. |
| Originality strength | /10 | The product reinterprets references and avoids repeated structure, motif, and preview staging. |
| Human craft | /10 | The design shows intentional rhythm, hierarchy, restraint, and buyer-specific judgement. |
| Design simulation verdict | /10 | Pre-build simulation passed, with no unresolved minimalist, scaffold, Envato, source hygiene, or originality blockers. |

## Pass Criteria

- No area below 7 for a serious marketplace release.
- Product clarity, editability, preview quality, and commercial polish should be 8 or higher.
- Medium fit and originality strength should be 8 or higher for reference-based or batch work.
- Any area below 7 requires revision before final delivery.
- Do not pass a template if it only looks good in one hero image but lacks reusable structure.

## Hard Fails

- Buyer or category is unclear.
- The product feels like a generic section stack.
- Preview images hide the actual template quality.
- Components cannot be edited or reused cleanly.
- The design system is sparse, receipt-only, or lacks concrete foundations, components, states, patterns, and editability guidance.
- Spacing, type, or alignment changes randomly across sections.
- The cover does not communicate the product value clearly.
- Responsive behavior is ignored for a template that buyers expect to adapt.
- Figma/source-template output lacks real auto-layout, layer/component naming, placeholder, responsive/editability, or source hygiene receipts.
- A visual similarity pass is claimed without screenshot, render, or visual inspection evidence.
- A marketplace template was built after the Design Simulation Layer returned `REVISE` or `BLOCKED`.
- A batch/repeated template reuses an accepted prior structure fingerprint without a fresh scaffold disposal.
- A marketplace template skips Sequential Layout Originality Gate when it is reference-led, batch, Figma/source, or required to be distinct.
- A template copies its reference layout or matches a previous AI output on a structure-defining axis.
- The final receipt lacks reference layout audit result, AI pairwise layout audit result, or fingerprint lock status.
