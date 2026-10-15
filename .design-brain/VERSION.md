# Design Brain Version

- Current version: Design Brain v2.8.0
- Previous version: Design Brain v2.7.0
- Upgrade date: 2026-10-10
- Upgrade type: Web Deck Medium + Activation Layer
- Rollback snapshot: `.design-brain-backups/v2.7.0-preflight-20261010-221155`

## v2.8.0 Focus

- Added the Web Deck medium for browser-rendered decks, with `web_deck`, `html_deck`, `browser_presentation`, `animated_slides`, and `web_slides` as its medium strings.
- Added Web Deck Intelligence, Web Deck Stage Gate, Web Deck Motion Grammar, and Web Deck Delivery Contract as the knowledge layer for the medium.
- Added the `skills/presentation-deck/resources/web-deck/` runtime kit: `design-brain.web-deck.deck-plan.v1` plan schema, stage stylesheet, and dependency-free deck runtime.
- Added `deck-motion` and `web-deck-stage-fidelity` craft axes, the `web-deck` seed pack, the `motion-stage` direction pack, and the Web Deck receipt template.
- Added the Deck Source Bridge so an existing static deck can be read as planning material instead of being converted blindly.
- Added the Node ESM web deck tool chain for plan, audit, render review, deck source extraction, and smoke coverage, because the runtime-facing tools must drive a browser and parse generated HTML.
- Added the Claude Code activation layer: plugin and marketplace manifests, the Brain Design router skill, the Web Deck builder skill, and session-start plus prompt-submit hooks.
- Added `/design-web-deck` and the `web_deck_tool` runtime tool at the `plan_only` permission tier.
- Static deck work is unchanged: motion and runtime vocabulary stays forbidden for the presentation mode, and plain deck requests still route to `presentation-deck`.
- Preserved section layout extraction, Hyper-Accuracy Gate, Section Layout Matching Gate, `sectionPatternMix` fingerprint evidence, Design Agent Runtime, Design Cognition Contract, Design Simulation Layer, Sequential Layout Originality Gate, Post-Build Completion Gate, Subagent Orchestration, and Design Craft support bridge.

## v2.7.0 Focus

- Added Section Layout Matching Gate so extraction compares candidates against stable catalog patterns and `_incoming` before writing new vocabulary.
- Added exploratory dedupe statuses: `DUPLICATE`, `NEAR_DUPLICATE`, `VARIANT`, and `NEW_PATTERN`.
- Added required structural signature, match score, match group, duplicate/variant lineage, matching evidence, and dedupe decision fields to section pattern schema.
- Added `match` CLI for candidate-vs-catalog inspection.
- Exact duplicates now write receipts only; near duplicates write receipts plus review candidates; variants keep `variantOf`; new patterns remain incoming until Hyper-Accuracy PASS.
- Stable catalog validation now fails duplicate patterns inside the same section.
- Preserved section layout extraction, Hyper-Accuracy Gate, `sectionPatternMix` fingerprint evidence, Design Agent Runtime, Design Cognition Contract, Design Simulation Layer, Sequential Layout Originality Gate, Post-Build Completion Gate, Subagent Orchestration, and Design Craft support bridge.

## 2026-06-01 Serial Provenance Hotfix

- Added Serial Provenance Gate as Pass 0 for multi-template website/Figma/source batches.
- Post-build READY is blocked when lifecycle proof is missing, multiple final templates are produced from one builder/script/schema, or cognition/fingerprint/design-system receipts show same-shaped batch morphology.
- Build Session Lifecycle now requires `scaffold_disposed` before the next template cycle starts.
- The rejected 2026-06-01 website-template pack now returns BLOCKED for missing serial provenance and identical receipt/fingerprint morphology.

## v2.6.3 Focus

