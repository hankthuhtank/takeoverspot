from pathlib import Path
p=Path('takeover-v3.js')
s=p.read_text()

def must(old,new):
    global s
    if old not in s: raise SystemExit('missing: '+old[:120])
    s=s.replace(old,new,1)

must("const TOTAL=16,COLS=4,ROWS=4,CENTER=[6,7,10,11];","const TOTAL=16,COLS=4,ROWS=4;")
must("function isCenterSelection(arr){return arr.length===4&&CENTER.every(n=>arr.includes(n))}\n","")
must("function safeImg(src){const s=String(src||'');if(s.startsWith(`${SUPA_URL}/storage/v1/object/public/takeover-creative/`)||s.startsWith(`${SUPA_URL}/storage/v1/object/public/takeover-logos/`))return s;if(s.startsWith(LOCAL_ASSET_PREFIX))return localAssetUrls.get(s)||'';return''}\n",
"function normalizeImgRef(src){const s=String(src||'');if(s.startsWith(`${SUPA_URL}/storage/v1/object/public/takeover-creative/`)||s.startsWith(`${SUPA_URL}/storage/v1/object/public/takeover-logos/`)||s.startsWith(LOCAL_ASSET_PREFIX))return s;return''}\nfunction safeImg(src){const s=normalizeImgRef(src);if(s.startsWith(LOCAL_ASSET_PREFIX))return localAssetUrls.get(s)||'';return s}\n")
must("c.bg.image=safeImg(c.bg.image);","c.bg.image=normalizeImgRef(c.bg.image);")
must("src:safeImg(l.src),","src:normalizeImgRef(l.src),")
must("g.className='grid-cell'+(CENTER.includes(n)?' center-cell':'');","g.className='grid-cell';")
must("b.className='available-cell'+(CENTER.includes(n)?' center-cell':'');","b.className='available-cell';")
must("b.className='mini-spot'+(sel?' selected':'')+(self?' own':'')+(CENTER.includes(n)?' center-selected':'');","b.className='mini-spot'+(sel?' selected':'')+(self?' own':'');")

# Make sure the anonymous ref survives normalization before it is uploaded after sign-in.
if "c.bg.image=normalizeImgRef(c.bg.image)" not in s or "src:normalizeImgRef(l.src)" not in s:
    raise SystemExit('local asset preservation missing')
if 'CENTER=' in s or 'isCenterSelection' in s or 'CENTER.includes' in s:
    raise SystemExit('center special case remains')
p.write_text(s)
print('final canvas integrity fixes applied')
