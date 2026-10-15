# Brain Design Total Integration Input Digest

Generated: 2026-05-30

## Active Features

- Router and product-family detection are active workflow inputs.
- Design Cognition Contract is active as a JSON/checker gate.
- Design Simulation Layer is active as the pre-build gate.
- Sequential Layout Originality Gate is active for reference and pairwise layout checks.
- Build Session Lifecycle is script-backed and already tracks references, cognition, simulation, layout audits, build artifacts, design systems, post-build audits, locks, and completion receipts.
- Post-Build Completion Gate is active as the design-system, triple-audit, repair, and receipt gate.
- Package integrity/export/install checks already exclude public-package unsafe content in exported packages.

## Partial Features

- Real visual verification still requires screenshot/render/Figma inspection.
- Design system proof is receipt-backed; it needs explicit artifact evidence to distinguish source proof from notes.
- Lifecycle is strong but must be treated as the mandatory wrapper around real template builds.
- Design Craft and TypeUI-derived support are useful craft inputs, but they need a clear non-override contract so they cannot supersede Brain Design gates.
- Similarity docs use strict product language; scripts need explicit hard/soft axis semantics so thresholds are readable.

## Critical Issues

- Source package integrity fails because `downloads/MiroFish` exists inside the active workspace.
- Real template builds can still be finalized incorrectly if the caller does not run the lifecycle final verification step.
- Completion receipt enforcement is stricter in `--strict` mode than in default final template behavior.

## Cleanup Candidates

- `downloads/MiroFish` should be archived outside the active workspace, not deleted.
- `.bak-*`, `.backup-*`, `.orig`, `.old`, and `.tmp` files should be archived outside active source.
- Old generated evidence such as context packets, PPTX precision reports, and reference insight studies should be preserved as evidence but removed from active package/source ownership.
- TypeUI-managed/generated design files remain excluded from public package scope and should stay non-authoritative.

## Source Integrity Blockers

- Active forbidden external source directories: `downloads/MiroFish`.
- Active backup files: `.bak-*` snapshots across `.design-brain`, scripts, and skills.
- Active generated temp/evidence folders make source noisy even when not exported.

## Recommended Patch Order

1. Create cleanup plan and manifest before moving files.
2. Archive `downloads/MiroFish` outside active workspace.
3. Archive backup snapshots outside active source.
4. Move old generated evidence into local archive space or external archive.
5. Add Design Craft non-override contract and wire it into autoload/source-of-truth docs.
6. Add lifecycle `verify-final` and make it the required final readiness check.
7. Make completion receipt default-required for template final audits.
8. Add artifact evidence requirements to design system receipts/checker.
9. Align similarity threshold language with script output.
10. Update package integrity and safe smoke tests.
11. Run safe tests with runtime checks active.
