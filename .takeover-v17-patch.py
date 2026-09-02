from pathlib import Path

js=Path('takeover-v3.js')
css=Path('takeover-v3.css')
boot=Path('boot.js')
index=Path('index.html')

s=js.read_text()
c=css.read_text()
b=boot.read_text()
i=index.read_text()

old="""async function uploadSpecific(f,bucket='takeover-creative',max=IMAGE_STORED_LIMIT){if(!f)return null;if(!session)throw new Error('Sign in when you are ready to pay');f=await prepareImageFile(f);if(f.size>max)throw new Error('Image could not be optimized for upload');const ext=f.type==='image/png'?'png':f.type==='image/webp'?'webp':'jpg',path=`${session.user.id}/${crypto.randomUUID()}.${ext}`;const {error}=await sb.storage.from(bucket).upload(path,f,{contentType:f.type,upsert:false});if(error)throw error;return sb.storage.from(bucket).getPublicUrl(path).data.publicUrl}"""
new="""async function uploadSpecific(f,bucket='takeover-creative',max=IMAGE_STORED_LIMIT){if(!f)return null;if(!session)throw new Error('Sign in when you are ready to pay');f=await prepareImageFile(f);if(!f||!Number(f.size))throw new Error('That image could not be read. Re-select it and try again.');if(f.size>max)throw new Error('Image could not be optimized for upload');const ext=f.type==='image/png'?'png':f.type==='image/webp'?'webp':'jpg',path=`${session.user.id}/${crypto.randomUUID()}.${ext}`,raw=await f.arrayBuffer();if(!raw.byteLength)throw new Error('That image could not be read. Re-select it and try again.');const {error}=await sb.storage.from(bucket).upload(path,raw,{contentType:f.type||'image/jpeg',upsert:false});if(error)throw error;return sb.storage.from(bucket).getPublicUrl(path).data.publicUrl}"""
assert old in s, 'uploadSpecific signature changed'
s=s.replace(old,new,1)

old="""async function uploadTakeoverLogo(){if(String(selectedLogoUrl||'').startsWith(LOCAL_ASSET_PREFIX))return uploadLocalRef(selectedLogoUrl,'takeover-logos',IMAGE_STORED_LIMIT);const f=$('#logoFile')?.files?.[0];if(f)return uploadSpecific(f,'takeover-logos',IMAGE_STORED_LIMIT);return selectedLogoUrl||profile?.logo_url||null}"""
new="""async function uploadTakeoverLogo(){const f=$('#logoFile')?.files?.[0];if(f)return uploadSpecific(f,'takeover-logos',IMAGE_STORED_LIMIT);if(String(selectedLogoUrl||'').startsWith(LOCAL_ASSET_PREFIX))return uploadLocalRef(selectedLogoUrl,'takeover-logos',IMAGE_STORED_LIMIT);return selectedLogoUrl||profile?.logo_url||null}"""
assert old in s, 'uploadTakeoverLogo signature changed'
s=s.replace(old,new,1)

old="motion:['none','float','pulse','drift','glow','tilt','marquee'].includes(l.motion)?l.motion:'none'"
new="motion:['none','float','pulse','drift','glow','tilt','marquee','bounce','spin','shake','zoom','sweep'].includes(l.motion)?l.motion:'none'"
assert old in s, 'motion whitelist changed'
s=s.replace(old,new,1)

old="""<option value=\"marquee\">Slide</option></select>"""
new="""<option value=\"marquee\">Slide</option><option value=\"bounce\">Bounce</option><option value=\"spin\">Spin</option><option value=\"shake\">Shake</option><option value=\"zoom\">Zoom</option><option value=\"sweep\">Sweep</option></select>"""
assert old in s, 'motion select changed'
s=s.replace(old,new,1)

