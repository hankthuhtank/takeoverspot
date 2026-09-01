(()=>{'use strict';
const $=s=>document.querySelector(s);
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
})();
