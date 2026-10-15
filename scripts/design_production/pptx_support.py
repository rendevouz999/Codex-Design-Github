"""Bounded use of the internal native importer, preserving exporter and OOXML QA."""
import json
import os
from pathlib import Path
import zipfile
from xml.etree import ElementTree as ET

from .policy import ROOT

NS = {'p':'http://schemas.openxmlformats.org/presentationml/2006/main', 'a':'http://schemas.openxmlformats.org/drawingml/2006/main', 'c':'http://schemas.openxmlformats.org/drawingml/2006/chart', 'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
CAP = ROOT / 'skills/presentation-deck/runtime'


def source_inventory(path, units):
    with zipfile.ZipFile(path) as z:
        slides = sorted(n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml'))
        result = {'slide_count':len(slides), 'selected':[], 'untrusted_reference_data':True}
        size = ET.fromstring(z.read('ppt/presentation.xml')).find('p:sldSz', NS)
        for unit in units:
            if not unit.source_slide or unit.source_slide > len(slides):
                raise ValueError('Assigned source slide does not exist')
            if (int(size.get('cx')), int(size.get('cy'))) != (unit.width*9525,unit.height*9525):
                raise ValueError('Existing PPTX dimensions cannot change')
            doc = ET.fromstring(z.read(f'ppt/slides/slide{unit.source_slide}.xml'))
            texts = []
            for shape in doc.findall('.//p:sp', NS):
                identity = shape.find('p:nvSpPr/p:cNvPr', NS)
                texts.append({'shape_id':int(identity.get('id')), 'text':''.join(t.text or '' for t in shape.findall('.//a:t',NS))})
            result['selected'].append({'unit_id':unit.id, 'slide':unit.source_slide, 'texts':texts})
        return result


async def build_preserving(adapter):
    python = ROOT / ('.venv-presentation/Scripts/python.exe' if os.name == 'nt' else '.venv-presentation/bin/python')
    prefix = [str(python), '-B', str(CAP / 'presentation.py'), '--timeout', '60']
    source_inventory(adapter.pptx_source, adapter.task.units)
    workspace = adapter.directory / 'roundtrip'
    await adapter.process([*prefix,'import-pptx',str(workspace),'--source',str(adapter.pptx_source)],90)
    for unit in adapter.task.units:
        content = adapter.contents[unit.id]
        path = workspace / 'authoring-svg-flat' / f'slide_{unit.source_slide:02d}.svg'
        doc = ET.parse(path)
        for edit in content.edits:
            matches = [el for el in doc.iter() if el.get('data-pptx-source-ref') == f'slide:{edit.shape_id}']
            if len(matches) != 1 or matches[0].get('data-pptx-source-proxy'):
                raise ValueError('Unsupported or ambiguous slide-local shape ID')
            texts = [el for el in matches[0].iter() if el.tag.rsplit('}',1)[-1] == 'text']
            if len(texts) != 1 or len(list(texts[0])) or texts[0].text != edit.expected:
                raise ValueError('Bounded text edit requires a single plain text run matching expected content; rich text/proxy is preserved, not flattened')
            texts[0].text = edit.replacement
        if content.edits:
            ET.register_namespace('', 'http://www.w3.org/2000/svg')
            doc.write(path, encoding='utf-8', xml_declaration=True)
        source = adapter.directory / (unit.id + '.json')
        source.write_text(content.model_dump_json(indent=2), encoding='utf-8')
        adapter.manifest(source, 'source', True, [unit.id])
        adapter.manifest(path, 'source', True, [unit.id])
    await adapter.process([str(python),'-B',str(CAP/'native/svg_authoring_view.py'),str(workspace/'authoring-svg-flat'),'--refresh-summary'],30)
    await adapter.process([str(python),'-B',str(CAP/'native/svg_quality_checker.py'),str(workspace),'--roundtrip','--json'],30)
    await adapter.process([*prefix,'export-roundtrip',str(workspace),'--output',str(adapter.directory/'design.pptx'),'--native-data'],90)
    await adapter.process([*prefix,'delivery-check',str(adapter.directory/'design.pptx')],30)
    adapter.manifest(adapter.directory/'design.pptx','deliverable',True)


def canonical(data):
    return ET.canonicalize(data.decode('utf-8'))


def verify_preserving(adapter):
    checks, issues = [], []
    selected = {f'ppt/slides/slide{u.source_slide}.xml':u for u in adapter.task.units}
    with zipfile.ZipFile(adapter.pptx_source) as old, zipfile.ZipFile(adapter.directory/'design.pptx') as new:
        for name in old.namelist():
            if name.startswith(('ppt/slides/','ppt/slideMasters/','ppt/slideLayouts/','ppt/charts/','ppt/embeddings/','ppt/theme/','ppt/media/')) and name not in selected:
                if name not in new.namelist() or old.read(name) != new.read(name):
                    issues.append('Out-of-scope source part changed: '+name)
        for name, unit in selected.items():
            before, after = ET.fromstring(old.read(name)), ET.fromstring(new.read(name))
            edits = adapter.contents[unit.id].edits
            for edit in edits:
                matches = [s for s in after.findall('.//p:sp',NS) if s.find('p:nvSpPr/p:cNvPr',NS).get('id') == str(edit.shape_id)]
                if len(matches) != 1 or ''.join(t.text or '' for t in matches[0].findall('.//a:t',NS)) != edit.replacement:
                    issues.append('Requested native text edit was not preserved')
            changed = {str(e.shape_id) for e in edits}
            for shape in before.findall('.//p:sp',NS):
                identity = shape.find('p:nvSpPr/p:cNvPr',NS).get('id')
                if identity in changed:
                    continue
                counterparts = [s for s in after.findall('.//p:sp',NS) if s.find('p:nvSpPr/p:cNvPr',NS).get('id') == identity]
                if len(counterparts) != 1 or canonical(ET.tostring(shape)) != canonical(ET.tostring(counterparts[0])):
                    issues.append('Unassigned shape changed in selected slide: '+identity)
    checks.extend(['Source input hash immutable', 'Native replacement text read back by shape ID', 'Unselected slides, relationships, masters, layouts, charts, media and workbooks byte-preserved', 'Unassigned native shapes in selected slides semantically preserved', 'Internal round-trip capacity and delivery checks; native PowerPoint preview'])
    return checks, issues


def verify_native(adapter):
    checks, issues = [], []
    with zipfile.ZipFile(adapter.directory/'design.pptx') as z:
        seen_charts=[]
        for i, (key, content) in enumerate(adapter.contents.items(),1):
            slide = ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
            rels = ET.fromstring(z.read(f'ppt/slides/_rels/slide{i}.xml.rels'))
            layout = next((r.get('Target').split('/')[-1] for r in rels if r.get('Type','').endswith('/slideLayout')),None)
            if not layout or 'ppt/slideLayouts/'+layout not in z.namelist():
                issues.append('Missing actual slide-layout relationship')
                continue
            layout_doc = ET.fromstring(z.read('ppt/slideLayouts/'+layout))
            layout_rels = ET.fromstring(z.read('ppt/slideLayouts/_rels/'+layout+'.rels'))
            master = next((r.get('Target').split('/')[-1] for r in layout_rels if r.get('Type','').endswith('/slideMaster')),None)
            if not master or 'ppt/slideMasters/'+master not in z.namelist():
                issues.append('Missing actual layout-master relationship')
            elif adapter.task.presentation and adapter.task.presentation.structure=='structured':
                contract=adapter.task.presentation
                master_doc=ET.fromstring(z.read('ppt/slideMasters/'+master))
                for role,size in [('title',contract.title_size),('body',contract.body_size)]:
                    style=master_doc.find(f'p:txStyles/p:{role}Style/a:lvl1pPr/a:defRPr',NS)
                    if style is None or int(style.get('sz','0'))!=round(size*75):
                        issues.append('Master typography does not match assignment')
            expected = [(n.native_placeholder,n.placeholder_index) for n in content.nodes if n.native_placeholder]
            types = {'subtitle':'subTitle','picture':'pic','table':'tbl','slide-number':'sldNum','footer':'ftr'}
            for role, index in expected:
                wanted = (types.get(role,role), str(index))
                for owner in (slide,layout_doc):
                    actual = {(p.get('type','obj'),p.get('idx','0')) for p in owner.findall('.//p:ph',NS)}
                    if wanted not in actual:
                        issues.append('Native placeholder type/index missing: '+str(wanted))
            if len(slide.findall('.//c:chart',NS)) != sum(n.kind == 'chart' for n in content.nodes):
                issues.append('Native chart object count mismatch')
            for chart_ref, expected_chart in zip(slide.findall('.//c:chart',NS),[n.chart for n in content.nodes if n.chart]):
                rid=chart_ref.get('{'+NS['r']+'}id')
                target=next((r.get('Target') for r in rels if r.get('Id')==rid),None)
                if not target:
                    issues.append('Chart relationship missing')
                    continue
                chart_path='ppt/charts/'+target.split('/')[-1]
                seen_charts.append(chart_path)
                chart=ET.fromstring(z.read(chart_path))
                series=chart.findall('.//c:ser',NS)
                if len(series)!=len(expected_chart.series):
                    issues.append('Chart series count mismatch')
                for actual_series,expected_series in zip(series,expected_chart.series):
                    actual_values=[float(v.text) for v in actual_series.findall('c:val/c:numRef/c:numCache/c:pt/c:v',NS)]
                    actual_categories=[v.text for v in actual_series.findall('c:cat/c:strRef/c:strCache/c:pt/c:v',NS)]
                    if actual_values!=expected_series.values or actual_categories!=expected_chart.categories:
                        issues.append('Native chart editable cache data mismatch')
                if chart.find('.//c:externalData',NS) is None:
                    issues.append('Chart is missing workbook relationship')
            tables = slide.findall('.//a:tbl',NS)
            expected_tables = [n.table for n in content.nodes if n.table]
            if len(tables) != len(expected_tables):
                issues.append('Native table object count mismatch')
            for table, expected_table in zip(tables,expected_tables):
                actual = [[''.join(t.text or '' for t in cell.findall('.//a:t',NS)) for cell in row.findall('a:tc',NS)] for row in table.findall('a:tr',NS)]
                if actual != [expected_table.columns,*expected_table.rows]:
                    issues.append('Native table cell data mismatch')
        charts = [n for n in z.namelist() if n.startswith('ppt/charts/chart') and n.endswith('.xml')]
        if adapter.task.presentation and adapter.task.presentation.structure=='structured':
            theme=ET.fromstring(z.read('ppt/theme/theme1.xml'))
            config=adapter.task.presentation
            for role,font in [('major',config.title_font),('minor',config.body_font)]:
                node=theme.find(f'.//a:{role}Font/a:latin',NS)
                if node is None or node.get('typeface')!=font:
                    issues.append('Theme font does not match assignment')
        if charts and not any(n.startswith('ppt/embeddings/') and n.endswith('.xlsx') for n in z.namelist()):
            issues.append('Native chart editable workbook missing')
        if 'native_charts' in adapter.task.required_features and not seen_charts:
            issues.append('Requested native chart feature was not produced')
        if 'native_tables' in adapter.task.required_features and not any(n.table for c in adapter.contents.values() for n in c.nodes):
            issues.append('Requested native table feature was not produced')
        if 'native_placeholders' in adapter.task.required_features and not any(n.native_placeholder for c in adapter.contents.values() for n in c.nodes):
            issues.append('Requested native placeholders were not produced')
        checks.extend(['Actual slide-layout-master relationships', 'Native placeholder type/index on slide and layout', 'Assignment master typography and theme fonts', 'Native chart objects, categories and values with embedded editable workbook', 'Native table cell text read back'])
    return checks, issues
