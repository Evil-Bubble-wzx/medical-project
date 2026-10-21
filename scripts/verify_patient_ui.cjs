const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(path.join(process.env.AUDIT_PLAYWRIGHT_MODULES,'playwright'));
const origin='http://127.0.0.1:8012',base='/api/v1/business',password='Synthetic-password-only-123';
const output=path.resolve(process.env.PATIENT_REPORT_DIR||'evaluations/reports/patient-ui-1.8');fs.mkdirSync(output,{recursive:true});
const checks=[],errors=[];const check=s=>{checks.push(s);console.log(s);};
(async()=>{
  const browser=await chromium.launch({headless:true,executablePath:process.env.AUDIT_BROWSER_EXECUTABLE});
  const contexts=[];
  async function page(){const c=await browser.newContext({viewport:{width:1440,height:1000}});contexts.push(c);const p=await c.newPage();p.on('pageerror',e=>errors.push(e.message));await p.goto(origin+'/patients');await p.waitForLoadState('networkidle');return p;}
  async function login(p,name){await p.locator('#username').fill(name);await p.locator('#password').fill(password);await p.locator('#login-form button').click();await p.locator('#identity').filter({hasText:name}).waitFor();await p.waitForFunction(()=>!state.busy);}
  async function save(p,text){await p.locator('#chief-complaint').fill(text);await p.locator('#snapshot-synthetic').check();await p.locator('#snapshot-form button[type=submit]').click();await p.locator('#patient-message.success').filter({hasText:'已保存版本'}).waitFor();await p.waitForFunction(()=>!state.busy);}
  try{
    if(process.argv.includes('--live-only')){await verifyLive(browser);return;}
    const a=await page();const proof=await (await a.request.get(origin+'/fixture-proof')).json();
    assert.equal(proof.scope,'patient-ui-synthetic-fixture');assert.deepEqual(proof.accounts,['patient-a','patient-b','doctor-a']);
    await a.locator('#username').fill('patient-a');await a.locator('#password').fill('wrong');await a.locator('#login-form button').click();await a.locator('#patient-message').filter({hasText:'账号或密码不正确'}).waitFor();assert.equal(await a.locator('#password').inputValue(),'');check('login_failure_clears_password');
    await login(a,'patient-a');assert(await a.locator('#profile-form').isVisible());
    await a.locator('#patient-label').fill('<img src=x onerror=alert(1)> Synthetic A');await a.locator('#profile-form button').click();assert(await a.locator('#profile-form').isVisible());
    await a.locator('#profile-synthetic').check();await a.locator('#profile-form button').click();await a.locator('#patient-message.success').filter({hasText:'合成档案已建立'}).waitFor();assert.equal(await a.locator('img').count(),0);check('profile_requires_explicit_synthetic_confirmation_and_safe_text');
    await a.locator('#age').fill('35');await a.locator('#duration').fill('Synthetic duration');await a.locator('#patient-history').fill('Synthetic history');await a.locator('#pasted-text').fill('Synthetic pasted');await save(a,'Synthetic complaint v1');await save(a,'Synthetic complaint v2');assert.equal(await a.locator('#snapshots details').count(),2);assert((await a.locator('#snapshots').textContent()).includes('Synthetic complaint v1'));check('snapshot_versions_preserve_original');
    await a.reload();await a.waitForLoadState('networkidle');await a.locator('#patient-revision').filter({hasText:'当前资料版本 2'}).waitFor();assert.equal(await a.locator('#chief-complaint').inputValue(),'Synthetic complaint v2');assert.equal(await a.locator('#snapshot-synthetic').isChecked(),false);check('login_and_saved_snapshot_survive_reload_without_auto_consent');
    const d=await page();await login(d,'doctor-a');assert((await d.locator('#patient-list').textContent()).includes('暂无有效授权'));assert(await d.locator('#profile-form').isHidden());check('doctor_has_no_ungranted_patients');
    const doctorId=await a.locator('#doctor option').nth(1).getAttribute('value');await a.locator('#doctor').selectOption(doctorId);a.once('dialog',x=>x.accept());await a.locator('#grant-form button').click();await a.locator('#patient-message.success').filter({hasText:'访问授权已建立'}).waitFor();
    await d.locator('#refresh-patients').click();await d.locator('#patient-revision').filter({hasText:'当前资料版本 2'}).waitFor();assert(await d.locator('#grants-panel').isHidden());assert.equal(await d.locator('#chief-complaint').inputValue(),'Synthetic complaint v2');check('doctor_reads_same_history_after_patient_grant');
    await d.locator('#duration').fill('Unsaved synthetic duration');d.once('dialog',x=>x.dismiss());await d.locator('#refresh-patients').click();assert.equal(await d.locator('#duration').inputValue(),'Unsaved synthetic duration');check('unsaved_changes_cancel_refresh');
    await save(a,'Synthetic complaint v3');await d.locator('#chief-complaint').fill('Conflicting synthetic input');await d.locator('#snapshot-synthetic').check();await d.locator('#snapshot-form button[type=submit]').click();await d.locator('#patient-message').filter({hasText:'资料已被另一页面更新'}).waitFor();assert.equal(await d.locator('#chief-complaint').inputValue(),'Conflicting synthetic input');check('version_conflict_preserves_local_input');
    d.once('dialog',x=>x.accept());await d.locator('#reload-patient').click();await d.locator('#patient-revision').filter({hasText:'当前资料版本 3'}).waitFor();assert.equal(await d.locator('#chief-complaint').inputValue(),'Synthetic complaint v3');check('explicit_reload_resolves_conflict');
    await d.route('**/api/v1/business/patients/*/snapshots',r=>r.request().method()==='POST'?r.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:{error_code:'business_component_unavailable'}})}):r.continue(),{times:1});
    await d.locator('#chief-complaint').fill('Synthetic retained after failure');await d.locator('#snapshot-synthetic').check();await d.locator('#snapshot-form button[type=submit]').click();await d.locator('#patient-message').filter({hasText:'资料服务暂不可用'}).waitFor();assert.equal(await d.locator('#chief-complaint').inputValue(),'Synthetic retained after failure');check('save_failure_keeps_input');
    a.once('dialog',x=>x.accept());await a.locator('#grants-list button').click();await a.locator('#patient-message.success').filter({hasText:'授权已撤销'}).waitFor();d.once('dialog',x=>x.accept());await d.locator('#reload-patient').click();await d.locator('#patient-message').filter({hasText:'访问授权已失效'}).waitFor();assert(await d.locator('#patient-detail').isHidden());assert.equal(await d.locator('#chief-complaint').inputValue(),'');assert.equal(await d.locator('#patient-list').textContent(),'');check('revocation_blocks_access_and_clears_visible_patient');
    const b=await page();await login(b,'patient-b');assert(await b.locator('#profile-form').isVisible());assert.equal(await b.locator('#patient-list button').count(),0);
    const list=await (await a.request.get(origin+base+'/patients')).json();const id=list.patients[0].patient_id;
    const cross=await b.request.get(origin+base+'/patients/'+id+'/snapshots');assert.equal(cross.status(),404);assert(!(await cross.text()).includes('Synthetic complaint'));check('second_patient_cannot_read_first_patient');
    // Seed extra versions only in the proven synthetic fixture to exercise paging.
    for(let revision=3;revision<24;revision++){const response=await a.request.post(origin+base+'/patients/'+id+'/snapshots',{headers:{Origin:origin},data:{synthetic_only:true,expected_revision:revision,age:35,chief_complaint:'Synthetic page '+(revision+1)}});assert.equal(response.status(),200);}
    await a.locator('#refresh-patients').click();await a.locator('#patient-revision').filter({hasText:'当前资料版本 24'}).waitFor();assert.equal(await a.locator('#snapshots details').count(),20);await a.locator('#more-snapshots').click();await a.waitForFunction(()=>document.querySelectorAll('#snapshots details').length===24);check('history_pagination_appends_without_overwriting_form');
    await a.screenshot({path:path.join(output,'desktop.png'),fullPage:true});await a.setViewportSize({width:390,height:844});await a.screenshot({path:path.join(output,'mobile.png'),fullPage:true});assert(await a.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));assert.equal(await a.evaluate(()=>localStorage.length+sessionStorage.length),0);check('mobile_layout_and_no_browser_storage');
    await a.locator('#logout').click();await a.locator('#patient-message.success').filter({hasText:'已退出'}).waitFor();assert(await a.locator('#patient-workspace').isHidden());assert.equal(await a.locator('#snapshots').textContent(),'');assert.equal(await a.locator('#chief-complaint').inputValue(),'');check('logout_clears_patient_content');
    await login(a,'patient-a');await a.route('**/api/v1/business/me',r=>r.fulfill({status:401,contentType:'application/json',body:JSON.stringify({detail:{error_code:'login_required'}})}),{times:1});await a.locator('#refresh-patients').click();await a.locator('#patient-message').filter({hasText:'登录已失效'}).waitFor();assert(await a.locator('#login-panel').isVisible());assert.equal(await a.locator('#chief-complaint').inputValue(),'');check('expired_session_returns_to_login_and_clears_patient_content');
    assert.deepEqual(errors,[]);check('no_browser_javascript_errors');fs.writeFileSync(path.join(output,'browser-check.json'),JSON.stringify({passed:true,synthetic_fixture_only:true,checks,errors},null,2));
  }catch(e){for(let i=0;i<contexts.length;i++){const p=contexts[i].pages()[0];await p.screenshot({path:path.join(output,'failure-'+i+'.png'),fullPage:true}).catch(()=>{});}throw e;}
  finally{for(const c of contexts)await c.close();await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});

