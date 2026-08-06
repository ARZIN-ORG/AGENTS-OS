const state = {
  locale: localStorage.getItem("agentos.locale") || "fa-IR",
  theme: localStorage.getItem("agentos.theme") || "dark",
  role: localStorage.getItem("agentos.role") || "governance"
};

function applyLocale(){
  const html = document.documentElement;
  const isFa = state.locale === "fa-IR";
  html.lang = isFa ? "fa" : "en";
  html.dir = isFa ? "rtl" : "ltr";
  document.querySelectorAll("[data-i18n]").forEach(el => {
    el.textContent = I18N.t(el.getAttribute("data-i18n"));
  });
}

function applyTheme(){
  document.documentElement.setAttribute("data-theme", state.theme === "light" ? "light" : "dark");
}

function populateControls(){
  const langSel = document.getElementById("langSel");
  const themeSel = document.getElementById("themeSel");
  const roleSel = document.getElementById("roleSel");

  langSel.value = state.locale;
  themeSel.value = state.theme;
  roleSel.value = state.role;

  roleSel.innerHTML = Roles.ALL.map(r => `<option value="${r}">${I18N.t(Roles.labels[r])}</option>`).join("");

  langSel.onchange = () => { state.locale = langSel.value; localStorage.setItem("agentos.locale", state.locale); applyLocale(); };
  themeSel.onchange = () => { state.theme = themeSel.value; localStorage.setItem("agentos.theme", state.theme); applyTheme(); };
  roleSel.onchange = () => { state.role = roleSel.value; localStorage.setItem("agentos.role", state.role); Router.init(); };
}

function buildViewsIndex(){
  const list = document.getElementById("viewsIndex");
  const groups = {};
  VIEW_REGISTRY.forEach(v => {
    groups[v.layer] = groups[v.layer] || [];
    groups[v.layer].push(v);
  });

  const order = ["os","infra","domain","interaction"];
  const html = order.map(layer => {
    const items = (groups[layer]||[]).map(v => {
      const path = `/${v.layer}/${v.slug}`;
      return `<tr>
        <td><code>${path}</code></td>
        <td>${v.title}</td>
        <td class="small">${v.roles.join(", ")}</td>
        <td><button onclick="Router.go('${path}')">Open</button></td>
      </tr>`;
    }).join("");
    return `<div class="card">
      <h2>${layer.toUpperCase()} Views</h2>
      <table><thead><tr><th>Path</th><th>Title</th><th>Roles</th><th></th></tr></thead><tbody>${items}</tbody></table>
    </div>`;
  }).join("");

  list.innerHTML = html;
}

window.addEventListener("DOMContentLoaded", () => {
  applyTheme();
  applyLocale();
  populateControls();
  buildViewsIndex();
  Router.init();
});
