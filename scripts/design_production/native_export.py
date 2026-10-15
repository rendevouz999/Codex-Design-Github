"""Private fixed adapter process, using the internally adopted editable PPTX converter."""
import contextlib
import json
from pathlib import Path
import sys
import shutil

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "skills/presentation-deck/runtime/native"))

if __name__ == "__main__":
    from capability_integrity import require_skill_integrity
    from svg_to_pptx import create_pptx_with_native_svg
    from svg_to_pptx.drawingml.theme_fonts import ThemeFontFace, ThemeFontSpec, MasterTextStyleSpec
    from svg_to_pptx.drawingml.theme_colors import ThemeColorSpec, _OFFICE_DEFAULTS

    require_skill_integrity()
    directory = Path(sys.argv[1]).resolve()
    if not directory.is_relative_to(ROOT / "output") or not directory.is_dir():
        raise ValueError("Output boundary violation")
    # SVG files are generated exclusively from validated primitives by adapters.py.
    files = [directory / name for name in json.loads((directory / "unit-order.json").read_text())]
    if any(p.parent != directory or p.suffix != ".svg" for p in files):
        raise ValueError("Invalid unit list")
    output = directory / "design.pptx"
    if output.exists():
        raise ValueError("Refusing artifact overwrite")
    config = json.loads((directory / 'native-contract.json').read_text())
    options = {}
    mode = config['structure'] if config else 'flat'
    if config:
        major, minor = config['title_font'], config['body_font']
        slots = dict(_OFFICE_DEFAULTS, lt1=config['background'][1:], dk1=config['foreground'][1:], accent1=config['accent'][1:])
        options = dict(master_text_style_spec=MasterTextStyleSpec(round(config['title_size']*75), round(config['body_size']*75)),
            theme_font_spec=ThemeFontSpec(ThemeFontFace(major,major,major), ThemeFontFace(minor,minor,minor), major, minor),
            theme_color_spec=ThemeColorSpec(slots, {'background':slots['lt1'], 'text':slots['dk1'], 'primary':slots['accent1']}, {'background':'lt1','text':'dk1','primary':'accent1'}))
    with contextlib.redirect_stdout(sys.stderr):
        if config and config.get('reusable_template'):
            from config import CANVAS_FORMATS
            from xml.etree import ElementTree as ET
            from apply_template import apply_templates
            from template_preview_pptx import main as preview_template
            root = ET.parse(files[0]).getroot()
            canvas = next((k for k,v in CANVAS_FORMATS.items() if v['viewbox']==root.get('viewBox')),None)
            if canvas is None:
                raise ValueError('Reusable template workspace backend does not support this canvas preset')
            workspace = directory/'authored-template'
            target = workspace/'templates'
            target.mkdir(parents=True)
            prototypes=[]
            for i,file in enumerate(files,1):
                name=f'{i:02d}_{file.stem}.svg'
                shutil.copy2(file,target/name)
                prototypes.append(name)
            spec = {'layout_id':'assigned','kind':'layout','summary':'Assigned reusable native layout system; authored content and theme supplied by controller.', 'canvas_format':canvas,'canvas_width':int(root.get('width')),'canvas_height':int(root.get('height')),'canvas_viewbox':root.get('viewBox'),'native_structure_mode':'structured','replication_mode':'standard','page_count':len(prototypes),'page_types':[p.stem for p in files]}
            import yaml
            spec['placeholders']={Path(p).stem:[] for p in prototypes}
            (target/'design_spec.layout.assigned.md').write_text('---\n'+yaml.safe_dump(spec,sort_keys=False)+'---\n\n# Assigned layout system\n\n## IV. Signature Design Elements\nNative role slots preserve assigned geometry, theme and editability.\n\n## V. Page Roster\n| SVG | Layout key | Purpose |\n|---|---|---|\n'+ '\n'.join('| `'+p+'` | '+ET.parse(target/p).getroot().get('data-pptx-layout')+' | Assigned reusable layout |' for p in prototypes)+'\n',encoding='utf-8')
            applied = directory/'applied-template'
            applied.mkdir()
            plan = apply_templates(applied,[str(workspace)],validate=True)
            if preview_template([str(applied),'-o',str(directory/'template-preview.pptx'),'--native-charts-and-tables']) != 0:
                raise ValueError('Internal reusable template preview failed')
            files = [applied/'templates'/name for name in prototypes]
            (directory/'template-receipt.json').write_text(json.dumps({'status':'PASS','operations':['authored typed prototypes','template-check via apply_templates(validate=True)','apply-template','template-preview'],'source':str(workspace),'applied':str(applied),'prototypes':prototypes},indent=2),encoding='utf-8')
        result = create_pptx_with_native_svg(files, output, resource_root=directory,
            use_native_shapes=True, use_compat_mode=False, transition=None,
            workers=1, verbose=False, pptx_structure=mode, native_objects=True, use_layout_placeholder_frames=mode=='structured',
            conversion_trace_path=directory / "conversion-trace.json", **options)
    if not result or not output.is_file():
        raise RuntimeError("Native export failed")
    print(json.dumps({"path": str(output)}))
