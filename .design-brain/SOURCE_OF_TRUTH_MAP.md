# Source Of Truth Map

For visual inspection during plugin work, load `.design-brain/VISUAL_INSPECTION_PROTOCOL.md`. Main and the single Engineer use current-source overview, targeted full-resolution crops, and a return to whole-frame context. Record actual observations and unresolved checks; generated images, metadata, screenshot presence and another agent's verdict alone cannot establish visual PASS.

For actual Codex-Design work, load `.design-brain/LOCAL_MEMORY_POLICY.md`. Use the bundled shared memory capability: Supabase first, the local outbox/cache as fallback, and existing plugin-local records alongside both. Include pending/local-only history after recovery. Main and the single Engineer read/search before planning; Main writes and revises with readback. Preserve positive and negative evidence. A service outage does not block local access; conflicts and unknown writes require reconciliation, never blind replay. This owner-approved rule is plugin-scoped.

For plugin PPTX design, load `skills/presentation-deck/workflows/PPTX_LAYOUT_ORIGINALITY_POLICY.md`: extract actual slide geometry and compare with verified earlier PPTX cases across sessions through verified plugin-local memory evidence pointers. Identical composition rejects even after text/color/photo/shape-form/size/count changes. Reused images are allowed only when current tone, content and purpose all pass Main review. No automatic originality PASS from metadata or an empty history.

For plugin-native PPTX creation or substantial deck redesign, load `skills/presentation-deck/workflows/PPTX_FIRST_THREE_SLIDES_REVIEW.md`. Main must inspect rendered slides 1–3 and record PASS before the single Engineer authors slide 4 onward. Reuse the same Engineer for revisions; this is internal Main approval under auto-full trust.

Only during this plugin's use or maintenance, required host worker effort is **Extra High (`xhigh`)**, explicitly passed as `reasoning_effort="xhigh"` together with `model="gpt-6.1-sol"` on the Codex host, or as `effort: xhigh` with `model: claude-opus-5-5` on the Claude Code host. Do not inherit Main effort or silently downgrade; if unavailable, report the specific host limit. An already-running worker must finish or be stopped before a replacement with the required effort starts. Historical completed workers are not concurrent team members.

For plugin-native PPTX photo sourcing, load `skills/presentation-deck/workflows/PPTX_IMAGE_SELECTION_POLICY.md`. The single Engineer searches web/Unsplash/Pexels with available internal tools; Main visually reviews contextual candidates. Two rejected Engineer rounds per stable slot require Main search takeover and a slide-number/placement/crop handoff. Main verifies the rendered result. Prefer hidden in-app or isolated browsing; Firecrawl is an available conditional helper, never a reason to use the user's active browser. This is a standing sourced-photo exception to the generic placeholder default for useful PPTX photo slots, not permission for AI generation or other-platform size changes.

These plugin rules activate only for work using or maintaining `<CODEX_DESIGN_WORKSPACE>`, not unrelated tasks. Within that scope, the owner selects Main plus ONE explicit `gpt-6.1-sol` (Codex host) / `claude-opus-5-5` (Claude Code host) **General Design Production Engineer**. Main has auto-full trust for creative direction, delegation and evidence-based PASS/REVISE. Host capacity does not authorize extra workers; SDK is an explicit replacement route. Main's requested GPT-6 Astra (Codex) / Claude Fable 5.1 (Claude Code) identity must not be represented as verified actual host selection from a policy file alone.

For non-PPTX platform templates, resolve missing platform/size with the user before layout. Existing explicit requirements need no repeated question. Only native PPTX has an automatic standing size; former PPTX presets are removed from active selection.

`skills/presentation-deck/workflows/PPTX_SIZE_POLICY.md` owns physical-size defaults exclusively for new native `.pptx`: 10 × 5.625 inches landscape; explicit user overrides and source-preserving edits remain authoritative. Other formats retain their own size rules. `runtime/HOST_DESIGN_PRODUCTION_SPECIALIST.md` owns the ordinary host subagent role prompt and bounded assignment contract, separate from the optional SDK worker.

`runtime/PRODUCTION_EXECUTION_POLICY.md` owns production-route choice and explicit-user precedence over local plugin defaults. Main may use native/local tools, authorized host collaboration, or the SDK Specialist. For the SDK route only, `runtime/DESIGN_PRODUCTION_SPECIALIST.md` and `scripts/design_production/` own its one-worker topology, adapter availability, scoped tools and approval. The executable SDK hook belongs to `scripts/design_brain_runtime.py`; advisory prompt hooks do not authorize execution. Legacy role lists are responsibilities unless actual host-agent execution was authorized and performed. Creative and completion requirements follow the user's scope; missing evidence never becomes PASS.

Design Brain v2.8.0 uses this hierarchy whenever rules overlap.

## Rule Hierarchy

1. User explicit instruction
   - Within this plugin, explicit scope overrides workflow defaults and local approval rituals. See `runtime/PRODUCTION_EXECUTION_POLICY.md`. Host/system constraints and factual capability limits remain outside this plugin's authority.
