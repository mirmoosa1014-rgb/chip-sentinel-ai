/** Deterministic UI-only verification. Never trains a model or rewrites experiment data. */
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdir, writeFile, readFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const output=path.resolve(root,process.env.CHIP_BROWSER_OUTPUT||'artifacts/browser');
await mkdir(output,{recursive:true});
await readFile(path.join(root,'frontend/dist/index.html')); // Fail early if the production app was not built.
const checks=[], pageErrors=[];
let server, browser, page;
const report={playwright:'1.56.1',viewports:{desktop:{width:1440,height:1100},mobile:{width:390,height:844}},checks,passed:false};
function record(name){checks.push(name);console.log(`PASS ${name}`);}

async function startServer(){
  const source=[
    'from http.server import ThreadingHTTPServer',
    'from chipsentinel.server import Handler',
    "server=ThreadingHTTPServer(('127.0.0.1',0),Handler)",
    'print(server.server_port,flush=True)',
    'server.serve_forever()',
  ].join('\n');
  server=spawn(process.env.PYTHON_BIN||'python3',['-u','-c',source],{cwd:root,stdio:['ignore','pipe','pipe']});
  let log='';server.stderr.on('data',chunk=>{log=(log+chunk.toString()).slice(-4000)});
  return await new Promise((resolve,reject)=>{
    let stdout='';const timer=setTimeout(()=>reject(Error(`HTTP server startup timed out. ${log}`)),15000);
    server.once('error',error=>{clearTimeout(timer);reject(error)});
    server.once('exit',code=>{clearTimeout(timer);reject(Error(`HTTP server exited ${code}. ${log}`))});
    server.stdout.on('data',chunk=>{stdout+=chunk.toString();const line=stdout.split('\n')[0];
      if(/^\d+$/.test(line)&&stdout.includes('\n')){clearTimeout(timer);resolve(`http://127.0.0.1:${line}`)}
    });
  });
}
async function settled(){
  await page.waitForFunction(()=>document.querySelector('.run-state')?.textContent?.includes('Observation set ready')&&!!document.querySelector('.evidence-table'));
  await page.waitForFunction(()=>document.getAnimations().every(a=>a.playState!=='running'));
  await page.evaluate(()=>document.fonts.ready);
}
async function noOverflow(){
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'The page must not overflow horizontally');
}
async function snapshot(name){await page.screenshot({path:path.join(output,name),fullPage:true,animations:'disabled'});}

