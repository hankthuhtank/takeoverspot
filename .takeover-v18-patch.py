from pathlib import Path
import re

js=Path('takeover-v3.js'); css=Path('takeover-v3.css'); boot=Path('boot.js'); index=Path('index.html')
s=js.read_text(); c=css.read_text(); b=boot.read_text(); i=index.read_text()

def rep(old,new,label,count=1):
    global s
    n=s.count(old)
    assert n>=count, f'{label}: expected {count}, found {n}'
    s=s.replace(old,new,count)

# Preserve a richer shape vocabulary in saved creatives.
rep("motion:['none','float','pulse','drift','glow','tilt','marquee','bounce','spin','shake','zoom','sweep'].includes(l.motion)?l.motion:'none',rotation:clamp(l.rotation||0,-180,180),opacity:clamp(l.opacity==null?1:l.opacity,.15,1),radius:clamp(l.radius||0,0,50),z:clamp(l.z||1,0,30)",
    "motion:['none','float','pulse','drift','glow','tilt','marquee','bounce','spin','shake','zoom','sweep','orbit','morph','flicker'].includes(l.motion)?l.motion:'none',rotation:clamp(l.rotation||0,-180,180),opacity:clamp(l.opacity==null?1:l.opacity,.15,1),radius:clamp(l.radius||0,0,50),shapeStyle:['rect','blob','ring','star','burst','ribbon','diamond','particles'].includes(l.shapeStyle)?l.shapeStyle:'rect',z:clamp(l.z||1,0,30)", 'normalize shape/motion')

# Shared shape decorator for live board, previews and editor.
anchor="function shapeLayerGeom(l,cells,display='combined'){return{x:Number(l.x)||0,y:Number(l.y)||0,w:Number(l.w)||40,h:Number(l.h)||20,size:Number(l.size)||18}}\n"
insert=anchor+"function decorateShapeLayer(d,l){if(l.type!=='shape')return;const kind=l.shapeStyle||'rect';d.dataset.shape=kind;d.style.setProperty('--shape-fill',l.bg||'#111111');if(['ring','particles'].includes(kind))d.style.background='transparent';if(kind==='particles'&&!d.querySelector('.shape-particle')){for(let n=0;n<14;n++){const p=document.createElement('i');p.className='shape-particle';p.style.setProperty('--p',String(n));d.appendChild(p)}}}\n"
rep(anchor,insert,'shape decorator')

rep("d.className=`canvas-layer ${layerFont(l)} ${l.type==='button'?'is-button':''} ${l.type==='shape'?'is-shape':''} motion-${l.motion||'none'}`;",
    "d.className=`canvas-layer ${layerFont(l)} ${l.type==='button'?'is-button':''} ${l.type==='shape'?'is-shape':''} motion-${l.motion||'none'}`;", 'canvas class')
rep("if(l.type==='shape'){d.style.background=l.bg||'#111111';d.style.borderRadius=`${Number(l.radius||0)}%`}else if(l.type==='button')",
    "if(l.type==='shape'){d.style.background=l.bg||'#111111';d.style.borderRadius=`${Number(l.radius||0)}%`;decorateShapeLayer(d,l)}else if(l.type==='button')", 'live shape render')

# Editor shape rendering.
rep("if(l.type==='button'||l.type==='shape')d.style.background=l.bg||'#111';if(l.type==='shape')d.style.borderRadius=`${Number(l.radius||0)}%`}",
    "if(l.type==='button'||l.type==='shape')d.style.background=l.bg||'#111';if(l.type==='shape'){d.style.borderRadius=`${Number(l.radius||0)}%`;d.dataset.shape=l.shapeStyle||'rect';d.style.setProperty('--shape-fill',l.bg||'#111');if(['ring','particles'].includes(l.shapeStyle||'rect'))d.style.background='transparent'}}", 'editor style')
rep("if(l.type==='button'){const content=document.createElement('span');content.className='editor-content';content.textContent=l.text||'LEARN MORE';d.appendChild(content)}else if(l.type==='image'&&safeImg(l.src))",
    "if(l.type==='button'){const content=document.createElement('span');content.className='editor-content';content.textContent=l.text||'LEARN MORE';d.appendChild(content)}else if(l.type==='shape'){decorateShapeLayer(d,l)}else if(l.type==='image'&&safeImg(l.src))", 'editor shape children')

