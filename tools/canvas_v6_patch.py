from pathlib import Path

root=Path('.')
js_path=root/'takeover-v3.js'
css_path=root/'takeover-v3.css'
boot_path=root/'boot.js'
js=js_path.read_text()
css=css_path.read_text()
boot=boot_path.read_text()

def rep(text,old,new,label):
    if old not in text:
        raise SystemExit(f'missing {label}')
    return text.replace(old,new,1)

# Make the whole logo box one native label target. No competing click zones.
old_logo="function setLogoPreview(boxSelector,inputSelector,url,placeholder){const box=$(boxSelector),input=$(inputSelector);if(!box||!input)return;[...box.children].forEach(el=>{if(el!==input)el.remove()});const src=safeImg(url),el=document.createElement(src?'img':'span');if(src){el.src=src;el.alt='Logo preview'}else el.textContent=placeholder||'CLICK TO CHOOSE LOGO';const choose=document.createElement('button');choose.type='button';choose.className='logo-choose';choose.textContent=src?'REPLACE LOGO':'CHOOSE LOGO';const openPicker=e=>{e?.preventDefault();e?.stopPropagation();choose.textContent='OPENING…';input.click();setTimeout(()=>{if(document.body.contains(choose))choose.textContent=src?'REPLACE LOGO':'CHOOSE LOGO'},1200)};choose.onclick=openPicker;box.onclick=e=>{if(e.target!==input&&e.target!==choose)openPicker(e)};box.insertBefore(el,input);box.insertBefore(choose,input)}"
new_logo="function setLogoPreview(boxSelector,inputSelector,url,placeholder){const box=$(boxSelector),input=$(inputSelector);if(!box||!input)return;box.onclick=null;[...box.children].forEach(el=>{if(el!==input)el.remove()});const trigger=document.createElement('label');trigger.className='logo-trigger';trigger.htmlFor=input.id;const src=safeImg(url),el=document.createElement(src?'img':'span');if(src){el.src=src;el.alt='Logo preview'}else el.textContent=placeholder||'CLICK TO CHOOSE LOGO';const choose=document.createElement('span');choose.className='logo-choose';choose.textContent=src?'REPLACE LOGO':'CHOOSE LOGO';trigger.append(el,choose);box.insertBefore(trigger,input)}"
js=rep(js,old_logo,new_logo,'logo picker')

# Give the multi-display section an addressable wrapper so single-spot editing can hide it.
js=rep(js,
'<div class=\\"canvas-section\\"><h3>MULTI-SPOT DISPLAY</h3>',
'<div class=\\"canvas-section\\" id=\\"multiSpotSection\\"><h3>MULTI-SPOT DISPLAY</h3>',
'multi spot section id')

# Replace selection geometry with exact connected-shape support and SVG union clipping.
old_shape="function selectionShape(nums){if(!nums?.length)return{w:1,h:1};const rs=nums.map(n=>Math.floor((n-1)/COLS)),cs=nums.map(n=>(n-1)%COLS);return{w:Math.max(...cs)-Math.min(...cs)+1,h:Math.max(...rs)-Math.min(...rs)+1}}"
new_shape="""function selectionShape(nums){if(!nums?.length)return{r:0,c:0,w:1,h:1};const rs=nums.map(n=>Math.floor((n-1)/COLS)),cs=nums.map(n=>(n-1)%COLS),r=Math.min(...rs),c=Math.min(...cs);return{r,c,w:Math.max(...cs)-c+1,h:Math.max(...rs)-r+1}}
function selectionComponents(nums){const left=new Set((nums||[]).map(Number)),out=[];while(left.size){const first=left.values().next().value,q=[first],part=[];left.delete(first);while(q.length){const n=q.shift();part.push(n);[n-COLS,n+COLS,n-1,n+1].forEach(m=>{if(left.has(m)&&neighbor(n,m)){left.delete(m);q.push(m)}})}out.push(part.sort((a,b)=>a-b))}return out}
function ensureShapeClip(nums){const cells=[...new Set((nums||[]).map(Number))].sort((a,b)=>a-b),shape=selectionShape(cells),id='takeover-shape-'+cells.join('-');if(!document.getElementById(id)){const NS='http://www.w3.org/2000/svg';let svg=$('#takeoverShapeDefs');if(!svg){svg=document.createElementNS(NS,'svg');svg.id='takeoverShapeDefs';svg.setAttribute('width','0');svg.setAttribute('height','0');svg.setAttribute('aria-hidden','true');svg.style.position='absolute';svg.style.pointerEvents='none';const defs=document.createElementNS(NS,'defs');svg.appendChild(defs);document.body.appendChild(svg)}const cp=document.createElementNS(NS,'clipPath');cp.id=id;cp.setAttribute('clipPathUnits','objectBoundingBox');cells.forEach(n=>{const r=Math.floor((n-1)/COLS),c=(n-1)%COLS,rect=document.createElementNS(NS,'rect');rect.setAttribute('x',String((c-shape.c)/shape.w));rect.setAttribute('y',String((r-shape.r)/shape.h));rect.setAttribute('width',String(1/shape.w));rect.setAttribute('height',String(1/shape.h));cp.appendChild(rect)});svg.querySelector('defs').appendChild(cp)}return`url(#${id})`}
function syncEditorStageShape(){const stage=$('#canvasStage'),grid=stage?.querySelector('.editor-grid'),multi=$('#multiSpotSection');if(!stage||!editorCanvas)return;const nums=[...new Set((selected||[]).map(Number))].sort((a,b)=>a-b),isMulti=nums.length>1,divided=isMulti&&editorCanvas.display==='divided';if(multi)multi.hidden=!isMulti;const shape=divided||!isMulti?{w:1,h:1}:selectionShape(nums);stage.style.aspectRatio=`${shape.w}/${shape.h}`;stage.style.clipPath=divided||!isMulti?'none':ensureShapeClip(nums);stage.dataset.display=divided?'divided':'combined';if(grid){grid.style.gridTemplateColumns=`repeat(${shape.w},1fr)`;grid.style.gridTemplateRows=`repeat(${shape.h},1fr)`;grid.innerHTML='<i></i>'.repeat(shape.w*shape.h);grid.style.opacity=divided||!isMulti?'0':'.13'}}"""
js=rep(js,old_shape,new_shape,'selection shape')

