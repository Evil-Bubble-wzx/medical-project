"use strict";
function appendMissingInputDetails(record){
 const box=document.querySelector('#consultation-result');
 if(!box||record.state!=='completed'||!(/缺少|还缺|补充.*信息/.test(record.question||'')||record.result?.answer?.limitations?.includes('missing_patient_details')))return;
 const missing=[['history','既往史'],['pasted_text','已有检查或报告（如有）']].filter(([key])=>!String(record.patient?.[key]||'').trim());
 if(!missing.length)return;
 const panel=node('section',undefined,'audit-panel');panel.id='patient-missing-inputs';panel.append(node('h3','本次尚未填写的信息'));
 panel.append(node('p',missing.map(([,label])=>label).join('、')+'。'));
 panel.append(node('p','这是已保存表单的缺项，不代表没有相关病史，也不表示需要去做检查。可展开“本次症状”补充已经知道的信息；系统仍不能据此确诊。','audit-muted'));
 box.append(panel);
}
const patientBaseLoad=load;
load=async function(){const me=await api('/me');if(me.role!=='patient'){clearSession();throw new Error('当前不是患者账号，请使用 patient-trial 登录此入口。');}await patientBaseLoad();};
const patientBaseClear=clearDetail;
clearDetail=function(){patientBaseClear();document.querySelector("#patient-workspace > aside").hidden=false;};
const patientBaseSelect=select;
select=async function(patient){await patientBaseSelect(patient);$('#patient-list').hidden=true;document.querySelector('#patient-workspace > aside').hidden=true;$('#list-note').textContent='仅显示本人合成资料。医生授权是可选项，不影响自己咨询。';};
const patientBaseRender=renderConsultation;
renderConsultation=function(record){patientBaseRender(record);const box=$('#consultation-result');const summary=[...box.querySelectorAll('.answer-section')].find(s=>s.querySelector('h3')?.textContent==='患者易懂版');const first=box.querySelector('.answer-section');if(summary&&first&&summary!==first)box.insertBefore(summary,first);appendMissingInputDetails(record);};

const patientResultWithSummary=renderConsultation;
renderConsultation=function(record){
 patientResultWithSummary(record);
 if(record.state!=='completed'||record.result?.answer?.status==='answered')return;
 const box=$('#consultation-result'),panel=node('section',undefined,'audit-panel');panel.id='patient-next-actions';panel.append(node('h3','接下来可以怎么做'));
 const code=record.result?.validation?.scope_code,status=record.result?.answer?.status,category=record.result?.validation?.outcome_category;
 const boundary=['individual_prescription_unsupported','adult_library_target_mismatch','live_hospital_data_unavailable','missing_imaging_diagnosis_unsupported'].includes(code);
 panel.append(node('p',boundary?'本次请求超出当前功能或资料范围。补充个人信息不一定能解除这个限制。':category==='content_rejected'?'检索到了候选资料，但本轮解释未通过内容核验，暂不展示。这不等于资料库没有相关内容；可以把想了解的内容说得更具体。':status==='validation_failed'?'回答未通过程序核对，不能据此判断你的情况；这不等于疾病不存在或资料库完全没有相关内容。':status==='needs_information'?'先核对本次使用的资料，再补充明确的问题。': '当前没有可展示且通过核对的解释。这不等于疾病不存在，也不表示所有相关资料都已查完。'));
 const review=node('button','核对本次实际使用的资料','audit-secondary');review.type='button';review.addEventListener('click',()=>{const detail=box.querySelector('details');if(detail){detail.open=true;detail.scrollIntoView({block:'center',behavior:'smooth'});}});panel.append(review);
 if(!boundary){panel.append(node('p','可改问资料中的一般知识。下面只填入新问题，不会自动发送或重试。'));
 for(const question of ['关于上述不适，现有资料介绍了哪些一般知识？','现有资料对相关症状描述了哪些表现？']){const button=node('button',question,'audit-secondary');button.type='button';button.addEventListener('click',()=>{if(state.consultDirty&&!window.confirm('替换尚未提交的问题？'))return;$('#consultation-question').value=question;$('#consultation-consent').checked=false;state.ticket=null;state.consultDirty=true;say('新问题已填入。请先核对资料，再明确确认发送。');$('#consultation-question').focus();});panel.append(button);}}
 panel.append(node('p','需要补充症状、病程时，请修改上方资料并保存新版本。不要仅反复提交同一个问题。','audit-muted'));box.append(panel);
};

