# Template Product Quality Gate

Use this checklist before calling a template product marketplace-ready.

When a gate fails, report it with `.design-brain/QUALITY_GATE_FAILURE_TAXONOMY.md`: PASS/FAIL, failure category, evidence, root cause, required action, and whether rebuild/recompose/recolor/rewrite/source repair is needed.

## Post-Build Completion Requirement

A marketplace template product is incomplete without:

- built template
- built design system tied to the template
- post-build triple audit
- batch pairwise similarity audit when more than one template is delivered
- repair loop after failed audits
- completion receipt in the final response

## Design Cognition Contract Requirement

Before template orchestration/build, require a Design Cognition Receipt. Fail quality gate when:

- cognition_contract_missing
- color_identity_copy
- reference_boundary_violation
- weak_visual_grammar
- missing_structural_reconfiguration
- weak_pattern_divergence
- generic_section_logic
- weak_marketplace_readiness

## Product Clarity

- [ ] Product concept is clear.
- [ ] Template type is obvious.
- [ ] Medium is obvious: website, deck, dashboard, UI kit, brand kit, portfolio, or preview.
- [ ] Target niche is obvious.
- [ ] Target buyer is specific.
- [ ] Marketplace category is clear.
- [ ] For Envato/marketplace, reference-based, anti-identical, anti-minimalist, or batch template work, a Design Simulation verdict exists and is `PASS` before build.
- [ ] For Figma website templates, one of the 16 website product families is explicitly selected before structure planning.
- [ ] For website-template work, product-family-matched references from `Template Website` were checked before assuming structure, density, proof placement, or buyer completeness.
- [ ] For reference-based work, the reference standard was extracted: section count/range, section roles, layout-shape inventory, color-role inventory, effect/gradient inventory, and marketplace completeness clues.
- [ ] Landing page is selected only when the brief explicitly asks for landing/campaign/lead-generation/sales-page intent.

## Structure And Reuse

- [ ] Structure count is justified by product purpose, not by a reduced-scope habit.
- [ ] Product-type standard count has been checked before design; if uncertain, web/category research was used.
- [ ] Website, web-template, Figma website-template, and standard landing-page templates have at least 8 meaningful sections/blocks unless the brief explicitly asks for a hero/header kit, micro landing, narrow campaign, squeeze page, or waitlist page.
- [ ] Minimalist, clean, restrained, safe, simple, fallback, or basic visual language was not used as an excuse for fewer than 8 sections.
- [ ] If a Figma reference was used, a Figma reference schema receipt exists before build.
- [ ] If a Figma template reference was used, the professional reading order was completed: product purpose, visual direction, section structure, grid/layout, typography hierarchy, color roles, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, and Figma source hygiene.
- [ ] Figma reference study includes pages, frames, sections, components, variants, states, design-system panels, density rhythm, and product-family standard inference.
- [ ] Reference study includes layout-shape inventory and safe remix options, not just mood, colors, or generic section names.
- [ ] Unknown Figma category standard was resolved through taxonomy/corpus/category evidence or one targeted question, not a minimalist fallback.
- [ ] Section count is normal for the product category, not forced long, not forced minimalist, and not copied one-to-one from the reference.
- [ ] The template is not merely visually different from the reference; it is structurally complete enough to sell as a product.
- [ ] Old task-specific omissions such as no components, no devices/mobile/tablet, no cover/preview, or desktop-only were not reused as persistent bans; output surfaces match the current request, product category, marketplace standard, and buyer value.
- [ ] Website tasks are classified with `.design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.md` before section count is chosen.
- [ ] Generic website, SaaS website, business website, ecommerce, portfolio, blog, docs, dashboard, event, travel, marketplace/listing, and education briefs are not automatically routed to landing-page.
- [ ] For single Figma website/template builds, responsive preview boards and marketplace covers were not created by default; they were included only when explicitly requested or required by the delivery contract.
- [ ] If responsive preview/cover surfaces were omitted, the saved scope was redirected into a stronger design system rather than a thinner deliverable.
- [ ] Section structure makes sense for the product type.
- [ ] The structure follows the correct medium playbook.
- [ ] Full website templates include a homepage block map and inner page map.
- [ ] Landing pages include enough proof, detail, objection handling, conversion closure, and footer trust for their goal.
- [ ] Homepage-only outputs include enough standard blocks to feel reusable; otherwise they are labeled as small landing pages or kits, not full template products.
- [ ] Hero/header kits are labeled as kits and do not pretend to be full websites.
- [ ] Presentation decks use slide roles, not website section maps.
- [ ] Reusable components or sections are visible.
- [ ] Editable placeholders are clear.
- [ ] Source-template image areas use text clue placeholders such as `image placeholder: [purpose]` unless the user explicitly asked for generated/final images.
- [ ] Human/profile image areas use `profile photo placeholder: [role]` instead of generated fake people.
- [ ] Reference imagery has been translated into replacement-slot logic, not copied or regenerated as final source-template content.
- [ ] Responsive needs are considered.
- [ ] The template can be adapted across client projects.

