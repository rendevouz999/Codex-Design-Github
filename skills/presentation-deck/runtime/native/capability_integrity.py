"""Validate adopted runtime identity and attribution without a donor checkout."""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from capability_paths import CAPABILITY_ROOT

@lru_cache(maxsize=1)
def require_skill_integrity():
    manifest = CAPABILITY_ROOT / 'provenance/integrity.json'
    try:
        data = json.loads(manifest.read_text(encoding='utf-8'))
        if data.get('owner') != 'codex-design.presentation-deck':
            raise ValueError('unexpected capability identity')
        for name, expected in data['criticalFiles'].items():
            path = (CAPABILITY_ROOT / name).resolve()
            if not path.is_relative_to(CAPABILITY_ROOT) or not path.is_file():
                raise ValueError(f'missing capability resource: {name}')
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError(f'capability resource changed: {name}')
        if not data['criticalFiles']:
            raise ValueError('empty integrity manifest')
    except (OSError, ValueError, KeyError) as exc:
        raise RuntimeError(f'Codex Design presentation integrity failed: {exc}') from exc
    return True

if __name__ == '__main__':
    require_skill_integrity()
    print('Codex Design presentation integrity: PASS')
