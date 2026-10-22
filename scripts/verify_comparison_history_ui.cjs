const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(path.join(process.env.AUDIT_PLAYWRIGHT_MODULES,'playwright'));
const output=path.resolve('evaluations/reports/comparison-classification-4.7/browser');fs.mkdirSync(output,{recursive:true});
(async()=>{
 const packet=JSON.parse(fs.readFileSync('evaluations/reports/doctor-trial-quality-4.6/review/pending-medical-review.json','utf8'));
 const old=packet.items.find(i=>i.attention_flags?.length&&i.case_id==='TRIAL-01');
 const folders=fs.readdirSync('evaluations/reports/comparison-classification-4.7/live-final').filter(n=>n.startsWith('R'));
 const partial=folders.map(n=>({name:n,value:JSON.parse(fs.readFileSync(`evaluations/reports/comparison-classification-4.7/live-final/${n}/consultation.json`,'utf8'))})).find(x=>x.value.result?.validation?.input_comparison_withheld);
 assert(partial,'A real saved partial-result branch must exist for this check');
 const cases=JSON.parse(fs.readFileSync('configs/doctor-trial-cases.json','utf8')).cases;
 const browser=await chromium.launch({headless:true,executablePath:process.env.AUDIT_BROWSER_EXECUTABLE});const context=await browser.newContext({viewport:{width:1440,height:1000}}),page=await context.newPage(),errors=[],blocked=[],checks=[];
 page.on('pageerror',e=>errors.push(e.message));await context.route('**/api/**',route=>{const r=route.request();if(r.method()!=='GET'&&!r.url().endsWith('/login')){blocked.push(r.url());return route.abort();}return route.continue();});
 async function open(caseId,run){const item=cases.find(c=>c.id===caseId);await page.getByRole('button',{name:item.label,exact:true}).click();await page.locator(`#consultation-list [data-run-id="${run}"] button`).click();await page.locator('#trial-feedback-form').waitFor();}
 try{
  await page.goto('http://127.0.0.1:8012/doctor');await page.waitForLoadState('networkidle');await page.locator('#username').fill('doctor-trial');await page.locator('#password').fill(process.env.ENT_TRIAL_PASSWORD);delete process.env.ENT_TRIAL_PASSWORD;await page.locator('#login-form button').click();await page.locator('#account-panel').waitFor();
  await open('TRIAL-01',old.consultation_id);await page.locator('#consultation-result').getByText('历史输入段（分类待复核）',{exact:true}).waitFor();assert((await page.locator('#consultation-result').textContent()).includes('未改写原结果'));checks.push('historical_category_warning_and_nonapproval_label');await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(output,'historical-warning.png'),fullPage:true});
  const caseId=partial.name.split('-').slice(1).join('-');await open(caseId,partial.value.consultation_id);await page.locator('#consultation-result').getByText('本次输入比较未通过分类核对，该段已隐藏；以下仅提供一般资料，不能当作针对本人情况的解释。',{exact:true}).waitFor();assert((await page.locator('#consultation-result').textContent()).includes('专业资料与解释'));checks.push('withheld_comparison_disclosed_while_retained_knowledge_visible');assert(partial.value.result.answer.input_explanation.length===0);checks.push('no_rejected_comparison_relabelled_as_input_record');
  await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(output,'withheld-section.png'),fullPage:true});await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(output,'mobile.png'),fullPage:true});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));checks.push('mobile_layout');assert.deepEqual(errors,[]);assert.deepEqual(blocked,[]);
  fs.writeFileSync(path.join(output,'checks.json'),JSON.stringify({passed:true,checks,errors,history_only:true,additional_generation_requests:0},null,2));
 }catch(e){await page.screenshot({path:path.join(output,'failure.png'),fullPage:true});throw e;}finally{await context.close();await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
