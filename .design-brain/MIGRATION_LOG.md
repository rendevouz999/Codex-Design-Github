# Migration Log

## 2026-10-10 - v2.8.0 Web Deck Medium + Activation Layer

- Added the Web Deck medium so browser-rendered decks route to their own module instead of loosening the static presentation-deck guards.
- Added Web Deck Intelligence, Web Deck Stage Gate, Web Deck Motion Grammar, Web Deck Delivery Contract, and Deck Source Bridge as the knowledge layer for the medium.
- Added the `skills/presentation-deck/resources/web-deck/` runtime kit with the `design-brain.web-deck.deck-plan.v1` plan schema, stage stylesheet, and dependency-free deck runtime.
- Added `deck-motion` and `web-deck-stage-fidelity` craft axes, the `web-deck` seed pack, the `motion-stage` direction pack, and the Web Deck receipt template.
- Added the Node ESM web deck tool chain for plan, audit, render review, deck source extraction, and smoke coverage, because the runtime-facing tools must drive a browser and parse generated HTML.
- Added the Claude Code activation layer: plugin and marketplace manifests, the Brain Design router skill, the Web Deck builder skill, and session-start plus prompt-submit hooks.
- Registered `/design-web-deck` and the `web_deck_tool` runtime tool at the `plan_only` permission tier.
- Kept the web-deck gates inside the existing build and post-build stages instead of adding a new required runtime stage.
- Fixed the missing section-layout managed/mandatory cross-check loop and the stale release ZIP filename in package integrity.
- Bumped active package/version identity to `2.8.0` and preserved historical `v2.7.0` upgrade notes.

## 2026-06-02 - v2.7.0 Section Layout Matching & Dedupe Gate

- Added Section Layout Matching Gate as an exploratory dedupe layer for section layout extraction.
- Extended section pattern schema with structural signatures, match status, match score, match group, duplicate/variant lineage, matching evidence, and dedupe decision fields.
- Updated section layout extraction so candidates are matched against stable catalog patterns and `_incoming` before new pattern files are written.
- Exact duplicates now write `_incoming/_matches/` receipts only; near duplicates write match receipts plus review candidates; variants keep `variantOf`; new patterns remain incoming until Hyper-Accuracy PASS.
- Added `match` CLI and matching smoke tests for exact duplicate, near duplicate, variant, new pattern, and duplicate stable validation behavior.
- Bumped active package/version identity to `2.7.0` and preserved historical `v2.6.3` upgrade notes.

## 2026-06-01 - v2.6.3 Product-Grade Design System Gate Hotfix

- Added a Product-Grade Website Design System Contract so marketplace website/Figma/source templates cannot pass with compact color/type/button/card style summaries.
- Hardened batch gates so each template pair requires a buyer-usable design-system board before the next template can start.
- Added required receipt fields for product DNA, product-specific modules, reusable section patterns, visual-language rules, reference-standard coverage, usage examples, package/source map, accessibility/editing notes, and board metrics.
- Hardened `design_brain_design_system_check.py` to fail missing board metrics, insufficient component/module/pattern/example counts, compact style-summary boards, and missing category-specific modules.
- Hardened subagent semantic validation so design-system-depth evidence must include product DNA, stronger component/state/module counts, package/source map, and board metrics or artifact evidence.
- Added smoke-test coverage proving compact style-summary design systems now FAIL and receipt-only design systems BLOCK final post-build readiness.

## 2026-06-01 - v2.6.3 Serial Provenance Gate Hotfix

- Added Serial Provenance Gate for multi-template website/Figma/source batches.
- Added mandatory scaffold disposal stage before the next template cycle can start.
- Added a post-build Pass 0 so all-at-once scaffold batches cannot return READY before visual/design-system/similarity passes.
- Added same-shaped receipt/fingerprint morphology detection for the exact failure pattern where multiple templates are generated from one shared builder.
- Hardened build-session lifecycle so a new template cannot register until earlier templates are fingerprint locked and scaffold-disposed.
- Integrated the gate into autoload, source-of-truth routing, batch hard gates, post-build completion, natural intent, AGENTS installer text, and package integrity.
- Verified the rejected 2026-06-01 website-template pack now BLOCKS instead of passing when the lifecycle ledger is missing and cognition/fingerprint receipts have identical morphology.

