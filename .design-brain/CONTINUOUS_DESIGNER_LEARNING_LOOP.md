# Continuous Designer Learning Loop

This file defines the long-horizon learning workflow for professional template-design cognition.

The goal is not speed. The goal is to keep learning until Design Brain can explain and apply the logic, schema, and decision pattern of a professional template designer.

## Core Rule

After a substantial template build, reference study, batch template task, or user critique, learning is not finished.

Codex must continue with a question-led learning loop:

1. Capture what was built, studied, or criticized.
2. Extract the strongest lesson and the weakest uncertainty.
3. Turn the uncertainty into one or more new design questions.
4. Search for outside evidence on the web when the user asks for deeper learning or when the question affects marketplace quality.
5. Prefer primary or high-signal sources: Figma documentation, Material Design, Nielsen Norman Group, Baymard, Webflow Marketplace, Envato author requirements, official design-system documentation, and credible research.
6. Compare web evidence against local reference evidence.
7. Distill the answer into a designer schema: buyer effect, structure logic, visual logic, source-file logic, and marketplace value.
8. Apply the schema in the next design or write a proposed rule change when the lesson is actionable.
9. Record the learning as evidence, not as stable memory, unless the user explicitly requests stable memory promotion.

By default, learning creates proposed rules in `.design-brain/proposed-rules/` using `.design-brain/templates/PROPOSED_RULE_CHANGE.md`. Do not directly change active rules from a single lesson.

## Learning Is Complete Only When

A learning cycle is not complete just because one file was created or one design was generated.

It is complete only when Codex can answer:

- What did the reference or output teach?
- What question did that lesson create?
- What evidence was found beyond local intuition?
- What changed in the designer schema?
- What must be applied differently next time?
- What should not be copied or overgeneralized?
- Which Brain Design rule, workflow, or checklist needs to change?
- What remains unresolved for the next cycle?

## Designer Schema Dimensions

Every deep learning cycle should update understanding across these dimensions:

- Product type: what kind of template product is this?
- Buyer decision: what must the buyer believe before purchasing?
- End-user effect: what should the final user feel, understand, trust, or do?
- Marketplace standard: what makes this complete and sellable?
- Structure depth: which sections, pages, states, or modules are expected?
- Attention path: where does the viewer look first, second, and third?
- Rhythm: where does the design create calm, density, proof, contrast, or action?
- Visual language: color roles, typography, spacing, image direction, effects, surface depth, and motif.
- Content logic: what objections are answered and where?
- Source editability: naming, auto-layout, components, variables, styles, placeholders, documentation, and responsive behavior.
- Originality: which abstract logic transfers and which visible execution must change?

## Question Types To Generate

When learning from a template, Codex should create new questions such as:

- Why did this product family need this section depth?
- What buyer objection is this section answering?
- Why is proof placed before or after the CTA?
- What is the real role of the color accent?
- Is this image decorative, product proof, emotional proof, or instruction?
- Which component should become reusable, and which should stay local?
- What responsive behavior would a buyer expect?
- What makes this feel complete rather than thin?
- What makes this different from a generic clean layout?
- Which marketplace requirement would reject this output?
- Which visual decision is art direction, and which is source-file hygiene?
- What would make two templates feel like siblings even when colors differ?

## Web Evidence Rules

Use web search when:

- the user explicitly asks for deeper learning via web search
- a product category standard is unclear
- marketplace readiness is being claimed
- responsive, accessibility, ecommerce, Figma source, component, or design-system behavior needs evidence
- a local rule risks becoming a personal assumption instead of a tested design principle

Do not use web search to copy design layouts. Use it to answer design questions.

For each source, record:

- source title and URL
- what question it helps answer
- what evidence it gives
- how the answer changes Brain Design behavior
- confidence: high, medium, or low

## Evidence-To-Rule Promotion

One web source is not enough to rewrite stable taste.

Learning produces a proposed rule by default. Promote a learning into active workflow only when:

- the user explicitly asks for the rule change
- repeated feedback supports it
- multiple evidence sources support it
- it fixes a known failure mode and the scope is clear

Do not update `DESIGN_MEMORY.md` or `DESIGN_PREFERENCES.json` automatically. Keep evolving learning in evidence files, workflow files, templates, and reflection logs unless stable-memory promotion is explicitly requested.

Never generalize one niche-specific lesson into a global rule. Choose scope deliberately: global, product-family, niche, or project-only.

## After-Build Learning Requirement

After substantial Figma/template work, Codex should produce or mentally complete:

- build summary
- visual inspection result
- auto-layout/source editability result when Figma is involved
- cross-template similarity result when batch work is involved
- question backlog
- at least one deeper research question when the task is part of long-term learning
- next application rule

Quality learning may take longer than fast output. That is expected.
