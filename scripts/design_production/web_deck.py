"""Typed web units reuse the single internal stage/runtime and review tools."""
import base64
import hashlib
from html import escape
import json
import shutil
from .policy import ROOT

CAP = ROOT/'skills/presentation-deck'


def build_web(adapter):
    css = (CAP/'resources/web-deck/stage-base.css').read_text(encoding='utf-8')
    script = (CAP/'resources/web-deck/deck-runtime.js').read_text(encoding='utf-8')
    sha = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
    sections = []
    for index,unit in enumerate(adapter.task.units):
        children=[]
        for n in adapter.contents[unit.id].nodes:
            style=f'position:absolute;left:{n.x}px;top:{n.y}px;width:{n.width}px;height:{n.height}px;box-sizing:border-box;'
            if n.kind=='text':
                style+=f'font-family:{n.font};font-size:{n.font_size}px;font-weight:{700 if n.bold else 400};line-height:1.15;color:{n.fill};white-space:pre-wrap;'
                children.append(f'<div id="{unit.id}-{n.id}" style="{style}">{escape(n.text)}</div>')
            else:
                style+=f'background:{n.fill};border:{n.stroke_width}px solid {n.stroke};border-radius:{"50%" if n.kind=="ellipse" else str(n.radius)+"px"};'
                children.append(f'<div aria-hidden="true" id="{unit.id}-{n.id}" style="{style}"></div>')
        sections.append(f'<section class="deck-slide{" is-active" if index==0 else ""}" data-deck-headline="{escape(unit.id)}" aria-label="{escape(unit.id)}">'+''.join(children)+'</section>')
    csp=f"default-src 'none'; script-src 'sha256-{sha}'; style-src 'unsafe-inline'; img-src 'none'; font-src 'none'; connect-src 'none'; base-uri 'none'; form-action 'none'"
    html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="{csp}"><title>Assigned presentation</title><style>{css}</style></head><body>
<div class="deck-viewport"><main class="deck-stage deck-stage--fade" data-deck-transition="fade">{''.join(sections)}</main></div>
<nav class="deck-chrome" aria-label="Slide controls"><div class="deck-progress"><div class="deck-progress-bar"></div></div><div class="deck-counter"><span class="deck-counter-current">1</span> / <span class="deck-counter-total">{len(sections)}</span></div><div class="deck-controls"><button class="deck-control" data-deck-nav="prev" aria-label="Previous slide">←</button><button class="deck-control" data-deck-nav="next" aria-label="Next slide">→</button></div></nav><div class="deck-live deck-sr-only" aria-live="polite"></div>
<script>{script}</script></body></html>'''
    path=adapter.directory/'design.html'
    path.write_text(html,encoding='utf-8')
    adapter.manifest(path,'deliverable',True)


async def render_web(adapter):
    node=shutil.which('node')
    audit=await adapter.process([node,str(CAP/'runtime/web/design_brain_web_deck_audit.mjs'),str(adapter.directory/'design.html'),'--json'],30)
    data=json.loads(audit.read_text(encoding='utf-8'))
    (adapter.directory/'web-audit.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    adapter.manifest(adapter.directory/'web-audit.json','evidence')
    await adapter.process([node,str(CAP/'runtime/web/design_brain_web_deck_render_review.mjs'),str(adapter.directory/'design.html'),'--out',str(adapter.directory/'web-preview'),'--json'],120)
    for path in (adapter.directory/'web-preview').rglob('*'):
        if path.is_file():
            adapter.manifest(path,'preview' if path.suffix in {'.png','.pdf'} else 'evidence')


def verify_web(adapter):
    static=json.loads((adapter.directory/'web-audit.json').read_text())
    rendered=json.loads((adapter.directory/'web-preview/render-review.json').read_text())
    issues=[]
    if static['status']!='PASS' or rendered['result']!='PASS':
        issues.append('Internal web deck audit/render did not pass')
    if rendered['slideCount']['dom']!=len(adapter.units):
        issues.append('Web slide count mismatch')
    for unit in adapter.task.units:
        for node in adapter.contents[unit.id].nodes:
            if node.kind=='text' and escape(node.text) not in (adapter.directory/'design.html').read_text(encoding='utf-8'):
                issues.append('Editable HTML text missing')
    return ['Internal stage/runtime and static audit', 'Real Chromium navigation, stage/viewport fidelity, overflow, contrast, reduced-motion and print review', 'Editable HTML text and assigned slide count read back', 'CSP denies network/assets and allows only the trusted runtime script hash'],issues