## 2026-05-31 - v2.6.3 Worker Exit Finalization + Supervisor Watchdog

- Added Subagent Receipt Semantic Validator so Brain Design blocks fake, placeholder, invalid, or shallow subagent receipts instead of passing on file presence alone.
- Added semantic validation smoke tests for bad evidence BLOCK and structured evidence PASS.
- Fixed process smoke worker done-but-not-exited hang.
- Added worker hard-exit mode for supervisor-managed worker subprocesses.
- Added supervisor detection for `done` status without process exit.
- Added parent-side watchdog for per-worker timeout and cleanup deadline.
- Repeat 3 and repeat 5 process smoke now complete reliably.
- Export preflight now runs process smoke repeat 5 by default.
- Preserved Design Agent Runtime, Design Cognition Contract, Design Simulation Layer, Sequential Layout Originality Gate, Post-Build Completion Gate, and Design Craft bridge.
- Added Subagent Orchestration Layer so Brain Design can assign accountable design roles with required evidence and blocking authority before final readiness is claimed.

## 2026-05-31 - v2.6.2 Supervisor Hard Timeout Isolation

- Fixed process smoke supervisor hard-timeout behavior.
- Supervisor no longer uses `run_command()` or `kill_process_tree()` to terminate hung workers.
- Added supervisor-native hard kill implementation with isolated worker process group/session.
- Added worker watchdog/status heartbeat evidence for startup, invocation resolution, normal command, failed command, simple timeout, direct nested kill, and done phases.
- Package integrity runtime keeps process smoke active and bounded.
- Preserved Design Agent Runtime, Design Cognition Contract, Design Simulation Layer, Sequential Layout Originality Gate, Post-Build Completion Gate, and Design Craft bridge.

## 2026-05-31 - v2.6.1 Independent Process Smoke Supervisor Fix

- Refactored process-utils smoke supervisor to launch workers with an independent direct subprocess runner instead of `run_command()`.
- Added temporary-file stdout/stderr capture, manual polling timeout, and process-tree kill to the supervisor worker runner.
- Added supervisor-resolved Python invocation handoff to worker processes through environment variables.
- Added `BRAIN_DESIGN_SKIP_PYTHON_PROBES` worker behavior so repeated workers do not redo fragile probe cycles.
- Added stability-pass probing for the supervisor-selected Python invocation.
- Package integrity now uses a longer process smoke max duration for repeat worker supervision.
- Preserved Design Cognition Contract, Design Simulation Layer, Post-Build Completion Gate, Sequential Layout Originality Gate, Design Agent Runtime, and Design Craft support adapter behavior.

## 2026-05-30 - v2.6.0 Design Agent Runtime

- Added Claude-Code-style pattern adaptation as original Brain Design runtime.
- Added runtime command registry, tool registry, permission modes, hooks, session state, repair tickets, doctor/status, and context compaction.
- Wrapped existing gates as runtime tools.
- Added runtime smoke tests.
- Integrated Design Craft as support-only craft adapter.
- Added Design Craft v0.3.0 Craft Tool Adapter files and smoke tests.
- No Claude Code source copied or bundled.
- Preserved Design Cognition Contract, Design Simulation Layer, Sequential Layout Originality Gate, Build Session Lifecycle, and Post-Build Completion Gate.

## 2026-05-30 - v2.5.0 Sequential Layout Originality Gate + Build Session Lifecycle

- Added build-session lifecycle ledger.
- Added Sequential Layout Originality Gate.
- Added reference-vs-AI layout audit before build/final.
- Added AI-output-vs-previous-AI-output pairwise layout audit.
- Added fingerprint locking before proceeding to next batch template.
- Added axis-based layout similarity scoring.
- Added idea recovery corpus config for local Template Website folder.
- Added lifecycle smoke test.
- Added layout audit smoke test.
- Integrated layout audit with Design Cognition, Design Simulation, Post-Build Completion Gate, and Batch Hard Gates.

