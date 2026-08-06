const Router = (() => {
  function normalize(path){
    if(!path) return "/";
    path = path.replace(/\/+$/,"");
    return path === "" ? "/" : path;
  }

  function getViewByPath(path){
    path = normalize(path);
    if(path === "/") return { kind:"home" };
    const parts = path.split("/").filter(Boolean);
    if(parts.length < 2) return null;
    const layer = parts[0];
    const slug = parts.slice(1).join("/");
    const v = VIEW_REGISTRY.find(x => x.layer === layer && x.slug === slug);
    return v || null;
  }

  function allowed(view, role){
    if(!view || view.kind === "home") return true;
    return view.roles.includes(role);
  }

  async function loadView(view){
    if(view.kind === "home"){
      return await fetch("./views/home.html").then(r => r.text());
    }
    const file = `./views/${view.layer}/${view.slug.replaceAll("/","__")}.html`;
    const res = await fetch(file);
    if(!res.ok) throw new Error("NOT_FOUND");
    return await res.text();
  }

  async function render(path){
    const view = getViewByPath(path);
    const root = document.getElementById("viewRoot");
    if(!view){
      root.innerHTML = `<div class="card"><h2>${I18N.t("err.notfound")}</h2></div>`;
      return;
    }
    if(!allowed(view, state.role)){
      root.innerHTML = `<div class="card"><h2>${I18N.t("err.forbidden")}</h2><p class="small">role=<code>${state.role}</code></p></div>`;
      return;
    }
    try{
      const html = await loadView(view);
      root.innerHTML = html;
      if(view.kind !== "home"){
        document.getElementById("currentView").textContent = `${view.layer.toUpperCase()} / ${view.title}`;
      }else{
        document.getElementById("currentView").textContent = "";
      }
    }catch(e){
      root.innerHTML = `<div class="card"><h2>${I18N.t("err.notfound")}</h2></div>`;
    }
  }

  function go(path){
    history.pushState({}, "", "#"+normalize(path));
    render(normalize(path));
  }

  function current(){
    const hash = (location.hash || "#/").slice(1);
    return normalize(hash);
  }

  function init(){
    window.addEventListener("popstate", () => render(current()));
    window.addEventListener("hashchange", () => render(current()));
    render(current());
  }

  return { init, go, current, getViewByPath };
})();
