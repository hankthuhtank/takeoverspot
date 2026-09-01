(()=>{'use strict';
const PROJECT_URL='https://xvfgiaxxvwdnmzzdfboc.supabase.co';
const PROJECT_KEY='sb_publishable_ShdZijibR7b6EvowZ1yN9Q_dIkGmcCZ';
const initialQuery=new URLSearchParams(location.search);
const initialTakeover=initialQuery.get('takeover');
const initialAttempt=initialQuery.get('attempt');
let sb=null,moderationSpot=null;

/* Make both TAKEOVER scripts share one auth client instead of opening competing clients. */
if(window.supabase?.createClient){
  const original=window.supabase.createClient.bind(window.supabase);
  sb=original(PROJECT_URL,PROJECT_KEY,{auth:{storageKey:'takeover-auth-v1',persistSession:true,autoRefreshToken:true,detectSessionInUrl:true}});
  const wrapped=(url,key,options={})=>url===PROJECT_URL?sb:original(url,key,options);
  window.supabase.createClient=wrapped;
  window.takeoverSb=sb;
}

const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const esc=s=>String(s??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
function toast(msg){const t=$('#toast');if(!t)return;t.textContent=msg;t.classList.add('on');setTimeout(()=>t.classList.remove('on'),3000)}
function openModerationPanel(){const p=$('#moderationModal'),scrim=$('#scrim');if(!p||!scrim)return;scrim.classList.add('on');p.classList.add('on')}
function closeModerationPanel(){const p=$('#moderationModal');if(p)p.classList.remove('on');if(!$$('.panel.on').length)$('#scrim')?.classList.remove('on')}
function reasonLabel(reason){return({fraud_or_scam:'Fraud or scam',malware_or_phishing:'Malware / phishing',illegal_or_dangerous:'Illegal / clearly dangerous',impersonation_or_rights:'Impersonation / serious rights abuse',credible_safety_or_legal_risk:'Credible safety / legal risk',other_extreme_issue:'Other extreme issue'})[reason]||'Moderation reset'}

async function openReset(n){
  moderationSpot=Number(n);
  const title=$('#moderationTitle'),reason=$('#moderationReason'),note=$('#moderationNote');
  if(title)title.textContent=`Reset Spot ${String(moderationSpot).padStart(2,'0')}?`;
  if(reason)reason.value='';if(note)note.value='';openModerationPanel();
}

async function confirmReset(){
  if(!sb||!moderationSpot)return;
  const reason=$('#moderationReason')?.value||'',note=$('#moderationNote')?.value.trim()||'';
  if(!reason)return toast('Choose a reset reason');
  if(reason==='other_extreme_issue'&&!note)return toast('Add a short private note for Other');
  const btn=$('#confirmResetSpot'),old=btn?.textContent||'RESET SPOT TO AVAILABLE';
  if(btn){btn.disabled=true;btn.textContent='RESETTING…'}
  const {error}=await sb.rpc('admin_reset_takeover_spot',{p_spot_number:moderationSpot,p_reason:reason,p_note:note||null});
  if(btn){btn.disabled=false;btn.textContent=old}
  if(error)return toast(error.message||'Could not reset spot');
  toast(`Spot ${moderationSpot} reset to available`);moderationSpot=null;closeModerationPanel();
  setTimeout(()=>location.reload(),650);
}

async function renderModerationHistory(){
  if(!sb||!$('#adminModeration'))return;
  const {data,error}=await sb.from('takeover_moderation_log').select('spot_number,previous_company_name,reason,note,created_at').order('created_at',{ascending:false}).limit(15);
  if(error){$('#adminModeration').innerHTML='<div class="empty">Moderation history unavailable.</div>';return}
  const rows=data||[];
  $('#adminModeration').innerHTML=rows.length?rows.map(m=>`<div class="admin-row moderation-row"><span>${String(m.spot_number).padStart(2,'0')}</span><div><b>${esc(m.previous_company_name||'Unknown advertiser')}</b><small>${esc(reasonLabel(m.reason))} · ${new Date(m.created_at).toLocaleString()}</small>${m.note?`<p>${esc(m.note)}</p>`:''}</div></div>`).join(''):'<div class="empty">No moderation resets. Good.</div>';
}

/* No MutationObserver here. Admin rows are rendered explicitly by launch.js. */
document.addEventListener('click',e=>{
  const reset=e.target.closest?.('[data-moderation-reset]');
  if(reset){e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();openReset(reset.dataset.moderationReset);return}
  if(e.target.closest?.('#adminBtn'))setTimeout(renderModerationHistory,240);
},true);

$('#confirmResetSpot')?.addEventListener('click',confirmReset);
$('#moderationCancel')?.addEventListener('click',()=>{moderationSpot=null;closeModerationPanel()});

/* Capture what occupied the cells before Stripe so the successful buyer sees it erased. */
function selectedSpotNumbers(){return $$('#miniGrid .mini-spot').map((b,i)=>b.classList.contains('selected')?i+1:null).filter(Boolean)}
function snapshotCell(n){
  const board=$('#board');if(!board)return{spot_number:n,name:'AVAILABLE',image:null};
  const br=board.getBoundingClientRect(),cols=4,rows=3,c=(n-1)%cols,r=Math.floor((n-1)/cols),x=br.left+(c+.5)*br.width/cols,y=br.top+(r+.5)*br.height/rows;
  const territory=$$('.territory').find(t=>{const z=t.getBoundingClientRect();return x>=z.left&&x<=z.right&&y>=z.top&&y<=z.bottom});
  if(!territory)return{spot_number:n,name:'AVAILABLE',image:null};
  const image=territory.querySelector('.compact-logo,.creative-logo,.media-logo,.feature-photo,img')?.src||null;
  const name=territory.querySelector('.creative-name,.wordmark,.media-wordmark')?.textContent?.trim()||territory.querySelector('.site')?.textContent?.trim()||'CURRENT OWNER';
  return{spot_number:n,name:name.slice(0,80),image};
}
function saveRevealDraft(){
  const kicker=$('#takeoverKicker')?.textContent||'';if(/DEFEND/i.test(kicker))return;
  const nums=selectedSpotNumbers();if(!nums.length)return;
  try{localStorage.setItem('takeover_polish_reveal_v1',JSON.stringify({targets:nums.map(snapshotCell),at:Date.now()}))}catch{}
}
$('#checkoutBtn')?.addEventListener('click',saveRevealDraft,true);

function clearReveal(){try{localStorage.removeItem('takeover_polish_reveal_v1')}catch{}}
function revealData(){try{return JSON.parse(localStorage.getItem('takeover_polish_reveal_v1')||'null')}catch{return null}}
function playReveal(){
  const data=revealData(),stage=$('#takeoverRevealStage');
  if(!data||!stage||!Array.isArray(data.targets)||!data.targets.length){clearReveal();return}
  if(Date.now()-Number(data.at||0)>3600000){clearReveal();return}
  stage.innerHTML='';
  data.targets.forEach((item,i)=>{
    const n=Number(item.spot_number),r=Math.floor((n-1)/4),c=(n-1)%4,card=document.createElement('div');
    card.className='takeover-reveal-card';card.style.left=(c*25)+'%';card.style.top=(r/3*100)+'%';card.style.width='25%';card.style.height=(100/3)+'%';card.style.setProperty('--reveal-delay',(i*90)+'ms');
    const old=item.image?`<img src="${esc(item.image)}" alt="">`:`<div class="wipe-wordmark">${esc(item.name||'AVAILABLE')}</div>`;
    card.innerHTML=`<div class="wipe-old">${old}<small>SPOT ${String(n).padStart(2,'0')}</small></div><div class="eraser-sweep"><i></i></div><div class="take-stamp">TAKEN</div>`;stage.appendChild(card);
  });
  stage.hidden=false;requestAnimationFrame(()=>requestAnimationFrame(()=>stage.classList.add('run')));
  setTimeout(()=>{stage.classList.remove('run');stage.hidden=true;stage.innerHTML='';clearReveal()},2600);
}

async function waitForSuccessfulTakeover(){
  if(initialTakeover==='cancel'){clearReveal();return}
  if(initialTakeover!=='success'||!initialAttempt||!sb)return;
  for(let i=0;i<20;i++){
    const {data}=await sb.from('takeover_attempts').select('status').eq('id',initialAttempt).maybeSingle();
    if(data?.status==='won'){setTimeout(playReveal,850);return}
    if(['refunded','refund_failed','failed','cancelled'].includes(data?.status)){clearReveal();return}
    await new Promise(r=>setTimeout(r,700));
  }
}
setTimeout(waitForSuccessfulTakeover,150);
})();
