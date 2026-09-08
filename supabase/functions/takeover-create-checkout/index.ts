import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

const cors={"Access-Control-Allow-Origin":"https://takeoverspot.com","Access-Control-Allow-Headers":"authorization, x-client-info, apikey, content-type"};
const form=(o:Record<string,string>)=>new URLSearchParams(o);
const json=(b:unknown,s=200)=>new Response(JSON.stringify(b),{status:s,headers:{...cors,"Content-Type":"application/json","Cache-Control":"no-store"}});

Deno.serve(async(req:Request)=>{
  if(req.method==="OPTIONS")return new Response("ok",{headers:cors});
  if(req.method!=="POST")return json({error:"Method not allowed"},405);
  try{
    const stripeKey=Deno.env.get("STRIPE_SECRET_KEY");
    if(!stripeKey)throw new Error("Stripe payments are not configured yet.");
    const url=Deno.env.get("SUPABASE_URL")!,anon=Deno.env.get("SUPABASE_ANON_KEY")!,service=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const auth=req.headers.get("Authorization")||"";
    const userClient=createClient(url,anon,{global:{headers:{Authorization:auth}}});
    const admin=createClient(url,service);
    const {data:{user},error:ue}=await userClient.auth.getUser();
    if(ue||!user)return json({error:"Sign in with your email first"},401);

    const body=await req.json();
    const spots=Array.isArray(body.spot_numbers)?body.spot_numbers.map((x:any)=>Number(x)):[];
    const bids=Array.isArray(body.bid_levels)?body.bid_levels.map((x:any)=>Number(x)):[];
    const company=String(body.company_name||"").trim();
    let website=String(body.website||"").trim();
    const logo=body.logo_url?String(body.logo_url):null;
    const canvas=(body.canvas_json&&typeof body.canvas_json==="object")?body.canvas_json:{};
    const kind=body.kind==="defend"?"defend":"takeover";
    if(website&&!/^https?:\/\//i.test(website))website="https://"+website;

    const {data:created,error:ce}=await admin.rpc("create_takeover_attempt_v4",{
      p_user_id:user.id,
      p_spot_numbers:spots,
      p_bid_levels:bids,
      p_company_name:company,
      p_website:website,
      p_logo_url:logo,
      p_canvas_json:canvas,
      p_kind:kind
    });
    if(ce)throw ce;
    const row=Array.isArray(created)?created[0]:created;
    if(!row?.attempt_id||!row?.total_amount)throw new Error("Could not create takeover quote");

    const amount=Math.round(Number(row.total_amount)*100);
    const label=kind==="defend"?`TAKEOVER · Defend Spot ${spots[0]}`:`TAKEOVER · ${spots.length===16?"Full Page":spots.length===1?`Spot ${spots[0]}`:`${spots.length} Spots`}`;
    const success=`https://takeoverspot.com/?takeover=success&attempt=${row.attempt_id}`;
    const cancel=`https://takeoverspot.com/?takeover=cancel&attempt=${row.attempt_id}`;
    const params:Record<string,string>={
      mode:"payment",success_url:success,cancel_url:cancel,customer_email:user.email||"",
      "line_items[0][price_data][currency]":"usd",
      "line_items[0][price_data][unit_amount]":String(amount),
      "line_items[0][price_data][product_data][name]":label,
      "line_items[0][quantity]":"1",
      "metadata[takeover_attempt_id]":row.attempt_id,
      "metadata[takeover_user_id]":user.id,
      "payment_intent_data[metadata][takeover_attempt_id]":row.attempt_id,
      "payment_intent_data[metadata][takeover_user_id]":user.id,
      "payment_method_types[0]":"card",
      expires_at:String(Math.floor(Date.now()/1000)+1860)
    };
    const r=await fetch("https://api.stripe.com/v1/checkout/sessions",{method:"POST",headers:{Authorization:`Bearer ${stripeKey}`,"Content-Type":"application/x-www-form-urlencoded","Idempotency-Key":`takeover-checkout-${row.attempt_id}`},body:form(params)});
    const checkout=await r.json();
    if(!r.ok){
      const reason=checkout?.error?.message||"Checkout creation failed";
      console.error("Stripe Checkout creation failed",{attempt_id:row.attempt_id,type:checkout?.error?.type,code:checkout?.error?.code,param:checkout?.error?.param,message:reason});
      await admin.rpc("mark_takeover_refund",{p_attempt_id:row.attempt_id,p_status:"failed",p_reason:reason});
      return json({error:reason,code:checkout?.error?.code||null,param:checkout?.error?.param||null},400);
    }
    const {data:linked,error:linkError}=await admin.rpc("mark_takeover_checkout",{p_attempt_id:row.attempt_id,p_session_id:checkout.id});
    if(linkError||linked!==true){
      // Never expose a payment URL until recovery can find its Stripe session.
      try{await fetch(`https://api.stripe.com/v1/checkout/sessions/${encodeURIComponent(checkout.id)}/expire`,{method:"POST",headers:{Authorization:`Bearer ${stripeKey}`}});}catch{}
      throw new Error("Checkout could not be saved safely. Please try again.");
    }
    return json({url:checkout.url,attempt_id:row.attempt_id,total:Number(row.total_amount)});
  }catch(e){
    const message=e instanceof Error?e.message:"Checkout error";
    console.error("Checkout function error",message);
    return json({error:message},400)
  }
});