## Figma Auto-Layout Gate

- [ ] Figma source-template structure uses real auto-layout for editable sections, groups, cards, rows, controls, and design-system panels.
- [ ] Major frames define padding, gap, alignment, and resizing behavior instead of relying on primary manual x/y positioning.
- [ ] Child layers use clear `HUG`, `FILL`, or `FIXED` sizing semantics where resizing matters.
- [ ] Decorative absolute-position layers are limited to backgrounds, glows, overlays, mockup callouts, or preview-only effects.
- [ ] An auto-layout receipt names the main auto-layout groups and any documented exceptions.
- [ ] A Figma template without auto-layout is failed before marketplace-ready delivery.

## Design System Depth Gate

- [ ] The design system board is not merely a minimalist receipt of swatches, typography, one button, and notes.
- [ ] Color roles explain function: background, surface, elevated surface, text, muted text, border, action/accent, and product-specific signals.
- [ ] Typography roles explain usage across hero, section headings, cards, labels, body, nav, buttons, and metadata.
- [ ] Spacing/grid/radius/elevation rules show how sections and components should be extended.
- [ ] Component anatomy is visible for core template components, not only final page instances.
- [ ] Variants/states are represented: default, hover, focus, active, disabled, and product-specific states when relevant.
- [ ] Reusable section modules are documented from the actual template: hero, proof, feature/service, process/workflow, pricing/package, FAQ, contact/CTA, footer, and niche-specific blocks.
- [ ] Placeholder rules cover image, profile, chart/diagram, screenshot, and other source-template replacement zones.
- [ ] Effect/surface tokens are semantic and applied where useful; restraint is allowed only when another hierarchy mechanism is documented.
- [ ] Buyer source-editing guidance is included so the template can be reused without reverse-engineering the main page.

## Style Fit

- [ ] Visual style matches buyer and niche.
- [ ] Selected style pack is coherent.
- [ ] Reference colors were interpreted as color-role insight, then reconstructed into an original palette fit for product type, buyer, accessibility, and intended emotion.
- [ ] Color exploration proves the selected A+B, A+B+C, or richer A-G role map works for hierarchy, CTA, contrast, mood, and batch differentiation.
- [ ] Exact palette, glow color, gradient sequence, and accent/CTA/background role map were not copied from the reference.
- [ ] Effects and gradients were explored as functional options; if omitted, deliberate restraint is documented with the hierarchy mechanism that replaces them.
- [ ] There is no mismatched style pack.
- [ ] Spacing and typography are consistent.
- [ ] The design does not look generic.
- [ ] Human craft is visible through rhythm, hierarchy, restraint, and product-specific judgement.

## Originality And Similarity

- [ ] Reference insight was deconstructed before designing.
- [ ] Section or slide order is not copied.
- [ ] Composition, spacing rhythm, motif, grouping, and title/media placement are reinterpreted.
- [ ] Layout shape ideas borrowed from references are recombined subtly; no final section remains obviously traceable to one reference layout.
- [ ] Color-role mapping is original, not merely the reference palette with small shade changes.
- [ ] Naming and marketplace preview staging are not recycled.
- [ ] Similarity risk is 5 or below when scored.
- [ ] Text-only similarity heuristics are not presented as visual proof. If no screenshot/render was inspected, state: `Visual similarity not verified; only textual/structural heuristic checked.`
- [ ] For repeated or batch template work, the current `structure_fingerprint.json` was compared against accepted prior fingerprints before build.

## Marketplace Presentation

- [ ] Preview direction is strong.
- [ ] Cover or overview has marketplace-ready potential.
- [ ] Section breakdown can prove product completeness.
- [ ] Perspective or mockup effects improve selling power without hiding the UI.

## Anti-Generic Gate

- [ ] No random decoration.
- [ ] No overuse of trendy effects.
- [ ] No visual clutter.
- [ ] No vague generic SaaS copy.
- [ ] No one-off layout decisions that break editability.
