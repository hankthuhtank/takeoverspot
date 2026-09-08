-- Prevent quote totals and line items from observing different market states.
CREATE OR REPLACE FUNCTION public.create_takeover_attempt_v4(p_user_id uuid, p_spot_numbers integer[], p_bid_levels numeric[], p_company_name text, p_website text, p_logo_url text, p_canvas_json jsonb, p_kind text DEFAULT 'takeover'::text)
 RETURNS TABLE(attempt_id uuid, total_amount numeric)
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
declare
  v_uid uuid:=p_user_id; v_cfg public.takeover_config%rowtype; v_profile public.takeover_profiles%rowtype;
  v_attempt uuid; v_total numeric:=0; v_i integer; v_spot public.takeover_spots%rowtype;
  v_min numeric; v_bid numeric; v_charge numeric; v_company text:=trim(coalesce(p_company_name,''));
  v_site text:=trim(coalesce(p_website,'')); v_logo text:=nullif(trim(coalesce(p_logo_url,'')),'');
  v_canvas jsonb:=coalesce(p_canvas_json,'{}'::jsonb); v_owns_page boolean:=false; v_recent integer:=0;
begin
  if v_uid is null or not exists(select 1 from auth.users u where u.id=v_uid) then raise exception 'Valid user required'; end if;
  -- Serialize each user's quote limit, then hold one board state through both loops.
  perform pg_advisory_xact_lock(hashtextextended('takeover-quote:'||v_uid::text,0));
  select count(*) into v_recent from public.takeover_attempts where user_id=v_uid and created_at>now()-interval '5 minutes';
  if v_recent>=8 then raise exception 'Too many checkout attempts. Wait a few minutes and try again'; end if;
  select * into v_cfg from public.takeover_config where singleton=true for update;
  if not v_cfg.purchases_enabled then raise exception 'Takeovers are temporarily paused'; end if;
  select count(*)=16 into v_owns_page from public.takeover_spots where owner_user_id=v_uid;
  if v_cfg.page_shield_until is not null and v_cfg.page_shield_until>now() and not v_owns_page then raise exception 'The full-page takeover is currently protected'; end if;
  if p_kind not in ('takeover','defend') then raise exception 'Invalid purchase type'; end if;
  if p_spot_numbers is null or cardinality(p_spot_numbers)<1 or cardinality(p_spot_numbers)>16 then raise exception 'Choose between 1 and 16 spots'; end if;
  if cardinality(array(select distinct x from unnest(p_spot_numbers) x))<>cardinality(p_spot_numbers) then raise exception 'A spot can only be selected once'; end if;
  if cardinality(p_bid_levels)<>cardinality(p_spot_numbers) then raise exception 'Bid list does not match spot selection'; end if;
  if p_kind='defend' and cardinality(p_spot_numbers)<>1 then raise exception 'Defend one spot at a time'; end if;
  if cardinality(p_spot_numbers)<>16 and not public.takeover_selection_connected(p_spot_numbers) then raise exception 'Multiple spots must touch each other'; end if;
  if v_company='' or length(v_company)>80 then raise exception 'Enter a name / brand (80 characters max)'; end if;
  if length(v_site)>300 or (v_site<>'' and v_site !~* '^https?://[^[:space:]]+$') then raise exception 'Enter a valid http(s) link or leave it blank'; end if;
  if jsonb_typeof(v_canvas)<>'object' or octet_length(v_canvas::text)>40000 then raise exception 'Creative design is invalid or too large'; end if;
  if jsonb_typeof(v_canvas->'layers')='array' and jsonb_array_length(v_canvas->'layers')>40 then raise exception 'Creative design has too many layers'; end if;
  if not public.takeover_canvas_assets_owned(v_uid,v_canvas) then raise exception 'Creative images must come from your own TAKEOVER uploads'; end if;
  if v_logo is not null and v_logo !~ ('^https://xvfgiaxxvwdnmzzdfboc[.]supabase[.]co/storage/v1/object/public/takeover-logos/'||v_uid::text||'/') then raise exception 'Invalid logo upload'; end if;

  perform 1 from public.takeover_spots where spot_number=any(p_spot_numbers) order by spot_number for update;

  insert into public.takeover_profiles(user_id,company_name,website,logo_url)
  values(v_uid,v_company,v_site,v_logo)
  on conflict(user_id) do update set company_name=excluded.company_name,website=excluded.website,logo_url=coalesce(excluded.logo_url,public.takeover_profiles.logo_url),updated_at=now()
  returning * into v_profile;

  for v_i in 1..cardinality(p_spot_numbers) loop
    select * into v_spot from public.takeover_spots where spot_number=p_spot_numbers[v_i];
    if not found then raise exception 'Spot % does not exist',p_spot_numbers[v_i]; end if;
    v_bid:=trunc(p_bid_levels[v_i]);
    if v_bid is null or v_bid<0 or v_bid>1000000 then raise exception 'Invalid bid level'; end if;
    if p_kind='defend' then
      if v_spot.owner_user_id is distinct from v_uid then raise exception 'You can only defend a spot you own'; end if;
      v_min:=v_spot.current_price+v_cfg.min_increment;
      if v_bid<v_min then raise exception 'Spot % must be raised to at least $%',v_spot.spot_number,v_min; end if;
      v_charge:=v_bid-v_spot.current_price;
    elsif v_spot.owner_user_id=v_uid then v_bid:=v_spot.current_price; v_charge:=0;
    else
      v_min:=case when v_spot.current_price=0 then v_cfg.starting_price else v_spot.current_price+v_cfg.min_increment end;
      if v_bid<v_min then raise exception 'Spot % now requires at least $%',v_spot.spot_number,v_min; end if;
      v_charge:=v_bid;
    end if;
    v_total:=v_total+v_charge;
  end loop;
  if v_total<=0 then raise exception 'There is nothing new to purchase'; end if;

  insert into public.takeover_attempts(user_id,kind,company_name,website,logo_url,total_amount,canvas_json)
  values(v_uid,p_kind,v_company,v_site,v_logo,v_total,v_canvas)
  returning id into v_attempt;

  for v_i in 1..cardinality(p_spot_numbers) loop
    select * into v_spot from public.takeover_spots where spot_number=p_spot_numbers[v_i];
    v_bid:=trunc(p_bid_levels[v_i]);
    if p_kind='defend' then v_charge:=v_bid-v_spot.current_price;
    elsif v_spot.owner_user_id=v_uid then v_bid:=v_spot.current_price; v_charge:=0;
    else v_charge:=v_bid; end if;
    insert into public.takeover_attempt_items(attempt_id,spot_number,bid_level,charge_amount) values(v_attempt,v_spot.spot_number,v_bid,v_charge);
  end loop;
  return query select v_attempt,v_total;