- Added Subagent Receipt Semantic Validator so final gates read evidence contents, not just file presence.
- Added semantic smoke tests that prove placeholder/smoke evidence blocks and structured subagent evidence passes.
- Added worker hard-exit mode for supervisor-managed process smoke workers.
- Added supervisor detection for workers that write `done` but do not exit.
- Added parent-side per-worker watchdog with a second hard cleanup deadline.
- Timeout diagnostics now report reason, last worker status, status path, kill strategy, killed PIDs, and output excerpts.
- Export preflight now exercises process smoke repeat 5 by default.
- Preserved Design Agent Runtime, Design Cognition Contract, Design Simulation Layer, Sequential Layout Originality Gate, Post-Build Completion Gate, and Design Craft support bridge.
- Preserved Subagent Orchestration and hardened it with semantic receipt validation for visual QA, design-system depth, originality, Figma source QA, and marketplace verdicts.

## v2.6.2 Focus

- Added supervisor-native hard timeout kill for process-utils smoke workers.
- Supervisor worker timeout no longer calls `run_command()` or `kill_process_tree()`.
- Worker subprocesses are started in an isolated process group/session only for supervisor control.
- Added worker status heartbeat phases so timeout output reports the last observed worker phase.
- Preserved Design Agent Runtime, Design Cognition Contract, Design Simulation Layer, Sequential Layout Originality Gate, Post-Build Completion Gate, and Design Craft support bridge.

## v2.6.1 Focus

- Refactored the process-utils smoke supervisor so worker iterations are launched by an independent direct subprocess runner instead of `run_command()`.
- Added supervisor-to-worker Python invocation handoff through `BRAIN_DESIGN_RESOLVED_PYTHON*` environment variables.
- Added stability-pass probing for the supervisor-selected Python invocation while allowing workers to skip redundant probes.
- Preserved the worker proofs for `run_command()` normal command, failed command, simple timeout, and direct nested process-tree kill.
- Kept runtime, package integrity, export, cognition enforcement, simulation, post-build, sequential layout, and Design Craft adapter checks active.
- Added Subagent Orchestration Layer with 12 accountable design subagents, schemas, receipt template, runtime command/tool wiring, smoke test, and package integrity checks.

## v2.6.0 Focus

- Added Design Agent Runtime command registry, tool registry, permission modes, hooks, session state, repair tickets, doctor/status, and context compaction.
- Wrapped existing Brain Design gates as runtime tools.
- Added Design Craft support adapter integration.
- Preserved Design Cognition Contract, Design Simulation Layer, Sequential Layout Originality Gate, Build Session Lifecycle, and Post-Build Completion Gate.
- Claude Code ZIP was used only as architecture reference; no source was copied or bundled.

## v2.5.0 Focus

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

## v2.4.6 Focus

- Added Python invocation policy: executable and runtime flags are resolved together.
- Resolver probes the same invocation mode used by runtime commands.
- Added fallback from plain Python to safe `-S` Python mode when site startup/shutdown hangs.
- Process utils smoke passes without `BRAIN_DESIGN_PYTHON` in environments where plain Python child execution hangs.
- Preserved cognition enforcement, simulation layer, post-build gate, routing guard, and package hygiene.

## v2.4.5 Focus

- Refactored process-utils smoke to avoid race-prone nested ready-file timeout checks.
- Split run_command timeout test from process-tree kill test.
- Added direct nested process-tree kill verification after explicit ready handshake.
- Added deterministic supervisor worker tests.
- Preserved runtime checks, cognition enforcement, simulation layer, post-build gate, routing guard, and package hygiene.

## v2.4.4 Focus

- Added child-execution sanity check for Python executable resolver.
- Added automatic fallback when `sys.executable` is valid but unusable as a child process.
- Split process-utils smoke into single-iteration worker and repeat supervisor.
- Added supervisor timeout per repeat iteration.
- Prevented process-utils smoke from hanging the whole runtime proof.
- Preserved cognition enforcement, simulation layer, post-build gate, routing guard, and package hygiene.

## v2.4.3 Focus

