// Refuse writes until the dedicated 8012 server proves its synthetic S1/Q1/B1 inventory.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = require(path.join(process.env.AUDIT_PLAYWRIGHT_MODULES, 'playwright'));
const origin = 'http://127.0.0.1:8012';
const output = path.resolve('evaluations/reports/development-ui-1.6');
fs.mkdirSync(output, {recursive:true});
const checks = [], errors = [];
const check = name => { checks.push(name); console.log(name); };
(async () => {
  const browser = await chromium.launch({headless:true, executablePath:process.env.AUDIT_BROWSER_EXECUTABLE});
  const context = await browser.newContext({viewport:{width:1440,height:1000}});
  const page = await context.newPage();
  page.on('pageerror', e => errors.push(e.message));
  try {
    if (process.argv.includes('--live-only')) { await verifyLive(browser); return; }
    await page.goto(origin + '/audit'); await page.waitForLoadState('networkidle');
    await page.getByRole('heading', {name:'Synthetic source', exact:true}).waitFor();
    const items = await (await page.request.get(origin + '/api/v1/validation/audit/items')).json();
    assert.deepEqual(items.items.map(i=>i.item_id).sort(), ['B1','Q1','S1']);
    assert(items.items.every(i=>i.revision===0));
    await page.locator('#dev-current').filter({hasText:'当前启用'}).waitFor();
    assert(await page.locator('#dev-plan').isDisabled());
    assert(await page.locator('#dev-prepare').isDisabled());
    assert(await page.locator('#dev-withdraw').isDisabled());
    check('pending_evidence_cannot_prepare');
    async function post(url, body) {
      const result = await page.request.post(origin+url, {data:body, headers:{Origin:origin}});
      assert.equal(result.status(), 200, await result.text()); return result.json();
    }
    const base = '/api/v1/validation/development';
    const initial = await (await page.request.get(origin+base+'/history')).json();
    // Seed declarations only after the synthetic identity guard. Actual release operations use UI.
    for (const [kind,id] of [['source','S1'],['case','Q1']]) {
      const url='/api/v1/validation/audit/items/'+kind+'/'+id;
      const item=await (await page.request.get(origin+url)).json();
      const review={decision:'accept',reviewer:'Synthetic browser reviewer',reviewed_at:new Date().toISOString(),notes:'Synthetic declaration only',
        ...(kind==='source' ? {adult_scope:'Synthetic adult scope',evidence_quality:'Synthetic limitations',conflicts_of_interest:'Synthetic funding',license_version_confirmed:true,source_family_aliases_checked:true}
        : {question_clarity:true,adult_applicability:true,evidence_sufficiency:true,scope_limitations:'Synthetic fixture only',additional_relevant_evidence:[]})};
      await post(url+'/submit',{binding_hash:item.binding_hash,expected_revision:item.revision,review});
    }
    await page.locator('#dev-refresh').click(); await page.locator('#dev-cases input[value=Q1]').waitFor();
    assert.equal(await page.locator('#dev-cases input').count(),1);
    await page.locator('#dev-cases input').check(); await page.locator('#dev-plan').click();
    await page.locator('#dev-preview').filter({hasText:'1 份来源 · 1 个证据片段'}).waitFor();
    check('selected_evidence_preview_scope');
    await page.locator('#dev-prepare').click();
    await page.locator('#dev-message').filter({hasText:'请先填写'}).waitFor();
    check('operator_and_reason_required');
    await page.locator('#dev-actor').fill('Synthetic operator'); await page.locator('#dev-note').fill('<img src=x onerror=alert(1)> Synthetic reason');
    await page.locator('#dev-prepare').click();
    await page.locator('#dev-message.success').filter({hasText:'尚未启用'}).waitFor();
    assert((await page.locator('#dev-current').textContent()).includes(initial.active_snapshot_id));
    assert(await page.locator('#dev-prepare').isDisabled());
    check('prepare_does_not_activate_and_clears_plan');
    const ready=page.locator('#dev-releases button[data-ready=true]').first();
    page.once('dialog', d=>d.dismiss()); await ready.click();
    assert((await page.locator('#dev-current').textContent()).includes(initial.active_snapshot_id));
    check('activation_cancel_preserves_current');
    page.once('dialog', d=>d.accept()); await ready.click();
    await page.locator('#dev-message.success').filter({hasText:'开发版本已启用'}).waitFor();
    const first=await (await page.request.get(origin+base+'/history')).json();
    assert.notEqual(first.active_snapshot_id, initial.active_snapshot_id);
    check('explicit_activation_updates_current');
    // A network failure must not erase the operator text or leave busy controls stuck.
    await page.locator('#dev-cases input').check(); await page.locator('#dev-plan').click();
    await page.locator('#dev-preview').waitFor({state:'visible'});
    await page.route('**/development/prepare', route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:{error_code:'development_index_failed_active_snapshot_preserved'}})}), {times:1});
    await page.locator('#dev-prepare').click();
    await page.locator('#dev-message').filter({hasText:'索引准备失败'}).waitFor();
    assert.equal(await page.locator('#dev-note').inputValue(),'<img src=x onerror=alert(1)> Synthetic reason');
    assert(await page.locator('#dev-prepare').isDisabled());
    assert.equal(await page.locator('img').count(),0);
    check('failure_preserves_operator_text_and_invalidates_plan');
    // Prepare another snapshot through the UI, then activate it elsewhere to create a conflict.
    await page.locator('#dev-plan').click(); await page.locator('#dev-preview').waitFor({state:'visible'});
    await page.locator('#dev-prepare').click();
    await page.locator('#dev-message.success').filter({hasText:'尚未启用'}).waitFor();
    const stage=await (await page.request.get(origin+base+'/history')).json();
    await post(base+'/activate',{snapshot:stage.releases[0].snapshot_id,expected_snapshot:first.active_snapshot_id,actor:'Other synthetic operator',note:'Synthetic concurrent activation'});
    page.once('dialog', d=>d.accept()); await page.locator('#dev-releases button[data-ready=true]').first().click();
    await page.locator('#dev-message').filter({hasText:'当前开发版本已被更新'}).waitFor();
    check('concurrent_activation_conflict_preserves_input');
    await page.locator('#dev-refresh').click(); await page.locator('#dev-message.success').filter({hasText:'版本状态已更新'}).waitFor();
    // Dirty review form must block release changes without discarding the review.
    await page.locator('#field-notes').fill('Unsaved synthetic review');
    await page.locator('#dev-plan').click(); await page.locator('#dev-message').filter({hasText:'未保存修改'}).waitFor();
    assert.equal(await page.locator('#field-notes').inputValue(),'Unsaved synthetic review');
    page.once('dialog', d=>d.accept()); await page.locator('#reload').click();
    await page.waitForFunction(()=>!state.busy);
    check('unsaved_review_blocks_release_operations');
    await page.locator('.development-maintenance summary').click();
    await page.locator('#dev-target').selectOption(initial.active_snapshot_id);
    page.once('dialog',d=>d.accept()); await page.locator('#dev-rollback').click();
    await page.locator('#dev-message.success').filter({hasText:'回滚快照已准备'}).waitFor();
    page.once('dialog',d=>d.accept()); await page.locator('#dev-releases button[data-ready=true]').first().click();
    await page.locator('#dev-message.success').filter({hasText:'开发版本已启用'}).waitFor();
    const empty=await (await page.request.get(origin+base+'/history')).json(); assert.equal(empty.active_versions.length,0);
    check('rollback_prepare_then_explicit_activation');
    // Reinclude, then withdraw the actual active bound development version.
    await page.locator('#dev-plan').click(); await page.locator('#dev-preview').waitFor({state:'visible'});
    await page.locator('#dev-prepare').click(); await page.locator('#dev-message.success').filter({hasText:'尚未启用'}).waitFor();
    page.once('dialog',d=>d.accept()); await page.locator('#dev-releases button[data-ready=true]').first().click();
    await page.locator('#dev-message.success').filter({hasText:'开发版本已启用'}).waitFor();
    const included=await (await page.request.get(origin+base+'/history')).json();
    await page.locator('#dev-version').selectOption(included.active_versions[0].version_id);
    page.once('dialog',d=>d.accept()); await page.locator('#dev-withdraw').click();
    await page.locator('#dev-message.success').filter({hasText:'所选资料已撤回'}).waitFor();
    const withdrawn=await (await page.request.get(origin+base+'/history')).json();
    assert.equal(withdrawn.active_versions[0].state,'withdrawn');
    assert.equal(await page.locator('#dev-version option').count(),1);
    check('withdraw_immediate_before_snapshot_activation');
    await page.locator('#dev-target').selectOption(first.active_snapshot_id);
    page.once('dialog',d=>d.accept()); await page.locator('#dev-rollback').click();
    await page.locator('#dev-message').filter({hasText:'已撤回或审核绑定失效'}).waitFor();
    check('rollback_cannot_resurrect_withdrawn_version');
    await page.screenshot({path:path.join(output,'desktop.png'),fullPage:true});
    await page.setViewportSize({width:390,height:844});
    await page.screenshot({path:path.join(output,'mobile.png'),fullPage:true});
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
    assert.deepEqual(errors,[]); check('mobile_layout_and_no_javascript_errors');
    fs.writeFileSync(path.join(output,'browser-check.json'),JSON.stringify({passed:true,synthetic_fixture_only:true,checks,errors},null,2));
    await verifyLive(browser);
  } catch(error) {
    await page.screenshot({path:path.join(output,'failure.png'),fullPage:true}).catch(()=>{});
    throw error;
  } finally { await context.close(); await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1;});

