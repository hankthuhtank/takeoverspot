from pathlib import Path

root = Path('.')
js_path = root / 'takeover-v3.js'
css_path = root / 'takeover-v3.css'
index_path = root / 'index.html'
boot_path = root / 'boot.js'

js = js_path.read_text()
css = css_path.read_text()
index = index_path.read_text()
boot = boot_path.read_text()

def rep(text, old, new, label):
    if old not in text:
        raise SystemExit(f'missing {label}')
    return text.replace(old, new, 1)

# Font library + much larger size range.
js = rep(js,
"font:['clean','heavy','mono','editorial'].includes(l.font)?l.font:'clean',size:clamp(l.size||18,8,42)",
"font:['clean','heavy','mono','editorial','condensed','modern','display','serif','script','tech'].includes(l.font)?l.font:'clean',size:clamp(l.size||18,8,200)",
'font normalization')

js = rep(js,
"function layerFont(l){return l.font==='heavy'?'font-heavy':l.font==='mono'?'font-mono':l.font==='editorial'?'font-editorial':'font-clean'}",
"function layerFont(l){const map={heavy:'font-heavy',mono:'font-mono',editorial:'font-editorial',condensed:'font-condensed',modern:'font-modern',display:'font-display',serif:'font-serif',script:'font-script',tech:'font-tech'};return map[l.font]||'font-clean'}",
'font class mapper')

js = js.replace("clamp(l.size||18,8,42)}px", "clamp(l.size||18,8,200)}px")
if js.count("clamp(l.size||18,8,200)}px") < 2:
    raise SystemExit('editor size clamps were not updated')

old_select = '<select id=\\"layerFont\\"><option value=\\"clean\\">Clean</option><option value=\\"heavy\\">Heavy</option><option value=\\"mono\\">Mono</option><option value=\\"editorial\\">Editorial</option></select>'
new_select = '<select id=\\"layerFont\\"><option value=\\"clean\\">Clean · Manrope</option><option value=\\"heavy\\">Heavy · Manrope</option><option value=\\"modern\\">Modern · Space Grotesk</option><option value=\\"condensed\\">Condensed · Oswald</option><option value=\\"display\\">Display · Bebas Neue</option><option value=\\"editorial\\">Editorial · Playfair</option><option value=\\"serif\\">Classic Serif · Baskerville</option><option value=\\"mono\\">Mono · DM Mono</option><option value=\\"tech\\">Tech · Orbitron</option><option value=\\"script\\">Script · Pacifico</option></select>'
js = rep(js, old_select, new_select, 'font selector')

old_size = '<input id=\\"layerSize\\" type=\\"range\\" min=\\"8\\" max=\\"42\\" value=\\"${l.size||18}\\">'
new_size = '<input id=\\"layerSize\\" type=\\"range\\" min=\\"8\\" max=\\"200\\" value=\\"${l.size||18}\\"><output id=\\"layerSizeValue\\" class=\\"size-readout\\">${l.size||18}px</output>'
js = rep(js, old_size, new_size, 'size slider')

js = rep(js,
"if($('#layerSize'))$('#layerSize').oninput=e=>{l.size=Number(e.target.value);syncEditorLayer(l)};",
"if($('#layerSize'))$('#layerSize').oninput=e=>{l.size=Number(e.target.value);if($('#layerSizeValue'))$('#layerSizeValue').textContent=l.size+'px';syncEditorLayer(l)};",
'size handler')

