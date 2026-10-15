# Changelog

## v0.3.0

- Added Brain Design compatibility contract.
- Added craft adapter JSON output.
- Added craft request/result/compatibility schemas.
- Added override guard so Design Craft cannot change Brain Design route, product family, mode, structure, cognition, simulation verdict, layout audit, post-build status, or final status.
- Added craft adapter smoke test.

## v0.2.7

- Fixed Facebook cover and book cover routing/blocking.
- Added voucher/coupon/gift-card/loyalty-card modes or mappings.
- Added sticker/postcard/certificate/booklet modes or mappings.
- Added packaging label / label / price tag / hang tag modes.
- Fixed tag/label collateral not to route to website/ecommerce by default.
- Improved anti-scaffold sanitation for cover/collateral/label/tag modes.
- Export script now kills hanging subprocesses reliably during manual checks.
- Smoke tests now cover all v0.2.6 audit failures.

## v0.2.6

- Fixed social carousel/story routing.
- Fixed Instagram story routing.
- Added letterhead / price list / table tent modes or mappings.
- Added catalog/lookbook design modes.
- Fixed product catalog/lookbook design not to become ecommerce website.
- Improved anti-scaffold sanitation for social/collateral formats.
- Export manual checks now have per-query progress and timeout.
- Smoke tests now cover all v0.2.5 audit failures.

## v0.2.5

- Fixed static/collateral anti-scaffold block.
- Added non-web fallback family map.
- Added brochure/invoice/resume/order-ticket/collateral modes.
- Fixed flyer/banner/thumbnail/social-banner routing.
- Removed `full_website_template` fallback label from non-web modes.
- Export script now has timeout/progress/fail-fast guard.
- Smoke tests now cover static/collateral and non-web fallback labels.

## v0.2.4

- Fixed conversion/CTA payload leak.
- Blocked `landing.csv` metadata from non-web modes.
- Added mode-specific action model.
- Added niche-specific landing conversion notes.
- Replaced dashboard conversion wording with task-efficiency/data-hierarchy language.
- Removed `full website` keyword leak from non-website modes.
- Smoke tests now inspect conversion, CTA, best_for, keywords, and persisted markdown.

## v0.2.3

- Fixed style payload leak after auto-repair.
- Anti-scaffold gate now validates style name, keywords, effects, key effects, best_for, checklist, and persisted output.
- Added mode-specific style profiles.
- Added mode-specific effect language.
- Added mode-specific quality checklists.
- Added niche-aware landing structures.
- Blocked web-only effects from presentation/static/social/menu/email/brand modes.
- Blocked web UI checklist from non-web modes.
- Expanded smoke tests with negative content assertions.
- Added persisted MASTER.md content validation.
- Export remains clean and cache-free.

## v0.2.2

- Anti-scaffold FAIL now blocks persistence and triggers auto-repair or hard stop.
- Landing page intent now uses `MODE: landing` while preserving niche family.
- Added presentation/PPTX/Google Slides/Keynote detection.
- Added static canvas / brand kit / menu design / poster design / social post modes.
- Added UI kit / component library / design system modes.
- Fixed fashion/apparel ecommerce routing.
- Fixed furniture rental / sewa furniture routing.
- Restricted onboarding from auto-routing to mobile app without app/screen context.
- Raw JSON search output now includes safety metadata.
- Component specs are now token-based and style-DNA aware.
- Expanded smoke tests for all v0.2.2 edge cases.

## v0.2.1

- Removed hardcoded Codex-Design Windows path.
- Made Design Craft portable by repo-root marker detection.
- Restricted `Minimal & Direct` and minimal/flat patterns to explicit small-scope use only.
- Added expanded product families: real estate, education/course, medical/clinic, beauty/wellness, car rental, email/newsletter.
- Added safety metadata for legacy patterns.
- Strengthened Brain Design defer behavior.
- Added raw-search safety labeling.
- Added extension slot for future user ideas.
- Added more smoke tests and package hygiene checks.

## v0.2.0

- Made Design Craft a Brain Design support layer.
- Added Indonesian aliases, product depth rules, structure patterns, anti-scaffold gate, validation, smoke tests, and clean export.
