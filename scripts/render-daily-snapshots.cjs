// Durable noon data is captured in Postgres. This worker can retry hours later.
const fs=require('node:fs/promises'),path=require('node:path'),http=require('node:http');
const {chromium}=require('playwright'),sharp=require('sharp');
const ROOT=path.resolve(__dirname,'..');
const API='https://xvfgiaxxvwdnmzzdfboc.supabase.co/functions/v1/takeover-snapshot-render';
async function token(){
  const url=new URL(process.env.ACTIONS_ID_TOKEN_REQUEST_URL);url.searchParams.set('audience','takeover-daily-snapshots');
  const r=await fetch(url,{headers:{Authorization:'Bearer '+process.env.ACTIONS_ID_TOKEN_REQUEST_TOKEN}});
  if(!r.ok)throw Error('Renderer identity unavailable');return (await r.json()).value;
}
async function api(date,body){const r=await fetch(API+(date?'?date='+encodeURIComponent(date):''),{method:'POST',headers:{Authorization:'Bearer '+await token(),'Content-Type':body?'image/jpeg':'application/json'},body:body||'{}'});if(!r.ok)throw Error('Snapshot service returned '+r.status);return r.json();}
async function main(){
  const {pending}=await api();
  const server=http.createServer(async(req,res)=>{try{const name=decodeURIComponent(new URL(req.url,'http://localhost').pathname).slice(1),file=path.resolve(ROOT,name);if(!file.startsWith(ROOT+path.sep)||!/^([\w-]+\.(html|css|js)|vendor\/[\w.-]+\.js)$/.test(name))throw Error('not found');res.setHeader('Content-Type',({'.html':'text/html','.css':'text/css','.js':'application/javascript'})[path.extname(file)]);res.end(await fs.readFile(file));}catch{res.writeHead(404);res.end();}});
  await new Promise(r=>server.listen(0,'127.0.0.1',r));const origin='http://127.0.0.1:'+server.address().port;
  const browser=await chromium.launch();let saved=0;
  try{
    const page=await browser.newPage({viewport:{width:1600,height:1600},deviceScaleFactor:1});
    await page.route('**/*',route=>{const url=new URL(route.request().url());const allowed=url.origin===origin||['https://fonts.googleapis.com','https://fonts.gstatic.com'].includes(url.origin)||(url.origin==='https://xvfgiaxxvwdnmzzdfboc.supabase.co'&&url.pathname.startsWith('/storage/v1/object/public/'));return allowed?route.continue():route.abort();});
    await page.goto(origin+'/snapshot-render.html',{waitUntil:'load',timeout:90000});
    await page.waitForFunction(()=>!!window.TakeoverArchiveRender);
    async function render(record){
      await page.evaluate(async row=>{
        window.TakeoverArchiveRender.render(row);await document.fonts.ready;
        const board=document.getElementById('boardSurface');
        await Promise.all([...board.querySelectorAll('img')].map(img=>img.decode()));
        const urls=[...board.querySelectorAll('*')].flatMap(el=>[...getComputedStyle(el).backgroundImage.matchAll(/url\(["']?([^"')]+)["']?\)/g)].map(m=>m[1]));
        await Promise.all([...new Set(urls)].map(async src=>{const image=new Image();image.src=src;await image.decode();}));
        for(const animation of board.getAnimations({subtree:true})){animation.pause();animation.currentTime=1500;}
        await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
      },record);
      const png=await page.locator('#boardSurface').screenshot({type:'png',animations:'allow'});
      let jpeg;for(const quality of [88,80,70,60]){jpeg=await sharp(png).jpeg({quality,mozjpeg:true}).toBuffer();if(jpeg.length<=1048576)break;}
      const meta=await sharp(jpeg).metadata();if(meta.width!==1600||meta.height!==1600||jpeg.length>1048576)throw Error('Invalid snapshot output');return jpeg;
    }
    // Exercise real Chromium, fonts, clip paths and compression even before day one.
    const fixture={config_json:{starting_price:10,min_increment:1},board_json:Array.from({length:16},(_,i)=>({spot_number:i+1,current_price:0,owner_key:[1,2,5].includes(i+1)?'fixture':null,creative_id:'fixture',company_name:'SNAPSHOT TEST',canvas_json:{display:'combined',frameCells:[1,2,5],bg:{type:'solid',color:'#123456'},layers:[{type:'text',text:'SNAPSHOT TEST',font:'heavy',color:'#ffffff',x:5,y:20,w:90,h:30,size:24}]}}))};
    const checked=await render(fixture),stats=await sharp(checked).stats();if(stats.channels.every(c=>c.stdev<5))throw Error('Renderer produced a blank image');
    console.log('Renderer smoke passed: 1600 × 1600, fonts, combined artwork, JPEG '+checked.length+' bytes.');
    for(const row of pending||[]){const image=await render(row);await api(row.snapshot_date,image);saved++;console.log('Saved daily snapshot '+row.snapshot_date+' ('+image.length+' bytes)');}
    console.log('Pending snapshots processed: '+saved);
    if(saved){await fs.mkdir(path.join(ROOT,'snapshots'),{recursive:true});await fs.writeFile(path.join(ROOT,'snapshots/latest.json'),JSON.stringify({latest:(pending||[]).at(-1).snapshot_date})+'\n');}
  }finally{await browser.close();server.close();}
}
main().catch(e=>{console.error(e.message);process.exitCode=1;});
