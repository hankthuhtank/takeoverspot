/* Owner console PNG export. No uploads, payment data, or social posting. */
(()=>{'use strict';
const SIZE=2048, OMIT='.take-pill,.inspect-spot,.territory-outline,.pending-territory,#takeoverRevealStage';
const $=s=>document.querySelector(s);
let active=false,generation=0,blob=null,objectUrl=null,filename='',options=null;
function release(){generation++;blob=null;if(objectUrl)URL.revokeObjectURL(objectUrl);objectUrl=null;const image=$('#snapshotImage');if(image){image.removeAttribute('src');image.hidden=true;}for(const id of ['snapshotCopy','snapshotDownload'])if($('#'+id))$('#'+id).disabled=true;}
function status(message){$('#snapshotStatus').textContent=message;}
function toDataURL(value){return new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(r.result);r.onerror=()=>reject(new Error('Could not prepare an image.'));r.readAsDataURL(value);});}
async function resource(url,signal){const r=await fetch(url,{signal,credentials:'omit'});if(!r.ok)throw new Error('An image or font could not load. Try again when your connection is stable.');return r;}
// Read all styles synchronously: polling and animation cannot mix two board states.
function frozenBoard(source){
  const copy=source.cloneNode(true), originals=[source,...source.querySelectorAll('*')],copies=[copy,...copy.querySelectorAll('*')];
  for(let i=0;i<originals.length;i++){
    const from=originals[i],to=copies[i];if(!to.style)continue;
    const style=getComputedStyle(from);
    for(const property of Array.from(style))to.style.setProperty(property,style.getPropertyValue(property),style.getPropertyPriority(property));
    to.style.setProperty('animation','none','important');to.style.setProperty('transition','none','important');
    to.removeAttribute('href');to.removeAttribute('tabindex');
  }
  copy.querySelectorAll(OMIT).forEach(el=>el.remove());
  copy.querySelectorAll('.available-cell').forEach(el=>{el.style.setProperty('background','transparent','important');el.style.setProperty('outline','none','important');el.style.setProperty('box-shadow','none','important');el.querySelector('b')?.style.setProperty('text-decoration','none','important');});
  // Combined territories use SVG masks outside the live board. Bring them along.
  const defs=$('#takeoverShapeDefs')?.cloneNode(true),prefix='snapshot-'+generation+'-';
  if(defs){defs.removeAttribute('id');defs.querySelectorAll('[id]').forEach(el=>el.id=prefix+el.id);copy.appendChild(defs);}
  for(const el of [copy,...copy.querySelectorAll('*')]){
    if(el.style){const clip=el.style.clipPath,match=clip?.match(/#([^"')]+)["']?\)/);if(match){
      const definition=document.getElementById(match[1]),rects=definition?.querySelectorAll('rect');
      if(definition?.getAttribute('clipPathUnits')==='objectBoundingBox'&&rects?.length){
        const width=parseFloat(el.style.width),height=parseFloat(el.style.height);
        // Self-contained paths survive SVG/foreignObject export without external IDs.
        const parts=[...rects].map(rect=>{const x=Number(rect.getAttribute('x'))*width,y=Number(rect.getAttribute('y'))*height,w=Number(rect.getAttribute('width'))*width,h=Number(rect.getAttribute('height'))*height;return `M ${x} ${y} h ${w} v ${h} h ${-w} Z`;});
        el.style.clipPath='path("'+parts.join(' ')+'")';
      }else el.style.clipPath='url(#'+prefix+match[1]+')';
    }}
    if(!el.closest('svg'))el.removeAttribute('id');
  }
  Object.assign(copy.style,{position:'relative',left:'0px',top:'0px',margin:'0px',transform:'none',boxShadow:'none'});
  return copy;
}
async function embedArtwork(root,signal){
  const cache=new Map();
  const embed=url=>{if(url.startsWith('data:'))return Promise.resolve(url);if(!cache.has(url))cache.set(url,resource(url,signal).then(r=>r.blob()).then(b=>{if(!b.type.startsWith('image/'))throw new Error('An artwork image could not be read.');return toDataURL(b);}));return cache.get(url);};
  for(const el of [root,...root.querySelectorAll('*')]){
    if(el.tagName==='IMG'){el.src=await embed(el.src);el.removeAttribute('srcset');await el.decode();}
    const bg=el.style?.backgroundImage;if(!bg||bg==='none')continue;
    let updated=bg;
    for(const match of bg.matchAll(/url\(["']?([^"')]+)["']?\)/g))updated=updated.replace(match[0],'url("'+await embed(match[1])+'")');
    el.style.backgroundImage=updated;
  }
}
async function embedFonts(root,signal){
  const families=new Set([...root.querySelectorAll('*')].map(el=>getComputedStyle(el).fontFamily.split(',')[0].replace(/["']/g,'').trim()));
  const link=document.querySelector('link[href^="https://fonts.googleapis.com/css2?"]');if(!link)return '';
  const css=await (await resource(link.href,signal)).text(),blocks=css.match(/@font-face\s*\{[^}]+\}/g)||[];
  const cache=new Map(),out=[];
  for(let rule of blocks){const family=rule.match(/font-family:\s*["']?([^;"']+)/)?.[1]?.trim();if(!families.has(family))continue;
    for(const match of rule.matchAll(/url\(([^)]+)\)/g)){const url=match[1].replace(/["']/g,'');if(!cache.has(url))cache.set(url,resource(url,signal).then(r=>r.blob()).then(toDataURL));rule=rule.replace(match[0],'url("'+await cache.get(url)+'")');}out.push(rule);
  }
  if(!out.length)throw new Error('Board fonts could not load. Please try again.');return out.join('\n');
}
function abortable(promise,signal){return new Promise((resolve,reject)=>{const abort=()=>reject(new DOMException('Timed out','AbortError'));if(signal.aborted)return abort();signal.addEventListener('abort',abort,{once:true});promise.then(resolve,reject).finally(()=>signal.removeEventListener('abort',abort));});}
async function capture(){
  if(active)return;active=true;release();const run=generation,button=$('#snapshotCreate');button.disabled=true;
  status('Checking owner access…');let holder=null;const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),45000);
  try{
    if(!await options.authorize())throw new Error('Sign in to your owner account to create a snapshot.');
    if(!await options.refresh())throw new Error('The board could not refresh. Try again before capturing.');
    if($('#boardSurface .pending-territory'))throw new Error('A purchase is still publishing. Wait for it to finish first.');
    await document.fonts.ready;
    if(run!==generation)return;
    status('Preparing the full board…');const source=$('#boardSurface'),size=source.getBoundingClientRect().width;
    if(size<1)throw new Error('The board is not ready. Refresh the page and try again.');
    const copy=frozenBoard(source);Object.assign(copy.style,{width:size+'px',height:size+'px'});
    holder=document.createElement('div');holder.setAttribute('aria-hidden','true');holder.inert=true;holder.style.cssText='position:fixed;left:-100000px;top:0;pointer-events:none';holder.appendChild(copy);document.body.appendChild(holder);
    const [,fontEmbedCSS]=await Promise.all([embedArtwork(copy,controller.signal),embedFonts(copy,controller.signal)]);
    if(run!==generation)return;
    const output=await abortable(window.htmlToImage.toBlob(copy,{width:size,height:size,canvasWidth:SIZE,canvasHeight:SIZE,pixelRatio:1,backgroundColor:'#f7f7f3',fontEmbedCSS,skipAutoScale:true}),controller.signal);
    if(!output?.size)throw new Error('Your browser could not create the image. Please try again.');
    const stillOwner=await options.authorize();if(run!==generation||!stillOwner)return;
    blob=output;objectUrl=URL.createObjectURL(blob);filename='takeover-board-'+new Date().toISOString().replace(/[:.]/g,'-')+'.png';
    const image=$('#snapshotImage');image.src=objectUrl;image.hidden=false;
    $('#snapshotDownload').disabled=false;$('#snapshotCopy').disabled=!(window.ClipboardItem&&navigator.clipboard?.write);
    status('Ready · 2048 × 2048 PNG · '+new Intl.DateTimeFormat('en-US',{timeZone:'America/Chicago',dateStyle:'medium',timeStyle:'short'}).format(new Date())+' CT. Copy the image or download it to post.');
  }catch(e){if(run===generation)status(e.name==='AbortError'?'Loading took too long. Check your connection and try again.':e.message||'Could not create the snapshot. Please try again.');}
  finally{clearTimeout(timer);controller.abort();holder?.remove();active=false;button.disabled=false;}
}
function mount(settings){
  options=settings;const create=$('#snapshotCreate');if(!create||create.dataset.wired)return;create.dataset.wired='true';create.onclick=capture;
  $('#snapshotCopy').onclick=async()=>{if(!blob)return;try{await navigator.clipboard.write([new ClipboardItem({'image/png':blob})]);status('Image copied. Paste it into your social post.');}catch{status('This browser could not copy the image. Use Download PNG, then attach it to your post.');}};
  $('#snapshotDownload').onclick=()=>{if(!objectUrl)return;const a=document.createElement('a');a.href=objectUrl;a.download=filename;document.body.appendChild(a);a.click();a.remove();};
}
async function exportSavedBoard(){
  if(document.documentElement.dataset.snapshotRender!=='true')throw new Error('Saved-board renderer required');
  await document.fonts.ready;
  const source=$('#boardSurface');
  await Promise.all([...source.querySelectorAll('img')].map(image=>image.decode()));
  for(const animation of source.getAnimations({subtree:true})){animation.pause();animation.currentTime=1500;}
  const copy=frozenBoard(source),controller=new AbortController();
  const timer=setTimeout(()=>controller.abort(),40000);
  Object.assign(copy.style,{width:'1600px',height:'1600px',position:'fixed',left:'-100000px'});
  copy.style.setProperty('display','block','important');
  document.body.appendChild(copy);
  try{
    const [,fontEmbedCSS]=await Promise.all([embedArtwork(copy,controller.signal),embedFonts(copy,controller.signal)]);
    return await abortable(window.htmlToImage.toBlob(copy,{width:1600,height:1600,canvasWidth:1600,canvasHeight:1600,pixelRatio:1,backgroundColor:'#f7f7f3',fontEmbedCSS,skipAutoScale:true,style:{position:'relative',left:'0px'}}),controller.signal);
  }finally{clearTimeout(timer);controller.abort();copy.remove();}
}
window.TakeoverSnapshot={mount,release,exportSavedBoard};
})();