# Toggling Combined/Divided now immediately changes the editor geometry.
old_sync="function syncDisplayButtons(){$('#displayCombined')?.classList.toggle('active',editorCanvas?.display!=='divided');$('#displayDivided')?.classList.toggle('active',editorCanvas?.display==='divided')}"
new_sync="function syncDisplayButtons(){$('#displayCombined')?.classList.toggle('active',editorCanvas?.display!=='divided');$('#displayDivided')?.classList.toggle('active',editorCanvas?.display==='divided');syncEditorStageShape()}"
js=rep(js,old_sync,new_sync,'display sync')

# Render a combined creative as the actual connected polyomino, not bounding rectangles.
old_rects="function territoryRects(){const out=[];for(const g of creativeGroups()){const nums=g.items.map(s=>Number(s.spot_number)).sort((a,b)=>a-b),canvas=normalizeCanvas(g.ad.canvas_json,g.ad.company_name,g.ad.logo_url),parts=canvas.display==='divided'?nums.map(n=>({r:Math.floor((n-1)/COLS),c:(n-1)%COLS,w:1,h:1,cells:[n]})):partitionRectangles(nums);parts.forEach(r=>out.push({...r,creativeId:g.creativeId,ad:g.ad,canvas}))}return out}"
new_rects="function territoryRects(){const out=[];for(const g of creativeGroups()){const nums=g.items.map(s=>Number(s.spot_number)).sort((a,b)=>a-b),canvas=normalizeCanvas(g.ad.canvas_json,g.ad.company_name,g.ad.logo_url);const parts=canvas.display==='divided'?nums.map(n=>({r:Math.floor((n-1)/COLS),c:(n-1)%COLS,w:1,h:1,cells:[n],clip:''})):selectionComponents(nums).map(cells=>{const b=selectionShape(cells);return{...b,cells,clip:cells.length===b.w*b.h?'':ensureShapeClip(cells)}});parts.forEach(r=>out.push({...r,creativeId:g.creativeId,ad:g.ad,canvas}))}return out}"
js=rep(js,old_rects,new_rects,'territory geometry')

old_height="t.style.height=(r.h/ROWS*100)+'%';t.appendChild(buildCanvasCreative(r.ad,r.creativeId));"
new_height="t.style.height=(r.h/ROWS*100)+'%';t.style.clipPath=r.clip||'none';t.appendChild(buildCanvasCreative(r.ad,r.creativeId));"
js=rep(js,old_height,new_height,'territory clip application')

# Cache bust.
boot=boot.replace('takeover-v3.css?v=5','takeover-v3.css?v=6').replace('takeover-v3.js?v=5','takeover-v3.js?v=6')

css += r'''

/* TAKEOVER CANVAS V6 — exact multi-spot geometry + single native logo target */
.logo-drop{position:relative!important;cursor:pointer!important}
.logo-trigger{position:absolute;inset:0;z-index:2;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:10px;padding:14px;cursor:pointer;border-radius:inherit}
.logo-trigger:hover{background:rgba(255,255,255,.35)}
.logo-trigger img{width:auto!important;height:auto!important;max-width:88%!important;max-height:88px!important;object-fit:contain!important;display:block!important}
.logo-trigger span:not(.logo-choose){font:700 10px 'DM Mono',monospace;color:#777;letter-spacing:.07em;pointer-events:none}
.logo-choose{display:inline-flex!important;align-items:center;justify-content:center;pointer-events:none!important;user-select:none}
#multiSpotSection[hidden]{display:none!important}
.canvas-stage{transform-origin:center;transition:clip-path .16s ease!important}
.canvas-stage[data-display="divided"]{max-width:660px}
'''

js_path.write_text(js)
css_path.write_text(css)
boot_path.write_text(boot)
print('TAKEOVER Canvas V6 patch applied')
# workflow trigger