// Patient entry keeps the existing access control and immutable records behind one form.
const patientForm=$('#consultation-form');
const symptomFields=$('#snapshot-form .audit-form-grid');
patientForm.prepend(symptomFields);
$('#snapshot-form').closest('.audit-panel').hidden=true;
$('#consultation-snapshot').closest('label').hidden=true;
$('#consultation-snapshot').required=false;
const authorization=$('#grants-panel').parentElement;
$('#patient-detail').append(authorization);
const historyPanel=$('#snapshots').closest('.audit-panel');
const historyFold=node('details');historyFold.append(node('summary','查看症状资料历史'));historyPanel.before(historyFold);historyFold.append(historyPanel);
$('#consultation-submit').textContent='提交咨询';
patientForm.prepend(node('p','填写本次症状和问题，提交时自动保存资料。继续提问会沿用当前症状；追问会参考本会话最近三轮，仍需重新检索资料。','audit-muted'));
symptomFields.addEventListener('input',()=>{state.dirty=true;state.ticket=null;});
const patientControls=controls;
controls=function(value){patientControls(value);$('#consultation-submit').disabled=value||!state.selected;};
const patientSelectUnified=select;
select=async function(patient){await patientSelectUnified(patient);};
function patientInput(){return {age:Number($('#age').value),chief_complaint:$('#chief-complaint').value,duration:$('#duration').value,history:$('#patient-history').value,pasted_text:$('#pasted-text').value};}
patientForm.addEventListener('submit',event=>{
 event.preventDefault();event.stopImmediatePropagation();
 if(state.busy||!state.selected||!patientForm.reportValidity())return;
 const input=patientInput(),question=$('#consultation-question').value.trim();
 if(!question){say('请填写具体问题。');return;}
 run('正在保存资料并提交咨询…',async()=>{
  if(!$('#consultation-snapshot').value||JSON.stringify(input)!==JSON.stringify(state.patientSavedInput)){
   const saved=await api(url('/snapshots'),{...input,synthetic_only:true,expected_revision:state.revision});
   state.revision=saved.revision;state.patientSavedInput=input;state.dirty=false;state.ticket=null;
   const option=node('option',`资料版本 ${saved.revision}`);option.value=saved.snapshot_id;$('#consultation-snapshot').prepend(option);$('#consultation-snapshot').value=saved.snapshot_id;
   renderHistory(await api(url('/snapshots')));$('#consultation-snapshot').value=saved.snapshot_id;
  }
  const snapshot_id=$('#consultation-snapshot').value;
  if(!state.ticket||state.ticket.snapshot_id!==snapshot_id||state.ticket.question!==question)state.ticket={key:crypto.randomUUID(),snapshot_id,question};
  const record=await api(url('/consultations'),{snapshot_id,question,request_key:state.ticket.key,synthetic_only:true,provider_consent:$('#consultation-consent').checked,parent_consultation_id:state.conversationParent||null});
  state.dirty=false;state.consultDirty=false;$('#consultation-consent').checked=false;
  renderConsultation(record);await loadConsultations();say('咨询已保存，正在处理时可以离开页面，刷新不会重复提交。',true);
 });
},true);
const patientRenderUnified=renderConsultation;
renderConsultation=function(record){
 patientRenderUnified(record);
 const box=$('#consultation-result');
 box.querySelector('h3').textContent='本次咨询';
 const professional=[...box.querySelectorAll('.answer-section')].filter(s=>s.querySelector('h3')?.textContent!=='患者易懂版');
 if(professional.length){const fold=node('details');fold.append(node('summary','展开专业解释与引用依据'));professional[0].before(fold);for(const section of professional)fold.append(section);}
 if(record.state==='completed'){
  const follow=node('button','沿用本次症状继续提问','audit-secondary');follow.type='button';
  follow.addEventListener('click',()=>{
   if((state.dirty||state.consultDirty)&&!window.confirm('使用这次咨询的症状，并清空尚未提交的问题？'))return;
   restorePatientRecord(record);
   state.ticket=null;state.consultDirty=true;
   $('#consultation-question').value='';$('#consultation-consent').checked=false;$('#consultation-question').focus();
   say('已沿用这次症状。请把追问写完整，例如具体提及想了解的症状或资料；会参考本会话最近三轮帮助理解追问，医学内容仍须本轮引用支持。');
  });box.append(follow);
 }
};

