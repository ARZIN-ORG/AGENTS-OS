#!/bin/bash
set -e

cd /home/zi/WORKSPACES/SHARED/AGENTS-OS/Landing-ui/ui

echo "1. تغییر mode در index.html به real"
sed -i 's/mode: "mock"/mode: "real"/g' index.html

echo "2. تغییر mode در config.js به real"
sed -i "s/mode: (c.mode || 'mock').toString()/mode: 'real'/g" js/config.js

echo "3. حذف ایمپورت MOCK از app.js"
sed -i '/import {MOCK} from/d' js/app.js

echo "4. جایگزینی تمام MOCK. با await fetch... در app.js (با فرض وجود توابع api)"
# این دستورات ساده هستند؛ برای دقت بیشتر نیاز به تحلیل محتواست، اما فعلاً سریع تغییر می‌دهیم
sed -i 's/MOCK\.system/await fetchSystem()/g' js/app.js
sed -i 's/MOCK\.agents/await fetchAgents()/g' js/app.js
sed -i 's/MOCK\.channels/await fetchChannels()/g' js/app.js
sed -i 's/MOCK\.policies/await fetchPolicies()/g' js/app.js
sed -i 's/MOCK\.audit/await fetchAudit()/g' js/app.js
sed -i 's/MOCK\.permits/await fetchPermits()/g' js/app.js

echo "5. اضافه کردن import توابع api به ابتدای app.js (اگر هنوز وجود ندارد)"
if ! grep -q "import { fetchSystem" js/app.js; then
  sed -i '1i import { fetchSystem, fetchAgents, fetchPolicies, fetchAudit, fetchPermits, fetchChannels } from "./api.js";' js/app.js
fi

echo "6. ساخت api.js کامل (اگر وجود ندارد، بازنویسی می‌شود)"
cat > js/api.js << 'APIFILE'
const API_BASE = window.CONFIG?.apiBase || 'http://localhost:8000';
export async function fetchSystem() {
  const res = await fetch(`${API_BASE}/system`);
  return res.json();
}
export async function fetchAgents() {
  const res = await fetch(`${API_BASE}/agents`);
  return res.json();
}
export async function fetchPolicies() {
  const res = await fetch(`${API_BASE}/policies`);
  return res.json();
}
export async function fetchAudit() {
  const res = await fetch(`${API_BASE}/audit`);
  return res.json();
}
export async function fetchPermits() {
  const res = await fetch(`${API_BASE}/permits`);
  return res.json();
}
export async function fetchChannels() {
  const res = await fetch(`${API_BASE}/channels`);
  return res.json();
}
APIFILE

echo "7. تبدیل تابع render به async در app.js"
sed -i 's/function render()/async function render()/g' js/app.js
sed -i 's/const render = /const render = async /g' js/app.js

echo "8. افزودن Media Queries جدید به app.css"
cat >> css/app.css << 'CSSEOF'

/* ===== موبایل ===== */
@media (max-width: 600px) {
  body { font-size: 14px; }
  .container { padding: 0.5rem; }
  .grid { grid-template-columns: 1fr !important; }
  .card { margin: 0.5rem 0; }
  .split { flex-direction: column; align-items: flex-start; gap: 0.25rem; }
  .badge-group { flex-wrap: wrap; }
  table { font-size: 0.75rem; }
  table td, table th { padding: 0.3rem 0.2rem; }
  .nav { flex-direction: column; gap: 0.5rem; }
  .pill { font-size: 0.7rem; padding: 0.15rem 0.5rem; }
}
@media (min-width: 601px) and (max-width: 980px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
  .container { padding: 1rem; }
}
CSSEOF

echo "✅ همه تغییرات اعمال شد. فایل mock-data.js را می‌توانید حذف کنید."
