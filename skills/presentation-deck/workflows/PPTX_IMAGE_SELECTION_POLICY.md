# PPTX image sourcing, Main review and slide assignment

Owner-approved policy, 2026-10-13. Activate only while using or maintaining the custom `<CODEX_DESIGN_WORKSPACE>` plugin for native PowerPoint/PPTX. It does not impose image, team or canvas rules on other platforms or unrelated tasks. Current explicit user instructions remain authoritative.

This policy owns sourced-image selection and overrides conflicting local instructions for an extra isolated reviewer, metadata-only approval, unlimited Engineer retry, or automatic transfer of rights checks to the user. It complements `PPTX_SIZE_POLICY.md`; it does not change dimensions, factual accuracy, native editability or required delivery checks.

## Ownership and authorized tools

The team remains Main plus ONE GPT-6.1 Sol (Codex) / Claude Opus 5.5 (Claude Code) General Design Production Engineer with **Extra High effort (`xhigh`)**. Main directs, evaluates actual evidence and decides PASS/REVISE. The Engineer searches first, prepares candidates, embeds accepted pictures and repairs layouts. Main does not rubber-stamp the Engineer's recommendation. No additional image-search or reviewer agent is created.

For PPTX photo slots that serve the brief, the user gives standing permission for public web/image search, Unsplash and Pexels, including downloading suitable originals into the project. AI image generation is a separate intent; this permission does not request it. Do not replace a requested diagram, exact artwork, technical evidence, real product or identifiable person with generic stock imagery. Keep unused template zones as editable text clue placeholders; do not fill every slide with photographs.

Use the available built-in web/image search first. For visual source-page inspection, prefer the Codex in-app browser in a new hidden tab, or an actually verified Agent Core isolated browser. Never attach to the user's active browser, extension session, tabs, history or profile by default. If internal browsing fails, continue through verified search/read tools or Firecrawl; report the specific gap if a necessary page cannot be checked. A tool's presence is not proof that a site, credential or download is accessible.

Search Unsplash and Pexels where suitable; a precise specialist source may fit scientific, historical or named subjects better. Web results are discovery, not license proof. Firecrawl search/scrape may help discover source pages or extract metadata when ordinary tools are insufficient; inspect its result and avoid repeated scraping. Use existing connected capabilities without creating accounts, buying assets, upgrading subscriptions or changing global security settings. Report a concrete missing capability instead of inventing an API.

The bundled `image_search.py` currently has Pexels (API key), Pixabay (API key), Openverse and Wikimedia adapters. It has **no Unsplash adapter**. Public Unsplash/Pexels searches through available web/browser tools do not require configuring those CLI adapters. Missing optional API keys must not block a working public-search route. Never print or store credentials in receipts.

## Reuse requires current image fitness

Reusable image-library assets are authorized when they fit the current deck. Repeated image identity alone is allowed; prior acceptance does not approve a new use. Main must view actual pixels in the current slide/deck context and record separate **tone**, **content relevance** and **presentation purpose** findings. Any mismatch automatically rejects the candidate; missing evidence remains unverified. Tone includes coherent style, mood, lighting and color treatment, not merely a matching color. A strong score in one category cannot compensate for a failure in another.

Follow `PPTX_LAYOUT_ORIGINALITY_POLICY.md` independently: same or different images in an identical prior-PPTX composition are rejected. Changes to text/color/photo or shape form, size or count alone do not establish originality. Extract and compare actual layout evidence across sessions through verified shared-memory and local-fallback pointers. Reusing local images does not authorize deletion, bulk duplication or stock-original redistribution.

## Search brief and candidate rounds

1. Main maps every required photo to a stable deck/slot ID and a 1-based slide number before search. Keep the slot ID through slide renumbering, filename changes, new queries and provider changes. Record the slide's message, image purpose, exact subject or conceptual role, audience, visual direction, target frame/ratio, focal point, text-safe region, crop limits and exclusions.
2. Engineer prepares one bounded round for each assigned slot, normally up to three genuinely different viable candidates. Fewer is acceptable when the exact subject has fewer matches; do not pad with irrelevant results. Include source pages, actual previews, original dimensions, provenance, intended-use license evidence and a short reason each candidate fits. A ranked result is a proposal only.
3. Main views actual candidate pixels with the slide copy/layout or a proposed crop. Open an original/detail preview when a contact sheet cannot establish subject or quality. Judge context and subject correctness, visual direction, composition/crop, useful resolution and sharpness, text readability, and source/license suitability. A missing critical requirement means rejection; do not average it away with an aesthetic score. Metadata alone cannot yield creative PASS.
4. Main records ACCEPT, REJECT or BLOCKED with concrete evidence. REJECT explains the mismatch and a changed search strategy. BLOCKED is an access/tool/evidence failure, not a judgment that the image is unsuitable. Pagination within one prepared submission is not a new round; Main's review of a materially new candidate submission is.
5. After the **second distinct rejected Engineer round for the same slot**, Main takes over the search immediately. Engineer must not search a third round for that slot, rename the slot to reset its count, or promote a previously rejected image. Duplicate receipts count once; conflicting duplicates must be repaired. Network/provider failures and layout/rendering defects do not consume candidate-selection opportunities. Other slots retain their own counts.
6. Main searches with the rejection evidence, inspects the new candidates, selects a passing original and gives the Engineer the complete slide assignment below. Engineer may perform bounded downloading, file checks and embedding for Main's selected URL; this is not another Engineer search. Main retains search ownership for later replacements in that slot. If no faithful image exists, Main reports the precise remaining limitation or asks a material creative question; never accept the least-bad image merely to finish.

