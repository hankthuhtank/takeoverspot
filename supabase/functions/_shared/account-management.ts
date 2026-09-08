// Invoked only after the admin console verifies the single owner using getUser.
export async function manageAccount(admin,actor,body){
  const id=String(body.user_id||''),action=String(body.action||'');
  if(!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(id))throw new Error('Invalid account');
  if(id===actor)throw new Error('Your owner account is protected');
  const {data:owners,error:ownerError}=await admin.from('spot_owners').select('user_id').eq('user_id',id);
  if(ownerError)throw ownerError;if(owners?.length)throw new Error('Owner accounts are protected');
  const {data:target,error:userError}=await admin.auth.admin.getUserById(id);if(userError||!target?.user)throw new Error('Account not found');
  const {data:blockers,error:blockError}=await admin.rpc('takeover_account_deletion_blockers',{p_user_id:id});if(blockError)throw blockError;
  if(action==='account_status'){
    const {data:control,error}=await admin.from('takeover_account_controls').select('disabled,note').eq('user_id',id).maybeSingle();if(error)throw error;
    return{ok:true,user_id:id,email:target.user.email||'',disabled:!!control?.disabled||new Date(target.user.banned_until||0).getTime()>Date.now(),blockers,can_delete:!!blockers&&!Object.values(blockers).some(Boolean)};
  }
  const note=String(body.note||'').trim().slice(0,500);
  if(action==='account_delete'&&(body.confirm_email!==target.user.email||body.confirmation!=='DELETE'))throw new Error('Type DELETE and confirm the selected email');
  if(action==='account_delete'&&(!blockers||Object.values(blockers).some(Boolean)))throw new Error('This account has protected records or uploads. Disable access instead.');
  if(!['account_disable','account_restore','account_delete'].includes(action))throw new Error('Unknown account action');
  const disabled=action!=='account_restore';
  // Reserve an audit entry before making a change. Do not log credentials or emails.
  const {data:event,error:auditError}=await admin.from('takeover_admin_events').insert({admin_user_id:actor,action:action+'_requested',details:{target_user_id:id,note}}).select('id').single();if(auditError)throw auditError;
  if(disabled){const {error}=await admin.from('takeover_account_controls').upsert({user_id:id,disabled:true,updated_by:actor,updated_at:new Date().toISOString(),note});if(error)throw error;}
  const {error:banError}=await admin.auth.admin.updateUserById(id,{ban_duration:disabled?'876000h':'none'});if(banError)throw new Error('Account change needs retry: '+banError.message);
  if(!disabled){const {error}=await admin.from('takeover_account_controls').upsert({user_id:id,disabled:false,updated_by:actor,updated_at:new Date().toISOString(),note});if(error)throw error;}
  if(action==='account_delete'){const {error}=await admin.auth.admin.deleteUser(id,false);if(error)throw new Error('Account remains disabled; deletion was blocked: '+error.message);}
  const {error:finishError}=await admin.from('takeover_admin_events').update({action,details:{target_user_id:id,note,completed:true}}).eq('id',event.id);
  return{ok:true,action,user_id:id,audit_warning:!!finishError};
}
