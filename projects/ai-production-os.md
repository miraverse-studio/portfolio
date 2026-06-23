# AI制作管理OS v0.1

> 一言: 自分の制作物を登録・管理する自作Webアプリ
> 種別: 動くWebアプリ ／ ランク: A（手動テスト 55/55 PASS）

## これは何か
作品を登録・編集・削除し、ダッシュボードで俯瞰、JSONで入出力、Markdownレポートを生成できる管理ツール。
データは localStorage に保存（サーバー送信なし）。

## 触り方
`../apps/ai-os/index.html` を開く → 1件登録 → ダッシュボード確認 → JSON入出力 → Markdownレポート生成

## 見てほしいポイント
- escHtml による innerHTML エスケープ（XSS対策）
- 純粋関数への切り出し（テスト可能性）
- 素のJSでの状態管理の設計
- 品質管理: 初回 53/55 → escHtml 重複定義バグ修正 → 55/55

## 既知の弱点
- フレームワーク未使用（意図的）
- 自動テストはユニット中心、E2E/CI なし

## リンク
- デモ: ../apps/ai-os/index.html
- テスト結果: ../apps/ai-os/TEST_RESULT.md
- テストランナー: ../apps/ai-os/test-runner.html
- ソースコード: GitHub 公開時にリンクを追加します
