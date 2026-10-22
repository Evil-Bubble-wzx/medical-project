'use strict';
const trial = {cases:[], currentRun:null, epoch:0, feedbackDirty:false};
Object.assign(messages, {doctor_account_required:'请使用医生账号。',completed_consultation_required:'咨询完成后才能留下反馈。',invalid_trial_feedback:'请填写反馈；发现问题时必须说明原因。',trial_feedback_conflict:'回答或反馈版本已变化。当前填写仍保留，请重新打开本次咨询核对。'});
const originalClearDetail = clearDetail;
clearDetail = function(){ trial.epoch++; trial.currentRun=null; trial.feedbackDirty=false; $('#trial-feedback-panel').replaceChildren(); $('#trial-feedback-panel').hidden=true; $('#trial-case-note').textContent=''; return originalClearDetail(); };
const originalLeave = leave;
leave = function(){return originalLeave()&&(!trial.feedbackDirty||window.confirm('试用反馈尚未保存，是否放弃并继续？'));};
const originalSelect = select;
select = async function(patient){
  await originalSelect(patient);
  if(!trial.cases.length&&state.me?.role==='doctor')trial.cases=(await api('/trial-cases')).cases;
  const item=patient.managed_case?null:trial.cases.find(c=>c.label===patient.label);
  $('#trial-case-note').textContent=item?`${item.id} · 观察重点：${item.observation}`:'可自行填写知识检索问题。';
};
$('#trial-example').addEventListener('click',()=>{
  const item=state.selected?.managed_case?null:trial.cases.find(c=>c.label===state.selected?.label);
  if(!item){say('请先选择预置合成病例。');return;}
  if($('#consultation-question').value.trim()&&!window.confirm('用示例问题替换当前问题？'))return;
  $('#consultation-question').value=item.question;state.consultDirty=true;state.ticket=null;
  say('示例问题已填入。请核对资料版本并确认发送，再提交。',true);
});
const originalLoad = load;
load = async function(){await originalLoad(); if(state.me?.role==='doctor'){trial.cases=(await api('/trial-cases')).cases;}};
const originalRenderConsultation = renderConsultation;
renderConsultation = function(record){if(trial.feedbackDirty&&!window.confirm('试用反馈尚未保存，是否重新载入本次咨询？'))return;trial.feedbackDirty=false;originalRenderConsultation(record);void showTrialFeedback(record);};
async function showTrialFeedback(record){
  const panel=$('#trial-feedback-panel');panel.replaceChildren();panel.hidden=true;
  const epoch=++trial.epoch,patient=state.selected?.patient_id,user=state.me?.id;
  const alive=()=>trial.epoch===epoch&&state.selected?.patient_id===patient&&state.me?.id===user;
  if(state.me?.role!=='doctor'||record.state!=='completed')return;
  const path=`/patients/${encodeURIComponent(patient)}/consultations/${encodeURIComponent(record.consultation_id)}/feedback`;
  try{
    const saved=await api(path,undefined,true,alive);if(!saved||!alive())return;
    panel.hidden=false;panel.append(node('h3','本次医生试用反馈'),node('p','意见仅用于开发改进，不会批准资料、应用表述或证明医院验收。','audit-muted'));
    const form=node('form');form.id='trial-feedback-form';form.addEventListener('input',()=>{trial.feedbackDirty=true;});form.addEventListener('change',()=>{trial.feedbackDirty=true;});
    const labels={relevance:'资料相关性',citation_support:'引用是否支持回答',input_fidelity:'输入解释是否忠实',patient_readability:'患者段是否易懂',overall:'整体试用体验'};
    const selects={};
    for(const [key,label]of Object.entries(labels)){
      const field=node('label',label),select=node('select');select.id='feedback-'+key;
      for(const [value,text]of [['not_assessed','尚未评估'],['acceptable','本次可接受'],['issue','发现问题']]){const option=node('option',text);option.value=value;select.append(option);}
      select.value=saved.review?.review[key]||'not_assessed';selects[key]=select;field.append(select);form.append(field);
    }
    const field=node('label','问题说明或建议（发现问题时必填）'),comment=node('textarea');comment.id='feedback-comment';comment.maxLength=2000;comment.rows=4;comment.value=saved.review?.review.comment||'';field.append(comment);form.append(field);
    const button=node('button','保存本次试用反馈','audit-primary');button.type='submit';form.append(button);
    const status=node('p',saved.revision?`已保存第 ${saved.revision} 版反馈，可修改后再次保存。`:'尚未留下反馈。','audit-muted');status.id='feedback-status';form.append(status);
    let revision=saved.revision;
    form.addEventListener('submit',event=>{event.preventDefault();if(!alive()||state.busy)return;
      const review=Object.fromEntries(Object.entries(selects).map(([key,select])=>[key,select.value]));
      if(Object.values(review).includes('issue')&&!comment.value.trim()){status.textContent='发现问题时请填写具体说明。';comment.focus();return;}
      run('正在保存试用反馈…',async()=>{const result=await api(path,{...review,comment:comment.value.trim(),expected_revision:revision,result_hash:saved.result_hash},true,alive);if(!result||!alive())return;revision=result.revision;trial.feedbackDirty=false;status.textContent=`已保存第 ${revision} 版反馈；旧版本仍保留。`;say('试用反馈已保存，未转为医学批准。',true);});
    });
    panel.append(form);
    if(saved.history.length){const history=node('details');history.append(node('summary',`查看最近 ${saved.history.length} 版反馈`));for(const row of saved.history){history.append(node('p',`第 ${row.revision} 版 · ${new Date(row.created_at*1000).toLocaleString()} · ${row.review.comment||'无文字补充'}`));}panel.append(history);}
  }catch(error){if(alive()){panel.hidden=false;panel.append(node('p','反馈暂不可用：'+error.message));}}
}
$('#export-trial-feedback').addEventListener('click',()=>run('正在导出本人反馈…',async()=>{
  const data=await api('/trial-feedback/export');const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=node('a');a.href=url;a.download='doctor-trial-feedback.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);say(`已导出 ${data.reviews.length} 条反馈历史。`,true);
}));
(async()=>{try{const r=await fetch('/api/v1/validation/status',{cache:'no-store'});if(!r.ok)throw new Error();const s=await r.json();$('#trial-readiness').textContent=`资料：${s.chunks} 个可检索片段；生成配置：${s.generation_state==='ready'?'已配置':'待配置'}；本地检索模型：${s.model_available?'已安装':'待安装'}。实际生成结果仍需医生核对。`;}catch{$('#trial-readiness').textContent='暂时无法确认服务状态，请检查启动窗口。';}})();

