# Runtime Repair Tickets

Repair tickets are created when a blocking gate fails.

Lifecycle:

open -> assigned -> repaired -> rerun_gate -> closed

Blocked branch:

blocked -> needs_user_input

Required fields:

- ticketId
- sessionId
- templateId
- sourceGate
- issue
- severity
- requiredRepair
- suggestedAction
- status
- createdAt
- updatedAt
- rerunGateRequired

Final delivery is blocked while any repair ticket is open, assigned, repaired without rerun, or blocked.

If a critical repair ticket remains unresolved, runtime final status is `BLOCKED`.
