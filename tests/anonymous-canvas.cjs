const { chromium } = require('playwright');

(async()=>{
  const browser=await chromium.launch({headless:true});
  const page=await browser.newPage({viewport:{width:1440,height:1000}});

  await page.route('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2',async route=>{
    const stub=`(()=>{const board=Array.from({length:16},(_,i)=>({spot_number:i+1,current_price:0,owner_key:null,company_name:null,website:null,logo_url:null,creative_id:null,canvas_json:null,owner_since:null,updated_at:new Date().toISOString()}));const cfg={starting_price:10,min_increment:1,purchases_enabled:true,page_shield_until:null};function builder(t){const b={select(){return b},eq(){return b},is(){return b},in(){return Promise.resolve({data:[],error:null})},update(){return b},insert(){return Promise.resolve({data:null,error:null})},limit(){return Promise.resolve({data:[],error:null})},order(){return Promise.resolve({data:t==='takeover_spots'?board:[],error:null})},maybeSingle(){return Promise.resolve({data:t==='takeover_config'?cfg:null,error:null})},then(r){return Promise.resolve({data:t==='takeover_spots'?board:[],error:null}).then(r)}};return b}window.__storageUploads=0;const sb={auth:{getSession:()=>Promise.resolve({data:{session:null}}),onAuthStateChange:()=>({data:{subscription:{unsubscribe(){}}}}),signOut:()=>Promise.resolve(),signInWithOtp:()=>Promise.resolve({error:null})},from:builder,rpc:(name)=>Promise.resolve({data:name==='is_takeover_admin'?false:null,error:null}),channel:()=>({on(){return this},subscribe(){return this}}),removeChannel(){},storage:{from:()=>({upload:()=>{window.__storageUploads++;return Promise.resolve({error:new Error('Anonymous storage upload should not happen')})},getPublicUrl:()=>({data:{publicUrl:'https://example.invalid/test.png'}})})},functions:{invoke:()=>Promise.resolve({data:{url:'https://stripe.test'},error:null})}};window.supabase={createClient:()=>sb}})();`;
    await route.fulfill({status:200,contentType:'application/javascript',body:stub});
  });

  await page.goto('http://127.0.0.1:4173/index.html',{waitUntil:'networkidle'});
  await page.locator('#introGotIt').click();
  await page.locator('.available-cell').nth(5).click();
  await page.locator('#companyName').fill('Example Co');
  await page.locator('#companyWebsite').fill('example.com');

  const png=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=','base64');
  await page.locator('#logoFile').setInputFiles({name:'logo.png',mimeType:'image/png',buffer:png});
  await page.waitForFunction(()=>document.querySelector('#logoPreview img')?.src.startsWith('blob:'));
  if(await page.locator('#logoPreview img').count()!==1)throw new Error('Anonymous logo preview missing');

  await page.locator('#openPurchaseCanvas').click();
  await page.waitForSelector('#canvasModal.on');
  const presetCount=await page.locator('#canvasPresets .preset-card').count();
  if(presetCount<10)throw new Error('Preset library too small: '+presetCount);

  await page.locator('#addText').click();
  await page.locator('#canvasStage .editor-layer').last().click();
  const text=page.locator('#layerText');
  await text.click();
  await text.press(process.platform==='darwin'?'Meta+A':'Control+A');
  await text.pressSequentially('HELLO WORLD',{delay:20});
  if((await page.locator('#layerText').inputValue())!=='HELLO WORLD')throw new Error('Text input lost focus during typing');
  const active=await page.evaluate(()=>document.activeElement?.id);
  if(active!=='layerText')throw new Error('Text editor lost focus after typing');

  await page.locator('#bgImageFile').setInputFiles({name:'background.png',mimeType:'image/png',buffer:png});
  await page.waitForFunction(()=>document.querySelector('#canvasStage')?.style.background.includes('blob:'));
  if((await page.evaluate(()=>window.__storageUploads))!==0)throw new Error('Photo background tried to upload before sign-in');

  await page.locator('[data-preset="photo"]').click();
  await page.waitForFunction(()=>document.querySelector('#canvasStage')?.style.background.includes('blob:'));
  await page.locator('#saveCanvas').click();
  await page.waitForSelector('#canvasModal:not(.on)');

  await page.locator('#continueSignin').click();
  await page.waitForSelector('#authModal.on');
  const draft=await page.evaluate(()=>JSON.parse(localStorage.getItem('takeover_purchase_draft_v3')||'null'));
  if(!draft)throw new Error('Anonymous purchase draft was not saved before sign-in');
  if(!String(draft.logoUrl||'').startsWith('local:'))throw new Error('Logo draft did not preserve local reference');
  if(!String(draft.canvas?.bg?.image||'').startsWith('local:'))throw new Error('Photo background did not preserve local reference');
  if((await page.evaluate(()=>window.__storageUploads))!==0)throw new Error('Assets uploaded before customer signed in');

  console.log('PASS anonymous canvas: logo preview, presets, continuous typing, photo BG, local draft persistence, no pre-signin upload');
  await browser.close();
})().catch(async e=>{console.error(e);process.exit(1)});
