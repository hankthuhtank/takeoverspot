from pathlib import Path

js_path=Path('takeover-v3.js')
css_path=Path('takeover-v3.css')
boot_path=Path('boot.js')
js=js_path.read_text()
css=css_path.read_text()
boot=boot_path.read_text()

old="let editorCanvas=null,editorCreativeId=null,editorContext='purchase',editorSelected=null,editorCompany='',editorWebsite='',moderationSpot=null,refundAttempt=null,lastImpressionKey='',adminHistorySpot='all',adminControlSpot=null;"
new=old+"\nlet editorPreviewMode=false;"
assert old in js, 'editor state target missing'
js=js.replace(old,new,1)

old='<button class="tool-btn" id="addLogo">+ LOGO</button></div><div class="canvas-stage-wrap">'
new='<button class="tool-btn" id="addLogo">+ LOGO</button><button class="tool-btn canvas-preview-toggle" id="toggleCanvasPreview" type="button" aria-pressed="false">PREVIEW</button></div><div class="canvas-stage-wrap">'
assert old in js, 'toolbar target missing'
js=js.replace(old,new,1)

old="$('#canvasCompany').oninput=e=>{editorCompany=e.target.value;renderPresetChoices()};$('#canvasWebsite').oninput=e=>editorWebsite=e.target.value;"
new="$('#canvasCompany').oninput=e=>{editorCompany=e.target.value;renderPresetChoices();if(editorPreviewMode)renderEditor()};$('#canvasWebsite').oninput=e=>{editorWebsite=e.target.value;if(editorPreviewMode)renderEditor()};"
assert old in js, 'identity input target missing'
js=js.replace(old,new,1)

old="$('#addLogo').onclick=()=>{const logo=selectedLogoUrl||profile?.logo_url;if(!logo||!safeImg(logo))return toast('Upload a logo above first');addEditorLayer({type:'image',role:'logo',src:logo,x:25,y:24,w:50,h:45,fit:'contain'})};$('#displayCombined').onclick=()=>{editorCanvas.display='combined';syncDisplayButtons();renderEditor();renderPurchaseCanvasPreview()};"
new="$('#addLogo').onclick=()=>{const logo=selectedLogoUrl||profile?.logo_url;if(!logo||!safeImg(logo))return toast('Upload a logo above first');addEditorLayer({type:'image',role:'logo',src:logo,x:25,y:24,w:50,h:45,fit:'contain'})};$('#toggleCanvasPreview').onclick=()=>setCanvasPreview(!editorPreviewMode);$('#displayCombined').onclick=()=>{editorCanvas.display='combined';syncDisplayButtons();renderEditor();renderPurchaseCanvasPreview()};"
assert old in js, 'preview handler target missing'
js=js.replace(old,new,1)

old="function openCanvasEditor(context='purchase',creativeId=null){ensureCanvasModal();editorContext=context;"
new="function openCanvasEditor(context='purchase',creativeId=null){ensureCanvasModal();editorPreviewMode=false;syncCanvasPreviewUi();editorContext=context;"
assert old in js, 'open editor target missing'
js=js.replace(old,new,1)

old="function closeCanvasEditor(){$('#canvasModal')?.classList.remove('on');if(!$$('.panel.on').length)$('#scrim')?.classList.remove('on')}\nfunction syncDisplayButtons()"
new="function closeCanvasEditor(){editorPreviewMode=false;syncCanvasPreviewUi();$('#canvasModal')?.classList.remove('on');if(!$$('.panel.on').length)$('#scrim')?.classList.remove('on')}\nfunction syncCanvasPreviewUi(){const stage=$('#canvasStage'),btn=$('#toggleCanvasPreview'),tip=$('.canvas-stage-tip');stage?.classList.toggle('is-preview',editorPreviewMode);if(btn){btn.classList.toggle('active',editorPreviewMode);btn.setAttribute('aria-pressed',String(editorPreviewMode));btn.textContent=editorPreviewMode?'EDIT':'PREVIEW'}if(tip)tip.textContent=editorPreviewMode?'LIVE PREVIEW · EXACT BOARD RENDER':'LIVE PREVIEW STAYS ON SCREEN · DRAG to move · PINCH with two fingers to resize'}\nfunction setCanvasPreview(on){editorPreviewMode=!!on;syncCanvasPreviewUi();renderEditor()}\nfunction syncDisplayButtons()"
assert old in js, 'close editor target missing'
js=js.replace(old,new,1)

old="function renderEditor(){const stage=$('#canvasStage');if(!stage||!editorCanvas)return;stage.querySelectorAll('.editor-layer').forEach(x=>x.remove());stage.style.background=canvasBgStyle(editorCanvas);editorCanvas.layers.slice().sort((x,y)=>Number(x.z||1)-Number(y.z||1)).forEach(l=>{"
new="function renderEditor(){const stage=$('#canvasStage');if(!stage||!editorCanvas)return;stage.querySelectorAll('.editor-layer,.canvas-preview-live').forEach(x=>x.remove());stage.style.background=canvasBgStyle(editorCanvas);syncCanvasPreviewUi();if(editorPreviewMode){const live=buildCanvasCreative({company_name:editorCompany||'YOUR BRAND',website:editorWebsite||'',logo_url:selectedLogoUrl,canvas_json:editorCanvas},null,selected,false);live.classList.add('canvas-preview-live');stage.appendChild(live);renderInspector();return}editorCanvas.layers.slice().sort((x,y)=>Number(x.z||1)-Number(y.z||1)).forEach(l=>{"
assert old in js, 'render editor target missing'
js=js.replace(old,new,1)

css += "\n\n/* TAKEOVER V22.2 — subtle exact-live Canvas preview */\n.canvas-stage{container-type:size!important}.canvas-preview-toggle{margin-left:auto!important}.canvas-stage.is-preview .editor-grid{display:none!important}.canvas-stage .canvas-preview-live{position:absolute!important;inset:0!important;width:100%!important;height:100%!important;pointer-events:none!important}.canvas-stage .canvas-preview-live .canvas-layer{font-size:clamp(8px,var(--layer-size,5cqw),82px)!important}.canvas-stage.is-preview{cursor:default!important}.canvas-stage.is-preview .canvas-preview-live{z-index:40}.canvas-stage.is-preview .canvas-preview-live .canvas-site{z-index:50}\n@media(max-width:900px){.canvas-preview-toggle{margin-left:0!important;flex:0 0 auto!important}}\n"

assert "takeover-v3.css?v=22.1" in boot and "takeover-v3.js?v=22" in boot, 'boot cache target missing'
boot=boot.replace("takeover-v3.css?v=22.1","takeover-v3.css?v=22.2",1).replace("takeover-v3.js?v=22","takeover-v3.js?v=22.2",1)

js_path.write_text(js)
css_path.write_text(css)
boot_path.write_text(boot)
print('V22.2 preview patch applied')
