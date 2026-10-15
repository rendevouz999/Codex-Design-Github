# Reference Corpus Config

Design Brain uses local reference files only when the corpus exists and contains usable candidates. Never claim a design is locally reference-led when the selector found zero candidates.

Public-core packages do not include private local reference corpus files by default. The workflow and selector are included, but the corpus itself is optional unless the package is exported in an internal mode that explicitly includes it.

## Default Website Corpus

- Default relative path: `Template Website`
- Optional local override: pass `--source` to `scripts/design_brain_website_reference_select.py` or `scripts/design_brain_reference_corpus_health.py`.
- Local override should point to a folder that contains `.png`, `.jpg`, `.jpeg`, `.webp`, or `.fig` reference files.

## Approved Template Corpus

- Approved local path: `<USER_HOME>/Downloads\Template\Template yang Sudah Masuk Google Drive`
- Active Brain Design guide: `.design-brain/APPROVED_TEMPLATE_CORPUS.md`
- Use this folder as Yusuf's approved-output benchmark for template depth, design-system boards, preview packaging, and accepted visual range.
- Do not treat this folder as a copy source. Use it for product-family taste calibration and quality checks.

## Allowed Fallback Folders

Codex may check these folders when the default path is missing or empty:

- `Template Website`
- `references/Template Website`
- `references/template-website`
- `.design-brain/reference-corpus/template-website`
- `.design-brain/evidence/fig-extracts`
- `<USER_HOME>/Downloads\Template\Template yang Sudah Masuk Google Drive`

## No Silent Fail Rule

If no candidate is found:

- Say `No local reference candidates found`.
- List the path or fallback folders that were checked.
- Do not write or say `Product-type reference matches used` as though reference selection succeeded.
- Ask for a reference upload, a Figma/link reference, or a configured local corpus path unless the current task already includes a usable reference image/link.

## Health Check

Use:

```bash
python scripts/design_brain_reference_corpus_health.py
python scripts/design_brain_reference_corpus_health.py --source "C:/path/to/Template Website"
```

The health check returns a clear warning when the corpus is unavailable or empty.

## Package Modes

- `public-core`: includes workflow rules and selector scripts, excludes private/large local corpus folders such as `Template Website/`.
- `complete-internal --include-corpus`: may include local corpus files for private audit or handoff when the user explicitly wants that larger internal package.
- Raw local inventory and ledger files are excluded from public-core when they contain machine-local reference metadata. Public packages should rely on sanitized summaries and ask the user to add a local corpus.

If a public-core consumer has no corpus installed, the correct state is `READY: yes with warnings`, not `local-reference-led ready`.
