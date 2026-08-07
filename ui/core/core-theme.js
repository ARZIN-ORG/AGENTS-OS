export function setBrand(brand){
  document.body.dataset.brand = brand;
  const link = document.getElementById('themeLink');
  if (!link) return;
  link.href = brand === 'pedramflow' ? './core/theme-pedramflow.css' : './core/theme-arzin.css';
  const title = document.getElementById('brandTitle');
  if (title) title.textContent = brand === 'pedramflow' ? 'PedramFlow' : 'Arzin';
  console.log('✅ Brand changed to:', brand, 'Theme:', link.href);
}
