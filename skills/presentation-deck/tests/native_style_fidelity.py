"""Compare chart/table formatting independently of changed data values."""
import argparse
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
def signature(node):
    if node is None:return None
    return [node.tag,sorted(node.attrib.items()),(node.text or '').strip(),[signature(c) for c in node]]
def read(path):
    with zipfile.ZipFile(path) as z:
        slide=ET.fromstring(z.read('ppt/slides/slide1.xml'))
        chart=ET.fromstring(z.read(next(n for n in z.namelist() if n.startswith('ppt/charts/chart') and n.endswith('.xml'))))
        cells=[signature(c.find('a:tcPr',NS)) for c in slide.findall('.//a:tbl/a:tr/a:tc',NS)]
        axes=[]
        for kind in ('catAx','dateAx','valAx'):
            for a in chart.findall('.//c:'+kind,NS):
                axes.append({key:signature(a.find('c:'+key,NS)) for key in ('spPr','txPr')})
        return {'tableCellProperties':cells,'chartAxes':axes,'chartTypography':signature(chart.find('c:txPr',NS))}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('before');p.add_argument('after');p.add_argument('--report',required=True);a=p.parse_args()
    before,after=read(a.before),read(a.after)
    comparison={k:before[k]==after[k] for k in before}
    result={'status':'PASS' if all(comparison.values()) else 'FAIL','checks':comparison,'before':before,'after':after}
    Path(a.report).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'checks':comparison}))
    raise SystemExit(0 if result['status']=='PASS' else 1)
