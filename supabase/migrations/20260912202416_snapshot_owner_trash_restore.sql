alter table public.takeover_daily_snapshots add column deleted_at timestamptz;
drop policy daily_snapshots_public_read on public.takeover_daily_snapshots;
create policy daily_snapshots_public_read on public.takeover_daily_snapshots for select to anon,authenticated using(deleted_at is null);
create policy daily_snapshots_owner_read on public.takeover_daily_snapshots for select to authenticated using((select public.is_takeover_admin()));

create or replace function public.manage_takeover_snapshot(p_date date,p_action text)
returns boolean language plpgsql security definer set search_path='' as $$
declare v_uid uuid:=auth.uid(); v_deleted timestamptz;
begin
  if v_uid is null or not public.is_takeover_admin()
    or (select count(*) from public.spot_owners)<>1 then
    raise exception 'Owner access required' using errcode='42501';
  end if;
  if p_action is null or p_action not in ('trash','restore') then raise exception 'Invalid snapshot action'; end if;
  select deleted_at into v_deleted from public.takeover_daily_snapshots where snapshot_date=p_date for update;
  if not found then raise exception 'Snapshot not found'; end if;
  if (p_action='trash' and v_deleted is not null) or (p_action='restore' and v_deleted is null) then return true; end if;
  update public.takeover_daily_snapshots set deleted_at=case when p_action='trash' then clock_timestamp() else null end where snapshot_date=p_date;
  insert into public.takeover_admin_events(admin_user_id,action,details)
    values(v_uid,'snapshot_'||p_action,jsonb_build_object('snapshot_date',p_date));
  return true;
end;
$$;
revoke all on function public.manage_takeover_snapshot(date,text) from public,anon;
grant execute on function public.manage_takeover_snapshot(date,text) to authenticated;