old=""" ['clean','CLEAN'],['ink','INK'],['signal','SIGNAL'],['editorial','EDITORIAL'],['luxury','LUXURY'],['blueprint','BLUEPRINT'],['pop','POP'],['terminal','TERMINAL'],['poster','POSTER'],['photo','PHOTO HERO'],['stamp','STAMP'],['split','SPLIT'],['neon','NEON'],['orbit','ORBIT'],['glass','GLASS'],['racing','RACING'],['ticker','TICKER'],['aurora','AURORA']"""
new=""" ['clean','CLEAN'],['ink','INK'],['signal','SIGNAL'],['editorial','EDITORIAL'],['luxury','LUXURY'],['blueprint','BLUEPRINT'],['pop','POP'],['terminal','TERMINAL'],['poster','POSTER'],['photo','PHOTO HERO'],['stamp','STAMP'],['split','SPLIT'],['neon','NEON'],['orbit','ORBIT'],['glass','GLASS'],['racing','RACING'],['ticker','TICKER'],['aurora','AURORA'],['glitch','GLITCH'],['chaos','CHAOS'],['hyper','HYPER'],['confetti','CONFETTI']"""
assert old in s, 'preset list changed'
s=s.replace(old,new,1)

anchor="""case'aurora':c.bg={type:'gradient',color:'#071c24',color2:'#274b5b',angle:135};c.layers=[presetShape(4,4,48,48,'#5affd8',50,.25,0,'drift'),presetShape(58,48,46,46,'#7c6cff',50,.3,0,'float'),Object.assign(presetText(brand,8,31,84,28,'modern',29,'#ffffff'),{motion:'glow',z:4}),Object.assign(presetText(site,15,68,70,9,'mono',9,'#c8fff0'),{z:4}),logo&&Object.assign(logo,{motion:'float',z:4})];break;"""
insert=anchor+"""
case'glitch':c.bg={type:'solid',color:'#050505'};c.layers=[Object.assign(presetText(brand,8,31,84,27,'display',34,'#00f5ff'),{motion:'shake',z:2}),Object.assign(presetText(brand,6,33,84,27,'display',34,'#ff2b6a'),{motion:'sweep',z:3,opacity:.72}),Object.assign(presetText(brand,9,30,84,27,'display',34,'#ffffff'),{motion:'shake',z:4}),presetShape(-15,12,130,8,'#ffffff',0,.9,-6,'sweep'),presetButton('BREAK IN',34,76,32,12,'#050505','#00f5ff'),logo&&Object.assign(logo,{motion:'zoom',z:5})];break;
case'chaos':c.bg={type:'gradient',color:'#17002d',color2:'#ff3f00',angle:125};c.layers=[presetShape(-12,-8,42,42,'#00ffd5',50,.85,0,'spin'),presetShape(72,3,34,34,'#ffe600',12,.95,18,'bounce'),presetShape(4,70,28,28,'#ffffff',50,.8,0,'shake'),presetShape(74,68,38,38,'#9b5cff',2,.85,-18,'spin'),Object.assign(presetText(brand,8,31,84,27,'heavy',31,'#ffffff'),{motion:'zoom',z:6}),Object.assign(presetButton('DO IT',35,69,30,12,'#111111','#ffe600'),{motion:'bounce',z:7}),logo&&Object.assign(logo,{motion:'shake',z:7})];break;
case'hyper':c.bg={type:'solid',color:'#ffe600'};c.layers=[presetShape(-25,4,150,15,'#111111',0,1,-10,'sweep'),presetShape(-25,78,150,11,'#ff4d00',0,1,7,'sweep'),Object.assign(presetText('NOW / NOW / NOW',-5,19,110,10,'mono',10,'#111111','left'),{motion:'marquee',z:4}),Object.assign(presetText(brand,6,36,88,28,'condensed',38,'#111111','left'),{motion:'shake',z:5}),Object.assign(presetButton('OPEN →',7,72,32,12,'#ffffff','#111111'),{motion:'pulse',z:6}),logo&&Object.assign(logo,{motion:'bounce',z:6})];break;
case'confetti':c.bg={type:'solid',color:'#f7f7f3'};c.layers=[presetShape(4,8,12,12,'#ff4d00',3,1,18,'spin'),presetShape(82,10,10,18,'#625cff',50,1,-18,'bounce'),presetShape(8,76,16,9,'#00b894',2,1,28,'shake'),presetShape(78,72,14,14,'#ffe600',3,1,0,'zoom'),Object.assign(presetText(brand,10,32,80,26,'modern',30,'#111111'),{motion:'bounce',z:5}),Object.assign(presetText('CLICK IT. OWN IT.',15,62,70,10,'mono',10,'#555555'),{motion:'shake',z:5}),logo&&Object.assign(logo,{motion:'spin',z:6})];break;"""
assert anchor in s, 'aurora preset changed'
s=s.replace(anchor,insert,1)

