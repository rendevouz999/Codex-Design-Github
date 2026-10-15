---
description: Main-owned contextual visual review of PPTX web-image candidates.
---

# Web Image Review Stage

For native PPTX work in this plugin, read [PPTX_IMAGE_SELECTION_POLICY.md](../PPTX_IMAGE_SELECTION_POLICY.md). It owns this stage. The team is Main plus one GPT-6.1 Sol (Codex) / Claude Opus 5.5 (Claude Code) Engineer at Extra High (`xhigh`); never create an additional reviewer.

Engineer supplies the stable deck/slot ID, 1-based slide number, slide message and copy/layout, locked image intent, crop limits, candidate IDs, source/license evidence, actual dimensions and absolute preview/contact-sheet paths. Main inspects actual pixels and proposed placement. A contact sheet supports triage; open a larger candidate when identity or detail is unclear. Filename, search ranking and metadata alone cannot support ACCEPT.

| Gate | Main checks |
|---|---|
| Context and truth | Image supports this slide's message and audience; exact subjects are verified, conceptual stock is not presented as factual evidence. |
| Visual direction | Mood, style, lighting and quality suit the deck; no generic or irrelevant filler. |
| Placement | Orientation, focal point, crop safety and quiet space suit the assigned frame and copy. |
| Technical quality | Usable resolution after crop, sharpness and a readable, inspectable original. |
| Source and use | Source page, applicable license, intended template use and required credit are evidenced. Unknown rights do not pass. |

Main records a concrete reason for ACCEPT, REJECT or BLOCKED. Critical mismatches fail; never select the least-bad candidate to finish. BLOCKED means evidence/tool/access failure, not a rejected visual candidate. Candidate review is Main's own judgment and must not be written on Main's behalf by the Engineer.

For each stable slot, the second distinct REJECT of an Engineer submission transfers search to Main. Query/provider changes and slide renumbering preserve history. Identical duplicate review IDs count once; conflicting duplicates fail. Main may change search strategy using the rejection evidence and must inspect its own selection. Engineer may download and place the image Main selected, but may not initiate a third search round. Do not turn one round into endless pagination; keep submissions bounded.

Record decisions in `images/image_review.json` and source/license/credit facts in `images/image_sources.json`. Before embedding, Main supplies accepted candidate ID, local original/hash, slide and slot, frame coordinates/units, crop/focal direction, alt/caption/credit and reason. Run the canonical policy's `--stage handoff` check. Preserve native replaceable pictures. After draft export, Main checks the actual rendered slide and native QA evidence, records final review bound to the current deck and placement, then runs `--stage final`.

The user-facing handoff and delivery map must identify each **slide → image → purpose/placement → source**. Report missing visual capability honestly and repair access; no metadata-only fallback or unassigned image bundle.
