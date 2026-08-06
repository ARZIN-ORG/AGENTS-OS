import {onRoute,setActiveNav} from './router.js';
import {MOCK} from './mock-data.js';
import {t, initI18n} from './i18n.js';
import {isRealMode} from './config.js';
import {api} from './api.js';

const $ = (sel,root=document)=>root.querySelector(sel);
initI18n();

const STATE = {
  mode: isRealMode() ? 'real' : 'mock',
  lastError: null,
  overview: null,
  agents: null,
  policies: null,
  channels: null,
  permits: null,
  audit: null,
};

async function loadDataFor(hash){
  if(STATE.mode !== 'real') return;
  try{
    if(hash.startsWith('#/overview')){
      STATE.overview = await api.overview();
    } else if(hash.startsWith('#/agents')){
      STATE.agents = await api.agents();
    } else if(hash.startsWith('#/policies')){
      STATE.policies = await api.policies();
    } else if(hash.startsWith('#/channels')){
      STATE.channels = await api.channels();
    } else if(hash.startsWith('#/permits')){
      STATE.permits = await api.permits();
    } else if(hash.startsWith('#/audit')){
      STATE.audit = await api.audit();
    }
    STATE.lastError = null;
  }catch(e){
    STATE.lastError = e;
  }
}

function getSystemPills(){
  if(STATE.mode !== 'real' || !STATE.overview){
    return { phase: MOCK.system.phase, build: MOCK.system.build };
  }
  return {
    phase: (STATE.overview.system && STATE.overview.system.phase) ? STATE.overview.system.phase : 'phase1',
    build: (STATE.overview.system && (STATE.overview.system.build || STATE.overview.system.version)) ? (STATE.overview.system.build || STATE.overview.system.version) : 'unknown'
  };
}

const STATE = {
  mode: isRealMode() ? 'real' : 'mock',
  lastError: null,
  overview: null,
  agents: null,
  policies: null,
  channels: null,
  permits: null,
  audit: null,
};

async function loadDataFor(hash){
  if(STATE.mode !== 'real') return;
  try{
    if(hash.startsWith('#/overview')){
      STATE.overview = await api.overview();
    } else if(hash.startsWith('#/agents')){
      STATE.agents = await api.agents();
    } else if(hash.startsWith('#/policies')){
      STATE.policies = await api.policies();
    } else if(hash.startsWith('#/channels')){
      STATE.channels = await api.channels();
    } else if(hash.startsWith('#/permits')){
      STATE.permits = await api.permits();
    } else if(hash.startsWith('#/audit')){
      STATE.audit = await api.audit();
    }
    STATE.lastError = null;
  }catch(e){
    STATE.lastError = e;
  }
}


const STATE = {
  mode: isRealMode() ? 'real' : 'mock',
  lastError: null,
  overview: null,
  agents: null,
  policies: null,
  channels: null,
  permits: null,
  audit: null,
};

async function refreshOverview(){
  if(STATE.mode!=='real') return;
  try{
    const ov = await api.overview();
    STATE.overview = ov;
    STATE.lastError = null;
  }catch(e){
    STATE.lastError = e;
  }
}

async function loadRouteData(hash){
  if(STATE.mode!=='real') return;
  try{
    if(hash.startsWith('#/agents')) STATE.agents = await api.agents();
    if(hash.startsWith('#/policies')) STATE.policies = await api.policies();
    if(hash.startsWith('#/channels')) STATE.channels = await api.channels();
    if(hash.startsWith('#/permits')) STATE.permits = await api.permits();
    if(hash.startsWith('#/audit')) STATE.audit = await api.audit();
    STATE.lastError = null;
  }catch(e){
    STATE.lastError = e;
  }
}