## 2026-05-30 - v2.4.6 Python Child Invocation Policy Fix

- Added Python invocation policy: executable + runtime flags are resolved together.
- Resolver now probes the same invocation mode used by runtime commands.
- Added fallback from plain Python to safe `-S` Python mode when site startup/shutdown hangs.
- Process utils smoke now passes without BRAIN_DESIGN_PYTHON in environments where plain Python child execution hangs.
- Preserved cognition enforcement, simulation layer, post-build gate, routing guard, and package hygiene.

## 2026-05-30 - v2.4.5 Deterministic Runtime Smoke Refactor

- Refactored process-utils smoke to avoid race-prone nested ready-file timeout checks.
- Split run_command timeout test from process-tree kill test.
- Added direct nested process-tree kill verification after explicit ready handshake.
- Added deterministic supervisor worker tests.
- Preserved runtime checks, cognition enforcement, simulation layer, post-build gate, routing guard, and package hygiene.

## 2026-05-30 - v2.4.4 Deterministic Runtime Runner Finalization

- Added child-execution sanity check for Python executable resolver.
- Added automatic fallback when `sys.executable` is valid but unusable as a child process.
- Split process-utils smoke into single-iteration worker and repeat supervisor.
- Added supervisor timeout per repeat iteration.
- Prevented process-utils smoke from hanging the whole runtime proof.
- Preserved cognition enforcement, simulation layer, post-build gate, routing guard, and package hygiene.

## 2026-05-30 - v2.4.3 Cross-Environment Runtime Runner Stability

- Fixed Python executable resolver to avoid fragile subprocess probes.
- Current Python 3 interpreter is trusted by default when valid.
- Added non-isolated default subprocess mode to avoid Popen hangs caused by session/process-group startup.
- Process tree kill still uses psutil/procfs/taskkill, but no longer requires process-group creation by default.
- Process utils smoke now passes repeat tests without environment override.
- Package integrity and export runtime checks remain enabled.

## 2026-05-30 - v2.4.2 Runtime Runner Hardening

- Reworked process runner to avoid pipe/communicate deadlocks.
- Runtime checks now capture stdout/stderr through temporary files instead of unbounded pipes.
- Added polling-based timeout loop with hard process-tree kill.
- Fixed process utils smoke hanging on repeat iterations.
- Package integrity runtime can run repeatedly without hanging.
- Preserved v2.4.1 cognition enforcement and package hygiene.

## 2026-05-29 - v2.4.1 Cognition Enforcement + Runtime Hygiene

- Design Simulation Layer now validates cognition receipts using the cognition checker.
- Missing cognition receipt blocks reference-led/template simulation unless explicitly allowed.
- Fake status-only cognition receipts no longer pass.
- Added machine-readable cognition receipt template.
- Post-build audit can require cognition receipts for template builds.
- Fixed runtime smoke hanging in agent source override/process utils repeat.
- Public-core export excludes `.bak-*` backup files.
- Public-core export excludes TypeUI-managed files by default.
- Integrity checker now fails when backup or TypeUI-managed files are included.

## 2026-05-29 - v2.4.0 Design Cognition Contract

- Added mandatory 10-step design cognition workflow.
- Added Style DNA, Design Intent Lock, Visual Grammar, Reference Boundary, Color Role Re-Mapping, Visual Mood Reinterpretation, Structural Reconfiguration, Pattern Divergence, Section Logic, and Marketplace Readiness as required workflow contract.
- Added cognition receipt template.
- Added cognition gate.
- Added cognition checker script.
- Integrated cognition receipt into Reference Insight, Template Orchestrator, Design Simulation Layer, Batch Hard Gates, Marketplace Quality Gate, and Post-Build Completion Gate.
- Added smoke tests for missing cognition fields, color identity copy risk, generic section logic, and marketplace readiness.

