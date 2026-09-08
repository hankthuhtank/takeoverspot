import { createClient } from 'npm:@supabase/supabase-js@2.112.4';
import { createRemoteJWKSet, jwtVerify } from 'npm:jose@6.1.0';

const jwks=createRemoteJWKSet(new URL('https://token.actions.githubusercontent.com/.well-known/jwks'));
const json=(data:unknown,status=200)=>new Response(JSON.stringify(data),{status,headers:{'Content-Type':'application/json','Cache-Control':'no-store'}});
const bucket='takeover-daily-snapshots',maxBytes=1048576;
// Only this repository's dedicated main-branch renderer can write an image.
// It cannot create a snapshot, change artwork/payments, or replace an existing image.
export function trustedRenderer(p:Record<string,unknown>){
  return p.repository_id==='1353746487'&&p.repository_owner_id==='236490719'
    &&p.repository==='hankthuhtank/takeoverspot'&&p.ref==='refs/heads/main'
    &&p.workflow_ref==='hankthuhtank/takeoverspot/.github/workflows/daily-snapshots.yml@refs/heads/main'
    &&['schedule','workflow_dispatch','push'].includes(String(p.event_name));
}
async function limitedBody(req:Request){
  const reader=req.body?.getReader();if(!reader)throw new Error('Image required');
  const chunks:Uint8Array[]=[];let size=0;
  while(true){const {done,value}=await reader.read();if(done)break;size+=value.length;if(size>maxBytes){await reader.cancel();throw new Error('Image exceeds 1 MB');}chunks.push(value);}
  const out=new Uint8Array(size);let at=0;for(const c of chunks){out.set(c,at);at+=c.length;}
  if(size<100||out[0]!==255||out[1]!==216||out.at(-2)!==255||out.at(-1)!==217)throw new Error('JPEG required');return out;
}
Deno.serve(async(req:Request)=>{
  if(req.method!=='POST')return json({error:'Method not allowed'},405);
  try{
    const token=req.headers.get('Authorization')?.replace(/^Bearer /,'')||'';
    let payload;try{({payload}=await jwtVerify(token,jwks,{issuer:'https://token.actions.githubusercontent.com',audience:'takeover-daily-snapshots',algorithms:['RS256'],maxTokenAge:'10m'}));}catch{return json({error:'Unauthorized'},401);}
    if(!trustedRenderer(payload))return json({error:'Renderer access required'},403);
    const admin=createClient(Deno.env.get('SUPABASE_URL')!,Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!,{auth:{persistSession:false,autoRefreshToken:false}});
    const url=new URL(req.url),date=url.searchParams.get('date');
    if(!date){const {data,error}=await admin.from('takeover_daily_snapshots').select('snapshot_date,captured_at,scheduled_at,board_json,config_json').is('image_path',null).order('snapshot_date').limit(14);if(error)throw error;return json({pending:data});}
    if(!/^\d{4}-\d{2}-\d{2}$/.test(date))return json({error:'Invalid date'},400);
    const {data:row,error}=await admin.from('takeover_daily_snapshots').select('image_path').eq('snapshot_date',date).single();
    if(error||!row)return json({error:'Snapshot not found'},404);if(row.image_path)return json({ok:true,already_saved:true});
    const bytes=await limitedBody(req),path=date+'.jpg';
    const {error:uploadError}=await admin.storage.from(bucket).upload(path,bytes,{contentType:'image/jpeg',cacheControl:'31536000',upsert:false});
    let savedBytes=bytes.length;
    if(uploadError){
      // Resume an interrupted upload -> row-update without overwriting the file.
      if(!['409','400'].includes(String(uploadError.statusCode)))throw uploadError;
      const {data:existing,error:readError}=await admin.storage.from(bucket).download(path);if(readError||!existing)throw uploadError;savedBytes=existing.size;
    }
    const {error:updateError}=await admin.from('takeover_daily_snapshots').update({image_path:path,image_bytes:savedBytes,rendered_at:new Date().toISOString()}).eq('snapshot_date',date).is('image_path',null);
    if(updateError)throw updateError;return json({ok:true,date,bytes:savedBytes});
  }catch(e){console.error('snapshot renderer',e instanceof Error?e.message:'failed');return json({error:'Snapshot image could not be saved'},500);}
});
