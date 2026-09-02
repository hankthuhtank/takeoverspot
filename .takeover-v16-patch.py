from pathlib import Path

js_path=Path('takeover-v3.js')
css_path=Path('takeover-v3.css')
boot_path=Path('boot.js')
index_path=Path('index.html')
js=js_path.read_text()
css=css_path.read_text()
boot=boot_path.read_text()
index=index_path.read_text()

def rep(old,new,label,count=1):
    global js
    found=js.count(old)
    if found!=count:
        raise SystemExit(f'{label}: expected {count}, found {found}')
    js=js.replace(old,new,count)

# 1) Persist the original territory footprint inside the creative itself.
old=""";if(!c.layers.length)return defaultCanvas(company,logo);return c}"""
new=""";c.frameCells=Array.isArray(c.frameCells)?[...new Set(c.frameCells.map(Number).filter(n=>n>=1&&n<=TOTAL))].sort((a,b)=>a-b):[];if(!c.layers.length){const d=defaultCanvas(company,logo);d.frameCells=c.frameCells;return d}return c}"""
rep(old,new,'normalize frameCells')

# Presets must not erase the original footprint while editing.
old="""b.onclick=()=>{editorCanvas=makePreset(key);editorSelected=null;renderEditor();renderPresetChoices()}"""
new="""b.onclick=()=>{const frame=[...(editorCanvas?.frameCells||[])];editorCanvas=makePreset(key);if(frame.length)editorCanvas.frameCells=frame;editorSelected=null;renderEditor();renderPresetChoices()}"""
rep(old,new,'preset frame preservation')

# Add a clip-path whose coordinate system is the ORIGINAL territory, not the remaining cells.
needle="""function syncEditorStageShape(){"""
if js.count(needle)!=1: raise SystemExit('syncEditorStageShape anchor missing')
insert="""function ensureFrameClip(visible,frame){const base=[...new Set((frame||[]).map(Number).filter(n=>n>=1&&n<=TOTAL))].sort((a,b)=>a-b),allowed=new Set(base),cells=[...new Set((visible||[]).map(Number).filter(n=>allowed.has(n)))].sort((a,b)=>a-b);if(!base.length||!cells.length)return'inset(100%)';const shape=selectionShape(base),id='takeover-frame-'+base.join('-')+'--'+cells.join('-');if(!document.getElementById(id)){const NS='http://www.w3.org/2000/svg';let svg=$('#takeoverShapeDefs');if(!svg){svg=document.createElementNS(NS,'svg');svg.id='takeoverShapeDefs';svg.setAttribute('width','0');svg.setAttribute('height','0');svg.setAttribute('aria-hidden','true');svg.style.position='absolute';svg.style.pointerEvents='none';const defs=document.createElementNS(NS,'defs');svg.appendChild(defs);document.body.appendChild(svg)}const cp=document.createElementNS(NS,'clipPath');cp.id=id;cp.setAttribute('clipPathUnits','objectBoundingBox');cells.forEach(n=>{const r=Math.floor((n-1)/COLS),c=(n-1)%COLS,rect=document.createElementNS(NS,'rect');rect.setAttribute('x',String((c-shape.c)/shape.w));rect.setAttribute('y',String((r-shape.r)/shape.h));rect.setAttribute('width',String(1/shape.w));rect.setAttribute('height',String(1/shape.h));cp.appendChild(rect)});svg.querySelector('defs').appendChild(cp)}return`url(#${id})`}
"""
js=js.replace(needle,insert+needle,1)

# Combined live creatives stay anchored to the footprint they were originally designed for.
old="""const parts=canvas.display==='divided'?nums.map(n=>({r:Math.floor((n-1)/COLS),c:(n-1)%COLS,w:1,h:1,cells:[n],clip:''})):selectionComponents(nums).map(cells=>{const b=selectionShape(cells);return{...b,cells,clip:cells.length===b.w*b.h?'':ensureShapeClip(cells)}});"""
new="""const frame=canvas.frameCells?.length?canvas.frameCells:nums,parts=canvas.display==='divided'?nums.map(n=>({r:Math.floor((n-1)/COLS),c:(n-1)%COLS,w:1,h:1,cells:[n],clip:''})):(canvas.frameCells?.length?[{...selectionShape(frame),cells:nums,clip:ensureFrameClip(nums,frame)}]:selectionComponents(nums).map(cells=>{const b=selectionShape(cells);return{...b,cells,clip:cells.length===b.w*b.h?'':ensureShapeClip(cells)}}));"""
rep(old,new,'live dead-pixel compositor')

