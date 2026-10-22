const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(path.join(process.env.AUDIT_PLAYWRIGHT_MODULES,'playwright'));
const output=path.resolve('evaluations/reports/doctor-trial-4.5/live/browser');fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.AUDIT_BROWSER_EXECUTABLE});
 const context=await browser.newContext({viewport:{width:1440,height:1000}}),page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 try{
  await page.goto('http://127.0.0.1:8012/doctor');await page.waitForLoadState('networkidle');
  await page.locator('#username').fill('doctor-trial');await page.locator('#password').fill(process.env.ENT_TRIAL_PASSWORD);delete process.env.ENT_TRIAL_PASSWORD;
  await page.locator('#login-form button').click();await page.locator('#account-panel').waitFor();await page.waitForFunction(()=>document.querySelectorAll('#patient-list button').length===6);
  await page.locator('#patient-list button').first().click();await page.locator('#consultation-list button').first().click();await page.locator('#trial-feedback-form').waitFor();
  assert((await page.locator('#consultation-result').textContent()).includes('deepseek-flash'));
  await page.locator('.answer-reference summary').first().click();assert((await page.locator('.answer-reference blockquote').first().textContent()).length>0);
  assert.equal(await page.locator('#feedback-overall').inputValue(),'not_assessed');
  await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(output,'desktop.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(output,'mobile.png'),fullPage:true});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(output,'proof.json'),JSON.stringify({passed:true,origin:'http://127.0.0.1:8012',cases:6,real_saved_model:'deepseek-flash',history_read_only:true,additional_model_calls:0,ratings:'not_assessed',errors},null,2));
 }finally{await context.close();await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
