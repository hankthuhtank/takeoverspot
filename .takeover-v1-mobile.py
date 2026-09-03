from pathlib import Path

js_path=Path('takeover-v3.js')
css_path=Path('takeover-v3.css')
boot_path=Path('boot.js')
index_path=Path('index.html')

js=js_path.read_text()
css=css_path.read_text()
boot=boot_path.read_text()
index=index_path.read_text()


def replace_once(text, old, new, label):
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'Missing expected {label}')
    return text.replace(old, new, 1)

js=replace_once(js,
    "const APP_VERSION='1.0',TOTAL=16",
    "const APP_VERSION='1.0.1',TOTAL=16",
    'APP_VERSION')

old_pill="const b=document.createElement('button');b.className='take-pill';b.textContent=own(s)?`DEFEND · ${cash(Number(s.current_price)+Number(config.min_increment))}`:shieldBlocked()?'PROTECTED':`TAKE · ${cash(minTake(s))}`;b.disabled=!own(s)&&shieldBlocked();b.onclick=()=>own(s)?openDefend(n):openTakeover(n);a.appendChild(b)"
new_pill="const b=document.createElement('button'),isOwn=own(s),nextPrice=isOwn?Number(s.current_price)+Number(config.min_increment):minTake(s);b.className='take-pill';b.textContent=isOwn?`DEFEND · ${cash(nextPrice)}`:shieldBlocked()?'PROTECTED':`TAKE · ${cash(nextPrice)}`;b.dataset.short=isOwn?`D ${cash(nextPrice)}`:shieldBlocked()?'LOCK':`↑ ${cash(nextPrice)}`;b.setAttribute('aria-label',b.textContent);b.disabled=!isOwn&&shieldBlocked();b.onclick=()=>isOwn?openDefend(n):openTakeover(n);a.appendChild(b)"
js=replace_once(js,old_pill,new_pill,'mobile action chip data')

old_tip="if(tip)tip.textContent=editorPreviewMode?'EXACT PUBLISHED COMPOSITION · MOBILE = DESKTOP':'SAME COMPOSITION ON EVERY SCREEN · DRAG to move · PINCH to resize'"
new_tip="if(tip)tip.textContent=editorPreviewMode?'EXACT PUBLISHED COMPOSITION · MOBILE = DESKTOP':'POSITION IS THE ANCHOR · DRAG to move · PINCH to resize'"
js=replace_once(js,old_tip,new_tip,'canvas tip')

