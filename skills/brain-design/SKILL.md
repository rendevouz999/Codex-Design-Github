---
name: brain-design
description: >-
  Route Brain Design template products, reference-led builds, editable sources, marketplace previews, design systems, naming, critique, and batch workflows through the repository quality gates. Handles Indonesian requests such as buat template, buat desain, jangan copy layout, terlalu mirip, and buat lebih premium. Main selects capable native/local tools, authorized host collaboration or the SDK Specialist and keeps creative control and approval. Explicit user instructions outrank local workflow defaults. Presentations, including browser decks, use presentation-deck guidance. Not for unrelated backend work or ordinary UI edits without Brain Design artifacts or gates.
---


For plugin tasks, load [shared memory and fallback](../../.design-brain/LOCAL_MEMORY_POLICY.md). Main and Engineer retrieve through the Supabase/local adapter before planning; Main saves positive and negative decisions with guarded revisions and readback. The service need not be online. Preserve local-only history after recovery and reconcile unknown writes before retry.

# Brain Design Router

For visual inspection during plugin work, load `.design-brain/VISUAL_INSPECTION_PROTOCOL.md`. Main and the single Engineer use current-source overview, targeted full-resolution crops, and a return to whole-frame context. Record actual observations and unresolved checks; generated images, metadata, screenshot presence and another agent's verdict alone cannot establish visual PASS.

Activate these rules only for actual work using or maintaining this custom plugin. Within that scope use Main + exactly one explicitly selected `gpt-6.1-sol` (Codex host) / `claude-opus-5-5` (Claude Code host) **General Design Production Engineer**, never a multi-worker panel. Main has auto-full trust for creative direction, delegation and evidence-based PASS/REVISE; ask only material ambiguity and the standing unspecified non-PPTX size decision. Reuse the same Engineer for repairs. SDK is an explicit replacement route. Unrelated tasks do not inherit this plugin's strict team/model/approval/size rules.

Authorized host subagents use `<PLUGIN_ROOT>/.design-brain/runtime/HOST_DESIGN_PRODUCTION_SPECIALIST.md`. New native `.pptx` uses `<PLUGIN_ROOT>/skills/presentation-deck/workflows/PPTX_SIZE_POLICY.md` (10 × 5.625 inches landscape); other media never inherit this size. Preserve source size for existing-PPTX edits and honor current explicit overrides.

For creating, editing, rendering, or technically checking an authorized design, Main defines scope and reads `<PLUGIN_ROOT>/.design-brain/runtime/PRODUCTION_EXECUTION_POLICY.md`. Choose native/local tools, authorized host collaboration, or the SDK Specialist based on actual capability; an SDK gap is not a global task blocker. Use `scripts/design_brain_runtime.py plan-production --production-request <path> --json` to inspect SDK compatibility without execution. Only when selecting SDK execution, read `DESIGN_PRODUCTION_SPECIALIST.md` and submit a bounded `DesignTask` through `start --production-request` or `/design-produce`. Main owns approval. Respect no-execution/unauthorized scope, preserve output fidelity and report real evidence. Never infer paid API authorization from a request to modify plugin rules.

Use this skill as the entry point for design work in this plugin's root. It carries no design taste of its
own. Its job is to load the repository source-of-truth layer, pick the correct medium workflow, run the
gates that decide when design work is finished, and leave a receipt behind.

`${CLAUDE_PLUGIN_ROOT}` resolves to the repository root, so plugin assets such as
`${CLAUDE_PLUGIN_ROOT}/skills/presentation-deck/workflows/web.md` and the Brain Design knowledge files under
`.design-brain/` sit in the same tree. In hosts without that variable, derive the root from this
skill's absolute path (`../..`); never assume the user's current directory is the plugin root.

## 1. Load The Source Of Truth

Read these before planning, in this order:

1. `<PLUGIN_ROOT>/AGENTS.md`
2. `.design-brain/AUTOLOAD_POLICY.md`
3. `.design-brain/CONTEXT_PRIORITY.md`
4. `.design-brain/SOURCE_OF_TRUTH_MAP.md`

`AUTOLOAD_POLICY.md` names the extra files each task cue requires. `CONTEXT_PRIORITY.md` decides what to
drop when context is tight. When documentation and routing files disagree, `SOURCE_OF_TRUTH_MAP.md` wins
and the stale file should be reported, not quietly followed.

## 2. Route The Intent

Infer the workflow from the user's natural sentence. Do not ask the user to name an internal command.

- `.design-brain/NATURAL_INTENT_ROUTER.md` for the intent families.
- `.design-brain/ROUTING_ALIASES_ID.json` for Indonesian and mixed-language aliases.
- `.design-brain/DESIGN_AUTOPILOT.md` for the quality behavior that must activate without being asked.
- `.design-brain/registry/modules.json` for the module, seed pack, direction pack, and validators.

Module selection has a tool:

```bash
python scripts/design_brain_module_select.py --task "..." --template-type "..." --niche "..." --target-buyer "..." --visual-mood "..." --dry-run
```

The repository tool scripts named `*.py` need a working Python interpreter. If `python` resolves to a
stub or the local virtual environment is broken, treat that tool as unavailable, follow the matching
registry and policy file manually, and state in the final response which tool could not be executed.
The `*.mjs` tools run on the repository `node` install and have no such dependency.

## 3. Hand Off By Medium

- Browser-rendered deck, animated slides without an explicit PowerPoint output, single-file browser presentation, deck-to-web conversion: stop here and
  use `${CLAUDE_PLUGIN_ROOT}/skills/presentation-deck/workflows/web.md`.
- Native PPTX generation, source-preserving edit, or reusable presentation workspace:
  `skills/presentation-deck/SKILL.md` and `skills/presentation-deck/workflows/native.md`.
  PowerPoint animation stays native when PPTX is the output. Explicit PPTX and HTML outputs
  require separate artifacts and receipts; PPTX-to-HTML remains the web-deck source bridge.
- Keynote, Google Slides, or a Figma slide template:
  `skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md` plus the Non-Web Mode Rule in
  `.design-brain/adapters/design-craft/SKILL.md`.
- Website or marketplace template: `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md`,
  `.design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.md`, `.design-brain/APPROVED_TEMPLATE_CORPUS.md`.
- Figma or editable source output: `.design-brain/FIGMA_OUTPUT_TARGET.md`,
  `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md`, `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`.
- Other mediums: `.design-brain/MEDIUM_PRODUCT_PLAYBOOKS.md`.

## 4. Think Before Building

- `.design-brain/DESIGN_COGNITION_CONTRACT.md` and `.design-brain/DESIGNER_COGNITION_LAYER.md` for buyer
  decision model, attention strategy, density strategy, and component reasoning.
- `.design-brain/DESIGN_SIMULATION_LAYER.md` to simulate the result before committing to it.
- `.design-brain/BUILD_SESSION_LIFECYCLE.md` to open the session for any built artifact.
- `.design-brain/HUMAN_CRAFT_HEURISTICS.md` and `.design-brain/craft/` for the craft axes the module
  requires.

Design Craft, TypeUI-derived style files, and design-system skills are support layers. They sharpen
critique and polish but never override Brain Design routing, cognition, simulation, lifecycle,
design-system, or completion gates. The boundary is
`.design-brain/DESIGN_CRAFT_NON_OVERRIDE_CONTRACT.md`.

## 5. Gates That Block Completion

Design work is not finished until the gates that apply to the medium have passed:

- `.design-brain/SEQUENTIAL_LAYOUT_ORIGINALITY_GATE.md` for reference-led or batch output.
- `.design-brain/BATCH_TEMPLATE_HARD_GATES.md` and
  `.design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md` for multiple outputs, one full cycle each.
- `.design-brain/DESIGN_SYSTEM_BUILD_REQUIREMENTS.md` for any built template.
- `.design-brain/POST_BUILD_COMPLETION_GATE.md` and `.design-brain/POST_BUILD_TRIPLE_AUDIT_GATE.md`
  before presenting an artifact as final.
- `.design-brain/MARKETPLACE_QUALITY_GATE.md` and `.design-brain/ORIGINALITY_GUARD.md` for sellable
  output and for names.
- `.design-brain/VISUAL_CRITIQUE_CHECKLIST.md` for the self-critique pass. One implementation pass is
  never enough; critique, name the concrete cause of each weakness, then revise.

Never present a design template as final without a design-system receipt, triple-audit receipt,
repair-loop status, and completion receipt.

## 6. Leave A Receipt

Fill the matching template in `.design-brain/templates/`, including
`DESIGN_SYSTEM_RECEIPT.md`, `POST_BUILD_AUDIT_RECEIPT.md`, `LAYOUT_FINGERPRINT.md`, and
`TEMPLATE_NAME_CHECK.md` when naming was part of the task. Capture useful user feedback as a lesson in
`.design-brain/REFLECTION_LOG.md` with `scripts/design_brain_reflect.py`. Do not promote a lesson into
`.design-brain/DESIGN_MEMORY.md` without explicit owner instruction.

## 7. Owner Guard

Protected modification of Brain Design itself requires the owner password gate in
`.design-brain/OWNER_GUARD.md`. Protected scope covers `.design-brain/` rules, memory, workflows, gates
and templates, `scripts/design_brain_*`, the Design Brain sections of `AGENTS.md`, and this plugin's own
skills and hooks. Before such a change, ask the owner exactly `kata sandinya apa?`, give no hints or
alternatives, and stop if the answer does not verify against the stored verifier.

Normal design work does not need the gate. Building templates, reviewing designs, reading files,
generating reports, and writing ad-hoc memory notes proceed without it.
