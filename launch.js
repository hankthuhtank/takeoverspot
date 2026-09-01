(()=>{'use strict';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const esc=s=>String(s??'').replace(/[&<>'\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','\"':'&quot;'}[c]));
const cash=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(Number(n||0));
function toast(msg){const t=$('#toast');if(!t)return;t.textContent=msg;t.classList.add('on');setTimeout(()=>t.classList.remove('on'),3000)}

/* Purchase assent. */
function installTermsConsent(){
  if($('#termsConsent')||!$('#checkoutBtn'))return;
  const box=document.createElement('div');box.className='terms-consent';box.id='termsConsent';
  box.innerHTML='<label><input id="termsAgree" type="checkbox"><span><strong>I agree to the purchase terms.</strong> By paying, I agree to the <a href="terms.html" target="_blank" rel="noopener">Terms</a>, <a href="payments.html" target="_blank" rel="noopener">Payments Policy</a>, and <a href="auction-rules.html" target="_blank" rel="noopener">Rules</a>, including that placement duration, site uptime, continued operation, traffic, and results are not guaranteed.</span></label>';
  $('#checkoutBtn').before(box);
}
installTermsConsent();
document.addEventListener('click',e=>{
  const checkout=e.target.closest?.('#checkoutBtn');if(!checkout)return;
  const agree=$('#termsAgree'),box=$('#termsConsent');if(agree?.checked)return;
  e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();box?.classList.add('attention');setTimeout(()=>box?.classList.remove('attention'),1200);toast('Agree to the purchase terms to continue');
},true);

/* Static social treatment: these elements are written once, not continuously rewritten. */
function installSocialLinks(){
  const pulse=$('.social-pulse');if(!pulse)return;
  pulse.innerHTML='<i aria-hidden="true"></i><strong>4-HOUR SOCIAL SNAPSHOTS</strong><span class="social-links"><a href="https://x.com/takeoverspot" target="_blank" rel="noopener">X</a><span aria-hidden="true">·</span><a href="https://www.instagram.com/takeover.spot" target="_blank" rel="noopener">INSTAGRAM</a></span>';
}
installSocialLinks();

/* Purchase drafts are one-time auth handoffs, never permanent UI state. */
const DRAFT_KEY='takeover_purchase_draft',DRAFT_TTL=30*60*1000;
function getDraft(){try{return JSON.parse(localStorage.getItem(DRAFT_KEY)||'null')}catch{return null}}
function clearDraft(){try{localStorage.removeItem(DRAFT_KEY)}catch{}}
function sanitizeLegacyDraft(){const d=getDraft();if(!d)return;if(!Number(d._savedAt)||Date.now()-Number(d._savedAt)>DRAFT_TTL)clearDraft()}
function stampFreshDraft(){const d=getDraft();if(!d)return;d._savedAt=Date.now();try{localStorage.setItem(DRAFT_KEY,JSON.stringify(d))}catch{}}
function consumeRestoredDraft(){const d=getDraft();if(!d||!Number(d._savedAt))return;const signed=/MY SPOTS/i.test($('#accountBtn')?.textContent||''),open=$('#takeoverModal')?.classList.contains('on');if(signed&&open)clearDraft()}
sanitizeLegacyDraft();
document.addEventListener('click',e=>{if(e.target.closest?.('#sendMagicLink'))setTimeout(stampFreshDraft,0)},true);
[700,1400,2600].forEach(ms=>setTimeout(consumeRestoredDraft,ms));
document.addEventListener('click',e=>{if(!$('#takeoverModal')?.classList.contains('on'))return;if(e.target.closest?.('#takeoverModal [data-close]')||e.target.id==='scrim')clearDraft()},true);

/*
  One source of truth for the page-control button: the 12 rendered cell actions.
  The core app rebuilds #spotActions after every board refresh. We observe only that
  container, then update a different element, so this cannot recursively observe itself.
*/
function amountFrom(text){const m=String(text||'').match(/\$([\d,]+)/);return m?Number(m[1].replace(/,/g,'')):0}
function syncPageControl(){
  const wrap=$('#spotActions'),page=$('#takePageBtn');if(!wrap||!page)return;
  const buttons=$$('#spotActions .spot-action button');if(buttons.length!==12)return;
  let owned=0,total=0,protectedState=false;
  for(const btn of buttons){const text=(btn.textContent||'').trim().toUpperCase();if(text.startsWith('DEFEND'))owned++;else if(text.includes('PROTECTED'))protectedState=true;else if(text.startsWith('TAKE'))total+=amountFrom(text)}
  const paused=$('#pauseFlag')&&!$('#pauseFlag').hidden;
  if(owned===12){
    page.textContent='YOU OWN THE PAGE · MANAGE';page.dataset.pageManage='1';page.disabled=false;page.title='Open My Spots';page.classList.add('owned-page-control');return;
  }
  page.dataset.pageManage='0';page.classList.remove('owned-page-control');page.title='';
  if(protectedState){page.textContent='PAGE TAKEOVER PROTECTED';page.disabled=true;return}
  page.textContent=`TAKE THE PAGE · ${cash(total)}`;page.disabled=paused||total<=0;
}
const spotActions=$('#spotActions');if(spotActions)new MutationObserver(syncPageControl).observe(spotActions,{childList:true,subtree:true});setTimeout(syncPageControl,900);
document.addEventListener('click',e=>{const b=e.target.closest?.('#takePageBtn');if(!b||b.dataset.pageManage!=='1')return;e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();$('#accountBtn')?.click()},true);

/* Admin always shows all 12 cells, even when the board is empty. */
async function renderAllAdminSpots(){
  const target=$('#adminBoard'),sb=window.takeoverSb;if(!target||!sb||!$('#adminPanel')?.classList.contains('on'))return;
  const [{data:rows},{data:cfg}]=await Promise.all([sb.from('takeover_spots').select('spot_number,current_price,owner_key,company_name,website').order('spot_number'),sb.from('takeover_config').select('starting_price').eq('singleton',true).maybeSingle()]);
  const map=new Map((rows||[]).map(r=>[Number(r.spot_number),r])),start=Number(cfg?.starting_price||10);
  target.innerHTML=Array.from({length:12},(_,i)=>{const n=i+1,s=map.get(n)||{spot_number:n,current_price:0,owner_key:null,company_name:null,website:null};const occupied=!!s.owner_key,price=Number(s.current_price)>0?Number(s.current_price):start;let site='No owner';try{site=s.website?new URL(/^https?:\/\//i.test(s.website)?s.website:'https://'+s.website).hostname.replace(/^www\./,''):'No owner'}catch{}return `<div class="admin-row"><span>${String(n).padStart(2,'0')}</span><div><b>${esc(s.company_name||'AVAILABLE')} · ${cash(price)}</b><small>${esc(site)}</small></div><button class="tiny danger" data-moderation-reset="${n}" ${occupied?'':'disabled'}>${occupied?'RESET':'AVAILABLE'}</button></div>`}).join('');
}
document.addEventListener('click',e=>{if(e.target.closest?.('#adminBtn'))setTimeout(renderAllAdminSpots,180)},true);
})();