2. `.design-brain/OWNER_GUARD.md`
3. `.design-brain/CONTEXT_PRIORITY.md`
4. `.design-brain/AUTOLOAD_POLICY.md`
5. Intent router / workflow trigger
6. Product family / medium playbooks
7. Web Deck Intelligence for browser-rendered deck medium work
8. Website Reference Prompt Lock for reference-led website/Figma website-template work
9. Brand & Reference Usage Memory Layer
10. Reference Insight / Style DNA
11. Design Cognition Contract
12. Section Layout Extraction Library / Matching Gate / Hyper-Accuracy Gate
13. Template Orchestration
14. Subagent Orchestration Layer
15. Design Simulation Layer
16. Build Session Lifecycle
17. Sequential Layout Originality Gate
18. Serial Provenance Gate
19. Build execution
20. Design System Build Requirements
21. Web Deck Stage Gate for web-deck stage and runtime fidelity
22. Post-Build Triple Audit Gate
23. Repair Loop
24. Visual Review / Similarity Gate
25. Marketplace Quality Gate
26. Completion Receipt
27. Learning Loop / Proposed Rules
28. Design Craft / TypeUI / craft modules as non-override support only
29. `README.md` and `.design-brain/QUICK_START.md` as documentation only, not primary rule source

The Design Simulation Layer is a pre-build gate. The Post-Build Completion Gate is a post-build gate. Post-Build Completion Gate can block final delivery until the design system and audits are complete.

The Build Session Lifecycle, Sequential Layout Originality Gate, and Serial Provenance Gate sit after Design Simulation and before build execution. They can block build/final delivery when reference-vs-AI layout audit, AI-vs-AI pairwise layout audit, fingerprint lock, scaffold disposal, one-template-at-a-time provenance, or single-template build scope is missing or failed.

Design Cognition Contract sits after Reference Insight and before Template Orchestration. If Subagent Orchestration, Design Simulation, or Post-Build Audit contradicts the Design Cognition Receipt, create a repair or rerun cognition; do not silently ignore it.

`.design-brain/SECTION_LAYOUT_EXTRACTION_LIBRARY.md`, `.design-brain/SECTION_LAYOUT_MATCHING_GATE.md`, and `.design-brain/SECTION_LAYOUT_HYPER_ACCURACY_GATE.md` sit after Reference Insight / Design Cognition and before Template Orchestration. They own section-level layout catalog extraction, dedupe/matching, stable pattern selection, density-limit vocabulary, hyper-accuracy promotion, and `sectionPatternMix` fingerprint evidence. They cannot override the Website Reference Prompt Lock, no-copy boundary, product-family completeness, or Design Cognition; they make section-level layout variation more accurate before orchestration and simulation.

`.design-brain/SUBAGENT_ORCHESTRATION_LAYER.md` sits after Template Orchestration and before Design Simulation. It decides which subagents are active, what evidence/receipts are mandatory, and whether missing critical evidence should block final delivery. `.design-brain/SUBAGENT_RECEIPT_SEMANTIC_VALIDATOR.md` governs whether those receipts are meaningful enough to trust. Together they do not replace Design Cognition, Design Simulation, Layout Originality, Post-Build Completion, Visual Review, or Marketplace Quality Gate; they make evidence responsibilities explicit and block fake or shallow proof.

`.design-brain/WEBSITE_REFERENCE_PROMPT_LOCK.md` sits between product-family routing and reference insight for reference-led website-template tasks. It owns the user's permanent website-reference prompt behavior: Style DNA only, no visual copying, minimum 9 meaningful sections by default, placeholder image zones, structural reconfiguration, responsive behavior, and mini design-system requirements.

`skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md` and `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md` sit after product-family routing for browser-rendered deck work. The intelligence module owns `web-deck` medium judgment: when a deck belongs in a browser instead of a static slide file, the fixed 1920x1080 stage, slide archetype selection, density mode, and the static-source bridge in `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md` that turns an existing slide file into a web deck. The stage gate owns stage and runtime fidelity, the motion grammar in `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`, and the delivery contract in `skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md`: uniform stage scaling, slide switching, runtime navigation, reveal order, reduced-motion behavior, print output, and single-file delivery, enforced by `skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs` and `skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs`. They cannot override the Design Cognition Contract, Design Simulation Layer, Sequential Layout Originality Gate, Build Session Lifecycle, Design System Build Requirements, Post-Build Completion Gate, Website Reference Prompt Lock, or the no-copy boundary, and they cannot relax the static presentation rules that own PPTX, Keynote, and other export-only slide artifacts.

`.design-brain/FIGMA_API_COMPATIBILITY.md` sits with build execution for Figma/source-template work. It owns Figma Plugin API enum normalization, especially auto-layout alignment values: use `MAX` for end alignment, never `END`, and block generated Figma code that assigns `primaryAxisAlignItems` or `counterAxisAlignItems` to CSS/Flexbox terms.

