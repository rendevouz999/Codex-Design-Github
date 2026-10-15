# General Design Production Specialist

Plugin scope only. The current default is Main plus one host `gpt-6.1-sol` General Design Production Engineer under `HOST_DESIGN_PRODUCTION_SPECIALIST.md`, with Main's auto-full trust for creative direction and approval. This SDK route is an explicitly selected alternative that replaces the host worker; never run both concurrently. The two-part team preference does not apply to unrelated work outside this custom plugin.

This document describes the optional SDK production route. `PRODUCTION_EXECUTION_POLICY.md` owns route selection and explicit-user precedence. The one-worker topology, SDK schemas, tool allowlist and limits below are local to this route. They do not prohibit Main native/local execution or separately authorized host collaboration. On an SDK capability gap, preserve the brief and check another available route before declaring the whole task blocked.

The Codex Design plugin owns one OpenAI Agents SDK production worker. When selected, Main is the existing external Codex/ChatGPT controller (preferred model `gpt-6-astra`); the SDK route does not create another Main. Its sole SDK Agent uses `gpt-6.1-sol` via the Responses API. There are no handoffs, recursive agents, MCP servers, daemon, scheduler, or unattended background execution inside this SDK path.

## Ownership and automatic entrypoint

`hooks/brain-design-route.mjs` is an advisory UserPromptSubmit hook. It tells Main to construct a bounded assignment after creative planning and authorization. It does not intercept all conversations or start paid work merely because a prompt contains design keywords.

The executable auto-hook is `scripts/design_brain_runtime.py::command_start` → `command_production` → `scripts/design_production/hook.py::DesignProductionAutoHook.dispatch`. A relevant `DesignTask` passed as `--production-request` invokes it automatically. Existing sessions call the same path through `run --command /design-produce`. The existing command router, permission system, tool registry, session state/history, and final readiness checks remain the controller interface.

Main owns the creative plan, authoritative brief, reference interpretation, units, feature requirements, tool grant, authorization, and approval. Legacy design-subagent roles are review responsibilities/checklists inside this SDK workflow, not evidence of separate agent executions. Host collaboration is a distinct route governed by `PRODUCTION_EXECUTION_POLICY.md` and actual host instructions. Applicable design cognition, simulation, originality, and completion checks still apply. Some legacy runtime stage commands record placeholder receipts: their PASS alone is not evidence of an actual design review.

SDK `Agent.as_tool()` applies when both Main and worker live in an SDK runtime. Here Main is external, so the existing CLI/request boundary is the correct callable integration; only one SDK `Agent` is constructed.

## Local setup and operation

For ordinary host subagents, use `HOST_DESIGN_PRODUCTION_SPECIALIST.md`. The SDK-only restrictions below do not govern that separate route. Both routes preserve the medium contract; new native PPTX uses `skills/presentation-deck/workflows/PPTX_SIZE_POLICY.md`, while other formats keep their own dimensions.

Implementation installed `openai-agents==0.23.1` in `.venv-design-production` using the bundled Python 3.12 interpreter. The exact installed dependency versions are in `scripts/design_production/requirements.lock.txt`; direct requirement is `requirements.txt`. No global packages were installed. This runtime selects its local interpreter when launched from another working Python.

On another checkout, create a local Python 3.12+ venv at `.venv-design-production` and install that lock file into it. Reuse the internal presentation capability's `.venv-presentation` and root Node/Playwright installation for PPTX and previews. Dependencies are not silently installed by the worker. Native PowerPoint rendering requires accessible PowerPoint on Windows; the existing renderer also supports LibreOffice on other supported setups. Missing renderer/dependencies yield UNVERIFIED, never a native-editability claim.

Run the complete offline acceptance from the plugin root:

```powershell
& '.\.venv-design-production\Scripts\python.exe' -B scripts/design_brain_production_smoke_test.py
```

This emits real artifacts and preserves an `entrypoint-evidence.json` beneath `output/design-production-acceptance/<run>/`. Its deterministic model goes through the actual Agents SDK `Agent` and `Runner`, function schemas, authorized adapters, browser/native renders, technical QA, and Main review boundary. It never constructs an OpenAI client. The fixtures are technical integration samples, not market-ready designs.

For a scoped production assignment supplied by Main:

```powershell
& '.\.venv-design-production\Scripts\python.exe' -B scripts/design_brain_runtime.py start --task 'Create assigned editable design units' --permission-mode full_build --production-request 'output/my-job/request.json' --dry-run --json
```

