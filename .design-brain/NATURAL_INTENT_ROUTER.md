# Natural Intent Router

Native PowerPoint/PPTX requests use `skills/presentation-deck/workflows/native.md`.
Explicit PowerPoint output, including animation, remains `presentation-deck`;
PPTX-to-HTML remains `web-deck`. When both outputs are requested, build both with
separate receipts. `skills/presentation-deck/runtime/presentation.py route` distinguishes Generate,
Create Template, and Edit Native operations; source-preserving edits require a
real source PPTX and a round-trip workspace.

Design Brain should infer workflow intent from natural user language. The user should not need to mention internal workflow names such as template orchestrate, batch plan, reference insight, name check, or visual review.

Natural requests should route automatically:

- "ini referensi, buat template baru"
- "buat 5 template tapi jangan mirip"
- "kasih nama yang beda dari sebelumnya"
- "ambil insight dari referensi ini"
- "buat preview cover untuk marketplace"
- "ini terlalu mirip struktur sebelumnya"
- "buat lebih premium"
- "jangan copy layout"
- "buat batch template"
- "buat tiga template website restoran"
- "buat beberapa design template website restoran"
- "tolong buatkan 4 gambar design nya saja 1 per 1"
- "buatkan 3 gambar design nya saja"
- "buat 5 variasi template"
- "buat aku design template di figma"
- "buat design template website"
- "create new design untuk template website"
- "pelajari link Figma ini sebagai referensi template"
- "ambil standar struktur dari Figma reference ini"
- "kenapa harus aku mention efek/gradient"
- "jangan tunggu aku sebut detail kualitasnya"
- "butuh library layout section"
- "ekstrak layout per section"
- "hyper-accuracy untuk struktur layout"
- "layout masih flat atau repetitive"
- "buat presentasi html yang ada animasinya"
- "bikin deck interaktif buat webinar"
- "ubah ppt ini jadi presentasi web satu file"
- "buat slide animasi yang jalan di browser"
- "convert this pptx into an animated html deck"

Codex must translate these into internal Design Brain workflows without requiring explicit commands.

When routing docs, scripts, or README guidance disagree, resolve through `.design-brain/SOURCE_OF_TRUTH_MAP.md` and update the stale source instead of leaving contradictory behavior active.

## Router Duties

1. Detect the user's design intent from the task text, attachments, reference language, and requested output.
2. Load `.design-brain/AUTOLOAD_POLICY.md` and task-relevant source-of-truth files.
3. Select the workflow internally.
4. Use existing scripts as tools when they help, without making the user manage command names.
5. Respond naturally, as a designer or art director, naming what will happen in plain language.

## Intent Families

- Reference intent: the user provides or mentions a reference, inspiration, vibe, example, Figma reference link, or "do not copy" constraint.
- Section layout library intent: the user asks for layout-library, section catalog, extraction per section, matching/dedupe between learned layouts, hyper-accurate section understanding, anti-flat layout variation, or stronger differences between section layouts. Route to `.design-brain/SECTION_LAYOUT_EXTRACTION_LIBRARY.md`, `.design-brain/SECTION_LAYOUT_MATCHING_GATE.md`, `.design-brain/SECTION_LAYOUT_HYPER_ACCURACY_GATE.md`, and `scripts/design_brain_section_layout_extract.py`.
- Template product intent: the user asks for a sellable or reusable template, UI kit, Figma template, marketplace product, preview, or cover.
- Web deck intent: the user asks for a web deck, html deck, html or web presentation, browser deck, animated or interactive slides, a single-file/presenter/webinar deck, or asks to turn an existing deck, PPT, or PPTX into web or html output, including Indonesian phrasing such as `presentasi web`, `presentasi html`, `slide animasi`, `deck interaktif`, `ppt ke web`, or `ubah ppt jadi web`. Route to `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md`, `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`, `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`, `skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md`, `skills/presentation-deck/resources/web-deck/`, `skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs`, and `skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs`, and add `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md` when an existing deck is the input. A bare `presentasi`, `deck`, `slides`, `ppt`, `powerpoint`, or `keynote` request is not web deck intent and stays with `skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md`.
- Figma reference deep-study intent: the user provides a Figma link, Figma frame, Figma template file, or `.fig` source as a reference. Route to `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md` and `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md`, inspect product purpose, visual direction, section structure, grid/layout, typography hierarchy, color roles, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, Figma source hygiene, page/frame/component/state scheme, write a reference schema receipt, infer the product-family standard, and do not default to minimalist when the standard is unknown.
- Figma learning corpus intent: the user asks to learn from the provided Figma material links or to form a professional designer schema. Route to `.design-brain/FIGMA_REFERENCE_LEARNING_CORPUS.md` as learning material, not as a reusable scaffold.
- Figma output intent: the user asks for Figma, Figma template, create new design, or naturally asks for a website template design in this workspace without another target. Route to `.design-brain/FIGMA_OUTPUT_TARGET.md`, `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md`, `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`, `.design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md`, and `.design-brain/VISUAL_CRITIQUE_CHECKLIST.md`. Create a new Figma design only when the configured project/file target is valid, and require real auto-layout plus receipts for editable source structure.
- Batch intent: the user asks for multiple templates, a pack, a set, a collection, several variants, or Indonesian quantity phrasing such as `dua/tiga/empat`, `beberapa`, `banyak`, `varian`, `variasi`, `gambar design`, or `gambar desain`. Route this to Sequential Reference-Led Batch Workflow and reject all-at-once batch planning. For Figma/source outputs, each cycle must finish the main template plus its own design-system board before the next template starts. Also route to automatic visual-language gates so effects, gradients, color roles, surface depth, CTA behavior, and media-placeholder treatment are handled without explicit user prompting. For website/Figma/source batches, also route to Serial Provenance Gate: no next template may start until the current template is audited, locked, and scaffold-disposed.
- Sequential batch intent: if the user says `satu per satu`, `1 per 1`, `one by one`, `masing-masing`, `tiap`, `per template`, `per desain`, or `per gambar`, every output must run as its own full cycle before the next output starts: template, design-system board when applicable, inspection, receipt, lock, then next cycle.
- Naming intent: the user asks for names, titles, branding names, item names, or originality against previous names.
- Review intent: the user asks to check, critique, improve, de-genericize, make premium, or diagnose similarity.
- Preview intent: the user asks for cover, preview, overview, mockup, section breakdown, or responsive presentation.

For section layout library intent, do not ask the user to name a workflow. Extract candidates into `_incoming`, validate the catalog, select only stable PASS patterns for builds, and write `sectionPatternMix` evidence into layout fingerprints.

## Non-Command Principle

Commands and scripts are internal tools. The user's natural sentence is the command. If the intent is clear, do not ask the user to choose a workflow name.

Use `scripts/design_brain_intent_route.py` when a task needs an explicit routing decision report or when multiple intent families overlap.

For multiple-template work, use `scripts/design_brain_sequential_batch.py` as an internal planning helper when useful. The user still should not need to name or run it.

For multiple-template work, the user's natural request is enough to activate art-direction gates. Do not wait for explicit words like "effect", "gradient", "shadow", "glow", "color role", "surface depth", or "CTA behavior" before judging them.
