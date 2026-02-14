> **ステータス: 計画段階**
> このドキュメントは `docs/ideas/20260213-social-content-creator.md` から生成されました。
> 実装後は `/update-docs` で実態に同期してください。

# 開発ガイドライン (Development Guidelines)

## コーディング規約

### 命名規則

#### 変数・関数

**Python**:
```python
# 良い例
blog_post_content = generate_blog_post(topic="AI最新ニュース")
collected_data = await fetch_url_content(url)

def create_weekly_summary(news_items: list[CollectedData]) -> BlogPost: ...
def publish_to_wordpress(post: BlogPost, status: str = "draft") -> PublishResult: ...

# 悪い例
data = gen(t="AI最新ニュース")
def do_stuff(items: list) -> dict: ...
```

**原則**:
- 変数: snake_case、名詞または名詞句
- 関数: snake_case、動詞で始める
- 定数: UPPER_SNAKE_CASE（例: `DEFAULT_WORD_COUNT`, `MAX_RETRY_COUNT`）
- Boolean: `is_`, `has_`, `should_` で始める（例: `is_published`, `has_categories`）

#### クラス・型

```python
from typing import Protocol, Literal
from dataclasses import dataclass

# クラス: PascalCase、名詞
class BlogPostGenerator: ...
class WordPressPublisher: ...
class WebSearchCollector: ...

# Protocol: PascalCase
class CollectorProtocol(Protocol):
    async def collect(self, query: str, **kwargs) -> list[CollectedData]: ...

class PublisherProtocol(Protocol):
    async def publish(self, post: BlogPost, **kwargs) -> PublishResult: ...

# 型エイリアス: PascalCase (Python 3.12+)
type ContentType = Literal[
    "weekly-ai-news", "paper-review", "project-intro",
    "tool-tips", "market-analysis", "ml-practice", "cv", "feature",
]
type PostStatus = Literal["draft", "review", "ready", "published"]
```

### コードフォーマット

**インデント**: 4スペース（PEP 8準拠）

**行の長さ**: 最大100文字

**例**:
```python
# リスト内包表記
valid_posts = [
    post
    for post in collected_posts
    if post.word_count >= MIN_WORD_COUNT
]

# 長い関数呼び出し
result = await wordpress_client.create_post(
    title=post.title,
    content=post.content,
    status="draft",
    categories=post.categories,
    tags=post.tags,
)
```

### コメント規約

**関数・クラスのドキュメント (Google Style Docstring)**:
```python
async def generate_blog_post(
    content_type: ContentType,
    topic: str | None = None,
    source_url: str | None = None,
) -> BlogPost:
    """ブログ記事のドラフトを生成する。

    指定されたコンテンツタイプとトピックに基づいて、テンプレートを適用し
    情報収集結果を統合して記事ドラフトを生成する。

    Args:
        content_type: コンテンツタイプ（weekly-ai-news, paper-review等）
        topic: トピック・キーワード（オプション）
        source_url: 参照URL（オプション）

    Returns:
        生成されたブログ記事のドラフト

    Raises:
        TemplateNotFoundError: 指定タイプのテンプレートが存在しない場合
        CollectionError: 情報収集に失敗した場合
    """
```

**インラインコメント**:
```python
# 良い例: なぜそうするかを説明
# WordPress APIは下書き投稿のURLを返さないため、投稿IDからURL を構築
post_url = f"{base_url}/?p={post_id}"

# 悪い例: 何をしているか（コードを見れば分かる）
# URLを構築する
post_url = f"{base_url}/?p={post_id}"
```

### エラーハンドリング

**原則**:
- 予期されるエラー: 適切な例外クラスを定義
- 予期しないエラー: 上位に伝播
- エラーを無視しない

**例**:
```python
from dataclasses import dataclass

# 例外クラス定義
@dataclass
class WordPressPublishError(Exception):
    """WordPress投稿エラー"""
    message: str
    status_code: int | None = None

    def __str__(self) -> str:
        if self.status_code:
            return f"{self.message} (HTTP {self.status_code})"
        return self.message

@dataclass
class CollectionError(Exception):
    """情報収集エラー"""
    source: str
    message: str

    def __str__(self) -> str:
        return f"[{self.source}] {self.message}"

# エラーハンドリング
try:
    result = await publisher.publish(post, status="draft")
except WordPressPublishError as e:
    # ローカルに保存してユーザーに通知
    await save_draft_locally(post)
    print(f"WordPress投稿エラー: {e}")
    print("ローカルにドラフトを保存しました")
except Exception as e:
    print(f"予期しないエラー: {e}")
    raise
```

## Git運用ルール

### ブランチ戦略

**ブランチ種別**:
- `main`: 安定版（リリース可能な状態）
- `develop`: 開発の最新状態
- `feature/[機能名]`: 新機能開発
- `fix/[修正内容]`: バグ修正
- `refactor/[対象]`: リファクタリング

**フロー**:
```
main
  └─ develop
      ├─ feature/blog-post-generator
      ├─ feature/wordpress-publisher
      ├─ feature/web-search-collector
      └─ fix/template-loading
```

### コミットメッセージ規約

**フォーマット**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type**:
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `style`: コードフォーマット
- `refactor`: リファクタリング
- `test`: テスト追加・修正
- `chore`: ビルド、補助ツール等

**Scope（本プロジェクト固有）**:
- `generator`: 記事生成エンジン
- `collector`: 情報収集ツール
- `publisher`: 投稿先連携
- `template`: テンプレート
- `model`: データモデル
- `skill`: Claude Codeスキル

