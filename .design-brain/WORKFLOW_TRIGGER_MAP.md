# Workflow Trigger Map

Native PPTX create/fill/edit/template requests activate `PPTX_NATIVE_WORKFLOW.md`
and the `presentation-deck` plugin skill. Explicit native output takes precedence
over generic animated-slide wording. Explicit browser conversion stays web-deck;
explicit native plus web output needs two artifacts and receipts. Shared artifact
disambiguation rules live in `skills/presentation-deck/resources/routing.json`.

Use this map to translate natural language into internal Design Brain workflows. The user should not need to say workflow names.

If this trigger map conflicts with routing scripts or `.design-brain/AUTOLOAD_POLICY.md`, update both sides so they match. Use `.design-brain/SOURCE_OF_TRUTH_MAP.md` as the hierarchy for resolving conflicts.

## Post-Build Completion Triggers

Trigger the Post-Build Completion Gate whenever a request produces a built design artifact:

- build/create/make a design template
- create Figma template or source template
- create website template
- create dashboard/app/presentation/UI kit/source design
- create multiple templates or a template batch
- generate marketplace-ready template
- final/finalize/ready a design artifact

Required after build:

- design system build
- post-build triple audit
- batch pairwise audit when N > 1
- repair loop after failure
- completion receipt in final response

The user does not need to mention post-build audit. It is default Brain Design behavior.

## Reference Triggers

Trigger words and phrases:

- reference
- contoh
- inspired by
- arah seperti ini
- mirip vibe
- jangan identik
- jangan copy
- ambil insight
- reinterpret
- Figma reference
- Figma link
- Figma frame
- `.fig` source
- belajar
- pelajari lebih dalam
- folder approved
- sudah masuk Google Drive
- valid dan approve
- pola pikir designer
- skema designer
- lanjut belajar
- web search

Workflow:

- Designer Cognition Layer
- Figma Reference Deep Study when the reference is Figma
- Figma Professional Template Learning when the reference is a Figma template or the user asks to learn professional designer schema
- Figma Reference Learning Corpus when using the user-provided Figma material links
- Approved Template Corpus when the user refers to approved, valid, accepted, or Google Drive-ready local template folders
- Continuous Designer Learning Loop when the task asks for deeper learning, new questions, post-build study, or web evidence
- Reference Insight System
- Originality Guard
- Reference Insight Journal
- Template Build Journal if relevant

## Template Product Triggers

Trigger words and phrases:

- template
- landing page
- dashboard template
- UI kit
- website template
- web template
- PowerPoint
- presentation
- pitch deck
- deck
- slides
- Keynote
- PPTX
- brand kit
- Envato
- Figma template
- Figma
- create new design
- design template di figma
- design template website
- marketplace
- product preview

Workflow:

- Medium Product Playbook
- Figma Output Target when Figma or natural website-template design output is implied
- Figma Professional Template Learning when a Figma template reference drives the product direction
- Figma Auto-Layout Enforcement, Template Image Placeholder Policy, Template Product Quality Gate, and Visual Critique Checklist when the output is Figma, source-template, editable UI, or Figma-like
- Website Template Reference Corpus when website-template intent is present
- Approved Template Corpus when the request asks to learn from Yusuf's accepted template outputs, Google Drive-ready folders, or already approved Figma template examples
- Template Product Intelligence
- Template Image Placeholder Policy
- Website Reference Prompt Lock when the task is reference-led website, web-template, or Figma website-template work
- Template Orchestrator
- Subagent Orchestration Layer for website-template, Figma/source-template, marketplace, reference-led, batch, anti-minimalist, or quality-sensitive design work
- Design Simulation Layer before build for marketplace, Envato, reference-based, batch, Figma website-template, anti-identical, or anti-minimalist work
- Style Router
- Quality Gate
- Section Layout Extraction Library, Matching Gate, and Hyper-Accuracy Gate when the task asks for richer layout exploration, non-flat sections, anti-repetition, section catalogs, layout dedupe, or hyper-accurate section structure understanding
- Presentation Deck Intelligence for bare presentation, deck, slides, PPT, PPTX, PowerPoint, or Keynote requests, and Web Deck Triggers only when the request adds a web, html, browser, animated, or interactive cue

## Design Simulation Triggers

Trigger words and phrases:

- Envato standard
- marketplace-ready
- anti identik
- jangan identik
- jangan minimalist
- visual maksimal
- terlalu sama
- terlalu generic
- kaku
- layout kaku
- bentuk layout sama
- silhouette sama
- terlalu boxed
- mirip antara template
- repeated scaffold
- layout library
- katalog layout
- katalog section
- matching layout
- dedupe layout
- duplikat layout
- hyper-accuracy
- struktur section
- layout section
- MiroFish style
- simulation layer
- buyer reaction
- reviewer risk
- reference DNA
- subagent
- visual QA
- Style DNA
- design system depth
- Claude gap
- kualitas output
- validasi visual

Workflow:

- Template Orchestrator
- Subagent Orchestration Layer
- Design Simulation Layer
- Layout Fluidity Expansion when the critique is stiffness, same silhouette, boxed layout, or sibling-like templates
- Section Layout Extraction Library, Matching Gate, and Hyper-Accuracy Gate when the critique involves flat/generic/repetitive/duplicate section layouts or the user wants catalog-driven section variation
- Originality Guard
- Marketplace Quality Gate
- Visual Critique Checklist after build

Required behavior:

- Build a proposed structure first; do not simulate a blank idea.
- Run or follow `scripts/design_brain_design_simulate.py` before implementation.
- Include the reference summary and do-not-copy boundary when references exist.
- Compare against prior fingerprints for batch or repeated template work.
- If the verdict is `REVISE` or `BLOCKED`, revise and rerun; do not proceed to build.
- Store the accepted structure fingerprint for future anti-identical checks.
- Record `sectionPatternMix`, `sectionPatternIds`, `sectionDensityLimits`, and `catalogDivergenceNotes` when the Section Layout Extraction Library is active.
- Treat the verdict as a local design review gate, not a public-opinion or social simulation. The layer does not run MiroFish/OASIS and must not replace routing, product-family detection, Reference Insight, Template Orchestration, Figma Build Rules, Visual Review, or Marketplace Quality Gate.

## Subagent Orchestration Triggers

Trigger when the task asks for stronger quality control, subagents, visual validation, Style DNA, design-system depth, Claude-level output, marketplace readiness, Figma source QA, originality, anti-minimalist behavior, or reference-led website template work.

Workflow:

- `.design-brain/SUBAGENT_ORCHESTRATION_LAYER.md`
- `.design-brain/design-subagents/agents.json`
- `scripts/design_brain_subagent_orchestrate.py`
- `scripts/design_brain_subagent_receipt_validate.py`
- subagent receipt/evidence presence and semantic quality verification before final delivery

Required behavior:

- Use Full mode for reference-led, Figma/source-template, marketplace-ready, batch, new-brand, or complete website template work.
- Use Standard mode for single landing pages, homepage concepts, large section redesigns, and design-system board work.
- Use Lightweight mode for small edits, but activate Brand & Reference Memory Guardian when reference or brand usage is involved, Figma Source QA when source is affected, and Marketplace Readiness Judge when a marketplace-ready claim is made.
- Final PASS is blocked if a critical subagent returns BLOCK, critical evidence is missing, receipt content is placeholder/fake/invalid, screenshot evidence is absent for visual template work, reference usage is unrecorded, design-system depth is missing or shallow, originality audit is not PASS, or Figma Source QA is not PASS for Figma source templates.

## Batch Triggers

Trigger words and phrases:

- batch
- 2 / 3 / 4 / 5 / 6 / 7 / 8 / 9 / 10 + template/design/desain/gambar/page/screen/output
- dua / tiga / empat / lima / enam / tujuh / delapan / sembilan / sepuluh + template/design/desain/gambar/page/screen/output
- 5 template
- beberapa template
- beberapa design
- beberapa desain
- banyak template
- gambar design
- gambar desain
- varian
- variasi
- versi
- satu per satu
- 1 per 1
- one by one
- masing-masing
- tiap
- per template
- per desain
- per gambar
- template pack
- collection
- set
- sekaligus

Workflow:

- Designer Cognition Layer
- Sequential Reference-Led Batch Workflow
- Serial Provenance Gate for website/Figma/source batches
- Website Template Reference Corpus when the batch contains website-template outputs
- Template Image Placeholder Policy for editable source templates
- Figma Auto-Layout Enforcement when any output is a Figma template
- Effect Language Judgment
- Section Layout Extraction Library, Matching Gate, and Hyper-Accuracy Gate
- Per-Cycle Reference Study
- Pattern Lock After Each Template
- Similarity Guard Against Previous Cycles

Required behavior:

- If the prompt contains a quantity or `beberapa/banyak` plus an output noun, activate batch workflow. If it contains `satu per satu`, `1 per 1`, `masing-masing`, or `per template/per desain/per gambar`, activate sequential batch workflow.
- Select one active product-purpose reference group for one template only. When enough matches exist, the group should contain up to 10 varied references.
- For website-template cycles, classify product family, select matching local previews from `Template Website`, and rotate the active group before planning.
- Convert reference imagery into text clue placeholders such as `image placeholder: [purpose]` and `profile photo placeholder: [role]` unless generated images were explicitly requested.
- Infer buyer decision model, designer intent, attention strategy, emotional rhythm, trust strategy, density strategy, conversion logic, component reasoning, structure, and visual logic with evidence.
- For Figma references, complete the professional reading order: product purpose, visual direction, section structure, grid/layout, typography hierarchy, color roles, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, and Figma source hygiene.
- Build one complete standard template.
- For Figma outputs, use real auto-layout for editable structure and include an auto-layout receipt before review.
- Define and apply a visual-language fingerprint: color roles, gradient logic, effect language, surface depth, CTA behavior, and media-placeholder treatment.
- Define and apply a section-pattern fingerprint: selected section catalog patterns, section density limits, compatible-before/after logic, and catalog divergence from previous accepted templates.
- Screenshot-inspect the effect/gradient system when possible; clean-but-flat output is not complete.
- Lock opening strategy, hero grammar, trust strategy, density rhythm, component system, CTA logic, visual motif, effect language, gradient logic, surface-depth grammar, and storytelling arc.
- Record scaffold disposal and serial provenance before any next template reference study starts.
- Repeat from reference selection for the next template only after the prior template has passed audit, fingerprint lock, and scaffold disposal.
- Do not use one global batch scaffold.
- Do not allow a post-build READY state when one builder/script/schema created multiple final website/Figma/source templates.
- Keep pairwise cross-template similarity below 10 percent against accepted prior fingerprints.

## Naming Triggers

Trigger words and phrases:

- nama
- title
- item name
- branding name
- nama template

Workflow:

- Template Naming Ledger
- Name Check

## Review Triggers

Trigger words and phrases:

- cek
- review
- critique
- terlalu mirip
- kurang premium
- generic
- spacing aneh
- struktur sama
- copy-paste
- identik
- sama dengan referensi

Workflow:

- Design Critic
- Visual Review if evidence exists
- Originality Similarity Score
- Sequential Batch Similarity if multiple templates
- Reflection if useful feedback

## Medium/Product-Type Triggers

Trigger words and phrases:

- website template
- landing page
- PowerPoint
- presentation
- pitch deck
- slides
- dashboard
- UI kit
- design system
- brand kit
- portfolio
- marketplace preview

Workflow:

- Medium Product Playbook
- Advanced Style Grammar
- Human Craft Heuristics
- Product-type critique gate
- Presentation Deck Intelligence when the medium is a static presentation, deck, slides, PPT, PPTX, PowerPoint, or Keynote artifact, and Web Deck Medium only when an explicit web, html, browser, animated, or interactive cue is present

## Web Deck Triggers

Trigger words and phrases:

- web deck
- html deck
- html presentation
- web presentation
- browser deck
- animated deck
- animated slides
- animated presentation
- interactive deck
- slide deck html
- single file deck
- presenter deck
- webinar deck
- demo day deck
- deck to web
- ppt to web
- pptx to html
- convert deck to html
- self running deck
- deck html
- presentasi web
- presentasi html
- slide web
- slide animasi
- presentasi animasi
- deck browser
- deck interaktif
- ppt ke web
- ppt ke html
- pptx ke html
- ubah ppt jadi web
- presentasi satu file
- slide buat live
- deck buat webinar

Workflow:

- Medium Product Playbook
- Web Deck Intelligence
- Deck Source Bridge when an existing deck, PPT, or PPTX is the input
- Web Deck Stage Gate before build
- Web Deck Motion Grammar
- Web Deck Delivery Contract
- Design Simulation Layer before build when the deck is sellable, reference-led, marketplace-ready, or anti-identical work
- Web Deck Audit and Web Deck Render Review after build
- Post-Build Completion Gate

Required behavior:

- Route here only on an explicit web, html, browser, animated, interactive, or single-file cue. A bare presentation, deck, slides, PPT, PPTX, PowerPoint, or Keynote request belongs to Presentation Deck Intelligence.
- Classify the source first: a new deck from a brief, or an existing deck converted to web. Conversion work runs through the Deck Source Bridge before planning.
- Produce a deck plan that validates against `skills/presentation-deck/resources/web-deck/deck-plan-schema.json` before any markup is written.
- Treat the deck as a fixed stage, not a responsive page. Scale the whole stage uniformly; do not reflow slide content for small viewports.
- Run or follow `skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs` on the built file, then `skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs` for rendered stage evidence. Audit failures are repair tickets, not notes.
- Keep motion, reduced-motion, keyboard navigation, deep link, and print behavior inside the delivery contract; a deck that only looks right in one browser window is not complete.

## Figma Output Triggers

Trigger words and phrases:

- Figma
- Figma template
- create new design
- buat design template di Figma
- buat design template website
- bikin template website baru

Workflow:

- Figma Output Target
- Figma Auto-Layout Enforcement
- Template Product Intelligence
- Website Template Reference Corpus when website-template intent is present
- Template Orchestrator
- Design Simulation Layer before build when the output is sellable, reference-based, Envato/marketplace, or anti-identical
- Visual review and output verification

Required behavior:

- If the user does not provide another Figma target, create a new Figma design file only when `.design-brain/FIGMA_OUTPUT_TARGET.local.json` or a task-supplied target contains a valid project/file ID. If the target is missing, placeholder, or not configured, do not call `create_new_file`. Ask for a valid target or continue with local plan only.
- Do not ask the user for the same project link again unless the Figma create step fails or the user asks for a different destination.
- Build editable source structure with real Figma auto-layout: major sections, nav, cards, CTAs, forms, repeated rows, dashboards, and design-system panels cannot be primary manual x/y layouts.
- Include an auto-layout receipt naming auto-layout groups and any decorative absolute-position exceptions.
- This target only decides where to build. It does not replace product-family classification, reference insight, originality guard, or marketplace quality gates.

## Figma Reference Deep-Study Triggers

Trigger words and phrases:

- Figma reference
- Figma link
- link Figma sebagai referensi
- Figma design template
- Figma frame reference
- `.fig` file
- study this Figma template

Workflow:

- Figma Reference Deep Study
- Figma Reference Schema Receipt
- Designer Cognition Layer
- Reference Insight System
- Template Product Intelligence
- Product-family standard inference
- Originality Guard

Required behavior:

- Inspect the Figma scheme before planning: pages, frames, sections, components, variants, states, design-system panels, density rhythm, and editable-source signals.
- Infer product family and marketplace category before selecting section/page/screen depth.
- If the standard is unclear, use taxonomy, local corpus, category research, or one targeted question. Do not choose minimalist as the safe fallback.
- Reconstruct color roles and effect language instead of copying exact reference palette, gradient, glow, CTA, or background roles.
- Produce a Figma reference schema receipt before build.

## Continuous Designer Learning Triggers

Trigger words and phrases:

- belajar terus
- jangan setengah-setengah
- pelajari materi sebelumnya
- goals panjang
- pertanyaan baru
- cari jawabannya via web search
- pola pikir seorang designer
- skema seorang designer
- lanjut belajar lebih dalam
- terapkan ke Brain Design

Workflow:

- Continuous Designer Learning Loop
- Designer Cognition Layer
- Reference Insight System
- Figma Professional Template Learning when Figma/template references are involved
- Web evidence search when the user requests web-based learning or when category standards are unclear
- Designer Learning Cycle template

Required behavior:

- Do not treat the latest build as the end of learning.
- Generate at least one new question from each substantial lesson.
- Search web evidence for questions that affect template quality, marketplace readiness, source editability, responsive behavior, ecommerce behavior, accessibility, or design-system behavior.
- Distill findings into designer schema: buyer effect, section logic, visual rhythm, source-file logic, and marketplace value.
- Update Brain Design workflow files when the finding is actionable and protected-change permission is satisfied.
- Keep evidence separate from stable memory unless the user explicitly asks for stable-memory promotion.

## Preview Triggers

Trigger words and phrases:

- cover
- preview
- overview
- mockup
- section breakdown
- responsive preview

Workflow:

- Template Orchestrator
- Marketplace Preview direction
- Perspective/Bento style guidance

## v2.5 Layout Originality Trigger

Trigger the Sequential Layout Originality Gate for reference-led template builds, batch template builds, marketplace template builds, Figma/source template builds, and any request for multiple distinct templates.

Workflow addition:

- Build Session Lifecycle
- Layout Fingerprint
- Reference-vs-AI Layout Audit
- AI-vs-AI Pairwise Layout Audit for Template 2+
- Fingerprint Lock
