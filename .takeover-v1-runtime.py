from pathlib import Path

js_path=Path('takeover-v3.js')
css_path=Path('takeover-v3.css')
boot_path=Path('boot.js')
index_path=Path('index.html')

js=js_path.read_text()
css=css_path.read_text()
boot=boot_path.read_text()
index=index_path.read_text()

old="const TOTAL=16,COLS=4,ROWS=4;"
new="const APP_VERSION='1.0',TOTAL=16,COLS=4,ROWS=4;document.documentElement.dataset.takeoverVersion=APP_VERSION;"
assert old in js, 'version anchor missing'
js=js.replace(old,new,1)

assert "size:clamp(l.size||18,8,200)" in js, 'normalize size anchor missing'
js=js.replace("size:clamp(l.size||18,8,200)","size:clamp(l.size||18,8,96)",1)

old="d.style.fontSize=`${clamp(l.size||18,8,200)}px`;"
new="d.style.setProperty('--layer-size',`${Math.max(2,clamp(l.size||18,8,96)/4)}cqw`);"
assert old in js, 'editor font anchor missing'
js=js.replace(old,new,1)

old="const native=['image/png','image/jpeg','image/webp'].includes(file.type);if(native&&file.size<=IMAGE_STORED_LIMIT)return file;"
new="const native=['image/png','image/jpeg','image/webp'].includes(file.type);if(native&&file.size<=IMAGE_STORED_LIMIT&&file.type!=='image/jpeg')return file;"
assert old in js, 'image normalization anchor missing'
js=js.replace(old,new,1)

old="if(tip)tip.textContent=editorPreviewMode?'LIVE PREVIEW · EXACT BOARD RENDER':'LIVE PREVIEW STAYS ON SCREEN · DRAG to move · PINCH with two fingers to resize'"
new="if(tip)tip.textContent=editorPreviewMode?'EXACT PUBLISHED COMPOSITION · MOBILE = DESKTOP':'SAME COMPOSITION ON EVERY SCREEN · DRAG to move · PINCH to resize'"
assert old in js, 'preview copy anchor missing'
js=js.replace(old,new,1)

old="renderPendingReturnPreview();$('#board')?.classList.toggle('full-takeover',rects.length===1&&rects[0].cells.length===TOTAL);trackImpressions()}"
new="renderPendingReturnPreview();const full=rects.length===1&&rects[0].cells.length===TOTAL,board=$('#board');board?.classList.toggle('full-takeover',full);if(board)board.style.background=full?canvasBgStyle(rects[0].canvas):'#f7f7f3';trackImpressions()}"
assert old in js, 'renderBoard launch anchor missing'
js=js.replace(old,new,1)

old="const thumb=document.createElement('i');thumb.className='preset-thumb';thumb.appendChild(buildCanvasCreative({company_name:d.display_name,website:d.website,logo_url:d.logo_url,canvas_json:d.canvas_json},null,null,false));"
new="const thumb=document.createElement('i');thumb.className='preset-thumb';const dc=normalizeCanvas(d.canvas_json,d.display_name,d.logo_url),ds=dc.display==='divided'||!dc.frameCells?.length?{w:1,h:1}:selectionShape(dc.frameCells);thumb.style.aspectRatio=`${ds.w}/${ds.h}`;thumb.appendChild(buildCanvasCreative({company_name:d.display_name,website:d.website,logo_url:d.logo_url,canvas_json:dc},null,null,false));"
assert old in js, 'saved chooser preview anchor missing'
js=js.replace(old,new,1)

old="const preview=document.createElement('div');preview.className='saved-design-preview';preview.appendChild(buildCanvasCreative({company_name:d.display_name,website:d.website,logo_url:d.logo_url,canvas_json:d.canvas_json},null,null,false));"
new="const preview=document.createElement('div');preview.className='saved-design-preview';const dc=normalizeCanvas(d.canvas_json,d.display_name,d.logo_url),ds=dc.display==='divided'||!dc.frameCells?.length?{w:1,h:1}:selectionShape(dc.frameCells);preview.style.aspectRatio=`${ds.w}/${ds.h}`;preview.appendChild(buildCanvasCreative({company_name:d.display_name,website:d.website,logo_url:d.logo_url,canvas_json:dc},null,null,false));"
assert old in js, 'saved library preview anchor missing'
js=js.replace(old,new,1)

css += r'''

/* TAKEOVER V1.0 LAUNCH — canonical cross-device board + WYSIWYG canvas */
.board{--takeover-board-size:min(100vw,calc(100dvh - 72px))}
.board>.grid-lines,.board>.territories,.board>.spot-actions,.board>.takeover-reveal-stage{inset:auto!important;left:50%!important;right:auto!important;top:50%!important;bottom:auto!important;width:var(--takeover-board-size)!important;height:var(--takeover-board-size)!important;transform:translate(-50%,-50%)!important}
.territory,.canvas-stage{container-type:size!important}
.territory .canvas-layer,.canvas-stage .canvas-preview-live .canvas-layer,.canvas-stage .editor-layer{font-size:var(--layer-size,5cqw)!important}
.editor-layer{line-height:1.05!important;word-break:break-word!important;white-space:pre-wrap!important}
.editor-layer.is-button{padding:.55em .8em!important;border-radius:999px!important;font-weight:850!important;white-space:nowrap!important}
.editor-content{max-height:100%!important;overflow:hidden!important;line-height:1.05!important}
.canvas-site{left:2.5cqw!important;bottom:2cqw!important;font-size:1.8cqw!important}
.preset-thumb{aspect-ratio:1/1;height:auto!important;min-height:58px}
.saved-design-preview{height:auto!important;min-height:72px}
.shape-particle{width:1.1cqw!important}
.canvas-layer[data-shape="ring"],.editor-layer[data-shape="ring"]{border-width:.6cqw!important}
@keyframes takeoverParticle{0%{transform:translate3d(-2cqw,2.3cqw,0);opacity:.25}55%{opacity:.95}100%{transform:translate3d(2.6cqw,-3.1cqw,0);opacity:.5}}
@media(max-width:720px){.board{--takeover-board-size:min(100vw,calc(100dvh - 146px))}.board>.grid-lines,.board>.territories,.board>.spot-actions,.board>.takeover-reveal-stage{top:calc(50dvh + 25px)!important}}
@media(max-width:720px) and (orientation:landscape){.board{--takeover-board-size:min(100vw,calc(100dvh - 88px))}.board>.grid-lines,.board>.territories,.board>.spot-actions,.board>.takeover-reveal-stage{top:calc(50dvh + 10px)!important}.site-legal{display:none!important}}
'''

assert 'takeover-v3.css?v=22.3' in boot and 'takeover-v3.js?v=22.3' in boot, 'boot cache anchors missing'
boot=boot.replace('takeover-v3.css?v=22.3','takeover-v3.css?v=1.0',1).replace('takeover-v3.js?v=22.3','takeover-v3.js?v=1.0',1)
assert 'boot.js?v=18' in index, 'index boot cache anchor missing'
index=index.replace('boot.js?v=18','boot.js?v=1.0',1)

js_path.write_text(js)
css_path.write_text(css)
boot_path.write_text(boot)
index_path.write_text(index)
print('TAKEOVER V1.0 runtime patch applied')
