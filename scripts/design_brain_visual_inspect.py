#!/usr/bin/env python
"""Prepare lossless inspection views and validate explicit visual-review evidence.

This local tool neither calls a model nor proves that a reviewer saw an image.
Opening its PNGs and supplying honest observations remain host-agent duties.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import uuid
import warnings
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile, BadZipFile
from xml.etree import ElementTree

from PIL import Image, ImageOps

sys.dont_write_bytecode = True
MAX_PIXELS = 64_000_000  # Local resource bound, not a model image limit.
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,95}$")
LIMITATION = "Hashes/pixel checks validate evidence integrity. Review attestations do not cryptographically prove actual seeing or creative quality."


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def file_ref(path):
    path = Path(path).resolve()
    need(path.is_file(), f"Missing file: {path}")
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def current(ref):
    need(isinstance(ref, dict) and isinstance(ref.get('path'), str), 'Invalid file reference')
    need(Path(ref['path']).is_absolute(), 'Evidence paths must be absolute')
    need(file_ref(ref['path'])['sha256'] == ref.get('sha256'), f"Stale file: {ref['path']}")
    return Path(ref['path'])


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def original(path):
    with warnings.catch_warnings():
        warnings.simplefilter('error', Image.DecompressionBombWarning)
        with Image.open(path) as image:
            need(getattr(image, 'n_frames', 1) == 1, 'Animated/multipage images need an explicitly extracted static frame')
            need(image.width * image.height <= MAX_PIXELS, 'Source exceeds local pixel resource bound')
            return ImageOps.exif_transpose(image).convert('RGBA')


def fitted(size, max_edge, upscale=False):
    need(type(max_edge) is int and 1 <= max_edge <= 8192, 'max_edge must be an integer from1 to8192')
    scale = max_edge / max(size)
    if not upscale:
        scale = min(scale, 1)
    return [max(1, round(size[0] * scale)), max(1, round(size[1] * scale))]


def box(value, size):
    need(isinstance(value, (list, tuple)) and len(value) == 4 and all(type(v) is int for v in value), 'Box requires four integer pixel edges; booleans/floats are invalid')
    x1, y1, x2, y2 = value
    need(0 <= x1 < x2 <= size[0] and 0 <= y1 < y2 <= size[1], 'Box is reversed, empty or outside the named view; clipping is not allowed')
    return list(value)


def root_box(view, requested):
    x1, y1, x2, y2 = box(requested, view['size_px'])
    left, top, right, bottom = view['source_box_px']
    sx = (right - left) / view['size_px'][0]
    sy = (bottom - top) / view['size_px'][1]
    return [left + math.floor(x1 * sx), top + math.floor(y1 * sy),
            left + math.ceil(x2 * sx), top + math.ceil(y2 * sy)]


def pptx_frames(path):
    if Path(path).suffix.lower() != '.pptx':
        return None
    with ZipFile(path) as z:
        xml = ElementTree.fromstring(z.read('ppt/presentation.xml'))
    ns = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
    count = len(xml.find(ns + 'sldIdLst'))
    need(count > 0, 'PPTX has no slides')
    return [f'slide-{n:03}' for n in range(1, count + 1)]


def coverage(artifact, inventory):
    expected = pptx_frames(artifact['path'])
    result = {'expected_frame_ids': expected or []}
    if inventory:
        inv_ref = file_ref(inventory); payload = load(inventory)
        need(payload.get('artifact_sha256') == artifact['sha256'], 'Render inventory artifact hash is stale')
        rows = payload.get('frames')
        need(isinstance(rows, list) and rows, 'Render inventory must list nonempty frames')
        names = [row['id'] for row in rows]
        need(len(names) == len(set(names)) and all(isinstance(n, str) and ID.fullmatch(n) for n in names), 'Invalid/duplicate inventory frame IDs')
        need(expected is None or set(expected) == set(names), 'Render inventory does not cover actual PPTX slide count')
        result.update(expected_frame_ids=expected or names, render_inventory=inv_ref)
    need(result['expected_frame_ids'], 'Non-PPTX artifacts require --inventory with declared render frame coverage')
    return result


def save_manifest(path, payload):
    path = Path(path).resolve()
    protected = [Path(payload['artifact']['path']).resolve()] + [Path(f['source']['path']).resolve() for f in payload['frames']]
    protected += [Path(v['file']['path']).resolve() for f in payload['frames'] for v in f['views']]
    if payload['coverage'].get('render_inventory'):
        protected.append(Path(payload['coverage']['render_inventory']['path']).resolve())
    need(path not in protected, 'Manifest must not overwrite artifact/source')
    loaded_hash = payload.pop('__loaded_file_sha256', None)
    if path.exists():
        existing = load(path)
        need(existing.get('schema_version') == 1 and existing.get('artifact') == payload['artifact'], 'Refusing unrelated existing manifest')
        need(loaded_hash == file_ref(path)['sha256'], 'Manifest changed during operation; reconcile before retry')
    else:
        need(loaded_hash is None, 'Existing manifest disappeared during operation')
    payload['status'] = 'EVIDENCE_PREPARED'
    payload['review_status'] = 'UNVERIFIED'
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temporary.open('x', encoding='utf-8') as handle:
            handle.write(json.dumps(payload, indent=2)); handle.flush(); os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def add_view(frame, image, output_dir, name, kind, source_box, max_edge, parent=None, parent_box=None, forbidden=()):
    need(isinstance(name, str) and ID.fullmatch(name), 'Invalid view ID')
    need(not any(v['id'] == name for v in frame['views']), 'View ID already exists; prepare a new inspection instead of overwriting')
    crop = image.crop(source_box)
    size = fitted(crop.size, max_edge, upscale=kind == 'detail')
    need(size[0] * size[1] <= MAX_PIXELS, 'View output exceeds local pixel resource bound')
    output = Path(output_dir).resolve() / f"{frame['id'].replace(':', '_')}--{name.replace(':', '_')}.png"
    need(output not in {Path(p).resolve() for p in forbidden}, 'View output must not replace manifest/source/artifact/inventory')
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents overwriting originals, earlier views or unrelated files.
    with output.open('xb') as handle:
        crop.resize(size, Image.Resampling.LANCZOS).save(handle, format='PNG')
    view = {'id': name, 'kind': kind, 'file': file_ref(output), 'size_px': size,
            'source_box_px': source_box, 'parent_view_id': parent['id'] if parent else None,
            'parent_view_sha256': parent['file']['sha256'] if parent else None,
            'parent_box_px': parent_box, 'coordinates': 'absolute half-open pixels; top-left origin; EXIF-oriented source'}
    frame['views'].append(view)
    return view


def prepare(image, artifact, frame_id, output_dir, manifest, max_edge=1600, inventory=None, render_method=None):
    need(isinstance(frame_id, str) and ID.fullmatch(frame_id), 'Invalid frame ID')
    artifact_ref = file_ref(artifact)
    existing_hash = file_ref(manifest)['sha256'] if Path(manifest).exists() else None
    m = load(manifest) if existing_hash else {
        'schema_version': 1, 'artifact': artifact_ref, 'coverage': coverage(artifact_ref, inventory),
        'frames': [], 'checks': [], 'reviews': [], 'main_approval': None,
        'status': 'EVIDENCE_PREPARED', 'review_status': 'UNVERIFIED'}
    m['__loaded_file_sha256'] = existing_hash
    need(m.get('schema_version') == 1 and m.get('artifact') == artifact_ref, 'Existing inspection belongs to another/stale artifact')
    need(frame_id in m['coverage']['expected_frame_ids'], 'Frame is outside declared artifact coverage')
    need(not any(f['id'] == frame_id for f in m['frames']), 'Frame already exists')
    source = file_ref(image); decoded = original(image)
    frame = {'id': frame_id, 'source': source, 'oriented_size_px': list(decoded.size),
             'display_orientation': 'exif_transposed', 'render_binding': {'artifact_sha256': artifact_ref['sha256'], 'method': render_method or ''}, 'views': []}
    if m['coverage'].get('render_inventory'):
        inv = load(current(m['coverage']['render_inventory']))
        row = next(r for r in inv['frames'] if r['id'] == frame_id)
        need(row['image'] == source, 'Source is not the current frame image in render inventory')
        frame['render_binding']['method'] = render_method or inv.get('method', '')
    protected = [image, artifact, manifest]
    if m['coverage'].get('render_inventory'):
        protected.append(m['coverage']['render_inventory']['path'])
    view = add_view(frame, decoded, output_dir, 'overview', 'overview', [0, 0, *decoded.size], max_edge, forbidden=protected)
    m['frames'].append(frame)
    m['checks'].extend([
        {'id': frame_id + ':composition', 'frame_id': frame_id, 'prompt': 'Inspect the complete frame: meaning, density, hierarchy, alignment, margins and visible numbering/footers where applicable.', 'critical': True, 'requires_detail': False},
        {'id': frame_id + ':detail', 'frame_id': frame_id, 'prompt': 'Inspect relevant small text, boundaries, labels or photographic details in original-source crops, then return to the full composition.', 'critical': True, 'requires_detail': True}])
    save_manifest(manifest, m)
    return {'status': 'EVIDENCE_PREPARED', 'review_status': 'UNVERIFIED', 'view': view,
            'next_action': 'Open the overview with an actual host image tool, identify detail questions, crop and inspect; supply honest observations.', 'limitation': LIMITATION}


def crop(manifest, frame_id, view_id, requested, name, max_edge=1600):
    initial_hash = file_ref(manifest)['sha256']; m = load(manifest); validate_evidence(m)
    m['__loaded_file_sha256'] = initial_hash
    frame = next(f for f in m['frames'] if f['id'] == frame_id)
    parent = next(v for v in frame['views'] if v['id'] == view_id)
    requested = box(requested, parent['size_px']); mapped = root_box(parent, requested)
    need(mapped != parent['source_box_px'], 'A whole-view duplicate is not detail evidence')
    image = original(current(frame['source']))
    protected = [manifest, m['artifact']['path']] + [f['source']['path'] for f in m['frames']]
    if m['coverage'].get('render_inventory'):
        protected.append(m['coverage']['render_inventory']['path'])
    view = add_view(frame, image, Path(parent['file']['path']).parent, name, 'detail', mapped, max_edge, parent, requested, protected)
    m['main_approval'] = None  # New evidence needs an explicit current Main decision.
    save_manifest(manifest, m)
    return {'status': 'EVIDENCE_PREPARED', 'review_status': 'UNVERIFIED', 'view': view,
            'next_action': 'Open this detail and then the original overview. Enlargement adds no source detail; unresolved questions must remain unresolved.', 'limitation': LIMITATION}


def validate_evidence(m, require_coverage=False):
    need(isinstance(m, dict) and m.get('schema_version') == 1, 'Unsupported inspection schema')
    current(m['artifact'])
    expected = m['coverage']['expected_frame_ids']
    need(isinstance(expected, list) and expected and len(set(expected)) == len(expected), 'Missing/duplicate frame coverage inventory')
    actual = pptx_frames(m['artifact']['path'])
    need(actual is None or set(actual) == set(expected), 'Coverage does not match actual PPTX slide count')
    inventory = m['coverage'].get('render_inventory')
    need(actual is not None or inventory, 'Non-PPTX source lacks render inventory')
    rows = None
    if inventory:
        inv = load(current(inventory)); rows = inv['frames']
        need(inv['artifact_sha256'] == m['artifact']['sha256'], 'Stale render inventory artifact')
        need(len(rows) == len(expected) and {r['id'] for r in rows} == set(expected), 'Render inventory/frame coverage mismatch')
    frames = m['frames']; ids = [f['id'] for f in frames]
    need(frames and len(ids) == len(set(ids)) and set(ids) <= set(expected), 'Missing, duplicate or unknown frames')
    if require_coverage:
        need(set(ids) == set(expected), 'Not every artifact frame has been prepared/reviewed')
    for frame in frames:
        path = current(frame['source']); image = original(path)
        need(list(image.size) == frame['oriented_size_px'] and frame['display_orientation'] == 'exif_transposed', 'Source orientation/size changed')
        need(frame['render_binding']['artifact_sha256'] == m['artifact']['sha256'], 'Frame is bound to another artifact')
        if require_coverage:
            need(isinstance(frame['render_binding'].get('method'), str) and len(frame['render_binding']['method'].strip()) >= 10, 'Meaningful actual render/capture provenance method required')
        if rows:
            need(next(r for r in rows if r['id'] == frame['id'])['image'] == frame['source'], 'Frame/source render inventory mismatch')
        views = frame['views']; by_id = {v['id']: v for v in views}
        need(views and len(views) == len(by_id), 'Missing/duplicate views')
        need(sum(v['kind'] == 'overview' for v in views) == 1, 'Each frame needs one complete overview')
        for v in views:
            source_box = box(v['source_box_px'], image.size); size = v['size_px']
            need(len(size) == 2 and all(type(n) is int and n > 0 for n in size) and size[0] * size[1] <= MAX_PIXELS, 'Invalid view dimensions')
            rw, rh = source_box[2] - source_box[0], source_box[3] - source_box[1]
            need(abs(size[0] * rh - size[1] * rw) <= max(rw, rh), 'Stretched/letterboxed view mapping is unsupported')
            if v['kind'] == 'overview':
                need(source_box == [0, 0, *image.size] and v['parent_view_id'] is None, 'Overview must cover the whole oriented source')
            else:
                need(v['kind'] == 'detail' and v['parent_view_id'] in by_id, 'Invalid detail lineage')
                parent = by_id[v['parent_view_id']]
                need(parent is not v and parent['file']['sha256'] == v['parent_view_sha256'], 'Stale/cyclic parent view')
                need(root_box(parent, v['parent_box_px']) == source_box and source_box != parent['source_box_px'], 'Detail/root coordinate mapping is inconsistent')
            view_path = current(v['file'])
            with Image.open(view_path) as rendered:
                need(rendered.format == 'PNG' and list(rendered.size) == size, 'View format/size changed')
                expected_pixels = image.crop(source_box).resize(size, Image.Resampling.LANCZOS)
                need(rendered.convert('RGBA').tobytes() == expected_pixels.tobytes(), 'View pixels do not match original-source crop/resize')


def verify_manifest(path, stage='final', expected_artifact=None):
    result = {'status': 'FAIL', 'evidence_status': 'INVALID', 'review_status': 'UNVERIFIED', 'issues': [], 'limitation': LIMITATION}
    try:
        need(stage in ['engineer', 'final'], 'Unsupported review stage')
        m = load(path); validate_evidence(m, require_coverage=True)
        if stage == 'final':
            need(expected_artifact is not None, 'Final verification requires the expected artifact target')
        if expected_artifact is not None:
            expected = expected_artifact if isinstance(expected_artifact, dict) else file_ref(expected_artifact)
            current(expected)
            need(m['artifact'] == expected, 'Inspection is for another artifact target/path/hash')
        result['evidence_status'] = 'VERIFIED'
        checks = m['checks']; names = [c['id'] for c in checks]
        frame_ids = {f['id'] for f in m['frames']}
        need(checks and len(names) == len(set(names)), 'Mandatory nonempty unique checks required')
        need({c['frame_id'] for c in checks} == frame_ids, 'Every artifact frame must have checks')
        need(all(type(c['critical']) is bool and type(c['requires_detail']) is bool and isinstance(c['prompt'], str) and len(c['prompt'].strip()) >= 20 for c in checks), 'Malformed/empty inspection questions')
        roles = ['engineer', 'main'] if stage == 'final' else ['engineer']
        for frame in m['frames']:
            frame_checks = [c for c in checks if c['frame_id'] == frame['id']]
            need(any(c['critical'] and c['requires_detail'] for c in frame_checks), 'Every frame needs a critical detail question')
            by_view = {v['id']: v for v in frame['views']}
            for check in frame_checks:
                for role in roles:
                    rows = [r for r in m['reviews'] if r['role'] == role and r['frame_id'] == frame['id'] and r['check_id'] == check['id']]
                    need(len(rows) == 1, f"One current {role} observation required for {check['id']}")
                    r = rows[0]
                    need(r['artifact_sha256'] == m['artifact']['sha256'] and r['source_sha256'] == frame['source']['sha256'] and r['check_sha256'] == digest(check), 'Stale review/source/question binding')
                    need(r['verdict'] in ['pass', 'fail', 'unresolved'], 'Unknown review verdict')
                    need(isinstance(r['observation'], str) and len(r['observation'].strip()) >= 20, 'Empty/placeholder review observation')
                    viewed = r['actual_views']; need(isinstance(viewed, list) and viewed, 'Actual-view attestations missing')
                    times = []
                    for entry in viewed:
                        need(entry['view_id'] in by_view and entry['sha256'] == by_view[entry['view_id']]['file']['sha256'], 'Stale/unknown actual-view attestation')
                        need(entry.get('actually_viewed') is True and entry.get('tool') in ['view_image', 'browser', 'host_image_tool'] and len(str(entry.get('evidence_note', '')).strip()) >= 10, 'Actual host-view tool evidence missing')
                        timestamp = datetime.fromisoformat(entry['viewed_at'].replace('Z', '+00:00')); need(timestamp.tzinfo is not None, 'View timestamp must include timezone'); times.append(timestamp)
                    need(all(a < b for a, b in zip(times, times[1:])), 'Actual views must be chronological')
                    kinds = [by_view[e['view_id']]['kind'] for e in viewed]
                    need(kinds[0] == 'overview' and kinds[-1] == 'overview', 'Inspect overview and return to full context')
                    if check['requires_detail']:
                        need(len(kinds) >= 3 and 'detail' in kinds[1:-1], 'Required sequence is overview→detail→overview')
                    need(set(r['view_ids']) == {e['view_id'] for e in viewed}, 'Review view IDs disagree with actual-view evidence')
                    if r['verdict'] != 'pass':
                        result['review_status'] = 'REVISE_REQUIRED'
                        raise ValueError(f"{role} {check['id']} remains {r['verdict']}; no inferred readability/PASS")
        if stage == 'final':
            approval = m.get('main_approval')
            need(isinstance(approval, dict) and approval.get('verdict') == 'accept', 'Explicit Main approval required')
            need(approval.get('artifact_sha256') == m['artifact']['sha256'] and approval.get('check_set_sha256') == digest(checks), 'Stale Main approval')
            need(len(str(approval.get('reason', '')).strip()) >= 20, 'Main approval reason missing')
            result['review_status'] = 'MAIN_ACCEPTED'
        else:
            result['review_status'] = 'ENGINEER_REVIEWED'
        result['status'] = 'PASS'
    except (ValueError, KeyError, TypeError, AttributeError, IndexError, OSError, StopIteration, OverflowError, ZeroDivisionError, BadZipFile, ElementTree.ParseError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        result['issues'].append(str(exc))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest='command', required=True)
    a = sub.add_parser('prepare')
    for flag in ['image', 'artifact', 'frame-id', 'output-dir', 'manifest']:
        a.add_argument('--' + flag, required=True)
    a.add_argument('--inventory'); a.add_argument('--render-method', help='Actual render/capture method; otherwise use inventory method or remain unverified'); a.add_argument('--max-edge', type=int, default=1600)
    a = sub.add_parser('crop')
    for flag in ['manifest', 'frame-id', 'view-id', 'name']:
        a.add_argument('--' + flag, required=True)
    a.add_argument('--box', type=int, nargs=4, required=True); a.add_argument('--max-edge', type=int, default=1600)
    a = sub.add_parser('verify'); a.add_argument('--manifest', required=True); a.add_argument('--artifact', help='Expected current artifact; required for final verification'); a.add_argument('--stage', choices=['engineer', 'final'], default='final'); a.add_argument('--json', action='store_true')
    args = vars(p.parse_args()); command = args.pop('command')
    try:
        if command == 'verify':
            args.pop('json'); result = verify_manifest(args['manifest'], args['stage'], args['artifact'])
        elif command == 'prepare':
            result = prepare(**args)
        else:
            args['requested'] = args.pop('box'); result = crop(**args)
        print(json.dumps(result, indent=2))
        return 1 if result['status'] == 'FAIL' else 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError, IndexError, OverflowError, ZeroDivisionError, BadZipFile, StopIteration, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        print(json.dumps({'status': 'FAIL', 'evidence_status': 'INVALID', 'review_status': 'UNVERIFIED', 'error': str(exc)})); return 1


if __name__ == '__main__':
    raise SystemExit(main())
