import { getSession, requireRoleForView } from './core-auth.js';
import { setLocale, t } from './core-i18n.js';
import { setBrand } from './core-theme.js';
import { ViewRegistry } from './view-registry.js';
const $=(s)=>document.querySelector(s);
function setActive(path){document.querySelectorAll('.nav a').forEach(a=>a.classList.toggle('active',a.getAttribute('href')===`#${path}`));}
async function loadView(path){
  const route=ViewRegistry.resolve(path);
  if(!route){$('#view').innerHTML=`<div class="card"><div class="h1">404</div><p class="p">View not found</p></div>`;return;}
  const s=getSession();
  if(!requireRoleForView(s.roles,route.roles)){
    $('#view').innerHTML=`<div class="card"><div class="h1">${t('ui.denied')}</div><p class="p">${route.id}</p></div>`;return;
  }
  const res=await fetch(route.template,{cache:'no-store'}); $('#view').innerHTML=await res.text();
  if(route.controller){ const mod=await import(route.controller); if(mod&&typeof mod.init==='function'){ await mod.init({route,session:s}); } }
  setActive(path);
}
function current(){return (location.hash||'#/os/os-dashboard').slice(1);}
export async function boot(){
  const cfg=await (await fetch('./core/app.config.json',{cache:'no-store'})).json();
  const brand=localStorage.getItem('agentos.brand')||cfg.defaults.brand;
  const locale=localStorage.getItem('agentos.locale')||cfg.defaults.locale;
  setBrand(brand); await setLocale(locale);
  $('#brandSel').value=brand; $('#localeSel').value=locale;
  $('#navOs').textContent=t('nav.os'); $('#navInfra').textContent=t('nav.infra'); $('#navDomain').textContent=t('nav.domain'); $('#navInteraction').textContent=t('nav.interaction');
  document.querySelectorAll('[data-titlekey]').forEach(el=>{el.textContent=t(el.getAttribute('data-titlekey'))});
  $('#brandSel').addEventListener('change',e=>{localStorage.setItem('agentos.brand',e.target.value); setBrand(e.target.value);});
  $('#localeSel').addEventListener('change',async e=>{localStorage.setItem('agentos.locale',e.target.value); await setLocale(e.target.value);
    document.querySelectorAll('[data-titlekey]').forEach(el=>{el.textContent=t(el.getAttribute('data-titlekey'))});
    await loadView(current());
  });
  window.addEventListener('hashchange',async ()=>loadView(current()));
  await loadView(current());
}
