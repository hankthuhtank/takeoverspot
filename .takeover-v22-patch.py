from pathlib import Path


def between(text,start,end,new):
    i=text.index(start)
    j=text.index(end,i)
    return text[:i]+new+text[j:]

# INDEX
p=Path('index.html'); s=p.read_text()
s=s.replace("script-src 'self' https://cdn.jsdelivr.net;","script-src 'self';")
s=s.replace('<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>','<script src="vendor/supabase-2.112.4.min.js"></script>')
s=s.replace('<script src="boot.js?v=17"></script>','<script src="boot.js?v=18"></script>')
refund='''<section class="panel modal moderation-modal" id="refundModal">
  <div class="panel-inner">
    <div class="panel-head"><div><span>OWNER REFUND</span><h2 id="refundTitle">Refund a purchase.</h2></div><button class="close" data-close>×</button></div>
    <div class="moderation-policy"><b>MONEY MOVES THROUGH STRIPE.</b><p>Issue a full or partial refund here. Money and territory are separate: a refund does not change the board unless you deliberately choose a safe territory action below.</p></div>
    <div class="field"><label>REFUND AMOUNT</label><input id="refundAmount" type="number" min="0.01" step="0.01"></div>
    <div class="field"><label>REASON</label><select id="refundReason"><option value="">Choose a reason</option><option value="customer_request">Customer request</option><option value="duplicate">Duplicate charge</option><option value="fraud_suspected">Fraud suspected</option><option value="service_issue">TAKEOVER service issue</option><option value="goodwill">Goodwill / courtesy</option><option value="other">Other</option></select></div>
    <div class="field"><label>PRIVATE NOTE · OPTIONAL</label><textarea id="refundNote" maxlength="500" placeholder="Internal note. Required if you choose Other."></textarea></div>
    <div class="field"><label>TERRITORY AFTER A FULL REFUND</label><select id="refundTerritoryAction"><option value="none">REFUND ONLY · LEAVE TERRITORY AS-IS</option><option value="restore_previous">RESTORE PREVIOUS OWNER / STATE</option><option value="vacate_keep_price">VACATE · KEEP CURRENT MARKET PRICE</option></select></div>
    <p class="hint" id="refundHint">Territory actions require the full remaining refund and affect only spots still tied to this exact payment. Refunds can no longer reset a spot to $1 from this screen.</p>
    <button class="action danger" id="confirmRefund">ISSUE REFUND</button>
    <button class="secondary" id="refundCancel">CANCEL</button>
  </div>
</section>'''
s=between(s,'<section class="panel modal moderation-modal" id="refundModal">','\n\n<div class="toast" id="toast">',refund)
p.write_text(s)

# BOOT
p=Path('boot.js'); s=p.read_text()
s=s.replace("(()=>{'use strict';","(()=>{'use strict';\nif(window.self!==window.top){document.documentElement.innerHTML='';return}")
s=s.replace("takeover-v3.css?v=21","takeover-v3.css?v=22").replace("takeover-v3.js?v=21","takeover-v3.js?v=22")
p.write_text(s)

