const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {chromium}=require('playwright'),sharp=require('sharp');
const root=path.resolve(__dirname,'..');
const server=http.createServer((req,res)=>{try{const name=new URL(req.url,'http://localhost').pathname;const file=path.resolve(root,'.'+name);if(!file.startsWith(root+path.sep))throw Error();res.setHeader('Content-Type',({'.html':'text/html','.js':'application/javascript','.css':'text/css'})[path.extname(file)]||'application/octet-stream');let content=fs.readFileSync(file);if(name==='/index.html')content=content.toString().replace(/<script src="boot.js[^>]+><\/script>/,'');res.end(content);}catch{res.writeHead(404);res.end();}});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const browser=await chromium.launch();
 try{
  const page=await browser.newPage({viewport:{width:1200,height:900}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  const origin='http://127.0.0.1:'+server.address().port;
  await page.goto(origin+'/index.html');
  const result=await page.evaluate(async()=>{
   const row={snapshot_date:'2026-09-09',captured_at:'2026-09-09T17:00:00Z',image_path:null,config_json:{starting_price:5,min_increment:1},board_json:Array.from({length:16},(_,i)=>({spot_number:i+1,current_price:0,owner_key:[2,3,6].includes(i+1)?'fixture':null,creative_id:'fixture',company_name:'SAVED NOON',canvas_json:{display:'combined',frameCells:[2,3,6],bg:{type:'solid',color:'#123456'},layers:[{type:'text',text:'SAVED NOON',font:'heavy',color:'#ffffff',x:5,y:20,w:90,h:30,size:24}]}}))};
   const calls=[];const query={select(){return this},eq(){return this},async single(){return{data:row}}};window.TakeoverDailySnapshots.mount({from(table){calls.push(table);return query}});
   const started=performance.now();const blob=await window.TakeoverDailySnapshots.savedPNG(row);
   const data=await new Promise(resolve=>{const r=new FileReader();r.onload=()=>resolve(r.result);r.readAsDataURL(blob)});
   return {data,calls,elapsed:performance.now()-started,frames:document.querySelectorAll('iframe').length};
  });
  const bytes=Buffer.from(result.data.split(',')[1],'base64');await fs.promises.mkdir('test-results',{recursive:true});await fs.promises.writeFile('test-results/noon-export.png',bytes);const meta=await sharp(bytes).metadata();assert.equal(meta.width,1600);assert.equal(meta.height,1600);assert.equal(result.frames,0);assert.deepEqual(result.calls,['takeover_daily_snapshots']);assert.ok(result.elapsed<45000);
  const pixel=async(left,top)=>[...(await sharp(bytes).extract({left,top,width:1,height:1}).removeAlpha().raw().toBuffer())];
  assert.deepEqual(await pixel(100,100),[247,247,243],'first tile must not carry hover highlight');
  assert.deepEqual(await pixel(500,100),[18,52,86],'combined artwork must render');
  assert.deepEqual(await pixel(900,500),[247,247,243],'L-shaped territory must not paint unowned cell');
  assert.deepEqual(errors,[]);await fs.promises.mkdir('test-results',{recursive:true});await fs.promises.writeFile('test-results/noon-export.png',bytes);
  console.log('PASS: saved noon data, real iframe PNG export, no highlight, combined territory clipping, cleanup; '+Math.round(result.elapsed)+' ms');
 }finally{await browser.close();server.close();}
})().catch(e=>{console.error(e);server.close();process.exitCode=1});