// Conversation identity is server-owned; nothing is stored in browser storage.
const conversationBar=node('section',undefined,'audit-panel');
const conversationLabel=node('p','新的咨询');conversationLabel.id='conversation-label';
const newConversation=node('button','开始新咨询','audit-secondary');newConversation.type='button';
const conversationTurns=node('div');conversationTurns.id='conversation-turns';
conversationBar.append(conversationLabel,newConversation,conversationTurns);patientForm.before(conversationBar);
function resetConversation(){state.conversationParent=null;state.activeConversation=null;state.pendingConversation=null;state.ticket=null;conversationLabel.textContent='新的咨询';conversationTurns.replaceChildren();}
const conversationClear=clearDetail;
clearDetail=function(){conversationClear();resetConversation();};
newConversation.addEventListener('click',()=>{
 if(!leave())return;stopConsultationWatch();resetConversation();
 for(const id of ['duration','chief-complaint','patient-history','pasted-text','consultation-question'])$('#'+id).value='';
 $('#consultation-consent').checked=false;state.dirty=true;state.consultDirty=false;
 $('#consultation-result').hidden=true;controls(false);$('#chief-complaint').focus();
 say('已开始新咨询，请填写这次症状。不会带入旧会话内容。');
});
const conversationControls=controls;
controls=function(value){conversationControls(value);$('#consultation-submit').disabled=value||!state.selected||!!state.pendingConversation;};
function continueConversation(record){
 state.activeConversation=record.conversation_id||record.consultation_id;
 state.conversationParent=record.state==='completed'?record.consultation_id:record.parent_consultation_id||null;
 state.pendingConversation=['queued','running'].includes(record.state)?record.consultation_id:null;
 conversationLabel.textContent='当前会话 · '+state.activeConversation.slice(0,8)+' · 最近三轮用于理解追问';
}
const conversationRender=renderConsultation;
renderConsultation=function(record){conversationRender(record);continueConversation(record);controls(state.busy);};
async function openConversation(identity,restoreInput=true){
 const data=await api(url('/consultations/'+encodeURIComponent(identity)+'/thread'));
 conversationTurns.replaceChildren();
 for(const [index,record]of data.turns.entries()){
  const button=node('button',`${index+1}. ${record.question}`,'audit-secondary');button.type='button';
  button.addEventListener('click',()=>{if(!leave())return;restorePatientRecord(record);state.ticket=null;$('#consultation-question').value='';$('#consultation-consent').checked=false;state.consultDirty=false;renderConsultation(record);say('已打开这一轮；下一次提交将从这一轮继续，可形成分支。',true);});conversationTurns.append(button);
 }
 const record=data.turns.at(-1);if(!record)return;
 if(restoreInput){
  restorePatientRecord(record);
  
  $('#consultation-question').value='';$('#consultation-consent').checked=false;state.consultDirty=false;state.ticket=null;
 }
 renderConsultation(record);
}
loadConsultations=async function(more=false,resume=false){
 const data=await api(url('/consultations'+(more&&state.conversationBefore?'?before='+state.conversationBefore:'')));
 if(!more)state.conversationRows=[];
 state.consultBefore=data.next_before;$('#more-consultations').hidden=!data.next_before;
 state.conversationRows=[...(state.conversationRows||[]),...data.consultations];state.conversationBefore=data.next_before;
 const box=$('#consultation-list');box.replaceChildren();const groups=new Map();
 for(const row of state.conversationRows){const id=row.conversation_id||row.id;if(!groups.has(id))groups.set(id,row);}
 for(const [id,row]of groups){const card=node('article',undefined,'snapshot-record');card.append(node('p','会话 '+id.slice(0,8)),node('p','最近问题：'+row.question));const button=node('button','打开会话','audit-secondary');button.type='button';button.addEventListener('click',()=>{if(leave())run('正在打开会话…',()=>openConversation(row.id));});card.append(button);box.append(card);}
 if(!groups.size)box.append(node('p','尚无咨询记录。','audit-muted'));
 if(resume&&data.consultations[0])await openConversation(data.consultations[0].id);
 else if(state.activeConversation){const active=data.consultations.find(r=>r.conversation_id===state.activeConversation);if(active)await openConversation(active.id,false);}
};