## 2026-05-29 - v2.3.0 Post-Build Design System & Triple Audit Gate

- Added mandatory post-build design system generation.
- Added automatic triple audit after each template build.
- Added batch pairwise similarity audit after multi-template build.
- Added auto-layout/source hygiene audit receipt.
- Added visual/layout defect audit receipt.
- Added repair loop after failed audit.
- Added final completion receipt as required output.
- Added smoke tests for missing design system, similar batch templates, auto-layout failure, and visual/layout defects.
- Preserved Design Simulation Layer as pre-build gate.
- Brain Design now has both pre-build simulation and post-build completion gate.

## 2026-05-29 - v2.2.4 Stable Runtime Smoke + Process Liveness Fix

- Fixed flaky process-utils smoke test.
- Added zombie/defunct process detection so zombies are not treated as active children.
- Added repeatable runtime integrity verification.
- Added Python executable resolver / override for subprocess checks.
- Preserved v2.2.3 marketplace routing guard and simulation router alignment.

## 2026-05-29 - v2.2.3 Realtime Runtime Safety + Fast Simulation Smoke

- Fixed nested subprocess timeout behavior.
- Added recursive process tree kill for children that create their own session/process group.
- Split simulation smoke into fast route-alignment tests and limited full simulation tests.
- Added quick/full/route-only modes for design simulation smoke.
- Package integrity and export now use quick bounded simulation smoke by default.
- Added process utility smoke test with intentionally hanging nested child.
- Preserved v2.2.2 marketplace routing guard.

## 2026-05-29 - v2.2.2 Runtime Reliability + Marketplace Routing Guard

- Fixed subprocess process-tree timeout/kill for simulation smoke, package integrity, and export checks.
- Fixed marketplace wording so template marketplace / Envato marketplace / marketplace-ready template does not trigger ecommerce routing.
- Added marketplace routing guard tests.
- Added simulation route tests with target buyer + visual mood + marketplace context.
- Fixed restaurant hospitality website simulation route not to fall into portfolio/ecommerce.
- Strengthened runtime integrity so checks either PASS, FAIL, or TIMEOUT with exact step.
- Strengthened export so ZIP integrity step cannot hang silently.
- Preserved Brain Design router as source of truth for Design Simulation Layer.

## 2026-05-29 - v2.2.1 Simulation Router Alignment + Release Reliability

- Design Simulation Layer now defers to Brain Design router/product-family detection.
- Removed unsafe standalone infer_mode behavior as source of truth.
- Fixed simulation routing for newsletter website, coffee shop, UI kit, pricing, social/static/document cases.
- Added router-alignment smoke tests for simulation layer.
- PASS verdict now has no requiredRepairs; non-blocking suggestions moved to recommendedImprovements.
- Added runtime timeout/fail-fast guards for package integrity and export ZIP checks.
- Strengthened JSON/agents/verdict schema validation.

## 2026-05-29 - v2.2.0 MiroFish-style Design Simulation Layer

- Added Design Simulation Layer as a Brain Design pre-build gate.
- Added design context graph, design agent panel, design verdict schema, and simulation artifacts.
- Added agent-based review before build/revision.
- Added PASS / REVISE / BLOCKED verdict.
- Added required repair plan output.
- Fixed installer/package support for simulation layer files.
- Fixed machine-readable JSON output.
- Fixed do-not-copy false-positive copy-risk.
- Added simulation smoke test and install integrity checks.
- Added licensing note: this layer adapts the MiroFish-style workflow pattern but does not bundle or copy MiroFish source code.

## 2026-05-29 - v2.1.3 Public-Core Cleanup Patch

- Fixed generated package manifest hash mismatch by hashing sanitized staging files instead of source files.
- Added generated package manifest hash validation in the integrity checker.
- Clarified public-core file categories and added unmanaged-file reporting.
- Excluded TypeUI raw, extracted, and TypeUI-managed imported skill files from public-core by default.
- Fixed coffee shop / cafe / kafe website routing so hospitality templates do not route to ecommerce.
- Fixed pricing page routing so pricing words alone do not route to ecommerce.
- Fixed .jsonl reference false-positive warnings by matching longer extensions first.
- Normalized .design-brain/templates/... references in Brain Design docs.
- Excluded generated .design-brain/exports assets from public-core unless intentionally promoted as public docs assets.