`.design-brain/TEMPLATE_REFERENCE_USAGE_POLICY.md` and `.design-brain/TEMPLATE_REFERENCE_USAGE_REGISTRY.json` sit after Website Reference Prompt Lock and before Reference Insight / Style DNA. They own generated template brand memory, reference brand memory, legacy manual reference availability, and post-build reference usage recording. For website local selector work, `scripts/design_brain_website_reference_select.py` and `.design-brain/TEMPLATE_REFERENCE_GROUP_ROTATION_REGISTRY.json` own product-purpose groups of up to 10 eligible varied references, group rotation, and reset after the final group. Reference Insight may study only the active allowed selector group or manual reference set; it must not reuse a blocked brand name.

Design Craft and TypeUI-derived style support never override Brain Design gates. Use `.design-brain/DESIGN_CRAFT_NON_OVERRIDE_CONTRACT.md` when craft advice conflicts with routing, cognition, simulation, lifecycle, design system, post-build audit, or completion receipt status.

## Design Agent Runtime Position

Brain Design Runtime sits around the existing workflow as an operating loop:

1. User explicit instruction
2. Core Brain Design rules
3. Router / product family
4. Web Deck Intelligence
5. Brand & Reference Usage Memory Layer
6. Reference Insight
7. Design Cognition Contract
8. Section Layout Extraction Library / Matching Gate / Hyper-Accuracy Gate
9. Template Orchestration
10. Subagent Orchestration Layer
11. Design Simulation Layer
12. Sequential Layout Originality Gate
13. Build Session Lifecycle
14. Serial Provenance Gate
15. Design Craft support adapter
16. Design System Build Requirements
17. Web Deck Stage Gate
18. Post-Build Completion Gate
19. Completion Receipt / verify-final
20. Learning Loop

Runtime command/tool execution cannot override these priorities. Design Craft adapter output is support evidence only and cannot change route, product family, structure, cognition, simulation, layout audit, post-build status, or final readiness.

## Conflict Rules

- If `README.md` conflicts with `.design-brain/AUTOLOAD_POLICY.md`, the autoload policy wins.
- If trigger documentation conflicts with routing scripts, update both so they stay synchronized; do not keep two active interpretations.
- If a learning log conflicts with an active rule, the learning log is evidence/proposal only until promoted.
- If a valid user explicit request conflicts with a default preference, the user request wins for that task.
- Design Simulation Layer may block or revise a plan, but it must not override user explicit instruction, product-family rules, medium playbooks, reference insight, or source-of-truth routing.
- Subagent Orchestration may block final delivery when critical evidence is missing or semantically weak, but it must not invent fake receipts or approve work that Visual Review, Figma Source QA, originality, design-system, or marketplace gates have not actually inspected.
- If simulation contradicts product family or output contract, create a required repair and rerun orchestration; do not silently override the router.
- Design Simulation Layer is a gate, not a router source of truth. Intent router, module router, and product-family detector win over simulation fallback routing.
- If simulation route conflicts with Brain Design router, Brain Design router wins and simulation must rerun using the correct route.
- Marketplace template wording is distribution context, not ecommerce intent. Ecommerce/listing marketplace routing requires product, vendor, cart, checkout, platform, app, listing, booking, property, job, or service marketplace context.
- Protected owner rules cannot be weakened by convenience defaults, generated notes, or old scaffold habits.

## Update Discipline

`skills/presentation-deck/workflows/native.md` owns the native PPTX adapter under the
`presentation-deck` medium. Its pinned external engine supplies technical conversion
and source-preservation contracts, without overriding Brain Design design/readiness
gates. The shared rules in `pptx-native/routing.json` disambiguate explicit PPTX
output from generic animation wording across the Python router and plugin hook.
Explicit web conversion and dual-artifact requests retain their own output contracts.

- Prefer cross-references over copying the same rule into many files.
- Keep active rules in the workflow, router, taxonomy, gate, or product-specific file that owns them.
- Keep journals and evidence append-only unless the user explicitly authorizes cleanup.
- Do not edit `.design-brain/DESIGN_MEMORY.md` or `.design-brain/DESIGN_PREFERENCES.json` from one lesson unless the user explicitly asks for stable promotion.

## Design Simulation Priority

For sellable template products, `.design-brain/SUBAGENT_ORCHESTRATION_LAYER.md` and `.design-brain/DESIGN_SIMULATION_LAYER.md` bridge planning and building. Subagent Orchestration identifies active roles, required evidence, and missing receipts; Design Simulation evaluates whether the proposed plan should be built.

If a design simulation verdict is `REVISE` or `BLOCKED`, later review, visual polish, or marketplace gates cannot overrule it. The structure, visual strategy, source-template plan, or reference transformation must be revised and the simulation rerun until `PASS`.

## Unified Presentation Capability

`skills/presentation-deck/SKILL.md` is the only presentation skill entry. `skills/presentation-deck/design/WORKFLOW.md` owns shared presentation design; native and web workflow documents own only their output-specific execution. `web-deck` remains a routing/medium alias for browser mode, not a separate skill. General Brain cognition, originality, lifecycle and completion gates remain shared. The capability executes its adopted internal modules and never needs a donor checkout.