Remove `--dry-run` only when the user has authorized paid execution and `approval_policy.allow_paid_model` is true. Live mode uses an existing `OPENAI_API_KEY` supplied by the host process, fixed official Responses endpoint, no automatic retries, tracing disabled, and no response storage. It does not read Codex/ChatGPT login stores, credential files, or `.env`. Codex subscription authentication is not automatically an SDK API credential. API credential/account/model access and live model behavior were not exercised during implementation.

## Assignment contract

Canonical typed definitions live in `scripts/design_production/contracts.py`; unknown fields are rejected. `DesignTask` includes:

- `parent_request_id`, `stage`, `operation`, `artifact_type`, `output_format`, and `revision`.
- `units`: IDs, kind (slide/artboard/graphic/page/spread/composition/glyph), per-job width/height, and Main instructions. No PowerPoint dimensions are imposed on other profiles.
- `inputs`: allowlisted IDs, local paths, SHA256 hashes, and `brief`, `reference`, or `editable_source` roles. One authoritative brief is mandatory. Stage explicitly authorized inputs beneath this project's `output/`, `exports/`, or `reports/`; the worker cannot browse those directories.
- `creative_constraints`, `editability_requirements`, and machine-checkable `required_features`. Features are gated per profile and operation. Presentation adds `slide_masters`, `native_placeholders`, `theme`, `native_charts`, `native_tables`, `reusable_template`, and `existing_pptx_text_edit`; editorial adds `linked_text_flow` and `editorial_grid`; web adds `navigation`, `reduced_motion`, and `print`. Other native requirements, including Smart Objects and font creation, fail explicitly. Main must translate application-specific brief requirements into this field rather than omit them.
- `allowed_tools`, `output_dir` beneath project `output/`, `authorized`, `no_execution`, timeout and call budget.
- `approval_policy`: approver `main`, required rendering, native-editability requirement, default maximum two revisions (controller configurable 0–5), explicit paid-model permission (default false).

`create`, `edit`, `refine`, `assets`, `render`, `qa`, and `repair` are production operations. `brainstorm`, `prompt`, `other`, `no_execution=true`, and unauthorized requests skip the worker. Full-build permission is required in addition to scope authorization. Edit/refine/repair/render/QA use declared editable `UnitContent` JSON sources; presentation preserve mode additionally accepts exactly one authorized passive PPTX. Render/QA cannot grant `write_unit`. Existing PPTX edits target assigned slide numbers and exact plain text in slide-local shape IDs through the internal preserving importer/exporter. Rich text, inherited-object edits and proxy edits fail specifically. Arbitrary PSD/HTML imports remain unavailable.

`UnitContent` contains an assigned unit ID and editable text/rectangle/ellipse/line nodes, typed chart/table payloads, editorial story/frame links, or bounded native `TextEdit` records. IDs, dimensions, colors, fonts, geometry, counts, and text sizes are validated. No raw markup, scripts, URLs, external fonts/resources or arbitrary executable content are accepted. The trusted native picture-slot compiler owns one fixed transparent PNG carrier; it is not a user asset or a flattened slide. Primitive source editing creates new output copies; source files and approved artifacts remain unchanged. Raster reference files are hash-checked, but Main must supply their visual interpretation in the brief/constraints; this version does not transmit reference pixels to the SDK model.

## Specialist tool policy — complete allowlist

| Tool | Actual permission and implementation |
| --- | --- |
| `read_input` | Read only a declared input ID with a matching hash. Text <=100 KB; ordinary input files <=2 MB. PPTX <=20 MB compressed, <=100 MB expanded, <=4000 entries; passive chart XLSX and SVG payloads receive nested validation. Raster inputs return bounded metadata, not a fabricated visual inspection. |
| `discover_capabilities` | Return the fixed adapter matrix; no broad computer/app control. |
| `write_unit` | Validate scoped editable content and medium-specific payloads; no path argument. No writes after a build or in render/QA stages. |
| `build_artifact` | Write assigned sources to a new job directory; use internal native structured/flat export, template validation/apply/preview, source-preserving round-trip, browser-measured editorial reflow, or trusted HTML runtime compilation as selected by the typed contract. No output overwrite. |
| `render_preview` | Offline Playwright SVG previews with network blocked; PPTX uses the existing native PowerPoint renderer. HTML runs the internal static audit and browser render review with restrictive CSP, fixed trusted runtime, navigation, stage, reduced-motion and print checks. No model-generated script execution. |
| `technical_qa` | Read back hashes, dimensions, layer IDs/order, text bounds and preview pixels. Native QA checks master/layout relationships, placeholder type/index, theme/master settings, chart data/workbook and table cells; preserving edits compare unselected package parts and unassigned shapes. Editorial QA verifies contiguous story offsets and overset; web QA consumes actual internal audit/render receipts. No self-approval. |

