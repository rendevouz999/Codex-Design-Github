# Website Template Reference Corpus

Use `Template Website` as the default local visual reference corpus for website-template work. See `.design-brain/REFERENCE_CORPUS_CONFIG.md` for fallback paths and health rules.

This folder contains many filled preview images from existing website template outputs. Treat it as evidence for product-type expectations, visual density, section depth, market category, and designer cognition. Do not treat it as a layout library to copy.

## When To Use

Use this corpus before planning a website template when the task involves:

- Figma website template
- website template
- web template
- full website
- homepage template
- SaaS/product website
- business/corporate website
- agency/studio website
- service/booking website
- ecommerce/storefront
- portfolio/case-study website
- blog/editorial/CMS website
- docs/help center
- dashboard/admin/web app
- community/nonprofit
- event/travel/hospitality
- utility page kit
- batch website template work

## Product-Type First Rule

Do not browse this corpus randomly. First classify the requested product using `.design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.md` and `.design-brain/FIGMA_WEBSITE_TEMPLATE_PRODUCT_TYPES.json`.

Then use the selected product family to choose reference previews from `Template Website`.

If the corpus is missing or contains zero candidates, say `No local reference candidates found`, list checked paths, and do not claim local-reference-led selection happened.

The corpus is a local evidence source. It should reduce assumptions about:

- expected homepage section depth
- page map and flow requirements
- proof and trust placement
- density rhythm
- visual proof strategy
- image placeholder role and replacement clue
- component systems common to the product family
- market completeness signals
- generic or underbuilt risks

## Selection Workflow

1. Classify the website product family.
2. Query `Template Website` by product-family triggers, niche terms, and buyer terms.
3. Use all relevant matches as the Pattern Learning Pool.
4. Split the matched pool into product-purpose reference groups of up to 10 varied references, balanced so the final group is not a tiny leftover when enough references exist.
5. Use one active reference group as the Execution Influence Pool for one template cycle.
6. Record the active group usage in the selector rotation registry so the next same-product build uses the next group.
7. After all groups for that product-purpose are used, reset to group 1 and continue rotation.
8. Apply `.design-brain/DESIGNER_COGNITION_LAYER.md` to the active reference group.
9. Extract evidence-backed cognition before structure planning.
10. Define what visual execution must not be copied.

Use the selector when useful:

```bash
python scripts/design_brain_website_reference_select.py --task "..." --template-type "website template" --niche "..." --dry-run
python scripts/design_brain_website_reference_group_inventory.py
python scripts/design_brain_reference_corpus_health.py
```

For batch work, use a fresh active reference group per cycle. Do not reuse group 1 for template 2 when group 2 exists for the same product-purpose. Do not reuse the same execution references for every output unless the user explicitly requires it.

## Group Rotation Rule

When the selector finds many product-family candidates, the correct output is not a tiny repeated top-3 set. The selector should expose:

- broad match count
- Pattern Learning Pool
- numbered reference groups of up to 10 templates
- minimum desired group size of 4 when enough product-purpose references exist
- active group index
- rotation registry state

Example: if 100 SaaS/AI references are group-ready and group size is 10, the selector should create 10 groups. Template build 1 uses group 1, build 2 uses group 2, and so on. After group 10 is used, the next same-product build resets to group 1.

If the group-ready pool is not divisible by 10, distribute the references into balanced groups instead of creating a weak leftover group. For example, 22 references should become 8/7/7, not 10/10/2. If a product has a small but valid pool, use one group with at least 4 references when possible. If only 1-3 strong references exist, the selector may add product-purpose support references, but it must label the supplement count and keep the confidence lower. If the pool still cannot reach 4, do not form an active rotation group for that product yet.

The groups must remain product-purpose matched. Do not pad a SaaS/AI group with unrelated restaurant, portfolio, ecommerce, or hospitality references just to reach 10.

## Evidence Rules

For each selected preview in the active group, record:

- source file path
- product-family match
- observed visual evidence
- inferred designer reason
- user or buyer effect
- reusable thinking logic
- recognizable execution to avoid
- confidence level

If selected references do not visibly support the product family, select different references before designing.

## Reference Transformation

Allowed:

- Learning product-type standards.
- Learning how proof, density, image role, rhythm, and CTA pressure are handled.
- Learning what text clue image placeholder a template buyer needs.
- Reusing abstract thinking logic such as evidence-before-action or calm-to-dense pacing.

Not allowed:

- Copying exact composition.
- Copying exact section order.
- Copying image placement.
- Copying distinctive motif.
- Copying CTA staging.
- Generating final images for source templates just because references include photos, screenshots, portraits, maps, or product shots.
- Averaging many references into one bland template.
- Reusing one reference group's execution pattern across a batch.

## Image Placeholder Rule

When a selected reference uses imagery, identify the job of the image and convert it into a role-specific text clue placeholder in the new source template. Examples: `image placeholder: SaaS dashboard screenshot`, `image placeholder: ecommerce product image`, `profile photo placeholder: consultant portrait`, `image placeholder: restaurant interior or signature dish`.

Do not use reference imagery as pressure to create generated images unless the user explicitly requests final image generation.
