# Craft Output Contract

Design Craft adapter output is support evidence only.

It cannot approve final delivery. It cannot change Brain Design route, product family, mode, section structure, cognition, simulation verdict, layout audit status, post-build audit status, or final status.

If a request includes fields such as `overrideRoute`, `overrideProductFamily`, `overrideStructure`, `overrideSimulationVerdict`, `overrideLayoutAuditStatus`, `finalStatus`, or asks to shorten a full template into a generic minimalist scaffold, the adapter must return:

```json
{
  "status": "BLOCKED_BY_BRAIN_DESIGN_CONTRACT"
}
```

