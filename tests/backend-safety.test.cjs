const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {stripTypeScriptTypes}=require('node:module');
const references=fs.readFileSync('supabase/functions/_shared/storage-references.ts','utf8').replace(/export /g,'');
const shared=vm.runInNewContext(references+';({readAllRows,storageReferences})',{Date,Number,Array,Promise,Error});
test('cleanup reads references beyond the 1,000 row API cap',async()=>{
  const rows=Array.from({length:1201},(_,id)=>({id,canvas_json:id===1200?'keep-last-image':null}));let calls=0;
  const result=await shared.readAllRows(()=>({range:async(a,b)=>{calls++;return{data:rows.slice(a,b+1),count:rows.length,error:null};}}));
  assert.equal(result.length,1201);assert.equal(result[1200].canvas_json,'keep-last-image');assert.equal(calls,3);
});
test('cleanup aborts on failed, truncated, or uncounted reference reads',async()=>{
  for(const response of [{error:{message:'offline'},data:null},{data:[{}],count:1200},{data:[],count:null}])
    await assert.rejects(shared.readAllRows(()=>({range:async()=>response})),/failed|incomplete|unavailable/);
});
test('cleanup refuses to infer retention when config fails',async()=>{
  const q={select(){return q},eq(){return q},single:async()=>({error:{message:'offline'}})};
  await assert.rejects(shared.storageReferences({from:()=>q}),/retention settings unavailable/);
});
test('storage worker never deletes when a reference scan fails',async()=>{
  let handler,deletes=0;
  const source=stripTypeScriptTypes(fs.readFileSync('supabase/functions/takeover-storage-worker/index.ts','utf8').replace(/^import .*;\n/gm,''));
  const q={select(){return q},eq(){return q},maybeSingle:async()=>({data:{secret:'test-secret'}})};
  const admin={from:()=>q,storage:{from:()=>({remove:async()=>{deletes++;}})}};
  vm.runInNewContext(source,{Deno:{env:{get:()=>''},serve:h=>handler=h},createClient:()=>admin,storageReferences:async()=>{throw Error('Reference read failed')},Response,Date,Set,console:{error(){}}});
  const res=await handler(new Request('https://example.test',{method:'POST',headers:{'X-Takeover-Cron':'test-secret'},body:'{}'}));
  assert.equal(res.status,500);assert.equal(deletes,0);
});
test('checkout never returns a pay URL when session linking fails',async()=>{
  let handler,expired=false;
  const source=stripTypeScriptTypes(fs.readFileSync('supabase/functions/takeover-create-checkout/index.ts','utf8').replace(/^import .*;\n/gm,''));
  const client={auth:{getUser:async()=>({data:{user:{id:'test-user',email:'test@example.test'}}})},rpc:async name=>name==='create_takeover_attempt_v4'?{data:{attempt_id:'test-attempt',total_amount:10}}:{data:null,error:{message:'write failed'}}};
  vm.runInNewContext(source,{Deno:{env:{get:()=> 'test'},serve:h=>handler=h},createClient:()=>client,Response,URLSearchParams,Date,console:{error(){}},fetch:async url=>{if(url.endsWith('/expire')){expired=true;return new Response('{}');}return new Response(JSON.stringify({id:'cs_test_mock',url:'https://checkout.stripe.com/test'}));}});
  const res=await handler(new Request('https://example.test',{method:'POST',body:JSON.stringify({spot_numbers:[1],bid_levels:[10],company_name:'Test'})}));
  const result=await res.json();assert.equal(res.status,400);assert.equal(result.url,undefined);assert.equal(expired,true);
});
