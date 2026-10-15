# Craft Tool Adapter

The craft adapter exposes Design Craft as a machine-readable support tool for Brain Design.

CLI:

```bash
python scripts/craft_adapter.py --request brain_design_request.json --json
```

The adapter reads Brain Design decisions and returns craft support without changing those decisions.

Required input:

- route
- productFamily
- mode
- designCognition
- layoutFingerprint
- simulationVerdict
- layoutAuditStatus
- designSystemRequirement
- craftScope

Output:

- craftResult
- tokens
- typography
- spacing
- components
- states
- accessibility
- sourceHandoff
- polishNotes
- blockedOverrides
- status

