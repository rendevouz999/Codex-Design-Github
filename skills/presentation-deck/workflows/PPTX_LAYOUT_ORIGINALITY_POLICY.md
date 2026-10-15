# PPTX layout history and contextual image reuse

Owner-approved 2026-10-13. Mandatory for PPTX design/template creation, substantial redesign and originality reviews through `<CODEX_DESIGN_WORKSPACE>`. This policy owns the PPTX interpretation of earlier generic originality/repetition rules. It does not impose PPTX dimensions, object counts or layout rules on another platform. Current explicit user instructions remain authoritative.

## Two independent acceptance requirements

1. **Layout originality:** the same image may appear in a genuinely different layout. The same or a different image in a composition identical to an earlier generated PPTX is rejected, including results from earlier sessions. Changes to color, wording, photographs, shape type/form, shape size or shape count alone do not prove a new layout. Main must identify a material change in spatial composition, dominant regions, image/text relationships, hierarchy, grouping and visual reading flow. Cosmetic edits cannot compensate for structural reuse.
2. **Image fitness:** every image, including a previously approved or library image, must match the current slide content, the presentation's purpose and the deck's intended visual tone. Tone means coherent style, mood, lighting and color treatment in context; merely sharing a color is insufficient. Main automatically rejects an image when any one of tone, content relevance or purpose fails. Missing evidence stays unverified. Prior acceptance in another deck is not current acceptance.

Both requirements must pass independently. An original layout does not rescue an irrelevant image. An appropriate image does not rescue a repeated composition. A high overall score cannot average away either failure.

The reusable image library is permitted. Reuse existing local asset/provenance files without copying stock originals into a new library merely to implement this rule. Preserve license/source evidence and replacement editability. Repetition of the image itself, within or across decks, is not a rejection reason. No file deduplication, deletion, purchase, AI generation or mass download is implied by this permission.

## Extract evidence on every PPTX inspection

Before a substantive visual/originality review, extract the inspected PPTX revision with `scripts/design_brain_pptx_layout_audit.py`. Keep the source unchanged. Place the report in the current project's `analysis/` or review directory, identified by the deck identity and source hash. Reuse an existing verified extraction of identical source bytes; re-extract when the PPTX changes.

Capture actual canvas dimensions and per-slide object roles, normalized positions, sizes, ordering/grouping, image framing and available crop information. Retain raw shape geometry/count evidence for diagnosis. Compare spatial structure independently of photo identity, text strings, fill colors and shape names. Handle master/layout inheritance and group transforms through the existing native parser; unsupported or flattened content must be disclosed, not treated as proof of a new layout.

The extractor and comparator produce reproducible technical evidence. They cannot see a flattened slide's hidden structure or replace Main's visual judgment. Open the appropriate actual slide render as well. Record whether evidence comes from the source preview or native PowerPoint render, and bind the review to the inspected source/report hashes. Missing source, stale hashes, missing history or unresolved extraction coverage must never yield an originality PASS.

## Recover history across sessions

The owner authorized the bundled Supabase/local capability under `.design-brain/LOCAL_MEMORY_POLICY.md`; it supersedes the earlier Agent Core-only and local-only priorities in this plugin. Before layout planning and review, Engineer and Main read/search both returned sources and list applicable PPTX layout cases. Include queued/conflicting local records, negative decisions and cache coverage after outages. Engineer recovers artifact pointers, source hashes, deck identities, slide mappings and prior decisions, verifies them against current files, and performs preliminary comparisons. Main validates coverage and the creative result. Preserve previous revisions and reasons.

Geometry reports, paired-slide comparisons and renders remain ordinary project evidence. Main keeps bounded references and decisions in the plugin-local store, not raw images, full slide XML or credentials. For each inspected deck revision record the source path/hash, report path/hash, slide count, coverage limitations, review status and compared case IDs. Reuse/update the existing case for the same product; do not invent a new product ID to hide its history.

If an earlier actual deliverable is known but lacks an extraction, extract it read-only and register its evidence before claiming cross-session coverage. Exclude development fixtures, duplicate exports and reference-only documents from the accepted prior-product set; record their role honestly. A size reference does not automatically become an accepted creative design. Renamed/copied deliverables with identical source bytes are not new products. Intentional editing of the same deck is revision work, not a demand to redesign all unchanged slides; preserve its old revision and do not misrepresent it as a new distinct template.