old="""function renderPresetChoices(){const box=$('#canvasPresets');if(!box)return;box.innerHTML='';CANVAS_PRESETS.forEach(([key,label])=>{const c=makePreset(key),b=document.createElement('button');b.type='button';b.className='preset-card';b.dataset.preset=key;const thumb=document.createElement('i');thumb.className='preset-thumb';thumb.style.background=canvasBgStyle(c);const mark=document.createElement('strong');mark.textContent=(editorCompany||'Aa').slice(0,10);thumb.appendChild(mark);const name=document.createElement('span');name.textContent=label;b.append(thumb,name);b.onclick=()=>{const frame=[...(editorCanvas?.frameCells||[])];editorCanvas=makePreset(key);if(frame.length)editorCanvas.frameCells=frame;editorSelected=null;renderEditor();renderPresetChoices()};box.appendChild(b)})}"""
new="""function renderPresetChoices(){const box=$('#canvasPresets');if(!box)return;box.innerHTML='';CANVAS_PRESETS.forEach(([key,label])=>{const c=makePreset(key),b=document.createElement('button');b.type='button';b.className='preset-card';b.dataset.preset=key;const thumb=document.createElement('i');thumb.className='preset-thumb';const fake={company_name:editorCompany||'YOUR BRAND',website:editorWebsite||'https://example.com',logo_url:selectedLogoUrl,canvas_json:c};thumb.appendChild(buildCanvasCreative(fake,null,null,false));const name=document.createElement('span');name.textContent=label;b.append(thumb,name);b.onclick=()=>{const frame=[...(editorCanvas?.frameCells||[])];editorCanvas=makePreset(key);if(frame.length)editorCanvas.frameCells=frame;editorSelected=null;renderEditor();renderPresetChoices()};box.appendChild(b)})}"""
assert old in s, 'renderPresetChoices changed'
s=s.replace(old,new,1)

s=s.replace("DRAG to move · PINCH with two fingers to resize · corner handle on desktop · use POSITION for exact control","LIVE PREVIEW STAYS ON SCREEN · DRAG to move · PINCH with two fingers to resize",1)

