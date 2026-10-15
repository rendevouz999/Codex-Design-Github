# Medium Product Playbooks

Use this file before designing any template product. The goal is to prevent Codex from treating every design as a landing page. Choose the medium first, then choose structure, style, and critique criteria.

## Universal Medium Decision

Before planning visuals, identify:

- Medium: website, presentation deck, web deck, dashboard, UI kit, brand kit, portfolio, marketplace preview, or other.
- Buyer: who purchases or reuses the template.
- End user: who experiences the finished output.
- Primary use: sell, explain, operate, present, document, showcase, or govern.
- Design system scope: tokens, components, slide masters, chart rules, brand rules, or preview rules.
- Anti-generic risk: what would make this medium feel like a generic AI template.

## Landing Page / Website Template

Purpose:
- Convert a visitor through a vertical scroll experience.
- Make the offer, category, product, or brand obvious in the first viewport.
- For full website templates, prove a complete reusable site system, not only one conversion page.
- Choose the Figma website product family before choosing section order.

Structure:
- First classify scope using `.design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.md`: multipurpose/full website, landing/campaign, SaaS/product website, corporate/business, professional service/booking, agency/studio, portfolio/case-study, ecommerce/storefront, marketplace/listing, editorial/blog/CMS, education/course/LMS, docs/help center, dashboard/admin/web app, community/nonprofit/membership, event/venue/travel/hospitality, or utility pages kit.
- Before planning from assumption, use `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md` and the local `Template Website` preview corpus to select product-family-matched references.
- Do not classify a website as landing-page unless the brief explicitly says landing page, lead generation, campaign, sales page, squeeze page, or waitlist.
- Hero/header kit: 1-4 narrow variants or 5-12 broader variants, with navigation and responsive behavior.
- Focused landing page: usually 6-8 sections.
- Standard product/service landing page: usually 8-12 sections.
- Trust-heavy sales/service page: often 10-14 sections.
- Full website template: homepage with 8-12 content blocks plus a relevant inner page map.
- Website template: still use standard product depth. Do not reuse old exclusions around mobile/components/cover/preview as persistent bans; decide those surfaces from the current product category and buyer value. Serious service, SaaS, business, and trust-heavy pages usually need 10-14 product-specific blocks plus page-map/design-system evidence.
- SaaS/product website: 10-14 homepage blocks plus features, use cases, pricing, integrations, customers/case studies, resources/blog, security/docs, contact/demo, and auth/utility.
- Ecommerce website: shop/category/product/cart/checkout/account/support pages and states.
- Marketplace/listing/directory: search/filter, listing index, listing detail, map/compare, saved/favorites, inquiry/booking, account/profile, and support.
- Editorial/blog/CMS: article, category/archive, author, search, newsletter, about/contact, and utility pages.
- Documentation/help center: docs home, category, article, search, API/reference, changelog, support/contact, and utility pages.
- Dashboard/admin website: app shell, dashboards, apps, forms, tables, components, auth, states, and settings.
- Desktop, tablet, and mobile frames.
- For Figma website templates, editable section frames, navigation, repeated modules, CTAs, forms, cards, and design-system panels use real auto-layout with a documented receipt.

Design system:
- Color, type, spacing, radius, shadow, buttons, forms, nav, cards, icons, section rules, responsive rules.
- For full templates, also define page-map rules, reusable section variants, form states, navigation states, footer system, product-specific components, and auto-layout behavior.

Anti-patterns:
- Using visual restraint as a reason to underbuild structure.
- Equating "clean premium" with fewer sections.
- Delivering only a concept homepage when the user asked for a template product.
- Treating any output-scope decision as permission to omit required product sections, proof, states, or page-map thinking.
- Treating every website template as a short landing page.
- Same hero-card-feature-pricing order for every niche.
- Decorative mockups that hide the actual page.
- Generic bento grids without a buyer reason.
- CTA repetition without content progression.
- Figma source templates built primarily from manual x/y positioning instead of editable auto-layout structure.

Acceptance criteria:
- Structure count is justified by template purpose and buyer journey.
- The template meets or exceeds the standard structure for its product type before visual polish is considered.
- The page reads as a real product in the first viewport.
- Section order supports conversion and buyer trust.
- Responsive behavior is planned and inspectable.
- Full website templates include enough pages/sections to feel reusable and sellable.
- Figma outputs include an auto-layout receipt and documented decorative exceptions.

## PowerPoint / Pitch Deck / Presentation Template

Purpose:
- Communicate a story slide by slide.
- Give buyers reusable slide roles, not a resized website.

Structure:
- Cover, agenda, divider, intro, problem, solution, market, service/product, timeline, metric, chart/table, comparison, team, quote/testimonial, contact, closing.
- Build each slide as an individual 16:9 frame.
- For Figma-to-PPTX export pages, prefer exact 1920x1080 Full HD frames when the plugin or PowerPoint output treats smaller 16:9 frames as inset content.
- Use slide-role matrix before visuals.

Design system:
- Theme colors, heading/body fonts, type scale, slide masters, layout masters, title positions, safe margins, footer/page number rules, chart palette, table style, image placeholder treatments, section divider rules.

Anti-patterns:
- Long-scroll website logic.
- Same slide sequence as the reference.
- Same title placement or master rhythm across variants.
- Dense paragraphs without grouping.
- Missing chart/table/footer rules.
- Assuming a mathematically correct 16:9 frame is enough without checking whether the PowerPoint export fills the slide.