const conversationHistory=renderHistory;
renderHistory=function(data,more=false){conversationHistory(data,more);if(!more)state.patientSavedInput=data.snapshots[0]?.patient||null;};

messages.conversation_parent_not_completed='上一轮尚未完成，请等候结果或开始新咨询。';
messages.conversation_turn_limit='本会话已达到30轮上限，请开始新咨询。';

// Keep symptom editing available without making patients repeat the form for every followup.
const symptomDetails=node('details',undefined,'patient-symptoms');symptomDetails.id='patient-symptoms';
const symptomSummary=node('summary','填写本次症状');symptomSummary.id='patient-symptom-summary';
symptomFields.before(symptomDetails);symptomDetails.append(symptomSummary,symptomFields);symptomDetails.open=true;
const answerBox=$('#consultation-result');patientForm.before(answerBox);
const questionHeading=node('h3','填写问题');questionHeading.id='patient-question-heading';patientForm.prepend(questionHeading);
patientForm.addEventListener('invalid',event=>{if(symptomDetails.contains(event.target))symptomDetails.open=true;},true);
function refreshSymptomSummary(){
 const current=patientInput();symptomSummary.textContent=current.chief_complaint?
  `本次症状：${current.age||'年龄未填'}岁 · ${current.chief_complaint} · ${current.duration||'病程未填'}（展开修改）`:'填写本次症状';
}
symptomFields.addEventListener('input',()=>{refreshSymptomSummary();questionHeading.textContent='症状已修改，提交时一并保存';});
const focusedReset=resetConversation;
resetConversation=function(){focusedReset();symptomDetails.open=true;symptomSummary.textContent='填写本次症状';questionHeading.textContent='填写问题';};
const focusedClear=clearDetail;
clearDetail=function(){focusedClear();focusedRecord=null;symptomSummary.textContent='填写本次症状';symptomDetails.open=true;};
let focusedRecord=null;
const focusedRender=renderConsultation;
renderConsultation=function(record){
 focusedRender(record);refreshSymptomSummary();
 if(focusedRecord!==record.consultation_id&&!state.dirty){
  symptomDetails.open=false;
  if(!state.consultDirty&&$('#consultation-question').value.trim()===record.question)$('#consultation-question').value='';
 }
 focusedRecord=record.consultation_id;
 questionHeading.textContent=['queued','running'].includes(record.state)?'回答处理中，可稍后继续':'继续提问';
 $('#consultation-question').placeholder='可以继续问具体想了解的内容，例如：这些表现有哪些区别？';
};

