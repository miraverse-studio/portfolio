# AI制作ポートフォリオ（portfolio-hub）

AIを使って「検証済みの小さなプロトタイプ」を設計・統制した記録です。
要件定義・設計判断・テスト基準・レビュー観点・セキュリティ確認は自分が行い、
実装はAI（主にClaude Code）に委譲しています。

## これは何か / 誰に見せるものか
- コードと設計プロセスの両方を見たいエンジニア向けのポートフォリオ入口です。
- まず `index.html` を開いてください。

## 30秒の見方
1. `index.html` を開く（入口）
2. 代表作「AI制作管理OS v0.1」を実際に触る
3. テスト結果とコードで「動くこと／読めること」を確認する
4. 見てほしい観点は `REVIEW_GUIDE.md` にまとめています

## 掲載成果物
| 名前 | 種別 | ランク | 入口 |
|---|---|---|---|
| AI制作管理OS v0.1 | 動くWebアプリ | A（手動テスト 55/55 PASS） | apps/ai-os/index.html |
| Prompt Launcher v1 | 動くツール | A | apps/prompt-launcher/index.html |
| Mira Full-Power Test（41本） | HTML/ツール群 | A | apps/full-power-test/index.html |
| Chrome拡張 | ブラウザ拡張 | B | projects/chrome-extension.md |
| AI制作練度カリキュラム | 学習設計 | A | projects/ai-skill-curriculum.md |
| Claude Code共通起動パック | プロセス設計 | A | projects/session-start-pack.md |
| Blender学習支援OS v0.1 | 動くWebアプリ | A（実機テスト14件PASS） | apps/blender-os/index.html |

## 技術的制約（意図的な縛り）
- 静的HTMLのみ ／ 外部ライブラリなし ／ 外部APIなし ／ 個人情報なし
- データはブラウザの localStorage に保存（サーバー送信なし）

## AIとの役割分担
- 自分: 要件・設計判断・テスト基準・レビュー観点・セキュリティ確認・品質ゲート
- AI: 実装・リファクタ・ドキュメント草案の生成

## 現時点の弱点（正直に）
- Git/公開運用はこれから（本リポジトリがその実践）
- フレームワーク利用はまだ少ない（素のJS中心）
- 一般公開前のセキュリティチェックは未完了

## 公開ステータス
現在はレビュー準備段階です。`SECURITY_PUBLIC_CHECKLIST.md` の全項目を満たしてから一般公開します。

## レビューのお願い
見てほしい観点は [REVIEW_GUIDE.md](REVIEW_GUIDE.md) にまとめています。
