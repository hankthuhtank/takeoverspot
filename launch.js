(()=>{'use strict';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const esc=s=>String(s??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
const cash=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(Number(n||0));
function toast(msg){const t=$('#toast');if(!t)return;t.textContent=msg;t.classList.add('on');setTimeout(()=>t.classList.remove('on'),3000)}

/* Purchase assent — checkout button exists in the static page, so no DOM observer is needed. */
function installTermsConsent(){
  if($('#termsConsent')||!$('#checkoutBtn'))return;
  const box=document.createElement('div');
  box.className='terms-consent';
  box.id='termsConsent';
  box.innerHTML='<label><input id="termsAgree" type="checkbox"><span><strong>I agree to the purchase terms.</strong> By paying, I agree to the <a href="terms.html" target="_blank" rel="noopener">Terms</a>, <a href="payments.html" target="_blank" rel="noopener">Payments Policy</a>, and <a href="auction-rules.html" target="_blank" rel="noopener">Rules</a>, including that placement duration, site uptime, continued operation, traffic, and results are not guaranteed.</span></label>';
  $('#checkoutBtn').before(box);
}
installTermsConsent();
document.addEventListener('click',e=>{
  const checkout=e.target.closest?.('#checkoutBtn');
  if(!checkout)return;
  const agree=$('#termsAgree'),box=$('#termsConsent');
  if(agree?.checked)return;
  e.preventDefault();e.stopPropagation();e.stopImmediatePropagation();
  box?.classList.add('attention');setTimeout(()=>box?.classList.remove('attention'),1200);
  toast('Agree to the purchase terms to continue');
},true);

/* Public social links — compact labels only; usernames remain off the page. */
function installSocialLinks(){
  const pulse=$('.social-pulse');if(!pulse)return;
  pulse.innerHTML='<i></i><strong>4-HOUR SOCIAL SNAPSHOTS</strong><span class="social-links"><a href="https://x.com/takeoverspot" target="_blank" rel="noopener">X</a><span>·</span><a href="https://www.instagram.com/takeover.spot" target="_blank" rel="noopener">INSTAGRAM</a></span>';
}
installSocialLinks();

/* Main app rewrites the page button as board state changes. Check it safely without observing our own mutations. */
function normalizeOwnedPageButton(){
  const b=$('#takePageBtn');if(!b)return;
  const text=(b.textContent||'').trim();
  const owned=/^YOU OWN THE PAGE(?:\b| ·)/.test(text)||/^PAGE PROTECTED ·/.test(text);
  if(owned){
    if(!b.classList.contains('owned-page-control'))b.classList.add('owned-page-control');
    if(b.disabled)b.disabled=false;
    if(b.title!=='Open My Spots')b.title='Open My Spots';
    if(text==='YOU OWN THE PAGE')b.textContent='YOU OWN THE PAGE · MANAGE';
  }else{
    if(b.classList.contains('owned-page-control'))b.classList.remove('owned-page-control');
    if(b.title)b.title='';
  }
}
normalizeOwnedPageButton();
setInterval(normalizeOwnedPageButton,1000);
document.addEventListener('click',e=>{
  const b=e.target.closest?.('#takePageBtn');if(!b)return;
  const text=(b.textContent||'').trim();
  if(!(/^YOU OWN THE PAGE/.test(text)||/^PAGE PROTECTED ·/.test(text)))return;
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
})();