# The editor uses the saved footprint when editing an already-published creative.
old="""function syncEditorStageShape(){const stage=$('#canvasStage'),grid=stage?.querySelector('.editor-grid'),multi=$('#multiSpotSection');if(!stage||!editorCanvas)return;const nums=[...new Set((selected||[]).map(Number))].sort((a,b)=>a-b),isMulti=nums.length>1,divided=isMulti&&editorCanvas.display==='divided';if(multi)multi.hidden=!isMulti;const shape=divided||!isMulti?{w:1,h:1}:selectionShape(nums);stage.style.aspectRatio=`${shape.w}/${shape.h}`;stage.style.clipPath=divided||!isMulti?'none':ensureShapeClip(nums);stage.dataset.display=divided?'divided':'combined';if(grid){grid.style.gridTemplateColumns=`repeat(${shape.w},1fr)`;grid.style.gridTemplateRows=`repeat(${shape.h},1fr)`;grid.innerHTML='<i></i>'.repeat(shape.w*shape.h);grid.style.opacity=divided||!isMulti?'0':'.13'}}"""
new="""function syncEditorStageShape(){const stage=$('#canvasStage'),grid=stage?.querySelector('.editor-grid'),multi=$('#multiSpotSection');if(!stage||!editorCanvas)return;const nums=[...new Set((selected||[]).map(Number))].sort((a,b)=>a-b),frame=editorContext==='purchase'?nums:(editorCanvas.frameCells?.length?editorCanvas.frameCells:nums),isMulti=nums.length>1||frame.length>1,divided=nums.length>1&&editorCanvas.display==='divided',combinedFrame=!divided&&frame.length>1;if(editorContext==='purchase')editorCanvas.frameCells=[...nums];if(multi)multi.hidden=!isMulti;const shape=divided||!combinedFrame?{w:1,h:1}:selectionShape(frame);stage.style.aspectRatio=`${shape.w}/${shape.h}`;stage.style.clipPath=combinedFrame?ensureFrameClip(nums,frame):'none';stage.dataset.display=divided?'divided':'combined';if(grid){grid.style.gridTemplateColumns=`repeat(${shape.w},1fr)`;grid.style.gridTemplateRows=`repeat(${shape.h},1fr)`;grid.innerHTML='<i></i>'.repeat(shape.w*shape.h);grid.style.opacity=combinedFrame?'.13':'0'}}"""
rep(old,new,'editor original footprint')

# New purchases always stamp their final selected cells into the creative before checkout.
old="""if(!currentCanvas)currentCanvas=defaultCanvas(company,oldLogoRef||selectedLogoUrl);const replacements={};"""
new="""if(!currentCanvas)currentCanvas=defaultCanvas(company,oldLogoRef||selectedLogoUrl);currentCanvas.frameCells=[...new Set(selected.map(Number).filter(n=>n>=1&&n<=TOTAL))].sort((a,b)=>a-b);const replacements={};"""
rep(old,new,'checkout frame stamp')

# Editing an older creative without frame metadata gets a one-time fallback to its currently-owned footprint.
old="""editorCanvas=normalizeCanvas(group.ad.canvas_json,editorCompany,group.ad.logo_url);selectedLogoUrl=group.ad.logo_url||profile?.logo_url||null"""
new="""editorCanvas=normalizeCanvas(group.ad.canvas_json,editorCompany,group.ad.logo_url);if(!editorCanvas.frameCells.length)editorCanvas.frameCells=[...new Set(selected.map(Number))].sort((a,b)=>a-b);selectedLogoUrl=group.ad.logo_url||profile?.logo_url||null"""
rep(old,new,'legacy edit frame fallback')

