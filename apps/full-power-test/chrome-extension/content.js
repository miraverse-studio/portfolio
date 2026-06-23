// Mira Hub — Content Script
// Injects a floating action button (FAB) on all pages

(function() {
  'use strict';

  // Avoid double injection
  if (document.getElementById('mira-fab')) return;

  // ─── FAB button ──────────────────────────────────────────────────────────────
  const fab = document.createElement('div');
  fab.id = 'mira-fab';
  fab.innerHTML = '🌸';
  fab.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7c3aed, #f59e0b);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    cursor: pointer;
    z-index: 2147483647;
    box-shadow: 0 4px 16px rgba(124,58,237,0.5);
    transition: transform 0.2s, box-shadow 0.2s;
    user-select: none;
  `;
  fab.title = 'Mira Hub';

  fab.addEventListener('mouseenter', () => {
    fab.style.transform = 'scale(1.1)';
    fab.style.boxShadow = '0 6px 24px rgba(124,58,237,0.7)';
  });
  fab.addEventListener('mouseleave', () => {
    fab.style.transform = 'scale(1.0)';
    fab.style.boxShadow = '0 4px 16px rgba(124,58,237,0.5)';
  });

  // ─── Mini panel ──────────────────────────────────────────────────────────────
  const panel = document.createElement('div');
  panel.id = 'mira-panel';
  panel.style.cssText = `
    position: fixed;
    bottom: 74px;
    right: 20px;
    width: 240px;
    background: rgba(7,7,15,0.96);
    border: 1px solid rgba(124,58,237,0.3);
    border-radius: 16px;
    padding: 14px;
    z-index: 2147483647;
    display: none;
    font-family: -apple-system, 'Hiragino Sans', sans-serif;
    color: #e2e8f0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.6);
    backdrop-filter: blur(12px);
  `;

  panel.innerHTML = `
    <div style="font-size:11px;color:#a78bfa;font-weight:700;letter-spacing:0.1em;margin-bottom:10px;">MIRA HUB</div>

    <!-- Pomo timer display -->
    <div id="ac-pomo-display" style="background:rgba(124,58,237,0.1);border:1px solid rgba(124,58,237,0.2);border-radius:10px;padding:10px;text-align:center;margin-bottom:10px;">
      <div id="ac-pomo-time" style="font-size:24px;font-weight:900;font-family:'JetBrains Mono',monospace;color:#a78bfa;">25:00</div>
      <div id="ac-pomo-label" style="font-size:9px;color:#64748b;margin-top:2px;">IDLE</div>
      <div style="display:flex;gap:6px;justify-content:center;margin-top:8px;">
        <button id="ac-pomo-btn" style="font-size:10px;padding:4px 12px;border-radius:8px;cursor:pointer;border:1px solid rgba(124,58,237,0.4);background:rgba(124,58,237,0.12);color:#a78bfa;font-family:inherit;">▶ 開始</button>
        <button id="ac-pomo-stop" style="font-size:10px;padding:4px 12px;border-radius:8px;cursor:pointer;border:1px solid rgba(255,255,255,0.1);background:transparent;color:rgba(255,255,255,0.3);font-family:inherit;">■ 停止</button>
      </div>
    </div>

    <!-- Quick note -->
    <textarea id="ac-note" placeholder="クイックメモ..." style="width:100%;height:60px;background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.08);border-radius:8px;color:#e2e8f0;font-size:11px;padding:6px 8px;resize:none;font-family:inherit;outline:none;"></textarea>

    <!-- Stats -->
    <div style="display:flex;gap:6px;margin-top:8px;">
      <div style="flex:1;background:rgba(0,0,0,0.2);border-radius:8px;padding:6px;text-align:center;">
        <div id="ac-sessions" style="font-size:16px;font-weight:900;color:#f59e0b;">0</div>
        <div style="font-size:8px;color:#64748b;">セッション</div>
      </div>
      <div style="flex:1;background:rgba(0,0,0,0.2);border-radius:8px;padding:6px;text-align:center;">
        <div id="ac-tabs" style="font-size:16px;font-weight:900;color:#34d399;">0</div>
        <div style="font-size:8px;color:#64748b;">タブ数</div>
      </div>
      <div style="flex:1;background:rgba(0,0,0,0.2);border-radius:8px;padding:6px;text-align:center;">
        <div id="ac-focus" style="font-size:16px;font-weight:900;color:#60a5fa;">0h</div>
        <div style="font-size:8px;color:#64748b;">集中時間</div>
      </div>
    </div>
  `;

  let panelOpen = false;
  fab.addEventListener('click', () => {
    panelOpen = !panelOpen;
    panel.style.display = panelOpen ? 'block' : 'none';
    if (panelOpen) refreshPanel();
  });

  document.body.appendChild(fab);
  document.body.appendChild(panel);

  // ─── Panel logic ─────────────────────────────────────────────────────────────
  let polling = null;

  function fmtTime(sec) {
    const m = Math.floor(sec / 60).toString().padStart(2,'0');
    const s = (sec % 60).toString().padStart(2,'0');
    return `${m}:${s}`;
  }

  function refreshPanel() {
    chrome.runtime.sendMessage({ type: 'GET_STATUS' }, data => {
      if (!data) return;
      document.getElementById('ac-pomo-time').textContent  = fmtTime(data.pomo_remaining || 1500);
      document.getElementById('ac-pomo-label').textContent =
        data.pomo_state === 'work' ? '🍅 集中中' : data.pomo_state === 'break' ? '☕ 休憩中' : 'IDLE';
      document.getElementById('ac-sessions').textContent   = data.pomo_sessions || 0;
      document.getElementById('ac-tabs').textContent       = data.tab_count || 0;
      const hours = Math.floor((data.total_focus_sec || 0) / 3600);
      const mins  = Math.floor(((data.total_focus_sec || 0) % 3600) / 60);
      document.getElementById('ac-focus').textContent = hours > 0 ? `${hours}h` : `${mins}m`;
      document.getElementById('ac-note').value        = data.quick_memo || '';
    });
  }

  // Start/stop pomo
  document.getElementById('ac-pomo-btn').addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'POMO_START' }, () => { refreshPanel(); });
  });
  document.getElementById('ac-pomo-stop').addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'POMO_STOP' }, () => { refreshPanel(); });
  });

  // Auto-save memo
  document.getElementById('ac-note').addEventListener('input', e => {
    chrome.storage.local.set({ quick_memo: e.target.value });
  });

  // Poll every 5 seconds when panel is open
  setInterval(() => {
    if (panelOpen) refreshPanel();
  }, 5000);

  // Close panel when clicking outside
  document.addEventListener('click', e => {
    if (panelOpen && !panel.contains(e.target) && e.target !== fab) {
      panelOpen = false;
      panel.style.display = 'none';
    }
  });
})();
