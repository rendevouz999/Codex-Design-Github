# Codex Design Brain

This is the curated, public source distribution of the Codex Design Brain / Claude Code plugin. Clone this repository, run `claude plugin validate .`, and replace `<CODEX_DESIGN_WORKSPACE>` in local installation examples with the clone's actual folder. Configure private Supabase, Figma, and owner-verifier settings separately on your computer; no personal memory, local credentials, studio outputs, or source-reference repositories are included in this distribution.

The existing runtime now includes one [General Design Production Specialist](.design-brain/runtime/DESIGN_PRODUCTION_SPECIALIST.md), using the official OpenAI Agents SDK. Main remains in Codex/ChatGPT; authorized `start --production-request` calls automatically delegate bounded production to `gpt-6.1-sol` and return editable artifacts plus QA for Main review. The linked guide contains the actual capability matrix, tool restrictions, local setup, offline acceptance command, and application integration limits.

Codex Design Brain is a local workflow layer for premium, reference-led, marketplace-ready design template work. It does not retrain Codex; it gives the agent repo-local routing, taxonomy, critique, reference, Figma, batch, and learning rules.

Start with `.design-brain/AUTOLOAD_POLICY.md`. Resolve rule conflicts through `.design-brain/SOURCE_OF_TRUTH_MAP.md`.

## Presentation Design Capability

`skills/presentation-deck/` owns reusable Brand/Style/Layout/Deck design, native
PowerPoint generation and editing, and HTML/browser output. Shared design logic,
runtime, resources and tests are consolidated there. Selected MIT-licensed PPT
Master implementation is adopted internally with provenance and original notices;
no donor checkout, engine root or Git pin is required to run the capability.

Read [Presentation Design](skills/presentation-deck/SKILL.md). Use
`python skills/presentation-deck/runtime/presentation.py doctor` for native diagnosis.
The CLI selects the local `.venv-presentation` when present; `--python` and
`BRAIN_DESIGN_PYTHON` support another interpreter. Install
`skills/presentation-deck/runtime/requirements.txt` into that environment if needed.
Browser tools use the existing Node dependencies. PowerPoint/LibreOffice rendering
and optional media services require their declared prerequisites.

Technical readiness, rendered design review and source-edit fidelity are separate
evidence. `skills/presentation-deck/provenance/verification.json` records the tested
scope. Existing `design:pptx` and `design:web-deck` commands select internal modes.

## Install As A Claude Code Plugin

Load the repository in place through the personal skills directory, so Claude Code (CLI and Desktop) reads this working copy directly and runtime state stays in the one tree that the Codex host also uses:

```bash
cmd /c mklink /J "%USERPROFILE%\.claude\skills\codex-design" "<CODEX_DESIGN_WORKSPACE>"
claude plugin list
```

`claude plugin list` then shows `codex-design@skills-dir` with `Status: loaded`, and `${CLAUDE_PLUGIN_ROOT}` resolves to the junction path, which is the same tree as `<CODEX_DESIGN_WORKSPACE>`. Do not use `claude plugin marketplace add` plus `claude plugin install` for this repository: that route copies the whole tree, including `node_modules`, virtual environments and corpora, into `~/.claude/plugins/cache` as a stale snapshot, and plugin state would diverge from this directory. `CLAUDE_CODE_PLUGIN_DIRS` is an alternative in-place route on Claude Code v2.1.280 or later. While iterating on the skills or hooks, run `/reload-plugins` in the session to pick up edits without restarting Claude Code. Verify a manifest change with `claude plugin validate "<CODEX_DESIGN_WORKSPACE>"`.

On Claude Code the plugin's single Engineer is the bundled subagent `codex-design:general-design-production-engineer` (`agents/general-design-production-engineer.md`, `model: claude-opus-5-5`, `effort: xhigh`) and Main is Claude Fable 5.1. The Codex host keeps `gpt-6.1-sol` at `xhigh`; both hosts read this same tree, so the policy files name both mappings.

Key v2.8.0 additions:

- Brain Design v2.8.0 adds the Web Deck medium for browser-rendered decks: a fixed 1920x1080 authored stage, one uniform scale transform, keyboard/pointer/wheel navigation, deep links, reduced-motion behavior, and print output of one slide per page.
- `web-deck` is the browser-mode routing alias within the `presentation-deck` capability. Static PPTX/Keynote/Google Slides work keeps the Non-Web Mode Rule, and a plain presentation or deck request still routes to the static medium.
- The medium knowledge lives in `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md`, `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`, `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`, `skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md`, and `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md`.
- The `skills/presentation-deck/resources/web-deck/` kit ships the deck plan schema, stage stylesheet, and dependency-free deck runtime. `deck-motion` and `web-deck-stage-fidelity` are the new craft axes, `web-deck` is the new seed pack, and `motion-stage` is the new direction pack.
- The web deck tool chain is Node ESM: plan, audit, render review, deck source extraction, and smoke test, exposed as the `design:web-deck*` and `design:deck-source:extract` package scripts.
- The Claude Code activation layer adds `.claude-plugin/` plugin and marketplace manifests, the `skills/brain-design` router skill, the `skills/web-deck` builder skill, and `hooks/` session-start plus prompt-submit hooks. Those files activate this repository as a plugin; the installer does not copy them into other repositories.

