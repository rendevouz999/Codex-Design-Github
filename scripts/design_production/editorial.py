"""Linked editable stories use Chromium's installed-font measurement engine."""
import json
import shutil
from pathlib import Path


async def reflow(adapter):
    settings = adapter.task.editorial
    stories = {}
    for content in adapter.contents.values():
        for story in content.stories:
            if story.id in stories:
                raise ValueError('Duplicate editorial story ID')
            if story.style not in {s.id for s in settings.styles}:
                raise ValueError('Unknown editorial typography style')
            stories[story.id] = story.model_dump()
    frames = []
    page_boxes = []
    for unit in adapter.task.units:
        b=settings.bleed
        page_boxes.append(dict(unit=unit.id,media_box=[0,0,unit.width,unit.height],trim_box=[b,b,unit.width-2*b,unit.height-2*b]))
        previous={}
        for node in adapter.contents[unit.id].nodes:
            if node.kind == 'text_frame':
                if node.story_id not in stories:
                    raise ValueError('Text frame references an absent story')
                m = settings.margin + settings.bleed
                column_width = (unit.width-2*m-(settings.columns-1)*settings.gutter)/settings.columns
                column = round((node.x-m)/(column_width+settings.gutter))
                if column_width <= 0 or column not in range(settings.columns) or abs(node.x-(m+column*(column_width+settings.gutter))) > .5 or node.width > column_width+.5 or node.y < m or node.y+node.height > unit.height-m:
                    raise ValueError('Text frame violates editorial margin/column/gutter contract')
                order=(column,node.y)
                if node.story_id in previous and order <= previous[node.story_id]:
                    raise ValueError('Linked frame reading order reverses columns or rows')
                previous[node.story_id]=order
                for frame in frames:
                    if frame['unit']==unit.id and node.x<frame['x']+frame['width'] and node.x+node.width>frame['x'] and node.y<frame['y']+frame['height'] and node.y+node.height>frame['y']:
                        raise ValueError('Editorial text frames overlap')
                frames.append(dict(unit=unit.id, **node.model_dump()))
    if set(stories) != {f['story_id'] for f in frames}:
        raise ValueError('Every story requires at least one linked frame')
    source = adapter.directory / 'publication.json'
    source.write_text(json.dumps({'settings':settings.model_dump(),'pages':page_boxes,'stories':list(stories.values()),'frames':frames},indent=2),encoding='utf-8')
    await adapter.process([shutil.which('node'),str(Path(__file__).with_name('editorial_reflow.mjs')),str(adapter.directory)],60)
    # Reflow changes editable SVG sources before their final hashes are registered.
    adapter.manifests = [m for m in adapter.manifests if m.format != 'svg']
    for key in adapter.units:
        adapter.manifest(adapter.directory/(key+'.svg'),'deliverable',True,[key])
    adapter.manifest(source,'source',True)
    adapter.manifest(adapter.directory/'flow-receipt.json','evidence')


def verify_flow(adapter):
    document = json.loads((adapter.directory/'publication.json').read_text())
    receipt = json.loads((adapter.directory/'flow-receipt.json').read_text())
    issues = list(receipt['issues'])
    for story in document['stories']:
        segments = [f for f in receipt['frames'] if f['story_id']==story['id']]
        cursor = 0
        for frame in segments:
            if frame['start'] != cursor or story['text'][frame['start']:frame['end']] != frame['text']:
                issues.append('Lost, duplicated or reordered story text: '+story['id'])
            cursor = frame['end']
        if cursor != len(story['text']):
            issues.append('Overset story: '+story['id']+'; remaining '+str(len(story['text'])-cursor))
    return ['Linked story/frame IDs retained in editable JSON and SVG', 'Contiguous source offsets prove no missing/duplicated text', 'Chromium font measurement, line capacity, grid, reading order and overset checked'], issues
