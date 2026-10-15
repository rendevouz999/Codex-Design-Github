# Main review of the first three PPTX slides

Owner-approved on 2026-10-13. This policy applies only to native PPTX deck/template creation and substantial deck redesign through the custom `<CODEX_DESIGN_WORKSPACE>` plugin. It does not impose a three-slide process on other platforms, tiny existing-slide edits, or brand/token-only tasks without a slide roster.

## Required production sequence

1. Main resolves the brief, ordered slide roster, canvas, initial visual direction and required inputs. Planning the whole deck and preparing shared primitives is allowed before this gate.
2. The single GPT-6.1 Sol (Codex) / Claude Opus 5.5 (Claude Code) General Design Production Engineer, with Extra High effort (`xhigh`), authors **slides 1, 2 and 3 in their intended order**. Do not replace these with easier samples or add unrequested slides. If the entire requested deck has fewer than three slides, review all requested slides.
3. Render those slides and provide Main the source paths, preview paths and applicable technical evidence. A source-render preview can support early visual review; label its evidence type accurately and retain later native PPTX rendering/editability checks. Use a separate draft preview when necessary; do not alter the final roster or waive its checks to create a partial preview.
4. Main inspects the actual previews and relevant source/native evidence. Evaluate the slide messages, visual direction, typography and hierarchy, spacing/alignment, readability, image/context/crop, diagrams or data where present, composition variety and editability. Apply `PPTX_LAYOUT_ORIGINALITY_POLICY.md`: extract the inspected draft PPTX, compare these slides with verified prior-deck history, and record current image tone/content/purpose checks. Technical success or the Engineer's recommendation alone cannot yield creative PASS.
5. Main records **PASS**, **REVISE** or **BLOCKED** with concrete findings in the project's existing review report, or `<project>/analysis/first_three_slides_review.md` if no suitable report exists. Reference the exact reviewed slide IDs/source hashes, preview files and evidence type. This is a project review artifact. Main also saves its bounded decision and evidence pointers through the Supabase/local shared memory capability under `.design-brain/LOCAL_MEMORY_POLICY.md`.
6. **Slide 4 and later must not be authored or batch-generated until Main records PASS for all three initial slides.** On REVISE, the same Engineer repairs the affected slides; Main reviews the new previews and records the result. On missing evidence, repair the specific gap. Do not equate elapsed time or silence with approval.
7. After PASS, Main authorizes the remaining production within the accepted direction. Continue varied, content-appropriate compositions and normal checks; the first three slides are not a universal scaffold for every later slide. Final review still covers the completed deck.

Main has the user's auto-full trust for this internal approval. Do not ask the user to approve each pilot or revision; ask only a material decision that genuinely needs user intent. Do not dispatch an additional reviewer or a second Engineer. Main-authored work follows the same stop-and-review boundary.

## Evidence and changes

The first-three review is a workflow gate enforced by Main's bounded assignments and recorded decisions; it is not a claim that every low-level exporter automatically intercepts premature production. In the initial Engineer assignment, authorize only the first three slide outputs and their necessary assets/previews. Main grants subsequent slide authoring after reviewing the receipt and actual visuals.

Keep the current size contract and all image-selection rules. The two-rejected-round image-search takeover still applies per slot during this phase and later production. A pilot PASS does not approve unseen images or the unbuilt slides.

If a later change materially alters the approved direction, typography system, canvas, shared layout rules or the first-three slide messages/imagery, pause the remaining production and reopen the affected first-three review. Bind the new decision to current evidence; preserve previous findings rather than rewriting old reviews as successes. Local repairs to later slides do not require restarting an unchanged pilot.

## Scope of the owner's approval

The owner subsequently authorized reusable images when tone, content and purpose all fit the current deck, under `PPTX_LAYOUT_ORIGINALITY_POLICY.md`. Reusing an image is allowed; repeating an earlier PPTX composition is rejected. Changes to photo/text/color or shape form/size/count alone do not establish a new composition. Every reused image receives a new contextual Main review.
