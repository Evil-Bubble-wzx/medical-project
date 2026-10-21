const form=document.querySelector('#query-form');
const message=document.querySelector('#form-message');
let activeRun=null;
let generation=0;
let generationReady=false;
let workbenchBusy=false;
const el=(tag,text,cls)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(cls)node.className=cls;return node;};
async function api(path,body){
  const response=await fetch(path,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json'}:{},body:body?JSON.stringify(body):undefined,cache:'no-store'});
  const data=await response.json();
    if(!response.ok){
      const detail=data.detail;
      const message=typeof detail==='object'&&detail!==null?`${detail.message} (${detail.error_code})`:detail;
      throw new Error(data.message||message||'请求未完成，请稍后重试。');
    }
  return data;
}
function renderCard(chunk,index,strategy,run){
  const card=el('article',undefined,'card');
  const top=el('div',undefined,'card-top');top.append(el('span',`# ${String(index+1).padStart(2,'0')}`,'rank'),el('span','待临床审核','tag'));
  card.append(top,el('h4',chunk.title),el('p',chunk.section,'section'),el('p',chunk.text.length>220?chunk.text.slice(0,220)+'…':chunk.text,'excerpt'));
  if(chunk.applicability_warning)card.append(el('p',chunk.applicability_warning,'applicability-warning'));
  const detail=el('details');detail.append(el('summary','查看原文与引用依据'),el('p',chunk.text,'full-text'));
  const citation=el('div',undefined,'citation');
  citation.append(el('div',`资料：${chunk.document_id}`),el('div',`版本：${chunk.version_id}`),el('div',`片段：${chunk.chunk_id}`),el('div',`定位：${chunk.locator} · 字符 ${chunk.start}–${chunk.end}`));
  try{const url=new URL(chunk.source_url);if(['http:','https:'].includes(url.protocol)){const link=el('a','打开原始来源 ↗');link.href=url.href;link.target='_blank';link.rel='noreferrer noopener';citation.append(link);}}catch{}
  if(typeof chunk.rerank_score==='number')citation.append(el('div',`重排序分：${chunk.rerank_score.toFixed(3)}（非医学可信度）`));
  detail.append(citation);card.append(detail);
  const buttons=el('div',undefined,'review-actions');const state=el('div','','review-state');
  for(const [judgment,label] of [['relevant','相关'],['irrelevant','不相关'],['insufficient','证据不足']]){
    const button=el('button',label);button.type='button';
    button.addEventListener('click',async()=>{
      if(activeRun!==run){state.textContent='请对最新一次检索结果进行标记。';return;}
      const all=[...buttons.querySelectorAll('button')];all.forEach(b=>b.disabled=true);state.textContent='保存中…';
      try{await api('/api/v1/validation/reviews',{run_id:run.run_id,strategy,version_id:chunk.version_id,chunk_id:chunk.chunk_id,judgment});all.forEach(b=>b.classList.toggle('active',b===button));state.textContent=`已记录：${label}`;}
      catch(error){state.textContent=error.message;}finally{all.forEach(b=>b.disabled=false);}
    });buttons.append(button);
  }
  card.append(buttons,state);return card;
}
function render(result){
  activeRun=result;
  document.querySelector('#empty').hidden=true;document.querySelector('#columns').hidden=false;
  document.querySelector('#run-meta').hidden=false;
  document.querySelector('#run-meta').textContent=`快照 ${result.snapshot_id||'无'} · 本次处理 ${(result.elapsed_ms/1000).toFixed(1)}秒 · 本地不保存患者输入`;
  document.querySelector('#run-status').textContent='检索完成';
  for(const [mode,target] of [['hybrid','baseline'],['reranked','reranked']]){
    const container=document.querySelector('#'+target);container.replaceChildren();
    const hits=result[mode];document.querySelector('#'+target+'-count').textContent=mode==='reranked'&&!result.reranker_enabled?'未启用':`${hits.length} 条`;
    if(!hits.length)container.append(el('p',mode==='reranked'&&!result.reranker_enabled?'勾选左侧“对比重排序结果”后可查看。':'本次没有可展示的资料。可检查信息或调整问题；没有结果不代表医学上没有证据。','placeholder'));
    hits.forEach((chunk,index)=>container.append(renderCard(chunk,index,mode,result)));
  }
}
form.addEventListener('submit',async(event)=>{
  event.preventDefault();if(workbenchBusy)return;workbenchBusy=true;refreshGenerateButton();document.querySelector('#answer-panel').hidden=true;const ticket=++generation;const data=Object.fromEntries(new FormData(form));data.age=Number(data.age);data.compare_reranker=form.elements.compare_reranker.checked;
  const submit=document.querySelector('#submit');submit.disabled=true;message.textContent='正在本机检索'+(data.compare_reranker?'并进行重排序':'')+'…';document.querySelector('#run-status').textContent='处理中';
  try{const result=await api('/api/v1/validation/retrieve',data);if(ticket===generation){render(result);message.textContent='已完成。可展开原文，并标记资料相关性。';}}
  catch(error){if(ticket===generation){message.textContent=error.message;document.querySelector('#run-status').textContent='未完成';}}
  finally{submit.disabled=false;workbenchBusy=false;refreshGenerateButton();}
});
document.querySelector('#sample').addEventListener('click',()=>{Object.entries({age:35,chief_complaint:'反复鼻塞、打喷嚏',duration:'反复半年',history:'过敏性鼻炎病史',pasted_text:'',question:'成人过敏性鼻炎可能伴随哪些共病？'}).forEach(([key,value])=>form.elements[key].value=value);message.textContent='已填入模拟示例，可修改后检索。';});
document.querySelector('#clear').addEventListener('click',()=>{generation++;document.querySelector('#answer-panel').replaceChildren();document.querySelector('#answer-panel').hidden=true;form.reset();activeRun=null;message.textContent='';document.querySelector('#baseline').replaceChildren();document.querySelector('#reranked').replaceChildren();document.querySelector('#columns').hidden=true;document.querySelector('#run-meta').hidden=true;document.querySelector('#empty').hidden=false;document.querySelector('#run-status').textContent='等待检索';refreshGenerateButton();});
api('/api/v1/validation/status').then(status=>{document.querySelector('#library-count').textContent=`${status.chunks} 个资料片段`;document.querySelector('#library-state').textContent=status.model_available?'本地模型就绪 · 资料待审核':'本地模型待配置';form.elements.compare_reranker.disabled=!status.reranker_available;}).catch(()=>{document.querySelector('#library-count').textContent='连接未完成';document.querySelector('#library-state').textContent='请检查本地服务';});

function refreshGenerateButton(){document.querySelector('#generate').disabled=workbenchBusy||!generationReady||!document.querySelector('#synthetic-consent').checked;}
document.querySelector('#synthetic-consent').addEventListener('change',refreshGenerateButton);
function renderAnswer(result){
  const panel=document.querySelector('#answer-panel');panel.replaceChildren();panel.hidden=false;
  panel.append(el('h2','有引用的解释'),el('p',`${result.model} · 引用身份及摘录匹配${result.validation.citation_identity_and_quote_match?'通过':'未通过'} · 医学支持充分性待审核`,'answer-status'));
  const audit=result.validation.verification;
  const repair=result.validation.quote_repair;
  if(repair?.attempts)panel.append(el('p',repair.accepted?'已完成一次短引文格式修订，并重新检查原文匹配。':'短引文格式修订未通过，回答未展示。'));
  if(audit){
    const rejected=audit.claims.filter(c=>!c.supported).length;
    panel.append(el('p',`本次核验覆盖 ${audit.claims.length} 项输出，排除 ${rejected} 项。医学内容由模型核验，原话记录由程序逐字核对；尚未经临床审核。`));
    const labels={justified:'模型认为本次证据不足以回答',possible_over_refusal:'模型发现可能可回答的证据，需人工复查拒答',uncertain:'模型无法确定拒答是否合理'};
    if(labels[audit.refusal_assessment])panel.append(el('p',labels[audit.refusal_assessment]));
    const detail=el('details');detail.append(el('summary','查看模型核验记录'));
    for(const row of audit.claims)detail.append(el('p',`${row.claim_id} · ${row.supported?'保留':'排除'} · ${row.reason}`));
    for(const support of audit.refusal_supports)detail.append(el('blockquote',`[${support.evidence_id}] ${support.quote}`));
    panel.append(detail);
  }
  if(result.validation.schema_issues?.length){
    const detail=el('details');detail.append(el('summary','查看格式错误定位（不含输入或草稿）'));
    for(const row of result.validation.schema_issues)detail.append(el('p',`${row.path.join('.')} · ${row.rule}`));
    panel.append(detail);
  }
  const answer=result.answer;
  if(result.validation.scope_decision)panel.append(el('p',result.validation.scope_decision.message,'answer-message'));
  if(answer.status!=='answered'){
    const categories={input_binding_failed:'输入信息未能可靠对应，本次未展示解释。请核对所填内容。',model_format_failed:'模型输出格式不符合要求，本次未展示草稿。',content_rejected:'生成内容未通过证据或表达范围核验，本次未展示。',verification_failed:'本次证据核验未完成，尚无可展示的回答。',source_unavailable:'本次资料已不可用，需要重新检索。'};
    const reasons={insufficient_evidence:'现有证据不足，未生成解释。',needs_information:'需要补充信息，未生成解释。',validation_failed:'模型输出未通过引用或规则校验，原始回答未展示。'};
    panel.append(el('p',categories[result.validation.outcome_category]||reasons[answer.status]||'未能生成可展示的解释。','answer-message'));return;
  }
  const references=new Map(result.citations.map(c=>[c.evidence_id,c]));
  for(const [name,label] of [['professional','专业解释'],['input_explanation','结合输入的说明'],['patient_summary','患者易懂总结']]){
    const section=el('section',undefined,'answer-section');section.append(el('h3',label));
    if(!answer[name].length)section.append(el('p','证据暂不足以展开这一部分。'));
    for(const claim of answer[name]){
      section.append(el('p',claim.text));
      for(const anchor of claim.input_anchors||[]){const names={age:'年龄',chief_complaint:'主诉',duration:'病程',history:'病史',pasted_text:'补充记录',question:'问题'};const states={reported:'陈述',denied:'含否认信息',unknown:'含未知信息',mixed:'含否认及未知信息'};section.append(el('p',`${names[anchor.field]||anchor.field}原话（${states[anchor.state]||anchor.state}）：${anchor.quote}`,'audit-muted'));}
      for(const support of claim.supports){
        const source=references.get(support.evidence_id);if(!source)continue;
        const detail=el('details',undefined,'answer-reference');detail.append(el('summary',`[${support.evidence_id}] ${source.title}`),el('blockquote',support.quote),el('div',`原文定位：${source.locator} · 版本 ${source.version_id}`));
        try{const url=new URL(source.source_url);if(['http:','https:'].includes(url.protocol)){const link=el('a','查看原始来源 ↗');link.href=url.href;link.target='_blank';link.rel='noopener noreferrer';detail.append(link);}}catch{}
        section.append(detail);
      }
    }panel.append(section);
  }
}
document.querySelector('#generate').addEventListener('click',async()=>{
  if(workbenchBusy||!form.reportValidity()||!generationReady||!document.querySelector('#synthetic-consent').checked)return;
  workbenchBusy=true;const ticket=++generation;const button=document.querySelector('#generate');button.disabled=true;document.querySelector('#submit').disabled=true;
  document.querySelector('#answer-panel').hidden=true;message.textContent='正在检索、生成并进行分阶段证据核验…';
  const data=Object.fromEntries(new FormData(form));data.age=Number(data.age);data.compare_reranker=form.elements.compare_reranker.checked;data.synthetic_only=true;
  try{const result=await api('/api/v1/validation/answer',data);if(ticket===generation){render(result.retrieval);renderAnswer(result);message.textContent='生成流程完成；请检查引用与原文是否充分支持解释。';}}
  catch(error){if(ticket===generation)message.textContent=error.message;}
  finally{workbenchBusy=false;document.querySelector('#submit').disabled=false;refreshGenerateButton();}
});
api('/api/v1/validation/status').then(status=>{
  generationReady=status.generation_state==='ready';
  document.querySelector('#generation-status').textContent=generationReady?`${status.generation_model} · ${status.generation_destination}`:'DeepSeek V4.1 Flash · 需在本机配置API密钥并重启';
  refreshGenerateButton();
}).catch(()=>{document.querySelector('#generation-status').textContent='生成状态未能读取';});