State the actual comparison coverage: which previous decks/revisions were found, inspected and unavailable. Compare against all applicable retrieved prior-product slides, not only slides with the same number. A reordered duplicate must still be detected. Never claim all past sessions were covered from one sample or an empty search result. Agent Core unavailability does not block this local workflow. Missing or stale actual historical evidence still limits coverage; recover it from local sources and report the precise gap. Do not manufacture an empty-history PASS.

## Compare, reject and repair

Use the installed Python runtime resolved for the workspace. The commands below write reproducible evidence only; `--output` refuses to replace an existing file unless `--overwrite` is explicitly supplied. Never overwrite a source PPTX.

```powershell
python scripts/design_brain_pptx_layout_audit.py extract <deck.pptx> --deck-id <stable-product-id> --output <analysis/layout-fingerprint.json>
python scripts/design_brain_pptx_layout_audit.py compare <analysis/layout-fingerprint.json> --previous <earlier-layout-fingerprint.json> --output <analysis/layout-comparison.json>
python scripts/design_brain_pptx_layout_audit.py verify <analysis/layout-comparison.json>
```

Repeat `--previous` for every applicable verified baseline. Verification re-extracts current source bytes and rechecks report consistency. `EXTRACTED` means geometry evidence was collected, not creative approval. A zero exit code or `MAIN_REVIEW_REQUIRED` never means originality PASS; `NO_HISTORY` leaves coverage unverified. Main still owns the creative verdict.

- Exact repeated composition: **REJECT**. Record current and previous deck/slide IDs plus the matched regions.
- Likely same arrangement with resized/retyped shapes, extra decoration or changed object counts: **MAIN_REVIEW_REQUIRED**, never automatic PASS. Inspect the paired renders and semantic grouping. If the composition is still identical, reject it.
- No machine match: inspect the layout anyway. This is not proof of originality.
- Missing/stale/unsupported evidence or missing history: repair the evidence or report **BLOCKED/UNVERIFIED** for that claim.

Matching outer table/chart frames does not prove their internal composition is identical; inspect the actual internals visually. Unsupported group transforms and flattened-slide evidence cannot support an automatic structural conclusion. Keep these limits visible in the review.

Compare meaningful layout relationships, not XML IDs or filenames. A repeated small footer/header alone does not establish that the entire composition is identical; report that local match separately. Conversely, replacing decorations, splitting one block into several shapes or merging shapes cannot erase an identical dominant arrangement. Do not claim a mathematical originality percentage from a coarse match score.

On rejection Main gives the same Engineer a structural repair brief: which earlier slide was matched, what composition must change, which content must remain and what the revised attention/reading flow should achieve. Recoloring, rewording, swapping photos or merely changing shape form/size/count is not an adequate repair by itself. Re-render, re-extract and compare the revised slide again. Main records the final decision with evidence; Engineer cannot approve its own result.

## Integration with existing gates

The team remains Main plus one GPT-6.1 Sol (Codex) / Claude Opus 5.5 (Claude Code) General Design Production Engineer at Extra High (`xhigh`). Apply the cross-session layout comparison during the first-three-slide pilot; Main's PASS must cover both layout originality and current image fitness before slide 4 onward starts. Recheck every new slide during production and the completed PPTX at final review. Do not give the first-three PASS to unseen later images/layouts.

Keep `PPTX_IMAGE_SELECTION_POLICY.md`: Engineer proposes images; Main reviews actual pixels; two rejected Engineer rounds per stable slot transfer search to Main; every handoff specifies the slide, frame, crop and purpose. Record separate tone/content/purpose findings in the image review receipt. The image ledger's current schema binds approvals to deck purpose and visual tone as well as slide context, so changed intent requires a fresh Main review.

At delivery include the compact slide-to-image map, layout-comparison report, actual history coverage and remaining limitations. Main updates the canonical local record with bounded evidence references after verification and reads back the save. The policy, source files and technical reports are not claims that any particular production deck has already passed visual review.
