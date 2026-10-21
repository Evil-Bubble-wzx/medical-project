'use strict';
// The audit page owns the session, safe text renderer and shared operation lock.
const development = {history:null, plan:null, loading:false, cases:[]};
const devBase = '/api/v1/validation/development';
function devSay(text, success=false) {
  $('#dev-message').textContent = text;
  $('#dev-message').classList.toggle('success', success);
}
function devControls() {
  const locked = state.busy || development.loading;
  $('#development').querySelectorAll('input, select, button').forEach(e => { e.disabled = locked; });
  $('#dev-plan').disabled = locked || !$('#dev-cases input:checked');
  $('#dev-prepare').disabled = locked || !development.plan;
  $('#dev-withdraw').disabled = locked || !$('#dev-version').value;
  $('#dev-rollback').disabled = locked || !$('#dev-target').value;
  $('#dev-releases').querySelectorAll('button').forEach(b => {
    b.disabled = locked || b.dataset.ready !== 'true';
  });
}
function devInvalidate() {
  development.plan = null; $('#dev-preview').hidden = true; devControls();
}
function devError(error) {
  const text = error.message || '操作未完成。';
  devSay(text + '\n当前操作人和原因仍保留。刷新版本状态后再核对，不会自动重试启用。');
}
function devShort(id) { return id ? id.slice(0,8) : '尚无'; }
function devRender(history, items) {
  development.history = history;
  development.cases = items.filter(i => i.kind === 'case' && i.case_kind !== 'boundary_manual_review' && i.state === 'submitted');
  $('#dev-current').textContent = history.active_snapshot_id ? `当前启用的开发快照：${history.active_snapshot_id}` : '当前尚无启用的开发快照。';
  const selected = new Set([...document.querySelectorAll('#dev-cases input:checked')].map(e => e.value));
  const cases = $('#dev-cases'); cases.replaceChildren();
  for (const item of development.cases) {
    const label = node('label'); const input = node('input'); input.type = 'checkbox'; input.value = item.item_id;
    input.checked = selected.has(item.item_id); input.addEventListener('change', devInvalidate);
    label.append(input, node('span', `${item.item_id} · ${topics[item.topic] || item.topic || '证据题'} · 已提交声明`)); cases.append(label);
  }
  if (!development.cases.length) cases.append(node('p', '暂无已提交声明的证据题。请先在上方完成来源和证据题审核。', 'audit-muted'));
  const releases = $('#dev-releases'); releases.replaceChildren();
  if (!history.releases.length) releases.append(node('p', '暂无开发资料准备记录。', 'audit-muted'));
  const operations = {include:'纳入资料', rollback:'回滚版本', withdraw:'撤回资料'};
  const statuses = {prepared:'正在准备或构建中断', indexed:'索引已准备完成', failed:'索引准备失败'};
  for (const release of history.releases) {
    const box = node('article', undefined, 'audit-history-event');
    const active = release.snapshot_id === history.active_snapshot_id;
    const ready = release.status === 'indexed' && release.base_snapshot_id === history.active_snapshot_id && !active;
    box.append(node('strong', `${operations[release.operation] || '开发版本'} · ${active ? '当前已启用' : statuses[release.status] || '状态待核对'}`));
    box.append(node('p', `快照：${release.snapshot_id}`));
    let details; try { details = JSON.parse(release.details); } catch { details = {}; }
    if (details.case_ids?.length) box.append(node('p', `所选题目：${details.case_ids.join('、')}`));
    if (details.restored_from) box.append(node('p', `回滚来源：${details.restored_from}`));
    if (details.withdrawn_version) box.append(node('p', `已撤回资料版本：${details.withdrawn_version}`));
    if (!active && release.status === 'indexed' && !ready) box.append(node('p', '当前版本已变化，请重新准备；此记录不能直接启用。', 'audit-muted'));
    const button = node('button', active ? '当前已启用':'启用此开发版本', 'audit-secondary'); button.type = 'button';
    button.dataset.ready = String(ready); button.dataset.snapshot = release.snapshot_id;
    button.addEventListener('click', () => devActivate(release)); box.append(button); releases.append(box);
  }
  function options(selector, placeholder, rows) {
    const select = $(selector); const value = select.value; select.replaceChildren();
    const first = node('option', placeholder); first.value = ''; select.append(first);
    for (const [id, label] of rows) { const option = node('option', label); option.value = id; select.append(option); }
    select.value = rows.some(([id]) => id === value) ? value : '';
  }
  options('#dev-version', '请选择资料', (history.active_versions || []).filter(v => v.state === 'draft').map(v => [v.version_id, `${v.title} · ${devShort(v.version_id)}`]));
  options('#dev-target', '请选择历史版本', (history.snapshots || []).filter(s => s.id !== history.active_snapshot_id).map(s => [s.id, `${new Date(s.created_at).toLocaleString()} · ${devShort(s.id)} · ${s.note}`]));
  devControls();
}
async function devLoad() {
  const [history, listing] = await Promise.all([api(devBase + '/history'), api(base + '/items')]);
  devRender(history, listing.items);
}
async function devRun(message, work) {
  if (state.busy || development.loading) return;
  development.loading = true; busy(true); devSay(message);
  try { await work(); }
  catch (error) { devError(error); }
  finally { development.loading = false; busy(false); }
}
function devOperator() {
  const actor = $('#dev-actor').value.trim(), note = $('#dev-note').value.trim();
  if (!actor || !note) { devSay('请先填写本次操作人和操作原因。'); return null; }
  return {actor, note};
}
function devSavedOnly() {
  if (!state.dirty) return true;
  devSay('上方审核意见有未保存修改，请先保存或重新载入后再操作开发资料版本。'); return false;
}
async function devActivate(release) {
  if (state.busy || !devSavedOnly()) return;
  const operator = devOperator(); if (!operator) return;
  if (!window.confirm(`将启用开发快照 ${release.snapshot_id}。检索将使用此版本，正式库不变。确认启用？`)) return;
  const expected = development.history.active_snapshot_id;
  await devRun('正在核对并启用开发版本…', async () => {
    await api(devBase + '/activate', {snapshot:release.snapshot_id, expected_snapshot:expected, ...operator});
    devInvalidate(); await devLoad(); devSay('开发版本已启用。正式资料库未改变。', true);
  });
}
$('#dev-refresh').addEventListener('click', () => devRun('正在刷新版本状态…', async () => { devInvalidate(); await devLoad(); devSay('版本状态已更新。', true); }));
$('#dev-plan').addEventListener('click', () => {
  if (!devSavedOnly()) return;
  const ids = [...document.querySelectorAll('#dev-cases input:checked')].map(e => e.value);
  devRun('正在核对资料和已提交声明…', async () => {
    devInvalidate(); const plan = await api(devBase + '/plan', {case_ids:ids}); development.plan = plan;
    const box = $('#dev-preview'); box.replaceChildren(); box.hidden = false;
    box.append(node('h3', '本次纳入范围（尚未准备或启用）'), node('p', `题目：${plan.case_ids.join('、')}`),
      node('p', `${plan.source_ids.length} 份来源 · ${plan.chunks.length} 个证据片段`),
      node('p', `基于开发版本：${plan.base_snapshot_id || '尚无'}`));
    for (const source of plan.source_ids) box.append(node('p', `${source}：${plan.chunks.filter(c => c[0] === source).map(c => c[1]).join('、')}`));
    box.append(node('p', '每份来源仅保留本次所选片段；确认范围后再准备索引。', 'audit-muted')); devSay('范围核对完成，请检查本次片段。', true);
  });
});
$('#dev-prepare').addEventListener('click', () => {
  if (!devSavedOnly() || !development.plan) return;
  const operator = devOperator(); if (!operator) return;
  const plan = development.plan;
  devRun('正在准备资料与索引，请等待完成…', async () => {
    try {
      const result = await api(devBase + '/prepare', {operation:'include', expected_snapshot:plan.base_snapshot_id,
        case_ids:plan.case_ids, plan_id:plan.plan_id, ...operator});
      devInvalidate(); await devLoad(); devSay(`已准备 ${result.index.chunks} 个快照片段的索引，尚未启用。请在准备记录中明确启用。`, true);
    } catch (error) { devInvalidate(); await devLoad().catch(() => {}); throw error; }
  });
});
for (const [selector, operation, target] of [['#dev-withdraw','withdraw','#dev-version'], ['#dev-rollback','rollback','#dev-target']]) {
  $(selector).addEventListener('click', () => {
    if (!devSavedOnly() || !$(target).value) return;
    const operator = devOperator(); if (!operator) return;
    const id = $(target).value, expected = development.history.active_snapshot_id;
    const text = operation === 'withdraw' ? '所选资料版本将立即停止检索。即使随后索引失败，撤回仍生效。确认撤回？' : '将为所选历史版本准备新快照与索引，之后仍需明确启用。确认准备？';
    if (!window.confirm(text)) return;
    devRun(operation === 'withdraw' ? '正在撤回资料并准备索引…':'正在准备回滚索引…', async () => {
      try {
        await api(devBase + '/prepare', {operation, expected_snapshot:expected, ...operator,
          ...(operation === 'withdraw' ? {version_id:id}:{target_snapshot:id})});
        devInvalidate(); await devLoad(); devSay(operation === 'withdraw' ? '所选资料已撤回。移除后的快照已准备，仍需明确启用。':'回滚快照已准备，尚未启用。请核对准备记录。', true);
      } catch (error) { devInvalidate(); await devLoad().catch(() => {}); throw error; }
    });
  });
}
$('#dev-version').addEventListener('change', devControls); $('#dev-target').addEventListener('change', devControls);
document.addEventListener('workbench-busy', devControls);
document.addEventListener('review-saved', () => { devInvalidate(); devSay('审核记录已更新，请点击“刷新版本状态”后重新核对纳入范围。'); });
// Refresh is explicit so unsaved review forms and operator text are never replaced.
development.loading = true; devControls();
devLoad().catch(devError).finally(() => { development.loading = false; devControls(); });