end;
$function$
;

-- Trigger functions are invoked by triggers, never by API clients.
revoke execute on function public.enforce_takeover_saved_design_limit() from public, anon, authenticated;
revoke execute on function public.takeover_capture_spot_history() from public, anon, authenticated;
revoke execute on function public.touch_takeover_saved_design() from public, anon, authenticated;

-- Only Stripe reconciliation may expire a linked Checkout session.
CREATE OR REPLACE FUNCTION public.takeover_housekeeping()
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
declare
  v_expired integer:=0; v_shields integer:=0; v_notices integer:=0; v_emails integer:=0; v_unpaid integer:=0; v_email_recovered integer:=0;
begin
  update public.takeover_attempts
  set status='cancelled',failure_reason=coalesce(failure_reason,'Checkout expired before payment completed'),updated_at=now()
  where status='created' and stripe_checkout_session_id is null and stripe_payment_intent_id is null and created_at<now()-interval '2 hours';
  get diagnostics v_expired=row_count;

  update public.takeover_config set page_shield_until=null,updated_at=now()
  where singleton=true and page_shield_until is not null and page_shield_until<=now();
  get diagnostics v_shields=row_count;

  update public.takeover_email_outbox
  set status='pending',next_attempt_at=now(),updated_at=now(),last_error=coalesce(last_error,'Recovered after interrupted email worker')
  where status='sending' and updated_at<now()-interval '10 minutes';
  get diagnostics v_email_recovered=row_count;

  delete from public.takeover_attempts where status in ('cancelled','failed') and stripe_payment_intent_id is null and created_at<now()-interval '30 days';
  get diagnostics v_unpaid=row_count;

  delete from public.takeover_notifications where read_at is not null and created_at<now()-interval '180 days';
  get diagnostics v_notices=row_count;

  delete from public.takeover_email_outbox where sent_at is not null and sent_at<now()-interval '90 days';
  get diagnostics v_emails=row_count;

  return jsonb_build_object('expired_attempts',v_expired,'expired_shields',v_shields,'recovered_email_claims',v_email_recovered,'old_unpaid_attempts',v_unpaid,'old_notifications',v_notices,'old_emails',v_emails);
end;$function$
;

alter policy takeover_saved_designs_select_own on public.takeover_saved_designs using (user_id=(select auth.uid())) ;
alter policy takeover_saved_designs_insert_own on public.takeover_saved_designs  with check (user_id=(select auth.uid()));
alter policy takeover_saved_designs_update_own on public.takeover_saved_designs using (user_id=(select auth.uid())) with check (user_id=(select auth.uid()));
alter policy takeover_saved_designs_delete_own on public.takeover_saved_designs using (user_id=(select auth.uid())) ;
