from pathlib import Path

js_path=Path('takeover-v3.js')
css_path=Path('takeover-v3.css')
boot_path=Path('boot.js')
index_path=Path('index.html')
js=js_path.read_text()
css=css_path.read_text()
boot=boot_path.read_text()
index=index_path.read_text()

old="async function openRefund(id,company,kind){refundAttempt={id,kind,company};const {data,error}=await sb.rpc('admin_refund_summary',{p_attempt_id:id});if(error)return toast(error.message);const row=Array.isArray(data)?data[0]:data;if(!row||Number(row.remaining_refundable)<=0)return toast('Nothing remains to refund');$('#refundTitle').textContent=`Refund ${company||'purchase'}?`;$('#refundAmount').value=Number(row.remaining_refundable).toFixed(2);$('#refundAmount').max=Number(row.remaining_refundable).toFixed(2);$('#refundReason').value='';$('#refundNote').value='';$('#refundTerritoryAction').value='none';$('#refundTerritoryAction').disabled=kind!=='takeover';openPanel('#refundModal')}"
new="function syncRefundTerritoryAction(){const sel=$('#refundTerritoryAction'),hint=$('#refundHint');if(!sel||!refundAttempt)return;const remaining=Number(refundAttempt.remaining||0),amount=Number($('#refundAmount')?.value||0),full=Math.abs(amount-remaining)<.005,takeover=refundAttempt.kind==='takeover';sel.disabled=!takeover||!full;if(!takeover||!full)sel.value='none';else if(sel.value==='none')sel.value='restore_previous';if(hint)hint.textContent=!takeover?'This purchase has no territory to change.':full?'Full refunds default to restoring the exact previous owner/state. You can still choose refund-only or vacate while preserving the market level.':'Partial refunds leave territory unchanged. Refund the full remaining amount to enable restore/vacate options.'}\nasync function openRefund(id,company,kind){refundAttempt={id,kind,company,remaining:0};const {data,error}=await sb.rpc('admin_refund_summary',{p_attempt_id:id});if(error)return toast(error.message);const row=Array.isArray(data)?data[0]:data;if(!row||Number(row.remaining_refundable)<=0)return toast('Nothing remains to refund');refundAttempt.remaining=Number(row.remaining_refundable);$('#refundTitle').textContent=`Refund ${company||'purchase'}?`;$('#refundAmount').value=Number(row.remaining_refundable).toFixed(2);$('#refundAmount').max=Number(row.remaining_refundable).toFixed(2);$('#refundReason').value='';$('#refundNote').value='';$('#refundTerritoryAction').value=kind==='takeover'?'restore_previous':'none';$('#refundAmount').oninput=syncRefundTerritoryAction;syncRefundTerritoryAction();openPanel('#refundModal')}"
assert old in js, 'openRefund target missing'
js=js.replace(old,new,1)

old_hint='<p class="hint" id="refundHint">Territory actions require the full remaining refund and affect only spots still tied to this exact payment. Refunds can no longer reset a spot to $1 from this screen.</p>'
new_hint='<p class="hint" id="refundHint">Full refunds default to restoring the exact previous owner/state. Partial refunds leave territory unchanged.</p>'
assert old_hint in index, 'refund hint target missing'
index=index.replace(old_hint,new_hint,1)

css += "\n\n/* TAKEOVER V22.3 — contain admin history previews */\n.spot-history-preview{position:relative!important;isolation:isolate!important}.spot-history-preview>.canvas-creative{position:absolute!important;inset:0!important;width:100%!important;height:100%!important;max-width:100%!important;max-height:100%!important;overflow:hidden!important}.spot-history-preview>.canvas-creative .canvas-layer{font-size:clamp(3px,var(--layer-size,5cqw),18px)!important}.spot-control-modal .panel-inner{position:relative!important;z-index:1!important}\n"

assert 'takeover-v3.css?v=22.2' in boot and 'takeover-v3.js?v=22.2' in boot, 'boot cache target missing'
boot=boot.replace('takeover-v3.css?v=22.2','takeover-v3.css?v=22.3',1).replace('takeover-v3.js?v=22.2','takeover-v3.js?v=22.3',1)

js_path.write_text(js)
css_path.write_text(css)
boot_path.write_text(boot)
index_path.write_text(index)
print('V22.3 admin/refund patch applied')
