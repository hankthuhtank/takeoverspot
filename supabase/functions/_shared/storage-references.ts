// Cleanup must stop if any source is unavailable or pagination is incomplete.
export async function readAllRows(makeQuery) {
  const rows = [];
  for (let offset = 0; offset < 100000; offset += 500) {
    const { data, error, count } = await makeQuery().range(offset, offset + 499);
    if (error) throw new Error('Storage reference read failed: ' + error.message);
    if (!Array.isArray(data) || !Number.isInteger(count)) throw new Error('Storage reference count unavailable');
    rows.push(...data);
    if (data.length < 500 || rows.length === count) {
      if (rows.length !== count) throw new Error('Storage reference scan was incomplete; no files deleted');
      return rows;
    }
  }
  throw new Error('Storage reference scan exceeded its safe limit; no files deleted');
}

export async function storageReferences(admin) {
  const { data: config, error } = await admin.from('takeover_config').select('storage_retention_days').eq('singleton', true).single();
  if (error || !config || !Number.isFinite(Number(config.storage_retention_days))) throw new Error('Storage retention settings unavailable; no files deleted');
  const days = Math.max(7, Math.min(365, Number(config.storage_retention_days)));
  const cutoff = Date.now() - days * 86400000;
  const since = new Date(cutoff).toISOString();
  const sources = [
    ['takeover_spots', 'spot_number', 'logo_url,feature_image_url,canvas_json', q => q.not('owner_key', 'is', null)],
    ['takeover_profiles', 'user_id', 'logo_url,feature_image_url', q => q],
    ['takeover_attempts', 'id', 'logo_url,feature_image_url,canvas_json,created_at', q => q.gte('created_at', since)],
    ['takeover_saved_designs', 'id', 'user_id,logo_url,canvas_json', q => q],
    ['takeover_spot_history', 'id', 'logo_url,feature_image_url,canvas_json,created_at', q => q.gte('created_at', since)],
  ];
  const [spots, profiles, attempts, saved, history] = await Promise.all(sources.map(([table, key, columns, filter]) =>
    readAllRows(() => filter(admin.from(table).select(columns, { count: 'exact' }).order(key)))
  ));
  return { days, cutoff, spots, profiles, attempts, saved, history };
}
