---
name: design-craft
description: Cross-platform design intelligence for creating, critiquing, and refining polished templates, UI screens, visual systems, and implementation-ready design specs. Use when Codex designs or improves Figma screens, PowerPoint decks, web templates, WordPress themes, CSS/Tailwind systems, dashboards, landing pages, product pages, forms, charts, branding, typography, color palettes, TypeUI-inspired style profiles, component states, responsive layouts, accessibility, or visual handoff.
---

# Design Craft

Version: v0.3.0

Use this skill to raise the craft quality of any visual or UI deliverable. Treat it as a design director plus implementation partner for tokens, components, accessibility, interaction, and polish. When Brain Design / Codex-Design context exists, this skill is a support layer, not the primary decision brain.

## Craft Tool Adapter

Design Craft v0.3.0 exposes `scripts/craft_adapter.py` for Brain Design runtime. The adapter returns JSON craft support and blocks any attempt to override Brain Design route, product family, mode, structure, cognition, simulation verdict, layout audit, post-build status, or final readiness.

## Design Craft Role

Design Craft must not override Brain Design. If Brain Design / Codex-Design context exists, defer to:

1. Brain Design intent routing.
2. Brain Design product family.
3. Brain Design reference insight.
4. Brain Design section/screen depth lock.
5. Brain Design structural reconfiguration.
6. Brain Design originality/similarity gate.
7. Brain Design marketplace quality gate.

Design Craft may help with color tokens, typography pairing, spacing scale, component states, accessibility, UI polish, platform handoff, design-system consistency, UX checklist, interaction notes, and component anatomy. It must not decide final template structure when Brain Design already defines it.

Forbidden behavior:

- Do not replace Brain Design structure with `Hero + Features + CTA`.
- Do not reduce a full website template to 3-5 sections.
- Do not default to minimalism or flat design.
- Do not use generic clean SaaS scaffold for every niche.
- Do not treat dashboard/app/admin products as landing pages.
- Do not override reference-led art direction with conservative defaults.

## Support-Layer Contract

Design Craft is not the decision brain.

When Brain Design context exists, Design Craft must defer to:

1. Brain Design intent router.
2. Brain Design product family.
3. Brain Design reference insight.
4. Brain Design style DNA extraction.
5. Brain Design visual mood reinterpretation.
6. Brain Design structural reconfiguration.
7. Brain Design section/screen/module depth lock.
8. Brain Design similarity/originality gate.
9. Brain Design marketplace quality gate.

Design Craft may provide typography system, color roles, spacing scale, component anatomy, component states, accessibility checklist, responsive behavior notes, interaction/microcopy hints, UI polish, token suggestions, and platform handoff notes.

Design Craft must not replace Brain Design structure, reduce full website templates to short landing pages, force generic minimal design, treat every product as SaaS, treat dashboard/app/deck as landing page, apply `Hero + Features + CTA` as a universal skeleton, or output generic Inter + blue + cards as default identity.

## Mode Priority

Design Craft must detect output mode before product/niche pattern.

Priority order:

1. Brain Design explicit output contract if present.
2. Dashboard/admin/app/deck/email/static/brand/menu/social/UI kit explicit intent.
3. Landing page explicit intent.
4. Website/full template intent.
5. Fallback standalone safe mode.

Landing intent should use `MODE: landing` while preserving the niche family, such as finance consulting or restaurant hospitality. Presentation/PPTX/Google Slides/Keynote intent must use presentation slide-system coverage, not website sections. Brand, menu, social, poster/static, UI kit, component library, and design system intents must not output website section flow.

## Anti-Scaffold Enforcement

If the anti-scaffold gate fails, Design Craft must not persist or present the failed output as usable. It must attempt one auto-repair pass, rerun the gate, and either output the repaired PASS result or block with `Output blocked: anti-scaffold gate failed.` Failed output may only be printed with an explicit debug flag and must remain marked unsafe.

## JSON Safety

When returning machine-readable search results, restricted legacy patterns must carry safety metadata: `is_restricted`, `safety_scope`, `risk_level`, `allowed_when`, `forbidden_when`, `recommended_replacement`, and `brain_design_note`.

## Payload Safety Rule

Design Craft must not pass an output simply because the mode/family is correct. The full payload must be mode-compatible: style name, keywords, effect language, key effects, checklist, accessibility notes, component specs, and persisted output must all match the detected mode.

## Mode-Specific Craft Rule

