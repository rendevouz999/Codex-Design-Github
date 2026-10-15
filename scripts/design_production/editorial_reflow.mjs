// Trusted layout adapter: model data never becomes executable source.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const directory=await fs.realpath(process.argv[2]);
if(!directory.startsWith(path.join(root,'output')+path.sep)) throw Error('Output boundary');
const source=JSON.parse(await fs.readFile(path.join(directory,'publication.json'),'utf8'));
const browser=await chromium.launch({headless:true});
const receipt={frames:[],issues:[],engine:'Chromium Canvas2D installed font metrics'};
try {
  const context=await browser.newContext({serviceWorkers:'block'});
  await context.route('**/*',r=>r.abort());
  const page=await context.newPage();
  const layout=await page.evaluate(async doc=>{
    const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');
    const cursors=Object.fromEntries(doc.stories.map(s=>[s.id,0]));
    const issues=[],frames=[];
    for(const [i,style]of doc.settings.styles.entries()){
      try{await new FontFace('__local_probe_'+i,`local("${style.font}")`).load();}
      catch{issues.push(`Font unavailable; substitution forbidden: ${style.font}`);}
    }
    for(const f of doc.frames){
      const story=doc.stories.find(s=>s.id===f.story_id),style=doc.settings.styles.find(s=>s.id===story.style);
      ctx.font=`${style.bold?'bold ':''}${style.size}px "${style.font}"`;
      const start=cursors[story.id],lines=[];
      let cursor=start;
      for(let row=0;row<Math.floor(f.height/style.leading)&&cursor<story.text.length;row++){
        const from=cursor;
        let end=cursor,lastBreak=-1;
        while(end<story.text.length){
          const cp=String.fromCodePoint(story.text.codePointAt(end));
          if(cp==='\n'){end++;break;}
          if(ctx.measureText(story.text.slice(from,end+cp.length)).width>f.width){
            if(lastBreak>from) end=lastBreak;
            if(end===from){issues.push(`Glyph exceeds frame: ${f.id}`);end+=cp.length;}
            break;
          }
          end+=cp.length;
          if(/\s/.test(cp))lastBreak=end;
        }
        lines.push({start:from,end,text:story.text.slice(from,end)});
        cursor=end;
      }
      cursors[story.id]=cursor;
      frames.push({...f,style,start:Array.from(story.text.slice(0,start)).length,end:Array.from(story.text.slice(0,cursor)).length,text:story.text.slice(start,cursor),lines});
    }
    return {frames,issues};
  },source);
  receipt.frames=layout.frames.map(({lines,style,...f})=>({...f,lines}));receipt.issues=layout.issues;
  for(const unit of new Set(layout.frames.map(f=>f.unit))){
    if(!/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}$/.test(unit))throw Error('Invalid unit');
    const file=path.join(directory,unit+'.svg');
    const svg=await fs.readFile(file,'utf8');
    const revised=await page.evaluate(({svg,frames,box,bleed})=>{
      const doc=new DOMParser().parseFromString(svg,'image/svg+xml'),ns='http://www.w3.org/2000/svg';
      doc.documentElement.setAttribute('data-bleed',bleed);
      doc.documentElement.setAttribute('data-trim-box',box.trim_box.join(' '));
      for(const f of frames){
        const group=doc.getElementById(f.id);if(!group)throw Error('Missing text frame');
        group.setAttribute('data-story-start',f.start);group.setAttribute('data-story-end',f.end);
        const text=doc.createElementNS(ns,'text');
        for(const [k,v]of Object.entries({'font-family':f.style.font,'font-size':f.style.size,'fill':f.style.color,'font-weight':f.style.bold?'700':'400','xml:space':'preserve'}))text.setAttribute(k,v);
        f.lines.forEach((line,i)=>{const t=doc.createElementNS(ns,'tspan');t.setAttribute('x',f.x);t.setAttribute('y',f.y+f.style.size+i*f.style.leading);t.textContent=line.text.replace(/\n$/,'');text.append(t);});
        group.append(text);
      }
      return new XMLSerializer().serializeToString(doc);
    },{svg,frames:layout.frames.filter(f=>f.unit===unit),box:source.pages.find(p=>p.unit===unit),bleed:source.settings.bleed});
    await fs.writeFile(file,revised);
  }
}finally{await browser.close();}
await fs.writeFile(path.join(directory,'flow-receipt.json'),JSON.stringify(receipt,null,2),{flag:'wx'});