## 2026-05-29 - v2.1.2 Publish-Core Safety Patch

- Fixed package installability / manifest managed-files mismatch by keeping dev visual-review files in the public-core package when they are managed by installer/package scripts.
- Fixed editorial/blog/news/magazine website routing so content websites route to `website-template` with `editorial_blog_cms`, not `email-newsletter`.
- Excluded `.design-brain/tmp` binary source files from public-core and complete-internal exports by default.
- Sanitized or excluded local absolute path learning metadata from publish-safe exports.
- Strengthened Figma target wording: create a new Figma design file only when a valid configured project/file target exists.
- Strengthened package integrity checker for installer dry-run, manifest managed files, temp binary assets, absolute path leaks, routing sanity, and ZIP contents.
- Added install dry-run verification for source and extracted ZIP packages.
- Updated smoke tests to include editorial/newsletter distinction and package sanity checks.


## 2026-05-29 - Design Brain v2.1.1

- Backup snapshot: `.design-brain-backups/v2.1.1-preflight-20260529-010057`
- Migration type: additive safeguarded regression fix.
- Package version synced to `2.1.1`.

### Fixed
- Fixed missing hard gate files in export package: `.design-brain/BATCH_TEMPLATE_HARD_GATES.md` and `.design-brain/EFFECT_LANGUAGE_JUDGMENT.md`.
- Fixed stale Figma placeholder/project-target rule in workflow trigger documentation.
- Improved Indonesian batch and sequential-batch intent detection.
- Improved website routing edge cases for agency/studio, personal portfolio/case-study, finance consultant, and travel/hospitality booking prompts.
- Added referenced-file integrity check so missing mandatory rules fail status/integrity instead of reporting ready.
- Added package export verification and publish-safe ZIP generation.
- Removed cache/pyc from package export.

### Created
- `scripts/design_brain_package_integrity.py`
- `scripts/design_brain_export_package.py`
- `PUBLIC_PACKAGE_NOTES.md`

### Verification
- Router smoke tests expanded beyond v2.1.0 coverage.
- Package integrity is required before and after export.

## 2026-05-28 - Design Brain v2.1.0

- Backup snapshot: `.design-brain-backups/v2.1.0-preflight-20260528-235612`
- Migration type: additive safeguarded upgrade.
- Stable memory untouched: `DESIGN_MEMORY.md`, `DESIGN_PREFERENCES.json`.

### Created
- `README.md`
- `.design-brain/ROUTING_ALIASES_ID.json`
- `.design-brain/REFERENCE_CORPUS_CONFIG.md`
- `.design-brain/SOURCE_OF_TRUTH_MAP.md`
- `.design-brain/QUALITY_GATE_FAILURE_TAXONOMY.md`
- `.design-brain/FIGMA_OUTPUT_TARGET.local.example.json`
- `.design-brain/proposed-rules/README.md`
- `.design-brain/templates/PROPOSED_RULE_CHANGE.md`
- `scripts/design_brain_reference_corpus_health.py`
- `scripts/design_brain_router_smoke_test.py`

### Updated
- Fixed website-template over-routing in `scripts/design_brain_modules.py`.
- Added Indonesian alias normalization and specific-product override in `scripts/design_brain_website_types.py`.
- Added Indonesian query expansion and corpus-empty warnings in `scripts/design_brain_website_reference_select.py`.
- Made Figma build rules global for source-template/editable Figma output.
- Added Figma target placeholder safety and private local config guidance.
- Added source-of-truth cross references across AGENTS, README, autoload, router, trigger map, and autopilot docs.
- Added quality-gate root-cause taxonomy across product, marketplace, batch, visual, review, lint, and originality workflows.
- Hardened website section-depth locks, sequential batch cycles, and proposed-rule learning workflow.
- Added router smoke tests for module selection, website product type selection, landing behavior, Indonesian aliases, Figma placeholder behavior, and corpus health.

