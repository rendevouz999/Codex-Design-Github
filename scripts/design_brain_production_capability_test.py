"""Focused capability acceptance through the existing runtime and SDK mock."""
import json
from pathlib import Path
import unittest
import zipfile
import io
from xml.etree import ElementTree as ET

import design_brain_production_smoke_test as baseline
from design_production.policy import digest


class Capabilities(baseline.Acceptance):
    def sources(self, contents):
        return [dict(id='source-'+str(i), path=str(p), sha256=digest(p), role='editable_source') for i,c in enumerate(contents) for p in [self.write(c)]]

    def native_fixture(self):
        def text_node(identity, text, y, role, idx, size=28):
            return dict(id=identity,kind='text',x=64,y=y,width=1100,height=90,text=text,font_size=size,fill='#17243B',native_placeholder=role,placeholder_index=idx)
        background = dict(id='background',kind='rect',x=0,y=0,width=1280,height=720,fill='#FFFFFF',layer='master')
        cover = dict(unit_id='cover',nodes=[background,text_node('title','Systems review',70,'title',0,44),text_node('body','Reusable native source',210,'body',1)])
        data = dict(unit_id='data',nodes=[background,text_node('title','Measured outcomes',40,'title',0,44),
            dict(id='chart',kind='chart',x=64,y=180,width=560,height=380,font_size=24,fill='#17243B',native_placeholder='chart',placeholder_index=1,chart=dict(type='column',categories=['Q1','Q2'],series=[dict(name='Revenue',values=[12,18])])),
            dict(id='table',kind='table',x=700,y=180,width=500,height=250,font_size=24,fill='#17243B',native_placeholder='table',placeholder_index=2,table=dict(columns=['Period','Revenue'],rows=[['Q1','12'],['Q2','18']]))])
        picture=dict(unit_id='picture',nodes=[background,
            dict(id='image-panel',kind='rect',x=64,y=180,width=1120,height=400,fill='#EAF0F7',layer='layout'),
            dict(id='image-clue',kind='text',x=100,y=350,width=1000,height=50,text='image placeholder: supporting evidence',font_size=24,fill='#17243B',layer='layout'),
            text_node('title','Image role',40,'title',0,44),
            dict(id='image-slot',kind='rect',x=64,y=180,width=1120,height=400,fill='none',native_placeholder='picture',placeholder_index=1)])
        contents=[cover,data,picture]
        spec = self.spec(artifact_type='presentation',output_format='pptx',required_features=['slide_masters','native_placeholders','theme','native_charts','native_tables'],
            units=[dict(id=c['unit_id'],kind='slide',width=1280,height=720,instruction='Native structural integration fixture',layout=c['unit_id']) for c in contents],
            presentation=dict(structure='structured',reusable_template=True,title_size=44,body_size=28,title_font='Arial',body_font='Arial',background='#FFFFFF',foreground='#17243B',accent='#315A73'),
            inputs=[self.spec()['inputs'][0],*self.sources(contents)])
        return self.start(spec)[0]

    def test_20_structured_native_and_edit(self):
        result = self.native_fixture()
        job = result['job']
        self.assertEqual(job['result']['qa']['status'],'PASS',job)
        pptx = Path(next(m['path'] for m in job['result']['artifacts'] if m['format']=='pptx'))
        ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
        with zipfile.ZipFile(pptx) as z:
            master=ET.fromstring(z.read('ppt/slideMasters/slideMaster1.xml'))
            self.assertEqual(master.find('p:txStyles/p:titleStyle/a:lvl1pPr/a:defRPr',ns).get('sz'),'3300')
            self.assertGreaterEqual(len([n for n in z.namelist() if n.startswith('ppt/slideLayouts/slideLayout') and n.endswith('.xml')]),2)
            slide=ET.fromstring(z.read('ppt/slides/slide1.xml'))
            shape=next(s for s in slide.findall('.//p:sp',ns) if ''.join(t.text or '' for t in s.findall('.//a:t',ns))=='Systems review')
            shape_id=int(shape.find('p:nvSpPr/p:cNvPr',ns).get('id'))
        before=digest(pptx)
        content=dict(unit_id='selected',edits=[dict(shape_id=shape_id,expected='Systems review',replacement='Systems update')])
        spec=self.spec(operation='edit',artifact_type='presentation',output_format='pptx',required_features=['existing_pptx_text_edit'],
            units=[dict(id='selected',kind='slide',width=1280,height=720,instruction='Replace assigned title only',source_slide=1)],
            inputs=[self.spec()['inputs'][0],dict(id='pptx',path=str(pptx),sha256=before,role='editable_source'),*self.sources([content])],
            presentation=dict(structure='preserve',title_size=44,body_size=28,title_font='Arial',body_font='Arial',background='#FFFFFF',foreground='#17243B',accent='#315A73'))
        edited,_=self.start(spec)
        self.assertEqual(edited['job']['result']['qa']['status'],'PASS',edited)
        self.assertEqual(digest(pptx),before)
        # Reuse the actual editable source and change native data through SDK tools.
        native_inputs=[self.spec()['inputs'][0]]+[dict(id='native-'+u['id'],path=str(Path(job['directory'])/(u['id']+'.json')),sha256=digest(Path(job['directory'])/(u['id']+'.json')),role='editable_source') for u in job['task']['units']]
        changed_spec=dict(job['task'],parent_request_id=job['task']['parent_request_id']+'-data',operation='edit',inputs=native_inputs)
        changed_spec['presentation']=dict(changed_spec['presentation'],title_size=48,body_size=30,title_font='Georgia',body_font='Georgia',accent='#AA4422')
        data_edit,_=self.start(changed_spec)
        output=Path(next(m['path'] for m in data_edit['job']['result']['artifacts'] if m['format']=='pptx' and m['role']=='deliverable'))
        with zipfile.ZipFile(output) as z:
            master=ET.fromstring(z.read('ppt/slideMasters/slideMaster1.xml'))
            self.assertEqual(master.find('p:txStyles/p:titleStyle/a:lvl1pPr/a:defRPr',ns).get('sz'),'3600')
            theme=z.read('ppt/theme/theme1.xml').decode()
            self.assertIn('Georgia',theme)
            self.assertIn('AA4422',theme)
            chart=ET.fromstring(z.read(next(n for n in z.namelist() if n.startswith('ppt/charts/chart') and n.endswith('.xml'))))
            cns={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
            self.assertEqual(float(chart.find('.//c:ser/c:val/c:numRef/c:numCache/c:pt/c:v',cns).text),13)
        self.assertEqual(digest(pptx),before)

    def test_21_editorial_reflow_and_overset(self):
        story='A publication keeps its reading order across linked frames. '*25
        def pages(text):
            result=[]
            for i in range(2):
                result.append(dict(unit_id='page-'+str(i+1),stories=[dict(id='article',style='body',text=text)] if i==0 else [],nodes=[
                    dict(id='paper',kind='rect',x=0,y=0,width=600,height=800,fill='#FFFFFF'),
                    dict(id='heading',kind='text',x=40,y=45,width=520,height=55,font_size=30,text='Editorial systems',fill='#17243B'),
                    dict(id='left',kind='text_frame',x=40,y=140,width=250,height=570,story_id='article'),
                    dict(id='right',kind='text_frame',x=310,y=140,width=250,height=570,story_id='article'),
                    dict(id='caption',kind='text',x=40,y=735,width=460,height=25,font_size=14,text='Linked publication source / '+str(i+1),fill='#17243B')]))
            return result
        def spec(text,operation='create'):
            contents=pages(text)
            return self.spec(artifact_type='editorial_svg',operation=operation,required_features=['linked_text_flow','editorial_grid'],
                units=[dict(id=c['unit_id'],kind='page',width=600,height=800,instruction='Two-column publication fixture') for c in contents],
                editorial=dict(margin=40,columns=2,gutter=20,bleed=0,styles=[dict(id='body',font='Georgia',size=18,leading=26,color='#17243B')]),
                inputs=[self.spec()['inputs'][0],*self.sources(contents)])
        initial,_=self.start(spec(story))
        directory=Path(initial['job']['directory'])
        receipt=json.loads((directory/'flow-receipt.json').read_text())
        self.assertGreater(sum(bool(f['text']) for f in receipt['frames']),1)
        originals={str(p):digest(p) for p in directory.glob('*.json')}
        longer=story+' Additional material remains linked and editable.'*8
        edit_spec=spec(story,'edit')
        edit_spec['inputs']=[self.spec()['inputs'][0]]+[dict(id='original-'+str(i),path=str(directory/(unit.id+'.json')),sha256=digest(directory/(unit.id+'.json')),role='editable_source') for i,unit in enumerate(__import__('design_production.contracts',fromlist=['DesignTask']).DesignTask.model_validate(edit_spec).units)]
        edited,_=self.start(edit_spec)
        revised=json.loads((Path(edited['job']['directory'])/'flow-receipt.json').read_text())
        self.assertEqual(''.join(f['text'] for f in revised['frames']),longer)
        self.assertTrue(all(digest(Path(p))==h for p,h in originals.items()))
        overflow,_=self.start(spec(story*3),expected=2)
        self.assertEqual(overflow['job']['result']['qa']['status'],'FAIL')
        self.assertTrue(any('Overset' in issue for issue in overflow['job']['result']['qa']['issues']))

    def test_22_web_create_edit(self):
        contents=[dict(unit_id='slide-'+str(i+1),nodes=[
            dict(id='background',kind='rect',x=0,y=0,width=1920,height=1080,fill='#FFFFFF'),
            dict(id='title',kind='text',x=140,y=150,width=1600,height=130,font_size=72,bold=True,text='Web source '+str(i+1),fill='#17243B'),
            dict(id='body',kind='text',x=140,y=380,width=1450,height=180,font_size=38,text='Editable text. Keyboard navigation. Print and reduced motion.',fill='#17243B')]) for i in range(2)]
        spec=self.spec(artifact_type='web_deck',output_format='html',required_features=['navigation','reduced_motion','print'],timeout_seconds=300,
            units=[dict(id=c['unit_id'],kind='slide',width=1920,height=1080,instruction='Browser integration fixture') for c in contents],inputs=[self.spec()['inputs'][0],*self.sources(contents)])
        initial,_=self.start(spec)
        files=initial['job']['result']['artifacts']
        original=Path(next(m['path'] for m in files if m['format']=='html'))
        original_hash=digest(original)
        inputs=[self.spec()['inputs'][0]]+[dict(id='edit-'+str(i),path=m['path'],sha256=m['sha256'],role='editable_source') for i,m in enumerate(files) if m['role']=='source' and m['format']=='json']
        spec.update(parent_request_id=spec['parent_request_id']+'-edit',operation='edit',inputs=inputs)
        edited,_=self.start(spec)
        revised=Path(next(m['path'] for m in edited['job']['result']['artifacts'] if m['format']=='html'))
        self.assertNotEqual(digest(revised),original_hash)
        self.assertEqual(digest(original),original_hash)

    def test_23_package_and_profile_boundaries(self):
        from design_production.contracts import DesignTask,UnitContent
        from design_production.profiles import select
        from design_production.package_guard import validate_pptx
        for category,feature in [('social_graphic','native_charts'),('vector','linked_text_flow'),('editorial_svg','slide_masters')]:
            with self.assertRaisesRegex(ValueError,'UNSUPPORTED'):
                select(DesignTask.model_validate(self.spec(artifact_type=category,required_features=[feature])))
        with self.assertRaises(ValueError):
            UnitContent.model_validate({'unit_id':'one','nodes':[],'script':'alert(1)'})
        base={'[Content_Types].xml':'<Types/>','ppt/presentation.xml':'<presentation/>'}
        external='<Relationships><Relationship Id="rId1" Target="https://example.invalid/image" TargetMode="External"/></Relationships>'
        nested=io.BytesIO()
        with zipfile.ZipFile(nested,'w') as z:
            z.writestr('xl/workbook.xml','<workbook><f>WEBSERVICE("https://example.invalid")</f></workbook>')
        cases=[('../escape.xml','<x/>'),('ppt/vbaProject.bin',b'active'),('ppt/_rels/presentation.xml.rels',external),('ppt/media/active.svg','<svg><script>run()</script></svg>'),('ppt/embeddings/data.xlsx',nested.getvalue())]
        for i,(name,data) in enumerate(cases):
            path=self.directory/f'rejected-{i}.pptx'
            with zipfile.ZipFile(path,'w') as z:
                for k,v in base.items():z.writestr(k,v)
                z.writestr(name,data)
            with self.assertRaises(ValueError):validate_pptx(path)
            bad=self.spec(inputs=[self.spec()['inputs'][0],dict(id='bad-package',path=str(path),sha256=digest(path),role='reference')])
            result,_=self.start(bad,expected=2)
            self.assertNotIn('job',result)
        # Large expansion is rejected before reading the payload into an application.
        bomb=self.directory/'expanded.pptx'
        with zipfile.ZipFile(bomb,'w',zipfile.ZIP_DEFLATED) as z:
            for k,v in base.items():z.writestr(k,v)
            z.writestr('ppt/oversize.xml','a'*1_000_000)
        with self.assertRaisesRegex(ValueError,'expansion'):validate_pptx(bomb)


if __name__=='__main__':
    unittest.main(verbosity=2)
