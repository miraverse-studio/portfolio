// Mira Productivity Hub — Background Service Worker (MV3)
// Handles: pomodoro timer alarms, tab tracking, session stats

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    pomo_state: 'idle',       // idle | work | break
    pomo_remaining: 25 * 60,  // seconds
    pomo_sessions: 0,
    pomo_work_min: 25,
    pomo_break_min: 5,
    tab_count: 0,
    total_focus_sec: 0,
    install_date: new Date().toISOString(),
    quick_memo: '',
    tasks: [
      { id:1, text:'Meshyで3Dモデル制作', done:false },
      { id:2, text:'Claudeセッション記録まとめ', done:false },
      { id:3, text:'収益ダッシュボード更新', done:true },
    ],
    next_task_id: 4,
  });
});

// ─── Pomodoro alarm handling ───────────────────────────────────────────────────
chrome.alarms.onAlarm.addListener(alarm => {
  if (alarm.name === 'pomo-tick') {
    chrome.storage.local.get(['pomo_state','pomo_remaining','pomo_sessions','pomo_work_min','pomo_break_min','total_focus_sec'], data => {
      if (data.pomo_state === 'idle') return;

      let remaining = (data.pomo_remaining || 0) - 1;
      let sessions  = data.pomo_sessions  || 0;
      let totalFocus = (data.total_focus_sec || 0);

      if (data.pomo_state === 'work') totalFocus++;

      if (remaining <= 0) {
        if (data.pomo_state === 'work') {
          sessions++;
          chrome.notifications.create('pomo-done', {
            type: 'basic',
            iconUrl: 'icons/icon48.png',
            title: '🍅 集中タイム完了！',
            message: `${sessions}セッション達成！${data.pomo_break_min}分の休憩をどうぞ。`,
            priority: 2,
          });
          chrome.storage.local.set({ pomo_state:'break', pomo_remaining: data.pomo_break_min*60, pomo_sessions:sessions, total_focus_sec:totalFocus });
        } else {
          chrome.notifications.create('break-done', {
            type: 'basic',
            iconUrl: 'icons/icon48.png',
            title: '✅ 休憩終了',
            message: '次のポモドーロを開始しましょう！',
            priority: 1,
          });
          chrome.storage.local.set({ pomo_state:'idle', pomo_remaining: data.pomo_work_min*60, total_focus_sec:totalFocus });
        }
      } else {
        chrome.storage.local.set({ pomo_remaining: remaining, total_focus_sec:totalFocus });
      }
    });
  }
});

// ─── Tab count tracking ────────────────────────────────────────────────────────
function updateTabCount() {
  chrome.tabs.query({}, tabs => {
    chrome.storage.local.set({ tab_count: tabs.length });
  });
}
chrome.tabs.onCreated.addListener(updateTabCount);
chrome.tabs.onRemoved.addListener(updateTabCount);

// ─── Message handler (from popup) ─────────────────────────────────────────────
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'POMO_START') {
    chrome.alarms.create('pomo-tick', { periodInMinutes: 1/60 });  // every second
    chrome.storage.local.get(['pomo_work_min'], data => {
      chrome.storage.local.set({ pomo_state:'work', pomo_remaining: data.pomo_work_min*60 });
      sendResponse({ ok: true });
    });
    return true;
  }
  if (msg.type === 'POMO_STOP') {
    chrome.alarms.clear('pomo-tick');
    chrome.storage.local.get(['pomo_work_min'], data => {
      chrome.storage.local.set({ pomo_state:'idle', pomo_remaining: data.pomo_work_min*60 });
      sendResponse({ ok: true });
    });
    return true;
  }
  if (msg.type === 'GET_STATUS') {
    chrome.storage.local.get(null, data => sendResponse(data));
    return true;
  }
});
