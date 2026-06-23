# Mira Productivity Hub — Chrome Extension

Manifest V3 準拠のChrome拡張機能。どのサイトでも使えるポモドーロ・タスク管理・クイックメモ。

## ファイル構成

```
chrome-extension/
├── manifest.json      # MV3マニフェスト
├── background.js      # Service Worker (アラーム・タブ監視)
├── content.js         # 全サイトに🌸FABボタンを注入
├── popup.html/js      # ツールバーアイコンクリック時のポップアップ
├── generate_icons.py  # アイコンPNG生成スクリプト
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## インストール手順

```bash
# 1. アイコンを生成
cd chrome-extension
python generate_icons.py

# 2. Chromeで読み込む
# chrome://extensions/ を開く
# 「デベロッパーモード」をON
# 「パッケージ化されていない拡張機能を読み込む」をクリック
# このフォルダ (chrome-extension/) を選択
```

## 機能

| 機能 | 説明 |
|------|------|
| 🍅 ポモドーロタイマー | Background Service Workerで精密計測。完了時にOS通知 |
| ✅ タスク管理 | chrome.storage.localで永続保存。追加・完了・削除 |
| 📝 クイックメモ | どのサイトからでも即座にメモ。自動保存 |
| 🔗 アプリランチャー | Miraの各アプリへワンクリックアクセス |
| 🌸 FABボタン | 全サイトに浮かぶミニパネル。ポモ残時間・メモがどこでも確認可能 |
| 📊 タブカウンター | 開いているタブ数をリアルタイム監視 |

## 技術仕様

- **Manifest V3** (MV2廃止対応済み)
- **Background Service Worker** (MV3標準。永続バックグラウンドページなし)
- **chrome.alarms API** — 1秒単位のポモドーロタイマー
- **chrome.notifications API** — OS標準通知でタイマー完了を通知
- **chrome.storage.local** — データ永続化 (sync APIではなくlocal)
- **Content Script** — `<all_urls>` マッチで全サイトにFABを注入
- **chrome.runtime.sendMessage** — popup ↔ background ↔ content通信

## 注意事項

- APIキー・認証情報は一切含まれていません
- 外部サーバーへの通信は行いません（完全ローカル動作）
- permissions: storage, alarms, notifications, tabs, activeTab のみ使用
