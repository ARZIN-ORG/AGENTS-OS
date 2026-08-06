const I18N = (() => {
  const dict = {
    "fa-IR": {
      "app.title":"Agent OS — Governance Console",
      "nav.home":"خانه",
      "nav.views":"ویوها",
      "nav.session":"نشست",
      "ctl.language":"زبان",
      "ctl.theme":"پوسته",
      "ctl.role":"نقش",
      "theme.dark":"تیره",
      "theme.light":"روشن",
      "role.governance":"Governance",
      "role.security":"Security",
      "role.auditor":"Auditor",
      "role.cto":"CTO",
      "role.ops":"Ops",
      "role.business":"Business Owner",
      "role.exec":"Executive",
      "err.forbidden":"دسترسی غیرمجاز است. نقش شما اجازه این ویو را ندارد.",
      "err.notfound":"ویو یافت نشد."
    },
    "en-US": {
      "app.title":"Agent OS — Governance Console",
      "nav.home":"Home",
      "nav.views":"Views",
      "nav.session":"Session",
      "ctl.language":"Language",
      "ctl.theme":"Theme",
      "ctl.role":"Role",
      "theme.dark":"Dark",
      "theme.light":"Light",
      "role.governance":"Governance",
      "role.security":"Security",
      "role.auditor":"Auditor",
      "role.cto":"CTO",
      "role.ops":"Ops",
      "role.business":"Business Owner",
      "role.exec":"Executive",
      "err.forbidden":"Forbidden. Your role is not allowed for this view.",
      "err.notfound":"View not found."
    }
  };

  function t(key, locale){
    const l = locale || state.locale;
    return (dict[l] && dict[l][key]) || key;
  }

  return { t, dict };
})();
