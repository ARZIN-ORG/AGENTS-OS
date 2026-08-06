// Runtime config injected by server or static host.
// Keep this file tiny and boring: CTOs like boring.

export function getConfig(){
  const c = (typeof window !== 'undefined' && window.__AGENTOS_CONFIG__) ? window.__AGENTOS_CONFIG__ : {};
  const apiBaseUrl = (c.apiBaseUrl || '').toString().replace(/\/$/, '');

  return {
    // 'mock' keeps UI usable without backend; 'real' requires governance-console-api.
    mode: (c.mode || 'mock').toString(),
    apiBaseUrl,
    requestTimeoutMs: Number(c.requestTimeoutMs || 8000),
    auth: {
      enabled: c.auth && typeof c.auth.enabled === 'boolean' ? c.auth.enabled : true,
    },
  };
}

export function isRealMode(){
  const cfg = getConfig();
  return cfg.mode.toLowerCase() === 'real';
}
