# Design Simulation Layer

This layer adapts the useful MiroFish-style workflow pattern for marketplace template design work:

```text
seed brief -> design context graph -> agent panel -> verdict -> revision loop
```

This Design Simulation Layer is a Brain Design-native implementation inspired by the MiroFish-style workflow pattern:
seed material -> context graph -> agent panel -> simulation rounds -> verdict/report.

It does not bundle, copy, import, or execute MiroFish source code.
It does not run OASIS or social/public-opinion simulation.
It adapts the architectural idea into a local design review and quality-gate workflow.

## Relationship to Post-Build Completion Gate

Design Simulation Layer is pre-build. It asks: should this plan be built?

Subagent Orchestration runs immediately before Design Simulation for website-template, Figma/source-template, marketplace, reference-led, batch, anti-minimalist, or quality-sensitive work. It decides which accountable subagents are active and which evidence/receipts are required. Its semantic validator checks whether receipt contents are meaningful enough to trust. Design Simulation evaluates the proposed plan after that responsibility map exists; missing or fake subagent evidence must not be treated as a successful final state.

Post-Build Completion Gate is post-build. It asks:

- Was the built template completed correctly?
- Was the design system built?
- Is the source editable and clean?
- Are batch templates distinct?
- Are there visual/source defects?

Both gates are required for high-value template builds. The simulation verdict must not replace the design system, source hygiene, visual/layout QA, batch similarity audit, repair loop, or final completion receipt.

## Design Cognition Receipt Input

For reference-led template builds, Design Simulation Layer should receive the Design Cognition Receipt before verdict generation.

Simulation input should include:

- cognition receipt path
- cognition status
- color remap summary
- reference boundary summary
- structural reconfiguration summary
- pattern divergence summary
- marketplace readiness summary

Agents evaluate whether Style DNA was extracted, Color Role Re-Mapping is complete, reference color identity was avoided, Structural Reconfiguration is real, Section Logic is strong, and Marketplace Readiness is concrete. Missing or failing cognition receipt should produce REVISE or BLOCKED before build.

For reference-led/template tasks, the simulation script must validate the JSON cognition receipt with the Design Cognition checker. It must not trust a raw `status` field, and a fake status-only receipt must fail. If cognition is required and missing or invalid, the simulation verdict cannot be PASS.

`--allow-missing-cognition` is for debug/emergency inspection only. It still produces a non-final, non-PASS result and must not be used as release proof.

It uses a lightweight local gate that fits Codex Design Brain and produces deterministic artifacts that can be reviewed, versioned, and reused in batch work.

## Purpose

Use this layer before building any serious marketplace template, especially Envato, Figma website template, SaaS template, UI kit, dashboard, landing page, brand kit, or batch template pack.

The layer exists to prevent these failure modes:

- AI jumps directly into visuals without a sellable product plan.
- Website templates collapse into thin minimalist section stacks.
- Multiple templates reuse the same hero/feature/pricing/FAQ scaffold.
- A reference is copied as section order, color-role mapping, glow/gradient logic, or component grouping.
- The template looks clean but lacks commercial preview value.
- The source template lacks editability, placeholder logic, auto-layout discipline, documentation, or source hygiene.
- Envato-style presentation, information, technical, and legal readiness are treated as afterthoughts.

## Activation Rule

Run this layer after template orchestration and reference DNA extraction, but before implementation/build.

Workflow position:

```text
Natural Request
-> Intent Router
-> Product / Medium Detection
-> Reference Insight
-> Style DNA Extraction
-> Reinterpretation Visual Mood
-> Structural Reconfiguration
-> Template Orchestration
-> Subagent Orchestration Layer
-> Design Simulation Layer
-> Required Repair Plan
-> Build / Revise / Block
-> Figma Build Rules
-> Visual Review
-> Similarity + Originality Gate
-> Marketplace Quality Gate
-> Learning Loop as Proposed Rule
```

The Design Simulation Layer is a pre-build gate, an agent critique/review layer, and a repair decision layer. It must not replace Brain Design routing, product-family detection, Reference Insight, Template Orchestration, Figma Build Rules, Visual Review, or Marketplace Quality Gate.

## Router Deference Rule

The Design Simulation Layer must not independently re-route tasks when the Brain Design router is available. It must consume the Brain Design route, product-family, and medium decision, then evaluate the proposed plan against that contract.

The simulation route order is:

1. Explicit CLI route arguments such as `--mode`, `--module`, `--product-family`, `--website-type`, or `--output-contract`.
2. Brain Design module router, intent router, and website product-family detector.
3. Conservative fallback routing only when router imports are unavailable or the router returns no usable module.

If fallback routing is used, the verdict and report must mark `routing.routeSource=fallback` and warn: `Simulation route fallback used; verify Brain Design router availability.`

Simulation is a gate, not a router source of truth. If simulation route conflicts with Brain Design router, Brain Design router wins and the simulation must rerun with the correct route.

