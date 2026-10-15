# Output Format Rules

- Rule category: workflow
- Last reviewed: 2026-05-26
- Source references used:
  - Microsoft Support: What is a slide master in PowerPoint? https://support.microsoft.com/en-us/office/what-is-a-slide-master-in-powerpoint-b9abb2a0-7aef-4257-a14e-4329c904da54
  - Microsoft Support: Create and save a PowerPoint template https://support.microsoft.com/en-us/office/create-and-save-a-powerpoint-template-ee4429ad-2a74-4100-82f7-50f8169c8aca
  - Microsoft Learn: Structure of a PresentationML document https://learn.microsoft.com/en-us/office/open-xml/presentation/structure-of-a-presentationml-document
  - Microsoft Learn: Working with slide masters https://learn.microsoft.com/en-us/office/open-xml/presentation/working-with-slide-masters
  - Playwright: Screenshots https://playwright.dev/docs/screenshots
  - Playwright: Visual comparisons https://playwright.dev/docs/test-snapshots
## Format Rules

- PPTX requires slide size, masters/layouts, placeholders, editable text/shapes, theme colors, theme fonts, and export checks.
- Google Slides and Keynote require theme/layout thinking and editable media/text placeholders.
- Figma Slides and Figma Design require visible frame organization, editable placeholders, and export-aware 16:9 structure.
- HTML previews require Chromium screenshot QA, responsive checks, and visual regression when baselines exist.

## Decision Rule

- Never validate a PPTX only by screenshot; native PPTX structure must also be checked.
