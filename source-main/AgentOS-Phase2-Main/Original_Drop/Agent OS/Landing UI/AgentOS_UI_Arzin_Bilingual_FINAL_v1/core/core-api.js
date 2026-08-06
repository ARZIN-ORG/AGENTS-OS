import { authHeader } from './core-auth.js';
async function cfg(){return await (await fetch('./core/app.config.json',{cache:'no-store'})).json();}
async function request(method,url,body){
  const headers={'Content-Type':'application/json',...authHeader()};
  const opt={method,headers,cache:'no-store'};
  if(body!==undefined) opt.body=JSON.stringify(body);
  const res=await fetch(url,opt); const txt=await res.text();
  let data=null; try{data=txt?JSON.parse(txt):null}catch{data={raw:txt}}
  if(!res.ok){const err=new Error(`HTTP ${res.status}`); err.status=res.status; err.data=data; throw err;}
  return data;
}
export const API={
  async registry(p,m='GET',b){const c=await cfg(); return request(m,`${c.api.registry.baseUrl}${p}`,b);},
  async policy(p,m='GET',b){const c=await cfg(); return request(m,`${c.api.policy.baseUrl}${p}`,b);},
  async permit(p,m='GET',b){const c=await cfg(); return request(m,`${c.api.permit.baseUrl}${p}`,b);},
  async intent(p,m='GET',b){const c=await cfg(); return request(m,`${c.api.intent.baseUrl}${p}`,b);},
  async governance(p,m='GET',b){const c=await cfg(); return request(m,`${c.api.governance.baseUrl}${p}`,b);},
};
