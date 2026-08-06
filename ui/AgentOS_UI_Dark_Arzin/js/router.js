export function setActiveNav(hash){
  document.querySelectorAll('[data-nav]').forEach(a=>{
    const target=a.getAttribute('href');
    a.classList.toggle('active', target===hash);
  });
}
export function onRoute(cb){
  window.addEventListener('hashchange', ()=>cb(location.hash||'#/overview'));
  cb(location.hash||'#/overview');
}
