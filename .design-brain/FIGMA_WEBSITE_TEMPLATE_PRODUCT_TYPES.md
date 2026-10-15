# Figma Website Template Product Types

Use this taxonomy before planning any Figma website template. The goal is to stop treating every website brief as a landing page. A landing page is only one product family.

## Routing Rule

- Expand Indonesian and mixed-language prompts through `.design-brain/ROUTING_ALIASES_ID.json` before scoring.
- Product-specific cues override generic `template website`, `website template`, or `web template` wording.
- Generic website triggers are low-score fallback only.
- If the brief explicitly says landing page, lead generation, campaign page, sales page, squeeze page, or waitlist page, use the landing-page standard.
- If the brief says website, website template, web template, homepage template, SaaS website, business website, agency website, service website, ecommerce, dashboard, portfolio, blog, docs, education, community, event, travel, or similar without explicit landing-page language, choose the matching website product family below.
- If the niche is unclear, default to Multipurpose / Full Website Template, not Landing Page.
- If the standard for a product family is uncertain, do web/category research before deciding structure.
- Before assuming structure from memory, use `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md` and `.design-brain/REFERENCE_CORPUS_CONFIG.md` to select references that match the product family. If no local candidates are found, do not claim local-reference-led selection happened.

## Indonesian Alias Examples

- `template website restoran` -> Event / Venue / Travel / Hospitality Website.
- `template website keuangan` -> Corporate / Business Website.
- `template website sewa alat` -> Professional Service / Local Booking Website.
- `template website perhiasan ecommerce` -> Ecommerce / Storefront Template.
- `template website properti` -> Marketplace / Listing / Directory Website.
- `template website kursus online` -> Education / Course / LMS Website.
- `template website blog editorial` -> Editorial / Blog / CMS Website.
- `developer docs website` -> Documentation / Help Center / Developer Docs.
- `admin dashboard web app` -> Dashboard / Admin / Web App Template.

## Count

Design Brain recognizes 16 practical Figma website-template product families:

1. Multipurpose / Full Website Template
2. Landing Page / Campaign Page
3. SaaS / Product Marketing Website
4. Corporate / Business Website
5. Professional Service / Local Booking Website
6. Agency / Studio Website
7. Personal Portfolio / Resume / Case-Study Site
8. Ecommerce / Storefront Template
9. Marketplace / Listing / Directory Website
10. Editorial / Blog / News / CMS Website
11. Education / Course / LMS Website
12. Documentation / Help Center / Developer Docs
13. Dashboard / Admin / Web App Template
14. Community / Nonprofit / Membership Website
15. Event / Venue / Travel / Hospitality Website
16. Utility Pages / Coming Soon / Error Kit

## Standards By Type

### 1. Multipurpose / Full Website Template

Standard:
- 10-14 homepage blocks.
- Inner page map with at least 5 usable page types.
- Design-system notes for color, typography, spacing, buttons, forms, cards, navigation, footer, and editable areas.

Expected structure:
- Header/navigation, hero, trust/proof, audience/problem, product/service overview, feature/service depth, process/workflow, proof/case/gallery, pricing/package/comparison, testimonials/authority, FAQ/objections, lead/contact CTA, footer, inner page map, design-system overview.

### 2. Landing Page / Campaign Page

Standard:
- 6-8 sections for narrow campaigns only when the brief explicitly asks for narrow campaign, squeeze page, waitlist page, micro landing page, or one focused conversion asset.
- 8-12 sections for normal product/service offers.
- 10-14 sections for trust-heavy sales pages.

Expected structure:
- Hero with one CTA, credibility/proof cue, problem/audience fit, offer or solution detail, benefits/features, mechanism/process, social proof, pricing/package/form, FAQ/objection handling, final CTA, footer.

Guard:
- Only use this type when landing/campaign/sales/lead-gen intent is explicit.

### 3. SaaS / Product Marketing Website

