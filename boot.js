(()=>{'use strict';
const css=document.createElement('link');css.rel='stylesheet';css.href='polish.css?v=1';document.head.appendChild(css);
const polish=document.createElement('script');polish.src='polish.js?v=1';polish.onload=()=>{const main=document.createElement('script');main.src='takeover-v2.js?v=4';document.body.appendChild(main)};document.body.appendChild(polish);
})();