# Replace invisible full-area file input behavior with an explicit clickable control.
old_logo = "function setLogoPreview(boxSelector,inputSelector,url,placeholder){const box=$(boxSelector),input=$(inputSelector);if(!box||!input)return;[...box.children].forEach(el=>{if(el!==input)el.remove()});const src=safeImg(url),el=document.createElement(src?'img':'span');if(src){el.src=src;el.alt='Logo preview'}else el.textContent=placeholder;box.insertBefore(el,input)}"
new_logo = "function setLogoPreview(boxSelector,inputSelector,url,placeholder){const box=$(boxSelector),input=$(inputSelector);if(!box||!input)return;[...box.children].forEach(el=>{if(el!==input)el.remove()});const src=safeImg(url),el=document.createElement(src?'img':'span');if(src){el.src=src;el.alt='Logo preview'}else el.textContent=placeholder||'CLICK TO CHOOSE LOGO';const choose=document.createElement('button');choose.type='button';choose.className='logo-choose';choose.textContent=src?'REPLACE LOGO':'CHOOSE LOGO';const openPicker=e=>{e?.preventDefault();e?.stopPropagation();choose.textContent='OPENING…';input.click();setTimeout(()=>{if(document.body.contains(choose))choose.textContent=src?'REPLACE LOGO':'CHOOSE LOGO'},1200)};choose.onclick=openPicker;box.onclick=e=>{if(e.target!==input&&e.target!==choose)openPicker(e)};box.insertBefore(el,input);box.insertBefore(choose,input)}"
js = rep(js, old_logo, new_logo, 'logo picker')
js = js.replace("'UPLOAD LOGO · OPTIONAL'", "'CLICK TO CHOOSE LOGO'")

# Load the new font families on the customer-facing board.
old_fonts = 'https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@500;600;700;800&display=swap'
new_fonts = 'https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=Libre+Baskerville:wght@400;700&family=Manrope:wght@500;600;700;800&family=Orbitron:wght@400;600;800&family=Oswald:wght@400;600;700&family=Pacifico&family=Playfair+Display:wght@400;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap'
index = rep(index, old_fonts, new_fonts, 'Google font link')
index = index.replace('UPLOAD LOGO · OPTIONAL</span><input id="logoFile"', 'CLICK TO CHOOSE LOGO</span><input id="logoFile"', 1)

# Cache bust JS/CSS.
boot = boot.replace("takeover-v3.css?v=4", "takeover-v3.css?v=5")
boot = boot.replace("takeover-v3.js?v=4", "takeover-v3.js?v=5")

css += r'''

/* TAKEOVER CANVAS V5 — explicit logo picker + expanded typography */
.logo-drop{cursor:pointer!important;transition:border-color .15s ease,background .15s ease,box-shadow .15s ease!important;gap:10px!important;flex-direction:column!important}
.logo-drop:hover{border-color:#111!important;background:#fff!important;box-shadow:inset 0 0 0 1px rgba(17,17,17,.05)!important}
.logo-drop input[type="file"]{display:none!important}
.logo-drop span{pointer-events:none!important}
.logo-drop img{pointer-events:none!important}
.logo-choose{cursor:pointer!important;border:0!important;border-radius:999px!important;background:#111!important;color:#fff!important;padding:9px 13px!important;font:850 8px 'DM Mono',monospace!important;letter-spacing:.05em!important;box-shadow:0 4px 14px rgba(0,0,0,.09)!important}
.logo-choose:hover{transform:translateY(-1px)}
.canvas-layer.font-modern,.editor-layer.font-modern{font-family:'Space Grotesk',Manrope,Arial,sans-serif!important}
.canvas-layer.font-condensed,.editor-layer.font-condensed{font-family:'Oswald','Arial Narrow',Arial,sans-serif!important}
.canvas-layer.font-display,.editor-layer.font-display{font-family:'Bebas Neue','Arial Narrow',Arial,sans-serif!important;letter-spacing:.02em}
.canvas-layer.font-editorial,.editor-layer.font-editorial{font-family:'Playfair Display',Georgia,'Times New Roman',serif!important}
.canvas-layer.font-serif,.editor-layer.font-serif{font-family:'Libre Baskerville',Georgia,'Times New Roman',serif!important}
.canvas-layer.font-script,.editor-layer.font-script{font-family:'Pacifico','Brush Script MT',cursive!important;font-weight:400!important}
.canvas-layer.font-tech,.editor-layer.font-tech{font-family:'Orbitron','DM Mono',monospace!important}
.canvas-row #layerSize{min-width:0;flex:1;accent-color:#111}
.size-readout{flex:0 0 50px;text-align:right;font:800 9px 'DM Mono',monospace;color:#111}
'''

js_path.write_text(js)
css_path.write_text(css)
index_path.write_text(index)
boot_path.write_text(boot)
print('TAKEOVER Canvas V5 patch applied')