Key v2.6.3 additions:

- Subagent receipts now have semantic validation: final gates read receipt contents, reject placeholder/smoke evidence, and block weak design-system, visual QA, originality, Figma QA, or marketplace verdict proof.
- Brain Design v2.6.3 fixes the process smoke worker `done`-but-not-exited hang class.
- Supervisor-managed workers receive `BRAIN_DESIGN_WORKER_HARD_EXIT=1`, so after PASS/failure output is flushed the worker exits with `os._exit(code)`.
- The supervisor detects `lastWorkerStatus=done` while the worker process is still alive, applies a short grace window, then fails with `reason=worker_done_but_not_exited` instead of hanging.
- Per-worker polling now has a parent-side deadline plus a second absolute cleanup deadline.
- Export preflight runs process smoke repeat 5 by default while package integrity keeps bounded repeat 3 runtime proof.

Key v2.6.2 additions:

- Brain Design v2.6.2 isolates the process-utils smoke supervisor timeout path from the runtime functions being tested.
- Supervisor worker timeout now uses a local supervisor-native hard kill implementation instead of `run_command()` or `kill_process_tree()`.
- Worker subprocesses are started in an isolated process group/session only inside the supervisor runner so a hung worker tree can be terminated without depending on runtime utility cleanup.
- Workers write heartbeat/status phases (`started`, `resolved_invocation`, `normal_command`, `failed_command`, `simple_timeout`, `direct_nested_kill`, `done`) so timeout diagnostics show the last observed phase.
- Package integrity and export keep process smoke, runtime smoke, simulation, cognition, post-build, sequential layout, and craft adapter checks enabled.

Key v2.6.1 additions:

- Brain Design v2.6.1 fixes the process-utils smoke supervisor so repeat workers are launched by an independent direct subprocess runner instead of the `run_command()` function under test.
- Supervisor worker launches use temporary stdout/stderr files, manual polling timeout, and process-tree kill without `PIPE` or `communicate()`.
- The supervisor resolves the Python invocation once with stability passes, then hands the exact executable, flags, mode, and source to workers through `BRAIN_DESIGN_RESOLVED_PYTHON*`.
- Workers can skip redundant Python probes via `BRAIN_DESIGN_SKIP_PYTHON_PROBES=1` while still running the actual runtime proofs.
- Package integrity and export keep runtime checks enabled and use the refactored supervisor smoke path.

Key v2.6.0 additions:

- Brain Design v2.6.0 adds the Design Agent Runtime: command registry, tool registry, permission modes, hooks, session state, repair tickets, doctor/status, context compaction, and runtime smoke tests.
- Design Craft v0.3.0 is bundled in `.design-brain/adapters/design-craft` as a support-only craft adapter. It can provide craft tokens, typography, spacing, states, accessibility, and handoff notes, but it cannot override Brain Design decisions or depend on the source machine's global skill folder.
- Subagent Orchestration adds 12 accountable design roles for reference visual analysis, Style DNA, brand/reference memory, product architecture, section flow, layout composition, design-system depth, visual signature, Figma source QA, originality, visual QA, and marketplace readiness. Subagents require evidence/receipts and can block final delivery when critical proof is missing.
- Subagent semantic validation upgrades that gate from "file exists" to "receipt content proves the claim," using `scripts/design_brain_subagent_receipt_validate.py` and the `design:subagents:validate` package script.
- The runtime wraps existing gates; it does not replace Design Cognition Contract, Design Simulation Layer, Sequential Layout Originality Gate, Build Session Lifecycle, or Post-Build Completion Gate.
- Brain Design v2.5.0 adds the Sequential Layout Originality Gate and build-session lifecycle ledger.
- Total integration stabilization adds lifecycle `verify-final`, default completion-receipt enforcement for template final audits, design-system artifact evidence status, and a Design Craft non-override contract without changing the package version.
- Every reference-led template build now needs a layout fingerprint and an axis-based reference-vs-AI layout audit before build/final.
- Batch templates advance sequentially: Template B cannot start until Template A is fingerprint locked, Template C must compare against A and B, and so on.
- AI-vs-AI layout audits compare hero grammar, section order, grid system, layout rhythm, component cadence, CTA placement, image treatment, typography behavior, color roles, effects, navigation, footer, and scaffold risk.
- Recoloring or replacing images is not a valid repair when layout or scaffold axes fail; the template must be structurally reconfigured.
- The optional local idea recovery corpus points to `<CODEX_DESIGN_WORKSPACE>\Template Website` for inspiration only and is not bundled in public-core ZIP files.
- Local source cleanup moves forbidden external sources, `.bak-*` snapshots, and old generated evidence outside active workspace. No ZIP export is required for source-only stabilization.

