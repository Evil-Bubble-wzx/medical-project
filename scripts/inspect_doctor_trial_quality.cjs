const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(path.join(process.env.AUDIT_PLAYWRIGHT_MODULES,'playwright'));
const output=path.resolve('evaluations/reports/doctor-trial-quality-4.6/browser');fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.AUDIT_BROWSER_EXECUTABLE});
 const context=await browser.newContext({viewport:{width:1440,height:1000}}),page=await context.newPage(),checks=[],errors=[],blocked=[];
 page.on('pageerror',e=>errors.push(e.message));await context.route('**/api/**',route=>{const r=route.request();if(r.method()!=='GET'&&!r.url().endsWith('/login')){blocked.push(r.url());return route.abort();}return route.continue();});
 try{
  await page.goto('http://127.0.0.1:8012/doctor');await page.waitForLoadState('networkidle');await page.locator('#username').fill('doctor-trial');await page.locator('#password').fill(process.env.ENT_TRIAL_PASSWORD);delete process.env.ENT_TRIAL_PASSWORD;await page.locator('#login-form button').click();await page.locator('#account-panel').waitFor();
  const cases=JSON.parse(fs.readFileSync('configs/doctor-trial-cases.json','utf8')).cases;
  for(const item of cases){
   await page.getByRole('button',{name:item.label,exact:true}).click();await page.locator('#trial-case-note').filter({hasText:item.id}).waitFor();await page.locator('#consultation-list button').first().click();await page.locator('#consultation-result').waitFor();
   if(item.id==='TRIAL-06'){await page.locator('#consultation-result').getByText('本试用版不提供个体处方或用药剂量；补充信息也不会解除这一边界，可改问资料中的一般知识。',{exact:true}).waitFor();checks.push('prescription_boundary_visible_after_saved_history');await page.screenshot({path:path.join(output,'prescription-boundary.png'),fullPage:true});}
   if(['TRIAL-01','TRIAL-02','TRIAL-03','TRIAL-04'].includes(item.id)){
    await page.locator('#trial-feedback-form').waitFor();const texts=await page.locator('.answer-section').last().locator(':scope > p').allTextContents();assert(texts.length);assert(!texts.some(t=>/raspy|strained/i.test(t)));checks.push(item.id+'_patient_summary_no_known_unexplained_terms');
   }
   if(item.id==='TRIAL-02'){assert(/结合输入的资料比较|已填信息核对（不是个体解释）/.test(await page.locator('#consultation-result').textContent()));checks.push('comparison_label_distinct_from_input_record');await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(output,'desktop.png'),fullPage:true});await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(output,'mobile.png'),fullPage:true});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));await page.setViewportSize({width:1440,height:1000});checks.push('mobile_layout');}
  }
  assert.deepEqual(errors,[]);assert.deepEqual(blocked,[]);fs.writeFileSync(path.join(output,'checks.json'),JSON.stringify({passed:true,checks,errors,additional_generation_requests:0,history_only:true},null,2));
 }catch(e){await page.screenshot({path:path.join(output,'failure.png'),fullPage:true});throw e;}finally{await context.close();await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