Keep history across revisions. A later discovery that the image itself is wrong reopens selection without erasing earlier rejection rounds. A correct image with poor cropping returns to Engineer for placement repair, not an unnecessary new search.

## Required handoff before embedding

Never give the Engineer an unassigned image dump. Every accepted placement includes:

- Deck ID, stable slot ID, slide number and title, and the message the image supports.
- Accepted round/candidate IDs, Main's reason and actual visual-review evidence.
- Absolute local original path and SHA-256; preserve the original and record derivatives separately.
- Exact frame `x/y/width/height` in inches on the actual PPTX canvas, crop/fit mode, focal point, protected subject areas, and any overlay/text-safe area. State units; use the current size contract, including explicit overrides.
- Source/provenance record, required credit, caption or alt text, and how the buyer can replace the picture.

Example of a direction, not a supplied asset: “Slide 6, slot `sensing-detail`: place the selected close-up in the right-hand 4.0 × 3.0 inch frame at x=5.5, y=1.3; crop to fill, preserve the sensor at the left-third focal point, keep text outside the picture; use the approved local file named in the receipt.” Never claim this example was sourced or reviewed.

Embed a native, replaceable PowerPoint picture with the intended crop; keep text, diagrams, labels and layout elements editable. Do not flatten a slide to hide unsupported authoring. Recheck the downloaded original matches the reviewed candidate, its actual format/dimensions and available resolution after crop. Use existing `analyze_images.py` and downstream image-quality checks.

## Provenance, rights and delivery

Reuse `images/image_queries.json` for acquisition state when the CLI is used, and **`images/image_sources.json` as the single source of truth for source/license/credits** for every adopted web asset. A URL obtained by Main through the browser is still web-sourced; `--from-url` being classified `manual` does not establish rights or delegate Main's license check to the user. Inspect the original asset page and current applicable terms for the intended presentation or editable commercial template. Record original provider/creator, source page, license URL/name, access date, attribution, intended use and Main's evidenced decision. Unknown or unresolved use rights block that asset's final approval. Do not silently label an unverified asset CC0 or public domain. Check free stock separately from premium/Unsplash+ or paid partner listings.

Do not bundle standalone stock originals for resale just because an image is viewable or downloadable. Reuse the existing per-slide credit renderer where required. A supported template-use decision is different from permission to redistribute a raw stock library. Current official references: [Unsplash license](https://unsplash.com/license), [Pexels license](https://www.pexels.com/license/). Recheck relevant terms during acquisition rather than treating this document as a permanent license ruling.

Create **schema version 2** `images/image_review.json` with root `deck_purpose` and `visual_tone`, and `fit_review` on each accepted round containing `tone`, `content` and `purpose` objects, each with `verdict: pass` and a concrete Main `reason`. Legacy version 1 receipts require current-context Main review before upgrading; never auto-stamp their new checks. The placement binding includes purpose and tone, so changes invalidate old approvals. Use `.design-brain/templates/PPTX_IMAGE_REVIEW.example.json` for required sourced slots. The review ledger links existing provenance; it does not replace it. Run the read-only checker from the plugin root:

```powershell
python scripts/design_brain_pptx_image_review.py <project>/images/image_review.json --stage progress
python scripts/design_brain_pptx_image_review.py <project>/images/image_review.json --stage handoff
python scripts/design_brain_pptx_image_review.py <project>/images/image_review.json --stage final
```

`progress` checks history and reports who searches next. `handoff` is required before accepted pictures are embedded; it checks assignments and file/provenance evidence. `final` follows a draft export/render and Main's review of each affected slide, so there is no circular requirement to render before embedding. Final review must match the actual deck/assets/placement and cover crop, readability, consistency, credit and replaceability. A picture or layout change invalidates its old final review. The script checks receipt consistency, not visual taste, factual identity, legal conclusions or the actual native picture objects; Main and the existing native QA tools still inspect those. It is a required workflow check, not a claim that all low-level exporters intercept it.

Final delivery includes a compact **slide → image → role/placement → source** map, with any unresolved slot clearly identified. State only review, search, downloads and browser capabilities actually exercised. Required images with failed checks block final readiness; unaffected design work may continue.
