> See [`image-base.md`](image-base.md) for the common framework. Technical SVG/PPT constraints are in [`shared-standards-core.md`](shared-standards-core.md).

# Image_Searcher Reference Manual

For plugin PPTX work, [PPTX_IMAGE_SELECTION_POLICY.md](../../workflows/PPTX_IMAGE_SELECTION_POLICY.md) owns team, web access, Main visual review, two-round takeover and assigned slide placement. Main is the reviewer; Engineer is the initial search/embedding owner. No additional reviewer agent or metadata-only creative approval.

Role definition for the **web image acquisition path**: translate the resource owner's intent into keyword queries, search openly-licensed providers, download one license-cleared image into `project/images/`, and record provenance and license in `image_sources.json`.

**Trigger**: the Default resource list contains `Acquire Via: web`, or Quick has resolved a required web image in active context.

---

## 1. License Tier Discipline

Every provider-sourced image lands in one of two tiers; everything else is rejected. `manual` exists only for a directly selected `--from-url` replacement or an adopted-page package image — never for a provider result with an unknown license. Downstream consumers read `license_tier` alone and never interpret raw license strings.

| Tier | Licenses | On-slide attribution |
|---|---|---|
| `no-attribution` | CC0, Public Domain, Pexels License, Unsplash License (verified free asset), Pixabay Content License | None |
| `attribution-required` | CC BY, CC BY-SA, publisher terms that require a source credit | Inline credit `<text>` on the slide (the CC token only for a CC licence) |
| `manual` | Directly selected URL or adopted-page image, license unverified | Unverified: hold from final use until Main checks the actual source terms and records a supported tier/credit |

**Forbidden — auto-rejected**: CC BY-NC, CC BY-NC-SA, CC BY-ND, CC BY-NC-ND, All Rights Reserved, unknown or missing license.

---

## 2. Search Strategy

Quality first across all allowed tiers — never prefer CC0 over a better CC BY image; the manifest's `license_tier` lets Executor add credit only when needed. `--strict-no-attribution` (CC0 / PD / Pexels / Pixabay only) is opt-in for decks that cannot carry any on-slide credit.

```
Multimodal Generate: explicit query variants × provider chain + allowed licenses
         → aggregate/deduplicate/rank → first 8 thumbnails → visually select
         → Main review; bounded further candidates form the next submission.
         → second rejected Engineer round transfers search to Main.
Standalone CLI best-only: may retrieve a metadata-ranked proposal only.
         → cannot authorize PPTX placement; Main must inspect pixels and context.
```

---

## 3. Providers