# MAIN JS
p=Path('takeover-v3.js'); s=p.read_text()
old="if(error)throw error;return sb.storage.from(bucket).getPublicUrl(path).data.publicUrl"
new="if(error){if(/row-level security|policy|not permitted/i.test(error.message||''))throw new Error('Upload limit reached or this upload is not permitted for your account. Reuse a saved design or contact TAKEOVER support.');throw error}return sb.storage.from(bucket).getPublicUrl(path).data.publicUrl"
assert old in s
s=s.replace(old,new,1)
restore='''async function restoreSpotHistory(id,row,fullMedia){const mediaWarning=fullMedia?'':`\n\nThis snapshot is older than the current ${config.storage_retention_days||30}-day media protection window. Text, owner and price can still restore, but an unused old image may already have been cleaned.`;const shieldWarning=shieldActive()?'\n\nRestoring a historical state will cancel the active full-page protection shield.':'';if(!confirm(`Restore Spot ${String(row.spot_number).padStart(2,'0')} to ${row.company_name||'AVAILABLE'} at ${cash(row.current_price||0)}?${mediaWarning}${shieldWarning}`))return;const note=$('#adminSpotNote').value.trim()||null,{error}=await sb.rpc('admin_restore_takeover_spot',{p_history_id:id,p_note:note});if(error)return toast(error.message);await refreshSpotControl(`Spot ${row.spot_number} restored`)}'''
s=between(s,'async function restoreSpotHistory(','\nasync function renderSpotControlHistory',restore)
refund_js='''async function openRefund(id,company,kind){refundAttempt={id,kind,company};const {data,error}=await sb.rpc('admin_refund_summary',{p_attempt_id:id});if(error)return toast(error.message);const row=Array.isArray(data)?data[0]:data;if(!row||Number(row.remaining_refundable)<=0)return toast('Nothing remains to refund');$('#refundTitle').textContent=`Refund ${company||'purchase'}?`;$('#refundAmount').value=Number(row.remaining_refundable).toFixed(2);$('#refundAmount').max=Number(row.remaining_refundable).toFixed(2);$('#refundReason').value='';$('#refundNote').value='';$('#refundTerritoryAction').value='none';$('#refundTerritoryAction').disabled=kind!=='takeover';openPanel('#refundModal')}
if($('#confirmRefund'))$('#confirmRefund').onclick=async()=>{if(!refundAttempt)return;const amount=Math.round(Number($('#refundAmount').value||0)*100),reason=$('#refundReason').value,note=$('#refundNote').value.trim(),territoryAction=$('#refundTerritoryAction')?.value||'none';if(amount<1)return toast('Enter a refund amount');if(!reason)return toast('Choose a refund reason');if(reason==='other'&&!note)return toast('Add a short note for Other');const b=$('#confirmRefund'),old=b.textContent;b.disabled=true;b.textContent='REFUNDING…';const {data,error}=await sb.functions.invoke('takeover-admin-refund',{body:{attempt_id:refundAttempt.id,amount_cents:amount,reason,note:note||null,territory_action:territoryAction}});b.disabled=false;b.textContent=old;if(error||data?.error)return toast(data?.error||error?.message||'Refund failed');const changed=Number(data?.territory?.restored||0)+Number(data?.territory?.vacated||0);toast(data?.territory_error?'Refund issued · territory needs manual review':changed?`Refunded ${cash(data.amount)} · ${changed} spot${changed===1?'':'s'} updated`:`Refunded ${cash(data.amount)}`);refundAttempt=null;closePanels();await refreshBoard();await renderAdmin();openPanel('#adminPanel')};if($('#refundCancel'))$('#refundCancel').onclick=()=>{refundAttempt=null;closePanels()};'''
s=between(s,'async function openRefund(','\n\n\nfunction saveRevealDraft',refund_js+'\n\n')
s=s.replace("['no_failed_emails','EMAIL QUEUE']]","['no_failed_emails','EMAIL QUEUE'],['reconcile_worker','RECONCILIATION WORKER']]")
p.write_text(s)

# DESKTOP READABILITY
p=Path('takeover-v3.css'); s=p.read_text()
marker='/* TAKEOVER V22 DESKTOP READABILITY */'
if marker not in s:
    s+='''\n\n/* TAKEOVER V22 DESKTOP READABILITY */
@media(min-width:1100px){
.identity{min-height:62px!important;padding:13px 18px!important;gap:22px!important}.identity>b{font-size:20px!important}.identity>span{font-size:11px!important;letter-spacing:.025em}.social-pulse strong{font-size:10px!important}.social-pulse a{font-size:11px!important}.chrome-btn{font-size:11px!important;padding:12px 14px!important}.available-cell span{font-size:11px!important;letter-spacing:.08em}.available-cell b{font-size:16px!important;margin-top:5px!important}.take-pill{font-size:11px!important;padding:10px 12px!important}.site-legal a{font-size:8px!important;padding:6px 8px!important}
}
@media(min-width:901px){
.panel-inner{font-size:15px}.panel-head span{font-size:11px!important}.panel-head h2{font-size:30px!important;line-height:1.08!important}.hint,.rules-copy{font-size:12px!important;line-height:1.55!important}.field>label{font-size:10px!important;letter-spacing:.08em}.field input,.field textarea,.field select{font-size:16px!important}.selector-title b{font-size:13px!important}.selector-title small{font-size:11px!important;line-height:1.4!important}.mini-spot{font-size:11px!important}.mini-spot b{font-size:13px!important}.bid-row>span>b{font-size:14px!important}.bid-row small{font-size:11px!important}.bid-row input{font-size:17px!important}.summary>span{font-size:10px!important}.summary>b{font-size:32px!important}.purchase-assent span{font-size:11px!important;line-height:1.5!important}.action,.secondary{font-size:13px!important}.logo-drop span{font-size:12px!important}.canvas-purchase-head b{font-size:15px!important}.canvas-purchase-head span{font-size:11px!important}.admin-row b{font-size:13px!important}.admin-row small{font-size:10px!important;line-height:1.4!important}.admin-block-head b{font-size:13px!important}.admin-block-head span{font-size:10.5px!important}
}
'''
p.write_text(s)

