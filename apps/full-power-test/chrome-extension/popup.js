// Mira Hub — Popup Script

const LINKS = [
  { icon:'📊', name:'ダッシュボード', url:'dashboard.html' },
  { icon:'📌', name:'カンバン',       url:'kanban.html' },
  { icon:'🍅', name:'ポモドーロ',     url:'pomodoro.html' },
  { icon:'🗺', name:'マインドマップ', url:'mindmap.html' },
  { icon:'🌐', name:'組織ネット',     url:'network.html' },
  { icon:'✨', name:'シェーダー',     url:'shader.html' },
  { icon:'🎵', name:'アンビエント',   url:'ambient.html' },
  { icon:'📝', name:'メモ帳',         url:'memo.html' },
];

// Note: In a real installation, these would point to the actual app URL.
// For demo/dev purposes, the links open relative paths.
const APP_BASE = './';

let currentTab = 'pomo';
let pomoData = {};
let refreshInterval;

// ─── Tab switching ─────────────────────────────────────────────────────────────
function switchTab(tab) {
  currentTab = tab;
  ['pomo','task','memo','links'].forEach(t => {
    document.getElementById('sec-' + t).style.display = t === tab ? '' : 'none';
    document.getElementById('tab-' + t).className = 'tab' + (t === tab ? ' active' : '');
  });
  if (tab === 'task') renderTasks();
  if (tab === 'memo') loadMemo();
  if (tab === 'links') renderLinks();
}
window.switchTab = switchTab;

// ─── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Header date
  const now = new Date();
  document.getElementById('hdr-date').textContent = now.toLocaleDateString('ja-JP', {month:'short',day:'numeric',weekday:'short'});

  loadPomoData();
  refreshInterval = setInterval(loadPomoData, 1000);

  // Memo auto-save
  document.getElementById('memo-area').addEventListener('input', saveMemo);

  // Task enter key
  document.getElementById('task-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') addTask();
  });
});

// ─── Pomo ─────────────────────────────────────────────────────────────────────
function loadPomoData() {
  chrome.runtime.sendMessage({ type: 'GET_STATUS' }, data => {
    if (!data) return;
    pomoData = data;

    const remaining = data.pomo_remaining || 1500;
    const state     = data.pomo_state    || 'idle';
    const workMax   = (data.pomo_work_min || 25) * 60;
    const breakMax  = (data.pomo_break_min || 5) * 60;
    const maxTime   = state === 'break' ? breakMax : workMax;
    const pct       = Math.max(0, remaining / maxTime * 100);

    const m = Math.floor(remaining / 60).toString().padStart(2,'0');
    const s = (remaining % 60).toString().padStart(2,'0');
    document.getElementById('pomo-time').textContent = `${m}:${s}`;

    const stateLabel = { idle:'IDLE · 集中25分', work:'🍅 集中中', break:'☕ 休憩中' };
    document.getElementById('pomo-state').textContent = stateLabel[state] || 'IDLE';
    document.getElementById('pomo-bar').style.width = pct + '%';

    document.getElementById('ps-sessions').textContent = data.pomo_sessions || 0;
    const totalMin = Math.floor((data.total_focus_sec || 0) / 60);
    const totalH   = Math.floor(totalMin / 60);
    document.getElementById('ps-focus').textContent = totalH > 0 ? `${totalH}h${totalMin%60}m` : `${totalMin}m`;
    document.getElementById('ps-tabs').textContent  = data.tab_count || 0;
    document.getElementById('hdr-tabs').textContent = `${data.tab_count || 0} tabs open`;

    const startBtn = document.getElementById('pomo-start');
    if (state === 'idle') { startBtn.textContent = '▶ 開始'; startBtn.style.opacity = '1'; }
    else { startBtn.textContent = '⏸ 実行中'; startBtn.style.opacity = '0.5'; }
  });
}

function pomoStart() {
  chrome.runtime.sendMessage({ type: 'POMO_START' }, () => { loadPomoData(); });
}
window.pomoStart = pomoStart;

function pomoStop() {
  chrome.runtime.sendMessage({ type: 'POMO_STOP' }, () => { loadPomoData(); });
}
window.pomoStop = pomoStop;

// ─── Tasks ────────────────────────────────────────────────────────────────────
function renderTasks() {
  chrome.storage.local.get(['tasks'], data => {
    const tasks = data.tasks || [];
    const list = document.getElementById('task-list');
    list.innerHTML = tasks.map(t => `
      <div class="task-item">
        <div class="task-check ${t.done?'done':''}" onclick="toggleTask(${t.id})"></div>
        <div class="task-text ${t.done?'done':''}">${escHtml(t.text)}</div>
        <div class="task-del" onclick="deleteTask(${t.id})">✕</div>
      </div>
    `).join('');
  });
}

function addTask() {
  const input = document.getElementById('task-input');
  const text = input.value.trim();
  if (!text) return;
  chrome.storage.local.get(['tasks','next_task_id'], data => {
    const tasks = data.tasks || [];
    const id = data.next_task_id || (tasks.length + 1);
    tasks.push({ id, text, done: false });
    chrome.storage.local.set({ tasks, next_task_id: id + 1 }, renderTasks);
  });
  input.value = '';
}
window.addTask = addTask;

function toggleTask(id) {
  chrome.storage.local.get(['tasks'], data => {
    const tasks = (data.tasks || []).map(t => t.id === id ? {...t, done: !t.done} : t);
    chrome.storage.local.set({ tasks }, renderTasks);
  });
}
window.toggleTask = toggleTask;

function deleteTask(id) {
  chrome.storage.local.get(['tasks'], data => {
    const tasks = (data.tasks || []).filter(t => t.id !== id);
    chrome.storage.local.set({ tasks }, renderTasks);
  });
}
window.deleteTask = deleteTask;

// ─── Memo ─────────────────────────────────────────────────────────────────────
function loadMemo() {
  chrome.storage.local.get(['quick_memo','memo_saved'], data => {
    document.getElementById('memo-area').value = data.quick_memo || '';
    if (data.memo_saved) {
      const d = new Date(data.memo_saved);
      document.getElementById('memo-saved').textContent = `最終保存: ${d.toLocaleTimeString('ja-JP')}`;
    }
  });
}

function saveMemo() {
  const val = document.getElementById('memo-area').value;
  const now = new Date().toISOString();
  chrome.storage.local.set({ quick_memo: val, memo_saved: now }, () => {
    const d = new Date(now);
    document.getElementById('memo-saved').textContent = `最終保存: ${d.toLocaleTimeString('ja-JP')}`;
  });
}

// ─── Links ────────────────────────────────────────────────────────────────────
function renderLinks() {
  const grid = document.getElementById('link-grid');
  grid.innerHTML = LINKS.map(l => `
    <a class="link-card" href="${APP_BASE}${l.url}" target="_blank">
      <div class="link-icon">${l.icon}</div>
      <div class="link-name">${l.name}</div>
    </a>
  `).join('');
}

// ─── Util ─────────────────────────────────────────────────────────────────────
function escHtml(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
