(()=>{'use strict';
if(window.supabase?.createClient){const rawCreate=window.supabase.createClient.bind(window.supabase);window.supabase.createClient=(...args)=>{const client=rawCreate(...args);const rawRpc=client.rpc.bind(client);client.rpc=(...rpcArgs)=>Promise.resolve(rawRpc(...rpcArgs));return client}}
function applyTakeoverCopy(){
  const intro=[...document.querySelectorAll('#introModal .rule')];
  if(intro[1])intro[1].innerHTML='<b>2 · Keep it until somebody takes it.</b><span>No daily reset. No countdown. Ownership continues until somebody takes it or another applicable Term ends it.</span>';
  const assent=document.querySelector('#purchaseAssent')?.closest('.purchase-assent')?.querySelector('span');
  if(assent)assent.innerHTML='I agree to the <a href="terms.html" target="_blank">Terms</a>, <a href="payments.html" target="_blank">Payments</a> and <a href="auction-rules.html" target="_blank">Rules</a>. Placement has no guaranteed minimum duration or cash value.';
  const checkoutHint=document.querySelector('#checkoutBtn + .hint');
  if(checkoutHint)checkoutHint.textContent='A full 16-spot purchase gets 24 hours of exclusive protection. If the board changes while you are in Checkout, a stale purchase is rejected and automatically refunded instead of overwriting valid territory.';
  const rulesInner=document.querySelector('#rulesModal .panel-inner');
  if(rulesInner&&!document.querySelector('#rulesCatchphrase')){const p=document.createElement('p');p.id='rulesCatchphrase';p.className='rules-copy';p.innerHTML='<strong>THE WEBPAGE BELONGS TO WHOEVER WANTS IT MOST.</strong>';const head=rulesInner.querySelector('.panel-head');head?.insertAdjacentElement('afterend',p)}
  const quickRules=[...document.querySelectorAll('#rulesModal .rule')];
  if(quickRules[1])quickRules[1].innerHTML='<b>Keep it until you are outbid.</b><span>No daily timer. Another advertiser can take it by paying the valid takeover price.</span>';
  [...document.querySelectorAll('#rulesModal .rules-fineprint .rules-copy')].forEach(p=>{if(/^Future seasons\./i.test(p.textContent.trim()))p.remove()});
}
applyTakeoverCopy();
const css=document.createElement('link');css.rel='stylesheet';css.href='takeover-v3.css?v=18';document.head.appendChild(css);
const main=document.createElement('script');main.src='takeover-v3.js?v=18';main.onload=()=>{applyTakeoverCopy();const social=document.querySelector('.social-pulse');if(social)social.innerHTML='<i></i><strong>DAILY SNAPSHOT · 12 PM CT</strong><em><a href="https://x.com/takeoverspot" target="_blank" rel="noopener">X</a><span>·</span><a href="https://www.instagram.com/takeover.spot" target="_blank" rel="noopener">INSTAGRAM</a></em>'};document.body.appendChild(main);
})();