| Provider | Config | Strength |
|---|---|---|
| Pexels | `PEXELS_API_KEY` (free, [signup](https://www.pexels.com/api/)) | modern stock photography, people, workplace, lifestyle |
| Pixabay | `PIXABAY_API_KEY` (free, [signup](https://pixabay.com/api/docs/)) | broad coverage including illustrations; its API serves at most a 1280 px long edge, so prefer Wikimedia or Pexels for full-bleed heroes |
| Openverse | zero-config | fallback aggregator: Wikimedia + Flickr + museums + rawpixel |
| Wikimedia Commons | zero-config | educational, scientific, geographic, historical; pin `provider: wikimedia` for murals, manuscripts, artworks, and museum objects, which stock providers tag with tourist snapshots |

For host web/browser search, Unsplash and Pexels public pages are also authorized; the table describes CLI adapters, not the complete host capability surface. No Unsplash CLI adapter currently exists. Prefer built-in search and hidden in-app/verified isolated browsing. Use Firecrawl when needed; never default to the user's active browser.

Default CLI chain: `pexels` → `pixabay` (each when keyed) → `openverse` → `wikimedia`; a keyed provider without a key is silently skipped. Configure Pexels or Pixabay when stock coverage serves the brief; their absence is never a failure.

---

## 4. Intent → Query Translation

| Layer | Owner and grammar |
|---|---|
| Default `design_spec.md §VIII Reference` / Quick active `Reference` | The owner's complete visual intent — exact subject, view/mood, focal or quiet region, crop safety, positive quality cues — fixed for the run and never rewritten by this role |
| `image_queries.json.items[].query` / positional query | This role's concrete entity keyword string: the shortest phrase that preserves identity, keeping exact multi-word names and disambiguators even beyond four words; no mood, quality, composition, HEX, or negative wording |

Web APIs match metadata, not intent: providers try each explicit query, then progressively simplified four/three/two/one-word variants, so keep a concise primary `query` plus `query_variants` for materially different official translations, spellings, aliases, or Chinese names (never cosmetic word-order changes); for Chinese landmarks pair the Wikimedia Chinese name with compact English identity terms. A candidate must satisfy the existing intent. Engineer gets at most two Main-rejected submission rounds for a stable slot before Main takes over searching; Main may mark `Needs-Manual` only after its own faithful recovery is exhausted; never loosen `required_terms`, the license policy, or the intent to manufacture a match.

**Hard rule — `required_terms` for exact entities** (landmarks, people, companies, products, venues, named artworks and institutions): write them with the query — one group per identity anchor, `|` for aliases, e.g. `["Chongqing|重庆", "Jiefangbei|解放碑|Liberation Monument"]`. Never loosen them to category words (`canyon`, `stone pillar`, `ancient town`, `bridge`, `temple`); those belong in the query, and a small or local attraction that metadata cannot prove ends in `Needs-Manual` or a user `--from-url`, never a plausible image of the wrong place. Never use them for generic mood rows ("modern city skyline", "team collaboration"). **Forbidden — negative words** (`not tourist snapshot`, `no amateur photo`): keyword APIs search them literally.

| §VIII Reference (intent) | Provider query |
|---|---|
| "Offshore wind farm at dusk, aerial view, quiet sky on the left for safe crop" | `offshore wind farm` |
| "Diverse engineering team around a laptop, modern office, natural light" | `engineering team laptop` |
| "Chongqing Jiefangbei monument, full structure visible, landscape frame" | `Chongqing Jiefangbei monument` |

---

## 5. Running `image_search.py`

```bash
python3 scripts/image_search.py "<query>" --filename <name>.jpg --slide <slide_id> \
  --orientation landscape --purpose background -o <project_path>/images
```

Every flag, its default, and its exact behavior: [`image.md`](../../runtime/native/docs/image.md) § `image_search.py`.

**Batch mode (≥2 web rows) — preferred**: write every row into `image_queries.json` and run one concurrent batch (the web sister of `image_gen.py --manifest`); add `--save-candidates` whenever the agent can inspect images:

```bash
python3 scripts/image_search.py --batch <project_path>/images/image_queries.json -o <project_path>/images --save-candidates
```

```json
{ "items": [ {
  "filename": "jiefangbei.jpg",
  "query": "Jiefangbei Chongqing downtown monument",
  "query_variants": ["Chongqing Liberation Monument", "重庆 解放碑"],
  "slide": "03_landmark", "purpose": "exact landmark photo", "orientation": "landscape",
  "required_terms": ["Chongqing", "Jiefangbei|Liberation Monument"],
  "status": "Pending"
} ] }
```

Required per item: `filename`, `query`, `status`; optional: `query_variants`, `candidate_page`, `slide`, `purpose`, `orientation`, `provider`, `strict_no_attribution`, `min_width`, `min_height`, `required_terms`. The runner revalidates `Sourced` rows, searches every `Pending` / `Failed` row concurrently, writes `Needs-Selection` with paging fields in thumbnail mode, and saves status after each completion; ranking orders provider metadata, never pixels, and is not a taste engine — exact runner and ranking behavior: [`image.md`](../../runtime/native/docs/image.md).

**Suitability review** — ranking is not visual approval. Engineer submits a bounded candidate round with source pages, previews, exact slide/slot, locked intent, slide copy/layout and crop direction. Main reviews actual pixels through [`web-image-review.md`](../../workflows/stages/web-image-review.md). Use `--save-candidates` when acquiring via the CLI; only Main-approved candidates may be promoted. If Main cannot inspect pixels, record BLOCKED and repair access; do not use metadata-only approval. No extra reviewer is dispatched.

**Replacement ladder**: Main rejects unsuitable candidates with a concrete changed search direction. A submission may include bounded pagination; changing query/provider does not reset its slot history. After two distinct rejected Engineer rounds, Main itself searches and selects, then hands the Engineer the chosen asset plus slide number, exact frame and crop directions. The Engineer may download/verify Main's chosen original and embed it, but may not initiate a third search round for that slot. Main retains search ownership for later replacement. Duplicates and network failures do not count as additional candidate rejections. Use the canonical policy's review ledger and checker.

**Host-sourced originals**: a verified public source page can supply a suitable image without a CLI provider adapter. Adopt or download only the selected asset, preserve its source/license/credit in `image_sources.json`, and reconcile `image_queries.json` when used. A low-level `--from-url` import writes `manual`; this is not clearance. Main must review source terms for the intended template use and record the supported license tier and credit before final placement approval. Required unresolved slots block final export, while unaffected work may proceed.

**Standalone thumbnail selection** (opt-in outside Generate):

```bash
python3 scripts/image_search.py "<query>" --filename <name>.jpg -o <project_path>/images --save-candidates
python3 scripts/image_search.py --promote candidate_03.jpg --filename <name>.jpg -o <project_path>/images
python3 scripts/image_search.py "<same query>" --filename <name>.jpg -o <project_path>/images --save-candidates --candidate-page 2
python3 scripts/image_search.py --promote candidate_03.jpg --filename <name>.jpg --batch <project_path>/images/image_queries.json -o <project_path>/images
```

Previews land in `images/candidates/<stem>/review/` with a thumbnail-only `candidates.json` (page, size, total, `has_more_candidates`, matched query, identity evidence) and `review_sheet.jpg` for the current round; the target and manifest stay untouched until promotion.

---

## 6. Manifest (`image_sources.json`)

Each successful download appends or replaces one entry keyed on `filename` (written atomically; an unreadable existing manifest blocks the write). `license_tier` drives Executor's attribution, `attribution_text` is the canonical credit source, `width` / `height` are measured from the saved file, and `selection_method` records `visual-thumbnail` or `metadata-ranked`. Complete field list and example: [`image.md`](../../runtime/native/docs/image.md).

---

## 7. On-Slide Attribution Contract

For `license_tier: attribution-required`, every slide using the asset carries a visible, readable credit bound unambiguously to it, preserving author, source/provider, and — for a CC licence — the CC BY / CC BY-SA fact from `attribution_text`. Position, size, color, per-image versus combined credits, labels, and contrast treatment belong to the page — a compact credit near the image edge or footnote area for one image, per-image credits or one labeled combined line for several, a quiet region (a scrim or gradient only when contrast fails) on a hero. Compress without dropping required facts: `team.jpg — "Untitled" via Openverse — license: CC0 (...)` → `via Openverse / CC0`; `team.jpg — "Sunset" by Jane Doe via Wikimedia Commons — license: CC BY-SA 4.0 (...)` → `© Jane Doe / Wikimedia / CC BY-SA 4.0`.

---

## 8. Failure Handling (web-specific)

Within PPTX, the two-rejected-round Main takeover in §5 takes precedence over automatic provider exhaustion. Infrastructure failures do not consume those rounds. After Main recovery, exhausted candidates and variants end in `Needs-Manual` with a reason, provider or network failures stay retryable `Failed`, and a promoted original that fails its gate stays `Needs-Selection`. Exit codes and per-case runner behavior: [`image.md`](../../runtime/native/docs/image.md).

---

## 9. Handoff with the Intent Owner

`Reference` is intent, not a query ([`image-base.md`](image-base.md) §1): keep it intact as the acceptance contract, derive a separate concise provider query that preserves exact names and disambiguation, and never pass it verbatim or rewrite it after search.

## 10. Handoff with Executor

For PPTX, Main first supplies the complete accepted slide assignment and a passing image-review handoff receipt; unresolved manual rights do not pass. Executor then reads `image_sources.json` per slide and acts on `license_tier` — `no-attribution` and `manual` embed the `<image>` only, `attribution-required` adds the §7 credit — without interpreting license strings. `svg_quality_checker.py` verifies that every referenced attribution-required image has its own visible author + license credit; one deck-level CC token never covers several images.

## 11. Task Completion Checkpoint

Beyond [`image-base.md`](image-base.md) §4: each required web row must have its original at `project/images/<filename>`, verified provenance, Main's contextual visual acceptance and complete assigned placement before embedding. Required `Needs-Selection`/`Needs-Manual` rows block readiness. Main's final rendered-slide review and a passing `image_review.json --stage final` check are mandatory. Host-search originals and CLI-thumbnail originals follow the same review rules. Never require metadata-only approval or endless provider exhaustion. Every attribution-required image has its visible credit in each referencing slide; surface discrepancies between actual image dimensions and provider metadata.
