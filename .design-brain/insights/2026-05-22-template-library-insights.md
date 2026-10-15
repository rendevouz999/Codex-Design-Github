# Template Library Design Insights - 2026-05-22

Source audit:
- `Template/Babun - Business & Finance HTML5 Template`
- `Template/buyer-file`
- `Template/dist`
- `Template/ekobyte-it-service-&-technology-php-template`
- `Template/main-files`
- `Template/medcity`
- `Template/NemuNextjs`
- `Template/package`
- `Template/TechFolio-Laravel_v1.0`
- `Template/monas-package-file`

## High-Value Patterns

1. Large editorial hero type works best when balanced by quiet proof objects.
   Finance and creative templates use oversized headlines as the first viewport signal, but the better executions add measurable trust nearby: company counts, status cards, service chips, or client proof.

2. Accent color must have a job.
   Lime, cyan, blue, and coral accents are strongest when used for CTAs, active navigation, progress states, and proof highlights. When accent color decorates everything equally, hierarchy gets weaker.

3. Section rhythm matters more than section count.
   The most reusable pages alternate between high-impact hero, narrow proof band, service/value grid, case/product evidence, and a focused CTA. Reordering these blocks keeps the layout fresh while preserving conversion logic.

4. Auto-layout needs clear content units.
   Good template sections are built from named, repeatable units: metric strip, service card, process step, case row, product tile, appointment panel, testimonial quote, and footer link group. These units should be editable frames, not decorative one-off shapes.

5. Premium does not mean more effects.
   The strongest examples use restrained borders, large whitespace, precise typography, and one or two signature visual moves. Heavy shadows, generic blobs, and unstructured gradients reduce marketplace quality unless they clarify the product mood.

6. Domain mood should change the information architecture.
   Healthcare needs trust, schedule, service category, and safety reassurance early. Finance needs credibility, measurable outcomes, and advisory clarity. Tech services need capability mapping and diagnostic/productized offers. Creative commerce needs portfolio/product evidence and visual drama.

7. The best hero compositions avoid predictable split sameness.
   Reusable alternatives include centered headline with side proof objects, floating command panels, offset product bands, asymmetric bento zones, horizontal ticker proof, and editorial whitespace with delayed product reveal.

8. Design-system boards should be useful, not decorative.
   A good board shows role-based color tokens, type scale, spacing/radius rules, primitive examples, and accessibility notes in compact rows. Token palettes must wrap cleanly and stay inside the frame.

## Rules To Reuse

- Start every template with a different structural order from the source reference.
- Use real landing-page roles: hero, trust/proof, service/value, process, cases/products, CTA, footer.
- Keep card radius at 8px or lower unless the domain needs softer medical or consumer commerce treatment.
- Use accent colors for action and state, not random ornament.
- Avoid nested cards and oversized decorative blobs.
- Verify Figma screenshots for text overflow, palette overflow, clipped frames, and parent frame height.
- Create variables and local styles first; no components unless the user explicitly asks.