Acceptance criteria:
- Each slide has one dominant idea.
- The deck remains readable as thumbnails.
- Slide roles are reusable and visibly different.
- It includes master/layout thinking and presentation-specific tokens.
- Converted PowerPoint output fills the slide area, with no unintended undersized frame inside the slide.

## Web Deck / HTML Presentation

Purpose:
- Present a story in a browser, slide by slide, on a fixed stage.
- Give the room a deck that runs from one file, one link, and one keyboard.
- Replace a static slide artifact only when motion, runtime navigation, or link sharing is part of the value.
- Choose the `web-deck` medium before structure when the brief says web, HTML, browser, animated, or interactive deck.

Structure:
- Use the slide archetype set: cover, agenda, section-divider, problem, solution, feature, data, dashboard, timeline, roadmap, case-study, testimonial, team, pricing, portfolio, closing.
- Author every slide on a fixed 1920x1080 stage. The stage scales uniformly to the viewport and letterboxes the leftover space.
- Give each slide a reveal order so its blocks arrive in reading order instead of all at once.
- Runtime navigation: arrow and page keys, space, Home and End, tap zones for coarse pointers, a debounced wheel step, and a `#<n>` deep link.
- Keep chrome such as progress, page number, and controls outside the scaled stage and out of print output.
- Plan print as one slide per page, so the deck still leaves a shareable PDF behind.
- Choose the density mode, speaker-led or reading-first, before writing slide copy.

Design system:
- Stage tokens, color roles, display/body pairing, type scale authored at stage size, stage padding, block and item gaps, slide-role matrix, chart palette, media placeholder rules, chrome rules.
- Motion signature: entrance set, accent set, forbidden set, entrance/transition/stagger durations, and one easing curve.
- A reduced-motion path for every animation, and a visible focus state for every runtime control.

Anti-patterns:
- Long-scroll website logic.
- Reflowing slide content for phones instead of scaling the stage.
- Identical entrance on every slide.
- Motion replacing structure.
- Display-toggled slides, which a later layout rule overrides so every slide reveals at once.
- Chrome drawn inside the stage, so it scales with the slides and prints with them.
- Framework or CDN payload for a deck that needs one file.

Acceptance criteria:
- Each slide has one dominant idea and holds it at any scale.
- The stage fits every target viewport with no clipped, overlapping, or overflowing content.
- Navigation, deep link, reduced motion, and print behave as specified.
- Motion follows the declared signature and differs by slide role.
- Static audit and rendered review both pass and are recorded.

## Dashboard / Admin / Analytics Template

Purpose:
- Help a user scan status, compare data, and act repeatedly.
- Prioritize operational clarity over marketing drama.

Structure:
- App shell, topbar, navigation, KPI overview, charts, data tables, filters, detail panel, activity feed, settings, empty/loading/error states.

Design system:
- Data color roles, chart styles, density scale, table states, form states, nav states, status badges, focus states, empty/loading/error patterns.

Anti-patterns:
- Oversized hero areas.
- Decorative cards inside cards.
- Charts without labels, legends, or comparison purpose.
- One-note dark-blue or purple dashboard palettes.

Acceptance criteria:
- Scan hierarchy is clear within seconds.
- Data states and table interactions are represented.
- The layout feels useful for repeated work.

## UI Kit / Design System Template

Purpose:
- Provide reusable foundations and components that buyers can adapt.

Structure:
- Foundations, tokens, typography, color, spacing, radius, shadows, icons, buttons, inputs, nav, cards, tables, modals, states, variants, examples, usage notes.

Design system:
- Token naming, component states, variants, documentation, accessibility notes, usage boundaries.

Anti-patterns:
- Components without states.
- Tokens without usage meaning.
- Pretty boards that do not explain when to use elements.

Acceptance criteria:
- Components are easy to find, edit, and reuse.
- States and variants are complete enough for real usage.
- Documentation prevents guesswork.

## Brand Kit / Identity Template

Purpose:
- Help a buyer present or apply a visual identity consistently.

Structure:
- Brand concept, logo usage, color palette, typography, graphic elements, photography/art direction, social layouts, stationery/collateral, mockups, usage rules.

Design system:
- Logo clear space, palette roles, type roles, image treatment, graphic motif, layout examples, do/dont rules.

Anti-patterns:
- Only logo mockups without usable guidelines.
- Random color palettes without roles.
- Brand visuals that do not survive small sizes or one-color usage.

Acceptance criteria:
- The identity can be applied across multiple touchpoints.
- Rules are clear enough for a non-designer buyer to reuse.

## Portfolio Template

Purpose:
- Showcase work, taste, and credibility.

Structure:
- Intro, selected work, case detail, about/philosophy, services or capabilities, testimonial/proof, contact.
- For deck portfolios, use gallery slide roles instead of scroll sections.

Design system:
- Editorial typography, project cards, image/gallery treatment, case-study structure, contact rules.

Anti-patterns:
- Generic personal hero with no work signal.
- Project grids that hide the actual work.
- Decorative typography that harms readability.

Acceptance criteria:
- The work is the visual priority.
- The template helps a creative person or agency look credible clearly.

## Marketplace Preview / Cover Template

Purpose:
- Sell a template product clearly and honestly.

Structure:
- Cover, primary preview, section/screen breakdown, responsive spread, style overview, detail crops, included items, final thumbnail.

Design system:
- Preview frame rules, mockup angle rules, label system, product naming, background system, crop/detail rules.

Anti-patterns:
- Beautiful cover that hides weak template structure.
- Over-perspective mockups that make screens unreadable.
- Cover text that says "premium" but shows no product evidence.

Acceptance criteria:
- Buyer understands the category and value within seconds.
- The preview proves completeness, editability, and polish.