# 2) Mobile touch gestures: one finger moves, two fingers resize+move uniformly.
old="""d.onpointerdown=e=>startLayerDrag(e,l.id);handle.onpointerdown=e=>{e.stopPropagation();startLayerResize(e,l.id)};d.onclick=e=>"""
new="""d.onpointerdown=e=>{if(e.pointerType==='touch')return;startLayerDrag(e,l.id)};handle.onpointerdown=e=>{e.stopPropagation();if(e.pointerType==='touch')return;startLayerResize(e,l.id)};d.ontouchstart=e=>startLayerTouch(e,l.id);d.onclick=e=>"""
rep(old,new,'touch binding')

needle="""function startLayerDrag(e,id){"""
if js.count(needle)!=1: raise SystemExit('drag anchor missing')
touch_code="""let editorTouchGesture=null;
function touchStagePoint(t){const r=$('#canvasStage').getBoundingClientRect();return{x:(t.clientX-r.left)/r.width*100,y:(t.clientY-r.top)/r.height*100}}
function touchDistance(a,b){const pa=touchStagePoint(a),pb=touchStagePoint(b);return Math.hypot(pb.x-pa.x,pb.y-pa.y)}
function touchMidpoint(a,b){const pa=touchStagePoint(a),pb=touchStagePoint(b);return{x:(pa.x+pb.x)/2,y:(pa.y+pb.y)/2}}
function rebaseTouchGesture(touches,l,id){if(touches.length>=2){const mid=touchMidpoint(touches[0],touches[1]);editorTouchGesture={id,mode:'pinch',dist:Math.max(.01,touchDistance(touches[0],touches[1])),mid,ow:l.w,oh:l.h,cx:l.x+l.w/2,cy:l.y+l.h/2}}else{const p=touchStagePoint(touches[0]);editorTouchGesture={id,mode:'drag',point:p,ox:l.x,oy:l.y}}}
function startLayerTouch(e,id){if(!e.touches?.length)return;e.preventDefault();e.stopPropagation();editorSelected=id;const l=editorCanvas.layers.find(x=>x.id===id);if(!l)return;if(editorTouchGesture){if(editorTouchGesture.id===id)rebaseTouchGesture(e.touches,l,id);return}rebaseTouchGesture(e.touches,l,id);const move=ev=>{if(!editorTouchGesture||editorTouchGesture.id!==id)return;ev.preventDefault();const layer=editorCanvas.layers.find(x=>x.id===id);if(!layer)return;if(ev.touches.length>=2){if(editorTouchGesture.mode!=='pinch'){rebaseTouchGesture(ev.touches,layer,id);return}const mid=touchMidpoint(ev.touches[0],ev.touches[1]),scale=touchDistance(ev.touches[0],ev.touches[1])/editorTouchGesture.dist,nw=clamp(editorTouchGesture.ow*scale,5,150),nh=clamp(editorTouchGesture.oh*scale,5,150),dx=mid.x-editorTouchGesture.mid.x,dy=mid.y-editorTouchGesture.mid.y;layer.w=nw;layer.h=nh;layer.x=clamp(editorTouchGesture.cx+dx-nw/2,-25,Math.max(-25,125-nw));layer.y=clamp(editorTouchGesture.cy+dy-nh/2,-25,Math.max(-25,125-nh));syncEditorLayer(layer);return}if(ev.touches.length===1){if(editorTouchGesture.mode!=='drag'){rebaseTouchGesture(ev.touches,layer,id);return}const p=touchStagePoint(ev.touches[0]);layer.x=clamp(editorTouchGesture.ox+p.x-editorTouchGesture.point.x,-25,Math.max(-25,125-layer.w));layer.y=clamp(editorTouchGesture.oy+p.y-editorTouchGesture.point.y,-25,Math.max(-25,125-layer.h));syncEditorLayer(layer)}};const end=ev=>{const layer=editorCanvas.layers.find(x=>x.id===id);if(ev.touches?.length&&layer){rebaseTouchGesture(ev.touches,layer,id);return}window.removeEventListener('touchmove',move);window.removeEventListener('touchend',end);window.removeEventListener('touchcancel',end);editorTouchGesture=null;renderInspector()};window.addEventListener('touchmove',move,{passive:false});window.addEventListener('touchend',end,{passive:false});window.addEventListener('touchcancel',end,{passive:false})}
"""
js=js.replace(needle,touch_code+needle,1)