Standard:
- 10-14 homepage blocks.
- Pages: features, use cases, pricing, integrations, customers/case studies, resources/blog, security or docs, contact/demo, auth/utility.

Expected structure:
- Product promise, UI preview, customer proof, use-case framing, feature depth, workflow/integration, reliability/security, case proof, pricing/demo CTA, FAQ, resources, footer.

Typical routing cues:
- saas, AI SaaS, SaaS website, software website, app website, product website, startup website, platform website, AI platform, tech product.

### 4. Corporate / Business Website

Standard:
- 9-13 homepage blocks.
- Pages: about, services, service detail, case studies, team, careers/news, contact, legal/utility.

Expected structure:
- Company positioning, trust metrics/logos, company overview, services/capabilities, industry fit, process/method, case/results proof, leadership/team, news/resources, compliance/FAQ cue, contact.

### 5. Professional Service / Local Booking Website

Standard:
- 10-14 homepage blocks.
- Pages: services, service detail, pricing/packages, booking/contact, testimonials, locations, FAQ, policy/utility.

Expected structure:
- Booking CTA, ratings/trust, service categories, audience pain, service detail preview, booking process, packages/pricing, testimonials/results, availability/locations, guarantee/FAQ, contact form.

### 6. Agency / Studio Website

Standard:
- 9-12 homepage blocks.
- Pages: work index, case study detail, services, about/team, blog/insights, contact, utility/error.

Expected structure:
- Agency positioning, selected work, service/capability overview, case-study spotlight, process/approach, client proof, team/culture, engagement model, insights, contact.

### 7. Personal Portfolio / Resume / Case-Study Site

Standard:
- 7-10 homepage blocks.
- Pages: work index, case study detail, about/resume, contact, utility/error.

Expected structure:
- Role and proof, selected work, case-study preview, skills/services, about narrative, experience/credentials, social proof, contact.

### 8. Ecommerce / Storefront Template

Standard:
- 10-14 homepage modules.
- Flows: category/product listing, product detail, search/filter, cart, checkout, account/orders, wishlist, support/returns, policy/utility.

Expected structure:
- Cart/search navigation, category discovery, product grid, product detail preview, reviews, offer/promo, shipping/returns trust, wishlist/account cues, newsletter/loyalty, support, footer.

### 9. Marketplace / Listing / Directory Website

Standard:
- 10-14 homepage/modules.
- Flows: listing index, listing detail, search/filter results, map/compare, saved/favorites, inquiry/booking, account/profile, support/FAQ.

Expected structure:
- Search-first hero, category/location discovery, featured listings, filter/sort preview, map or compare, detail preview, credibility/trust, how it works, reviews, listing/inquiry CTA.

### 10. Editorial / Blog / News / CMS Website

Standard:
- 8-12 homepage modules.
- Pages: category/archive, article detail, author profile, search results, newsletter/subscribe, about, contact, utility/error.

Expected structure:
- Editorial hero/top story, category rail, featured grid, latest/trending feed, newsletter CTA, author/column module, topic/archive discovery, sponsor/product cue, publication trust.

### 11. Education / Course / LMS Website

Standard:
- 10-14 homepage modules.
- Pages: course catalog, course detail, lesson preview, instructor profile, pricing/enroll, student dashboard/progress, FAQ/support, contact.

Expected structure:
- Learning promise, course/category discovery, featured courses, outcomes/skills, curriculum preview, instructor proof, learning process, pricing/enrollment, results/testimonials, FAQ/support.

### 12. Documentation / Help Center / Developer Docs

Standard:
- 7-11 core screens/pages.
- Pages: docs home, category, article detail, search results, API/reference, changelog, support/contact, utility/error.

Expected structure:
- Search-first docs home, quick-start cards, category navigation, popular articles, article layout preview, API/reference or changelog, support CTA.

### 13. Dashboard / Admin / Web App Template

Standard:
- 8-12 screens minimum for small products.
- Larger admin kits need many more screens, states, tables, forms, auth, permissions, and settings.

