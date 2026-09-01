(()=>{'use strict';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const esc=s=>String(s??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
const cash=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(Number(n||0));
function toast(msg){const t=$('#toast');if(!t)return;t.textContent=msg;t.classList.add('on');setTimeout(()=>t.classList.remove('on'),3000)}

function installTermsConsent(){
  if($('#termsConsent')||!$('#checkoutBtn'))return;
  const box=document.createElement('div');
  box.className='terms-consent';
  box.id='termsConsent';
  box.innerHTML='<label><input id="termsAgree" type="checkbox"><span><strong>I agree to the purchase terms.</strong> By paying, I agree to the <a href="terms.html" target="_blank" rel="noopener">Terms</a>, <a href="payments.html" target="_blank" rel="noopener">Payments Policy</a>, and <a href="auction-rules.html" target="_blank" rel="noopener">Rules</a>, including that placement duration, site uptime, continued operation, traffic, and results are not guaranteed.</span></label>';
  $('#checkoutBtn').before(box);
}
installTermsConsent();
new MutationObserver(installTermsConsent).observe(document.body,{childList:true,subtree:true});
document.addEventListener('click',e=>{
  const checkout=e.target.closest?.('#checkoutBtn');
  if(!checkout)return;
  const agree=$('#termsAgree'),box=$('#termsConsent');
  if(agree?.checked)return;
  e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();
  box?.classList.add('attention');setTimeout(()=>box?.classList.remove('attention'),1200);
  toast('Agree to the purchase terms to continue');
},true);

/* Public social links — no private owner identity is exposed. */
function installSocialLinks(){
  const pulse=$('.social-pulse');if(!pulse||pulse.dataset.linked==='1')return;
  pulse.dataset.linked='1';
  pulse.innerHTML='<i></i><strong>4-HOUR SOCIAL SNAPSHOTS</strong><span class="social-links"><a href="https://x.com/takeoverspot" target="_blank" rel="noopener">X @takeoverspot</a><a href="https://www.instagram.com/takeover.spot/" target="_blank" rel="noopener">IG @takeover.spot</a></span>';
}
installSocialLinks();

/* If the signed-in advertiser owns all 12 spots, the top-right status opens My Spots. */
function normalizeOwnedPageButton(){
  const b=$('#takePageBtn');if(!b)return;
  const text=(b.textContent||'').trim();
  const owned=/^YOU OWN THE PAGE(?:\b| ·)/.test(text)||/^PAGE PROTECTED ·/.test(text);
  b.classList.toggle('owned-page-control',owned);
  if(owned){
    b.disabled=false;
    b.title='Open My Spots';
    if(text==='YOU OWN THE PAGE')b.textContent='YOU OWN THE PAGE · MANAGE';
  }else if(!/^TAKE THE PAGE/.test(text)){
    b.title='';
  }
}
const pageBtn=$('#takePageBtn');
if(pageBtn){new MutationObserver(normalizeOwnedPageButton).observe(pageBtn,{attributes:true,childList:true,subtree:true});normalizeOwnedPageButton()}
document.addEventListener('click',e=>{
  const b=e.target.closest?.('#takePageBtn.owned-page-control');if(!b)return;
  e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();
  $('#accountBtn')?.click();
},true);

/* Admin always shows all 12 cells, even when the board is completely empty. */
async function renderAllAdminSpots(){
  const target=$('#adminBoard'),sb=window.takeoverSb;if(!target||!sb||!$('#adminPanel')?.classList.contains('on'))return;
  const [{data:rows},{data:cfg}]=await Promise.all([
    sb.from('takeover_spots').select('spot_number,current_price,owner_key,company_name,website').order('spot_number'),
    sb.from('takeover_config').select('starting_price').eq('singleton',true).maybeSingle()
  ]);
  const map=new Map((rows||[]).map(r=>[Number(r.spot_number),r])),start=Number(cfg?.starting_price||10);
  target.innerHTML=Array.from({length:12},(_,i)=>{
    const n=i+1,s=map.get(n)||{spot_number:n,current_price:0,owner_key:null,company_name:null,website:null};
    const occupied=!!s.owner_key,price=Number(s.current_price)>0?Number(s.current_price):start;
    let site='No owner';try{site=s.website?new URL(/^https?:\/\//i.test(s.website)?s.website:'https://'+s.website).hostname.replace(/^www\./,''):'No owner'}catch{}
    return `<div class="admin-row"><span>${String(n).padStart(2,'0')}</span><div><b>${esc(s.company_name||'AVAILABLE')} · ${cash(price)}</b><small>${esc(site)}</small></div><button class="tiny danger" data-moderation-reset="${n}" ${occupied?'':'disabled'}>${occupied?'RESET':'AVAILABLE'}</button></div>`;
  }).join('');
}
document.addEventListener('click',e=>{if(e.target.closest?.('#adminBtn'))setTimeout(renderAllAdminSpots,180)},true);
const adminBoard=$('#adminBoard');if(adminBoard)new MutationObserver(()=>{if($('#adminPanel')?.classList.contains('on'))setTimeout(renderAllAdminSpots,80)}).observe(adminBoard,{childList:true});
})();