## Marketplace Routing Guard

The word `marketplace` has two meanings:

1. Template distribution context: `marketplace template`, `Envato marketplace`, `Creative Market`, `UI8 marketplace`, `editable marketplace templates`, `marketplace-ready template`, `marketplace quality gate`, and `marketplace preview`. This is not ecommerce intent.
2. Product/listing context: `ecommerce marketplace`, `product marketplace`, `vendor marketplace`, `multi-vendor marketplace`, `marketplace app/platform/storefront`, `marketplace with cart`, `marketplace checkout`, `booking marketplace`, `property marketplace`, `job marketplace`, and `service marketplace`. This can route to ecommerce/listing.

Design Simulation must consume the Brain Design route after this distinction. A restaurant website template for marketplace buyers with gallery/visual-motif language remains a hospitality website template, not portfolio and not ecommerce.

## Runtime Reliability

Simulation smoke, package integrity, export, ZIP integrity, temp install, and JSON-purity checks must run through bounded subprocesses. Timeout handling must kill the process tree, report the exact command/step, and fail the release instead of hanging silently or claiming success.

The simulation layer has quick and full smoke modes:

- `--quick` is the default release/export mode. It runs route-alignment checks in-process and only a limited set of full simulation subprocesses.
- `--full` is for deeper regression runs. It may run more verdict simulations, but every case still has a per-case timeout and a global deadline.
- `--route-only` checks router alignment without spawning full simulation subprocesses.

Process tree timeout is required because simulation tools may spawn nested Python child processes. Release checks must run `scripts/design_brain_process_utils_smoke_test.py` and fail if an intentionally hanging nested child cannot be killed.

Runtime smoke is repeatable by default. Process utility smoke should run multiple nested timeout iterations and treat POSIX zombie/defunct processes as terminated, not as active child processes. Subprocess checks use a bounded Python executable resolver: `BRAIN_DESIGN_PYTHON` first, then a probed active interpreter such as `sys.executable`, `python3`, or `python`.

Required for:

- Envato or marketplace template products
- Reference-based template work
- Batch template packs
- Figma website templates
- Landing page or website templates where section count, buyer fit, or originality is uncertain
- Any output where the user says: `anti identik`, `jangan minimalist`, `maksimal menarik`, `marketplace-ready`, `standard Envato`, or similar

Recommended for all sellable template products.

## Pipeline Mapping

| MiroFish-style pattern | Brain-Design implementation |
| --- | --- |
| Seed material | user task, template type, niche, buyer, visual mood, reference summary, proposed structure |
| Ontology generation | design context graph with product, buyer, structure, visual, Envato, technical, legal, and originality nodes |
| Graph build | `graph/design_context_graph.json` artifact |
| Persona preparation | agent panel loaded from `.design-brain/design-simulation/agents.json` |
| Simulation round | agent panel evaluates the proposed structure and flags blockers |
| Forecast/report | `report/design_verdict.json`, `report/report.md`, and `report/revision_brief.md` |
| Run artifacts | `.design-brain/context-packets/design-sim/<run-id>/` |
| Verdict loop | PASS, REVISE, or BLOCKED; build is forbidden until PASS |

## CLI Entry Point

```bash
python scripts/design_brain_design_simulate.py \
  --task "Envato Figma SaaS website template" \
  --template-type "Figma website template" \
  --niche "AI compliance SaaS" \
  --target-buyer "SaaS founders and product marketing teams" \
  --visual-mood "premium futuristic trust-heavy" \
  --marketplace "Envato" \
  --proposed-structure "header; hero with product UI preview; problem/risk framing; workflow; feature depth; security proof; integrations; case study metrics; pricing/demo CTA; FAQ; resources; final CTA; footer; responsive spread; design system tokens; components; variants; auto-layout receipt; preview cover; section breakdown; metadata; license/attribution; structure fingerprint" \
  --reference-summary "Reference DNA: dark premium SaaS, high-contrast product UI, trust proof rhythm, dense section map, gradient depth. Do not copy exact layout, colors, hero composition, CTA role, or glow logic. Reinterpret with a new visual motif and structure."
```

The command writes a run folder unless `--dry-run` is used. When `--json` is active, stdout is valid JSON only; human-readable artifact messages go to stderr and artifact paths are included in the JSON payload.

## Required Artifacts

A valid simulation run creates:

```text
.design-brain/context-packets/design-sim/<run-id>/
├─ manifest.json
├─ input/
│  ├─ task.txt
│  ├─ proposed_structure.txt
│  └─ reference_summary.txt
├─ graph/
│  └─ design_context_graph.json
├─ simulation/
│  └─ agent_panel.json
├─ report/
│  ├─ design_verdict.json
│  ├─ report.md
│  └─ revision_brief.md
└─ fingerprints/
   └─ structure_fingerprint.json
```

These files are evidence. Do not claim the simulation passed unless `report/design_verdict.json` says `PASS`.

## Verdict Rules

