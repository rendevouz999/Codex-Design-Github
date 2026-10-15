# Context Priority

When context is limited, load source-of-truth and task-specific files before generated reports.

## Tier 1: Always Load For Design/Template Tasks

- `.design-brain/DESIGN_SOUL.md`
- `.design-brain/DESIGN_IDENTITY.md`
- `.design-brain/USER_DESIGN_CONTEXT.md`
- `.design-brain/DESIGN_PRINCIPLES.md`
- `.design-brain/DESIGN_OPERATING_RULES.md`
- `.design-brain/AUTOLOAD_POLICY.md`
- `.design-brain/APPROVED_TEMPLATE_CORPUS.md` when the task is template-product, Figma-template, website-template, marketplace preview, design-system, or user-approved-output learning
- `.design-brain/DESIGNER_COGNITION_LAYER.md` when reference, template, or batch reasoning matters
- `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md` when the task uses a Figma link, Figma reference, Figma template file, Figma frame, or `.fig` source as reference evidence
- `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md` when the task uses a Figma template reference or asks for professional designer schema learning
- `.design-brain/FIGMA_REFERENCE_LEARNING_CORPUS.md` when the user-provided Figma material links are relevant
- `.design-brain/CONTINUOUS_DESIGNER_LEARNING_LOOP.md` when the task asks for long-horizon learning, post-build study, professional designer schema learning, or web-evidence-based questions
- `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md` when the task is an editable template or template source
- `.design-brain/FIGMA_OUTPUT_TARGET.md` when the task asks for Figma, a Figma template, or a website-template design without a different target link
- `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md` when the task asks for Figma, a Figma template, or an editable source template
- `.design-brain/NATURAL_INTENT_ROUTER.md`
- `.design-brain/DESIGN_AUTOPILOT.md`
- `.design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md` when the task asks for multiple templates or batch revision
- `.design-brain/LAYOUT_FLUIDITY_EXPANSION.md` when the user says layouts feel kaku/stiff, boxed, too similar, or sibling-like
- `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md` when the task is website-template, Figma website, ecommerce, portfolio, blog, docs, dashboard/admin, event/travel, service, or website batch work
- `.design-brain/TEMPLATE_REFERENCE_USAGE_POLICY.md` when the task creates a new template brand from references, uses website/Figma template references, or selects local reference groups
- `.design-brain/TEMPLATE_REFERENCE_USAGE_REGISTRY.json` when the task creates a new template brand from references, checks naming/reference availability, or records post-build reference usage
- `.design-brain/MEDIUM_PRODUCT_PLAYBOOKS.md`
- `.design-brain/HUMAN_CRAFT_HEURISTICS.md`

## Tier 2: Load Based On Task Trigger

- `.design-brain/WORKFLOW_TRIGGER_MAP.md`
- `.design-brain/RESPONSE_BEHAVIOR.md`
- `.design-brain/templates/SEQUENTIAL_REFERENCE_BATCH_CYCLE.md` when executing a batch cycle
- `.design-brain/DESIGNER_COGNITION_LAYER.md`
- `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md`
- `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md`
- `.design-brain/FIGMA_REFERENCE_LEARNING_CORPUS.md` when requested or relevant
- `.design-brain/CONTINUOUS_DESIGNER_LEARNING_LOOP.md` when learning should continue beyond the immediate output
- `.design-brain/REFERENCE_INSIGHT_SYSTEM.md`
- `.design-brain/REFERENCE_DECONSTRUCTION_MATRIX.md`
- `.design-brain/ORIGINALITY_GUARD.md`
- `.design-brain/ORIGINALITY_SIMILARITY_SCORECARD.md`
- `.design-brain/TEMPLATE_ORCHESTRATOR.md`
- `.design-brain/TEMPLATE_PRODUCT_INTELLIGENCE.md`
- `.design-brain/APPROVED_TEMPLATE_CORPUS.md` when using Yusuf's accepted local template examples as the benchmark
- `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`
- `.design-brain/FIGMA_OUTPUT_TARGET.md`
- `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md`
- `.design-brain/TEMPLATE_STYLE_ROUTER.md`
- `.design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md`
- `.design-brain/TEMPLATE_NAMING_LEDGER.md`
- `.design-brain/templates/BRAND_REFERENCE_USAGE_RECORD.md` when checking or recording candidate output brand and reference group usage
- `.design-brain/ADVANCED_STYLE_GRAMMAR_MATRIX.md`
- `skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md` when presentation/deck intent is present
- `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md` when web deck, html deck, html/web presentation, browser deck, animated slide, or interactive deck intent is present
- `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md` when a web deck will be planned, built, or audited
- `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md` when web deck entrance, transition, reveal, or reduced-motion behavior matters
- `skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md` when web deck packaging, single-file output, font source, or PDF export matters
- `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md` when an existing deck, PPT, or PPTX is the input for a web deck
- `skills/presentation-deck/resources/web-deck/` when the web deck plan schema, stage CSS, or deck runtime is needed
- `.design-brain/seed-packs/website-template/` when full website, HTML template, PHP template, business website, agency website, or service website intent is present
- `.design-brain/seed-packs/hero-header-kit/` only when hero/header kit intent is present
- `<LOCAL_REFERENCE_CORPUS>/Template Website` as local preview-image reference corpus for website-template product-family evidence
- `.design-brain/evidence/fig-extracts/latest.json` and the latest extraction report when local `.fig` template evidence is requested
- `.design-brain/templates/FIGMA_REFERENCE_SCHEMA_RECEIPT.md` when a Figma reference link or template source is used for structure planning
- `.design-brain/templates/DESIGNER_LEARNING_CYCLE.md` when recording a question-led learning pass
- `.design-brain/GOOD_BAD_EXAMPLE_LIBRARY.md` when evaluating generic or repeated patterns

## Tier 3: Load Summaries Or Latest Relevant Entries

- `.design-brain/REFERENCE_INSIGHT_JOURNAL.md`
- `.design-brain/TEMPLATE_BUILD_JOURNAL.md`
- `.design-brain/REFLECTION_LOG.md`
- `.design-brain/typeui-skills/extracted/*.json`
- `.design-brain/template-orchestrations/*.md`

## Tier 4: Generated Reports

- `.design-brain/reviews/`
- `.design-brain/visual-reviews/`
- `.design-brain/pilots/`
- `.design-brain/promotion-proposals/`

Generated reports are historical evidence. They must not override `.design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md` for future multiple-template work.

## Large Context Rule

When context is too large, prefer summaries, latest relevant records, and task-specific files over loading every generated report.

## Design Brain v2.0.0 Priority

Load v2 files selectively. For presentation-template work, the first v2 layer is:

1. `skills/presentation-deck/design/00_input_system/template-brief-schema.md`
2. `skills/presentation-deck/design/01_powerpoint_technical/editable-template-rules.md`
3. Relevant files in `.design-brain/03_slide_archetypes/`
4. `skills/presentation-deck/design/04_marketplace_standard/envato-presentation-requirements.md`
5. `skills/presentation-deck/design/06_quality_control/powerpoint-technical-checklist.md`
6. `skills/presentation-deck/design/06_quality_control/generic-design-detector.md`

For visual preview tasks, prefer `.design-brain/07_visual_pipeline/chromium-visual-review.md` and `.design-brain/evidence/visual-reviews/`.

For FIG extraction or local Figma template corpus tasks, prefer `.design-brain/evidence/fig-extracts/README.md`, `.design-brain/evidence/fig-extracts/latest.json`, and the latest run manifest before loading individual `nodes.json` files.