# Pinch text should scale typography as well as geometry, with dampening.
rep("editorTouchGesture={id,mode:'pinch',dist:Math.max(.01,touchDistance(touches[0],touches[1])),mid,ow:l.w,oh:l.h,cx:l.x+l.w/2,cy:l.y+l.h/2}",
    "editorTouchGesture={id,mode:'pinch',dist:Math.max(.01,touchDistance(touches[0],touches[1])),mid,ow:l.w,oh:l.h,os:Number(l.size||18),cx:l.x+l.w/2,cy:l.y+l.h/2}", 'pinch baseline')
old="const mid=touchMidpoint(ev.touches[0],ev.touches[1]),scale=touchDistance(ev.touches[0],ev.touches[1])/editorTouchGesture.dist,nw=clamp(editorTouchGesture.ow*scale,5,150),nh=clamp(editorTouchGesture.oh*scale,5,150),dx=mid.x-editorTouchGesture.mid.x,dy=mid.y-editorTouchGesture.mid.y;layer.w=nw;layer.h=nh;layer.x=clamp(editorTouchGesture.cx+dx-nw/2,-25,Math.max(-25,125-nw));layer.y=clamp(editorTouchGesture.cy+dy-nh/2,-25,Math.max(-25,125-nh));syncEditorLayer(layer);return"
new="const mid=touchMidpoint(ev.touches[0],ev.touches[1]),rawScale=touchDistance(ev.touches[0],ev.touches[1])/editorTouchGesture.dist,isType=!['image','shape'].includes(layer.type),scale=isType?1+(rawScale-1)*.62:rawScale,nw=clamp(editorTouchGesture.ow*scale,5,150),nh=clamp(editorTouchGesture.oh*scale,5,150),dx=mid.x-editorTouchGesture.mid.x,dy=mid.y-editorTouchGesture.mid.y;layer.w=nw;layer.h=nh;if(isType)layer.size=clamp(editorTouchGesture.os*scale,8,96);layer.x=clamp(editorTouchGesture.cx+dx-nw/2,-25,Math.max(-25,125-nw));layer.y=clamp(editorTouchGesture.cy+dy-nh/2,-25,Math.max(-25,125-nh));syncEditorLayer(layer);return"
rep(old,new,'pinch typography')

# Sane text size UI + fine controls.
old="<div class=\"canvas-row\"><label>SIZE</label><input id=\"layerSize\" type=\"range\" min=\"8\" max=\"200\" value=\"${l.size||18}\"><output id=\"layerSizeValue\" class=\"size-readout\">${l.size||18}px</output></div>"
new="<div class=\"canvas-row size-row\"><label>SIZE</label><div class=\"size-control\"><button type=\"button\" id=\"layerSizeDown\" aria-label=\"Smaller text\">−</button><input id=\"layerSize\" type=\"range\" min=\"8\" max=\"96\" step=\"1\" value=\"${clamp(l.size||18,8,96)}\"><button type=\"button\" id=\"layerSizeUp\" aria-label=\"Larger text\">+</button><output id=\"layerSizeValue\" class=\"size-readout\">${Math.round(clamp(l.size||18,8,96))}px</output></div></div>"
rep(old,new,'size control')
old="if($('#layerSize'))$('#layerSize').oninput=e=>{l.size=Number(e.target.value);$('#layerSizeValue').textContent=l.size+'px';sync()};"
new="if($('#layerSize')){const setSize=v=>{l.size=Math.round(clamp(v,8,96));$('#layerSize').value=String(l.size);$('#layerSizeValue').textContent=l.size+'px';sync()};$('#layerSize').oninput=e=>setSize(Number(e.target.value));if($('#layerSizeDown'))$('#layerSizeDown').onclick=()=>setSize(Number(l.size||18)-1);if($('#layerSizeUp'))$('#layerSizeUp').onclick=()=>setSize(Number(l.size||18)+1)};"
rep(old,new,'size bindings')

