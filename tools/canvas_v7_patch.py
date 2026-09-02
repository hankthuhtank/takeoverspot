from pathlib import Path
import re
root=Path('.')
jp=root/'takeover-v3.js'; cp=root/'takeover-v3.css'; bp=root/'boot.js'; cip=root/'.github/workflows/ci.yml'
js=jp.read_text(); css=cp.read_text(); boot=bp.read_text(); ci=cip.read_text()

helpers=r'''function shapeLayerGeom(l,cells,display='combined'){const g={x:Number(l.x)||0,y:Number(l.y)||0,w:Number(l.w)||40,h:Number(l.h)||20,size:Number(l.size)||18},nums=[...new Set((cells||[]).map(Number))].sort((a,b)=>a-b);if(display==='divided'||nums.length<2)return g;const shape=selectionShape(nums);if(nums.length===shape.w*shape.h)return g;const center=clamp(g.y+g.h/2,0,99.999),row=Math.min(shape.h-1,Math.floor(center/100*shape.h)),occupied=new Set(nums),runs=[];let start=null;for(let cc=0;cc<=shape.w;cc++){const n=(shape.r+row)*COLS+shape.c+cc+1,on=cc<shape.w&&occupied.has(n);if(on&&start===null)start=cc;if((!on||cc===shape.w)&&start!==null){runs.push({start,len:cc-start});start=null}}if(!runs.length)return g;runs.sort((a,b)=>b.len-a.len||a.start-b.start);const run=runs[0],runLeft=run.start/shape.w*100,runW=run.len/shape.w*100,rowTop=row/shape.h*100,rowH=100/shape.h,padX=Math.min(2,runW*.06),padY=Math.min(1.5,rowH*.08),availW=Math.max(1,runW-padX*2),availH=Math.max(1,rowH-padY*2),w=Math.min(availW,g.w/100*availW),x=runLeft+padX+g.x/100*availW,h=Math.min(g.h,availH),y=clamp(g.y,rowTop+padY,rowTop+rowH-padY-h),scale=Math.max(.58,Math.min(1,Math.sqrt(runW/100)));return{x:Math.min(x,runLeft+runW-padX-w),y,w,h,size:g.size*scale}}
'''
build=r'''function buildCanvasCreative(s,creativeId,cells=null,interactive=true){const c=normalizeCanvas(s.canvas_json,s.company_name,s.logo_url),a=document.createElement('a');a.className='canvas-creative';if(interactive){a.href=s.website||'#';a.target='_blank';a.rel='noopener sponsored'}else{a.removeAttribute('href');a.removeAttribute('target');a.setAttribute('aria-hidden','true');a.tabIndex=-1}a.dataset.creativeId=creativeId||'';a.style.background=canvasBgStyle(c);c.layers.forEach(l=>{const g=shapeLayerGeom(l,cells,c.display),d=document.createElement('div');d.className=`canvas-layer ${layerFont(l)} ${l.type==='button'?'is-button':''}`;d.style.left=`${g.x}%`;d.style.top=`${g.y}%`;d.style.width=`${g.w}%`;d.style.height=`${g.h}%`;d.style.color=l.color;d.style.textAlign=l.align;d.style.setProperty('--layer-size',`${Math.max(2,g.size/4)}cqw`);if(l.type==='button'){d.textContent=l.text||'LEARN MORE';d.style.background=l.bg||'#111111'}else if(l.type==='image'&&safeImg(l.src)){d.dataset.fit=l.fit||'contain';const img=document.createElement('img');img.src=safeImg(l.src);img.alt=l.role==='logo'?(s.company_name||'Advertiser'):'';d.appendChild(img)}else{d.textContent=l.text||''}a.appendChild(d)});const site=document.createElement('span');site.className='canvas-site';site.textContent=host(s.website);a.appendChild(site);if(interactive)a.addEventListener('click',()=>{if(creativeId)sb.rpc('record_takeover_click',{p_creative_id:creativeId}).catch(()=>{})});return a}'''
pat=r"function buildCanvasCreative\(s,creativeId\)\{.*?return a\}\n\nfunction partitionRectangles"
m=re.search(pat,js,re.S)
if not m: raise SystemExit('buildCanvasCreative block not found')
js=js[:m.start()] + helpers + build + '\n\nfunction partitionRectangles' + js[m.end():]

old="t.appendChild(buildCanvasCreative(r.ad,r.creativeId));"
if old not in js: raise SystemExit('board creative call not found')
js=js.replace(old,"t.appendChild(buildCanvasCreative(r.ad,r.creativeId,r.cells,true));",1)

