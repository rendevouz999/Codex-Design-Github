# Template Structure Rules

Use these rules to decide what sections, components, and editable areas are required for a template product.

## Universal Product Structure

Every template product should define:

- Template type and marketplace category.
- Target buyer and target end user.
- Primary conversion or usage goal.
- Required sections, screens, or component groups.
- Editable text, image, data, and brand areas.
- Image placeholder policy: source templates use text clue placeholders by default, not forced generated imagery.
- Figma auto-layout policy: editable Figma template structure uses real auto-layout, not primary manual coordinate layout.
- Figma reference deep-study policy: when a Figma reference is used, study pages, frames, sections, components, states, variants, and product-family standard before deciding structure.
- Figma professional template learning policy: when a Figma template reference is used, study product purpose, visual direction, section structure, grid/layout, typography hierarchy, color roles, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, Figma source hygiene, and default-template syndrome risks before deciding structure.
- Responsive preview requirements.
- Preview and cover presentation direction.
- Marketplace quality criteria and anti-generic risks.

## Structure Count Is Purpose-Driven

Visual spareness is not a valid standard for deciding how many sections, pages, screens, or components a template needs. A template may have a quiet visual language, but its structure must be complete for its purpose, buyer, marketplace category, and end-user journey.

## Reference Standard Extraction Gate

When a reference is provided, "follow the reference standard" means extracting the reference's product depth before deciding the new structure. Do not translate this into minimalist styling or a generic section count.

Before planning the output, record:

- visible or inferable section count and section roles
- repeated module types and how many times they appear
- layout-shape inventory: split, rail, shelf, grid, table, gallery, timeline, drawer, stack, stage, ledger, form, footer, or other visible shapes
- density rhythm: where the reference is spacious, compact, proof-heavy, visual-led, or conversion-led
- color-role inventory: background roles, surface roles, CTA/accent roles, supporting hues, neutral system, contrast behavior, and any multi-color relationships
- effect/gradient inventory: shadows, glow, blur, overlay, texture, hairline, depth, gradient direction, and where the reference deliberately stays flat
- marketplace completeness clues: design-system depth, components, variants, responsive views, preview/cover, page map, or source hygiene

The rebuilt template does not copy the reference order or exact visuals, but it must match the standard of depth and craft implied by this evidence. If the reference has rich structure, varied section shapes, color interplay, effects, or gradients, the rebuilt template cannot be justified as minimalist unless a deliberate and evidence-backed restraint plan proves equal marketplace value.

## Operational Section Depth Lock

- Hero/header kit: 1-3 blocks only when explicitly requested as a hero/header kit.
- Landing page campaign: 6-10 sections depending on use case; 6-8 only for explicitly narrow campaign, squeeze, waitlist, or micro landing scope.
- Full website template: 8-14 meaningful sections/blocks minimum.
- Reference-led website/Figma website template: 9-14 meaningful sections/blocks minimum unless the brief explicitly requests a small-scope product.
- SaaS/product website: 9-14 sections.
- Corporate/business/finance: 8-12 sections.
- Ecommerce/storefront: 10-16 sections or a multi-page/module map.
- Restaurant/hospitality/event/travel: 8-12 sections.
- Portfolio/agency: 7-12 sections.
- Editorial/blog/CMS: 8-12 sections plus content/archive logic.
- Dashboard/admin: do not use section count; use screen/module/state count.
- UI kit/design system: do not use section count; use component/category/state coverage.
- Presentation deck: do not use website section count; use slide system coverage.
- Mobile app: do not use website section count; use screen flow/state coverage.

Forbidden:

- Fewer than 8 sections for a competitive website template unless an explicit small-scope product is requested.
- Using "minimalist", "clean", "safe", "simple", or "premium" as an excuse for thin structure.
- Using generic hero + features + pricing + FAQ + footer as the default scaffold for every template.

## Competitive Website Section Floor

For website, web template, Figma website template, and standard landing-page template work, the competitive baseline is at least 9 meaningful sections or homepage blocks when references are provided or marketplace readiness is requested.

