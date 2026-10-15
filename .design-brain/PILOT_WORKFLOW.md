# Real Project Pilot Workflow

A real project pilot is a controlled first run of Codex Design Brain inside a real frontend or UI project. It helps Codex inspect the project, plan evidence, create review artifacts, revise deliberately, and capture useful feedback without changing stable memory automatically.

## When To Run It

Run a pilot before the first substantial UI, frontend, landing page, dashboard, component, design system, marketplace template, or Figma-like layout task in a new project. Use it again when the project changes enough that prior assumptions may no longer hold.

## Recommended Flow

1. Install Design Brain into the target project with dry-run first.
2. Run the status checker.
3. Create a pilot brief.
4. Inspect project structure and UI target.
5. Capture or provide a screenshot or URL.
6. Build the first draft.
7. Create a review report.
8. Create a visual review report.
9. Revise based on critique.
10. Save useful feedback as reflection.
11. Promote repeated lessons only after approval.

## Commands

```bash
python scripts/install_design_brain.py --target "PROJECT_ROOT" --dry-run
python scripts/design_brain_status.py --root "PROJECT_ROOT"
python scripts/design_brain_pilot.py --project-root "PROJECT_ROOT" --task "TASK" --target "TARGET" --url "URL" --notes "NOTES"
python scripts/design_brain_review.py --task "TASK" --target "TARGET" --notes "NOTES"
python scripts/design_brain_visual_review.py --task "TASK" --target "TARGET" --screenshot ".design-brain/screenshots/SCREENSHOT.png" --notes "NOTES"
```

## Report Storage

By default, `design_brain_pilot.py` writes pilot reports into the Design Brain repo where the script lives: `.design-brain/pilots/`. Use `--output` to intentionally save a pilot report inside another project.

## Warnings

- Do not claim visual inspection unless a screenshot, browser view, or rendered output was actually inspected.
- Do not auto-promote reflection lessons into stable memory.
- Do not overwrite project files without user intent.
- Do not treat the pilot report as a reflection log.
- Do not use a single pilot result to rewrite `DESIGN_MEMORY.md` or `DESIGN_PREFERENCES.json`.