# Faster baseline motion + five higher-energy motion modes.
c += r'''

/* TAKEOVER V17 — mobile live editor + high-energy motion */
.motion-float{animation-duration:2.6s!important}.motion-pulse{animation-duration:1.35s!important}.motion-drift{animation-duration:3.1s!important}.motion-glow{animation-duration:1.55s!important}.motion-tilt{animation-duration:1.9s!important}.motion-marquee{animation-duration:2.35s!important}
.motion-bounce{animation:takeoverBounce .9s cubic-bezier(.2,.8,.3,1) infinite}.motion-spin{animation:takeoverSpin 2.15s linear infinite}.motion-shake{animation:takeoverShake .52s steps(2,end) infinite}.motion-zoom{animation:takeoverZoom 1.1s ease-in-out infinite}.motion-sweep{animation:takeoverSweep 1.45s cubic-bezier(.55,0,.2,1) infinite alternate}
@keyframes takeoverBounce{0%,100%{transform:translateY(0) scale(1) rotate(var(--rot,0deg))}45%{transform:translateY(-16%) scale(1.06) rotate(var(--rot,0deg))}70%{transform:translateY(3%) scale(.98) rotate(var(--rot,0deg))}}
@keyframes takeoverSpin{to{transform:rotate(calc(var(--rot,0deg) + 360deg))}}
@keyframes takeoverShake{0%,100%{transform:translate(0,0) rotate(var(--rot,0deg))}25%{transform:translate(-3%,2%) rotate(calc(var(--rot,0deg) - 2deg))}50%{transform:translate(3%,-2%) rotate(calc(var(--rot,0deg) + 2deg))}75%{transform:translate(-2%,-1%) rotate(calc(var(--rot,0deg) - 1deg))}}
@keyframes takeoverZoom{0%,100%{transform:scale(.94) rotate(var(--rot,0deg))}50%{transform:scale(1.12) rotate(var(--rot,0deg))}}
@keyframes takeoverSweep{from{transform:translateX(-18%) rotate(var(--rot,0deg))}to{transform:translateX(18%) rotate(var(--rot,0deg))}}
.preset-thumb{position:relative!important;container-type:size!important;background:#fff!important}.preset-thumb .canvas-creative{position:absolute!important;inset:0!important;pointer-events:none!important}.preset-thumb .canvas-layer{font-size:clamp(3px,var(--layer-size,5cqw),12px)!important;animation:none!important}.preset-thumb .canvas-site{display:none!important}
@media(max-width:900px){
 .canvas-modal .panel-inner{padding:12px!important}.canvas-modal .panel-head{margin-bottom:8px!important}.canvas-shell{display:grid!important;grid-template-columns:1fr!important;gap:0!important}.canvas-work{display:contents!important}
 .canvas-stage-wrap{order:1!important;position:sticky!important;top:0!important;z-index:25!important;min-height:0!important;height:42dvh!important;max-height:360px!important;padding:9px!important;border-radius:12px!important;background:rgba(233,233,227,.96)!important;backdrop-filter:blur(12px);box-shadow:0 10px 28px rgba(0,0,0,.16)!important;margin-bottom:6px!important}
 .canvas-stage{height:100%!important;width:auto!important;max-width:100%!important;max-height:100%!important;margin:auto!important;box-shadow:0 8px 24px rgba(0,0,0,.16)!important}
 .canvas-stage-tip{order:2!important;margin:3px 0 9px!important;font-size:8px!important}.canvas-toolbar{order:3!important;position:sticky!important;top:calc(min(42dvh,360px) + 4px)!important;z-index:24!important;background:#fbfbf8!important;padding:7px 0 9px!important;margin:0!important}.canvas-toolbar .tool-btn{min-height:42px!important;font-size:9px!important;flex:1 1 auto!important}
 .preset-title{order:4!important;margin-top:7px!important}.canvas-presets{order:5!important;margin-bottom:8px!important}.preset-card{flex-basis:108px!important}.preset-thumb{height:68px!important}
 .canvas-side{order:6!important;border:0!important;padding:4px 0 0!important;max-height:none!important}.canvas-section{padding:14px 0!important;margin:0!important}.canvas-section h3{font-size:11px!important}.canvas-row{gap:10px!important}.canvas-row label{font-size:10px!important;min-width:64px!important}.canvas-row input[type='text'],.canvas-row select{height:46px!important;font-size:14px!important}.canvas-row input[type='range']{min-height:34px!important}.geometry-grid{grid-template-columns:repeat(2,1fr)!important;gap:9px!important}.geometry-grid label{font-size:9px!important}.geometry-grid input{height:43px!important;font-size:14px!important}.inspector-actions{grid-template-columns:repeat(2,1fr)!important;gap:8px!important}.inspector-actions .tool-btn,.canvas-delete{min-height:44px!important;font-size:9px!important}.canvas-save{position:sticky!important;bottom:0!important;z-index:26!important;height:52px!important;font-size:13px!important;box-shadow:0 -8px 24px rgba(251,251,248,.96)!important}
}
@media(max-width:430px){.canvas-stage-wrap{height:39dvh!important}.canvas-toolbar{top:calc(min(39dvh,330px) + 4px)!important}.canvas-stage-tip{font-size:7px!important}.preset-card{flex-basis:100px!important}}
'''

b=b.replace('takeover-v3.css?v=16','takeover-v3.css?v=17').replace('takeover-v3.js?v=16','takeover-v3.js?v=17')
i=i.replace('boot.js?v=12','boot.js?v=13') if 'boot.js?v=12' in i else i.replace('boot.js?v=11','boot.js?v=13')

js.write_text(s)
css.write_text(c)
boot.write_text(b)
index.write_text(i)
