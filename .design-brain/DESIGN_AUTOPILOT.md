# Design Autopilot

Design Autopilot makes Design Brain feel natural and agentic instead of command-driven.

When Codex detects a design, template, reference, naming, batch, review, or preview intent, it should:

1. Identify the intent from natural language.
2. Load `.design-brain/AUTOLOAD_POLICY.md`.
3. Load the relevant source-of-truth files from `.design-brain/CONTEXT_PRIORITY.md`.
4. Select the correct workflow internally.
5. Run or follow existing scripts when appropriate.
6. Explain the result naturally.
7. Keep command details optional and secondary.

Do not ask the user to choose workflow names when the intent is clear.

Use `.design-brain/SOURCE_OF_TRUTH_MAP.md` whenever autopilot behavior conflicts with README, quick-start notes, old trigger text, learning logs, or default preferences.

## Decisive Autopilot

- If the intent is ambiguous in a way that blocks execution, ask one concise clarification. Otherwise choose a product-appropriate direction and proceed.
- If the task is small, do not run the full workflow.
- If the task risks copying a reference, activate Originality Guard.
- If the task uses a Figma reference link, Figma frame, Figma template file, or `.fig` source, activate `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md` and `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md` before structure planning. Inspect product purpose, visual direction, section structure, grid/layout, typography hierarchy, color roles, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, Figma source hygiene, file/page/frame/component/state scheme, produce a Figma reference schema receipt, infer the category standard, and reconstruct the design direction instead of copying or defaulting to minimalist.
- If the user asks to use the provided Figma material links as learning references, load `.design-brain/FIGMA_REFERENCE_LEARNING_CORPUS.md` and treat the links as study material, not a shared scaffold.
- If the user asks to continue learning, study deeply, build designer schema, ask new questions, or use web search to understand professional template logic, activate `.design-brain/CONTINUOUS_DESIGNER_LEARNING_LOOP.md`. Work as a long-horizon learning cycle: produce or review output, extract uncertainty, ask a new design question, search web evidence when useful or requested, answer the question, and apply the resulting rule in the next design.
- If the task includes multiple templates, activate Sequential Reference-Led Batch Workflow. Build one complete template per cycle, with the next active product-purpose reference group before each build. Use up to 10 eligible varied references when enough local matches exist. For website/Figma/source batches, also require Serial Provenance Gate: Template N+1 cannot start until Template N is complete, repaired, audited, fingerprint locked, and scaffold-disposed.
- If the task includes naming, activate the Naming Ledger and name check.
- If the task is marketplace-ready template work, activate template orchestration.
- If the task is website-template, reference-led, Figma/source-template, marketplace-ready, batch, anti-minimalist, or quality-sensitive, activate `.design-brain/SUBAGENT_ORCHESTRATION_LAYER.md` and run/follow `scripts/design_brain_subagent_orchestrate.py` to decide active subagents, required receipts, missing visual/source evidence, and semantic receipt quality before final readiness is claimed.
- If the task is complex/high-value, reference-led, marketplace-ready, Figma/source-template, batch, anti-identical, or at risk of minimalist/generic scaffold collapse, run or follow the Design Simulation Layer after orchestration and before build. PASS may proceed; REVISE requires repair; BLOCKED prevents build/finalization.
- After any template build, run or follow the Post-Build Completion Gate. Build the design system, run the triple audit, repair failures, rerun failed audits, and produce the completion receipt before claiming final readiness.
- For batch builds, run pairwise similarity audits after each new template and a global batch similarity audit before final delivery.
- If the task mentions a product medium such as website, PowerPoint, dashboard, UI kit, brand kit, portfolio, or marketplace preview, activate the medium playbook first.
- If the task mentions PowerPoint, presentation, deck, slides, Keynote, PPT, or PPTX, activate Presentation Deck Intelligence before any landing-page assumptions.
- If the task mentions a web deck, html deck, html or web presentation, browser deck, animated or interactive slides, a single-file deck, or converting an existing deck/PPT/PPTX to web or html, activate `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md`, `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`, `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`, and `skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md` instead of the static deck path, and add `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md` when an existing deck is the source. Plan against `skills/presentation-deck/resources/web-deck/deck-plan-schema.json`, build on the fixed stage, then audit and render-review before claiming readiness. Without a web, html, browser, animated, or interactive cue, stay with Presentation Deck Intelligence.
- If the task mentions Figma, Figma template, create new design, or asks naturally for a website template design without another output target, load `.design-brain/FIGMA_OUTPUT_TARGET.md`, `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md`, `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`, `.design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md`, and `.design-brain/VISUAL_CRITIQUE_CHECKLIST.md`; create the Figma design only when the configured target is valid.
- If the output is a Figma template, auto-layout is mandatory for editable structure. Build major sections, repeated modules, navigation, cards, CTAs, forms, dashboards, and design-system panels with real Figma auto-layout; document decorative absolute-position exceptions in an auto-layout receipt.
- Figma/source-template outputs also need layer/component naming, placeholder, responsive/editability, and source hygiene receipts before being called complete.
- If visual evidence exists or the task asks for review, activate visual review where possible.
- If a subagent critical role returns BLOCK, if critical subagent evidence is missing at final gate, or if `scripts/design_brain_subagent_receipt_validate.py` reports weak/fake receipt content, do not claim the design/template is complete or marketplace-ready.
- If the user gives broad creative trust, increase structure depth, composition variety, and niche-specific proof before first delivery.
- If the task is a batch, quality gates outrank completion claims. Compare each new template against every accepted prior fingerprint; if cross-template similarity reaches 10 percent, rebuild the newer template before continuing.
- If the task is a batch, activate visual-language autopilot. Infer effect language, gradient logic, surface depth, color-role divergence, CTA behavior, and media-placeholder treatment without waiting for the user to mention them.
- If a batch item is clean but flat, under-art-directed, or only different by section order, treat it as unfinished. Apply a functional effect/gradient/surface-depth pass or document deliberate restraint with visual evidence before delivery.

