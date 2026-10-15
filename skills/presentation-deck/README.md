# Presentation capability

One entry point: `SKILL.md`. One shared design owner: `design/WORKFLOW.md`.

| Operation | Result |
|---|---|
| Create Template | Reusable Brand, Style, Layout or Deck workspaces; editable native masters, layouts and placeholders |
| Generate | New presentations from a brief and selected resources |
| Edit Existing | Source-preserving native edits within tested object/format boundaries |

Each operation uses native PowerPoint or browser output as appropriate. Browser delivery includes stage/navigation/motion, static audit and browser/print review. Native delivery includes SVG/native authoring, tables/charts, notes, validation, export and round-trip checks. Seven neutral layout families, fourteen style families, ten optional theme references and an indexed icon library support design decisions. They are primitives and references, not a shared whole-template scaffold.

## Setup and use

Install `runtime/requirements.txt` with the chosen Python interpreter, then run `python runtime/presentation.py doctor`. Select the interpreter with `--python` or the host `BRAIN_DESIGN_PYTHON` setting when needed. No machine-specific interpreter path or donor checkout is required. Run `python runtime/presentation.py --help` for project/template/export commands. Author new templates in a project workspace, outside this installed directory.

Browser generation/audit need Node only. For PPTX intake and browser review, install `runtime/web/package.json` dependencies with `npm ci --prefix runtime/web`; install Chromium using that directory's Playwright CLI. An existing compatible host installation also works. On Windows, contact-sheet rendering supports installed Microsoft PowerPoint. The alternative LibreOffice path additionally needs LibreOffice and pypdfium2; it is not validated by this adoption run.

## Ownership and verification

Native and web workflows live in `workflows/`. Technical details and design resources live inside this capability. Shared Brain gates remain in the plugin's shared infrastructure. Root compatibility scripts delegate here; they are not another implementation.

`provenance/components.json` records adoption decisions, `adopted-files.json` records original and adapted hashes, and `verification.json` records actual test coverage and limits. Original MIT, Apache-2.0, icon and other resource notices remain packaged. The donor checkout and previous web skill are not runtime dependencies.