Each mode has its own style language, effect language, checklist, and output anatomy. Presentation, email, menu, social, static canvas, brand kit, dashboard, mobile app, UI kit, component library, and design system outputs must use their own structure and validation rules instead of inheriting generic web behavior.

## Non-Web Mode Rule

The static `presentation` mode, email, menu, social, static canvas, and brand kit outputs must not use web interaction language such as scroll-triggered effects, sticky positioning, hover behavior, or web breakpoint checklists unless the user explicitly asks for an interactive web artifact. The static `presentation` mode covers PPTX, PowerPoint, Google Slides, and Keynote artifacts, and it keeps this restriction in full.

The `web_deck` mode is a web mode, not a non-web mode. Runtime, motion, and stage vocabulary is legal there because the artifact is a browser-rendered deck: stage scale, slide transitions, reveal choreography, keyboard and pointer navigation, deep links, and reduced-motion fallback are required payload language, not leakage. `web_deck` is governed by `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`, which owns stage and runtime fidelity. It is still not a website mode: the stage is a fixed frame, so long-scroll section vocabulary and static-export vocabulary both stay forbidden there. This grants Design Craft no new authority. Per `.design-brain/DESIGN_CRAFT_NON_OVERRIDE_CONTRACT.md` it remains a support layer and must not route a request into `web_deck`, out of the static `presentation` mode, or past the stage gate.

## Auto-Repair Rule

Auto-repair must replace the entire invalid payload. Renaming the style is not sufficient. Repair must replace keywords, layout behavior, visual depth, effect language, key effects, best-for notes, accessibility notes, checklist, and mode compatibility before the anti-scaffold gate can pass.

## Brain Design Rule

When Brain Design context exists, Design Craft remains support layer only. It must not override Brain Design structure, reference insight, originality, section depth, or product family decisions.

## Medium Action Model

Design Craft must not use website conversion/CTA language for every output. Each mode has its own action model:

- Dashboard: workflow, primary user task, data hierarchy, filters, and state coverage.
- Presentation: slide narrative outcome, audience argument, closing slide, and data readability.
- Email: email-safe CTA block, client compatibility, mobile stack, unsubscribe/legal footer, and alt text.
- Menu design: category hierarchy, item/price readability, print/digital use, and scan path.
- Social post: hook, crop safety, aspect ratio, carousel rhythm, and export cue.
- Brand kit: logo usage, clearspace, typography pairing, color roles, and applications.
- Static canvas: visual hierarchy, safe margin, focal point, export clarity, and print/readability.
- UI kit/component library/design system: tokens, components, states, variants, naming, and accessibility behavior.

## Raw Payload Sanitization

Raw search or corpus fields must be sanitized before becoming design-system output. A matching row from landing/product data is not automatically valid for every medium. Non-web modes must not inherit landing CSV fields such as conversion focus, CTA placement, contact-sales flows, logo carousel patterns, tab switching, web sections, or generic bottom-section notes.

## Gate Rule

Anti-scaffold PASS requires all payload fields to be mode-compatible: style, keywords, effects, best_for, conversion, CTA, action model, checklist, and persisted markdown. A correct mode/family label is not enough.

## Static / Collateral / Document Safety

Design Craft must not treat all design requests as websites. If the user asks for brochure, flyer, poster, banner, thumbnail, invoice, resume, order ticket, receipt, menu, social post, or brand identity, Design Craft must switch to the appropriate non-web mode and sanitize any raw website or landing metadata before output.

## Social Format Safety

Social carousel, Instagram story, social banner, feed post, carousel post, and reels cover requests are social/static outputs, not websites. Keep restaurant, finance, fashion, or other domains as domain context while using `social_post` as the output mode.

## Collateral and Document Priority

Letterhead, price list, table tent, catalog, lookbook, invoice, resume, ticket, receipt, brochure, poster, flyer, banner, and thumbnail must never be forced into website mode. Detect the medium first, then preserve niche/domain as supporting context.

## Catalog / Lookbook Distinction

Catalog and lookbook are browsing/editorial collateral by default. Do not treat them as ecommerce websites unless the user explicitly asks for a website, shop, cart, checkout, storefront, or ecommerce page experience.

## Cover / Card / Voucher / Label Safety

Cover, voucher, coupon, gift card, loyalty card, sticker, postcard, certificate, booklet, packaging label, label, price tag, and hang tag are non-web collateral modes by default. They must not inherit landing conversion fields, website sections, Contact Sales/Login flows, or ecommerce cart/checkout language unless the user explicitly asks for a website/ecommerce page.