# Update Canvas help copy.
js=js.replace('DRAG anything · RESIZE from the corner · DOUBLE-CLICK text · use POSITION for exact control','DRAG to move · PINCH with two fingers to resize · corner handle on desktop · use POSITION for exact control')

# 3) Same-device magic-link handoff: wake original tab instantly and close the handoff tab when the browser permits.
old="""let loginHandoffPoll=null,loginHandoffCompleting=false;"""
new="""let loginHandoffPoll=null,loginHandoffCompleting=false;const loginHandoffChannel=('BroadcastChannel'in window)?new BroadcastChannel('takeover-login-handoff-v1'):null;"""
rep(old,new,'handoff broadcast channel')

old="""function startStoredLoginHandoffPoll(){if(session||loginHandoffPoll||!readLoginHandoff())return;loginHandoffPoll=setInterval(checkLoginHandoff,1200);checkLoginHandoff()}"""
new="""function startStoredLoginHandoffPoll(){if(session||loginHandoffPoll||!readLoginHandoff())return;loginHandoffPoll=setInterval(checkLoginHandoff,900);checkLoginHandoff()}if(loginHandoffChannel)loginHandoffChannel.onmessage=e=>{if(e.data?.type==='ready')checkLoginHandoff()};"""
rep(old,new,'instant handoff wake')

needle="""async function completeLoginHandoffFromUrl(){"""
if js.count(needle)!=1: raise SystemExit('complete handoff anchor missing')
return_ui="""function showHandoffReturnScreen(){let box=$('#handoffReturn');if(!box){box=document.createElement('div');box.id='handoffReturn';box.className='handoff-return';box.innerHTML='<div><span>TAKEOVER</span><b>YOU’RE SIGNED IN.</b><p>Returning to the TAKEOVER tab you started from…</p><button type=\"button\" id=\"handoffClose\">CLOSE THIS TAB</button></div>';document.body.appendChild(box);$('#handoffClose').onclick=()=>{try{window.close()}catch{}}}box.classList.add('on');setTimeout(()=>{try{window.close()}catch{}},250);setTimeout(()=>box.classList.add('manual'),1100)}
"""
js=js.replace(needle,return_ui+needle,1)

old="""if(data?.status==='ready'){removeHandoffParam();toast('Sign-in confirmed. Your other TAKEOVER tab is signing in too.')}"""
new="""if(data?.status==='ready'){removeHandoffParam();try{loginHandoffChannel?.postMessage({type:'ready',id})}catch{}showHandoffReturnScreen()}"""
rep(old,new,'handoff return UX')

# CSS for touch ergonomics and the temporary handoff-return screen.
css += """

/* TAKEOVER V16 — dead-pixel canvas + mobile gestures + clean auth return */
@media(pointer:coarse){.editor-layer .resize-handle{width:24px!important;height:24px!important;right:4px!important;bottom:4px!important}.canvas-stage-tip{font-size:9px!important;line-height:1.45!important}}
.handoff-return{position:fixed;inset:0;z-index:9999;background:#f7f7f3;display:none;place-items:center;padding:24px;text-align:center}.handoff-return.on{display:grid}.handoff-return>div{width:min(420px,100%);border:1px solid #d8d8d1;border-radius:20px;background:#fff;padding:34px 24px;box-shadow:0 20px 70px rgba(0,0,0,.08)}.handoff-return span{display:block;font:800 10px 'DM Mono',monospace;letter-spacing:.14em;color:#777}.handoff-return b{display:block;margin-top:10px;font:900 30px Manrope,sans-serif;letter-spacing:-.05em}.handoff-return p{margin:10px auto 0;max-width:300px;color:#666;font-size:13px;line-height:1.5}.handoff-return button{display:none;margin:20px auto 0;border:0;border-radius:999px;background:#111;color:#fff;padding:13px 18px;font:800 10px 'DM Mono',monospace}.handoff-return.manual button{display:inline-flex}
"""

# Cache-bust V16.
boot=boot.replace('takeover-v3.css?v=15','takeover-v3.css?v=16').replace('takeover-v3.js?v=15','takeover-v3.js?v=16')
index=index.replace('boot.js?v=11','boot.js?v=12')

js_path.write_text(js)
css_path.write_text(css)
boot_path.write_text(boot)
index_path.write_text(index)
print('V16 patch applied')