Only the assignment's subset is exposed as SDK `FunctionTool`s. Every tool uses a typed schema and execution limits. Maximum 20 units, 300 primitives/unit, 4096×4096 canvas/unit, 80 tool invocations, 300 seconds/job; defaults are smaller. Functions are serialized even if a model emits concurrent calls. Native commands are fixed by trusted adapter code, run without a shell, receive a reduced environment without API credentials or arbitrary Python/Node injection settings, and have bounded output/time. Cancellation/timeout kills the owned process tree via the existing process utility. Junctions, symlinks, hidden paths, alternate streams, credential-named files, and paths outside the staged boundary are rejected.

Everything outside that allowlist is forbidden, including agent creation/delegation, model changes, shell, unrestricted files, secrets, permission/policy edits, source brief changes, dependency installation, system settings, commit/push/deploy/publish/upload, external stock search/download, unrelated app/process control, deletion, and approval. Main may perform separately authorized actions through existing host tools. They are not implicitly granted to the Specialist. The trust boundary is the model-facing tool API; a malicious local user who can modify plugin source or controller state is outside this boundary.

## Capability matrix for this Specialist

| Category | Status | Callable output / limitation |
| --- | --- | --- |
| PowerPoint presentations | SUPPORTED (bounded) | Native `.pptx`, structured master/layout/placeholder/theme, reusable template apply/check/preview, native chart/table, and selected-slide plain-text round-trip. Arbitrary rich object edits remain unsupported; no universal lossless claim. |
| Instagram/social/ads/carousels | SUPPORTED | Editable `.svg` artboards and PNG previews within the enabled primitive feature set; each job defines dimensions. |
| Vector graphics | SUPPORTED | Native editable `.svg` with text/shapes and PNG previews; no Illustrator-specific AI/EPS claims. |
| Editorial pages/spreads | SUPPORTED (SVG) | SVG plus per-unit JSON and `publication.json`: linked stories, typography styles, margin/columns/gutter, bleed/trim metadata, measured reflow and overset QA. No INDD packaging. |
| Web/HTML decks | SUPPORTED (bounded) | Typed JSON create/edit compiles editable HTML using internal stage/runtime; static and real browser audits. Existing arbitrary HTML import is not enabled. |
| Google Slides | UNSUPPORTED | No authenticated local runtime adapter. |
| Photoshop PSD/Smart Objects | UNSUPPORTED | No callable application adapter. |
| Illustrator AI/EPS | UNSUPPORTED | Illustrator was not found in checked installation/COM inventory; native AI/EPS adapter absent. SVG remains a separate capability. |
| After Effects AEP/MOGRT/JSX | UNSUPPORTED | No callable application adapter. |
| InDesign INDD/IDML | UNSUPPORTED | InDesign CC 2019 is registered and its executable exists locally; InDesign 2025 directory also exists. No callable Specialist INDD/IDML adapter was introduced; installation is not proof of native execution. |
| Figma | UNSUPPORTED | Host connector presence does not expose authenticated operations to this SDK runtime. |
| Canva | UNSUPPORTED | Same host/runtime boundary; no bridged native operations. |
| Typeface OTF/TTF | UNSUPPORTED | Typography is supported on enabled artifacts; font authoring is unavailable. |

`production-capabilities --json` exposes the same profiles. Future categories extend the profile registry and narrowly validated adapter functions, plus focused tests; they do not create another agent. SUPPORTED refers to this stated feature set, not every feature of the named design product category.

## State, review, cancellation, and recovery

State is inside the existing `.design-brain/runtime/state/design-production/` tree. Task IDs deterministically hash parent, stage, category, ordered unit IDs, and revision. A full scope hash rejects changed assignments reusing an ID. A global OS lock permits only one active worker across processes. Completed duplicate requests return stored evidence without invoking the worker. Different execution modes cannot reuse an ID.

New revisions use separate output directories. Main must first submit REVISE with bounded feedback; the next revision receives that feedback automatically. Revision scope and original revision limit cannot be enlarged. Approved results and reviews are immutable. There is no automatic revision loop.