const toolsPanel=node('details',undefined,'audit-panel');toolsPanel.id='patient-tools';toolsPanel.append(node('summary','账号与本人咨询管理'));
const exportButton=node('button','导出本人资料与咨询（JSON）','audit-secondary');exportButton.type='button';
exportButton.addEventListener('click',()=>run('正在导出本人记录…',async()=>{
 const data=await api(url('/export'));const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),address=URL.createObjectURL(blob),a=node('a');a.href=address;a.download='patient-consultations.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(address),1000);say('已导出本人症状历史与咨询，请妥善保存文件。',true);
}));
const deleteButton=node('button','删除当前会话','audit-secondary');deleteButton.type='button';
deleteButton.addEventListener('click',()=>{
 if(!state.activeConversation){say('请先打开要删除的会话。');return;}
 if(!leave())return;
 if(!window.confirm('删除当前会话的所有轮次、回答和关联反馈？此操作不能在页面撤销。症状历史和已有本机备份仍会保留。'))return;
 run('正在删除当前会话…',async()=>{await api(url('/consultations/'+encodeURIComponent(state.activeConversation)+'/delete'),{confirm:'DELETE'});await select(state.selected);say('会话已删除。症状历史和已有备份保留。',true);});
});
const passwordForm=node('form');passwordForm.id='patient-password-form';
for(const [id,label,auto]of [['current-password','当前密码','current-password'],['new-password','新密码（至少12位）','new-password'],['repeat-password','再次输入新密码','new-password']]){const l=node('label',label),input=node('input');input.type='password';input.id=id;input.required=true;input.maxLength=200;input.autocomplete=auto;if(id!=='current-password')input.minLength=12;l.append(input);passwordForm.append(l);}
const change=node('button','修改密码并退出','audit-secondary');change.type='submit';passwordForm.append(change);
passwordForm.addEventListener('submit',event=>{event.preventDefault();if(!passwordForm.reportValidity())return;if($('#new-password').value!==$('#repeat-password').value){say('两次新密码不一致。');return;}const body={current_password:$('#current-password').value,new_password:$('#new-password').value};run('正在修改密码…',async()=>{try{const changed=await api('/password',body);clearSession();say(changed.local_cache_pending?'密码已修改，请用新密码登录。本机登录助手待同步，重启前会自动恢复；不要再使用旧密码。':'密码已修改，所有旧登录已失效。请使用新密码重新登录。',true);}finally{passwordForm.reset();}});});
toolsPanel.append(exportButton,deleteButton,node('p','导出包含本人症状和回答。删除按整个会话执行，症状快照及旧备份保留；暂不提供账号注销或备份彻底擦除。','audit-muted'),passwordForm);
$('#patient-detail').append(toolsPanel);
messages.patient_tasks_active='本人还有排队或运行中的咨询，请完成后再修改密码或删除会话。';
messages.local_password_cache_unavailable='本机加密登录文件暂不可更新，密码未修改。';
messages.new_password_unchanged='新密码不能与当前密码相同。';
const toolsClear=clearSession;
clearSession=function(){toolsClear();passwordForm.reset();toolsPanel.open=false;};

