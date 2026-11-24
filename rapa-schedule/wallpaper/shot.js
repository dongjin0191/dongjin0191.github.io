const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const ev=fs.readFileSync('/home/user/dongjin0191.github.io/rapa-schedule/events.json','utf8');
let h=fs.readFileSync('wp.html','utf8').replace('__EV__',ev).replace('__MONTHS__','[[2026,11],[2026,12]]');fs.writeFileSync('wp_built.html',h);
const b=await chromium.launch();const p=await b.newPage({viewport:{width:2560,height:4000}});
await p.goto('file://'+process.cwd()+'/wp_built.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
const ov=await p.evaluate(()=>[...document.querySelectorAll('#pc .ag,#ph')].map(e=>[e.scrollHeight,e.clientHeight]));console.log(ov);
await p.locator('#pc').screenshot({path:'pc.png'});await p.locator('#ph').screenshot({path:'ph.png'});await b.close()})();