marker='/* TAKEOVER V1.0.1 — mobile-first camera + exact edit/live containment */'
if marker not in css:
    css += r'''


/* TAKEOVER V1.0.1 — mobile-first camera + exact edit/live containment */
/* Edit mode and published mode now obey the same text box. Selection handles may sit outside the box; the creative may not. */
.canvas-stage:not(.is-preview) .editor-layer{animation:none!important}
.editor-content{display:block!important;width:100%!important;min-width:0!important;max-width:100%!important;max-height:100%!important;overflow:hidden!important;text-align:inherit!important;line-height:1.05!important;word-break:break-word!important;white-space:pre-wrap!important}
.editor-layer.is-button .editor-content{white-space:nowrap!important;text-overflow:clip!important}

/* Motion always begins on its saved anchor instead of beginning already displaced. */
@keyframes takeoverMarquee{0%,100%{transform:translateX(0) rotate(var(--rot,0deg))}50%{transform:translateX(3%) rotate(var(--rot,0deg))}}
@keyframes takeoverDrift{0%,100%{transform:translate(0,0) rotate(var(--rot,0deg))}50%{transform:translate(3%,2%) rotate(var(--rot,0deg))}}
@keyframes takeoverSweep{0%,100%{transform:translateX(0) rotate(var(--rot,0deg))}50%{transform:translateX(6%) rotate(var(--rot,0deg))}}
@keyframes takeoverOrbit{0%,100%{transform:translate(0,0) rotate(var(--rot,0deg))}25%{transform:translate(2%,-3%) rotate(calc(var(--rot,0deg) + 2deg))}50%{transform:translate(-2%,2%) rotate(var(--rot,0deg))}75%{transform:translate(2%,2%) rotate(calc(var(--rot,0deg) - 2deg))}}

/* Phone = closer camera on the same square board. No responsive stretching of creative geometry. */
@media(max-width:720px){
  html,body{overscroll-behavior:none!important}
  .board{--takeover-board-size:min(140vw,calc(100dvh - 104px))!important;overflow-x:auto!important;overflow-y:hidden!important;overscroll-behavior-x:contain!important;-webkit-overflow-scrolling:touch!important;scrollbar-width:none!important}
  .board::-webkit-scrollbar{display:none!important}
  .board>.grid-lines,.board>.territories,.board>.spot-actions,.board>.takeover-reveal-stage{left:0!important;right:auto!important;top:54px!important;bottom:auto!important;width:var(--takeover-board-size)!important;height:var(--takeover-board-size)!important;transform:none!important}
  .chrome{position:fixed!important;top:7px!important;left:7px!important;right:7px!important;z-index:40!important;align-items:flex-start!important;gap:5px!important}
  .identity{min-height:34px!important;padding:7px 10px!important;border-radius:11px!important;gap:0!important;flex:0 0 auto!important}
  .identity>b{font-size:14px!important}.identity>span,.social-pulse{display:none!important}
  .controls{max-width:calc(100vw - 108px)!important;gap:4px!important;flex-wrap:wrap!important}
  .chrome-btn{min-height:34px!important;padding:7px 8px!important;font-size:7px!important;line-height:1!important}
  .site-legal{position:fixed!important;left:0!important;right:0!important;bottom:0!important;z-index:40!important;height:42px!important;max-width:none!important;padding:5px 7px!important;background:rgba(247,247,243,.97)!important;border-top:1px solid #deded7!important}
  .territory .canvas-site{font-size:1.35cqw!important;left:1.8cqw!important;bottom:1.5cqw!important;opacity:.32!important}
  .available-cell{gap:4px!important}.available-cell span{font-size:6px!important}.available-cell b{font-size:8px!important}

  /* Visually tiny takeover control, but keep a forgiving touch target. */
  .take-pill{right:1px!important;bottom:1px!important;width:36px!important;height:36px!important;min-width:36px!important;min-height:36px!important;max-width:none!important;padding:0!important;border:0!important;background:transparent!important;box-shadow:none!important;backdrop-filter:none!important;font-size:0!important;display:grid!important;place-items:center!important;overflow:visible!important}
  .take-pill::after{content:attr(data-short);display:grid;place-items:center;min-width:24px;height:18px;padding:0 4px;border:1px solid rgba(0,0,0,.24);border-radius:999px;background:rgba(247,247,243,.94);color:#111;box-shadow:0 2px 8px rgba(0,0,0,.09);font:850 6px/1 'DM Mono',monospace;letter-spacing:0}
  .take-pill:hover,.take-pill:active{background:transparent!important;color:inherit!important;transform:none!important}
  .take-pill:hover::after,.take-pill:active::after{background:#111;color:#fff;border-color:#111}
}

@media(max-width:390px){
  .board{--takeover-board-size:min(145vw,calc(100dvh - 104px))!important}
  .chrome-btn{padding:7px 6px!important;font-size:6.5px!important}
}

@media(max-height:500px) and (pointer:coarse){
  .board{--takeover-board-size:min(100vw,calc(100dvh - 62px))!important;overflow-x:hidden!important}
  .board>.grid-lines,.board>.territories,.board>.spot-actions,.board>.takeover-reveal-stage{left:50%!important;top:46px!important;transform:translateX(-50%)!important}
  .site-legal{display:none!important}.identity{min-height:30px!important}.chrome-btn{min-height:30px!important}
}
'''

boot=boot.replace('takeover-v3.css?v=1.0','takeover-v3.css?v=1.0.1')
boot=boot.replace('takeover-v3.js?v=1.0','takeover-v3.js?v=1.0.1')
index=index.replace('boot.js?v=1.0','boot.js?v=1.0.1')

js_path.write_text(js)
css_path.write_text(css)
boot_path.write_text(boot)
index_path.write_text(index)
print('TAKEOVER V1.0.1 mobile-first camera patch applied')