**例**:
```
feat(generator): ブログ記事生成エンジンを実装

テンプレートに基づいてブログ記事のドラフトを生成する機能を追加。
- BlogPostGenerator クラスを実装
- コンテンツタイプ別テンプレート選択
- 情報収集結果の統合ロジック

Closes #1
```

### プルリクエストプロセス

**作成前のチェック**:
- [ ] 全てのテストがパス (`pytest`)
- [ ] Ruffエラーがない (`ruff check .`)
- [ ] mypyエラーがない (`mypy .`)
- [ ] Blackでフォーマット済み (`black .`)

## テスト戦略

### テストの種類

#### ユニットテスト

**対象**: 個別の関数・クラス

**カバレッジ目標**: 80%

**例 (pytest)**:
```python
import pytest
from unittest.mock import AsyncMock, MagicMock

class TestBlogPostGenerator:
    """BlogPostGenerator のテスト"""

    class TestGenerate:
        """generate メソッドのテスト"""

        async def test_with_valid_type_generates_post(
            self,
            generator: BlogPostGenerator,
            mock_collector: MagicMock,
        ) -> None:
            """有効なコンテンツタイプで記事を生成できる"""
            post = await generator.generate(
                content_type="weekly-ai-news",
                topic="AI最新ニュース",
            )

            assert post.title is not None
            assert post.content_type == "weekly-ai-news"
            assert post.word_count > 0

        async def test_with_invalid_type_raises_error(
            self,
            generator: BlogPostGenerator,
        ) -> None:
            """無効なコンテンツタイプでエラーをスローする"""
            with pytest.raises(TemplateNotFoundError):
                await generator.generate(content_type="invalid-type")
```

#### 統合テスト

**対象**: 複数コンポーネントの連携

**例**:
```python
class TestGenerateAndSave:
    """記事生成→保存の統合テスト"""

    async def test_generate_and_save_locally(
        self,
        generator: BlogPostGenerator,
        tmp_path: Path,
    ) -> None:
        """記事を生成してローカルに保存できる"""
        post = await generator.generate(
            content_type="tool-tips",
            topic="pytest tips",
        )

        save_path = tmp_path / "post.md"
        await save_post(post, save_path)

        assert save_path.exists()
        content = save_path.read_text()
        assert "pytest tips" in content
```

### テスト命名規則

**パターン**: `test_[対象]_[条件]_[期待結果]` または日本語docstring

**例**:
```python
# 良い例
async def test_publish_with_valid_post_returns_url(self) -> None:
    """有効な記事でURLが返される"""
    ...

async def test_collect_with_timeout_raises_collection_error(self) -> None:
    """タイムアウト時にCollectionErrorをスローする"""
    ...

# 悪い例
async def test_1(self) -> None: ...
async def test_works(self) -> None: ...
```

### モック・スタブの使用

**原則**:
- 外部依存（WordPress API、Web検索、GitHub API）はモック化
- ビジネスロジック（記事生成、テンプレート適用）は実装を使用

**例**:
```python
from unittest.mock import MagicMock, AsyncMock
import pytest

@pytest.fixture
def mock_wordpress_client() -> MagicMock:
    """WordPress APIクライアントをモック化"""
    client = MagicMock()
    client.create_post = AsyncMock(return_value={
        "id": 1,
        "link": "https://example.com/blog/test-post",
    })
    client.get_categories = AsyncMock(return_value=[])
    client.get_tags = AsyncMock(return_value=[])
    return client

@pytest.fixture
def publisher(mock_wordpress_client: MagicMock) -> WordPressPublisher:
    """Publisherは実際の実装を使用"""
    return WordPressPublisher(client=mock_wordpress_client)
```

## コードレビュー基準

### レビューポイント

**機能性**:
- [ ] 要件（PRD・機能設計書）を満たしているか
- [ ] エッジケース（空文字列、None、API失敗等）が考慮されているか
- [ ] エラーハンドリングが適切か

**可読性**:
- [ ] 命名が明確か
- [ ] Docstringが適切か（公開関数・クラスに必須）
- [ ] 複雑なロジックにコメントがあるか

**保守性**:
- [ ] 重複コードがないか
- [ ] 責務が明確に分離されているか（Generator/Collector/Publisher）
- [ ] Protocol に依存しているか（具象クラスへの直接依存を避ける）

**セキュリティ**:
- [ ] 認証情報がハードコードされていないか
- [ ] 入力検証が適切か
- [ ] APIキーがログに出力されていないか

## 開発環境セットアップ

### 必要なツール

| ツール | バージョン | インストール方法 |
|--------|-----------|-----------------|
| Python | 3.12+ | pyenv または公式インストーラー |
| uv | 最新 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Claude Code | 最新 | `npm install -g @anthropic/claude-code` |

### セットアップ手順

```bash
# 1. リポジトリのクローン
git clone <repository-url>
cd social-content-creator

# 2. Python環境のセットアップ
uv sync

# 3. 開発用依存関係のインストール
uv sync --dev

# 4. 環境変数の設定
cp .env.example .env
# .env ファイルを編集（WordPress認証情報等）

# 5. テストの実行
pytest

# 6. Lint・フォーマットの確認
ruff check .
black --check .
mypy .
```

### 環境変数（.env）

```bash
# WordPress設定
WORDPRESS_URL=https://your-site.com
WORDPRESS_USER=your-username
WORDPRESS_APP_PASSWORD=your-app-password

# Gemini CLI（オプション）
# Gemini CLIは別途インストール・認証が必要

# GitHub（オプション）
GITHUB_TOKEN=your-github-token
```
