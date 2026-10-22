'use strict';
const $ = s => document.querySelector(s);
const node = (tag,text,cls) => { const e=document.createElement(tag); if(text!==undefined)e.textContent=text; if(cls)e.className=cls; return e; };
const base='/api/v1/business';
const state={me:null,patients:[],selected:null,revision:0,before:null,dirty:false,busy:false,consultDirty:false,consultBefore:null,ticket:null,pollTimer:null,pollEpoch:0,watchRun:null,pollFailures:0};
const messages={invalid_credentials:'账号或密码不正确。',login_temporarily_limited:'登录失败次数较多，请15分钟后重试。',login_required:'登录已失效，请重新登录。',record_not_found:'该患者不存在或访问授权已失效。',patient_revision_conflict:'资料已被另一页面更新。当前填写仍保留，请重新载入当前资料后核对。',patient_profile_already_exists:'该账号已经有患者档案，请刷新列表。',patient_account_required:'此操作需要患者账号。',doctor_not_available:'所选医生账号不可用，请刷新后核对。',invalid_input:'请检查合成资料、字段长度、年龄和授权时长。',business_component_unavailable:'资料服务暂不可用，请稍后刷新核对，避免重复保存。',consultation_request_conflict:'此提交编号对应的输入已变化，请重新选择资料版本后提交。',consultation_input_too_long:'资料与问题合计过长，请缩短问题或保存较精简的合成资料。',consultation_configuration_changed:'生成期间配置或代码发生变化，本次未保存答案，请核对后新建咨询。',consultation_evidence_changed:'生成期间引用资料失效，本次未保存答案，请核对资料后新建咨询。'};
function say(text,success=false){$('#patient-message').textContent=text;$('#patient-message').classList.toggle('success',success);}
function clearDetail(){state.selected=null;state.revision=0;state.before=null;state.dirty=false;$('#snapshot-form').reset();$('#snapshot-dirty').textContent='';$('#patient-title').textContent='';$('#patient-revision').textContent='';$('#patient-detail').hidden=true;$('#patient-empty').hidden=false;$('#snapshots').replaceChildren();$('#grants-list').replaceChildren();$('#more-snapshots').hidden=true;clearConsultations();}
function clearSession(){clearDetail();state.me=null;state.patients=[];$('#profile-form').reset();$('#patient-list').replaceChildren();$('#doctor').replaceChildren();$('#identity').textContent='';$('#account-panel').hidden=true;$('#patient-workspace').hidden=true;$('#login-panel').hidden=false;$('#password').value='';}
async function api(path,body,retry=true,guard=null){
  if(guard&&!guard())return null;
  const r=await fetch(base+path,{method:body?'POST':'GET',cache:'no-store',headers:body?{'Content-Type':'application/json'}:{},body:body?JSON.stringify(body):undefined});
  const data=await r.json(),code=data.detail?.error_code||data.error_code;
  if(guard&&!guard())return null;
  // Renew only the workbench cookie, never replay an expired business login.
  if(r.status===401 && code!=='login_required' && code!=='invalid_credentials' && retry){await fetch('/patients',{cache:'no-store'});return api(path,body,false,guard);}
  if(r.ok)return data;
  if(code==='login_required')clearSession();
  if(r.status===404){clearDetail();state.patients=[];$('#patient-list').replaceChildren();}
  const error=new Error(messages[code]||data.message||'操作未完成，请刷新状态后核对。');error.code=code;throw error;
}
function controls(value){state.busy=value;document.querySelectorAll('button,input,textarea,select').forEach(e=>{e.disabled=value;});$('#more-snapshots').disabled=value||!state.before;$('#consultation-submit').disabled=value||!$('#consultation-snapshot').value;$('#more-consultations').disabled=value||!state.consultBefore;}
async function run(text,fn){if(state.busy)return;controls(true);say(text);try{await fn();}catch(e){say(e.message);}finally{controls(false);}}
function leave(){return !(state.dirty||state.consultDirty)||window.confirm('患者资料或咨询问题尚未保存，是否放弃修改并继续？');}
function url(suffix=''){return `/patients/${encodeURIComponent(state.selected.patient_id)}${suffix}`;}
function renderList(){
  const box=$('#patient-list');box.replaceChildren();
  $('#list-note').textContent=state.me.role==='patient'?'仅显示本人档案。':'显示当前有效授权及本人自建的合成病例。';
  for(const patient of state.patients){const button=node('button',patient.label,'audit-item');button.type='button';button.setAttribute('aria-current',String(state.selected?.patient_id===patient.patient_id));button.addEventListener('click',()=>{if(leave())run('正在读取患者资料…',()=>select(patient));});box.append(button);}
  if(!state.patients.length)box.append(node('p',state.me.role==='doctor'?'暂无有效授权。请由患者账号授权后刷新。':'尚未建立合成档案。','audit-muted'));
  $('#profile-form').hidden=state.me.role!=='patient'||state.patients.length>0;
}
function renderHistory(data,more=false){
  const box=$('#snapshots');if(!more)box.replaceChildren();
  if(!data.snapshots.length&&!more)box.append(node('p','尚无保存记录。','audit-muted'));
  const labels={age:'年龄',chief_complaint:'主诉',duration:'持续时间',history:'相关病史',pasted_text:'补充记录'};
  for(const row of data.snapshots){const d=node('details',undefined,'snapshot-record');d.append(node('summary',`版本 ${row.revision} · ${new Date(row.created_at*1000).toLocaleString()}`));for(const [k,v] of Object.entries(row.patient))d.append(node('p',`${labels[k]||k}：${v||'未填写'}`));box.append(d);}
  state.before=data.next_before;$('#more-snapshots').hidden=!data.next_before;
  consultationOptions(data,more);
}
async function grants(){
  if(state.me.role!=='patient'){$('#grants-panel').hidden=true;return;}
  const [doctors,grants]=await Promise.all([api('/doctors'),api(url('/grants'))]);
  const select=$('#doctor');select.replaceChildren();const first=node('option',doctors.doctors.length?'请选择医生':'暂无可用开发医生账号');first.value='';select.append(first);
  for(const doctor of doctors.doctors){const option=node('option',doctor.username);option.value=doctor.doctor_id;select.append(option);}
  const box=$('#grants-list');box.replaceChildren();
  if(!grants.grants.length)box.append(node('p','尚无授权记录。','audit-muted'));
  for(const grant of grants.grants){const active=!grant.revoked_at&&grant.expires_at>Date.now()/1000;const row=node('article',undefined,'snapshot-record');row.append(node('p',`${grant.username} · ${grant.revoked_at?'已撤销':active?'授权有效':'已到期'} · 截止 ${new Date(grant.expires_at*1000).toLocaleString()}`));if(active){const button=node('button','撤销该医生授权','audit-secondary');button.type='button';button.addEventListener('click',()=>{if(!window.confirm('确认撤销？该医生将不能继续读写此患者资料。'))return;run('正在撤销授权…',async()=>{await api(url(`/grants/${encodeURIComponent(grant.grant_id)}/revoke`),{});await grantsRefresh();say('授权已撤销，后续读写已阻断。',true);});});row.append(button);}box.append(row);}
  $('#grants-panel').hidden=false;
}
async function grantsRefresh(){await grants();}
async function select(patient){
  clearDetail();state.selected=patient;
  try{
    const data=await api(url('/snapshots'));renderHistory(data);
    const latest=data.snapshots[0];state.revision=latest?.revision||0;
    const values=latest?.patient||{};
    for(const [id,key] of [['age','age'],['duration','duration'],['chief-complaint','chief_complaint'],['patient-history','history'],['pasted-text','pasted_text']])$('#'+id).value=values[key]??'';
    $('#snapshot-synthetic').checked=false;$('#patient-title').textContent=patient.label;$('#patient-revision').textContent=`当前资料版本 ${state.revision} · 保存将创建版本 ${state.revision+1}`;
    $('#patient-detail').hidden=false;$('#patient-empty').hidden=true;$('#snapshot-dirty').textContent='当前没有未保存修改';
    await grants();await loadConsultations(false,true);renderList();say('患者资料已载入。',true);
  }catch(e){clearDetail();throw e;}
}
async function load(){
  const me=await api('/me');if(state.me?.id!==me.id)clearDetail();state.me=me;
  $('#login-panel').hidden=true;$('#account-panel').hidden=false;$('#patient-workspace').hidden=false;$('#identity').textContent=`${me.username} · ${me.role==='patient'?'患者账号':'医生账号'}`;
  state.patients=(await api('/patients')).patients;renderList();
  const selected=state.selected&&state.patients.find(p=>p.patient_id===state.selected.patient_id);
  if(selected)await select(selected);else{clearDetail();if(state.patients[0])await select(state.patients[0]);}
}
$('#login-form').addEventListener('submit',event=>{event.preventDefault();const username=$('#username').value,password=$('#password').value;run('正在登录…',async()=>{try{await api('/login',{username,password});await load();say('已登录本地合成数据工作台。',true);}finally{$('#password').value='';}});});
$('#logout').addEventListener('click',()=>{if(!leave())return;run('正在退出…',async()=>{await api('/logout',{});clearSession();say('已退出，页面中的患者资料已清除。',true);});});
$('#refresh-patients').addEventListener('click',()=>{if(leave())run('正在刷新身份和患者…',async()=>{await load();say('身份与患者列表已更新。',true);});});
$('#reload-patient').addEventListener('click',()=>{if(leave())run('正在重新载入…',()=>select(state.selected));});
$('#profile-form').addEventListener('submit',event=>{event.preventDefault();if(!$('#profile-form').reportValidity())return;run('正在建立合成档案…',async()=>{await api('/patients',{synthetic_only:$('#profile-synthetic').checked,label:$('#patient-label').value.trim()});$('#profile-form').reset();await load();say('合成档案已建立。',true);});});
$('#snapshot-form').addEventListener('input',()=>{state.dirty=true;$('#snapshot-dirty').textContent='有尚未保存的修改';});
$('#snapshot-form').addEventListener('submit',event=>{event.preventDefault();if(!state.selected||!$('#snapshot-form').reportValidity())return;if(state.consultDirty&&!window.confirm('保存资料将刷新页面并清除尚未提交的咨询问题，是否继续？'))return;const body={synthetic_only:$('#snapshot-synthetic').checked,expected_revision:state.revision,age:Number($('#age').value),chief_complaint:$('#chief-complaint').value,duration:$('#duration').value,history:$('#patient-history').value,pasted_text:$('#pasted-text').value};run('正在保存新版本…',async()=>{const saved=await api(url('/snapshots'),body);await select(state.selected);say(`已保存版本 ${saved.revision}，历史版本保留。`,true);});});
$('#more-snapshots').addEventListener('click',()=>run('正在读取更早资料…',async()=>{renderHistory(await api(url(`/snapshots?before=${state.before}`)),true);say('历史记录已更新。',true);}));
$('#grant-form').addEventListener('submit',event=>{event.preventDefault();if(!$('#grant-form').reportValidity())return;const doctor_id=$('#doctor').value,minutes=Number($('#grant-minutes').value);if(!window.confirm(`授权所选医生在${minutes}分钟内查看和保存该患者资料？`))return;run('正在保存授权…',async()=>{await api(url('/grants'),{doctor_id,minutes});await grants();say('访问授权已建立。',true);});});
function clearConsultations(){stopConsultationWatch();state.consultDirty=false;state.consultBefore=null;state.ticket=null;$('#consultation-form').reset();$('#consultation-snapshot').replaceChildren();$('#consultation-list').replaceChildren();$('#consultation-result').replaceChildren();$('#consultation-result').hidden=true;$('#more-consultations').hidden=true;}
function consultationOptions(data,more){const select=$('#consultation-snapshot');if(!more)select.replaceChildren();for(const row of data.snapshots){const option=node('option',`资料版本 ${row.revision} · ${new Date(row.created_at*1000).toLocaleString()}`);option.value=row.snapshot_id;select.append(option);}if(!select.options.length){const o=node('option','请先保存资料');o.value='';select.append(o);}}
function consultationStage(stage){return {queued:'当前阶段：排队等待',checking_access:'当前阶段：核对登录与访问权限',generating:'当前阶段：检索、生成及证据验证（不提供虚构百分比）',completed:'当前阶段：结果已保存',timed_out:'当前阶段：任务超时',interrupted:'当前阶段：运行中断',failed:'当前阶段：运行失败'}[stage]||'正在读取任务阶段';}
function stopConsultationWatch(){if(state.pollTimer)clearTimeout(state.pollTimer);state.pollTimer=null;state.pollEpoch++;state.watchRun=null;state.pollFailures=0;}
function startConsultationWatch(id){
  if(!state.selected||!state.me)return;
  if(state.watchRun?.id===id)return;
  stopConsultationWatch();const epoch=state.pollEpoch,patient=state.selected.patient_id,user=state.me.id;state.watchRun={id,patient,user};
  const alive=()=>state.pollEpoch===epoch&&state.selected?.patient_id===patient&&state.me?.id===user;
  const schedule=delay=>{if(alive())state.pollTimer=setTimeout(poll,delay);};
  async function poll(){
    if(!alive())return;state.pollTimer=null;
    if(state.busy||document.hidden){schedule(2000);return;}
    try{
      const record=await api(`/patients/${encodeURIComponent(patient)}/consultations/${encodeURIComponent(id)}`,undefined,true,alive);
      if(!record||!alive())return;
      state.pollFailures=0;renderConsultation(record);
      const row=[...document.querySelectorAll('#consultation-list [data-run-id]')].find(e=>e.dataset.runId===id);
      if(row)row.querySelector('.consultation-state').textContent=`${new Date(record.created_at*1000).toLocaleString()} · ${{queued:'已排队',running:'正在执行',completed:'流程已完成',failed:'运行失败，等待人工重试',interrupted:'运行已中断，等待人工重试'}[record.state]||record.state}`;
      if(['queued','running'].includes(record.state))schedule(2000);
      else if(!state.dirty&&!state.consultDirty)say(record.state==='completed'?'后台咨询已完成并保存。':'后台任务已结束，请查看状态并决定是否人工重试。',record.state==='completed');
    }catch(error){if(!alive()){if((error.code==='login_required'&&!state.me)||(error.code==='record_not_found'&&state.me?.id===user&&!state.selected))say(error.message);return;}state.pollFailures++;if(!state.dirty&&!state.consultDirty)say('暂时无法读取任务状态，将稍后继续查询；不会重新调用模型。');schedule(Math.min(15000,2000*state.pollFailures));}
  }
  schedule(100);
}
async function loadConsultations(more=false,resume=false){
  const data=await api(url(`/consultations${more&&state.consultBefore?'?before='+state.consultBefore:''}`));const box=$('#consultation-list');if(!more)box.replaceChildren();
  if(!more&&!data.consultations.length)box.append(node('p','尚无咨询记录。','audit-muted'));
  const labels={queued:'已排队，尚未开始',running:'正在检索、生成与验证',completed:'流程已完成',failed:'运行失败，等待人工重试',interrupted:'运行已中断，等待人工重试'};
  for(const row of data.consultations){const card=node('article',undefined,'snapshot-record');card.dataset.runId=row.id;card.append(node('p',`${new Date(row.created_at*1000).toLocaleString()} · ${labels[row.state]||row.state}`,'consultation-state'),node('p',row.question));const button=node('button','查看本次咨询','audit-secondary');button.type='button';button.addEventListener('click',()=>run('正在读取咨询…',async()=>{renderConsultation(await api(url('/consultations/'+encodeURIComponent(row.id))));say('已读取保存的咨询，不重新调用模型。',true);}));card.append(button);box.append(card);}
  state.consultBefore=data.next_before;$('#more-consultations').hidden=!data.next_before;if(resume){const pending=data.consultations.find(r=>['queued','running'].includes(r.state));if(pending)startConsultationWatch(pending.id);}
}
function appendManualRetry(box,record){const retry=node('button','准备作为新咨询重试','audit-secondary');retry.type='button';retry.addEventListener('click',()=>{if(!window.confirm('重试会新建任务；原请求可能已产生费用。确认准备重试？'))return;state.ticket=null;$('#consultation-question').value=record.question;if(![...$('#consultation-snapshot').options].some(o=>o.value===record.snapshot_id)){const option=node('option',`原咨询资料版本 ${record.snapshot_revision}`);option.value=record.snapshot_id;$('#consultation-snapshot').append(option);}$('#consultation-snapshot').value=record.snapshot_id;$('#consultation-consent').checked=false;state.consultDirty=true;say('请重新确认资料版本和发送授权，再提交新的咨询。');});box.append(retry)}
function renderConsultation(record){
  const box=$('#consultation-result');box.replaceChildren();box.hidden=false;
  box.append(node('h3',`咨询 · 资料版本 ${record.snapshot_revision}`),node('p',record.question));
  const input=node('details');input.append(node('summary','查看本次实际使用的已存资料'));const labels={age:'年龄',chief_complaint:'主诉',duration:'持续时间',history:'相关病史',pasted_text:'补充记录'};for(const [key,value]of Object.entries(record.patient))input.append(node('p',`${labels[key]||key}：${value||'未填写'}`));box.append(input);
  if(!['queued','running'].includes(record.state))stopConsultationWatch();
  if(record.state!=='completed'){
    box.append(node('p',record.state==='queued'?'任务已排队，尚未调用模型。可离开页面稍后回看，状态会自动更新。':record.state==='running'?'后台正在核查并执行检索、生成与验证。可离开页面，刷新不会重复生成。':record.state==='interrupted'?'本次运行因服务中断或执行权失效而停止，不会自动重试。原请求是否已产生费用可能无法确定。':'本次生成失败，未保存未经校验的回答。需要人工确认后才能重试。','audit-muted'));
    if(['queued','running'].includes(record.state)){box.append(node('p',consultationStage(record.stage),'audit-muted'));startConsultationWatch(record.consultation_id);}
    const errors={consultation_timeout:'本次任务已超时，迟到结果不会覆盖当前状态。',consultation_generator_busy:'模型正在处理其他请求，请稍后手动重试。',login_required:'发起任务的登录已失效，需要重新登录并确认发送。',record_not_found:'发起任务的患者访问授权已失效。',doctor_case_archived:'病例已归档，本次待执行任务未调用模型；恢复后可重新确认提交。',consultation_configuration_changed:'配置发生变化，本次未保存回答；已发出的请求仍可能产生费用。'};if(errors[record.error_code])box.append(node('p',errors[record.error_code],'audit-muted'));
    if(['failed','interrupted'].includes(record.state))appendManualRetry(box,record);return;
  }
  const result=record.result;box.append(node('p',`${result.model||'已记录模型'} · 医学支持仍待审核`,'audit-muted'));
  if(record.historical_evidence_currently_available===false)box.append(node('p','历史证据当前已撤回、绑定失效或不可读取。本记录仅用于回溯，请勿当作当前资料；需要时重新咨询。','audit-notice'));
  if(record.current_comparison_issues?.length)box.append(node('p','该历史回答存在输入记录或系统边界被标作医学比较的问题，未改写原结果；请仅作回溯并重新咨询或反馈。','audit-notice'));
  const answer=result.answer;
  const scopeMessages={patient_symptom_details_missing:'请先补充具体不适表现和开始时间；当前输入不足以作个体解释。',individual_prescription_unsupported:'本试用版不提供个体处方或用药剂量；补充信息也不会解除这一边界，可改问资料中的一般知识。',adult_library_target_mismatch:'当前仅有成人开发资料，不能据此解释儿童个体情况。',live_hospital_data_unavailable:'当前未接入医院实时数据，不能查询实际挂号、报告或病历。',missing_imaging_diagnosis_unsupported:'缺少影像和临床评估，不能确认影像诊断。',guideline_conflict_details_missing:'请提供具体指南名称、版本和冲突条目，再核对资料依据。',input_duration_needs_confirmation:'输入的病程信息有冲突，请先核对后再咨询。'};
  if(scopeMessages[result.validation?.scope_code])box.append(node('p',scopeMessages[result.validation.scope_code],'audit-notice'));
  if(result.validation?.input_comparison_withheld)box.append(node('p','本次输入比较未通过分类核对，该段已隐藏；以下仅提供一般资料，不能当作针对本人情况的解释。','audit-notice'));
  const compared=(answer.input_explanation||[]).some(c=>c.source_kind==='medical_comparison');
  if(answer.status==='answered'&&compared)box.append(node('p','以下只比较输入记录与引用资料，不构成个体确诊、病因判断或治疗建议。','audit-muted'));
  if(result.validation?.summary_strategy==='verified_core_excerpt')box.append(node('p','患者段仅摘取已核验核心句中已有的中文信息，未翻译英文术语；可读性仍请医生评估。','audit-muted'));
  if(result.validation?.summary_strategy==='verified_core_fallback')box.append(node('p','患者段复用了已核验的核心事实，未增加改写内容，可读性仍请医生评估。','audit-muted'));
  if(answer.status==='answered'&&!compared)box.append(node('p','本次尚无通过核验的个体资料比较；输入段仅核对已填信息，不表示这些资料已适用于本人。','audit-muted'));
  if(answer.status!=='answered'){const categories={input_binding_failed:'输入信息未能可靠对应，本次未展示解释。请核对所填内容。',model_format_failed:'模型输出格式不符合要求，本次未展示草稿。',content_rejected:'生成内容未通过证据或表达范围核验，本次未展示。',verification_failed:'本次证据核验未完成，尚无可展示的回答。',source_unavailable:'本次资料已不可用，需要重新检索。'};const notes={insufficient_evidence:'本次证据不足，未生成可展示的解释。',needs_information:'本次需要补充信息，未生成解释。',validation_failed:'本次回答未通过验证，未展示原始草稿。'};box.append(node('p',categories[result.validation?.outcome_category]||notes[answer.status]||'未获得可展示的回答。'));if(answer.status==='validation_failed')appendManualRetry(box,record);}
  else{
    const refs=new Map(result.citations.map(c=>[c.evidence_id,c]));
    for(const [key,label]of [['professional','专业资料与解释'],['input_explanation',record.current_comparison_issues?.length?'历史输入段（分类待复核）':compared?'结合输入的资料比较':'已填信息核对（不是个体解释）'],['patient_summary','患者易懂版']]){const section=node('section',undefined,'answer-section');section.append(node('h3',label));for(const claim of answer[key]||[]){section.append(node('p',claim.text));for(const anchor of claim.input_anchors||[]){const names={age:'年龄',chief_complaint:'主诉',duration:'病程',history:'病史',pasted_text:'补充记录',question:'问题'};const states={reported:'陈述',denied:'含否认信息',unknown:'含未知信息',mixed:'含否认及未知信息'};section.append(node('p',`${names[anchor.field]||anchor.field}原话（${states[anchor.state]||anchor.state}）：${anchor.quote}`,'audit-muted'));}for(const support of claim.supports||[]){const ref=refs.get(support.evidence_id);if(!ref)continue;const detail=node('details',undefined,'answer-reference');detail.append(node('summary',`[${support.evidence_id}] ${ref.title}`),node('blockquote',support.quote),node('p',`原文定位：${ref.locator} · 资料版本 ${ref.version_id}`));try{const u=new URL(ref.source_url);if(['http:','https:'].includes(u.protocol)){const a=node('a','查看原始来源 ↗');a.href=u.href;a.target='_blank';a.rel='noopener noreferrer';detail.append(a);}}catch{}section.append(detail);}}box.append(section);}
  }
  const meta=node('details');meta.append(node('summary','查看保存的运行版本'),node('p',`咨询编号：${record.consultation_id}`),node('p',`患者资料快照：${record.snapshot_id}`),node('p',`知识快照：${result.knowledge_snapshot_id||'未使用知识检索'}`));for(const [file,hash]of Object.entries(record.provenance.files||{}))meta.append(node('p',`${file}：${hash}`));box.append(meta);
}
$('#consultation-question').addEventListener('input',()=>{state.consultDirty=true;state.ticket=null;});
$('#consultation-snapshot').addEventListener('change',()=>{state.consultDirty=true;state.ticket=null;controls(state.busy);});
$('#consultation-form').addEventListener('submit',event=>{event.preventDefault();if(state.busy||!$('#consultation-form').reportValidity())return;if(state.dirty){say('患者资料尚有未保存修改。请先保存或重新载入，再基于已存版本咨询。');return;}const snapshot_id=$('#consultation-snapshot').value,question=$('#consultation-question').value.trim();if(!state.ticket)state.ticket={key:crypto.randomUUID(),snapshot_id,question};const request_key=state.ticket.key;run('正在提交后台任务，本次提交编号保持不变…',async()=>{const record=await api(url('/consultations'),{snapshot_id,question,request_key,synthetic_only:true,provider_consent:$('#consultation-consent').checked});state.consultDirty=false;$('#consultation-consent').checked=false;renderConsultation(record);await loadConsultations();say(record.state==='completed'?'咨询流程已完成并保存，可在咨询历史中回看。':'任务已提交，可离开页面；状态将自动更新。',true);});});
$('#refresh-consultations').addEventListener('click',()=>run('正在刷新咨询历史…',async()=>{await loadConsultations();say('咨询历史已更新。',true);}));
$('#more-consultations').addEventListener('click',()=>run('正在读取更早咨询…',async()=>{await loadConsultations(true);say('咨询历史已更新。',true);}));
window.addEventListener('beforeunload',event=>{if(state.dirty||state.consultDirty){event.preventDefault();event.returnValue='';}});
// No patient content, password or session token is stored in browser storage.
run('正在检查登录状态…',async()=>{try{await load();}catch(e){if(e.code==='login_required'){clearSession();say('请使用本机开发账号登录。');}else throw e;}});