Key v2.4.6 additions:

- Brain Design v2.4.6 fixes Python child invocation policy for runtime checks.
- The resolver now selects an exact invocation: executable plus runtime flags.
- Probe order is plain Python, `-S` no-site mode, then `-I -S` isolated no-site mode; runtime commands use the same mode that passed the probe.
- If plain Python child startup hangs, Brain Design can fall back to `-S` or another executable without requiring `BRAIN_DESIGN_PYTHON`.
- Internal Brain Design subprocess calls use `python_command()` so smoke, package integrity, export, install, cognition, simulation, and post-build checks share the same selected invocation.

Key v2.4.5 additions:

- Brain Design v2.4.5 refactors process utility smoke into deterministic runtime proofs.
- `run_command()` timeout is tested with a simple sleeping process, separate from nested child/grandchild setup.
- Nested child/grandchild cleanup is tested through direct `kill_process_tree()` after explicit ready-file setup, so default smoke no longer races readiness against a short timeout.
- Worker/supervisor repeat tests remain active by default and do not require `BRAIN_DESIGN_PYTHON`.
- Package integrity and export keep runtime checks enabled by default; skipped runtime remains debug-only.

Key v2.4.4 additions:

- Brain Design v2.4.4 finalizes deterministic runtime runner behavior for realtime release checks.
- The Python resolver now runs a child-execution sanity check before accepting `sys.executable`, then falls back to `python3` / `python` when the current interpreter cannot be used as a child process.
- Process utility smoke is split into a single-iteration worker and a repeat supervisor, so a hung worker iteration is killed instead of hanging the whole smoke.
- `run_command()` keeps tempfile capture, polling timeouts, non-isolated default process creation, and recursive process-tree cleanup.
- Process utility smoke reports the resolved Python executable, child sanity results, worker command, kill strategy, and child/grandchild liveness.
- Package integrity and export keep runtime checks enabled by default; skipped runtime remains debug-only.

Key v2.4.3 additions:

- Brain Design v2.4.3 improves runtime runner stability across environments without requiring `BRAIN_DESIGN_PYTHON`.
- The Python resolver uses non-fragile subprocess probing for explicit overrides or fallback names.
- `run_command()` now defaults to non-isolated process creation to avoid session/process-group startup hangs.
- Process-tree cleanup still uses psutil/procfs/taskkill and does not require process group creation for normal runtime checks.
- Process utility smoke verifies repeat runs, nested child/grandchild cleanup, tempfile capture, and non-isolated creation mode.

Key v2.4.2 additions:

- Brain Design v2.4.2 hardens the runtime process runner used by smoke, integrity, export, and ZIP checks.
- Runtime checks capture stdout/stderr through temporary files instead of unbounded subprocess pipes.
- `run_command()` uses a polling timeout loop and recursive process-tree kill, then returns a bounded timeout result without `communicate()`.
- Process utility smoke is repeatable and exercises nested child/grandchild cleanup.
- Package integrity and export keep runtime checks enabled by default; `--skip-runtime` remains debug-only proof.
- v2.4.1 cognition enforcement remains intact: missing/fake cognition receipts still block reference-led/template PASS.
- Public-core export still excludes `.bak-*`, `.backup-*`, `.orig`, `.tmp`, `.old`, and TypeUI-managed files by default.

Key v2.4.1 additions:

- Brain Design v2.4.1 enforces the Design Cognition Contract as a hard gate, not only documentation.
- Design Simulation Layer validates cognition receipts with `design_brain_design_cognition_check.py`.
- Reference-led/template simulations cannot PASS when cognition is missing or invalid; fake `{"status":"PASS"}` receipts fail validation.
- Machine-readable cognition receipts must be JSON. The Markdown receipt is human authoring guidance only unless a Markdown parser is explicitly implemented.
- Post-build audit supports required cognition receipts for template builds.

Key v2.4.0 additions:

- Official Brain Design v2.4.0 Design Cognition Contract.
- Every reference-led template build must define the 10 cognition steps before orchestration/build: Style DNA, Design Intent Lock, Visual Grammar, Reference Boundary, Color Role Re-Mapping, Visual Mood Reinterpretation, Structural Reconfiguration, Pattern Divergence, Section Logic, and Marketplace Readiness.
- Color Role Re-Mapping is mandatory: learn color roles and emotional energy from references, then remap to a new palette identity instead of copying hue/palette identity.
- Reference Boundary forbids exact layout, palette, section order, hero grammar, component scaffold, image placement, and signature visual identity copying.
- Structural Reconfiguration and Pattern Divergence block repainted-reference scaffolds and connect batch outputs to pairwise divergence checks.
- Section Logic blocks generic Hero > Features > CTA defaults for full templates; Marketplace Readiness ties cognition to source depth, editability, preview value, and commercial usefulness.
- Design Simulation Layer and Post-Build Completion Gate now accept cognition receipt context so pre-build and post-build gates can audit against the reasoning contract.

Key v2.3.0 additions:

- Official Brain Design v2.3.0 Post-Build Design System & Triple Audit Gate.
- Every built template must include a template-tied design system before final delivery.
- Every build must run the post-build triple audit: originality/batch similarity, design-system/source hygiene, and visual/layout QA.
- Batch outputs must compare every template pair for scaffold, rhythm, hero grammar, section flow, component cadence, CTA pattern, image treatment, and visual language similarity.
- Failed audits must produce a repair plan, apply repairs, and rerun the affected audit before final response.
- Final responses for design template builds must include a completion receipt with design-system count, audit results, repair cycles, remaining issues, visual verification status, and final status.
- Design Simulation Layer remains the pre-build gate; Post-Build Completion Gate is the post-build gate.

Key v2.2.4 additions:

- Official Brain Design v2.2.4 Design Simulation Layer package.
- Design Simulation Layer defers to the Brain Design module/product-family router and reports `routing.routeSource`.
- PASS verdicts have no `requiredRepairs`; non-blocking suggestions move to `recommendedImprovements`.
- Router-alignment smoke tests cover newsletter website, coffee shop, UI kit, pricing, marketplace-template wording, restaurant/gallery hospitality, social/static, and document/collateral cases.
- Process liveness checks are zombie/defunct-aware so killed child processes are not mistaken for active processes.
- Runtime integrity and export run repeatable process-utils smoke by default.
- Python subprocess checks use `BRAIN_DESIGN_PYTHON` or a bounded resolver before falling back to `sys.executable`, `python3`, or `python`.
- Export and integrity runtime checks use bounded recursive process-tree timeout/fail-fast subprocess execution.
- Simulation smoke now has quick/full modes; quick mode is the release default and route-alignment checks run in-process instead of spawning many full simulations.
- Process utility smoke verifies nested hanging child processes are killed before package integrity or export can pass.
- Marketplace routing guard treats Envato/template/marketplace-ready wording as distribution context, not ecommerce.
- Design Simulation Layer runs as a pre-build gate after template orchestration and before build/revision/finalization.
- Design context graph, source-of-truth agent panel, verdict schema, simulation artifacts, and required repair plan output.
- PASS / REVISE / BLOCKED verdict behavior for high-value template, reference, Figma/source, marketplace, and batch tasks.
- Installer, manifest, package integrity, smoke tests, and export now include and verify simulation-layer files.
- Machine-readable `--json` simulation output is pure JSON on stdout; human messages go to stderr.
- Copy-risk detection distinguishes safe do-not-copy boundaries from risky clone/exact-copy requests.
- Public-core generated manifest and ZIP integrity validate current package contents.

## MiroFish-Style Adaptation Note

This Design Simulation Layer is a Brain Design-native implementation inspired by the MiroFish-style workflow pattern:
seed material -> context graph -> agent panel -> simulation rounds -> verdict/report.

It does not bundle, copy, import, or execute MiroFish source code.
It does not run OASIS or social/public-opinion simulation.
It adapts the architectural idea into a local design review and quality-gate workflow.

Useful checks:

```bash
python scripts/design_brain_router_smoke_test.py
python scripts/design_brain_process_utils_smoke_test.py --worker-once --timeout 8 --setup-timeout 15 --simple-timeout 3 --worker-max-duration 30 --verbose
python scripts/design_brain_process_utils_smoke_test.py --repeat 5 --timeout 8 --max-duration 120
python scripts/design_brain_design_sim_smoke_test.py --quick --global-timeout 90 --case-timeout 20
python scripts/design_brain_post_build_smoke_test.py
python scripts/design_brain_design_cognition_smoke_test.py
python scripts/design_brain_sequential_layout_smoke_test.py
python scripts/design_brain_design_cognition_check.py --receipt "<receipt.json>" --json
python scripts/design_brain_post_build_audit.py --build-dir "<build-dir>" --expected-templates 1 --allow-visual-limitation --json
python scripts/design_brain_reference_corpus_health.py
python scripts/design_brain_package_integrity.py --runtime-timeout 180 --command-timeout 60 --process-smoke-repeat 3
python scripts/design_brain_module_select.py --task "template website restoran" --dry-run
node skills/presentation-deck/tests/design_brain_web_deck_smoke_test.mjs
```