## Internal Tool Use

Scripts are support tools, not user-facing rituals. Codex may use:

- `scripts/design_brain_intent_route.py` for routing decisions.
- `scripts/design_brain_sequential_batch.py` for multiple-template tasks that need per-cycle reference selection and pattern locks.
- `scripts/design_brain_medium_playbook.py` for medium/product-type diagnosis.
- `scripts/design_brain_originality_score.py` for reference similarity and copy-risk scoring.
- `scripts/design_brain_template_orchestrate.py` for sellable template product planning.
- `scripts/design_brain_subagent_orchestrate.py` for active subagent selection, receipt/evidence requirements, and final critical-evidence blocking.
- `scripts/design_brain_subagent_receipt_validate.py` for semantic receipt validation, screenshot evidence checks, design-system depth checks, originality score checks, and marketplace verdict proof.
- `scripts/design_brain_design_simulate.py` for Design Simulation Layer pre-build verdicts and required repair plans.
- `scripts/design_brain_reference_insight.py` for reusable reference lessons.
- `scripts/design_brain_name_check.py` for naming originality.
- `scripts/design_brain_review.py` for critique reports.
- `scripts/design_brain_visual_review.py` for screenshot or rendered evidence review.
- `scripts/design_brain_build_record.py` only after a template direction is accepted.
- `scripts/design_brain_lint_plan.py` to catch missing Figma auto-layout, shallow structure, or repeated scaffold risks before building.
- `skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs` to verify a built web deck against the stage, slide-switching, navigation, reduced-motion, and print rules before review.
- `skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs` for rendered web-deck evidence at stage size, including slide-change and reduced-motion behavior.
- `.design-brain/templates/FIGMA_REFERENCE_SCHEMA_RECEIPT.md` as the required planning shape when a Figma reference drives a template.
- `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md` as the required professional reading order for Figma template references.
- `.design-brain/CONTINUOUS_DESIGNER_LEARNING_LOOP.md` and `.design-brain/templates/DESIGNER_LEARNING_CYCLE.md` for post-build or long-horizon professional designer learning.

Do not modify `DESIGN_MEMORY.md` or `DESIGN_PREFERENCES.json` values from autopilot behavior. Do not add fake journal entries. Do not promote memory automatically.

## Continuous Learning Rhythm

When the user frames the work as a long-term learning goal, Codex should not stop at the latest deliverable. The active learning rhythm is:

build or study -> inspect result -> identify uncertainty -> ask a deeper question -> search evidence when useful or requested -> distill designer schema -> update workflow/checklist when permitted -> apply the lesson in the next build.

The next question matters. A design lesson that creates no better question is usually too shallow.

## Active Batch Rhythm

For batch work, avoid studying every reference globally, creating one shared batch scaffold, and then producing variants. The active autopilot rhythm is:

reference study for template 1 -> build template 1 -> lock pattern -> reference study for template 2 -> build template 2 -> lock pattern -> repeat until the user request is complete.

The required batch rhythm is:

reference study -> structure fingerprint -> visual-language fingerprint -> build -> applied effect/gradient review -> screenshot or visual review -> pairwise audit -> pattern lock -> scaffold disposal -> next cycle.