async function verifyLive(browser) {
    const realContext = await browser.newContext({viewport:{width:1440,height:1000}});
    try {
      const real = await realContext.newPage(), posts=[], realErrors=[];
      real.on('request',r=>{if(r.method()==='POST')posts.push(r.url());});
      real.on('pageerror',e=>realErrors.push(e.message));
      await real.goto('http://127.0.0.1:8011/audit'); await real.waitForLoadState('networkidle');
      await real.locator('#dev-current').filter({hasText:'当前启用'}).waitFor();
      const live=await (await real.request.get('http://127.0.0.1:8011/api/v1/validation/development/history')).json();
      assert(Array.isArray(live.snapshots) && Array.isArray(live.active_versions));
      assert.equal(live.releases.length,0); assert.equal(live.active_versions.length,0);
      const inventory=await (await real.request.get('http://127.0.0.1:8011/api/v1/validation/audit/items')).json();
      assert.equal(inventory.items.length,42); assert(inventory.items.every(i=>i.revision===0));
      assert(await real.locator('#dev-plan').isDisabled()); assert(await real.locator('#dev-prepare').isDisabled());
      await real.locator('#development').screenshot({path:path.join(output,'real-development-desktop.png')});
      await real.setViewportSize({width:390,height:844});
      await real.locator('#development').screenshot({path:path.join(output,'real-development-mobile.png')});
      assert(await real.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
      assert.deepEqual(posts,[]); assert.deepEqual(realErrors,[]);
      fs.writeFileSync(path.join(output,'real-read-only.json'),JSON.stringify({passed:true,item_count:42,revision_zero:true,releases:0,post_requests:0,errors:realErrors},null,2));
      check('real_page_read_only_42_pending_no_posts');
    } finally { await realContext.close(); }
}
