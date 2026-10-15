"""Compatibility entry point; implementation is owned by presentation-deck."""
from pathlib import Path
import runpy
import sys
_target = Path(__file__).resolve().parents[1] / 'skills/presentation-deck/runtime/design_brain_pptx_frame_precision_review.py'
sys.path.insert(0, str(_target.parent))
if __name__ == '__main__':
    runpy.run_path(str(_target), run_name='__main__')
else:
    globals().update({k:v for k,v in runpy.run_path(str(_target)).items() if not k.startswith('__')})