# Shape selector and extra motion options.
old="${l.type==='shape'?`<div class=\"canvas-row\"><label>ROUND</label><input id=\"layerRadius\" type=\"range\" min=\"0\" max=\"50\" value=\"${l.radius||0}\"></div>`:''}<div class=\"canvas-row\"><label>MOTION</label><select id=\"layerMotion\"><option value=\"none\">None</option><option value=\"float\">Float</option><option value=\"pulse\">Pulse</option><option value=\"drift\">Drift</option><option value=\"glow\">Glow</option><option value=\"tilt\">Tilt</option><option value=\"marquee\">Slide</option><option value=\"bounce\">Bounce</option><option value=\"spin\">Spin</option><option value=\"shake\">Shake</option><option value=\"zoom\">Zoom</option><option value=\"sweep\">Sweep</option></select></div>"
new="${l.type==='shape'?`<div class=\"canvas-row\"><label>SHAPE</label><select id=\"layerShape\"><option value=\"rect\">Block</option><option value=\"blob\">Organic Blob</option><option value=\"ring\">Ring</option><option value=\"star\">Star</option><option value=\"burst\">Burst</option><option value=\"ribbon\">Ribbon</option><option value=\"diamond\">Diamond</option><option value=\"particles\">Particle Field</option></select></div><div class=\"canvas-row\"><label>ROUND</label><input id=\"layerRadius\" type=\"range\" min=\"0\" max=\"50\" value=\"${l.radius||0}\"></div>`:''}<div class=\"canvas-row\"><label>MOTION</label><select id=\"layerMotion\"><option value=\"none\">None</option><option value=\"float\">Float</option><option value=\"pulse\">Pulse</option><option value=\"drift\">Drift</option><option value=\"glow\">Glow</option><option value=\"tilt\">Tilt</option><option value=\"marquee\">Slide</option><option value=\"bounce\">Bounce</option><option value=\"spin\">Spin</option><option value=\"shake\">Shake</option><option value=\"zoom\">Zoom</option><option value=\"sweep\">Sweep</option><option value=\"orbit\">Orbit</option><option value=\"morph\">Morph</option><option value=\"flicker\">Flicker</option></select></div>"
rep(old,new,'shape/motion inspector')
old="if($('#layerRadius'))$('#layerRadius').oninput=e=>{l.radius=Number(e.target.value);sync()};if($('#layerMotion'))"
new="if($('#layerShape')){$('#layerShape').value=l.shapeStyle||'rect';$('#layerShape').onchange=e=>{l.shapeStyle=e.target.value;renderEditor()}}if($('#layerRadius'))$('#layerRadius').oninput=e=>{l.radius=Number(e.target.value);sync()};if($('#layerMotion'))"
rep(old,new,'shape binding')

# New shape defaults and preset helpers.
rep("function presetShape(x,y,w,h,bg,radius=0,opacity=1,rotation=0,motion='none'){return{id:uid(),type:'shape',x,y,w,h,bg,radius,opacity,rotation,motion,z:0}}",
    "function presetShape(x,y,w,h,bg,radius=0,opacity=1,rotation=0,motion='none',shapeStyle='rect'){return{id:uid(),type:'shape',x,y,w,h,bg,radius,opacity,rotation,motion,shapeStyle,z:0}}", 'preset shape helper')

# Expand preset library.
old="['glitch','GLITCH'],['chaos','CHAOS'],['hyper','HYPER'],['confetti','CONFETTI']"
new="['glitch','GLITCH'],['chaos','CHAOS'],['hyper','HYPER'],['confetti','CONFETTI'],['gravity','GRAVITY'],['liquid','LIQUID'],['kinetic','KINETIC'],['stardust','STARDUST']"
rep(old,new,'preset list')

