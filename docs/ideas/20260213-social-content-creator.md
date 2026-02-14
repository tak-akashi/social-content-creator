# Social Content Creator

> 作成日: 2026-02-13
> ステータス: draft
> 優先度: P1

## 概要

AIエンジニア「Aidotters」としての情報発信を効率化するため、Claude Codeのスキルおよびpythonツール群を活用し、ブログ記事・SNS投稿の作成から投稿までを一貫して行う仕組みを構築する。

## 背景

### 現状の課題

- フリーランスAIエンジニアとして情報発信の重要性を認識しているが、記事作成の時間を捻出できない
- Notionに蓄積した情報資産（AI論文要約、ニュース、Medium記事）が発信に活かせていない
- Aidottersとしてのブランド発信基盤がまだ整っていない

### 解決したいこと

- 最小限の手間でコンスタントに質の高い記事を発信できる状態にする（週2〜3回）
- 蓄積した情報資産を効率的にコンテンツ化するパイプラインを構築する
- AIエンジニアとしてのビジネスに繋がる発信基盤を確立する

## 解決策

### アプローチ

Claude Codeのスキルとして記事作成コマンドを実装し、バックエンドにPythonツール群を配置する2層構造で構築する。

```
ユーザー → /create-blog-post → Claude Code（スキル層）
              → Pythonツール群（情報収集、記事整形、API投稿など）
```

### 設計方針

1. **スキル層とツール層の分離**: ユーザーインターフェースはClaude Codeスキル、バックエンド処理はPythonツール群として実装
2. **段階的な構築**: MVP（ブログ記事生成）から始め、X投稿、Notion連携と段階的に拡張
3. **情報収集手段の柔軟性**: Web検索、Gemini CLI、Notion DB、URL指定など、手段を限定せず幅広く活用

### 代替案と比較

| 案 | メリット | デメリット | 採否 |
|----|---------|-----------|------|
| Claude Codeスキル + Pythonツール群 | 対話的に操作可能、柔軟な拡張性 | Claude Code環境が必要 | 採用 |
| 独立したCLIツール | 単体で動作、CI/CD連携しやすい | 対話的な記事推敲が困難 | 不採用 |
| Webアプリケーション | GUI操作、共有しやすい | 開発コストが高い、現時点で不要 | 不採用 |

## 実装する機能

### ロードマップ（段階的開発）

| Phase | 機能 | 概要 |
|-------|------|------|
| 1 | ブログ記事生成・投稿 | WordPress連携での記事作成・投稿（今回のスコープ） |
| 2 | X投稿 | テキスト・画像・動画付き投稿 |
| 3 | Notion DB連携 | 蓄積データからの自動ネタ収集・記事生成 |

### 機能1: ブログ記事生成スキル

Claude Codeスキルとして、記事タイプやソースを指定して記事を生成する。

```
/create-blog-post --type weekly-ai-news
/create-blog-post --type paper-review --url https://arxiv.org/abs/xxxx
/create-blog-post --type project-intro --repo tak/my-project
/create-blog-post --type tool-tips --topic "Difyの使い方"
/create-blog-post --type market-analysis --topic "ミネルヴィニ手法による銘柄スクリーニング"
/create-blog-post --type ml-practice --topic "Claude Codeで特徴量エンジニアリングを効率化する"
/create-blog-post --type cv --topic "YOLOv8で物体検出を試してみた"
/create-blog-post --topic "LangChainの最新アップデート"
```

**パラメータ/オプション:**
- `--type`: 記事タイプ（weekly-ai-news / paper-review / project-intro / tool-tips / market-analysis / ml-practice / cv / feature）
- `--url`: 参照URL（論文、リポジトリ等）
- `--repo`: GitHubリポジトリ指定
- `--topic`: トピック・キーワード指定

### 機能2: コンテンツタイプ別テンプレート

| コンテンツタイプ | 文字数目安 | 内容 |
|---------------|-----------|------|
| 週刊AIニュースハイライト | 3,000〜5,000字 | その週のAI関連ニュースをまとめて紹介 |
| 論文解説 | 5,000〜8,000字 | AI論文の要約・解説・考察 |
| GitHubプロジェクト紹介 | 3,000〜5,000字 | 自身のプロジェクトの解説記事 |
| ツール・Tips紹介 | 3,000〜5,000字 | Dify / n8n / Google AI Studio / ブログ作成自動化のコツなど |
| AI×株式投資・企業分析 | 3,000〜8,000字 | Claude CodeやAIを株式投資・マーケット分析・企業分析にどう活用するかの技術ノウハウ |
| AI×データ分析・ML開発 | 3,000〜8,000字 | Claude Code/LLMを活用したデータ分析ワークフローやMLモデル開発の実践ノウハウ |
| 画像認識・コンピュータビジョン | 3,000〜8,000字 | 画像認識技術の解説・実践（自身のキャッチアップ兼アウトプット） |
| 特集記事 | 15,000〜20,000字 | 特定テーマの深掘り記事 |

### 機能3: WordPress投稿

Pythonツールとして、WordPress REST APIを利用した記事投稿機能を実装する。

### 機能4: 情報収集ツール群

記事作成のための情報収集手段をPythonツールとして実装する。

| 手段 | 用途 |
|------|------|
| Web検索 | リアルタイムの情報収集 |
| Gemini CLI | 調査レポート生成 |
| Notion MCP連携 | 蓄積データ（AI論文要約 / Google Alertニュース / Medium記事）の参照 |
| GitHub API | 自身のリポジトリ情報取得 |
| URL取得・解析 | 指定された論文・記事の内容取得 |
| stock-analysis参照 | 自作の株式分析プロジェクトのコード・分析結果を記事素材として活用（後述） |
| その他 | 必要に応じて柔軟に拡張 |

