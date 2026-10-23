const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(path.join(process.env.AUDIT_PLAYWRIGHT_MODULES,'playwright'));
const origin='http://127.0.0.1:8012',out=process.env.ENT_QA_RESUME||'evaluations/reports/patient-real-5.5/'+new Date().toISOString().replace(/[:.]/g,'-');
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.AUDIT_BROWSER_EXECUTABLE});
 const context=await browser.newContext({viewport:{width:1280,height:900}}),page=await context.newPage(),errors=[],submitted=[],records=[],checks=[];
 const username=process.env.ENT_QA_USERNAME,password=process.env.ENT_QA_PASSWORD;delete process.env.ENT_QA_PASSWORD;
 page.on('pageerror',e=>errors.push(e.message));
 page.on('request',r=>{if(r.method()==='POST'&&/\/consultations$/.test(r.url()))submitted.push(r.postDataJSON());});
 const get=async suffix=>{const r=await context.request.get(origin+'/api/v1/business'+suffix);assert.equal(r.status(),200);return r.json();};
 try{
  await page.goto(origin+'/patient');await page.waitForLoadState('networkidle');
  const login=async()=>{await page.locator('#username').fill(username);await page.locator('#password').fill(password);await page.locator('#login-form button').click();await page.locator('#patient-detail').waitFor();};
  await login();const patients=(await get('/patients')).patients;assert.equal(patients.length,1);const patient=patients[0].patient_id;
  const endpoint='/patients/'+patient;
  const cases=[{id:'general',duration:'3天',question:'声嘶资料中描述了哪些声音变化？',expect:'answered'},{id:'changed',duration:'5天',question:'声音嘶哑资料如何描述声音变化？',expect:'answered'},{id:'broad',duration:'5天',question:'怎么办',expect:'insufficient_evidence'}];
  if(!process.env.ENT_QA_RESUME)fs.writeFileSync(out+'/manifest.json',JSON.stringify({synthetic_only:true,cases,maximum_submissions:3,automatic_retries:false,medical_acceptance:false},null,2));
  await page.locator('#age').fill('40');await page.locator('#chief-complaint').fill('声音嘶哑');
  for(const c of cases){
   await page.locator('#duration').fill(c.duration);await page.locator('#consultation-question').fill(c.question);await page.locator('#consultation-consent').check();
   let record;if(process.env.ENT_QA_RESUME){record=JSON.parse(fs.readFileSync(out+'/'+c.id+'.json','utf8'));record=await get(endpoint+'/consultations/'+record.consultation_id);}else{
   const response=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/consultations'));
   await page.locator('#consultation-submit').click();const r=await response;assert(r.ok(),String(r.status()));const submittedRecord=await r.json();
   const deadline=Date.now()+600000;
   while(Date.now()<deadline){record=await get(endpoint+'/consultations/'+submittedRecord.consultation_id);if(!['queued','running'].includes(record.state))break;await page.waitForTimeout(2000);}
   fs.writeFileSync(out+'/'+c.id+'.json',JSON.stringify(record,null,2));}
   records.push(record);
   assert.equal(record.state,'completed');assert.equal(record.patient.duration,c.duration);assert.equal(record.question,c.question);
   if(c.id!=='broad')assert.equal(record.result.answer.status,c.expect,JSON.stringify(record.result.validation));else assert(['answered','insufficient_evidence','needs_information'].includes(record.result.answer.status));
   if(record.result.answer.status==='answered'){
    assert(record.result.answer.patient_summary.length>0);assert(record.result.citations.length>0);
    const refs=new Map(record.result.citations.map(e=>[e.evidence_id,e]));let supports=0;
    for(const key of ['professional','patient_summary'])for(const claim of record.result.answer[key]||[])for(const support of claim.supports||[]){const ref=refs.get(support.evidence_id);assert(ref);assert(ref.text.includes(support.quote));supports++;}
    assert(supports>0);checks.push(c.id+'_saved_answer_summary_and_exact_quotes');
   }else checks.push('broad_question_safely_withheld');
   await page.locator('#refresh-consultations').click();await page.locator('#consultation-list article').first().getByRole('button').click();
   if(record.result.answer.status==='answered')await page.locator('.answer-section').first().waitFor();else await page.locator('#patient-next-actions').waitFor();
   await page.screenshot({path:out+'/'+c.id+'.png',fullPage:true});
   console.log(c.id,record.state,record.result.answer.status);
  }
  const snapshots=(await get(endpoint+'/snapshots')).snapshots;assert.equal(snapshots.length,2);assert.equal(snapshots[0].patient.duration,'5天');assert.equal(snapshots[1].patient.duration,'3天');checks.push('changed_symptoms_new_version_same_symptoms_reused');
  await page.reload();await page.waitForLoadState('networkidle');await page.locator('#consultation-list article').first().waitFor();assert.equal((await get(endpoint+'/consultations')).consultations.length,3);
  await page.locator('#logout').click();await page.locator('#login-panel').waitFor();await login();
  for(const saved of records){const fresh=await get(endpoint+'/consultations/'+saved.consultation_id);assert.deepEqual(fresh.result,saved.result);assert.deepEqual(fresh.patient,saved.patient);}
  assert.equal(submitted.length,process.env.ENT_QA_RESUME?0:3);assert.deepEqual(errors,[]);checks.push('refresh_and_relogin_preserve_results_without_resubmission');
  fs.writeFileSync(out+'/checks.json',JSON.stringify({passed:true,checks,errors,consultation_submissions:submitted.length,total_saved_consultations:3,resumed_readonly:!!process.env.ENT_QA_RESUME,synthetic_only:true,real_provider:true,medical_acceptance:false},null,2));
 }catch(e){fs.writeFileSync(out+'/failure.json',JSON.stringify({error:e.message,checks,submissions:submitted.length,errors},null,2));await page.screenshot({path:out+'/failure.png',fullPage:true});throw e;}finally{await browser.close();}
})().catch(e=>{console.error(e.message);process.exit(1);});
