const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {stripTypeScriptTypes}=require('node:module');
const source=fs.readFileSync('supabase/functions/takeover-snapshot-render/index.ts','utf8');
const trust=vm.runInNewContext(stripTypeScriptTypes(source.slice(source.indexOf('export function trustedRenderer'),source.indexOf('async function limitedBody')).replace('export ',''))+';trustedRenderer');
const claims={repository_id:'1353746487',repository_owner_id:'236490719',repository:'hankthuhtank/takeoverspot',ref:'refs/heads/main',workflow_ref:'hankthuhtank/takeoverspot/.github/workflows/daily-snapshots.yml@refs/heads/main',event_name:'schedule'};
test('renderer rejects forks, other workflows, PR events and different branches',()=>{
  assert.equal(trust(claims),true);
  for(const key of Object.keys(claims))assert.equal(trust({...claims,[key]:'untrusted'}),false,key);
});
test('Central noon selects 17 UTC in daylight time and 18 UTC in standard time',()=>{
  const hour=d=>new Intl.DateTimeFormat('en-US',{timeZone:'America/Chicago',hour:'2-digit',hourCycle:'h23'}).format(new Date(d));
  assert.equal(hour('2026-09-08T17:00:00Z'),'12');assert.equal(hour('2026-12-08T18:00:00Z'),'12');
  assert.equal(hour('2026-03-08T17:00:00Z'),'12');assert.equal(hour('2026-11-01T18:00:00Z'),'12');
});
const manage=vm.runInNewContext(fs.readFileSync('supabase/functions/_shared/account-management.ts','utf8').replace('export ','')+';manageAccount',{Date,Error,Object,String});
const actor='11111111-1111-4111-8111-111111111111',target='22222222-2222-4222-8222-222222222222';
function mock(protectedRecords=false){
  const writes=[],admin={auth:{admin:{getUserById:async()=>({data:{user:{id:target,email:'example@example.test'}}}),updateUserById:async(...args)=>{writes.push(['ban',...args]);return{};},deleteUser:async(...args)=>{writes.push(['delete',...args]);return{};}}},rpc:async()=>({data:{payments:protectedRecords,owner:false,uploads:false}}),from(table){let mode='read';const q={select(){return q},eq(){return q},maybeSingle:async()=>({data:null}),single:async()=>({data:{id:'event'}}),insert(data){writes.push([table,'insert',data]);mode='insert';return q},upsert:async data=>{writes.push([table,'upsert',data]);return{}},update(data){writes.push([table,'update',data]);mode='update';return q},then(resolve){return Promise.resolve({data:mode==='read'?[]:null}).then(resolve)}};return q;}};return{admin,writes};
}
test('account manager refuses owner self-disable or self-delete',async()=>{
  const {admin,writes}=mock();for(const action of ['account_disable','account_delete'])await assert.rejects(manage(admin,actor,{action,user_id:actor}),/protected/);assert.equal(writes.length,0);
});
test('deletion requires confirmation and refuses financial records before any mutation',async()=>{
  const {admin,writes}=mock(true);await assert.rejects(manage(admin,actor,{action:'account_delete',user_id:target,confirm_email:'example@example.test',confirmation:'DELETE'}),/protected records/);assert.equal(writes.length,0);
  const clean=mock();await assert.rejects(manage(clean.admin,actor,{action:'account_delete',user_id:target}),/confirm/);assert.equal(clean.writes.length,0);
});
test('eligible deletion disables access first and records an audit event',async()=>{
  const {admin,writes}=mock();await manage(admin,actor,{action:'account_delete',user_id:target,confirm_email:'example@example.test',confirmation:'DELETE'});
  assert.equal(writes[0][0],'takeover_admin_events');assert.ok(writes.findIndex(x=>x[0]==='ban')<writes.findIndex(x=>x[0]==='delete'));assert.ok(writes.find(x=>x[0]==='takeover_account_controls'&&x[2].disabled));
});
