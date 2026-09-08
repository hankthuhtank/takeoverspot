(()=>{'use strict';
const $=s=>document.querySelector(s),BASE='https://xvfgiaxxvwdnmzzdfboc.supabase.co/storage/v1/object/public/takeover-daily-snapshots/';
let client,offset=0,busy=false,sequence=0,selected=null,png=null,url=null;
function dateLabel(date){return new Intl.DateTimeFormat('en-US',{dateStyle:'long',timeZone:'UTC'}).format(new Date(date+'T12:00:00Z'));}
function imageUrl(row){return /^\d{4}-\d{2}-\d{2}\.jpg$/.test(row.image_path||'')?BASE+row.image_path:null;}
function clear(){sequence++;selected=null;png=null;if(url)URL.revokeObjectURL(url);url=null;$('#dailyCopy').disabled=true;$('#dailyDownload').disabled=true;$('#dailyFullImage').removeAttribute('src');$('#dailyDetail').hidden=true;}
async function show(row){
  clear();selected=row;const run=sequence;$('#dailyDetail').hidden=false;$('#dailyTitle').textContent=dateLabel(row.snapshot_date);$('#dailyDetailStatus').textContent='Preparing image…';
  const image=$('#dailyFullImage');image.crossOrigin='anonymous';image.src=imageUrl(row);image.alt='TAKEOVER board on '+dateLabel(row.snapshot_date);
  try{await image.decode();if(run!==sequence)return;const canvas=document.createElement('canvas');canvas.width=image.naturalWidth;canvas.height=image.naturalHeight;canvas.getContext('2d').drawImage(image,0,0);const blob=await new Promise(r=>canvas.toBlob(r,'image/png'));if(!blob)throw Error('Could not prepare PNG');if(run!==sequence)return;png=blob;url=URL.createObjectURL(blob);$('#dailyDownload').disabled=false;$('#dailyCopy').disabled=!(window.ClipboardItem&&navigator.clipboard?.write);$('#dailyDetailStatus').textContent='Captured '+new Intl.DateTimeFormat('en-US',{timeZone:'America/Chicago',timeStyle:'short'}).format(new Date(row.captured_at))+' Central';}
  catch{if(run===sequence)$('#dailyDetailStatus').textContent='Image could not load. Select the date again to retry.';}
  $('#dailyDetail').scrollIntoView?.({behavior:'smooth',block:'nearest'});
}
async function load(reset=false){
  if(busy)return;busy=true;const list=$('#dailyList'),more=$('#dailyMore');more.disabled=true;
  if(reset){offset=0;list.replaceChildren();clear();}$('#dailyStatus').textContent='Loading snapshots…';
  try{const {data,error}=await client.from('takeover_daily_snapshots').select('snapshot_date,captured_at,image_path,image_bytes').order('snapshot_date',{ascending:false}).range(offset,offset+11);if(error)throw error;
    for(const row of data||[]){const button=document.createElement('button');button.className='daily-card';const src=imageUrl(row);const picture=document.createElement(src?'img':'span');
      if(src){picture.src=src;picture.alt='Board on '+dateLabel(row.snapshot_date);picture.loading='lazy';button.onclick=()=>show(row);}else{picture.className='daily-pending';picture.textContent='Image processing';button.disabled=true;}
      const date=document.createElement('b');date.textContent=dateLabel(row.snapshot_date);const time=document.createElement('small');time.textContent=src?'12 PM CENTRAL':'Board saved · image preparing';button.append(picture,date,time);list.appendChild(button);
    }
    offset+=(data||[]).length;more.hidden=(data||[]).length<12;
    $('#dailyStatus').textContent=offset?'One board. One day. Saved at noon Central.':'The first daily snapshot will appear after the next noon Central capture.';
  }catch{$('#dailyStatus').textContent='Snapshots could not load. Tap Refresh to retry.';}finally{busy=false;more.disabled=false;}
}
function mount(sb){client=sb;if(!$('#boardSnapshots')||$('#boardSnapshots').dataset.wired)return;$('#boardSnapshots').dataset.wired='true';
  $('#boardSnapshots').onclick=()=>{window.TakeoverBoard?.showArchive(true);load(true);};
  $('#dailyRefresh').onclick=()=>load(true);$('#dailyMore').onclick=()=>load();$('#dailyClose').onclick=clear;
  $('#dailyCopy').onclick=async()=>{if(!png)return;try{await navigator.clipboard.write([new ClipboardItem({'image/png':png})]);$('#dailyDetailStatus').textContent='Copied. Paste into your social post.';}catch{$('#dailyDetailStatus').textContent='Copy is unavailable in this browser. Use Download PNG.';}};
  $('#dailyDownload').onclick=()=>{if(!url||!selected)return;const a=document.createElement('a');a.href=url;a.download='takeover-'+selected.snapshot_date+'.png';document.body.appendChild(a);a.click();a.remove();};
}
window.TakeoverDailySnapshots={mount,clear};
})();
