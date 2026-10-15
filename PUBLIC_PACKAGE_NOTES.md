# Public Package Notes

This public-core package contains Brain Design v2.8.0 with Web Deck Medium + Activation Layer, Worker Exit Finalization + Supervisor Watchdog, Design Agent Runtime, Subagent Orchestration Layer, Sequential Layout Originality Gate, Build Session Lifecycle, Python child invocation policy fix, Design Cognition Contract, Design Simulation Layer, and Post-Build Design System & Triple Audit Gate: workflow rules, scripts, routers, gates, runtime docs/schemas, taxonomy, source-of-truth map, cognition receipt/schema, subagent definitions/schemas, simulation agents/schema, lifecycle schemas, post-build audit schemas, web deck knowledge/schema/runtime kit, Claude Code activation files, and reusable templates needed to run the Design Brain system.

v2.8.0 adds the Web Deck medium for browser-rendered decks. A web deck is authored on a fixed 1920x1080 stage, fitted to the viewport by one uniform scale transform, navigated at runtime, deep-linkable per slide, reduced-motion aware, and printable as one slide per page. It is a separate medium from `presentation-deck`, so static PPTX/Keynote/Google Slides output keeps the Non-Web Mode Rule and plain deck requests still route to the static medium. The deck runtime has no dependencies, no CDN script, and no build step; fonts are the only external request. The web deck tool chain is Node ESM so the plan, audit, render-review, deck-source extraction, and smoke tools can drive the bundled browser and parse generated HTML.