Do not use "minimalist", "safe", "simple", "fallback", "clean", "restrained", or "basic" as a reason to produce fewer than 9 sections. That is underbuilt for competitive marketplace design unless the user explicitly asks for a hero/header kit, micro landing page, narrow campaign, squeeze page, waitlist page, or another intentionally small product.

If the user did not explicitly request a small-scope product, a reference-led website plan with fewer than 9 meaningful sections must fail before design starts. Standard product/service pages should usually use 9-12 sections, and serious SaaS, service, finance, healthcare, education, ecommerce, or trust-heavy pages should usually use 10-14 sections.

For website-template requests based on references, use `.design-brain/WEBSITE_REFERENCE_PROMPT_LOCK.md` before section planning. The section list should be product-specific and must not become a fixed Header / Hero / Features / CTA scaffold.

## Standard Scope, Not Forced Long Or Minimal

Template structure should follow the normal product standard for the selected template type.

Do not force every reference into a long 12-15 section structure. Do not force every reference into a short minimalist page. Decide the section count from:

- product type and marketplace category
- target buyer and end-user decision journey
- how much proof, explanation, objection handling, and conversion support the product normally needs
- what the reference suggests about rhythm and density
- local corpus or category evidence when available

Codex may infer a practical section count from the reference when the reference gives enough evidence. The inferred count does not need to match the reference exactly. If the reference is short but the product type normally needs more proof, add the missing standard roles. If the reference is long but the product is narrower, condense it into a normal complete structure instead of padding.

The correct output is neither "minimalist by habit" nor "long by rule"; it is product-complete at the normal standard for the category.

## Product Completeness Gate

For sellable template products, "different from the reference" is only one gate. The stronger gate is whether the result has enough structure to be called a reusable product.

- Do not treat a sparse homepage as marketplace-ready just because it looks clean.
- Do not let originality checks replace completeness checks.
- Do not carry old task-specific omissions such as desktop-only, no component, no cover/preview, or no mobile into new briefs as persistent bans. Decide output surfaces from the current request, product family, buyer value, and marketplace standard, while keeping the buyer journey complete.
- If the output is only one desktop page, it must usually be a dense standard homepage, not a short concept page. Add enough product-specific blocks to cover discovery, trust, explanation, proof, conversion, objections, and footer/navigation.
- If the task intentionally excludes inner pages, still include an inner-page map or "included pages/extendable sections" block inside the design system or template notes so the buyer sees how the product grows beyond the homepage.
- If the standard structure for a niche is uncertain, do web/category research before deciding section count.
- For website templates, first use `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md` and the local `Template Website` preview folder to find product-type evidence. Do not decide section count from assumption when local corpus examples exist.
- A page is allowed to feel restrained. It is not allowed to feel underbuilt.

Before designing, choose the product scope:

- Use `.design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.md` and `.design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.json` as the website-template taxonomy before selecting section count.
- Design Brain recognizes 16 practical Figma website-template product families: multipurpose/full website, landing/campaign page, SaaS/product website, corporate/business website, professional service/booking website, agency/studio website, personal portfolio/case-study site, ecommerce/storefront, marketplace/listing/directory, editorial/blog/CMS, education/course/LMS, documentation/help center/developer docs, dashboard/admin/web app, community/nonprofit/membership, event/venue/travel/hospitality, and utility pages kit.
- Landing page is not the default. Use landing-page only when the brief explicitly says landing page, lead generation, campaign page, sales page, squeeze page, or waitlist page.
- If the brief says website, web template, Figma website template, SaaS website, business website, service website, ecommerce, portfolio, blog, docs, dashboard, event, or similar without explicit landing-page language, select the matching website product family and follow its standard.
- Hero/header kit: a section kit with variants, not a full website.
- Landing page: one focused conversion page.
- Full website template: homepage plus inner page map.
- Ecommerce template: product discovery, transaction, account, and support pages.
- Dashboard/admin template: operational screens, components, states, tables, and forms.
- Portfolio/agency template: work proof, services, case detail, team/about, and contact structure.
- Blog/editorial template: content discovery, archive, article detail, author, and subscription structure.

If a proposed structure is short, the agent must explain why the product type genuinely requires a short scope. Otherwise, missing sections/pages are a quality defect, not a premium style choice.