```powershell
# Main-owned review JSON: task_id, decision APPROVE/REVISE/BLOCK, reviewer main,
# artifact_hashes (all deliverable SHA256s for APPROVE), and feedback.
& '.\.venv-design-production\Scripts\python.exe' -B scripts/design_brain_runtime.py review-production --session '<session>' --review 'output/my-job/review.json' --json
& '.\.venv-design-production\Scripts\python.exe' -B scripts/design_brain_runtime.py run --session '<session>' --command /design-produce --production-request 'output/my-job/revision-1.json' --dry-run --json
& '.\.venv-design-production\Scripts\python.exe' -B scripts/design_brain_runtime.py cancel-production --session '<session>' --task-id '<task-id>' --json
& '.\.venv-design-production\Scripts\python.exe' -B scripts/design_brain_runtime.py recover-production --session '<session>' --task-id '<task-id>' --json
```

The Specialist can return only NEEDS_MAIN_REVIEW, FAILED, BLOCKED, or UNVERIFIED. Controller QA overrides unsupported success claims and replaces model manifests with actual adapter evidence. QA does not approve visual design. Main must inspect previews and creative requirements; APPROVE binds exact deliverable hashes and requires PASS technical evidence. Finalization rechecks hashes and requires Main approval of each latest stage revision **and** all pre-existing completion gates.

Cancellation records a cooperative cancel request checked while the SDK runs and native subprocesses execute. Deadline/process failures return UNVERIFIED and preserve partial artifacts. A hard interruption leaves RUNNING until reconciliation; a subsequent duplicate marks UNKNOWN and never replays. Recovery obtains the global lock to establish that no worker is active, preserves partial outputs, marks BLOCKED, and requires Main review/revision. No blind cleanup or replay occurs.

## Verification sources

SDK definitions and tools were checked against official [Agents documentation](https://openai.github.io/openai-agents-python/agents/), [function tools](https://openai.github.io/openai-agents-python/tools/), [Runner behavior](https://openai.github.io/openai-agents-python/running_agents/), and installed 0.23.1 signatures. Model features were checked against [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol). Implementation uses `Agent`, `Runner.run`, `FunctionTool`, structured `output_type`, fixed `OpenAIResponsesModel`, bounded turns, and disabled tracing.

Within Codex-Design, `.design-brain/LOCAL_MEMORY_POLICY.md` selects Supabase shared memory with local outbox/cache fallback and no Agent Core dependency. The SDK tool allowlist is unchanged: Main supplies a bounded packet of verified local records when the SDK worker cannot read them directly. Runtime receipts remain artifact evidence; Main records reviewed results through the shared adapter and reads back the actual sync state. See `reports/design-production-specialist-implementation.md` for actual validation results and memory-service availability.

## Expanded medium contracts (12 October 2026)

`presentation` declares `structure` (flat, structured, preserve), title/body font and pixel size, background/foreground/accent roles, and `reusable_template`. Structured units declare `layout`; nodes declare optional `layer`, native placeholder role/index and typed chart/table data. Title/body placeholders use contract typography and backend theme-font inheritance. Reusable template mode authors an isolated Layout workspace, validates and applies it with `apply_templates(validate=True)`, generates an internal template preview, and compiles the assigned deck. Template workspace canvas presets are those supported by the internal backend; unsupported presets fail without flattening.

Preserve mode declares `source_slide` per assigned unit. `read_input` returns selected shape IDs and plain text. `write_unit.edits` supplies shape ID, exact expected text and replacement; only single plain text carriers are currently editable. Source notes/media/proxies and non-target data stay native. The importer, capacity checker, preserving exporter, delivery checker and native renderer all run in owned bounded processes. Unavailable rendering is UNVERIFIED.

Editorial units may contain `text_frame` nodes linked by `story_id`. Exactly one unit owns each story's text and style; frames follow source unit/node reading order. `editorial` defines styles and grid. Unit dimensions are the media box; bleed is an inset to the trim box, and margin is measured inward from trim. `publication.json` and SVG `data-trim-box` retain those boxes. Chromium Canvas2D measures installed fonts and wraps horizontal plain text; receipts store contiguous Unicode character offsets, source text, frame IDs and line assignments. Missing fonts and overset fail QA. This does not claim advanced InDesign typography, glyph coverage for every script, hyphenation or print color management.

HTML is regenerated from editable unit JSON. No arbitrary HTML or JavaScript reaches the SDK tool surface. The internal CSS/runtime is included verbatim, data is escaped, and CSP denies external assets/network while allowing exactly the trusted runtime script hash. The web medium requires its internal 1920×1080 stage; this size rule does not apply to editorial/vector/social jobs.

Export synchronized contracts with `python -m design_production.export_contracts` while `scripts` is on `PYTHONPATH`. Run expanded offline acceptance with `.venv-design-production/Scripts/python.exe -B scripts/design_brain_production_capability_test.py`. SDK APIs and pinned 0.23.1 dependency are unchanged. See the dated capability-completion report for exact evidence and remaining boundaries.
