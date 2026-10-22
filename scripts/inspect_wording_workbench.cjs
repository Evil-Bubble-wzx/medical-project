// Read-only inspection of the real local workbench. Abort every non-GET API request.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = require(path.join(process.env.AUDIT_PLAYWRIGHT_MODULES, 'playwright'));
const output = path.resolve('evaluations/reports/wording-review-ui-4.1/workbench');
fs.mkdirSync(output,{recursive:true});
(async()=>{
  const browser=await chromium.launch({headless:true,executablePath:process.env.AUDIT_BROWSER_EXECUTABLE});
  const context=await browser.newContext({viewport:{width:1440,height:1000}});
  const writes=[];const errors=[];
  await context.route('**/api/**',route=>{
    if(route.request().method()!=='GET'){writes.push(route.request().method());return route.abort();}
    return route.continue();
  });
  const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
  try {
    await page.goto('http://127.0.0.1:8011/audit');await page.waitForLoadState('networkidle');
    await page.getByRole('button',{name:'回答表述 · 4.0',exact:true}).click();
    await page.locator('#field-proposed_text').waitFor();
    assert.equal(await page.locator('#item-list button').count(),11);
    assert.equal(await page.locator('#item-topic').textContent(),'回答表述 / 4.0');
    assert.equal(await page.locator('#field-reviewer').inputValue(),'');
    await page.screenshot({path:path.join(output,'desktop.png'),fullPage:true});
    await page.setViewportSize({width:390,height:844});
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    await page.screenshot({path:path.join(output,'mobile.png'),fullPage:true});
    assert.deepEqual(writes,[]);assert.deepEqual(errors,[]);
    fs.writeFileSync(path.join(output,'readonly-check.json'),JSON.stringify({items:11,api_writes:writes,page_errors:errors,mobile_no_horizontal_overflow:true,clinical_approval:false},null,2));
    console.log('Actual workbench: 11 items, no API writes, no page errors, mobile width verified.');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
