let dict={};let locale='fa-IR';
export function t(key){return dict[key]||key;}
export async function setLocale(loc){
  locale=loc; dict=await (await fetch(`./i18n/${loc}.json`,{cache:'no-store'})).json();
  const dir=(loc==='fa-IR')?'rtl':'ltr';
  document.documentElement.setAttribute('dir',dir);
  document.documentElement.setAttribute('lang',loc.startsWith('fa')?'fa':'en');
}
export function getLocale(){return locale;}