## Tag / Label Distinction

Price tags and hang tags are retail/print collateral, not ecommerce websites. Packaging labels and product labels are print/package systems, not website pages. Fashion, coffee, restaurant, or finance terms should be preserved as domain context, not used to override the medium.

## Non-Web Family Labels

For non-web modes, do not show `full_website_template` as the visible fallback family. Use mode-specific fallback family labels such as `generic_email_newsletter`, `generic_presentation_deck`, `generic_static_canvas`, `generic_invoice_template`, or `generic_resume_template`, and preserve product/niche as separate domain context.

## Export Reliability

Package export must be bounded by timeout, progress logging, and fail-fast behavior. A package export should print each step and each manual edge query, terminate hanging manual checks, report the exact query/command that caused failure, and never hang silently.

## Fast Workflow

1. Identify the medium: Figma, PowerPoint, web app, static HTML/CSS, WordPress, mobile/native, dashboard, document template, or brand asset.
2. Extract the brief: audience, domain, primary task, brand mood, content density, constraints, existing assets, and success criteria.
3. Query the design corpus unless the task is tiny or the user has already supplied a full design system.
4. Convert the findings into concrete tokens: color, type, spacing, radius, shadow, grid, component states, motion, and imagery.
5. Build or edit the artifact in the native toolchain. Preserve existing project conventions when working in a repo.
6. Validate the result against the quality rubric before final response.

Ask only when missing information would cause visibly wrong work. Otherwise, choose a domain-appropriate direction with enough visual identity, section depth, and marketplace-level art direction.

## Codex-Design Design-Anything Layer

When working inside a Codex-Design / Brain Design repository, detect the repository root by checking for one or more of: `.design-brain/`, `AGENTS.md`, `scripts/design_brain_module_select.py`, `scripts/design_brain_router_smoke_test.py`, or `PACKAGE_MANIFEST.generated.json`.

Do not assume the repository lives at a specific local path. Do not hardcode personal machine paths. If the repo root is unclear, operate relative to the current working directory and report uncertainty. If Brain Design files are present, Design Craft must switch to support-layer mode automatically.

When the repo-local selector exists, use it before choosing style:

```bash
python scripts/design_brain_module_select.py --task "..." --template-type "..." --niche "..." --target-buyer "..." --visual-mood "..." --dry-run
```

Treat `open-design` and `awesome-claude-skills` as selective-index references, not bulk content to copy. The selector should choose craft modules, seed pack, direction pack, and validators first; then style profiles can refine the visual mood.

Design Craft is allowed to translate Brain Design output into tokens, component rules, accessibility notes, state coverage, and implementation guidance. It is not allowed to flatten a reference-led template into a universal landing scaffold.

## Design Corpus

This skill includes the UI/UX Pro Max corpus and a small designer rules reference. Use the corpus as a searchable design memory, not as a substitute for judgement.

Run from any shell, replacing `<skill-dir>` with this skill folder:

```bash
python <skill-dir>/scripts/search.py "saas analytics dashboard professional" --design-system -p "Project Name" -f markdown
python <skill-dir>/scripts/search.py "premium saas dashboard finance" --domain typeui -n 3
python <skill-dir>/scripts/search.py "pricing conversion testimonial" --domain landing -n 3
python <skill-dir>/scripts/search.py "focus keyboard aria labels" --domain web -n 3
python <skill-dir>/scripts/search.py "responsive layout form states" --stack html-tailwind -n 3
```

Use `python` on Windows if `python3` points to the Microsoft Store alias.

### Domains

- `product`: product-type recommendations.
- `style`: visual styles, effects, implementation checklist, design variables.
- `color`: palettes by product category.
- `typography`: font pairings and CSS imports.
- `landing`: section order and conversion patterns.
- `chart`: chart choice, color guidance, accessibility.
- `ux`: interaction and usability issues.
- `web`: ARIA, focus, semantics, keyboard, forms.
- `react`: React and Next.js performance concerns.
- `icons`: icon library, import, and usage patterns.
- `typeui`: TypeUI-inspired style profile selector for Clean, Paper, Bento, Spacious, Dashboard, Enterprise, Premium, Refined, Luxury, Perspective, Shadcn, Storytelling, Bold, Neobrutalism, and Glassmorphism.

### Stacks

Use stack search when implementation details matter: `html-tailwind`, `react`, `nextjs`, `vue`, `nuxtjs`, `nuxt-ui`, `svelte`, `astro`, `shadcn`, `swiftui`, `react-native`, `flutter`, or `jetpack-compose`.

