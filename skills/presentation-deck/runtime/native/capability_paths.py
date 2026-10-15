"""Canonical resource ownership for Codex Design presentation modules."""
from pathlib import Path
CAPABILITY_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = CAPABILITY_ROOT.parents[1]
NATIVE_ROOT = CAPABILITY_ROOT / 'runtime/native'
RESOURCE_ROOT = CAPABILITY_ROOT / 'resources'
DESIGN_ROOT = CAPABILITY_ROOT / 'design/native'
