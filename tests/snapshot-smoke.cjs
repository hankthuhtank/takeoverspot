// Export pipeline checks with a stubbed rasterizer; not browser pixel validation.
const {JSDOM}=require('jsdom'),fs=require('node:fs'),assert=require('node:assert/strict');
const dom=new JSDOM(`<link href="https://fonts.googleapis.com/css2?family=Manrope" rel="stylesheet"><button id="snapshotCreate"></button><button id="snapshotCopy" disabled></button><button id="snapshotDownload" disabled></button><p id="snapshotStatus"></p><img id="snapshotImage" hidden><svg id="takeoverShapeDefs"><defs><clipPath id="frame"><rect width="1" height="1"/></clipPath></defs></svg><div id="boardSurface" style="width:390px;height:390px;font-family:Manrope"><div class="territory" style="clip-path:url(#frame);font-family:Manrope"><span style="font-family:Manrope">Public artwork</span></div><div id="spotActions"><button class="available-cell">SPOT 16</button><button class="take-pill">DEFEND</button><button class="inspect-spot">Inspect</button></div><div id="takeoverRevealStage">Private preview</div></div><div id="adminPanel">Private account details</div>`,{url:'https://takeoverspot.com',runScripts:'outside-only'});
const w=dom.window,d=w.document;let allowed=false,refreshOk=true,renders=0,revoked=0,lastOptions;
w.document.fonts={ready:Promise.resolve()};w.URL.createObjectURL=()=> 'blob:test';w.URL.revokeObjectURL=()=>revoked++;
d.getElementById('boardSurface').getBoundingClientRect=()=>({width:390,height:390});
w.fetch=async url=>({ok:true,text:async()=>"@font-face {font-family:'Manrope';src:url(https://fonts.gstatic.com/test.woff2);}",blob:async()=>new w.Blob(['font'],{type:'font/woff2'})});
w.htmlToImage={toBlob:async(root,opts)=>{renders++;lastOptions=opts;assert.equal(root.querySelectorAll('.take-pill,.inspect-spot,#takeoverRevealStage').length,0);assert.ok(!root.textContent.includes('Private'));assert.ok(root.textContent.includes('SPOT 16'));const clip=root.querySelector('.territory').style.clipPath.match(/#([^"')]+)/)[1];assert.ok(root.querySelector('[id="'+clip+'"]'),'combined territory clip must be embedded');return new w.Blob(['png'],{type:'image/png'});}};
w.eval(fs.readFileSync('board-snapshot.js','utf8'));
w.TakeoverSnapshot.mount({authorize:async()=>allowed,refresh:async()=>refreshOk});
async function capture(){d.getElementById('snapshotCreate').click();for(let i=0;i<100&&d.getElementById('snapshotCreate').disabled;i++)await new Promise(r=>setTimeout(r,5));assert.equal(d.getElementById('snapshotCreate').disabled,false);}
(async()=>{
  await capture();assert.equal(renders,0);assert.match(d.getElementById('snapshotStatus').textContent,/owner account/);
  allowed=true;refreshOk=false;await capture();assert.equal(renders,0);
  refreshOk=true;await capture();assert.equal(renders,1);assert.equal(lastOptions.width,390);assert.equal(lastOptions.canvasWidth,2048);assert.equal(lastOptions.canvasHeight,2048);assert.equal(lastOptions.pixelRatio,1);assert.match(lastOptions.fontEmbedCSS,/data:/);assert.equal(d.getElementById('snapshotDownload').disabled,false,d.getElementById('snapshotStatus').textContent);
  w.TakeoverSnapshot.release();assert.equal(revoked,1);assert.equal(d.getElementById('snapshotDownload').disabled,true);
  assert.equal(d.querySelectorAll('body>div[aria-hidden]').length,0);
  console.log('PASS: owner authorization, stale-board rejection, full-board export, clip definitions, embedded fonts, control exclusion, cleanup.');
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>w.close());