old_preview="function renderPurchaseCanvasPreview(){const box=$('#purchaseCanvasPreview');if(!box)return;box.innerHTML='';const c=normalizeCanvas(currentCanvas,$('#companyName')?.value,selectedLogoUrl),fake={company_name:$('#companyName')?.value||'YOUR BRAND',website:normalizeWebsite($('#companyWebsite')?.value||'example.com'),logo_url:selectedLogoUrl,canvas_json:c};box.appendChild(buildCanvasCreative(fake,null))}"
new_preview="function renderPurchaseCanvasPreview(){const box=$('#purchaseCanvasPreview');if(!box)return;box.innerHTML='';const c=normalizeCanvas(currentCanvas,$('#companyName')?.value,selectedLogoUrl),fake={company_name:$('#companyName')?.value||'YOUR BRAND',website:normalizeWebsite($('#companyWebsite')?.value||'example.com'),logo_url:selectedLogoUrl,canvas_json:c},nums=[...new Set((selected||[]).map(Number))].sort((a,b)=>a-b),multi=nums.length>1,divided=multi&&c.display==='divided',shape=divided||!multi?{w:1,h:1}:selectionShape(nums),frame=document.createElement('div');frame.className='purchase-preview-shape';frame.style.aspectRatio=`${shape.w}/${shape.h}`;frame.style.clipPath=divided||!multi?'none':ensureShapeClip(nums);if(shape.w>=shape.h)frame.style.width='100%';else frame.style.height='100%';frame.appendChild(buildCanvasCreative(fake,null,nums,false));box.appendChild(frame)}"
if old_preview not in js: raise SystemExit('purchase preview block not found')
js=js.replace(old_preview,new_preview,1)

old_geom="d.style.left=`${l.x}%`;d.style.top=`${l.y}%`;d.style.width=`${l.w}%`;d.style.height=`${l.h}%`;d.style.color=l.color||'#111';d.style.textAlign=l.align||'center';d.style.fontSize=`${clamp(l.size||18,8,200)}px`;"
new_geom="const g=shapeLayerGeom(l,selected,editorCanvas.display);d.style.left=`${g.x}%`;d.style.top=`${g.y}%`;d.style.width=`${g.w}%`;d.style.height=`${g.h}%`;d.style.color=l.color||'#111';d.style.textAlign=l.align||'center';d.style.fontSize=`${clamp(g.size||18,8,200)}px`;"
if old_geom not in js: raise SystemExit('editor geometry block not found')
js=js.replace(old_geom,new_geom,1)

old_toggle="$('#displayCombined').onclick=()=>{editorCanvas.display='combined';syncDisplayButtons()};$('#displayDivided').onclick=()=>{editorCanvas.display='divided';syncDisplayButtons()};"
new_toggle="$('#displayCombined').onclick=()=>{editorCanvas.display='combined';syncDisplayButtons();renderEditor();renderPurchaseCanvasPreview()};$('#displayDivided').onclick=()=>{editorCanvas.display='divided';syncDisplayButtons();renderEditor();renderPurchaseCanvasPreview()};"
if old_toggle not in js: raise SystemExit('display toggle block not found')
js=js.replace(old_toggle,new_toggle,1)

css += r'''

/* TAKEOVER CANVAS V7 — shape-aware creative placement + aligned logo picker */
.canvas-preview-mini{display:flex!important;align-items:center!important;justify-content:center!important;padding:10px!important;box-sizing:border-box!important;background:repeating-conic-gradient(#f3f3ef 0 25%,#ecece7 0 50%) 0/14px 14px!important}
.purchase-preview-shape{position:relative!important;max-width:100%!important;max-height:100%!important;overflow:hidden!important;background:#fff!important}
.canvas-preview-mini .canvas-creative{pointer-events:none!important;cursor:default!important}
.logo-trigger{width:100%!important;height:100%!important;box-sizing:border-box!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;gap:11px!important;text-align:center!important;padding:16px!important}
.logo-trigger>span:not(.logo-choose){display:block!important;width:100%!important;margin:0!important;text-align:center!important;line-height:1.35!important}
.logo-trigger>.logo-choose{display:inline-flex!important;width:auto!important;margin:0 auto!important;align-self:center!important;text-align:center!important}
'''

boot=boot.replace('takeover-v3.css?v=6','takeover-v3.css?v=7').replace('takeover-v3.js?v=6','takeover-v3.js?v=7')
ci=ci.replace("takeover-v3.js?v=6","takeover-v3.js?v=7").replace("takeover-v3.css?v=6","takeover-v3.css?v=7")
jp.write_text(js); cp.write_text(css); bp.write_text(boot); cip.write_text(ci)
print('Canvas V7 patch applied')
