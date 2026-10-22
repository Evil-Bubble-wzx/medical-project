const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(path.join(process.env.AUDIT_PLAYWRIGHT_MODULES,'playwright'));
const output=path.resolve('evaluations/reports/doctor-trial-4.5/browser');fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.AUDIT_BROWSER_EXECUTABLE});
 const context=await browser.newContext({viewport:{width:1440,height:1000}}),page=await context.newPage();
 const errors=[],checks=[];page.on('pageerror',e=>errors.push(e.message));const check=name=>checks.push(name);
 try{
  await page.goto('http://127.0.0.1:8013/doctor');await page.waitForLoadState('networkidle');
  assert((await page.locator('h1').textContent()).includes('选病例'));check('doctor_entry_and_trial_guidance');
  await page.locator('#username').fill('doctor-trial');await page.locator('#password').fill('Synthetic-password-only-123');await page.locator('#login-form button').click();await page.locator('#account-panel').waitFor();
  await page.waitForFunction(()=>document.querySelectorAll('#patient-list button').length===6);check('doctor_login_six_assigned_cases');
  await page.locator('#patient-list button').first().click();await page.locator('#trial-case-note').filter({hasText:'TRIAL-01'}).waitFor();
  await page.locator('#trial-example').click();assert((await page.locator('#consultation-question').inputValue()).length>0);check('case_snapshot_and_suggested_question');
  await page.locator('#consultation-consent').check();await page.locator('#consultation-submit').click();await page.locator('#trial-feedback-form').waitFor({timeout:30000});
  await page.locator('.answer-reference').first().locator('summary').click();assert((await page.locator('.answer-reference blockquote').first().textContent()).includes('synthetic'));check('background_consultation_answer_and_traceable_reference');
  await page.locator('#feedback-overall').selectOption('issue');await page.locator('#trial-feedback-form button').click();await page.locator('#feedback-status').filter({hasText:'请填写具体说明'}).waitFor();check('issue_requires_comment');
  await page.locator('#feedback-comment').fill('Synthetic doctor trial: reference is visible; wording needs review.');await page.locator('#trial-feedback-form button').click();await page.locator('#feedback-status').filter({hasText:'第 1 版'}).waitFor();check('feedback_saved_without_medical_approval');
  await page.reload();await page.waitForLoadState('networkidle');await page.locator('#patient-list button').first().click();await page.locator('#consultation-list button').first().click();await page.locator('#trial-feedback-form').waitFor();assert((await page.locator('#feedback-comment').inputValue()).includes('Synthetic doctor trial'));check('refresh_history_feedback_persists_without_regeneration');
  const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#export-trial-feedback').click()]);const data=JSON.parse(fs.readFileSync(await download.path(),'utf8'));assert.equal(data.reviews.length,1);assert.equal(data.clinical_approval,false);fs.writeFileSync(path.join(output,'feedback-export.json'),JSON.stringify(data,null,2));check('own_feedback_export');
  const state=await page.evaluate(()=>({patient:window.document.querySelector('#consultation-result details')?true:false}));assert(state.patient);
  const patients=await (await context.request.get('http://127.0.0.1:8013/api/v1/business/patients')).json();const patient=patients.patients[0].patient_id;
  const records=await (await context.request.get(`http://127.0.0.1:8013/api/v1/business/patients/${patient}/consultations`)).json();assert.equal(records.consultations.length,1);
  const endpoint=`http://127.0.0.1:8013/api/v1/business/patients/${patient}/consultations/${records.consultations[0].id}/feedback`;
  const bound=await (await context.request.get(endpoint)).json();const post=await context.request.post(endpoint,{headers:{Origin:'http://127.0.0.1:8013'},data:{...bound.review.review,expected_revision:bound.revision,result_hash:bound.result_hash}});assert.equal(post.status(),200);
  await page.locator('#feedback-comment').fill('Unsaved conflict note should remain.');await page.locator('#trial-feedback-form button').click();await page.locator('#patient-message').filter({hasText:'当前填写仍保留'}).waitFor();assert.equal(await page.locator('#feedback-comment').inputValue(),'Unsaved conflict note should remain.');check('concurrent_feedback_conflict_keeps_input');
  await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(output,'desktop.png'),fullPage:true});await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(output,'mobile.png'),fullPage:true});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));check('mobile_no_horizontal_overflow');
  page.once('dialog',d=>d.accept());await page.locator('#logout').click();await page.locator('#login-panel').waitFor();assert(await page.locator('#trial-feedback-panel').isHidden());assert.equal(await page.locator('#feedback-comment').count(),0);check('logout_clears_feedback_and_patient_data');
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(output,'checks.json'),JSON.stringify({passed:true,synthetic_fixture_only:true,checks,errors,provider_calls:0},null,2));
 }catch(e){await page.screenshot({path:path.join(output,'failure.png'),fullPage:true});throw e;}
 finally{await context.close();await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