# Upgrade some existing presets away from blocky geometry.
old="case'orbit':c.bg={type:'solid',color:'#f4f2e9'};c.layers=[presetShape(-6,10,38,38,'#ff5f40',50,.9,0,'drift'),presetShape(72,58,34,34,'#111111',50,.95,0,'float'),Object.assign(presetText(brand,13,33,74,25,'modern',28,'#111111'),{z:4}),Object.assign(presetText('OWN THE SPACE',18,63,64,9,'mono',10,'#555555'),{motion:'float',z:4}),logo&&Object.assign(logo,{z:4})];break;"
new="case'orbit':c.bg={type:'solid',color:'#f4f2e9'};c.layers=[presetShape(3,3,94,94,'#ff5f40',50,.75,0,'orbit','ring'),presetShape(0,0,100,100,'#111111',0,.5,0,'none','particles'),presetShape(72,6,20,20,'#111111',0,.95,0,'spin','star'),Object.assign(presetText(brand,12,34,76,24,'modern',29,'#111111'),{z:5}),Object.assign(presetText('IN MOTION · '+site,18,63,64,9,'mono',9,'#555555'),{motion:'marquee',z:5}),logo&&Object.assign(logo,{motion:'float',z:6})];break;"
rep(old,new,'orbit preset')
old="case'aurora':c.bg={type:'gradient',color:'#071c24',color2:'#274b5b',angle:135};c.layers=[presetShape(4,4,48,48,'#5affd8',50,.25,0,'drift'),presetShape(58,48,46,46,'#7c6cff',50,.3,0,'float'),Object.assign(presetText(brand,8,31,84,28,'modern',29,'#ffffff'),{motion:'glow',z:4}),Object.assign(presetText(site,15,68,70,9,'mono',9,'#c8fff0'),{z:4}),logo&&Object.assign(logo,{motion:'float',z:4})];break;"
new="case'aurora':c.bg={type:'gradient',color:'#061822',color2:'#2b1748',angle:135};c.layers=[presetShape(-10,-12,62,62,'#5affd8',50,.32,0,'morph','blob'),presetShape(55,45,62,62,'#8d6cff',50,.34,0,'morph','blob'),presetShape(0,0,100,100,'#ffffff',0,.34,0,'none','particles'),Object.assign(presetText(brand,8,31,84,27,'modern',30,'#ffffff'),{motion:'glow',z:5}),Object.assign(presetText(site,15,67,70,9,'mono',9,'#c8fff0'),{motion:'float',z:5}),logo&&Object.assign(logo,{motion:'orbit',z:6})];break;"
rep(old,new,'aurora preset')
old="case'confetti':c.bg={type:'solid',color:'#f7f7f3'};c.layers=[presetShape(4,8,12,12,'#ff4d00',3,1,18,'spin'),presetShape(82,10,10,18,'#625cff',50,1,-18,'bounce'),presetShape(8,76,16,9,'#00b894',2,1,28,'shake'),presetShape(78,72,14,14,'#ffe600',3,1,0,'zoom'),Object.assign(presetText(brand,10,32,80,26,'modern',30,'#111111'),{motion:'bounce',z:5}),Object.assign(presetText('CLICK IT. OWN IT.',15,62,70,10,'mono',10,'#555555'),{motion:'shake',z:5}),logo&&Object.assign(logo,{motion:'spin',z:6})];break;"
new="case'confetti':c.bg={type:'solid',color:'#f7f7f3'};c.layers=[presetShape(0,0,100,100,'#ff4d00',0,.85,0,'none','particles'),presetShape(5,8,18,18,'#625cff',0,.9,12,'spin','burst'),presetShape(78,68,18,18,'#00b894',0,.95,-10,'bounce','star'),presetShape(76,6,18,11,'#ffe600',0,.95,-12,'sweep','ribbon'),Object.assign(presetText(brand,10,32,80,26,'modern',30,'#111111'),{motion:'bounce',z:5}),Object.assign(presetText('CLICK IT. OWN IT.',15,62,70,10,'mono',10,'#555555'),{motion:'shake',z:5}),logo&&Object.assign(logo,{motion:'orbit',z:6})];break;"
rep(old,new,'confetti preset')