For Figma, PowerPoint, WordPress, or generic CSS, run `--design-system` plus domain searches for style, typography, color, UX, web, chart, or landing as relevant.

## Style Profiles

Read [typeui-style-profiles.md](references/typeui-style-profiles.md) when the brief needs stronger art direction or the user asks for a mood such as clean, paper, bento, premium, refined, enterprise, shadcn, storytelling, bold, neobrutalism, or glassmorphism.

Default profile selection:

- Use `Clean`, `Paper`, or `Premium` for professional polish when no strong style is requested.
- Use `Bento`, `Perspective`, `Spacious`, or `Dashboard` when layout, scanability, or information architecture is the hard part.
- Use `Enterprise`, `Shadcn`, or `Dashboard` for serious B2B tools, data products, and React/Tailwind component systems.
- Use `Refined`, `Luxury`, or `Premium` for editorial, portfolio, beauty, fashion, high-end commerce, and premium service work.
- Use `Storytelling` for decks, launches, case studies, tourism, education, and narrative product pages.
- Use `Bold`, `Neobrutalism`, or `Glassmorphism` only when expressive brand energy is more important than quiet productivity, and verify contrast carefully.

Minimalism, minimal, or flat design may only be used when the user explicitly asks for it, the reference clearly has that visual DNA, or Brain Design marks it as intended style. Otherwise, Design Craft must prefer reference-led visual identity, product-specific composition, and marketplace-ready art direction.

Forbidden defaults:

- Do not choose `Inter + blue + cards + Hero + Features + CTA` as a universal fallback.
- Do not use empty words like clean, modern, or premium unless they are explained with concrete visual decisions.
- Do not output only 3-5 sections for a full website template.
- Do not treat every product as SaaS.

## Style DNA and Reinterpretation

Style DNA means typography behavior, layout rhythm, color role, image direction, spacing density, shape language, effect language, and premium signal.

Reinterpretation visual mood means preserving emotional direction and market positioning while changing composition, palette behavior, asset treatment, hierarchy, depth, and emphasis. Do not copy the surface layout.

Structural reconfiguration means rebuilding section order, hero grammar, grid system, content rhythm, CTA placement, and component layout so the reference insight becomes a new original template direction.

When a reference is provided, Design Craft supports Brain Design by translating style DNA into tokens and component guidance, not by copying structure.

## Platform Translation

Read [platform-playbook.md](references/platform-playbook.md) when the target is Figma, PowerPoint, WordPress, CSS/Tailwind, dashboards, charts, branding, or multi-platform handoff.

Core translation rules:

- Figma: create variables/tokens first, then components, variants, states, and composed screens.
- PowerPoint: treat slides as a visual system with masters, reusable layouts, type scale, image rules, and chart styles.
- Web/CSS: express tokens as CSS variables or framework theme values, then implement responsive layout and interaction states.
- WordPress: map design decisions to theme.json, block patterns, template parts, reusable CSS, and editor-safe spacing.
- Dashboards: prioritize scanability, density, comparison, filtering, empty/loading/error states, and accessible charts.
- Branding: verify logo simplicity at small sizes, one-color usage, dark/light variants, and consistent applications.

## Quality Rubric

Before delivering, check:

- Purpose: the primary user action is visually obvious in the first viewport or first slide.
- Hierarchy: one focal point per screen/slide; secondary content supports it instead of competing.
- Layout: consistent grid, alignment, whitespace, and container widths; no nested decorative cards.
- Typography: readable body size, clear scale, sane line length, no viewport-width font scaling.
- Color: accessible contrast, restrained palette, purposeful accent, no one-note color theme.
- Components: all expected states exist: default, hover, active, focus, disabled, loading, error, empty.
- Interaction: clickable elements look clickable, focus is visible, motion is subtle and respects reduced motion.
- Assets: real or relevant imagery where the medium needs visual inspection; icons come from a consistent set.
- Responsiveness: verify mobile, tablet, and desktop constraints; text must not overflow or overlap.
- Handoff: name tokens by function, document when to use components, and include platform-specific implementation notes.

## Output Shape

When the user asks for design work, produce or implement concrete artifacts, not vague advice. If code or file edits are possible, make the edits. If the deliverable is a design spec, include tokens, layout rules, component/state specs, accessibility notes, and validation criteria.

For critiques or reviews, lead with the highest-impact visual and UX issues, then give direct fixes.
