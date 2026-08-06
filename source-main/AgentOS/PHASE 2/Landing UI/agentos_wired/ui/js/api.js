import { getConfig } from './config.js';

function withTimeout(promise, ms){
  let t;
  const timeout = new Promise((_, reject)=>{
    t = setTimeout(()=>reject(new Error('request_timeout')), ms);
  });
  return Promise.race([promise, timeout]).finally(()=>clearTimeout(t));
}

function getBearer(){
  // Expect an access token injected by reverse proxy / SSO flow.
  // This UI does not implement auth flows; it just consumes tokens.
  const tok = (typeof window !== 'undefined') ? (window.__AGENTOS_TOKEN__ || localStorage.getItem('agentos_token') || '') : '';
  return tok ? `Bearer ${tok}` : '';
}

async function httpJson(path, opts={}){
  const cfg = getConfig();
  if(!cfg.apiBaseUrl){
    throw new Error('api_base_url_missing');
  }
  const url = cfg.apiBaseUrl + path;
  const headers = {
    'Accept': 'application/json',
    ...(opts.body ? {'Content-Type':'application/json'} : {}),
    ...(opts.headers || {}),
  };
  const auth = getBearer();
  if(auth) headers['Authorization'] = auth;

  const req = fetch(url, {
    method: opts.method || 'GET',
    headers,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
    credentials: 'include',
  }).then(async r=>{
    const text = await r.text();
    let data;
    try{ data = text ? JSON.parse(text) : null; }catch{ data = {raw:text}; }
    if(!r.ok){
      const err = new Error('http_error');
      err.status = r.status;
      err.data = data;
      throw err;
    }
    return data;
  });

  return withTimeout(req, cfg.requestTimeoutMs);
}

export const api = {
  health: ()=>httpJson('/health'),
  whoami: ()=>httpJson('/whoami'),

  overview: ()=>httpJson('/v1/overview'),
  agents: ()=>httpJson('/v1/agents'),
  policies: ()=>httpJson('/v1/policies'),
  channels: ()=>httpJson('/v1/channels'),
  permits: ()=>httpJson('/v1/permits'),
  audit: ()=>httpJson('/v1/audit'),

  translateIntent: (payload)=>httpJson('/v1/intent/translate',{method:'POST', body: payload}),
  createPermit: (payload)=>httpJson('/v1/permits',{method:'POST', body: payload}),
  approvePermit: (permitId, payload)=>httpJson(`/v1/permits/${encodeURIComponent(permitId)}/approve`,{method:'POST', body: payload}),
};