The Claude Code activation layer ships `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `skills/brain-design/SKILL.md`, `skills/presentation-deck/workflows/web.md`, and the `hooks/` scripts. They activate Brain Design when this package itself is loaded as a Claude Code plugin. The installer does not copy them into other repositories: a copied plugin or marketplace manifest would register a duplicate plugin, and hook paths resolve only for the loaded plugin.

Subagent orchestration now includes a semantic receipt validator. Final gates do not only check whether subagent evidence files exist; they validate receipt contents for screenshot evidence, design-system depth, originality scores, Figma source QA, marketplace verdict proof, and placeholder/smoke evidence.

v2.6.3 fixes the process smoke worker done-but-not-exited hang class. Supervisor-managed workers run with a hard-exit flag, the parent detects `done` status without process exit, and per-worker watchdog deadlines prevent package integrity/export from waiting indefinitely on a completed but unreaped worker.

v2.6.2 isolates the process-utils smoke supervisor timeout path from the runtime helpers being tested. Hung workers are terminated by a supervisor-native hard kill path with isolated worker process groups/sessions, temporary stdout/stderr files, manual polling, bounded taskkill/procfs/parent kill fallbacks, and heartbeat status diagnostics.

v2.6.1 fixes the process-utils smoke supervisor. Repeat worker iterations are launched through an independent direct subprocess runner with temporary stdout/stderr files, manual polling timeout, and process-tree kill instead of using the `run_command()` function under test. The supervisor resolves the Python invocation once with stability passes, then hands the exact executable, flags, mode, and source to workers through `BRAIN_DESIGN_RESOLVED_PYTHON*` variables.

v2.6.0 adds a Brain Design-native Design Agent Runtime inspired by command/tool loop architecture patterns. It includes command registry, tool registry, permission modes, hooks, session state, repair tickets, doctor/status, context compaction, and a bundled Design Craft adapter bridge. Claude Code source is not copied or bundled.

The installable package now carries Design Craft v0.3.0 under `.design-brain/adapters/design-craft` so the active Brain Design craft adapter travels with the ZIP instead of relying on a source-machine `~/.codex/skills/design-craft` folder. Design Craft remains support-only and cannot override Brain Design gates.

The Subagent Orchestration Layer adds accountable design roles instead of cosmetic agent labels. It defines required inputs, required outputs, receipt evidence, blocking authority, and final PASS / REVISE_REQUIRED / BLOCK behavior for visual analysis, Style DNA, design-system depth, originality, Figma source QA, visual QA, and marketplace readiness.

v2.5.0 adds sequential layout originality checks. Each template must be fingerprinted, audited against its own reference layout, then for batch work audited against every previously accepted AI output before build/final delivery. A next template cannot start until the prior template has design system, post-build audit, and fingerprint lock.

The total integration stabilization layer remains preserved under v2.6.0 and keeps source-level enforcement: build-session `verify-final`, default completion-receipt enforcement for template final audits, design-system artifact evidence status, Design Craft non-override behavior, and source cleanup reporting.

The layout audit is axis-based. Hero grammar, section order, grid system, layout rhythm, card cadence, component patterns, CTA placement, image treatment, spacing, typography behavior, color roles, effect language, navigation/footer pattern, and scaffold risk are scored separately. A high-risk axis can fail the audit even when the aggregate score looks acceptable.

The optional idea recovery corpus points to `<CODEX_DESIGN_WORKSPACE>\Template Website` for layout-idea recovery only. It is local-only, not copied into the public-core ZIP, and cannot be used as a layout to copy.

v2.4.6 resolves Python as an invocation policy, not just an executable path. Brain Design probes plain Python, `-S`, and `-I -S` as exact runtime modes; if `-S` is the mode that passes, all internal runtime subprocess calls use `-S` too. This prevents a false pass where `candidate -I -S -c` works but later runtime commands launch plain Python and hang.

v2.4.5 removes the race-prone nested ready-file timeout check from default process utility smoke. `run_command()` timeout is proven with a simple sleeping command, while nested child/grandchild cleanup is proven by directly starting the nested process tree, waiting for explicit readiness, and then calling `kill_process_tree()`.

v2.4.4 finalizes runtime determinism. The Python resolver now proves that a candidate executable can run as a child process before accepting it, falls back from an unusable `sys.executable` to `python3` / `python`, and the process-utils smoke test runs repeat iterations through a supervisor that can kill a hung worker.

v2.4.3 improves cross-environment runtime stability. Runtime subprocesses use non-isolated creation mode by default to avoid process-group/session startup hangs.

v2.4.2 hardened runtime checks. The shared process runner captures stdout/stderr through temporary files, polls for timeout, kills the full process tree, and returns bounded PASS/FAIL/TIMEOUT results without pipe/communicate deadlocks.

v2.4.1 made cognition enforcement runtime-backed. Design Simulation validates cognition receipts with the cognition checker, fake status-only receipts fail, and reference-led/template simulations cannot PASS when cognition is missing or invalid. Post-build audit can also require a valid cognition receipt for template builds.

Automated cognition gates require JSON receipts. `.design-brain/templates/DESIGN_COGNITION_RECEIPT.md` is a human authoring template; `.design-brain/templates/DESIGN_COGNITION_RECEIPT.json` is the machine-readable JSON example/template used by checker and gates.

Public-core hygiene excludes `.bak-*`, `.backup-*`, `.orig`, `.tmp`, `.old`, TypeUI-managed markers, `.agents/skills/design-system/SKILL.md` when TypeUI-managed, and TypeUI-derived `DESIGN.md` files by default.

v2.4.0 adds a pre-orchestration cognition contract. Reference-led template builds must define Style DNA, Design Intent Lock, Visual Grammar, Reference Boundary, Color Role Re-Mapping, Visual Mood Reinterpretation, Structural Reconfiguration, Pattern Divergence, Section Logic, and Marketplace Readiness before build.

Color Role Re-Mapping is mandatory: references can teach emotional role, contrast behavior, hierarchy, and market positioning, but the output must use a new color identity unless the user explicitly requests an exact palette. Reference Boundary, Structural Reconfiguration, and Pattern Divergence block exact copy, repainted scaffolds, and repeated batch rhythm.

The Design Simulation Layer receives cognition receipt context when available, and the Post-Build Completion Gate can compare the built output against the cognition receipt. A cognition receipt is not a visual render check; it is the reasoning contract before orchestration/build.

v2.3.0 adds a post-build completion gate. A template is not complete until the template is built, a template-tied design system is built, all three audit passes run, critical issues are repaired, failed audits are rerun, and a completion receipt is generated.

Post-build triple audit includes:

- Originality, reference safety, and batch pairwise similarity.
- Design system, Figma/source hygiene, auto-layout, editability, component states, and responsive/source structure.
- Visual/layout QA for overlap, overflow, clipping, contrast, alignment, density, image crop, z-index, and responsive defects.

If screenshot/render inspection is unavailable, the final status must be READY_WITH_LIMITATIONS instead of claiming full visual verification.

v2.2.4 keeps simulation routing aligned with the Brain Design router, preserves marketplace-template routing guards, uses zombie-aware process liveness, and runs repeatable recursive process-tree smoke checks so runtime integrity and export cannot pass on a flaky one-off result.

Quick simulation smoke is the default for release and export checks. Full simulation smoke remains available for deeper regression runs, but every case still has a per-case timeout and a global deadline.

Set `BRAIN_DESIGN_PYTHON` to override the Python executable used by nested runtime checks. If it is absent, Brain Design tests `sys.executable`, `python3`, and `python` with bounded exact-mode child-execution probes and chooses the first invocation that prints `BD_PY_OK`.

## Design Simulation Layer Note

This Design Simulation Layer is a Brain Design-native implementation inspired by the MiroFish-style workflow pattern:
seed material -> context graph -> agent panel -> simulation rounds -> verdict/report.

It does not bundle, copy, import, or execute MiroFish source code.
It does not run OASIS or social/public-opinion simulation.
It adapts the architectural idea into a local design review and quality-gate workflow.

The simulation verdict is a pre-build gate. It is not a substitute for final visual review, screenshot/render inspection, or similarity verification on actual generated output.

## Included

- Core `.design-brain/` workflow files, gates, router docs, taxonomy files, and templates.
- Required `scripts/` for routing, status checks, reference corpus health checks, design simulation, simulation smoke tests, package integrity checks, install checks, and export.
- Design simulation docs, agent panel, verdict schema, and verdict template.
- Design cognition contract docs, cognition gate, receipt template, schema, checker script, and smoke test.
- Post-build completion gate docs, design-system requirements, triple-audit docs, schemas, receipt templates, post-build scripts, and post-build smoke tests.
- Sequential layout originality docs, lifecycle schemas, layout fingerprint/audit templates, layout similarity audit script, build-session ledger script, and sequential layout smoke test.
- Web deck knowledge files, stage gate, motion grammar, delivery contract, deck source bridge, deck plan schema, stage stylesheet, deck runtime, seed pack, receipt template, and the Node ESM web deck tools.
- Claude Code activation files: plugin and marketplace manifests, router and web deck skills, and hook scripts. They ship with the ZIP and are not installer-copied.
- Figma output safety docs and example local config file.
- Dev visual-review config files that are referenced by `package.json` scripts.
- Package manifest generated during export.

## Not Included By Default

The public-core package does not include the user's private local reference corpus by default.

Add a local website reference corpus at one of these paths:

- `Template Website/`
- `references/Template Website/`
- `.design-brain/reference-corpus/template-website/`

If the corpus is absent, local-reference-led selection must warn and ask for references or configuration. It must not claim that local reference selection succeeded.

The public-core package does not include `.design-brain/tmp` binary source files such as `.fig`, `.sketch`, `.xd`, `.psd`, `.ai`, `.eps`, or `.afdesign`.

The public-core package does not include raw local reference inventory/ledger files when they contain machine-local corpus metadata. Keep only sanitized summary docs and reusable workflow rules in public-core.

The public-core package does not include generated local report histories from folders such as `.design-brain/pilots/`, `.design-brain/reviews/`, `.design-brain/visual-reviews/`, or `.design-brain/reference-insights/` beyond their README files. Those reports often contain workspace-specific evidence paths.

Public-core does not include TypeUI raw, extracted, or TypeUI-managed imported skill files by default. Add or ingest TypeUI files locally if you want TypeUI style intelligence. Internal/private exports may opt into TypeUI-derived files explicitly.

The public-core package does not include generated `.design-brain/exports/` assets by default. Promote durable diagrams into a documented docs-assets folder before publishing them.

Visual similarity is not automatically verified unless screenshot/render inspection is actually performed and recorded.

The package does not include MiroFish/OASIS runtime, the user's local corpus by default, or raw TypeUI assets unless an explicitly different internal package mode is created.

Mandatory workflow files such as `.design-brain/BATCH_TEMPLATE_HARD_GATES.md` and `.design-brain/EFFECT_LANGUAGE_JUDGMENT.md` must always be included.

