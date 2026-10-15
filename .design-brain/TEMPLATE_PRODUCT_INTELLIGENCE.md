# Template Product Intelligence

Template Product Intelligence specializes Codex Design Brain for designing sellable, editable, marketplace-ready template products. It sits on top of the existing review, visual review, reflection, promotion, installer, and pilot workflows.

## Purpose

For any template product, Codex should determine the product logic before designing visuals. A strong marketplace template is not only attractive; it has a clear buyer, reusable structure, editable areas, and a preview system that sells the product.

## Required Questions

Before designing, answer:

- What type of template product is this?
- What medium is this: website, deck, dashboard, UI kit, brand kit, portfolio, or marketplace preview?
- If the medium is Figma, which Figma project or file should receive the output?
- If the medium is Figma, which editable structures must use auto-layout and what exceptions need to be documented?
- If the input is a Figma reference, which product purpose, visual direction, section structure, grid/layout, typography hierarchy, color-role system, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, Figma source hygiene, pages, frames, components, states, variants, and design-system areas were studied before planning?
- For website templates, which Figma website product family is this?
- What niche and marketplace category does it fit?
- Who is the target buyer?
- What section, screen, or component structure is required?
- Which TypeUI-derived style pack fits the product?
- Which medium/product playbook and style grammar apply?
- What editable areas must be obvious?
- Which image zones are semantic placeholders, and what replacement clue should each one show?
- What cover or preview direction will sell the product?
- What marketplace quality criteria must be passed?
- What generic-output risks should be avoided?

## Figma Template Scope Redirect

For a single Figma website/template request, do not build responsive preview boards or marketplace cover layouts by default. They are valuable package surfaces, but they must be opt-in unless the user explicitly asks for them, the task is a marketplace preview/cover task, or the delivery contract requires those assets.

When responsive preview or cover surfaces are omitted, this is a scope reduction, not a quality reduction. Redirect the saved effort into a stronger per-template design system board and source hygiene:

- color-role logic, not only swatches
- typography hierarchy with usage roles
- spacing, grid, radius, and surface-depth rules
- component anatomy for the core template components
- variants and states for buttons, cards, nav, forms, accordions, and product-specific modules
- reusable section modules that connect directly to the built template
- placeholder rules for images, profiles, charts, and diagrams
- effect and surface tokens with semantic purpose
- source editing guidance for buyers

Do not interpret `no responsive preview` or `no marketplace cover` as permission to make a thin design system.

## Template Product Types

- Website landing page templates
- Figma website templates
- Figma website product families: multipurpose/full website, landing/campaign, SaaS/product website, corporate/business, professional service/booking, agency/studio, portfolio/case-study, ecommerce/storefront, marketplace/listing/directory, editorial/blog/CMS, education/course/LMS, documentation/help center, dashboard/admin web app, community/nonprofit/membership, event/venue/travel/hospitality, and utility pages kit.
- Dashboard templates
- SaaS templates
- UI kits
- Design system templates
- Branding kit templates
- PowerPoint, Google Slides, Keynote, and pitch deck templates
- Portfolio deck templates
- Marketplace preview layouts
- Template cover layouts
- Section breakdown overviews
- Perspective mockup overviews
- Responsive preview layouts

## Operating Rule

Do not design from visuals alone. Convert product type, niche, buyer, style pack, structure, editability, and preview direction into design constraints before making the first draft.

For advanced work, run or follow `scripts/design_brain_medium_playbook.py` first. If the task is a presentation deck, use `skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md` and plan a slide-role matrix instead of a website section map.

For website template work, read or follow `.design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.md` before planning visuals. Landing page is a specific product family, not the default website-template interpretation.

For website template work, use `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md` and the local `Template Website` preview corpus after product-family classification. This corpus is the first local evidence source for expected section depth, density rhythm, proof strategy, and buyer completeness.

For Figma website template work, use `.design-brain/FIGMA_OUTPUT_TARGET.md` as the output-target policy when the user has not provided another Figma project, file, or node. Create a new Figma design file only when a valid configured project/file target exists. If the target is missing, placeholder, or the publish-safe package has no local config, do not call `create_new_file`; ask for a valid target or continue with local planning only.

For Figma source-template work, use `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md`. Editable sections, navigation, CTAs, cards, forms, repeated rows, dashboards, responsive groups, and design-system panels must use real auto-layout. Manual coordinate layout is limited to documented decorative or overlay exceptions.

For Figma reference-link work, use `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md` and `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md`. Study the reference as a whole source-template system before planning: product purpose, visual direction, section structure, grid/layout, typography hierarchy, color-role system, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, Figma source hygiene, product family, page/frame map, component sets, variants, states, design-system panels, effect language, and standard structure depth. Unknown category standard must trigger more evidence, corpus/category lookup, or one targeted question; it must not trigger a minimalist fallback.

For editable template-source work, follow `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`. Do not generate final imagery just because references contain images. If the user did not explicitly ask for generated images, represent image needs with product-specific text clue placeholders such as `image placeholder: SaaS dashboard screenshot`, `profile photo placeholder: doctor portrait`, or `image placeholder: ecommerce product image`.

## Product Depth Rule

Do not mistake a sparse, elegant first page for a marketplace-ready template product.

- Each template type has a normal structural expectation: section count, page map, states, reusable modules, and buyer-journey coverage.
- The product standard comes before stylistic restraint. Quiet visuals can be premium; shallow structure is usually underbuilt.
- For website, web-template, Figma website-template, and standard landing-page template work, fewer than 8 meaningful sections/blocks is below the competitive floor unless the user explicitly asked for a small-scope product such as a hero/header kit, micro landing, narrow campaign, squeeze page, or waitlist page.
- Minimalist, clean, safe, simple, fallback, restrained, or basic visual language must never be used to justify under-8 section structure.
- If the user gives a rich reference, assume the reference is demonstrating product completeness as well as mood. Study its breadth, pacing, and standard roles before reinterpreting the layout.
- If a product category's standard is unclear, use external research before planning. Do not invent a short structure from taste.
- Do not reuse old task-specific omissions such as desktop-only, no components, no devices, or no cover/preview as default limits. Let the current product standard decide whether components, responsive/device surfaces, cover/preview, or page-map notes improve the template.

## Design System Board Standard

The design system board for a Figma template must be commercially useful, not merely a receipt. It may be compact, but it must not be minimalist in coverage.

Minimum acceptable design-system coverage:

- Foundations: color roles, type roles, spacing/grid, radius, elevation/surface, icon/media/placeholder treatment.
- Component anatomy: at least the main reusable parts of the template, with labels for what changes and what remains stable.
- Variants/states: default, hover, focus, active, disabled, plus product-specific states when relevant.
- Section modules: hero, proof/trust, feature/service, process/workflow, pricing/package, FAQ, contact/lead, footer, and product-specific modules.
- Usage logic: when to use each module, how to extend it, and what not to change.
- Source hygiene: auto-layout expectations, naming behavior, placeholder replacement, text editability, and decorative exceptions.

Fail the design system if it is only color swatches, typography samples, one or two buttons, and a receipt note. That is a token receipt, not a design system.