async function verifyLive(browser){
  const context=await browser.newContext({viewport:{width:1440,height:1000}});
  try{
    const page=await context.newPage(),posts=[],liveErrors=[];
    page.on('request',r=>{if(r.method()==='POST')posts.push(r.url());});
    page.on('pageerror',e=>liveErrors.push(e.message));
    await page.goto('http://127.0.0.1:8011/patients');await page.waitForLoadState('networkidle');
    await page.locator('#patient-message').filter({hasText:'请使用本机开发账号登录'}).waitFor();
    assert(await page.locator('#login-panel').isVisible());assert(await page.locator('#patient-workspace').isHidden());
    assert.equal(await page.locator('#password').inputValue(),'');assert.equal(await page.locator('#snapshots').textContent(),'');
    await page.screenshot({path:path.join(output,'real-login-desktop.png'),fullPage:true});
    await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(output,'real-login-mobile.png'),fullPage:true});
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
    assert.deepEqual(posts,[]);assert.deepEqual(liveErrors,[]);
    fs.writeFileSync(path.join(output,'real-page.json'),JSON.stringify({passed:true,login_visible:true,patient_workspace_hidden:true,post_requests:0,errors:liveErrors},null,2));
    console.log('real_login_page_checked_without_posts');
  }finally{await context.close();}
}
