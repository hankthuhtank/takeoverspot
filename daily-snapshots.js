(()=>{'use strict';
const $=s=>document.querySelector(s),BASE='https://xvfgiaxxvwdnmzzdfboc.supabase.co/storage/v1/object/public/takeover-daily-snapshots/';
let adminDate=null,adminBusy=false,adminUrl=null;
let client,offset=0,busy=false,sequence=0,selected=null,png=null,url=null;
function dateLabel(date){return new Intl.DateTimeFormat('en-US',{dateStyle:'long',timeZone:'UTC'}).format(new Date(date+'T12:00:00Z'));}
function imageUrl(row){return /^\d{4}-\d{2}-\d{2}\.jpg$/.test(row.image_path||'')?BASE+row.image_path:null;}
async function savedPNG(row){
  // Old captures include a hover artifact; rebuild those from their original data.
  if(imageUrl(row)&&row.snapshot_date>'2026-09-11'){
    const image=new Image();image.crossOrigin='anonymous';image.src=imageUrl(row);await image.decode();
    const canvas=document.createElement('canvas');canvas.width=image.naturalWidth;canvas.height=image.naturalHeight;canvas.getContext('2d').drawImage(image,0,0);
    return new Promise(resolve=>canvas.toBlob(resolve,'image/png'));
  }
  const {data,error}=await client.from('takeover_daily_snapshots').select('snapshot_date,captured_at,board_json,config_json').eq('snapshot_date',row.snapshot_date).single();
  if(error||!data)throw Error('Saved board could not load');
  const frame=document.createElement('iframe');frame.title='Saved daily board renderer';frame.setAttribute('aria-hidden','true');frame.tabIndex=-1;
  frame.style.cssText='position:fixed;left:-100000px;top:0;width:1600px;height:1600px;border:0;pointer-events:none';
  let timeout;
  try{return await Promise.race([new Promise((_,reject)=>{timeout=setTimeout(()=>reject(Error('Snapshot preparation timed out. Try again.')),45000);}),new Promise((resolve,reject)=>{
    frame.onload=async()=>{try{const w=frame.contentWindow;if(!w.TakeoverArchiveRender)throw Error('Renderer unavailable');w.TakeoverArchiveRender.render(data);const blob=await w.TakeoverSnapshot.exportSavedBoard();if(!blob?.size)throw Error('Image export failed');resolve(blob);}catch(error){reject(error);}};
    frame.onerror=()=>reject(Error('Renderer could not load'));frame.src='snapshot-render.html?v=noon-2';document.body.appendChild(frame);
  })]);}finally{clearTimeout(timeout);frame.remove();}
}
async function refreshAdmin(){
  if(adminBusy||document.hidden||!$('#adminPanel')?.classList.contains('on'))return;
  adminBusy=true;const status=$('#dailyAdminStatus');
  try{
    const today=new Intl.DateTimeFormat('en-CA',{timeZone:'America/Chicago',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
    if(adminDate===today)return;
    const {data,error}=await client.from('takeover_daily_snapshots').select('snapshot_date,captured_at,image_path').eq('snapshot_date',today).maybeSingle();
    if(error)throw error;
    if(!data){if(adminUrl){URL.revokeObjectURL(adminUrl);adminUrl=null;adminDate=null;$('#dailyAdminImage').hidden=true;$('#dailyAdminCopy').disabled=true;$('#dailyAdminDownload').disabled=true;}status.textContent='Waiting for today’s noon Central capture. Updates automatically.';return;}
    status.textContent='Noon board saved. Preparing your image…';
    const blob=await savedPNG(data);if(adminUrl)URL.revokeObjectURL(adminUrl);adminUrl=URL.createObjectURL(blob);adminDate=today;
    $('#dailyAdminImage').src=adminUrl;$('#dailyAdminImage').hidden=false;
    $('#dailyAdminDownload').disabled=false;$('#dailyAdminDownload').onclick=()=>{const a=document.createElement('a');a.href=adminUrl;a.download='takeover-'+today+'.png';a.click();};
    $('#dailyAdminCopy').disabled=!(window.ClipboardItem&&navigator.clipboard?.write);$('#dailyAdminCopy').onclick=async()=>{try{await navigator.clipboard.write([new ClipboardItem({'image/png':blob})]);status.textContent='Copied. Ready to post.';}catch{status.textContent='Use Download PNG in this browser.';}};
    status.textContent=dateLabel(today)+' · Noon Central · Ready to post';
  }catch{status.textContent='Could not prepare today’s snapshot. Retrying automatically.';}finally{adminBusy=false;}
}
function clear(){sequence++;selected=null;png=null;if(url)URL.revokeObjectURL(url);url=null;$('#dailyCopy').disabled=true;$('#dailyDownload').disabled=true;$('#dailyFullImage').removeAttribute('src');$('#dailyDetail').hidden=true;}
async function show(row){
  clear();selected=row;const run=sequence;$('#dailyDetail').hidden=false;$('#dailyTitle').textContent=dateLabel(row.snapshot_date);$('#dailyDetailStatus').textContent='Preparing image…';
  try{const blob=await savedPNG(row);if(run!==sequence)return;png=blob;url=URL.createObjectURL(blob);const image=$('#dailyFullImage');image.src=url;image.alt='TAKEOVER board on '+dateLabel(row.snapshot_date);$('#dailyDownload').disabled=false;$('#dailyCopy').disabled=!(window.ClipboardItem&&navigator.clipboard?.write);$('#dailyDetailStatus').textContent='Captured '+new Intl.DateTimeFormat('en-US',{timeZone:'America/Chicago',timeStyle:'short'}).format(new Date(row.captured_at))+' Central';}
  catch{if(run===sequence)$('#dailyDetailStatus').textContent='Image could not load. Select the date again to retry.';}
  $('#dailyDetail').scrollIntoView?.({behavior:'smooth',block:'nearest'});
}
async function load(reset=false){
  if(busy)return;busy=true;const list=$('#dailyList'),more=$('#dailyMore');more.disabled=true;
  if(reset){offset=0;list.replaceChildren();clear();}$('#dailyStatus').textContent='Loading snapshots…';
  try{const {data,error}=await client.from('takeover_daily_snapshots').select('snapshot_date,captured_at,image_path,image_bytes').order('snapshot_date',{ascending:false}).range(offset,offset+11);if(error)throw error;
    for(const row of data||[]){const button=document.createElement('button');button.className='daily-card';const src=row.snapshot_date>'2026-09-11'?imageUrl(row):null;const picture=document.createElement(src?'img':'span');
      if(src){picture.src=src;picture.alt='Board on '+dateLabel(row.snapshot_date);picture.loading='lazy';button.onclick=()=>show(row);}else{picture.className='daily-pending';picture.textContent='VIEW NOON BOARD';}
      button.onclick=()=>show(row);
      const date=document.createElement('b');date.textContent=dateLabel(row.snapshot_date);const time=document.createElement('small');time.textContent=src?'12 PM CENTRAL':'Ready to view / download';button.append(picture,date,time);list.appendChild(button);
    }
    offset+=(data||[]).length;more.hidden=(data||[]).length<12;
    $('#dailyStatus').textContent=offset?'One board. One day. Saved at noon Central.':'The first daily snapshot will appear after the next noon Central capture.';
  }catch{$('#dailyStatus').textContent='Snapshots could not load. Tap Refresh to retry.';}finally{busy=false;more.disabled=false;}
}
function mount(sb){client=sb;if(!$('#boardSnapshots')||$('#boardSnapshots').dataset.wired)return;$('#boardSnapshots').dataset.wired='true';
  const admin=$('#dailyAdminStatus');if(admin){new MutationObserver(refreshAdmin).observe($('#adminPanel'),{attributes:true,attributeFilter:['class']});setInterval(refreshAdmin,10000);document.addEventListener('visibilitychange',refreshAdmin);}
  $('#boardSnapshots').onclick=()=>{window.TakeoverBoard?.showArchive(true);load(true);};
  $('#dailyRefresh').onclick=()=>load(true);$('#dailyMore').onclick=()=>load();$('#dailyClose').onclick=clear;
  $('#dailyCopy').onclick=async()=>{if(!png)return;try{await navigator.clipboard.write([new ClipboardItem({'image/png':png})]);$('#dailyDetailStatus').textContent='Copied. Paste into your social post.';}catch{$('#dailyDetailStatus').textContent='Copy is unavailable in this browser. Use Download PNG.';}};
  $('#dailyDownload').onclick=()=>{if(!url||!selected)return;const a=document.createElement('a');a.href=url;a.download='takeover-'+selected.snapshot_date+'.png';document.body.appendChild(a);a.click();a.remove();};
}
window.TakeoverDailySnapshots={mount,clear,savedPNG};
})();