# Add four modern art-direction presets before default.
anchor="default:c.bg={type:'solid',color:'#ffffff'};c.layers=[logo,presetText(brand,10,32,80,24,'heavy',28,'#111111'),presetText(site,12,66,76,9,'mono',9,'#777777'),presetButton('VISIT',34,80,32,10,'#ffffff','#111111')];}"
insert="""case'gravity':c.bg={type:'gradient',color:'#050711',color2:'#16102f',angle:145};c.layers=[presetShape(0,0,100,100,'#c9b7ff',0,.62,0,'none','particles'),presetShape(9,10,82,82,'#7a5cff',50,.7,0,'orbit','ring'),presetShape(69,11,22,22,'#ffdf70',0,.95,0,'spin','star'),Object.assign(presetText(brand,10,34,80,24,'tech',27,'#ffffff'),{motion:'flicker',z:6}),Object.assign(presetText('PULLING YOU IN',20,62,60,8,'mono',9,'#c9b7ff'),{motion:'float',z:6}),logo&&Object.assign(logo,{motion:'orbit',z:7})];break;
case'liquid':c.bg={type:'solid',color:'#f5efe7'};c.layers=[presetShape(-15,-8,72,72,'#ff6534',50,.88,0,'morph','blob'),presetShape(55,48,64,64,'#6857ff',50,.88,0,'morph','blob'),presetShape(4,4,92,92,'#111111',50,.28,0,'orbit','ring'),Object.assign(presetText(brand,9,29,82,30,'editorial',31,'#111111'),{z:6}),Object.assign(presetText('hello, internet',55,65,35,10,'script',14,'#111111','right'),{motion:'float',z:7}),logo&&Object.assign(logo,{motion:'drift',z:7})];break;
case'kinetic':c.bg={type:'solid',color:'#0b0b0b'};c.layers=[presetShape(-20,3,135,18,'#ff5a26',0,1,-8,'sweep','ribbon'),presetShape(-18,75,138,15,'#5b67ff',0,1,7,'sweep','ribbon'),presetShape(0,0,100,100,'#ffffff',0,.22,0,'none','particles'),Object.assign(presetText(brand,5,31,90,31,'condensed',40,'#ffffff','left'),{motion:'shake',z:6}),Object.assign(presetText('MOVE / CLICK / TAKE',7,66,72,8,'mono',9,'#ffdf70','left'),{motion:'marquee',z:6}),logo&&Object.assign(logo,{motion:'bounce',z:7})];break;
case'stardust':c.bg={type:'gradient',color:'#07070a',color2:'#151522',angle:120};c.layers=[presetShape(0,0,100,100,'#ffffff',0,.8,0,'none','particles'),presetShape(64,5,30,30,'#c6a6ff',50,.9,0,'orbit','ring'),presetShape(5,72,18,18,'#fff0a8',0,.9,0,'flicker','burst'),Object.assign(presetText(brand,10,29,80,30,'serif',30,'#ffffff'),{motion:'float',z:5}),Object.assign(presetText('make some noise',45,62,45,10,'script',13,'#d7c7ff','right'),{motion:'drift',z:6}),logo&&Object.assign(logo,{motion:'flicker',z:7})];break;
"""+anchor
rep(anchor,insert,'new presets')

# Make newly-added shapes usable from + SHAPE.
rep("$('#addShape').onclick=()=>addEditorLayer({type:'shape',x:25,y:25,w:50,h:50,bg:'#111111',radius:8,opacity:1,z:0});",
    "$('#addShape').onclick=()=>addEditorLayer({type:'shape',x:25,y:25,w:50,h:50,bg:'#111111',radius:8,opacity:1,shapeStyle:'blob',motion:'float',z:0});", 'add shape default')

