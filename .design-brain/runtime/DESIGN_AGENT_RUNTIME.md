# Design Agent Runtime

Brain Design Runtime is the operating loop for high-value design/template work.

It does not replace existing gates. It runs existing gates in order, records state, creates repair tickets, and blocks final delivery until required gates pass.

## Runtime Loop

User Request
-> Runtime Session Start
-> Route Tool
-> Reference Usage Tool
-> Cognition Tool
-> Section Layout Tool
-> Subagent Orchestration Tool
-> Simulation Tool
-> Layout Originality Tool
-> Build Session Tool
-> Design Craft Adapter Tool
-> Design System Tool
-> Post-Build Tool
-> Completion Tool
-> Verify Final
-> Delivery

## Required Stage Order

1. route
2. reference_usage
3. cognition
4. section_layout
5. subagent_orchestration
6. simulation
7. layout_audit
8. build_session_verify
9. craft_support
10. design_system_check
11. post_build_audit
12. completion_receipt
13. verify_final

## Blocking Rule

For design-template tasks, final delivery is blocked unless every required stage is `PASS`, no repair tickets are open, and build-session `verify-final` passes.

## Runtime Capabilities

- command registry
- tool registry
- permission modes
- hooks
- session state
- repair tickets
- doctor/status
- resume/rewind/history
- context compaction

## Design Craft Role

Design Craft is a support adapter and a non-override craft layer. It may help with tokens, typography, spacing, accessibility, components, states, and source handoff. It cannot override route, product family, cognition, simulation verdict, layout originality, post-build status, or final readiness.

## Web Deck Gate Placement

The Web Deck Stage Gate adds no stage to the required stage order. For `web-deck` output it runs inside stages that already exist:

- `build_session_verify`: the plan-time stage check runs after the deck plan exists and before any HTML is written.
- `design_system_check`: deck tokens, motion signature, and stage/runtime kit evidence are part of the design system evidence, not a separate receipt.
- `post_build_audit`: `web_deck_tool` runs the static audit and `web_deck_render_review_tool` runs the render review, both before Audit Pass 1.
- `completion_receipt`: the web deck receipt records the plan, the static audit result, and the render review result.

A P0 stage or runtime defect blocks final delivery through the existing blocking rule, and a web deck with no static audit and no render review is missing required stage evidence. The gate owns stage and runtime fidelity only. It cannot override route, medium choice, cognition, simulation verdict, layout originality, post-build status, or final readiness.