The simulation returns:

- `PASS` when the average score is at least 82, the minimum agent score is at least 72, and there are no blocking agents.
- `REVISE` when the idea is directionally usable but not ready to build.
- `BLOCKED` when the plan is too thin, too generic, too similar, legally risky, technically weak, or not sellable enough.

Build is forbidden until the verdict is `PASS`.

## Verdict Semantics

`PASS` means:

- no blockers
- no required repairs
- optional non-blocking `recommendedImprovements` only

`REVISE` means required repairs must be applied before build or finalization.

`BLOCKED` means blockers and required repairs must be resolved before build or finalization.

If the verdict is `REVISE` or `BLOCKED`, do not continue by explaining around the failure. Revise the proposed structure, change the visual strategy or product scope, then run the simulation again.

## Agent Panel

The default simulation panel is loaded from `.design-brain/design-simulation/agents.json`. That JSON file is the source of truth for agent IDs, roles, focus areas, evaluation axes, vote rules, and repair behavior.

The default simulation panel includes:

1. Marketplace Buyer Agent
2. Envato Reviewer Agent
3. Senior UI Designer Agent
4. Creative Director Agent
5. Conversion Strategist Agent
6. Anti-Minimalist Auditor
7. Anti-Scaffold Auditor
8. Reference DNA Guardian
9. Visual Language Director
10. Source Template Engineer
11. Originality & Legal Risk Auditor
12. Thumbnail / Preview Sales Agent
13. Existing Brain-Design Lint Gate, when the current plan lint script flags issues

The purpose is not to imitate human opinions randomly. Each agent owns a different failure surface and produces specific revision actions.

## Envato-Aligned Interpretation

For Envato-style template readiness, the simulation must consider four release surfaces:

- Item information and metadata: title, description, tags, attributes, included files, requirements, limitations.
- Presentation: cover, preview images, detail crops, responsive spreads, section breakdowns, live/interactive preview where applicable.
- Technical/source quality: editability, organization, components, variants/states, auto-layout, documentation, layer naming, responsiveness, placeholders.
- Legal/originality: rights, licenses, preview-only disclosures, trademark safety, no one-to-one copying from references.

The layer also checks commercial demand and usability. A template is not accepted as marketplace-ready just because it is clean.

## Anti-Minimalist Gate

For competitive website, landing page, and Figma website templates:

- Use at least 8 meaningful sections/blocks unless the product is explicitly a hero/header kit, micro landing, squeeze page, waitlist page, or another intentionally small product.
- Never use `minimalist`, `clean`, `simple`, `safe`, `basic`, or `restrained` as the reason for a thin product.
- Add buyer proof, objection handling, product depth, visual story, conversion closure, and preview value when the product family needs them.
- A clean design can pass only when it still has structure depth, visual language, editability, and commercial preview strength.

## Anti-Identical / Anti-Scaffold Gate

The simulation generates a `structure_fingerprint.json` and can compare against prior fingerprints:

```bash
python scripts/design_brain_design_simulate.py \
  --task "..." \
  --proposed-structure "..." \
  --prior-fingerprint-file ".design-brain/context-packets/design-sim/previous-run/fingerprints/structure_fingerprint.json"
```

If cross-template structure similarity is too high, the newer template must be rebuilt from a fresh structure fingerprint. Do not fix structural sameness with palette changes only.

For batch template work:

1. Simulate template 1.
2. Lock its accepted fingerprint.
3. Simulate template 2 against template 1's fingerprint.
4. Continue sequentially.
5. If a newer template fails similarity, change structure, hero grammar, section rhythm, preview staging, visual motif, and component cadence before build.

## Reference DNA Guard

When a reference is provided, extract and record:

- buyer effect
- product promise
- section logic
- hierarchy logic
- color-role intent
- effect language
- image/media direction
- component rhythm
- preview selling strategy
- what must not be copied
- how the insight will be transformed

Reference DNA is allowed to guide the design, but exact layout, exact palette, exact CTA role, exact hero composition, exact gradient/glow sequence, and one-to-one section order are not allowed.

## Build Rule

The build order for marketplace templates becomes:

```text
intent route
-> reference/product analysis
-> template orchestration
-> design simulation verdict
-> revise until PASS
-> build/editable source design
-> visual review
-> marketplace quality gate
-> originality score / batch similarity gate
-> final export
```

A design plan that fails simulation should be treated as a failed pre-build gate, not as a minor suggestion.

## Sequential Layout Originality Inputs

For reference-led or batch template plans, simulation should receive:

- reference layout fingerprint
- candidate layout fingerprint
- previous locked AI layout fingerprints
- layout audit status if already run

Agent review must evaluate reference layout copy risk, prior AI template similarity risk, hero/section/grid/CTA divergence, and whether the candidate can proceed to build. Verdicts include `layoutOriginalityStatus`, `referenceLayoutRisk`, `aiPairwiseLayoutRisk`, and `requiredLayoutRepairs`.