# CI V22
ci="""name: TAKEOVER V22 Smoke Test
'on':
  push:
    branches: [main]
    paths: ['index.html','takeover-v3.js','takeover-v3.css','takeover.css','boot.js','vendor/supabase-2.112.4.min.js','contact.js','contact.html','terms.html','auction-rules.html','payments.html','privacy.html','content-policy.html','.github/workflows/ci-v18.yml']
  pull_request:
    paths: ['index.html','takeover-v3.js','takeover-v3.css','takeover.css','boot.js','vendor/supabase-2.112.4.min.js','contact.js','contact.html','terms.html','auction-rules.html','payments.html','privacy.html','content-policy.html']
permissions:
  contents: read
jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - name: Syntax
        run: |
          node --check takeover-v3.js
          node --check boot.js
          node --check contact.js
      - name: V22 architecture
        run: |
          grep -q 'const TOTAL=16' takeover-v3.js
          grep -q 'takeover-v3.js?v=22' boot.js
          grep -q 'takeover-v3.css?v=22' boot.js
          grep -q 'boot.js?v=18' index.html
          grep -q 'vendor/supabase-2.112.4.min.js' index.html
          test -s vendor/supabase-2.112.4.min.js
          ! grep -q 'cdn.jsdelivr.net/npm/@supabase/supabase-js@2' index.html
          grep -q 'window.self!==window.top' boot.js
          grep -q 'TAKEOVER V22 DESKTOP READABILITY' takeover-v3.css
      - name: Core product contracts
        run: |
          grep -q 'frameCells' takeover-v3.js
          grep -q 'startLayerTouch' takeover-v3.js
          grep -q 'Particle Field' takeover-v3.js
          grep -q 'SAVE TO MY LIBRARY' takeover-v3.js
          grep -q 'REMOVE LOGO' takeover-v3.js
          grep -q 'anonymous to visitors' takeover-v3.js
          grep -q 'takeover_spot_history' takeover-v3.js
          grep -q 'admin_restore_takeover_spot' takeover-v3.js
          grep -q 'admin_set_takeover_spot_price' takeover-v3.js
          grep -q 'admin_vacate_takeover_spot' takeover-v3.js
          grep -q 'admin_hide_takeover_spot_content' takeover-v3.js
      - name: Refund safety regression
        run: |
          grep -q 'refundTerritoryAction' index.html
          grep -q 'restore_previous' takeover-v3.js
          grep -q 'vacate_keep_price' takeover-v3.js
          ! grep -q 'refundResetTerritory' index.html
          ! grep -q 'refundResetTerritory' takeover-v3.js
          ! grep -q 'reset_territory:reset' takeover-v3.js
      - name: Optional link and canvas regression
        run: |
          node - <<'JS'
          const fs=require('fs'),s=fs.readFileSync('takeover-v3.js','utf8');
          if(!s.includes("interactive&&link?'a':'div'")) throw Error('linkless territories are no longer display-only');
          if(s.includes("if(!website)return toast('Enter your website')")) throw Error('website became mandatory');
          if(!s.includes("layer.size=clamp(editorTouchGesture.os*scale,8,96)")) throw Error('text pinch regression');
          if(!s.includes('raw=await f.arrayBuffer()')) throw Error('mobile upload hardening missing');
          console.log('PASS PRODUCT REGRESSIONS');
          JS
      - name: Legal contract
        run: |
          grep -q 'THE WEBPAGE BELONGS TO WHOEVER WANTS IT MOST.' auction-rules.html
          grep -qi 'Future seasons and historical archives' terms.html
          ! grep -qi 'season' index.html
          ! grep -qi 'season' auction-rules.html
          ! grep -qi 'season' payments.html
          ! grep -qi 'archive' privacy.html
          grep -q 'Placement has no guaranteed minimum duration or cash value.' index.html
      - name: Repo hygiene
        run: |
          test ! -e launch.js
          test ! -e launch.css
          test ! -e polish.js
          test ! -e polish.css
          test ! -e takeover-v2.js
"""
Path('.github/workflows/ci-v18.yml').write_text(ci)

for dead in ['launch.js','launch.css','polish.js','polish.css','takeover-v2.js']:
    q=Path(dead)
    if q.exists(): q.unlink()

print('V22 patch applied')