# V18 CSS: modern shape language, particles, motion and sane size controls.
c += r'''

/* TAKEOVER V18 — expressive shapes, particles + sane typography scaling */
.canvas-layer[data-shape="blob"],.editor-layer[data-shape="blob"]{border-radius:43% 57% 66% 34% / 37% 42% 58% 63%!important}
.canvas-layer[data-shape="ring"],.editor-layer[data-shape="ring"]{background:transparent!important;border:3px solid var(--shape-fill)!important;border-radius:50%!important}
.canvas-layer[data-shape="diamond"],.editor-layer[data-shape="diamond"]{clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%)}
.canvas-layer[data-shape="star"],.editor-layer[data-shape="star"]{clip-path:polygon(50% 0%,61% 34%,98% 35%,68% 56%,79% 92%,50% 70%,21% 92%,32% 56%,2% 35%,39% 34%)}
.canvas-layer[data-shape="burst"],.editor-layer[data-shape="burst"]{clip-path:polygon(50% 0,60% 28%,82% 10%,76% 38%,100% 38%,78% 55%,96% 76%,68% 70%,64% 100%,48% 76%,28% 96%,31% 68%,0 64%,24% 48%,4% 27%,34% 30%)}
.canvas-layer[data-shape="ribbon"],.editor-layer[data-shape="ribbon"]{clip-path:polygon(0 18%,82% 0,100% 50%,82% 100%,0 82%,9% 50%)}
.canvas-layer[data-shape="particles"],.editor-layer[data-shape="particles"]{background:transparent!important;overflow:visible!important;pointer-events:none!important}
.shape-particle{position:absolute;width:clamp(3px,1.1cqw,9px);aspect-ratio:1;border-radius:50%;background:var(--shape-fill);opacity:.75;animation:takeoverParticle 2.7s ease-in-out infinite alternate;box-shadow:0 0 10px color-mix(in srgb,var(--shape-fill) 65%,transparent)}
.shape-particle:nth-child(1){left:8%;top:14%;animation-delay:-.2s}.shape-particle:nth-child(2){left:22%;top:73%;animation-delay:-1.1s;scale:.55}.shape-particle:nth-child(3){left:34%;top:28%;animation-delay:-1.8s;scale:1.3}.shape-particle:nth-child(4){left:47%;top:86%;animation-delay:-.7s;scale:.7}.shape-particle:nth-child(5){left:58%;top:12%;animation-delay:-2.2s;scale:.45}.shape-particle:nth-child(6){left:71%;top:57%;animation-delay:-1.5s;scale:1.2}.shape-particle:nth-child(7){left:87%;top:24%;animation-delay:-.9s;scale:.75}.shape-particle:nth-child(8){left:91%;top:82%;animation-delay:-2.4s;scale:.5}.shape-particle:nth-child(9){left:13%;top:47%;animation-delay:-1.9s;scale:.4}.shape-particle:nth-child(10){left:39%;top:55%;animation-delay:-.4s;scale:.8}.shape-particle:nth-child(11){left:64%;top:76%;animation-delay:-1.3s;scale:.55}.shape-particle:nth-child(12){left:78%;top:39%;animation-delay:-2.1s;scale:.4}.shape-particle:nth-child(13){left:52%;top:43%;animation-delay:-.8s;scale:.35}.shape-particle:nth-child(14){left:27%;top:8%;animation-delay:-1.6s;scale:.5}
@keyframes takeoverParticle{0%{transform:translate3d(-7px,8px,0);opacity:.25}55%{opacity:.95}100%{transform:translate3d(9px,-11px,0);opacity:.5}}
.motion-orbit{animation:takeoverOrbit 3s linear infinite}.motion-morph{animation:takeoverMorph 3.4s ease-in-out infinite alternate}.motion-flicker{animation:takeoverFlicker 1.2s steps(2,end) infinite}
@keyframes takeoverOrbit{0%{transform:rotate(var(--rot,0deg)) translateX(0)}25%{transform:rotate(calc(var(--rot,0deg) + 3deg)) translate(3%,-4%)}50%{transform:rotate(var(--rot,0deg)) translate(-2%,3%)}75%{transform:rotate(calc(var(--rot,0deg) - 3deg)) translate(3%,2%)}100%{transform:rotate(var(--rot,0deg)) translateX(0)}}
@keyframes takeoverMorph{0%{transform:scale(.96) rotate(var(--rot,0deg));border-radius:38% 62% 67% 33% / 46% 32% 68% 54%}50%{transform:scale(1.05) rotate(calc(var(--rot,0deg) + 5deg));border-radius:63% 37% 39% 61% / 35% 58% 42% 65%}100%{transform:scale(.99) rotate(calc(var(--rot,0deg) - 4deg));border-radius:45% 55% 70% 30% / 61% 36% 64% 39%}}
@keyframes takeoverFlicker{0%,17%,38%,61%,100%{opacity:1;filter:brightness(1)}18%,37%,62%,70%{opacity:.58;filter:brightness(1.45)}}
.size-row{align-items:center!important}.size-control{display:grid;grid-template-columns:34px minmax(0,1fr) 34px 48px;gap:7px;align-items:center;width:100%}.size-control button{height:34px;border:1px solid #d2d2cb;border-radius:8px;background:#fff;font-weight:900;font-size:17px;line-height:1}.size-control input[type="range"]{width:100%;min-width:0}.size-control output{text-align:center;font:800 9px 'DM Mono',monospace;color:#555}
@media(max-width:900px){.size-control{grid-template-columns:42px minmax(0,1fr) 42px 52px;gap:8px}.size-control button{height:42px;font-size:21px}.size-control input[type="range"]{height:36px}.shape-particle{width:5px}}
@media(prefers-reduced-motion:reduce){.shape-particle{animation:none!important}.motion-orbit,.motion-morph,.motion-flicker{animation:none!important}}
'''

b=b.replace('takeover-v3.css?v=17','takeover-v3.css?v=18').replace('takeover-v3.js?v=17','takeover-v3.js?v=18')
i=i.replace('boot.js?v=13','boot.js?v=14')

js.write_text(s); css.write_text(c); boot.write_text(b); index.write_text(i)
