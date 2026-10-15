# Website Reference Prompt Lock

This is the permanent Brain Design prompt lock for reference-led Figma website template work.

Use this file when the user asks for a website template, web template, Figma website template, source template, marketplace template, or reference-based website design. This file converts the user's preferred prompt into active workflow behavior.

## Core Instruction

Build a premium, complete, marketplace-ready website template in Figma from the provided reference evidence.

Use references only as Style DNA and product-standard evidence. Do not visually copy the reference.

Do not copy:

- exact layout
- composition
- section order
- hero shape or hero grammar
- scaffold/page builder pattern
- color palette, exact hues, gradients, CTA/background role mapping, or asset treatment
- component grouping
- spacing rhythm as a recognizable execution pattern
- image placement or media sequence
- visual motif or decorative signature

All photo/image zones in editable source templates must use placeholder text, such as `image placeholder: [purpose]` or `profile photo placeholder: [role]`, unless the user explicitly requests generated or final imagery.

## Brand & Reference Usage Memory

- Before extracting Style DNA, check `.design-brain/TEMPLATE_REFERENCE_USAGE_REGISTRY.json` through `scripts/design_brain_reference_usage_gate.py`.
- Do not reuse a spent reference brand or output brand name.
- For website local reference selection, use product-purpose group rotation from `scripts/design_brain_website_reference_select.py`.
- Do not use a generated output brand name, reference brand name, or too-similar prefix/suffix/token pattern as the new template brand.
- Use up to 10 eligible, varied local references in the active group when enough same-purpose matches exist.
- Rotate to the next same-product group for the next build; reset to group 1 only after the final group has been used.
- Record the allowed group key and usage mode in the Design Cognition Receipt, build record, build-session ledger, and post-build registry record.

## Minimum Website Template Completeness

For reference-led website template work, the default minimum is 9 meaningful main sections.

A complete marketplace-ready website template usually includes product-specific equivalents of:

- header / navigation
- hero section
- about / intro
- feature, service, or product-value section
- highlight content, process, mechanism, or editorial proof
- portfolio, gallery, product showcase, case study, or media proof
- testimonial, metric, logo, review, or social proof
- pricing, package, booking, cart, contact, or CTA block
- FAQ, objection handling, comparison, or support section
- blog, insight, resource, or update preview when relevant
- footer with navigation and trust cues

The section names and roles must match the product family. Do not use this list as a fixed scaffold. It is a completeness floor, not a layout recipe.

Fewer than 9 sections are allowed only when the user explicitly asks for a hero/header kit, micro landing page, narrow campaign, squeeze page, waitlist page, or another intentionally small product.

## Required Style DNA Extraction

Before planning, extract Style DNA from the reference:

- typography character
- layout rhythm
- color roles and color behavior
- image direction and media role
- density and spacing cadence
- shape language
- effect language
- premium visual signal
- product-family marketplace standard

Style DNA is not copied appearance. It is evidence for how the new original template should feel, sell, and behave.

## Visual Mood Reinterpretation

Preserve the emotional feel, market positioning, and quality level of the reference, but rebuild the expression through:

- different composition
- different palette behavior and role mapping
- different asset or placeholder treatment
- different content hierarchy
- different visual depth and surface grammar
- different visual emphasis and focal path
- different section rhythm

Never solve originality by only changing color, font, image, or spacing. If the structure and composition still feel like the reference, the design has failed reinterpretation.

## Structural Reconfiguration

Build the website structure from a fresh structure fingerprint:

- new hero grammar
- new grid system
- new section order
- new section-pattern mix from the Section Layout Extraction Library when active
- new content rhythm
- new CTA placement and conversion flow
- new component layout
- new user reading flow
- new visual navigation between sections
- desktop, tablet, and mobile responsive behavior plan

Avoid generic `Hero + Features + CTA + FAQ + Footer` scaffolds. Use product-family logic and buyer decision flow to decide sections and order.

When `.design-brain/SECTION_LAYOUT_EXTRACTION_LIBRARY.md` is active, choose section patterns as vocabulary only. Do not use one catalog pattern mix as a reusable page scaffold. Stable section patterns must have `qualityStatus: PASS`; incoming patterns are review evidence only.

## Visual Quality Bar

The final design must feel:

- emotionally related to the reference mood
- structurally different from the reference
- different in composition, section flow, and visual execution
- not minimalist-default
- not flat, empty, overly simple, or basic
- not built from a generic scaffold
- premium, layered, editorial, detailed, and marketplace-ready
- original enough to pass reference-vs-output and output-vs-output similarity checks
- cleanly editable, named, and Figma-ready

## Figma Source Best Practice

Every Figma website template build must include:

- real auto-layout for editable structure
- consistent grid/container system
- typography styles or clearly documented typography roles
- color styles or clearly documented color roles
- reusable components or component-like source modules
- button states
- card components and states
- form, input, navigation, footer, CTA, media placeholder, and product-specific modules when relevant
- responsive variants or responsive preview behavior when needed
- clean image placeholder areas
- clear layer and section names
- mini design system for color, typography, spacing, button, card, form, icon direction, component states, placeholder rules, and source hygiene

The design system must be buyer-usable, not just a receipt.

## Fail Conditions

Fail or revise before building/finalizing if:

- reference is copied visually
- hero grammar or section order is recognizably copied
- the output has fewer than 9 meaningful website sections without explicit small-scope permission
- the design is only a recolor, re-font, re-image, or spacing tweak of the reference
- the design uses a generic landing-page scaffold
- the design is minimalist-default, flat, empty, or underbuilt
- image zones do not use editable placeholders
- Figma auto-layout/source hygiene is missing
- the design system lacks concrete foundations, components, states, patterns, and responsive/editing notes
- desktop/tablet/mobile behavior is ignored when the product needs responsive source value