try{
  const url=await startServer();
  browser=await chromium.launch({headless:true,...(process.env.CHIP_BROWSER_EXECUTABLE?{executablePath:process.env.CHIP_BROWSER_EXECUTABLE}:{})});
  page=await browser.newPage({viewport:report.viewports.desktop,locale:'en-US',timezoneId:'UTC',colorScheme:'light',reducedMotion:'no-preference'});
  page.setDefaultTimeout(15000);page.on('pageerror',error=>pageErrors.push(error.message));
  await page.goto(url,{waitUntil:'networkidle'});await settled();
  assert.equal(await page.title(),'ChipSentinel · Digital Diagnosis Lab');
  assert.equal(await page.getByRole('heading',{name:'ChipSentinel',exact:true}).count(),1);
  const style=await page.evaluate(()=>({paper:getComputedStyle(document.documentElement).getPropertyValue('--bg').trim(),radius:getComputedStyle(document.querySelector('.run-test')).borderRadius}));
  assert.equal(style.paper,'#F3F0E8');assert.equal(style.radius,'0px');
  await noOverflow();await snapshot('desktop.png');record('desktop 1440px, live API rendering, Swiss tokens and square controls');

  await page.setViewportSize(report.viewports.mobile);await noOverflow();await snapshot('mobile.png');
  assert.equal(await page.locator('.diagram-viewport').evaluate(el=>el.scrollWidth>el.clientWidth),true,'The wide schematic should scroll locally on mobile');
  record('mobile 390px without page overflow; circuit remains in its own horizontal viewport');

  await page.emulateMedia({reducedMotion:'reduce'});await page.reload({waitUntil:'networkidle'});await settled();
  assert.equal(await page.evaluate(()=>document.getAnimations().filter(a=>a.playState==='running').length),0);
  await noOverflow();await snapshot('mobile-reduced-motion.png');
  await page.setViewportSize(report.viewports.desktop);await snapshot('desktop-reduced-motion.png');
  record('reduced-motion desktop/mobile: no running animations');

  await page.getByRole('button',{name:/^Run next test/}).click();await settled();
  assert.equal(await page.locator('.evidence-table tbody tr').count(),4);
  const actual=await page.evaluate(async()=>{
    const response=await fetch('/api/diagnose',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({family:6,seed:31,budget:4,policy:'active'})});
    if(!response.ok)throw Error('API comparison failed');return await response.json();
  });
  assert.equal(await page.locator('.readouts > div').first().locator('dd').textContent(),String(actual.remaining));
  const expectedRows=actual.observations.map((observation,i)=>[String(i+1).padStart(2,'0'),observation.vector.join(' / '),observation.expected.toString(2).padStart(4,'0'),observation.observed.toString(2).padStart(4,'0'),observation.expected===observation.observed?'PASS':'DIFF']);
  const displayedRows=await page.locator('.evidence-table tbody tr').evaluateAll(rows=>rows.map(row=>Array.from(row.querySelectorAll('td'),cell=>cell.textContent)));
  assert.deepEqual(displayedRows,expectedRows);record('next test updates exact live-engine evidence and candidate readout');

  await page.getByRole('checkbox',{name:'Reveal injected fault'}).check();
  await page.getByText(`Injected fault: ${actual.hidden}`,{exact:true}).waitFor();record('hidden fault reveal');
  const canvas=page.locator('canvas');const before=await canvas.evaluate(el=>el.toDataURL());const box=await canvas.boundingBox();assert.ok(box);
  await page.mouse.move(box.x+box.width*.5,box.y+box.height*.5);await page.mouse.down();await page.mouse.move(box.x+box.width*.5+90,box.y+box.height*.5,{steps:5});await page.mouse.up();
  assert.notEqual(await canvas.evaluate(el=>el.toDataURL()),before);record('pointer drag redraws actual 3D projection');

  const downloadPending=page.waitForEvent('download');await page.getByRole('button',{name:'Export evidence .json'}).click();const download=await downloadPending;
  assert.equal(download.suggestedFilename(),'chip-sentinel-transcript.json');
  await download.saveAs(path.join(output,'transcript.json'));
  const transcript=JSON.parse(await readFile(path.join(output,'transcript.json'),'utf8'));assert.equal(transcript.seed,31);assert.equal(transcript.observations.length,4);record('JSON evidence download contains current episode');

  await page.getByLabel('Netlist family').selectOption('7');await settled();
  await page.waitForFunction(()=>document.querySelector('.schematic .section-title p')?.textContent?.includes('alu-7'));
  await page.getByLabel('Episode seed').fill('17');await page.getByLabel('Episode seed').blur();await settled();
  const slider=page.getByRole('slider',{name:'Evidence budget'});await slider.focus();await slider.press('Home');for(let i=0;i<5;i++)await slider.press('ArrowRight');await settled();
  await page.waitForFunction(()=>document.querySelectorAll('.evidence-table tbody tr').length===5);
  assert.equal(await page.getByLabel('Episode seed').inputValue(),'17');assert.equal(await slider.inputValue(),'5');record('family, seed and keyboard budget controls');
  assert.deepEqual(pageErrors,[]);record('no uncaught browser JavaScript errors');report.passed=true;
}catch(error){
  report.error=String(error);process.exitCode=1;console.error(error);
  if(page&&!page.isClosed())await snapshot('failure.png').catch(()=>{});
}finally{
  await writeFile(path.join(output,'report.json'),JSON.stringify({...report,pageErrors},null,2)+'\n');
  if(browser)await browser.close();
  if(server&&server.exitCode===null){await new Promise(resolve=>{server.once('exit',resolve);server.kill('SIGTERM')})}
}