- Fixed Python executable resolver to avoid fragile subprocess probes.
- Current Python 3 interpreter is trusted by default when valid.
- Added non-isolated default subprocess mode to avoid Popen hangs caused by session/process-group startup.
- Process tree kill still uses psutil/procfs/taskkill, but no longer requires process-group creation by default.
- Process utils smoke now passes repeat tests without environment override.
- Package integrity and export runtime checks remain enabled.

## v2.4.2 Focus

- Reworked process runner to avoid pipe/communicate deadlocks.
- Runtime checks capture stdout/stderr through temporary files instead of unbounded pipes.
- Added polling-based timeout loop with hard process-tree kill.
- Fixed process utils smoke hanging risk on repeat iterations.
- Package integrity runtime can run repeatedly without hanging.
- Preserved v2.4.1 cognition enforcement and package hygiene.

## v2.4.1 Focus

- Design Simulation Layer validates cognition receipts using the cognition checker.
- Missing cognition receipt blocks reference-led/template simulation unless explicitly allowed for non-final debug.
- Fake status-only cognition receipts no longer pass.
- Added machine-readable JSON cognition receipt template.
- Post-build audit can require cognition receipts for template builds.
- Fixed runtime smoke stability for agent source override and process utility repeats.
- Public-core export excludes `.bak-*` backup files and TypeUI-managed files by default.
- Integrity checker fails when backup or TypeUI-managed files are included in public-core ZIP.

## v2.4.0 Focus

- Added mandatory 10-step Design Cognition Contract before orchestration/build.
- Added Style DNA, Design Intent Lock, Visual Grammar, Reference Boundary, Color Role Re-Mapping, Visual Mood Reinterpretation, Structural Reconfiguration, Pattern Divergence, Section Logic, and Marketplace Readiness as required workflow terms.
- Added Design Cognition Receipt template, schema, checker, and smoke test.
- Made Color Role Re-Mapping mandatory so reference hue/palette identity is not copied.
- Strengthened Reference Boundary and Structural Reconfiguration as anti-copy and anti-scaffold rules.
- Connected Pattern Divergence to batch workflow, Section Logic to anti-generic structure, and Marketplace Readiness to quality gates.
- Integrated cognition receipt expectations into Template Orchestration, Design Simulation Layer, Batch Hard Gates, Marketplace Quality Gate, and Post-Build Completion Gate.
- Preserved Design Simulation Layer as pre-build gate and Post-Build Completion Gate as post-build gate.

## v2.3.0 Focus

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

## v2.2.4 Focus

- Fixed flaky process-utils smoke test.
- Added zombie/defunct process detection so zombies are not treated as active children.
- Added repeatable runtime integrity verification.
- Added Python executable resolver / override for subprocess checks.
- Preserved v2.2.3 marketplace routing guard and simulation router alignment.

## v2.2.3 Focus

- Fixed nested subprocess timeout behavior for realtime package use.
- Added recursive process tree kill for children that create their own session/process group.
- Split simulation smoke into fast in-process route-alignment tests and limited full simulation verdict tests.
- Added quick/full/route-only smoke modes with per-case progress, per-case timeout, and global deadline.
- Package integrity and export use quick bounded simulation smoke by default.
- Added process utility smoke test with an intentionally hanging nested child process.
- Preserved v2.2.2 marketplace routing guard and Brain Design router source-of-truth behavior.

## v2.2.2 Focus

- Fixed subprocess process-tree timeout/kill for simulation smoke, package integrity, and export checks.
- Fixed marketplace wording so template marketplace / Envato marketplace / marketplace-ready template does not trigger ecommerce routing.
- Added marketplace routing guard tests with target buyer and visual mood context.
- Fixed restaurant hospitality website simulation route not to fall into portfolio/ecommerce when gallery or marketplace-template wording appears.
- Strengthened runtime integrity and export ZIP checks so they PASS, FAIL, or TIMEOUT with exact step output.
- Preserved Brain Design router as source of truth for Design Simulation Layer.
