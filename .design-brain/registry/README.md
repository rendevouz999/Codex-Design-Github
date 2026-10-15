# Design Brain Module Registry

The module registry is the selective-index layer for Design Brain. It tells Codex which craft modules, seed packs, validators, and source files to load for a task.

Use it before planning visual work that can span multiple media. The registry is intentionally compact: it stores routing metadata and distilled module relationships, not copied external repositories.

## Registry Fields

- `id`: stable module id.
- `kind`: `medium`, `craft`, `seed-pack`, `direction-pack`, or `validator`.
- `mediums`: applicable media.
- `productTypes`: product or template types.
- `triggers`: natural-language routing terms.
- `requiredCraft`: craft modules to load.
- `seedPack`: seed pack id.
- `validators`: lint or review scripts to run.
- `sourceInspiration`: local or conceptual source that inspired the module.
- `loadPriority`: lower numbers load first.

Generated external indexes live in `.design-brain/external-indexes/` and are not stable memory unless explicitly promoted.