### 機能5: stock-analysis プロジェクトを題材としたコンテンツ

別プロジェクト（`/Users/tak/Markets/Stocks/stock-analysis/`）で構築済みの日本株分析システムを**記事の題材・実例**として活用する。記事の主眼は「AIエンジニアが株式投資・企業分析にClaude CodeやAIをどう使うか」という技術ノウハウの共有。

**stock-analysisプロジェクトの概要:**
- J-Quants APIによる日本株データ収集（日次価格、財務データ）
- テクニカル分析（Minervini、HL比率、RSP/RSI、チャートパターン分類）
- 統合スコアリングによる銘柄スクリーニング（StockScreener）
- バックテスト・戦略最適化（Backtester / StrategyOptimizer）
- 仮想ポートフォリオ管理（VirtualPortfolio）
- plotlyによるインタラクティブチャート生成（TechnicalAnalyzer）

**想定する記事テーマ例:**
- Claude Codeで株式分析ツールを作ってみた（設計思想・実装プロセス）
- AIを活用したMinerviniトレンドスクリーニングの自動化
- Claude Code × Python で作るバックテストシステム
- 機械学習によるチャートパターン分類をAIエンジニアが解説
- J-Quants API × AI で日本株分析を効率化する方法
- AIエンジニアが実践する企業分析の自動化ワークフロー

**活用方法:**
- プロジェクトのコードや設計を記事の具体例として引用
- 分析結果やチャート画像を記事素材として使用
- 「AIでこう作った」という実践的なストーリーテリング

## 記事スタイルガイド

### 文体
- です・ます調、丁寧かつ親しみやすい
- カジュアルすぎず、フォーマルすぎない中間
- 参考スタイル: [ShiftAIブログ](https://shift-ai.co.jp/blog/10672/)

### 構成ルール
- 見出しで構造化し、読みやすく分割
- 専門用語は初出時に簡潔に説明
- 具体例やコード例を積極的に活用

## 受け入れ条件

### ブログ記事生成
- [ ] テーマ/キーワード指定で記事が生成される
- [ ] 記事タイプに応じたテンプレートが適用される
- [ ] 指定した文体ガイドに沿った記事が生成される
- [ ] 生成した記事を確認・編集できる

### WordPress投稿
- [ ] WordPress REST API経由で記事を投稿できる
- [ ] 下書き投稿と公開投稿を選択できる
- [ ] カテゴリ・タグを設定できる

### 情報収集
- [ ] Web検索で最新情報を取得できる
- [ ] 指定URLの内容を取得・要約できる
- [ ] Gemini CLI等を活用した調査レポートを生成できる

### テスト
- [ ] 単体テストが存在する
- [ ] WordPress API連携のテスト（モック）が存在する

## スコープ外

### 今回対象外
- note への投稿（WordPressの内容を手動で対応）
- Webアプリケーション化
- 複数ユーザー対応
- 画像・動画の自動生成（Phase 2以降で検討）

### 将来対応予定
- X（Twitter）投稿（画像・動画付き含む）- Phase 2
- Notion DBからの自動ネタ収集パイプライン - Phase 3
- RSSフィードからの自動ネタ収集
- 投稿スケジューリング機能
- アナリティクス連携（PV、エンゲージメント追跡）

## 技術的考慮事項

### アーキテクチャ

```
social-content-creator/
├── .claude/
│   └── skills/          # Claude Codeスキル定義
│       └── create-blog-post/
├── src/
│   ├── publishers/      # 投稿先プラットフォーム連携
│   │   └── wordpress.py
│   ├── collectors/      # 情報収集ツール群
│   │   ├── web_search.py
│   │   └── url_fetcher.py
│   ├── generators/      # 記事生成ロジック
│   │   └── blog_post.py
│   └── templates/       # 記事テンプレート
├── tests/
├── docs/
│   ├── posts/           # 生成した記事の保管
│   └── ideas/
└── pyproject.toml
```

### 依存コンポーネント

| コンポーネント | 用途 |
|--------------|------|
| WordPress REST API | ブログ記事投稿 |
| Notion MCP | 蓄積データ参照 |
| Gemini CLI | 調査レポート生成 |
| requests / httpx | HTTP通信 |
| python-wordpress-xmlrpc or REST | WordPress連携 |

### 外部サービスの現状

| サービス | 状態 |
|---------|------|
| WordPress（お名前.comサーバー） | サーバー契約済み、サイトこれから構築 |
| Notion MCP | Claude Code連携済み |
| X 開発者アカウント | Aidottersとして未作成（Phase 2で対応） |

### リスクと対策

| リスク | 影響度 | 対策 |
|-------|--------|------|
| WordPress APIの認証・権限設定 | 中 | Application Passwordsプラグイン等で対応 |
| 生成記事の品質のばらつき | 中 | テンプレートとスタイルガイドで品質を担保 |
| API制限（各プラットフォーム） | 低 | 投稿頻度が週2-3回のため影響小 |
| Notion API のレート制限 | 低 | キャッシュ・バッチ取得で対応 |

## 更新履歴

- 2026-02-13: 初版作成（ブレインストーミングセッション）
- 2026-02-13: AI×株式投資コンテンツタイプ追加、stock-analysisプロジェクトを題材としたコンテンツを追記（切り口を「AI活用ノウハウ」に修正）
- 2026-02-13: AI×データ分析・ML開発、画像認識・コンピュータビジョンのコンテンツタイプを追加
