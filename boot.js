(()=>{'use strict';
const css=document.createElement('link');css.rel='stylesheet';css.href='polish.css?v=1';document.head.appendChild(css);
const launchCss=document.createElement('link');launchCss.rel='stylesheet';launchCss.href='launch.css?v=1';document.head.appendChild(launchCss);
const polish=document.createElement('script');polish.src='polish.js?v=1';polish.onload=()=>{const launch=document.createElement('script');launch.src='launch.js?v=1';launch.onload=()=>{const main=document.createElement('script');main.src='takeover-v2.js?v=4';document.body.appendChild(main)};document.body.appendChild(launch)};document.body.appendChild(polish);
})();