### Verification
- `python scripts/design_brain_router_smoke_test.py` -> 29/29 passed.

### Skipped
- No old rule files were aggressively deleted.
- No fake memory or preference values were added.

## 2026-05-26 22:34:17 - Design Brain v2.0.0

- Rollback snapshot: `.design-brain-snapshots/v2.0.0-preflight-20260526-223018`
- Migration type: additive safeguarded upgrade.
- Stable memory untouched: `DESIGN_MEMORY.md`, `DESIGN_PREFERENCES.json`.

### Created
- .design-brain/VERSION.md
- skills/presentation-deck/design/00_input_system/template-brief-schema.md
- skills/presentation-deck/design/00_input_system/target-buyer-library.md
- skills/presentation-deck/design/00_input_system/marketplace-target-rules.md
- skills/presentation-deck/design/00_input_system/output-format-rules.md
- skills/presentation-deck/design/00_input_system/reference-classification.md
- skills/presentation-deck/design/00_input_system/asset-rules.md
- skills/presentation-deck/design/00_input_system/scoring-priority-system.md
- skills/presentation-deck/design/01_powerpoint_technical/slide-master-rules.md
- skills/presentation-deck/design/01_powerpoint_technical/slide-layout-rules.md
- skills/presentation-deck/design/01_powerpoint_technical/placeholder-system.md
- skills/presentation-deck/design/01_powerpoint_technical/theme-color-font-rules.md
- skills/presentation-deck/design/01_powerpoint_technical/pptx-openxml-structure.md
- skills/presentation-deck/design/01_powerpoint_technical/editable-template-rules.md
- skills/presentation-deck/design/01_powerpoint_technical/export-compatibility-rules.md
- skills/presentation-deck/design/02_design_principles/visual-hierarchy.md
- skills/presentation-deck/design/02_design_principles/grid-spacing-alignment.md
- skills/presentation-deck/design/02_design_principles/typography-system.md
- skills/presentation-deck/design/02_design_principles/color-system.md
- skills/presentation-deck/design/02_design_principles/composition-patterns.md
- skills/presentation-deck/design/02_design_principles/slide-rhythm.md
- skills/presentation-deck/design/02_design_principles/premium-vs-generic.md
- skills/presentation-deck/design/02_design_principles/visual-polish-rules.md
- skills/presentation-deck/design/03_slide_archetypes/cover-slide.md
- skills/presentation-deck/design/03_slide_archetypes/agenda-slide.md
- skills/presentation-deck/design/03_slide_archetypes/section-divider-slide.md
- skills/presentation-deck/design/03_slide_archetypes/problem-slide.md
- skills/presentation-deck/design/03_slide_archetypes/solution-slide.md
- skills/presentation-deck/design/03_slide_archetypes/feature-slide.md
- skills/presentation-deck/design/03_slide_archetypes/data-slide.md
- skills/presentation-deck/design/03_slide_archetypes/timeline-slide.md
- skills/presentation-deck/design/03_slide_archetypes/roadmap-slide.md
- skills/presentation-deck/design/03_slide_archetypes/pricing-slide.md
- skills/presentation-deck/design/03_slide_archetypes/team-slide.md
- skills/presentation-deck/design/03_slide_archetypes/portfolio-slide.md
- skills/presentation-deck/design/03_slide_archetypes/testimonial-slide.md
- skills/presentation-deck/design/03_slide_archetypes/dashboard-slide.md
- skills/presentation-deck/design/03_slide_archetypes/case-study-slide.md
- skills/presentation-deck/design/03_slide_archetypes/closing-slide.md
- skills/presentation-deck/design/04_marketplace_standard/envato-presentation-requirements.md
- skills/presentation-deck/design/04_marketplace_standard/file-organization.md
- skills/presentation-deck/design/04_marketplace_standard/documentation-requirements.md
- skills/presentation-deck/design/04_marketplace_standard/preview-image-rules.md
- skills/presentation-deck/design/04_marketplace_standard/marketplace-originality-rules.md
- skills/presentation-deck/design/04_marketplace_standard/buyer-usability-rules.md
- .design-brain/05_reference_breakdowns/reference-analysis-template.md
- .design-brain/05_reference_breakdowns/good-bad-reference-pairs.md
- .design-brain/05_reference_breakdowns/plagiarism-transformation-method.md
- .design-brain/05_reference_breakdowns/redesign-from-reference-method.md
- .design-brain/05_reference_breakdowns/reference-to-original-concept-pipeline.md
- skills/presentation-deck/design/06_quality_control/design-review-checklist.md
- skills/presentation-deck/design/06_quality_control/powerpoint-technical-checklist.md
- skills/presentation-deck/design/06_quality_control/accessibility-checklist.md
- skills/presentation-deck/design/06_quality_control/marketplace-readiness-checklist.md
- skills/presentation-deck/design/06_quality_control/premium-polish-scorecard.md
- skills/presentation-deck/design/06_quality_control/generic-design-detector.md
- skills/presentation-deck/design/06_quality_control/final-export-checklist.md
- .design-brain/07_visual_pipeline/chromium-visual-review.md
- .design-brain/07_visual_pipeline/playwright-setup.md
- .design-brain/07_visual_pipeline/screenshot-review-checklist.md
- .design-brain/07_visual_pipeline/overlap-detection-rules.md
- .design-brain/07_visual_pipeline/desktop-mobile-preview-rules.md
- .design-brain/07_visual_pipeline/visual-regression-rules.md
- .design-brain/08_feedback_memory/feedback-log.md
- .design-brain/08_feedback_memory/accepted-design-patterns.md
- .design-brain/08_feedback_memory/rejected-design-patterns.md
- .design-brain/08_feedback_memory/premium-lessons.md
- .design-brain/08_feedback_memory/client-style-preferences.md
- .design-brain/08_feedback_memory/README.md
- skills/presentation-deck/design/09_prompt_system/master-agent-instruction.md
- skills/presentation-deck/design/09_prompt_system/reference-analyzer-prompt.md
- skills/presentation-deck/design/09_prompt_system/slide-planner-prompt.md
- skills/presentation-deck/design/09_prompt_system/design-system-builder-prompt.md
- skills/presentation-deck/design/09_prompt_system/pptx-qa-prompt.md
- skills/presentation-deck/design/09_prompt_system/visual-review-prompt.md
- skills/presentation-deck/design/09_prompt_system/natural-intent-router.md
- .design-brain/evidence/README.md
- .design-brain/evidence/visual-reviews/README.md

