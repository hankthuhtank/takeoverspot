create table public.takeover_daily_snapshots (
  snapshot_date date primary key,
  scheduled_at timestamptz not null,
  captured_at timestamptz not null default clock_timestamp(),
  board_json jsonb not null check(jsonb_typeof(board_json)='array' and jsonb_array_length(board_json)=16),
  config_json jsonb not null check(jsonb_typeof(config_json)='object'),
  image_path text unique,
  image_bytes integer check(image_bytes between 1 and 1048576),
  rendered_at timestamptz,
  check(snapshot_date=(scheduled_at at time zone 'America/Chicago')::date),
  check((scheduled_at at time zone 'America/Chicago')::time='12:00:00'::time),
  check(image_path is null or image_path=snapshot_date::text||'.jpg')
);
alter table public.takeover_daily_snapshots enable row level security;
revoke all on public.takeover_daily_snapshots from anon,authenticated;
grant select on public.takeover_daily_snapshots to anon,authenticated;
grant all on public.takeover_daily_snapshots to service_role;
create policy daily_snapshots_public_read on public.takeover_daily_snapshots for select to anon,authenticated using(true);

create or replace function private.capture_takeover_daily_snapshot()
returns date language plpgsql security definer set search_path='' as $$
declare
  v_local timestamp:=clock_timestamp() at time zone 'America/Chicago';
  v_day date:=v_local::date;
  v_config jsonb;
  v_board jsonb;
begin
  -- UTC scheduler covers both CDT and CST; the IANA zone chooses the correct hour.
  if extract(hour from v_local)<>12 then return null; end if;
  if exists(select 1 from public.takeover_daily_snapshots where snapshot_date=v_day) then return v_day; end if;
  if not pg_try_advisory_xact_lock(hashtextextended('takeover-daily-snapshot',0)) then return null; end if;
  -- Checkout completion locks this row too, so a multi-spot purchase is one state.
  select jsonb_build_object('starting_price',starting_price,'min_increment',min_increment,'page_shield_until',page_shield_until)
    into v_config from public.takeover_config where singleton=true for share;
  if v_config is null then raise exception 'Snapshot settings unavailable'; end if;
  select jsonb_agg(jsonb_build_object(
    'spot_number',spot_number,'current_price',current_price,'owner_key',owner_key,
    'company_name',company_name,'website',website,'logo_url',logo_url,
    'creative_id',creative_id,'canvas_json',canvas_json,'owner_since',owner_since,'updated_at',updated_at
  ) order by spot_number) into v_board from public.takeover_spots;
  if v_board is null or jsonb_array_length(v_board)<>16 then raise exception 'Snapshot requires the complete board'; end if;
  insert into public.takeover_daily_snapshots(snapshot_date,scheduled_at,captured_at,board_json,config_json)
    values(v_day,(v_day+time '12:00') at time zone 'America/Chicago',clock_timestamp(),v_board,v_config)
    on conflict(snapshot_date) do nothing;
  return v_day;
end;
$$;
revoke all on function private.capture_takeover_daily_snapshot() from public,anon,authenticated;
grant execute on function private.capture_takeover_daily_snapshot() to service_role;

create or replace function private.protect_takeover_daily_snapshot()
returns trigger language plpgsql set search_path='' as $$
begin
  if (new.snapshot_date,new.scheduled_at,new.captured_at,new.board_json,new.config_json)
    is distinct from (old.snapshot_date,old.scheduled_at,old.captured_at,old.board_json,old.config_json)
    or (old.image_path is not null and (new.image_path,new.image_bytes,new.rendered_at)
      is distinct from (old.image_path,old.image_bytes,old.rendered_at)) then
    raise exception 'Daily snapshots cannot be rewritten';
  end if;
  return new;
end;
$$;
revoke all on function private.protect_takeover_daily_snapshot() from public,anon,authenticated;
create trigger daily_snapshot_immutable before update on public.takeover_daily_snapshots
  for each row execute function private.protect_takeover_daily_snapshot();

insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
  values('takeover-daily-snapshots','takeover-daily-snapshots',true,1048576,array['image/jpeg']);
-- No client write/list policies: the verified renderer uses a service credential.
select cron.schedule('takeover-daily-snapshot-noon-central','* 17,18 * * *','select private.capture_takeover_daily_snapshot();');
