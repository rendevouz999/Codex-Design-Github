"""Validate a bounded passive OOXML package before any application opens it."""
from pathlib import PurePosixPath
import posixpath
import io
import re
import zipfile
from xml.etree import ElementTree as ET


def validate_pptx(path):
    if path.stat().st_size > 20_000_000:
        raise ValueError("PPTX compressed size exceeds 20 MB")
    with zipfile.ZipFile(path) as package:
        entries = package.infolist()
        names = {e.filename for e in entries}
        if len(entries) > 4000 or len(names) != len(entries) or sum(e.file_size for e in entries) > 100_000_000:
            raise ValueError("PPTX entry count, duplicate name, or expanded size limit")
        if not {"[Content_Types].xml", "ppt/presentation.xml"} <= names:
            raise ValueError("Not a PowerPoint OOXML package")
        for entry in entries:
            name = entry.filename
            parts = PurePosixPath(name).parts
            if name.startswith('/') or '\\' in name or ':' in name or '..' in parts or entry.flag_bits & 1 or (entry.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("PPTX unsafe package entry: " + name)
            low = name.lower()
            passive_printer = re.fullmatch(r'ppt/printersettings/printersettings\d+\.bin', low) is not None
            if any(v in low for v in ('vbaproject', 'activex', 'oleobject', 'externallink', '_xmlsignatures')) or low.endswith(('.exe', '.js', '.vbs', '.html')) or low.endswith('.bin') and not passive_printer:
                raise ValueError("PPTX active/unsupported part: " + name)
            if entry.file_size > 25_000_000 or entry.file_size > max(1, entry.compress_size) * 300:
                raise ValueError("PPTX excessive expansion: " + name)
            if low.endswith('.svg'):
                data=package.read(name)
                if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
                    raise ValueError('Embedded SVG entities forbidden')
                svg=ET.fromstring(data)
                for element in svg.iter():
                    if element.tag.rsplit('}',1)[-1].lower() in {'script','foreignobject','style','image','use'}:
                        raise ValueError('Active/resource-bearing embedded SVG unsupported')
                    if any(key.lower().startswith('on') or key.rsplit('}',1)[-1].lower()=='href' or 'url(' in value.lower() for key,value in element.attrib.items()):
                        raise ValueError('Embedded SVG external/resource reference unsupported')
            if low.endswith(('.xml', '.rels')):
                data = package.read(name)
                if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
                    raise ValueError("PPTX XML entities are forbidden")
                root = ET.fromstring(data)
                if b'macroenabled' in data.lower():
                    raise ValueError("PPTX macro-enabled content is unsupported")
                if low.endswith('.rels'):
                    base = posixpath.dirname(posixpath.dirname(name))
                    for relation in root:
                        target = relation.get('Target', '')
                        if relation.get('TargetMode', '').lower() == 'external' or ':' in target or '\\' in target or target.startswith('//'):
                            raise ValueError("PPTX external relationship is forbidden: " + name)
                        resolved = posixpath.normpath(posixpath.join(base, target)) if not target.startswith('/') else target[1:]
                        if resolved.startswith('../') or resolved not in names:
                            raise ValueError("PPTX missing/escaping relationship: " + name)
        # Only passive XLSX chart workbooks are accepted as embedded data.
        for name in names:
            if name.startswith('ppt/embeddings/') and not name.endswith('.xlsx'):
                raise ValueError("Unsupported embedded object: " + name)
            if name.startswith('ppt/embeddings/') and name.endswith('.xlsx'):
                with zipfile.ZipFile(io.BytesIO(package.read(name))) as book:
                    items = book.infolist()
                    if len(items)>200 or sum(i.file_size for i in items)>10_000_000:
                        raise ValueError('Embedded workbook expansion limit')
                    for item in items:
                        part=item.filename.lower()
                        if '..' in PurePosixPath(part).parts or ':' in part or '\\' in part or part.startswith('/') or item.flag_bits & 1 or any(x in part for x in ('vba','activex','embedding','externallink')):
                            raise ValueError('Unsafe embedded workbook part')
                        if not part.endswith(('.xml','.rels')):
                            raise ValueError('Unsupported embedded workbook binary')
                        data=book.read(item.filename)
                        if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
                            raise ValueError('Embedded workbook XML entities forbidden')
                        doc=ET.fromstring(data)
                        if any(n.tag.rsplit('}',1)[-1]=='f' for n in doc.iter()):
                            raise ValueError('Active workbook formulas are unsupported')
                        if any(n.get('TargetMode','').lower()=='external' for n in doc.iter()):
                            raise ValueError('Embedded workbook external relationship forbidden')
        return {"entries": len(entries), "expanded_bytes": sum(e.file_size for e in entries)}