const esc = (s)=>String(s).replace(/[&<>"']/g, c=>({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c]));

function badge(status){
  const cls = status==='ok' ? 'badge' : (status==='warn' ? 'badge warn' : 'badge danger');
  const label = status==='ok' ? t('status.ok') : (status==='warn' ? t('status.watch') : t('status.fail'));
  return `<span class="${cls}"><span class="dot"></span>${label}</span>`;
}

function renderOverview(){
  const a = MOCK.agents;
  const ok=a.filter(x=>x.status==='ok').length;
  const warn=a.filter(x=>x.status==='warn').length;
  const fail=a.filter(x=>x.status==='fail').length;

  return `
  <div class="h1">
    <div>
      <h1>${t('page.overview')}</h1>
      <p>نمایش وضعیت کنترل‌پلین، قوانین قفل‌شده، و مسیر «پیشنهاد → تأیید انسان → Permit → Publish» بدون هیچ میان‌بُر.</p>
    </div>
    <div class="split">
      <span class="pill">${esc(MOCK.system.phase)}</span>
      <button class="btn" id="openAudit">Quick Audit</button>
      <button class="btn primary" id="newPermit">New Permit</button>
    </div>
  </div>

  <div class="grid">
    <div class="card" style="grid-column: span 4">
      <h3>Agents Health</h3>
      <p><b>${ok}</b> OK · <b>${warn}</b> WATCH · <b>${fail}</b> FAIL</p>
      <p class="small">هدف: شکست سریع، و جلوگیری از اجرای مستقیم. هیچ «Agent تصمیم‌گیر» در فاز ۱/۲ مجاز نیست.</p>
    </div>
    <div class="card" style="grid-column: span 4">
      <h3>Channels</h3>
      <p class="small">کانال‌های موازی AACP برای حذف نقطه شکست واحد و جداسازی بار/ریسک.</p>
      <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">
        ${MOCK.channels.map(c=>`<span class="badge ${c.status==='warn'?'warn':''}"><span class="dot"></span>${esc(c.id)} · ${esc(c.sla)}</span>`).join('')}
      </div>
    </div>
    <div class="card" style="grid-column: span 4">
      <h3>Policies (Locked)</h3>
      <p class="small">قوانین غیرقابل دورزدنِ فاز ۱.</p>
      <div style="margin-top:10px;display:flex;flex-direction:column;gap:8px">
        ${MOCK.policies.map(p=>`<div class="split"><span>${esc(p.id)} · ${esc(p.name)}</span><span class="pill">v${esc(p.version)}</span></div>`).join('')}
      </div>
    </div>

    <div class="card" style="grid-column: span 12">
      <div class="split">
        <h3 style="margin:0">Latest Audit Events</h3>
        <span class="small">Immutable trail · chain-hash ready</span>
      </div>
      <table class="table" aria-label="audit table">
        <thead><tr><th>Timestamp</th><th>Trace</th><th>Event</th><th>Actor</th><th>Channel</th></tr></thead>
        <tbody>
          ${MOCK.audit.map(r=>`
            <tr>
              <td>${esc(r.ts)}</td>
              <td><code>${esc(r.trace)}</code></td>
              <td>${esc(r.event)}</td>
              <td>${esc(r.actor)}</td>
              <td>${esc(r.channel)}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  </div>
  `;
}

function renderAgents(){
  const rows = MOCK.agents.map(a=>`
    <tr>
      <td>${esc(a.layer)}</td>
      <td><b>${esc(a.name)}</b><div class="small">${esc(a.code)} · owner=${esc(a.owner)}</div></td>
      <td>${badge(a.status)}</td>
      <td><button class="btn" data-open="agent" data-name="${esc(a.name)}">Inspect</button></td>
    </tr>
  `).join('');
  return `
    <div class="h1">
      <div>
        <h1>${t('page.agents')}</h1>
        <p>همه ایجنت‌ها «پیشنهاددهنده» هستند، نه «تصمیم‌گیر». کنترل با Policy و Permit قفل شده است.</p>
      </div>
      <div class="split">
        <input class="input" id="agentSearch" placeholder="Search agent..." style="width:240px" />
        <button class="btn primary" id="registerAgent">Register</button>
      </div>
    </div>
    <table class="table">
      <thead><tr><th>Layer</th><th>Agent</th><th>Status</th><th></th></tr></thead>
      <tbody id="agentRows">${rows}</tbody>
    </table>
  `;
}

function renderPolicies(){
  return `
    <div class="h1">
      <div>
        <h1>${t('page.policy')}</h1>
        <p>Policy-as-Code با نسخه‌بندی. تغییر بدون ثبت = تخلف. این صفحه فقط نمایش/پیشنهاد است.</p>
      </div>
      <div class="split">
        <button class="btn" id="simulatePolicy">Simulate</button>
        <button class="btn primary" id="proposePolicy">Propose Change</button>
      </div>
    </div>
    <div class="card">
      <h3>Active Policies</h3>
      <table class="table">
        <thead><tr><th>ID</th><th>Name</th><th>Version</th><th>Status</th></tr></thead>
        <tbody>
          ${MOCK.policies.map(p=>`
            <tr>
              <td><code>${esc(p.id)}</code></td>
              <td>${esc(p.name)}</td>
              <td>${esc(p.version)}</td>
              <td><span class="pill">${esc(p.status)}</span></td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function renderPermits(){
  return `
    <div class="h1">
      <div>
        <h1>${t('page.permit')}</h1>
        <p>هیچ اجرای عملیاتی بدون Permit صادرشده مجاز نیست. مسیر: Intent → Confirm → Permit → Publish.</p>
      </div>
      <div class="split">
        <button class="btn" id="refreshPermits">Refresh</button>
        <button class="btn primary" id="createPermit">Create Permit</button>
      </div>
    </div>
    <table class="table">
      <thead><tr><th>ID</th><th>Subject</th><th>Risk</th><th>Status</th><th>Requested By</th></tr></thead>
      <tbody>
        ${MOCK.permits.map(p=>`
          <tr>
            <td><code>${esc(p.id)}</code></td>
            <td>${esc(p.subject)}</td>
            <td><span class="pill">${esc(p.risk)}</span></td>
            <td>${esc(p.status)}</td>
            <td>${esc(p.requestedBy)}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
}

function renderAudit(){
  return `
    <div class="h1">
      <div>
        <h1>${t('page.audit')}</h1>
        <p>ثبت غیرقابل تغییر و قابل ارائه به ناظر. پیشنهاد: chain-hash برای هر batch و snapshot روزانه.</p>
      </div>
      <div class="split">
        <button class="btn" id="exportAudit">Export</button>
        <button class="btn primary" id="openChain">Verify Chain</button>
      </div>
    </div>
    <div class="card">
      <h3>Recent</h3>
      <table class="table">
        <thead><tr><th>Timestamp</th><th>Trace</th><th>Event</th><th>Actor</th><th>Channel</th></tr></thead>
        <tbody>${MOCK.audit.map(r=>`
          <tr>
            <td>${esc(r.ts)}</td><td><code>${esc(r.trace)}</code></td><td>${esc(r.event)}</td><td>${esc(r.actor)}</td><td>${esc(r.channel)}</td>
          </tr>`).join('')}</tbody>
      </table>
      <p class="small">این UI «گزارش» می‌دهد؛ اجرای مستقیم ممنوع است.</p>
    </div>
  `;
}

function renderChannels(){
  return `
    <div class="h1">
      <div>
        <h1>${t('page.channels')}</h1>
        <p>کانال‌های موازی AACP برای جداسازی ریسک/بار و جلوگیری از bottleneck. هر کانال دارای SLA و policy مستقل است.</p>
      </div>
      <div class="split">
        <button class="btn" id="dryRun">Dry-run</button>
        <button class="btn primary" id="addChannel">Add Channel</button>
      </div>
    </div>
    <div class="grid">
      ${MOCK.channels.map(c=>`
        <div class="card" style="grid-column: span 6">
          <div class="split">
            <h3 style="margin:0">${esc(c.id)}</h3>
            ${badge(c.status)}
          </div>
          <p class="small">mode=${esc(c.mode)} · sla=${esc(c.sla)}</p>
          <div style="margin-top:12px;display:flex;gap:10px;flex-wrap:wrap">
            <button class="btn">Rotate Keys</button>
            <button class="btn">Throttle</button>
            <button class="btn">Isolate</button>
          </div>
          <p class="small">همه اکشن‌ها در نسخه عملیاتی باید از مسیر Permit عبور کنند.</p>
        </div>
      `).join('')}
    </div>
  `;
}

function renderPartners(){
  return `
    <div class="h1">
      <div>
        <h1>${t('page.partners')}</h1>
        <p>Onboarding در فاز ۱ با Shadow/Canary و کنترل سخت‌گیرانه. هیچ ایجنت بیرونی مستقیم Publish نمی‌کند.</p>
      </div>
      <div class="split">
        <button class="btn" id="openSandbox">Sandbox</button>
        <button class="btn primary" id="startOnboarding">Start Onboarding</button>
      </div>
    </div>
    <div class="card">
      <h3>Rules (Phase-1)</h3>
      <p>Partner Agent → Shadow Channel → Interceptor → Audit → Human Confirm → Permit → Production Channel</p>
      <hr/>
      <p class="small">این صفحه نمونه UI است؛ مسیر واقعی در سرویس‌های BL-15/16/17/22 قفل می‌شود.</p>
    </div>
  `;
}

function renderKpis(){
  return `
    <div class="h1">
      <div>
        <h1>${t('page.kpis')}</h1>
        <p>حاکمیت بدون شاخص یعنی نمایش. اینجا KPIهای کنترل و KRIهای ریسک را می‌بینید.</p>
      </div>
      <div class="split">
        <button class="btn" id="refreshKpi">Refresh</button>
        <button class="btn primary" id="reportBoard">Board Report</button>
      </div>
    </div>
    <div class="grid">
      <div class="card" style="grid-column: span 4"><h3>Decisions Executed</h3><p><b>1,284</b> (all via Permit)</p></div>
      <div class="card" style="grid-column: span 4"><h3>Messages Rejected</h3><p><b>37</b> (missing envelope / bad signature)</p></div>
      <div class="card" style="grid-column: span 4"><h3>Policy Exceptions</h3><p><b>3</b> (all recorded)</p></div>
      <div class="card" style="grid-column: span 12"><h3>Starred Note</h3><p>در حکمرانی، پیچیدگی و راه‌حل‌های آن ماهیت اجتناب‌ناپذیر مسئله است و نباید ساده‌سازی انکاری شود.</p></div>
    </div>
  `;
}

function viewFor(hash){
  if(hash.startsWith('#/agents')) return renderAgents();
  if(hash.startsWith('#/policies')) return renderPolicies();
  if(hash.startsWith('#/permits')) return renderPermits();
  if(hash.startsWith('#/audit')) return renderAudit();
  if(hash.startsWith('#/channels')) return renderChannels();
  if(hash.startsWith('#/partners')) return renderPartners();
  if(hash.startsWith('#/kpis')) return renderKpis();
  return renderOverview();
}

function wireCommon(){
  // theme toggle
  const tbtn = $('#toggleTheme');
  if(tbtn){
    tbtn.onclick=()=>{
      const root=document.documentElement;
      const cur=root.getAttribute('data-theme')||'dark';
      const nxt=cur==='dark'?'light':'dark';
      root.setAttribute('data-theme',nxt);
      localStorage.setItem('agentos_theme',nxt);
      $('#themeLabel').textContent = nxt==='dark' ? 'Dark' : 'Light';
    };
  }
  // modal
  const back = $('#modalBackdrop');
  $('#modalClose').onclick=()=>{back.style.display='none'};
  back.addEventListener('click',(e)=>{ if(e.target===back) back.style.display='none';});
  document.addEventListener('keydown',(e)=>{ if(e.key==='Escape') back.style.display='none'; });

  // quick modal triggers (safe demo)
  document.addEventListener('click',(e)=>{
    const btn=e.target.closest('[data-open]');
    if(!btn) return;
    const kind=btn.getAttribute('data-open');
    if(kind==='agent'){
      const name=btn.getAttribute('data-name');
      openModal('Agent Inspect', `
        <div class="card"><h3>${esc(name)}</h3><p class="small">این نما فقط خواندنی است. هر تغییر باید از Policy/Permit عبور کند.</p></div>
        <div class="card"><h3>4W+H</h3>
          <p class="small"><b>Who:</b> ${esc(name)} · <b>What:</b> Suggestion/Observation · <b>Why:</b> reduce blind spots · <b>Where:</b> layer-bound · <b>How:</b> AACP events + audit envelope</p>
        </div>
      `);
    }
  });

  // shortcuts
  document.addEventListener('keydown',(e)=>{
    if(e.ctrlKey && e.key.toLowerCase()==='k'){
      e.preventDefault();
      openModal('Command Palette (Demo)', `
        <div class="card"><h3>Shortcuts</h3><p class="small">Ctrl+K · open palette (demo)</p></div>
        <div class="card"><h3>Navigation</h3><p class="small">#/overview · #/agents · #/policies · #/permits · #/audit · #/channels · #/partners · #/kpis</p></div>
      `);
    }
  });
}

function openModal(title, html){
  $('#modalTitle').textContent=title;
  $('#modalBody').innerHTML=html;
  $('#modalBackdrop').style.display='flex';
}

function wireRouteSpecific(hash){
  if(hash.startsWith('#/agents')){
    const input=$('#agentSearch');
    const tbody=$('#agentRows');
    if(input && tbody){
      input.addEventListener('input', ()=>{
        const q=input.value.trim().toLowerCase();
        const rows=MOCK.agents
          .filter(a => !q || a.name.toLowerCase().includes(q) || a.layer.toLowerCase().includes(q))
          .map(a=>`
            <tr>
              <td>${esc(a.layer)}</td>
              <td><b>${esc(a.name)}</b><div class="small">${esc(a.code)} · owner=${esc(a.owner)}</div></td>
              <td>${badge(a.status)}</td>
              <td><button class="btn" data-open="agent" data-name="${esc(a.name)}">Inspect</button></td>
            </tr>
          `).join('');
        tbody.innerHTML=rows;
      });
    }
  }
  if(hash.startsWith('#/overview')){
    const qa=$('#openAudit'); if(qa) qa.onclick=()=>location.hash='#/audit';
    const np=$('#newPermit'); if(np) np.onclick=()=>location.hash='#/permits';
  }
}

function bootstrap(){
  // load theme from storage
  const saved = localStorage.getItem('agentos_theme');
  if(saved) document.documentElement.setAttribute('data-theme', saved);
  $('#themeLabel').textContent = (document.documentElement.getAttribute('data-theme')||'dark')==='dark' ? 'Dark' : 'Light';

  wireCommon();
  onRoute((hash)=>{
    setActiveNav(hash);
    $('#view').innerHTML=viewFor(hash);
    wireRouteSpecific(hash);
    $('#statusPill').textContent = MOCK.system.phase;
    $('#buildPill').textContent = MOCK.system.build;
  });
}
bootstrap();
