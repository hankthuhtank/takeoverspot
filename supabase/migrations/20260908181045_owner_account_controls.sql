create table public.takeover_account_controls (
  user_id uuid primary key references auth.users(id) on delete cascade,
  disabled boolean not null default false,
  updated_at timestamptz not null default now(),
  updated_by uuid references auth.users(id),
  note text check(length(note)<=500)
);
alter table public.takeover_account_controls enable row level security;
revoke all on public.takeover_account_controls from anon,authenticated;
grant select on public.takeover_account_controls to authenticated;
grant all on public.takeover_account_controls to service_role;
create policy account_controls_read on public.takeover_account_controls for select to authenticated
  using(user_id=(select auth.uid()) or public.is_takeover_admin());

create or replace function private.takeover_account_enabled()
returns boolean language sql stable security definer set search_path='' as $$
  select auth.uid() is not null and not exists(select 1 from public.takeover_account_controls where user_id=auth.uid() and disabled);
$$;
revoke all on function private.takeover_account_enabled() from public,anon;
grant execute on function private.takeover_account_enabled() to authenticated,service_role;
create policy saved_design_active_insert on public.takeover_saved_designs as restrictive for insert to authenticated with check((select private.takeover_account_enabled()));
create policy saved_design_active_update on public.takeover_saved_designs as restrictive for update to authenticated using((select private.takeover_account_enabled())) with check((select private.takeover_account_enabled()));
create policy saved_design_active_delete on public.takeover_saved_designs as restrictive for delete to authenticated using((select private.takeover_account_enabled()));
create policy profile_active_update on public.takeover_profiles as restrictive for update to authenticated using((select private.takeover_account_enabled())) with check((select private.takeover_account_enabled()));

create or replace function public.takeover_account_deletion_blockers(p_user_id uuid)
returns jsonb language sql stable security definer set search_path='' as $$
  select jsonb_build_object(
    'owner',exists(select 1 from public.spot_owners where user_id=p_user_id),
    'board',exists(select 1 from public.takeover_spots where owner_user_id=p_user_id),
    'payments',exists(select 1 from public.takeover_attempts where user_id=p_user_id),
    'billing',exists(select 1 from public.billing_profiles where user_id=p_user_id),
    'legacy_bids',exists(select 1 from public.bids where bidder_id=p_user_id),
    'legacy_winners',exists(select 1 from public.auction_winners where bidder_id=p_user_id),
    'uploads',exists(select 1 from storage.objects where owner_id=p_user_id::text or owner=p_user_id)
  );
$$;
revoke all on function public.takeover_account_deletion_blockers(uuid) from public,anon,authenticated;
grant execute on function public.takeover_account_deletion_blockers(uuid) to service_role;

-- Enforce this at deletion time too, preventing cascades from erasing purchases.
create or replace function private.guard_takeover_account_deletion()
returns trigger language plpgsql security definer set search_path='' as $$
begin
  if exists(select 1 from jsonb_each(public.takeover_account_deletion_blockers(old.id)) where value='true'::jsonb) then
    raise exception 'Account has protected records; disable access instead';
  end if;
  return old;
end;
$$;
revoke all on function private.guard_takeover_account_deletion() from public,anon,authenticated;
create trigger protect_takeover_accounts before delete on auth.users for each row execute function private.guard_takeover_account_deletion();

create or replace function private.protect_takeover_owner_control()
returns trigger language plpgsql security definer set search_path='' as $$
begin
  if new.disabled and exists(select 1 from public.spot_owners where user_id=new.user_id) then raise exception 'Owner account cannot be disabled'; end if;
  return new;
end;
$$;
revoke all on function private.protect_takeover_owner_control() from public,anon,authenticated;
create trigger protect_takeover_owner before insert or update on public.takeover_account_controls for each row execute function private.protect_takeover_owner_control();

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
  if exists(select 1 from public.takeover_account_controls where user_id=v_uid and disabled) then raise exception 'This account is disabled. Contact support.'; end if;
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

CREATE OR REPLACE FUNCTION public.update_takeover_canvas(p_creative_id uuid, p_company_name text, p_website text, p_canvas_json jsonb)
 RETURNS boolean
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
declare v_uid uuid:=auth.uid(); v_company text:=trim(coalesce(p_company_name,'')); v_site text:=trim(coalesce(p_website,'')); v_canvas jsonb:=coalesce(p_canvas_json,'{}'::jsonb);
begin
  if exists(select 1 from public.takeover_account_controls where user_id=v_uid and disabled) then raise exception 'This account is disabled. Contact support.'; end if;
  if v_uid is null then raise exception 'Sign in first'; end if;
  if p_creative_id is null then raise exception 'Creative not found'; end if;
  if v_company='' or length(v_company)>80 then raise exception 'Enter a name / brand'; end if;
  if length(v_site)>300 or (v_site<>'' and v_site !~* '^https?://[^[:space:]]+$') then raise exception 'Enter a valid http(s) link or leave it blank'; end if;
  if jsonb_typeof(v_canvas)<>'object' or octet_length(v_canvas::text)>40000 then raise exception 'Creative design is invalid or too large'; end if;
  if jsonb_typeof(v_canvas->'layers')='array' and jsonb_array_length(v_canvas->'layers')>40 then raise exception 'Creative design has too many layers'; end if;
  if not public.takeover_canvas_assets_owned(v_uid,v_canvas) then raise exception 'Creative images must come from your own TAKEOVER uploads'; end if;
  if not exists(select 1 from public.takeover_spots where creative_id=p_creative_id and owner_user_id=v_uid) then raise exception 'You do not own this territory'; end if;
  update public.takeover_spots set company_name=v_company,website=v_site,canvas_json=v_canvas,updated_at=now() where creative_id=p_creative_id and owner_user_id=v_uid;
  update public.takeover_profiles set company_name=v_company,website=v_site,updated_at=now() where user_id=v_uid;
  return true;
end;
$function$

;

CREATE OR REPLACE FUNCTION public.takeover_storage_upload_allowed(p_bucket text, p_name text, p_metadata jsonb)
 RETURNS boolean
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public', 'storage'
AS $function$
declare
  v_uid uuid:=auth.uid();
  v_count integer:=0;
  v_bytes bigint:=0;
  v_minute integer:=0;
  v_hour integer:=0;
  v_new_size bigint:=4194304;
begin
  if exists(select 1 from public.takeover_account_controls where user_id=v_uid and disabled) then return false; end if;
  if v_uid is null then return false; end if;
  if p_bucket not in ('takeover-creative','takeover-logos') then return false; end if;
  if split_part(coalesce(p_name,''),'/',1)<>v_uid::text then return false; end if;
  begin
    v_new_size:=coalesce(nullif(p_metadata->>'size','')::bigint,nullif(p_metadata->>'contentLength','')::bigint,4194304);
  exception when others then
    v_new_size:=4194304;
  end;
  if v_new_size<1 or v_new_size>4194304 then return false; end if;

  select count(*),
         coalesce(sum(coalesce(nullif(metadata->>'size','')::bigint,nullif(metadata->>'contentLength','')::bigint,0)),0),
         count(*) filter(where created_at>now()-interval '1 minute'),
         count(*) filter(where created_at>now()-interval '1 hour')
  into v_count,v_bytes,v_minute,v_hour
  from storage.objects
  where bucket_id in ('takeover-creative','takeover-logos')
    and split_part(name,'/',1)=v_uid::text;

  if v_count>=120 then return false; end if;
  if v_bytes+v_new_size>104857600 then return false; end if;
  if v_minute>=12 or v_hour>=60 then return false; end if;
  return true;
end;
$function$

;
