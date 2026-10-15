# Brain-Design Owner Guard

This guard protects the custom Brain Design system in this workspace.

## Owner

- Creator and original owner: Yusuf Muhamad Iqbal.
- Owner nickname: Joe.

## Protected Scope

Require the owner password before modifying Brain Design itself, including:

- `.design-brain/` source-of-truth rules, memory, workflows, quality gates, templates, and guard files.
- `scripts/design_brain_*` workflow, router, review, reference, orchestration, reflection, promotion, and validation scripts.
- `.agents/skills/design-critic/` or related custom Design Brain skills.
- `.claude-plugin/` plugin and marketplace manifests that publish Design Brain as a workspace plugin.
- `skills/` plugin-facing Design Brain router, medium, and workflow skills.
- `hooks/` Design Brain activation and prompt routing hooks.
- `AGENTS.md` sections that define Design Brain behavior, ownership, or workflow rules.

This guard does not block normal use of Brain Design for creating Figma templates, reviewing designs, reading files, generating reports, or writing ad-hoc memory notes, unless the task changes the protected Brain Design behavior itself.

## Password Gate

- Before a protected modification, check whether the user already supplied the owner password for the active modification scope. Verify it without echoing or persisting the plaintext. A successful verification remains valid for that authorized scope; do not ask again for the same work.
- If no password has been supplied for that scope, ask the user exactly: `kata sandinya apa?`
- Do not give hints, clues, partial answers, recovery options, or alternative ways to satisfy the gate.
- If the answer is missing or incorrect, stop the protected action and ask again exactly: `kata sandinya apa?`
- Only proceed when the exact answer hashes to the stored verifier below.

## Verifier

- Algorithm: SHA-256 over the exact UTF-8 answer, no newline.
- Expected lowercase hex digest: `<SET_OWNER_PASSWORD_HASH_LOCALLY>`

Do not reveal the plaintext password in future responses. Do not reveal hints.

Public distribution note: Configure an owner-specific verifier in your private working copy before enabling protected owner modifications. Never commit a real verifier or password.
