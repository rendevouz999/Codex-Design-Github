"""Compile typed content into safe editable SVG and existing native metadata."""
import json
from xml.etree import ElementTree as ET


def svg_content(content, unit, presentation=None):
    root = ET.Element('svg', xmlns='http://www.w3.org/2000/svg', width=str(unit.width), height=str(unit.height), viewBox=f'0 0 {unit.width} {unit.height}')
    if presentation and presentation.structure == 'structured':
        root.attrib.update({'data-pptx-master': 'main', 'data-pptx-master-name': 'Assigned theme', 'data-pptx-layout': unit.layout, 'data-pptx-layout-name': unit.layout})
    for n in content.nodes:
        parent = root
        attrs = {'id': n.id, 'fill': n.fill, 'stroke': n.stroke, 'stroke-width': str(n.stroke_width)}
        if n.native_placeholder:
            parent = ET.SubElement(root, 'g', {'id': n.id, 'data-pptx-placeholder': n.native_placeholder, 'data-pptx-idx': str(n.placeholder_index), 'data-pptx-bounds': f'{n.x} {n.y} {n.width} {n.height}'})
            attrs['id'] += '-carrier'
            attrs['data-pptx-carrier'] = 'true'
        elif n.layer != 'slide':
            attrs.update({'data-pptx-layer': n.layer, 'data-pptx-editable': 'false'})
        if n.native_placeholder == 'picture':
            # Fixed transparent carrier enables a real native empty picture slot.
            # Its clue remains editable text, supplied by the typed authoring node.
            attrs.update(x=str(n.x),y=str(n.y),width=str(n.width),height=str(n.height),href='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR4nGNgAAIAAAUAAXpeqz8AAAAASUVORK5CYII=')
            ET.SubElement(parent,'image',attrs)
        elif n.kind in {'chart', 'table'}:
            attrs.update({'data-pptx-bounds': f'{n.x} {n.y} {n.width} {n.height}', 'data-pptx-replace-with': n.kind, 'data-pptx-native-authority': 'json'})
            group = ET.SubElement(parent, 'g', attrs)
            data = (n.chart or n.table).model_dump()
            data.update(name=n.id, x=n.x, y=n.y, width=n.width, height=n.height)
            if n.kind == 'table':
                data.update(schema='ppt-master.semantic-table.v2', style={'font_family': n.font, 'font_size': n.font_size, 'header_font_size': n.font_size, 'header_text': n.fill, 'body_text': n.fill, 'border_width': 0})
                rows = [n.table.columns, *n.table.rows]
                for ri, row in enumerate(rows):
                    for ci, value in enumerate(row):
                        t = ET.SubElement(group, 'text', x=str(n.x+8+ci*n.width/len(row)), y=str(n.y+n.font_size+ri*n.height/len(rows)), fill=n.fill, **{'font-family': n.font, 'font-size': str(n.font_size)})
                        t.text = value
            else:
                data.update(show_legend=len(n.chart.series)>1, style={'colors': [presentation.accent if presentation else '#315A73'], 'font_family': n.font, 'text_color': n.fill})
                # A compact readable data fallback; PPTX replaces it with the native object.
                rows = [f'{c}: ' + ', '.join(str(s.values[i]) for s in n.chart.series) for i,c in enumerate(n.chart.categories)]
                for i, value in enumerate(rows):
                    t = ET.SubElement(group, 'text', x=str(n.x+8), y=str(n.y+n.font_size+i*(n.font_size+6)), fill=n.fill, **{'font-family': n.font, 'font-size': str(n.font_size)})
                    t.text = value
            ET.SubElement(group, 'metadata', type='application/json').text = json.dumps(data)
        elif n.kind == 'text_frame':
            ET.SubElement(parent, 'g', {'id': n.id, 'data-story': n.story_id})
        else:
            if n.kind == 'ellipse':
                attrs.update(cx=str(n.x+n.width/2), cy=str(n.y+n.height/2), rx=str(n.width/2), ry=str(n.height/2))
            elif n.kind == 'line':
                attrs.update(x1=str(n.x), y1=str(n.y), x2=str(n.x+n.width), y2=str(n.y+n.height))
            else:
                attrs.update(x=str(n.x), y=str(n.y+n.font_size if n.kind == 'text' else n.y))
            if n.kind == 'rect':
                attrs.update(width=str(n.width), height=str(n.height), rx=str(n.radius))
            if n.kind == 'text':
                font,size=n.font,n.font_size
                if presentation and n.native_placeholder in {'title','body'}:
                    title=n.native_placeholder=='title'
                    font=presentation.title_font if title else presentation.body_font
                    size=presentation.title_size if title else presentation.body_size
                    attrs['y']=str(n.y+size)
                attrs.update({'font-family': font, 'font-size': str(size), 'font-weight': '700' if n.bold else '400', 'data-placeholder': str(n.placeholder).lower()})
            element = ET.SubElement(parent, n.kind, attrs)
            if n.kind == 'text':
                element.text = n.text
    return ET.tostring(root, encoding='unicode')
