# TypeUI Style Profiles

Use these profiles when the user asks for a specific design mood, when the brief is visually vague, or when the target platform needs a stronger art direction. These are distilled from TypeUI design skills and kept as selection guidance, not full upstream copies.

Primary source: TypeUI design skills registry, `https://www.typeui.sh/design-skills`, and the open-source `bergside/awesome-design-skills` registry.

## Selection Rules

- Start with `Clean`, `Paper`, or `Premium` when the user wants professional polish and does not specify a strong style.
- Use `Bento`, `Perspective`, `Spacious`, or `Dashboard` when information architecture is the hardest part.
- Use `Enterprise`, `Shadcn`, or `Dashboard` for serious B2B software, admin tools, data products, or component-heavy React/Tailwind systems.
- Use `Refined`, `Luxury`, or `Premium` for portfolio, editorial, beauty, fashion, high-end commerce, and premium service work.
- Use `Storytelling` for decks, launch pages, case studies, tourism, education, and narrative product pages.
- Use `Bold`, `Neobrutalism`, or `Glassmorphism` only when the brand needs expressive energy and the accessibility risks can be controlled.

## Worth-It Profiles

### Clean

Default for clarity-heavy products. Use minimal surfaces, whitespace, readable typography, semantic color, and restrained motion. Best for dashboards, docs, admin panels, productivity tools, and SaaS.

### Paper

Default for tactile calm. Use print-inspired cards, soft layering, subtle shadows, generous whitespace, and restrained color. Strong for reports, knowledge bases, portfolio grids, documentation, and PowerPoint-style narrative decks.

### Bento

Default for modular scannability. Use self-contained blocks with varied sizes, consistent gaps, and a logical reading order. Strong for feature sections, dashboards, metric groups, product overviews, and landing-page proof sections.

### Spacious

Default for breathing room. Use generous whitespace, consistent padding, readable sections, and calm rhythm. Strong for service pages, decks, documentation, premium landing pages, and content that should feel unhurried.

### Dashboard

Default for data products. Use modular grids, strong data hierarchy, purposeful density, chart accessibility, dark or light modes with tested contrast, and complete empty/loading/error states.

### Enterprise

Default for B2B workflow tools. Use high contrast, structured layout, predictable controls, comfortable density, clear workflow affordances, and practical interaction patterns such as drag/drop only when they improve task speed.

### Premium

Default for quiet high-end software. Use content over chrome, neutral surfaces, precise spacing, subtle interaction states, and medium-weight typography. Strong for productivity, finance, developer platforms, and premium SaaS.

### Refined

Default for editorial authority. Use serif-forward headings, restrained color, larger vertical rhythm, and typographic hierarchy. Strong for luxury commerce, portfolios, editorial platforms, premium services, and creative agencies.

### Luxury

Default for dark high-end brand presence. Use monochrome contrast, bold headings, sparse content, and dramatic whitespace. Strong for fashion, jewelry, watches, high-end portfolios, and premium hero pages.

### Perspective

Default for spatial hierarchy. Use layered surfaces, elevation, shadow, and contrast to explain what is foreground, background, and interactive. Useful for dashboards, ecommerce product pages, and workflow tools where depth clarifies hierarchy.

### Shadcn

Default for React/Tailwind component systems. Use monochrome surfaces, utility-first tokens, explicit component anatomy, and Radix-like state discipline. Strong for forms, settings, admin tools, dashboards, and SaaS panels.

### Storytelling

Default for narrative journeys. Sequence the interface like a story: context, tension, reveal, proof, action. Strong for launch pages, pitch decks, event pages, case studies, education, tourism, and brand storytelling.

### Bold

Use when the page needs immediate impact. Build big typography, high contrast, decisive sections, and unmistakable CTAs. Keep body text and layout discipline restrained so the result stays usable.

### Neobrutalism

Use for playful anti-corporate energy. Apply hard edges, thick outlines, flat blocks, and high contrast. Avoid for finance, healthcare, enterprise, or any sober trust-heavy workflow.

### Glassmorphism

Use sparingly for depth and ambience. Apply translucent panels over controlled backgrounds with solid fallback surfaces. Never let transparency reduce readability, form clarity, or chart contrast.

## Cross-Platform Translation

- Figma: turn the selected profile into variables and component variants before composing screens.
- PowerPoint: translate the profile into slide masters, title/body scale, image treatment, chart style, and section layouts.
- Web/CSS: translate the profile into CSS variables, responsive grid rules, component states, and motion defaults.
- WordPress: translate the profile into `theme.json`, block patterns, reusable template parts, and editor-safe spacing.

## Profile Search

Use the searchable CSV when choosing a profile:

```bash
python <skill-dir>/scripts/search.py "premium saas dashboard finance" --domain typeui -n 3
python <skill-dir>/scripts/search.py "narrative pitch deck launch story" --domain typeui -n 3
python <skill-dir>/scripts/search.py "react tailwind component system forms" --domain typeui -n 3
```
