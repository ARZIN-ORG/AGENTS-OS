const Roles = (() => {
  const ALL = ["governance","security","auditor","cto","ops","business","exec"];
  const labels = {
    governance:"role.governance",
    security:"role.security",
    auditor:"role.auditor",
    cto:"role.cto",
    ops:"role.ops",
    business:"role.business",
    exec:"role.exec"
  };
  return { ALL, labels };
})();