## Figma Reference Structure Gate

When a Figma reference link, Figma frame, Figma template file, or `.fig` source is used:

- Produce a Figma reference schema receipt before section planning.
- Complete the professional template reading order from `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md`.
- Identify observed pages, frames, sections, components, variants, states, and design-system panels.
- Infer the product family and normal marketplace standard before deciding section count.
- Use the reference to understand density rhythm, hierarchy, proof strategy, and editable source logic, not to copy its page order.
- If only a partial frame is visible, add missing standard roles required by the product family instead of shrinking the product to the visible fragment.
- If the standard remains unclear, use taxonomy/corpus/category research or ask one targeted question. Do not default to minimalist.

## Landing Page Structure

- Treat landing page as a specific focused conversion product, not as the default for every website template.
- Standard count is usually 8-12 sections for normal product/service pages and 10-14 for trust-heavy sales or service pages. Narrow campaigns, squeeze pages, waitlists, and micro landing pages may use 6-8 sections only when that small scope is explicit.
- The structure should follow a complete conversion arc: promise, evidence, problem/audience fit, solution or offer detail, mechanism/process, proof, comparison/pricing/package where relevant, objections/FAQ, final CTA, and footer.
- A landing page may be visually simple, but if it lacks proof, objection handling, and conversion closure it is incomplete.
- Cover or marketplace hero preview.
- Website hero with clear value proposition and primary CTA.
- Problem or audience-fit section.
- Benefits and feature blocks with varied composition.
- Product, service, or screenshot preview.
- Social proof, testimonials, logos, or metrics.
- Pricing, package, or offer section when relevant.
- FAQ and final CTA.
- Footer with basic navigation and trust cues.
- Desktop and mobile preview frames.

## Full Website Template Structure

- Homepage with 8-12 content blocks for most business, agency, service, portfolio, or corporate templates.
- When the product is a serious service, SaaS, corporate, marketplace, or trust-heavy website template, use the upper side of the homepage range, usually 10-14 product-specific blocks, because the page must carry strong product evidence.
- Inner page map before visual design: about, service listing, service detail, portfolio/project listing, portfolio/project detail, blog/news listing, blog/news detail, contact, FAQ, pricing, team, auth, account, or error pages as relevant.
- Header/navigation and footer are systems, not decorative afterthoughts.
- Marketplace-ready full-site templates must prove breadth through page variants, section breakdowns, and responsive examples.
- Do not call a homepage-only design a full website template unless the product scope explicitly says single-page website.

## Website Template Corpus Baseline

Local references in `Template Website` show these practical baselines:

- Full business/finance HTML packages can include 30+ content pages plus multiple home variants and RTL variants.
- Agency/portfolio/service templates commonly include 10-15 homepage blocks or partials and 10-20 content pages.
- Ecommerce templates commonly include 15-40+ pages or screens for shop, product detail, cart, checkout, account, wishlist, auth, support, and blog.
- Dashboard/admin templates can include 70+ screens in one layout mode because components, states, tables, forms, apps, and auth are part of the product value.
- Hero/header kits are smaller on purpose, but they must be sold and planned as kits with variants.

## External Web/Product Baseline

Use external research when a product category is unfamiliar or when the requested reference does not clearly show the whole product scope.

- Conversion landing pages commonly include a focused CTA plus supporting elements such as value proposition, benefits/features, social proof/trust signals, form or CTA, objection handling, and final trust reinforcement.
- SaaS and product landing pages commonly use a predictable sales arc: hero/promise, proof, feature or product explanation, testimonial/case proof, pricing/package or demo CTA, FAQ, and footer/final CTA.
- Ecommerce templates are not just homepages. Production-ready examples often include product listing/category, product detail, cart, checkout, account/order, support/returns, FAQ, and related shopping flows.
- If current research shows a richer market standard than local memory, follow the richer standard and record the reasoning in the plan/review.

## FIG Template Corpus Baseline

Decoded local `.fig` references in `Template Website` confirm the same rule at
the design-source level:

- Processed corpus: 26 main `.fig` files, 26 decoded, 0 decode failures.
- File types include raw `fig-kiwi` and ZIP-wrapped `.fig` files with `canvas.fig`, thumbnails, and image assets.
- Strong recurring structure signals include contact, services, navigation, commerce, pricing, portfolio, about, dashboard, hero, mobile, footer, blog, auth, team, testimonial, process, features, FAQ, stats, and gallery.
- Product scope varies widely: hero/header kits, landing pages, full website templates, ecommerce pages, dashboards/UI kits, mobile screens, portfolios/resumes, event/entertainment pages, travel, and technology/SaaS templates.
- Quiet visual style never reduces the required product structure. A clean template still needs the right sections, screens, states, responsive evidence, and marketplace proof for its category.
- Use `.design-brain/evidence/fig-extracts/latest.json` and the latest extraction report when local `.fig` evidence matters.

## Figma Website Template Structure

- Cover frame.
- Design overview frame.
- Full desktop page.
- Mobile page or key mobile sections.
- Section breakdown frames.
- Component or style guide frame.
- Editable content notes or named layers.
- Auto-layout receipt naming major auto-layout groups, reusable components, responsive behavior, and decorative absolute-position exceptions.
- Preview mockup frame for marketplace images.

## Dashboard Template Structure

- App shell with navigation and topbar.
- Overview dashboard with KPI hierarchy.
- Chart and analytics cards.
- Data table with filters, search, sorting, and row states.
- Detail view or side panel.
- Empty, loading, success, warning, and error states.
- Settings/profile/auth screens when relevant.
- Responsive or compact layout example.

## UI Kit And Design System Structure

- Foundations: color, typography, spacing, radius, shadow, icons.
- Components: buttons, inputs, selects, toggles, tabs, cards, modals, tables, nav.
- States: default, hover, active, disabled, focus, loading, error, success.
- Variants: sizes, tones, density, icons, layout options.
- Usage examples and common compositions.
- Documentation notes for naming and reuse.

## Branding Kit Structure

- Cover and brand mood overview.
- Logo or wordmark usage.
- Color palette and accessibility notes.
- Typography pairing and hierarchy.
- Graphic elements, textures, or patterns.
- Social media layouts.
- Stationery or business collateral.
- Mockup presentation frames.

## Presentation Deck Structure

- Slide contact sheet or deck overview frame.
- Cover slide with clear deck category and mood.
- Agenda or table of contents.
- Section divider slide.
- Context, company, or introduction slide.
- Problem or opportunity slide.
- Solution, service, or offer slide.
- Market, audience, or customer insight slide.
- Metric, achievement, or KPI slide.
- Timeline, roadmap, or process slide.
- Chart or table slide with defined data styles.
- Comparison, strategy, or package slide.
- Team, profile, or speaker slide.
- Quote, testimonial, or proof slide.
- Contact, next steps, and closing slide.

## Presentation Deck Design-System Rules

- Define theme colors, heading/body fonts, and type scale.
- Define slide title positions and safe margins.
- Define footer, page number, and section marker rules.
- Define chart palette, table style, legend style, and callout style.
- Define image placeholder treatments: full-bleed, masked, profile, screenshot, gallery, or case-study crop.
- Use auto-layout inside editable groups such as title stacks, bullet groups, metric rows, agenda rows, profile cards, rate cards, chart legends, and contact blocks.
- Check thumbnail readability for every slide.

## Editable Area Rules

- Name editable areas clearly.
- Avoid flattening important text or UI into images.
- For editable source templates, follow `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`: use role-specific text clue placeholders for image zones unless generated images were explicitly requested.
- A reference photo, screenshot, map, or product image should become a clue like `image placeholder: product dashboard screenshot`, not a forced generated image.
- A reference portrait/profile image should become a clue like `profile photo placeholder: founder portrait`, not a generated fake person.
- Keep placeholder data realistic.
- Use component-like repeatable structures.
- Avoid one-off spacing and inconsistent section widths.
- For Figma source templates, use auto-layout for editable sections, stacks, cards, controls, repeated rows, and design-system panels. Absolute positioning is reserved for documented decorative or overlay exceptions.
- Keep brand-specific styling swappable without breaking layout.