### Updated
- .design-brain/MANIFEST.json
- .design-brain/AUTOLOAD_POLICY.md
- .design-brain/CONTEXT_PRIORITY.md
- .design-brain/QUICK_START.md

### Skipped

## 2026-05-26 22:45:00 - v2.0.0 Tooling And Status Wiring

- Rollback snapshot: `.design-brain-snapshots/v2.0.0-preflight-20260526-223018`
- Migration type: additive safeguarded upgrade continuation.
- Stable memory untouched: `DESIGN_MEMORY.md`, `DESIGN_PREFERENCES.json`.

### Created
- package.json
- package-lock.json
- .gitignore
- tsconfig.json
- playwright.config.ts
- tests/visual-review.spec.ts
- .design-brain/evidence/visual-reviews/playwright-smoke.png
- .design-brain/evidence/visual-reviews/playwright-smoke-review.md

### Updated
- .design-brain/MANIFEST.json
- .design-brain/AUTOLOAD_POLICY.md
- .design-brain/MIGRATION_LOG.md
- scripts/design_brain_status.py
- scripts/install_design_brain.py
- scripts/design_brain_v2_upgrade.py

### Skipped
- No v1/v1.8 Design Brain files were deleted, moved, or renamed.

### Backed Up
- .design-brain/
- AGENTS.md
- scripts/design_brain*.py
- scripts/install_design_brain.py
- .design-brain/MANIFEST.json
- Root tooling files present before migration

