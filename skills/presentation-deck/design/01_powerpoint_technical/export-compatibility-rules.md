# Export Compatibility Rules

- Rule category: technical
- Last reviewed: 2026-05-26
- Source references used:
  - Microsoft Support: What is a slide master in PowerPoint? https://support.microsoft.com/en-us/office/what-is-a-slide-master-in-powerpoint-b9abb2a0-7aef-4257-a14e-4329c904da54
  - Microsoft Support: Create and save a PowerPoint template https://support.microsoft.com/en-us/office/create-and-save-a-powerpoint-template-ee4429ad-2a74-4100-82f7-50f8169c8aca
  - Microsoft Learn: Structure of a PresentationML document https://learn.microsoft.com/en-us/office/open-xml/presentation/structure-of-a-presentationml-document
  - Microsoft Learn: Working with slide masters https://learn.microsoft.com/en-us/office/open-xml/presentation/working-with-slide-masters
## Rules

- Validate slide size, aspect ratio, exported PDF/PNG preview, missing assets, fonts, and image links.
- PPTX, Keynote, Google Slides, and Figma export paths may differ; document limitations per format.
- If conversion changes layout, revise source or document the export caveat.

## Hard Gate

- If this rule fails on a PPTX output, do not call the template final.
