from pathlib import Path

def between(text,start,end,new):
    i=text.index(start); j=text.index(end,i); return text[:i]+new+text[j:]

p=Path('takeover-v3.js'); s=p.read_text()
restore=r'''async function restoreSpotHistory(id,row,fullMedia){const mediaWarning=fullMedia?'':`\n\nThis snapshot is older than the current ${config.storage_retention_days||30}-day media protection window. Text, owner and price can still restore, but an unused old image may already have been cleaned.`;const shieldWarning=shieldActive()?'\n\nRestoring a historical state will cancel the active full-page protection shield.':'';if(!confirm(`Restore Spot ${String(row.spot_number).padStart(2,'0')} to ${row.company_name||'AVAILABLE'} at ${cash(row.current_price||0)}?${mediaWarning}${shieldWarning}`))return;const note=$('#adminSpotNote').value.trim()||null,{error}=await sb.rpc('admin_restore_takeover_spot',{p_history_id:id,p_note:note});if(error)return toast(error.message);await refreshSpotControl(`Spot ${row.spot_number} restored`)}'''
s=between(s,'async function restoreSpotHistory(','\nasync function renderSpotControlHistory',restore)
p.write_text(s)
print('V22 restore warning fixed')
