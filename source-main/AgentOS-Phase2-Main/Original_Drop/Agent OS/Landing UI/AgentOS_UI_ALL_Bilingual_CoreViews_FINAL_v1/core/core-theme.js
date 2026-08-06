export function setBrand(brand){
  document.body.dataset.brand=brand;
  const link=document.getElementById('themeLink');
  link.href=brand==='pedramflow'?'./core/theme-pedramflow.css':'./core/theme-arzin.css';
  document.getElementById('brandTitle').textContent=brand==='pedramflow'?'PedramFlow':'Arzin';
}