## 2026-05-26 23:33:35 - Website Template Structure Standardization

- Source studied: `<LOCAL_REFERENCE_CORPUS>/Template Website`
- Migration type: additive structure-rule upgrade.
- Stable memory untouched: `DESIGN_MEMORY.md`, `DESIGN_PREFERENCES.json`.

### Created
- .design-brain/seed-packs/website-template/layouts.md
- .design-brain/seed-packs/website-template/checklist.md
- .design-brain/seed-packs/website-template/content-patterns.md
- .design-brain/seed-packs/website-template/design-system-scope.md
- .design-brain/seed-packs/hero-header-kit/layouts.md
- .design-brain/seed-packs/hero-header-kit/checklist.md
- .design-brain/seed-packs/hero-header-kit/content-patterns.md
- .design-brain/seed-packs/hero-header-kit/design-system-scope.md
- .design-brain/reference-insights/20260526-template-website-structure-standards.md

### Updated
- .design-brain/registry/modules.json
- .design-brain/MANIFEST.json
- .design-brain/TEMPLATE_STRUCTURE_RULES.md
- .design-brain/MEDIUM_PRODUCT_PLAYBOOKS.md
- .design-brain/TEMPLATE_PRODUCT_QUALITY_GATE.md
- .design-brain/AUTOLOAD_POLICY.md
- .design-brain/CONTEXT_PRIORITY.md
- .design-brain/QUICK_START.md
- .design-brain/craft/anti-ai-slop.md
- .design-brain/craft/layout-composition.md
- .design-brain/seed-packs/landing-page/layouts.md
- .design-brain/seed-packs/landing-page/checklist.md
- .design-brain/seed-packs/landing-page/content-patterns.md
- .design-brain/seed-packs/landing-page/design-system-scope.md
- .design-brain/08_feedback_memory/rejected-design-patterns.md
- .design-brain/08_feedback_memory/accepted-design-patterns.md
- .design-brain/08_feedback_memory/premium-lessons.md
- scripts/design_brain_status.py
- scripts/install_design_brain.py
- scripts/design_brain_lint_plan.py

### Skipped
- DESIGN_MEMORY.md and DESIGN_PREFERENCES.json were not changed.

## 2026-05-26 23:57:00 - FIG Template Corpus Extraction

- Source studied: `<LOCAL_REFERENCE_CORPUS>/Template Website`
- Migration type: additive evidence/corpus extraction workflow.
- Stable memory untouched: `DESIGN_MEMORY.md`, `DESIGN_PREFERENCES.json`.
- Latest extraction: `.design-brain/evidence/fig-extracts/20260526-235320-fig-template-corpus`
- Extraction result: 34 `.fig` files found, 26 main files processed, 8 AppleDouble/resource fork files skipped, 26 decoded, 0 failed.

### Created
- scripts/design_brain_fig_extract.mjs
- .design-brain/evidence/fig-extracts/README.md
- .design-brain/evidence/fig-extracts/latest.json
- .design-brain/evidence/fig-extracts/20260526-235320-fig-template-corpus/
- .design-brain/reference-insights/20260526-fig-template-corpus-learning.md

### Updated
- package.json
- package-lock.json
- .design-brain/MANIFEST.json
- .design-brain/MIGRATION_LOG.md
- .design-brain/TEMPLATE_STRUCTURE_RULES.md
- .design-brain/evidence/README.md
- .design-brain/AUTOLOAD_POLICY.md
- .design-brain/CONTEXT_PRIORITY.md
- .design-brain/QUICK_START.md
- scripts/design_brain_status.py
- scripts/install_design_brain.py

### Skipped
- DESIGN_MEMORY.md and DESIGN_PREFERENCES.json were not changed.
- `__MACOSX` and `._*.fig` AppleDouble/resource fork files were skipped by default.
