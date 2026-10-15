# Runtime Doctor And Status

`design_brain_doctor.py` verifies runtime health.

Doctor checks:

- runtime docs exist
- runtime schemas exist
- command registry exists
- tool registry exists
- permission modes exist
- hooks docs/config exist
- runtime state folder is writable
- required Brain Design scripts exist
- Design Craft adapter presence if configured
- manifest/install/export references exist
- no MiroFish/OASIS source in active workspace
- no `.bak-*` in source scope
- no TypeUI managed marker in public scope
- package integrity script exists
- smoke tests exist

`design_brain_status_runtime.py` reports:

- version
- active runtime session
- permission mode
- current stage
- missing stages
- open tickets
- last gate result
- final readiness
- next recommended command

