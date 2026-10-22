'use strict';
const $ = selector => document.querySelector(selector);
const node = (tag, text, cls) => {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = text;
  if (cls) element.className = cls;
  return element;
};
const base = '/api/v1/validation/audit';
const topics = {rhinitis:'鼻炎', sinusitis:'鼻窦炎', otitis_media:'中耳炎', hearing_loss:'听力损失', tinnitus:'耳鸣', throat:'咽喉'};
const states = {pending:'尚未记录', draft:'已存草稿', submitted:'已提交声明'};
const decisions = {accept:'建议保留', revise:'需要修改', exclude:'建议排除'};
const wordingDecisions = {accept:'确认候选表述', revise:'提出修改', exclude:'驳回候选表述'};
const decisionLabels = () => state.selected?.kind === 'wording' ? wordingDecisions : decisions;
const fields = {
  decision:'候选处理意见', reviewer:'审核人姓名', reviewed_at:'审核时间', notes:'审核说明与理由',
  adult_scope:'适用人群与成人范围', evidence_quality:'证据质量与研究限制', conflicts_of_interest:'资助及利益冲突说明',
  license_version_confirmed:'已确认许可及版本', source_family_aliases_checked:'已核查同源、译文及更新版本',
  question_clarity:'问题是否清晰', adult_applicability:'证据是否适用于题目中的成人范围',
  proposed_text:'本次建议采用或修改后的表述', evidence_checked:'已逐项核对引用原文', scope_checked:'已核对疾病、人群、关系与语气范围',
  scope_limitations:'适用范围与限制', evidence_sufficiency:'所列证据是否充分',
  additional_relevant_evidence:'是否还需补充证据', boundary_expected_behavior_confirmed:'是否确认候选预期处理行为'
};
const state = {items:[], kind:'source', selected:null, dirty:false, busy:false, historyBefore:null, originalAdditional:null, wordingLoaded:false};
function say(text, success=false) {
  $('#message').textContent = text;
  $('#message').classList.toggle('success', success);
}
function issueText(code) {
  const special = {
    decision_required:'请填写候选处理意见。', reviewer_required:'请填写真实审核人姓名。', notes_required:'请填写审核说明与理由。',
    valid_review_time_required:'请填写有效审核时间，不能使用未来时间。', accepted_source_required:'关联来源尚未提交有效的保留声明，请先审核来源。',
    additional_evidence_must_be_bound_before_accept:'补充证据尚未完成绑定，请选择“需要修改”并说明所缺内容。',
    evidence_required:'此证据题缺少证据身份。', invalid_boundary_contract:'候选边界题的预期行为不完整。',
    incomplete_evidence_identity:'引用身份不完整，需修改候选资料。'
  };
  if (special[code]) return special[code];
  if (code.endsWith('_required')) {
    const label = fields[code.slice(0, -9)];
    if (label) return `请核对并完成“${label}”。`;
  }
  return '有一项审核条件尚未满足，请核对资料和意见。';
}
async function api(path, body, retry=true) {
  const response = await fetch(path, {method:body ? 'POST':'GET', cache:'no-store',
    headers:body ? {'Content-Type':'application/json'}:{}, body:body ? JSON.stringify(body):undefined});
  if (response.status === 401 && retry) {
    const session = await fetch('/audit', {cache:'no-store'});
    if (session.ok) return api(path, body, false);
  }
  const data = await response.json();
  if (response.ok) return data;
  const detail = data.detail || {};
  const code = detail.error_code || data.error_code;
  const messages = {
    review_revision_conflict:'记录已被另一页面更新。当前填写仍保留，请重新载入最新记录后核对；不会自动覆盖。',
    stale_review_binding:'原始资料或题目已变化，当前填写仍保留。请重新载入条目后核对。',
    candidate_manifest_changed:'候选资料的版本关系已变化，需要先修复资料绑定。',
    review_archive_changed:'原始归档文件或证据定位发生变化，提交已阻止。请先核对资料。',
    invalid_review_fields:'审核字段类型、长度或名称不符合要求，请核对填写内容。',
    invalid_input:'请检查审核字段、时间和内容长度。',
    review_item_not_found:'该条目已不存在，请刷新列表。',
    review_component_unavailable:'审核库或资料暂不可用，请检查本地服务。',
    wording_archive_changed:'表述审核包或原始引用已变化，操作已阻止。请先核对材料版本，再重新载入。',
    wording_review_unavailable:'表述审核材料暂不可用，请检查4.0审核包与归档文件是否完整。其他资料审核仍可使用。',
    development_admission_not_ready:'所选题目或依赖来源尚未满足纳入条件，请核对已提交的保留声明、许可、成人范围和原文归档。',
    development_plan_changed:'资料、审核意见或当前版本已变化，请重新核对纳入范围。',
    development_snapshot_conflict:'当前开发版本已被更新，本次操作未启用。请刷新版本状态并重新准备。',
    withdrawn_or_stale_development_member:'所选快照包含已撤回或审核绑定失效的资料，操作已阻止。',
    development_index_failed_active_snapshot_preserved:'索引准备失败，原活动快照保持不变。如果本次执行撤回，被撤回资料仍保持停用；请查看准备记录后排查。',
    development_component_unavailable:'资料或索引组件暂不可用。请刷新版本状态核对操作结果，避免重复撤回或启用。',
    prepared_development_release_required:'该记录没有可用的准备索引，请重新准备。',
    prepared_index_changed:'索引与准备记录不一致，启用已阻止，请重新准备。',
    only_bound_development_draft_can_be_withdrawn:'此资料版本不能通过开发资料入口撤回，请刷新状态后核对。',
    development_snapshot_not_found:'所选历史开发版本不存在，请刷新状态。'
  };
  let text = messages[code] || data.message || (response.status === 401 ? '会话已失效，请刷新页面。':'请求未完成，请稍后重试。');
  if (code === 'review_submission_incomplete') text = '提交未完成，填写内容仍保留：\n' + (detail.issues || []).map(issueText).join('\n');
  throw new Error(text);
}
function busy(value) {
  state.busy = value;
  document.querySelectorAll('button, #search, #state-filter, #review-form input, #review-form select, #review-form textarea').forEach(element => { element.disabled = value; });
  document.dispatchEvent(new Event('workbench-busy'));
}
function markDirty() {
  state.dirty = true;
  $('#dirty-state').textContent = '有尚未保存的修改';
}
function canLeave() { return !state.dirty || window.confirm('当前意见尚未保存。是否放弃这些修改，切换条目？'); }
function itemURL(item=state.selected) { return item.kind === 'wording' ? `${base}/wording/items/${encodeURIComponent(item.item_id)}` : `${base}/items/${encodeURIComponent(item.kind)}/${encodeURIComponent(item.item_id)}`; }
function renderList() {
  const search = $('#search').value.trim().toLowerCase();
  const status = $('#state-filter').value;
  const container = $('#item-list'); container.replaceChildren();
  const visible = state.items.filter(item => item.kind === state.kind && (!status || item.state === status) &&
    [item.item_id, item.title || '', topics[item.topic] || item.topic || ''].join(' ').toLowerCase().includes(search));
  for (const item of visible) {
    const button = node('button', undefined, 'audit-item'); button.type = 'button';
    button.setAttribute('aria-current', String(state.selected?.kind === item.kind && state.selected?.item_id === item.item_id));
    const label = item.kind === 'source' || item.kind === 'wording' ? item.title : `${item.item_id} · ${item.case_kind === 'boundary_manual_review' ? '边界题':'证据题'}`;
    button.append(node('strong', label), node('small', `${topics[item.topic] || item.topic || ''} · ${states[item.state] || item.state}`));
    button.disabled = state.busy;
    button.addEventListener('click', () => selectItem(item)); container.append(button);
  }
  if (!visible.length) container.append(node('p', '没有符合当前筛选条件的条目。', 'audit-muted'));
  const sourceCount = state.items.filter(item => item.kind === 'source').length;
  const caseCount = state.items.filter(item => item.kind === 'case').length;
  const wordingCount = state.items.filter(item => item.kind === 'wording').length;
  $('#totals').textContent = `${sourceCount} 份来源 · ${caseCount} 道题目${state.wordingLoaded ? ` · ${wordingCount} 条表述`:''}\n已提交声明 ${state.items.filter(item => item.state === 'submitted').length} / ${state.items.length}`;
}
function safeLink(parent, value, label='打开原始来源 ↗') {
  try {
    const url = new URL(value);
    if (!['http:', 'https:'].includes(url.protocol)) return;
    const link = node('a', label); link.href = url.href; link.target = '_blank'; link.rel = 'noopener noreferrer'; parent.append(link);
  } catch { /* Missing or non-web source URL is not rendered. */ }
}
function identifiers(parent, pairs) {
  const detail = node('details', undefined, 'audit-identifiers'); detail.append(node('summary', '查看资料标识与定位'));
  for (const [label, value] of pairs) if (value !== undefined && value !== null) detail.append(node('div', `${label}：${value}`));
  parent.append(detail);
}
function renderSource(item) {
  const content = $('#source-content'); content.replaceChildren(); const p = item.payload;
  if (item.kind === 'wording') {
    content.append(node('p', '候选修改尚未应用。请对照原文填写自己的意见；提交不会替换历史回答或发布资料。', 'audit-muted'));
    const comparison = node('div', undefined, 'wording-comparison');
    for (const [title, text] of [['原回答表述', p.original_text], ['修改候选（待核对）', p.candidate_text]]) {
      const box = node('article', undefined, 'audit-evidence');
      box.append(node('h3', title), node('blockquote', text)); comparison.append(box);
    }
    content.append(comparison, node('p', `待核对问题：${p.observation}`, 'audit-muted'));
    for (const support of p.supports) {
      const box = node('article', undefined, 'audit-evidence');
      box.append(node('h3', support.source_title), node('blockquote', support.quote));
      safeLink(box, support.source_url);
      identifiers(box, [['资料', support.document_id], ['版本', support.version_id], ['片段', support.chunk_id], ['定位', support.locator]]);
      content.append(box);
    }
    identifiers(content, [['原论断', p.claim_id], ['材料版本', '4.0']]);
  } else if (item.kind === 'source') {
    content.append(node('p', p.population_note || '请核对原文的适用人群。', 'audit-muted'));
    content.append(node('p', `出版日期：${p.publication_date || '待核对'} · 许可：${p.license || '待核对'}`, 'audit-muted'));
    safeLink(content, p.source_url);
    if (p.license_statement) { const d = node('details', undefined, 'audit-identifiers'); d.append(node('summary', '查看原始许可声明'), node('p', p.license_statement)); content.append(d); }
    identifiers(content, [['资料', item.item_id], ['DOI', p.doi], ['PMCID', p.pmcid]]);
  } else {
    if (p.source_population_note) content.append(node('p', p.source_population_note, 'audit-muted'));
    if (p.proposed_expected_behavior) {
      const box = node('div', undefined, 'audit-evidence'); box.append(node('h3', '候选预期处理行为（待审核）'), node('p', p.proposed_expected_behavior)); content.append(box);
    }
    for (const evidence of p.expected_evidence || []) {
      const box = node('article', undefined, 'audit-evidence');
      box.append(node('h3', '候选原文依据'), node('blockquote', evidence.text)); safeLink(box, evidence.source_url);
      identifiers(box, [['资料', evidence.document_id], ['版本', evidence.version_id], ['片段', evidence.chunk_id], ['定位', evidence.locator], ['字符范围', `${evidence.start}–${evidence.end}`]]);
      content.append(box);
    }
  }
}
function field(grid, name, kind, value, hint) {
  const label = node('label', undefined, `audit-form-field${kind === 'area' ? ' wide':''}`); label.append(node('span', fields[name]));
  let input;
  if (kind === 'boolean' || kind === 'decision' || kind === 'additional') {
    input = node('select');
    const choices = kind === 'decision' ? [['', '请选择'], ...Object.entries(decisionLabels())] :
      kind === 'additional' ? [['', '未完成核对或仍需补充'], ['none', '已确认无需补充'],
        ...(Array.isArray(value) && value.length ? [['needed', '已有补充证据，待绑定']]:[])] : [['', '尚未核对'], ['true', '是'], ['false', '否']];
    for (const [key, text] of choices) { const option = node('option', text); option.value = key; input.append(option); }
    input.value = kind === 'additional' ? (Array.isArray(value) ? (value.length ? 'needed':'none'):'') : value === null || value === undefined ? '' : String(value);
  } else {
    input = node(kind === 'area' ? 'textarea':'input');
    if (kind === 'area') { input.rows = 3; input.maxLength = 4000; }
    else if (kind === 'date') { input.type = 'datetime-local'; input.step = 1; }
    else input.maxLength = 100;
    input.value = kind === 'date' ? localDate(value) : value || '';
  }
  input.name = name; input.id = `field-${name}`; label.append(input);
  if (hint) label.append(node('small', hint));
  if (kind === 'date') {
    const button = node('button', '填入当前时间', 'link-button'); button.type = 'button';
    button.addEventListener('click', () => { input.value = localDate(new Date().toISOString()); markDirty(); }); label.append(button);
  }
  input.addEventListener('input', markDirty); input.addEventListener('change', markDirty); grid.append(label);
}
function localDate(value) {
  if (!value) return '';
  const d = new Date(value); if (!Number.isFinite(d.getTime())) return '';
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 19);
}
function renderForm(item) {
  const container = $('#review-fields'); container.replaceChildren();
  const grid = node('div', undefined, 'audit-form-grid'); const r = item.review || {};
  field(grid, 'decision', 'decision', r.decision); field(grid, 'reviewer', 'text', r.reviewer, '填写实际审核人姓名；当前没有医院账号认证。');
  field(grid, 'reviewed_at', 'date', r.reviewed_at);
  if (item.kind === 'source') {
    for (const key of ['adult_scope', 'evidence_quality', 'conflicts_of_interest']) field(grid, key, 'area', r[key]);
    for (const key of ['license_version_confirmed', 'source_family_aliases_checked']) field(grid, key, 'boolean', r[key]);
  } else if (item.kind === 'wording') {
    field(grid, 'proposed_text', 'area', r.proposed_text, '确认候选或提出修改时，请填写完整表述；此处只保存审核意见。');
    const copy = node('button', '填入候选供核对', 'link-button'); copy.type = 'button';
    copy.addEventListener('click', () => { $('#field-proposed_text').value = item.payload.candidate_text; markDirty(); });
    grid.querySelector('#field-proposed_text').parentElement.append(copy);
    field(grid, 'evidence_checked', 'boolean', r.evidence_checked);
    field(grid, 'scope_checked', 'boolean', r.scope_checked);
  } else {
    field(grid, 'question_clarity', 'boolean', r.question_clarity);
    field(grid, 'scope_limitations', 'area', r.scope_limitations);
    if (item.payload.kind === 'boundary_manual_review') field(grid, 'boundary_expected_behavior_confirmed', 'boolean', r.boundary_expected_behavior_confirmed);
    else {
      field(grid, 'adult_applicability', 'boolean', r.adult_applicability);
      field(grid, 'evidence_sufficiency', 'boolean', r.evidence_sufficiency);
      state.originalAdditional = r.additional_relevant_evidence || null;
      field(grid, 'additional_relevant_evidence', 'additional', r.additional_relevant_evidence, '需要补充时请选择“需要修改”，并在说明中写清内容；新证据须先完成绑定。');
      if (state.originalAdditional?.length) {
        const d = node('details', undefined, 'audit-identifiers'); d.append(node('summary', `查看已有 ${state.originalAdditional.length} 条补充证据标识`));
        for (const ref of state.originalAdditional) d.append(node('p', `${ref.document_id} / ${ref.version_id} / ${ref.chunk_id} / ${ref.locator}`)); grid.append(d);
      }
    }
  }
  field(grid, 'notes', 'area', r.notes, '说明保留、修改或排除的理由。草稿可以暂不填完。');
  container.append(grid);
}
function renderSelected(item) {
  state.selected = item; state.originalAdditional = null;
  const index = state.items.findIndex(i => i.kind === item.kind && i.item_id === item.item_id);
  if (index >= 0) state.items[index] = {...state.items[index], ...item,
    title:item.payload.title, topic:item.payload.topic,
    case_kind:item.kind === 'case' ? item.payload.kind || 'evidence':null};
  $('#empty-detail').hidden = true; $('#selected-detail').hidden = false;
  $('#item-topic').textContent = item.kind === 'wording' ? '回答表述 / 4.0' : `${topics[item.payload.topic] || item.payload.topic || ''} / ${item.item_id}`;
  $('#item-title').textContent = item.kind === 'case' ? item.payload.question : item.payload.title;
  $('#export').textContent = item.kind === 'wording' ? '导出表述审核记录（含草稿）' : '下载审核表';
  $('#export-heading').textContent = item.kind === 'wording' ? '导出表述审核记录' : '导出已提交审核表';
  $('#export-description').textContent = item.kind === 'wording' ? '导出这11项的当前记录及保存、提交历史，包含草稿。未保存输入不导出，候选修改不会自动应用。' : '导出数据库中已提交的意见及准入检查结果。未保存输入和草稿不计入提交表，导出不会激活资料或启动模型评分。';
  $('#export-state').textContent = '';
  $('#item-state').textContent = states[item.state];
  $('#record-meta').textContent = `记录版本 ${item.revision} · ${item.updated_at ? '保存于 '+new Date(item.updated_at).toLocaleString():'尚未保存'} · 医学审核状态未授予`;
  renderSource(item); renderForm(item); state.dirty = false; $('#dirty-state').textContent = '当前没有未保存修改';
  $('#history').replaceChildren(); state.historyBefore = null; $('#more-history').hidden = true;
  renderList();
}
async function selectItem(item, force=false) {
  if (state.busy || (!force && !canLeave())) return;
  busy(true); say('正在读取条目…');
  try { renderSelected(await api(itemURL(item))); say(''); }
  catch (error) { say(error.message); }
  finally { busy(false); }
}
function collectReview() {
  const result = {};
  for (const input of $('#review-fields').querySelectorAll('input, textarea, select')) {
    const key = input.name; let value = input.value;
    if (key === 'additional_relevant_evidence') value = value === 'none' ? [] : value === 'needed' && state.originalAdditional?.length ? state.originalAdditional : null;
    else if (input.tagName === 'SELECT' && key !== 'decision') value = value === '' ? null : value === 'true';
    else if (key === 'reviewed_at') value = value ? new Date(value).toISOString() : null;
    else value = value.trim() || null;
    result[key] = value;
  }
  return result;
}
async function save(submit) {
  if (state.busy || !state.selected || !$('#review-form').reportValidity()) return;
  let review; try { review = collectReview(); } catch { say('请检查审核时间。'); return; }
  const extra = $('#field-additional_relevant_evidence');
  if (submit && review.decision === 'accept' && extra?.value === 'needed') { say('仍需补充证据时，请选择“需要修改”并写明所缺内容。'); return; }
  const body = {binding_hash:state.selected.binding_hash, expected_revision:state.selected.revision, review};
  busy(true); say(submit ? '正在核对并提交声明…':'正在保存草稿…');
  try {
    const result = await api(itemURL() + (submit ? '/submit':'/draft'), body);
    renderSelected(result); document.dispatchEvent(new Event('review-saved')); say(submit ? (result.kind === 'wording' ? '表述审核意见已提交。候选修改未应用，历史回答与医学审核状态保持原样。':'审核声明已提交并保存。资料尚未发布，医学审核状态未自动授予。'):'草稿已保存。未完成内容可以稍后继续填写。', true);
  } catch (error) { say(error.message); }
  finally { busy(false); }
}
async function history(more=false) {
  if (state.busy || !state.selected) return;
  busy(true);
  try {
    const before = more && state.historyBefore ? `&before=${state.historyBefore}`:'';
    const data = await api(itemURL() + `/history?limit=10${before}`); const container = $('#history');
    if (!more) container.replaceChildren();
    if (!data.events.length && !more) container.append(node('p', '暂无保存或提交记录。', 'audit-muted'));
    for (const event of data.events) {
      const box = node('article', undefined, 'audit-history-event');
      box.append(node('strong', `记录版本 ${event.revision} · ${states[event.state]}${event.binding_hash !== state.selected.binding_hash ? ' · 旧资料版本':''}`));
      box.append(node('p', `${new Date(event.created_at).toLocaleString()} · ${event.review.reviewer || '尚未填写审核人'} · ${decisionLabels()[event.review.decision] || '尚未决定'}`));
      box.append(node('p', event.review.notes || '未填写说明。'));
      const d = node('details'); d.append(node('summary', '查看当时的审核字段'));
      for (const [key, value] of Object.entries(event.review)) if (value !== null && !Array.isArray(value)) d.append(node('p', `${fields[key] || key}：${value === true ? '是':value === false ? '否':decisionLabels()[value] || value}`));
      box.append(d); container.append(box);
    }
    state.historyBefore = data.next_before; $('#more-history').hidden = !data.next_before;
  } catch (error) { say(error.message); }
  finally { busy(false); }
}
document.querySelectorAll('[data-kind]').forEach(button => button.addEventListener('click', async () => {
  if (state.busy || button.dataset.kind === state.kind || !canLeave()) return;
  state.kind = button.dataset.kind; state.dirty = false; state.selected = null; $('#selected-detail').hidden = true; $('#empty-detail').hidden = false;
  document.querySelectorAll('[data-kind]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
  if (state.kind === 'wording' && !state.wordingLoaded) {
    busy(true);
    try { state.items.push(...(await api(`${base}/wording/items`)).items); state.wordingLoaded = true; say(''); }
    catch (error) { say(error.message); }
    finally { busy(false); }
  }
  $('#search').value = ''; $('#state-filter').value = ''; renderList();
  const first = state.items.find(i => i.kind === state.kind); if (first) selectItem(first, true);
}));
$('#search').addEventListener('input', renderList); $('#state-filter').addEventListener('change', renderList);
$('#save-draft').addEventListener('click', () => save(false));
$('#review-form').addEventListener('submit', event => { event.preventDefault(); save(true); });
$('#reload').addEventListener('click', () => selectItem(state.selected));
$('#load-history').addEventListener('click', () => history()); $('#more-history').addEventListener('click', () => history(true));
$('#export').addEventListener('click', async () => {
  if (state.busy) return; busy(true); $('#export-state').textContent = '正在读取已提交审核表…';
  try {
    const wording = state.kind === 'wording';
    const result = await api(`${base}${wording ? '/wording':''}/export`); const blob = new Blob([JSON.stringify(result, null, 2)], {type:'application/json'});
    const url = URL.createObjectURL(blob); const link = node('a'); link.href = url; link.download = `ent-${wording ? 'wording-':''}review-export-${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
    document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 10000);
    $('#export-state').textContent = wording ? '已导出表述审核记录与历史（含草稿）。意见尚未应用，不代表医学审核通过。' : result.validation.ready_for_manual_governance_binding ? '已导出。声明结构完整，可进入后续人工治理绑定；不是医学或上线合格证明。':'已导出。仍有待审或待修改项，尚不能进入后续治理绑定。';
  } catch (error) { $('#export-state').textContent = error.message; }
  finally { busy(false); }
});
window.addEventListener('beforeunload', event => { if (state.dirty) { event.preventDefault(); event.returnValue = ''; } });
(async () => {
  busy(true);
  try { state.items = (await api(`${base}/items`)).items; renderList(); }
  catch (error) { say(error.message); $('#totals').textContent = '连接未完成'; }
  finally { busy(false); }
  const first = state.items.find(i => i.kind === state.kind); if (first) await selectItem(first, true);
})();
