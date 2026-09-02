(()=>{'use strict';
if(window.supabase?.createClient){const rawCreate=window.supabase.createClient.bind(window.supabase);window.supabase.createClient=(...args)=>{const client=rawCreate(...args);const rawRpc=client.rpc.bind(client);client.rpc=(...rpcArgs)=>Promise.resolve(rawRpc(...rpcArgs));return client}}
const css=document.createElement('link');css.rel='stylesheet';css.href='takeover-v3.css?v=14';document.head.appendChild(css);
const main=document.createElement('script');main.src='takeover-v3.js?v=14';main.onload=()=>{const social=document.querySelector('.social-pulse');if(social)social.innerHTML='<i></i><strong>DAILY SNAPSHOT · 12 PM CT</strong><em><a href="https://x.com/takeoverspot" target="_blank" rel="noopener">X</a><span>·</span><a href="https://www.instagram.com/takeover.spot" target="_blank" rel="noopener">INSTAGRAM</a></em>'};document.body.appendChild(main);
})();
