# Effect Language Judgment

## Purpose

- Mencegah design output menjadi flat, generic, safe-clean, atau decorative-only.
- Menilai apakah gradient, blur, glass, shadow, lighting, texture, pattern, depth, dan motion-implied effects punya fungsi desain.

Use this file when designing or reviewing templates from visual references. The goal is to make Aibo more flexible and art-directed with effects, without becoming decorative or copying a reference.

## Core Rule

Effects are not mandatory, and absence of effects is not automatically a weakness.

Effects are tools for hierarchy, depth, polish, separation, tactility, focus, trust, and mood. Use them only when they make the template feel more premium, clearer, or more reusable.

For batch templates, effect and gradient exploration is mandatory as a decision process even when the final answer uses restraint. The agent must not skip effects/gradients by saying the design is minimalist. It must inspect whether effects, gradients, or surface depth can create a more distinct visual language and reduce similarity risk without making the design noisy.

## Judgment Axes

### 1. Semantic Role

- Effect must support hierarchy, focus, grouping, product meaning, brand tone, or conversion path.
- Decorative effects without function should be reduced or replaced.

### 2. Surface Depth

- Check foreground, midground, and background.
- Check card elevation, image treatment, container depth, and interaction affordance.

### 3. Gradient Logic

- Gradient must have a role: ambient, CTA, hero energy, product glow, data emphasis, luxury depth, or editorial mood.
- Random gradient blobs that do not connect to structure are forbidden.
- Gradients may also separate templates in a batch when they are tied to product meaning, material, lighting, or CTA hierarchy; they are not a substitute for layout repair when structure is similar.

### 4. Lighting Logic

- Lighting must be consistent with art direction.
- Avoid AI-looking glow or neon without a product/niche reason.

### 5. Texture / Pattern Logic

- Texture and pattern may support premium signal, editorial rhythm, niche identity, or visual separation.
- Generic pattern that only fills empty space fails the gate.

### 6. Flatness Detection

- Fail if all sections/cards have the same depth, spacing, and visual rhythm.
- Fail if there is no art-direction fingerprint.
- Fail if the template feels like a default SaaS clean scaffold.

### 7. Product-Family Adaptation

- Ecommerce: product/media emphasis, trust surface, catalog rhythm.
- Finance: confidence, clarity, professional depth.
- Restaurant/hospitality: atmosphere, appetite, venue emotion.
- Agency/portfolio: expressive composition and case-study rhythm.
- Dashboard: data clarity, states, module hierarchy.
- Presentation: slide energy, contrast, system consistency.

### 8. Gate Output

- PASS/FAIL.
- Failure reason.
- Affected sections/screens.
- Required action: rebuild, recompose, recolor, retype, or re-depth.

## Reference Effect Reading

When studying a reference, inspect the effect layer:

- Drop shadows and elevation.
- Inner shadows or inset panels.
- Glow, bloom, or signal light.
- Background blur, glass, or translucent overlays.
- Gradient washes or soft lighting.
- Hairline borders, dividers, and edge highlights.
- Image overlays, scrims, and darkening layers.
- Surface depth between cards, panels, modals, and hero objects.

Identify what each effect is doing:

- Separating content from background.
- Making a CTA or product object feel touchable.
- Creating premium softness.
- Creating technical signal or futuristic energy.
- Making cards readable over imagery.
- Turning a flat placeholder into a credible replaceable media zone.
- Creating a stronger section transition.

## Flexible Reinterpretation

Do not copy a reference's effect values, exact shadow shape, blur intensity, glow color, or surface treatment.

Instead, translate the function into a new effect system that fits the new template:

- `Shadow/Soft card` for calm editorial or service templates.
- `Shadow/Floating panel` for booking forms, dashboards, purchase panels, and hero objects.
- `Glow/Signal` for AI, developer, analytics, event, or technology templates.
- `Overlay/Image scrim` for photo-led heroes or readable media placeholders.
- `Border/Hairline depth` for premium restrained cards that should not feel heavy.
- `Inset/Operational surface` for dashboards, control rooms, finance, rental, or admin templates.

## Premium Without Reference Effects

If a reference has little or no visible effect but still feels premium, do not blindly keep the rebuild flat.

Ask:

- Would a subtle effect improve depth without changing the mood?
- Would a light shadow or border make editable cards easier to understand?
- Would a glow or surface highlight make the hero/action more memorable?
- Would no effect be stronger because the layout relies on typography, image, or whitespace?
- Would the effect make the template more marketplace-ready or just busier?

If the answer improves polish, add a restrained, original effect system. If it adds noise, keep the design flat and premium.

## Figma Design System Rule

When effects are used in a Figma template, add semantic effect styles when possible:

- `Effect/Soft card shadow`
- `Effect/Floating panel`
- `Effect/Signal glow`
- `Effect/Image overlay`
- `Effect/Hairline depth`

Apply effects only to surfaces that need them, such as:

- Hero product panels.
- Booking/search/form panels.
- Product cards.
- Dashboard or console cards.
- CTA sections.
- Image/media placeholders.
- Premium testimonial or quote panels.

Do not apply effects everywhere. One or two effect roles are often enough.

## Batch Autopilot Rule

For multiple-template or batch design work, effect language is a mandatory design decision, not an optional polish request. The user should not need to mention effects, gradients, glow, blur, overlays, or shadow depth.

For each template in a batch, define an effect-language fingerprint before building:

- Reference effect reading: what the selected reference uses or deliberately avoids.
- New semantic effect roles: named by function, not by copied visual value.
- Gradient logic: where gradients appear, what hierarchy or material role they serve, and what zones stay flat.
- Surface depth: which surfaces are flat, raised, inset, glass, editorial, tactile, technical, or deliberately restrained.
- Focal-object treatment: how the hero, product, CTA, form, dashboard, proof, or media placeholder earns attention.
- Difference from accepted prior templates: which effect/gradient/surface-depth grammar must not repeat.

After building, screenshot-inspect whether the effect system is actually visible and useful. If the design looks clean but flat, if the effects only exist in the design-system notes, or if the gradient/effect system is too subtle to shape hierarchy, the template is not done.

If two templates are structurally distinct but still feel too similar, inspect whether their effect/gradient/surface-depth grammar is doing enough differentiation work. A useful effect pass may change surface behavior, lighting, hero object emphasis, media placeholder depth, CTA treatment, and section transitions. It must support the product; it must not become decorative noise.

Valid restraint must be deliberate and evidenced. If choosing flatness, explain what creates premium hierarchy instead: typography, scale contrast, image rhythm, negative space, composition tension, or material restraint.

## Anti-Copy And Anti-Noise Rules

- Do not copy exact effect values from the reference.
- Do not use heavy shadows just because the reference has shadows.
- Do not add glow to calm editorial, luxury, healthcare, finance, or service templates unless the concept clearly supports it.
- Do not use glass/blur unless it improves clarity and remains editable.
- Do not let effects hide weak structure.
- Do not let effects create low contrast, muddy edges, visual clutter, or generic AI-looking polish.

## Review Gate

Before finalizing:

- Screenshot-inspect whether effects are visible but not distracting.
- Check that effects support hierarchy and do not compete with text.
- Verify effect styles are named semantically in the design system.
- Confirm the effect system is original to the new template, not copied from the reference.
- For batch work, compare effect language, gradient logic, surface depth, CTA emphasis, and media-placeholder treatment against all accepted prior templates.
- Reject "clean but visually underbuilt" output. Add a functional effect/gradient pass or document deliberate restraint with visual evidence.