Expected structure:
- App shell/navigation, overview dashboard, KPI cards, charts, data table/list, filters/search/sort, detail drawer/page, create/edit form, settings/profile, notifications/activity, empty/loading/error states, auth/permission screens.

### 14. Community / Nonprofit / Membership Website

Standard:
- 9-13 homepage blocks.
- Pages: about/mission, programs/causes, donate/join, events, stories, volunteer/membership, contact, FAQ/utility.

Expected structure:
- Mission hero, impact metrics, program/cause overview, story proof, events/community, donation/join CTA, volunteer/member benefits, partners/testimonials, FAQ/support.

### 15. Event / Venue / Travel / Hospitality Website

Standard:
- 10-14 homepage blocks.
- Pages: schedule or amenities, listing/detail, booking/reservation, gallery, pricing/tickets, FAQ/policies, contact/location, utility/error.

Expected structure:
- Date/place/booking hero, rating/trust cue, experience/venue overview, schedule/amenities, room/ticket/menu/package preview, gallery, pricing/availability, reviews, policy/FAQ, booking CTA.

### 16. Utility Pages / Coming Soon / Error Kit

Standard:
- 3-6 pages or states.
- This is intentionally small and must not be sold as a full website template.

Expected structure:
- Coming soon/waitlist, 404/error, maintenance/status, thank-you/success, newsletter/form state, footer/legal.

## Hard Gates

- Do not choose Landing Page unless the brief explicitly says landing page or campaign-style intent.
- Do not use a visual reference to infer product type lazily. Identify the actual product family first.
- Do not plan website-template structure from assumption when `Template Website` contains relevant product-family previews. Select local evidence first.
- Do not judge product readiness only by the homepage. Check page map, screen states, reusable modules, and design-system scope.
- If a product family normally includes flows, such as ecommerce checkout or dashboard states, those flows are required even when the visual style is clean.
- Desktop-only is not a persistent default restriction. Decide responsive/device deliverables from the current request, product category, marketplace standard, and buyer value.

## External Research Baseline

Use these as category evidence when product-family standards are uncertain:

- Figma dashboard templates show dashboards as kits with widgets, statistics, styles, symbols, sign-in/profile pages, analytics, CRM, sales, healthcare, and other dashboard-specific structures: https://www.figma.com/templates/dashboard-designs/
- Webflow template categories separate Blog & Editorial, Community & Nonprofit, Documentation, Education, Personal/CV, Portfolio & Agency, Professional Services, Real Estate, Retail & E-Commerce, Technology, Travel, UI Kit, Weddings & Events, and more: https://webflow.com/templates/categories
- ThemeForest website templates are split across Site Templates, WordPress, UI Templates, Template Kits, eCommerce, Marketing, CMS Themes, Blogging, Courses, Forums, and marketplace/directory examples: https://themeforest.net/category/all
- Figma website template marketplaces list landing pages, SaaS websites, ecommerce UI kits, portfolio websites, blog/news templates, admin dashboards/web apps, mobile app UI, and coming soon/404 pages as separate template categories: https://figmawebsitetemplates.com/
- Ecommerce research emphasizes that stores require more than one page: homepage, category/product listing, product detail, cart, checkout, about/contact, returns/support, trust, search, and navigation: https://www.liquidweb.com/ecommerce/design/
- SaaS website examples commonly include multi-page product stories with features, pricing, case studies, integrations, blog/resources, FAQ, contact/demo, and 404 pages: https://sebadam.supply/templates/ignite
- Help centers use information architecture such as Home > Categories > Sections > Articles, so docs templates need category/article/search structures rather than generic marketing sections: https://support.zendesk.com/hc/en-us/articles/4408893893018-Workflow-Display-an-article-or-section-in-multiple-sections-or-categories
- Admin dashboards commonly include dashboard variants, CRUD/list pages, settings, auth flows, error pages, components, charts, tables, filters, and UI patterns: https://www.tailawesome.com/resources/flowbite-admin-dashboard
