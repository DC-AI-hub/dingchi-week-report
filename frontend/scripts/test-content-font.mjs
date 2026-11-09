import {build} from 'esbuild'
import {parse,compileScript} from '@vue/compiler-sfc'
import {readFileSync,mkdtempSync,writeFileSync,existsSync,rmSync} from 'node:fs'
import {tmpdir} from 'node:os'
import {resolve,dirname,join} from 'node:path'
import {execFileSync} from 'node:child_process'

const edge='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
if(!existsSync(edge))throw Error('此浏览器回归需要本机 Microsoft Edge。')
const temp=mkdtempSync(join(tmpdir(),'dingchi-content-font-'))
const source=`import {createApp,h,reactive,nextTick} from 'vue';import {createPinia,setActivePinia} from 'pinia';
import Control from './src/features/preferences/components/ContentFontControl.vue';
import {useContentTypography} from './src/features/preferences/useContentTypography';
globalThis.mockAuth=reactive({user:{id:'font-test-a'}});
for(const id of ['font-test-a','font-test-b'])localStorage.removeItem('dingchi.user-content-font-size:'+id);
const pinia=createPinia();setActivePinia(pinia);const settings=useContentTypography();
createApp({render:()=>h(Control)}).use(pinia).mount('#control');
const tick=()=>nextTick();const check=(test,message)=>{if(!test)throw Error(message)};
const font=selector=>getComputedStyle(document.querySelector(selector)).fontSize;
(async()=>{try{
 await tick();check(font('#goal')==='14px','默认字号应为14px');
 const heading=font('h2'),header=font('th'),action=font('#action'),status=font('#status');
 document.querySelector('[aria-label="增大内容字号"]').click();await tick();
 check(settings.size===15 && font('#goal')==='15px','增大字号立即生效');
 const slider=document.querySelector('input[type=range]');slider.value='22';slider.dispatchEvent(new Event('input',{bubbles:true}));await tick();
 for(const selector of ['#goal','#task','#entry']){check(font(selector)==='22px','内容字号没有统一:'+selector);check(getComputedStyle(document.querySelector(selector)).fontWeight==='400','内容不应加粗');}
 check(font('h2')===heading && font('th')===header && font('#action')===action && font('#status')===status,'影响了标题表头按钮或状态');
 check(localStorage.getItem('dingchi.user-content-font-size:font-test-a')==='22','没有记忆用户字号');
 globalThis.mockAuth.user={id:'font-test-b'};await tick();check(settings.size===14,'切换用户应使用独立设置');settings.setSize(18);
 globalThis.mockAuth.user={id:'font-test-a'};await tick();check(settings.size===22,'未恢复原用户字号');
 setActivePinia(createPinia());const reloaded=useContentTypography();check(reloaded.size===22,'刷新后未恢复存储字号');
 reloaded.setSize(100);check(reloaded.size===24,'上限错误');reloaded.setSize(0);check(reloaded.size===10,'下限错误');reloaded.reset();check(reloaded.size===14 && font('#task')==='14px','恢复默认失败');
 document.body.dataset.result='PASS';document.querySelector('#result').textContent='PASS: 内容字号、范围隔离、按用户记忆、重新加载和恢复默认';
}catch(error){document.body.dataset.result='FAIL';document.querySelector('#result').textContent=error.message;}})();`
const built=await build({stdin:{contents:source,resolveDir:process.cwd(),loader:'ts'},bundle:true,write:false,format:'iife',alias:{'@':resolve('src')},define:{__VUE_OPTIONS_API__:'true',__VUE_PROD_DEVTOOLS__:'false',__VUE_PROD_HYDRATION_MISMATCH_DETAILS__:'false','process.env.NODE_ENV':'"production"'},plugins:[{name:'vue-test',setup(b){
 b.onResolve({filter:/features\/auth\/store$/},()=>({path:'mock-auth',namespace:'mock'}));b.onLoad({filter:/.*/,namespace:'mock'},()=>({contents:'export function useAuthStore(){return globalThis.mockAuth}'}));
 b.onLoad({filter:/\.vue$/},args=>({contents:compileScript(parse(readFileSync(args.path,'utf8')).descriptor,{id:'font-test',inlineTemplate:true}).content,loader:'ts',resolveDir:dirname(args.path)}))
}}]})
const css=readFileSync('src/styles/user-content.css','utf8')+readFileSync('src/features/preferences/components/ContentFontControl.css','utf8')
const file=join(temp,'test.html')
writeFileSync(file,`<html><head><style>:root{--text:#132a55;--muted:#6e82a6;--line:#cad8eb;--accent:#2f80ed;--surface-soft:#f5f9ff}h2{font-size:22px}th{font-size:16px}#action,#status{font-size:13px}td{font-size:20px;font-weight:700}${css}</style></head><body><div id="control"></div><h2>月度计划</h2><p id="goal" class="user-content">月度目标正文</p><table><thead><tr><th>工作内容</th></tr></thead><tbody><tr><td><span id="task" class="user-content">周工作任务正文</span></td></tr></tbody></table><textarea id="entry" class="user-content">用户输入</textarea><button id="action">提交审批</button><span id="status">进行中</span><pre id="result">pending</pre><script>${built.outputFiles[0].text}</script></body></html>`)
try{
 const dom=execFileSync(edge,['--headless','--disable-gpu','--no-first-run','--no-default-browser-check',`--user-data-dir=${join(temp,'profile')}`,'--virtual-time-budget=4000','--dump-dom',new URL('file:///'+file.replaceAll('\\','/')).href],{encoding:'utf8',windowsHide:true,timeout:30000,maxBuffer:8*1024*1024,stdio:['ignore','pipe','ignore']})
 if(!dom.includes('data-result="PASS"'))throw Error(dom.match(/<pre id="result">(.*?)<\/pre>/)?.[1] || '浏览器验证未完成')
 console.log('PASS: 用户内容字号、非内容区域隔离、账号独立记忆、重载恢复、上下限及恢复默认')
}finally{if(dirname(temp)===tmpdir())try{rmSync(temp,{recursive:true,force:true})}catch{/* 浏览器释放配置文件后由系统临时文件清理。 */}}