window.addEventListener('beforeunload',event=>{if(trial.feedbackDirty){event.preventDefault();event.returnValue='';}});

const caseEditor={dirty:false,key:null};
Object.assign(messages,{doctor_case_archived:'病例已归档，请先恢复后再保存资料或提交新咨询。',doctor_case_limit:'当前账号最多保留80个自建合成病例（含归档）。',doctor_case_request_conflict:'本次新建编号已用于不同内容，请修改名称后重试。',doctor_case_revision_conflict:'病例名称或归档状态已被另一页面更新。当前填写保留，请核对后重新载入。',invalid_case_label:'病例名称需为1—80字。'});
const beforeCaseControls=controls;
controls=function(value){beforeCaseControls(value);if(state.selected?.archived_at){$('#snapshot-form button[type="submit"]').disabled=true;$('#consultation-submit').disabled=true;}};
const beforeCaseLeave=leave;
leave=function(){return beforeCaseLeave()&&(!caseEditor.dirty||window.confirm('病例名称尚未保存，是否放弃并继续？'));};
const beforeCaseClear=clearDetail;
clearDetail=function(){beforeCaseClear();caseEditor.dirty=false;$('#doctor-case-actions').hidden=true;};
const beforeCaseSession=clearSession;
clearSession=function(){beforeCaseSession();caseEditor.dirty=false;caseEditor.key=null;$('#doctor-case-create').reset();$('#doctor-case-archived-list').replaceChildren();$('#doctor-case-search').value='';$('#doctor-case-count').textContent='';};
const beforeCaseList=renderList;
renderList=function(){beforeCaseList();const query=$('#doctor-case-search').value.trim().toLowerCase();let shown=0;for(const button of $('#patient-list').querySelectorAll('button')){button.hidden=!!query&&!button.textContent.toLowerCase().includes(query);if(!button.hidden)shown++;}$('#doctor-case-count').textContent=`显示 ${shown} / ${state.patients.length} 个当前可用病例`;
$('#doctor-case-create').hidden=state.me?.role!=='doctor';};
$('#doctor-case-search').addEventListener('input',renderList);
const beforeCaseSelect=select;
select=async function(patient){if(patient.managed_case)patient=await api("/doctor-cases/"+encodeURIComponent(patient.patient_id));await beforeCaseSelect(patient);caseEditor.dirty=false;$('#doctor-case-actions').hidden=!patient.managed_case;if(patient.managed_case){$('#doctor-case-rename').value=patient.label;$('#doctor-case-state').textContent=patient.archived_at?'已归档：可查看历史；请恢复后再保存资料或新建咨询。':'自建合成病例 · 名称与归档状态版本 '+patient.case_revision;$('#doctor-case-toggle-archive').textContent=patient.archived_at?'恢复病例':'归档病例';}controls(state.busy);};
$('#doctor-case-label').addEventListener('input',()=>{caseEditor.key=null;});
$('#doctor-case-rename').addEventListener('input',()=>{caseEditor.dirty=true;});
$('#doctor-case-create').addEventListener('submit',event=>{event.preventDefault();if(!leave())return;run('正在建立合成病例…',async()=>{caseEditor.key=caseEditor.key||crypto.randomUUID();const created=await api('/doctor-cases',{label:$('#doctor-case-label').value.trim(),synthetic_only:$('#doctor-case-synthetic').checked,request_key:caseEditor.key});$('#doctor-case-create').reset();caseEditor.key=null;$('#doctor-case-search').value='';await load();const patient=state.patients.find(p=>p.patient_id===created.patient_id);if(patient)await select(patient);say('病例已建立，请填写并保存第一版合成资料，再发起咨询。',true);});});
async function updateCase(archived){const patient=state.selected;if(!patient?.managed_case)return;const label=$('#doctor-case-rename').value.trim();if(!label){say('请填写病例名称。');return;}run('正在保存病例信息…',async()=>{await api('/doctor-cases/'+encodeURIComponent(patient.patient_id),{label,archived,synthetic_only:true,expected_revision:patient.case_revision});caseEditor.dirty=false;clearDetail();await load();if(!archived){const current=state.patients.find(p=>p.patient_id===patient.patient_id);if(current)await select(current);}$('#doctor-case-archived-list').replaceChildren();say(archived?'病例已归档，历史保留。':'病例信息已保存。',true);});}
$('#doctor-case-save-name').addEventListener('click',()=>{if((state.dirty||state.consultDirty||trial.feedbackDirty)&&!window.confirm('其他表单有未保存内容，保存名称并重新载入会清除它们，是否继续？'))return;void updateCase(!!state.selected?.archived_at);});
$('#doctor-case-toggle-archive').addEventListener('click',()=>{if(!state.selected?.managed_case)return;if(!leave())return;if(!window.confirm(state.selected.archived_at?'确认恢复此合成病例？':'确认归档此病例？历史保留，归档后不再新增资料或咨询；已开始的任务可能继续完成。'))return;void updateCase(!state.selected.archived_at);});
$('#doctor-case-refresh-archive').addEventListener('click',()=>run('正在读取归档病例…',async()=>{const data=await api('/doctor-cases?archived=true'),box=$('#doctor-case-archived-list');box.replaceChildren();if(!data.cases.length)box.append(node('p','暂无已归档病例。','audit-muted'));for(const patient of data.cases){const button=node('button',patient.label+' · 查看历史或恢复','audit-item');button.type='button';button.addEventListener('click',()=>{if(leave())run('正在读取归档病例…',()=>select(patient));});box.append(button);}}));
window.addEventListener('beforeunload',event=>{if(caseEditor.dirty||$('#doctor-case-label').value.trim()){event.preventDefault();event.returnValue='';}});
