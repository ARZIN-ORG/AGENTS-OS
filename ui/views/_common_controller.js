import { API } from '../core/core-api.js';
function rid(){return (crypto.randomUUID&&crypto.randomUUID())||(`${Date.now()}-${Math.random().toString(16).slice(2)}`);}
async function openManifest(route){
  const key=route.id.replaceAll('/','__');
  const url=`./manifests/views/${key}.json`;
  const res=await fetch(url,{cache:'no-store'}); const txt=await res.text();
  const w=window.open('','_blank'); w.document.write(`<pre>${txt.replaceAll('<','&lt;')}</pre>`); w.document.close();
}
export async function init({route,session}){
  const traceId=rid(); document.getElementById('traceId').textContent=traceId;
  const btn=document.getElementById('primaryBtn'); const refresh=document.getElementById('refreshBtn'); const rows=document.getElementById('rows');
  document.getElementById('copyTraceBtn').addEventListener('click',async ()=>{await navigator.clipboard.writeText(traceId);});
  document.getElementById('openManifestBtn').addEventListener('click',()=>openManifest(route));
  function esc(s){return (s||'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');}
  async function render(obj){
    rows.innerHTML='';
    const entries=Object.entries(obj||{}).slice(0,18);
    if(!entries.length){rows.innerHTML='<tr><td>Result</td><td>null</td></tr>'; return;}
    for(const [k,v] of entries){rows.insertAdjacentHTML('beforeend',`<tr><td>${k}</td><td><code>${esc(JSON.stringify(v))}</code></td></tr>`);}
  }
  async function call(){
    const id=route.id;
    try{
      let data=null;
      if(id.startsWith('os/os-agent-registry')) data=await API.registry('/v1/agents');
      else if(id.startsWith('os/os-policy-browser')||id.startsWith('os/os-version-control')||id.startsWith('os/os-compliance-drift')) data=await API.policy('/v1/policies');
      else if(id.startsWith('os/os-permit-review')||id.startsWith('os/os-audit-trace')||id.startsWith('infra/infra-incident-analysis')||id.startsWith('interaction/interaction-audit-report')) data=await API.permit('/v1/permits');
      else if(id.startsWith('interaction/interaction-intent-input')||id.startsWith('interaction/interaction-intent-review')) data=await API.intent('/v1/intents');
      else data=await API.governance('/v1/status');
      await render({ok:true,view:id,data});
    }catch(e){
      await render({ok:false,view:id,error:{status:e.status||0,message:e.message,data:e.data||null}});
    }
  }
  btn.addEventListener('click',call); refresh.addEventListener('click',call);
  await call();
}
