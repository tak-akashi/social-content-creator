"""記事生成→保存の統合テスト。"""

from pathlib import Path

from src.generators.blog_post import BlogPostGenerator


class TestGenerateAndSave:
    """記事生成→ドラフト保存→読み込みの統合テスト。"""

    async def test_full_lifecycle(self, tmp_project_dir: Path) -> None:
        """記事の生成→保存→読み込みが一貫して動作する。"""
        gen = BlogPostGenerator(base_dir=tmp_project_dir)

        # 記事生成
        post = await gen.generate(
            content_type="tool-tips",
            title="pytest tips for beginners",
            content=(
                "# pytest Tips\n\npytestの便利な使い方を紹介します。"
                "\n\n## フィクスチャ\n\nフィクスチャは便利です。"
            ),
            topic="pytest tips",
        )
        assert post.title == "pytest tips for beginners"
        assert post.slug == "pytest-tips-for-beginners"

        # ドラフト保存
        draft_path = await gen.save_draft(post)
        assert draft_path.exists()
        assert "tool-tips" in str(draft_path)

        # 読み込み
        loaded = await gen.load_draft(draft_path)
        assert loaded.title == post.title
        assert loaded.content_type == "tool-tips"
        assert "pytest" in loaded.content

        # 投稿済みへ移動
        post_path = await gen.move_to_published(loaded, draft_path)
        assert post_path.exists()
        assert not draft_path.exists()
        assert "posts" in str(post_path)

    async def test_full_lifecycle_with_subtitle(self, tmp_project_dir: Path) -> None:
        """subtitle付き記事の生成→保存→読み込みが一貫して動作する。"""
        gen = BlogPostGenerator(base_dir=tmp_project_dir)

        # 記事生成
        post = await gen.generate(
            content_type="tool-tips",
            title="pytest tips",
            content="# pytest Tips\n\npytestの便利な使い方。",
            subtitle="初心者向けテスト入門ガイド",
            topic="pytest tips",
        )
        assert post.subtitle == "初心者向けテスト入門ガイド"

        # ドラフト保存
        draft_path = await gen.save_draft(post)
        assert draft_path.exists()
        content = draft_path.read_text()
        assert "subtitle:" in content

        # 読み込み
        loaded = await gen.load_draft(draft_path)
        assert loaded.subtitle == "初心者向けテスト入門ガイド"
        assert loaded.title == "pytest tips"

    async def test_generate_with_japanese_title(self, tmp_project_dir: Path) -> None:
        """日本語タイトルの記事が正しく保存される。"""
        gen = BlogPostGenerator(base_dir=tmp_project_dir)

        post = await gen.generate(
            content_type="weekly-ai-news",
            title="AI最新ニュース2026年2月号",
            content="# AI最新ニュース\n\n今週のハイライト",
        )
        # 日本語が除去され、英数字部分のみスラッグになる
        assert "ai" in post.slug or post.slug == "2026-2"

        draft_path = await gen.save_draft(post)
        assert draft_path.exists()

        loaded = await gen.load_draft(draft_path)
        assert loaded.title == "AI最新ニュース2026年2月号"
