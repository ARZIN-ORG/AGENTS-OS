export function getSession(){
  const jwt = localStorage.getItem('agentos.jwt') || '';
  let roles=[]; try{roles=JSON.parse(localStorage.getItem('agentos.roles')||'[]')}catch{roles=[]}
  if(!roles.length){roles=['viewer']}
  return {jwt,roles};
}
export function requireRoleForView(userRoles,allowedRoles){
  if(!allowedRoles||!allowedRoles.length) return false;
  return allowedRoles.some(r=>userRoles.includes(r));
}
export function authHeader(){
  const {jwt}=getSession();
  return jwt?{'Authorization':`Bearer ${jwt}`}:{};
}