const readableExport=node('button','导出可阅读报告（HTML）','audit-secondary');readableExport.type='button';
readableExport.addEventListener('click',()=>run('正在准备可阅读报告…',async()=>{
 const data=await api(url('/export')),doc=document.implementation.createHTMLDocument('我的咨询报告');
 const meta=doc.createElement('meta');meta.setAttribute('charset','utf-8');doc.head.prepend(meta);
 const style=doc.createElement('style');style.textContent='body{max-width:900px;margin:32px auto;padding:16px;font:16px/1.7 sans-serif}article{border-top:1px solid #ccc;padding:20px 0}p{white-space:pre-wrap;overflow-wrap:anywhere}blockquote{background:#f5f5f5;padding:12px}';doc.head.append(style);
 doc.body.append(node('h1','我的咨询报告'),node('p','本机合成资料试用报告；医学内容尚未临床审核。'));
 for(const snap of data.snapshots){const section=node('article');section.append(node('h2','症状资料版本 '+snap.revision));for(const [key,label]of [['age','年龄'],['chief_complaint','主要不适'],['duration','持续时间'],['history','相关病史'],['pasted_text','补充信息']])section.append(node('p',label+'：'+(snap.patient[key]??'')));doc.body.append(section);}
 for(const run of data.consultations){const article=node('article');article.append(node('h2',run.question),node('p','保存状态：'+run.state));const result=run.result;if(result){const answer=result.answer;article.append(node('p','回答状态：'+answer.status));for(const [key,label]of [['patient_summary','易懂解释'],['professional','专业依据'],['input_explanation','输入比较']]){article.append(node('h3',label));for(const claim of answer[key]||[])article.append(node('p',claim.text));}for(const citation of result.citations||[])article.append(node('h3',citation.evidence_id+' '+citation.title),node('p','原文位置：'+citation.locator),node('blockquote',citation.text),node('p',citation.source_url));}doc.body.append(article);}
 const blob=new Blob(['<!doctype html>'+doc.documentElement.outerHTML],{type:'text/html;charset=utf-8'}),address=URL.createObjectURL(blob),a=node('a');a.href=address;a.download='patient-report.html';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(address),1000);say('已导出可用浏览器阅读或打印的报告。',true);
}));
const clearData=node('button','清空本人症状、咨询及医生授权','audit-secondary');clearData.type='button';
clearData.addEventListener('click',()=>{
 if(!state.selected||!leave())return;
 if(!window.confirm('清空本人所有症状历史、咨询、相关反馈及医生授权？账号保留，旧备份仍保留。请先导出需要的记录。'))return;
 if(window.prompt('请输入 清空 确认操作')!=='清空')return;
 run('正在清空本人数据…',async()=>{await api(url('/clear'),{confirm:'DELETE'});await select(state.selected);say('当前数据库中的本人症状、咨询与医生授权已清空。账号和旧备份保留。',true);});
});
toolsPanel.insertBefore(readableExport,passwordForm);toolsPanel.insertBefore(clearData,passwordForm);
messages.credential_journal_mismatch='本机登录文件的恢复校验未通过，请保留数据并检查本机恢复记录。';
messages.current_password_incorrect='当前密码不正确。';

function restorePatientRecord(record){
 for(const [id,key]of [['age','age'],['duration','duration'],['chief-complaint','chief_complaint'],['patient-history','history'],['pasted-text','pasted_text']])$('#'+id).value=record.patient[key]??'';
 const select=$('#consultation-snapshot');if(![...select.options].some(o=>o.value===record.snapshot_id)){const option=node('option','历史症状版本 '+record.snapshot_revision);option.value=record.snapshot_id;select.append(option);}select.value=record.snapshot_id;
 state.patientSavedInput={...record.patient};state.dirty=false;
}
const checkLatest=node('button','核对最新症状，保留当前填写','audit-secondary');checkLatest.type='button';
checkLatest.addEventListener('click',()=>run('正在读取最新症状…',async()=>{
 const data=await api(url('/snapshots')),latest=data.snapshots[0];
 const labels={age:'年龄',chief_complaint:'主要不适',duration:'持续时间',history:'病史',pasted_text:'补充'};
 const text=Object.entries(latest?.patient||{}).map(([k,v])=>(labels[k]||k)+'：'+v).join('；');
 if(!window.confirm('服务器最新症状：'+(text||'尚无记录')+'。是否保留当前填写，并在下次提交时基于最新版本保存？'))return;
 state.revision=latest?.revision||0;state.patientSavedInput=null;state.dirty=true;state.ticket=null;
 say('当前填写和问题均已保留。已核对最新版本；请确认后再提交，不会自动发送。',true);
}));symptomDetails.append(checkLatest);
