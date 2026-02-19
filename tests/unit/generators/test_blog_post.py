"""BlogPostGeneratorのテスト。"""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.generators.blog_post import BlogPostGenerator
from src.models.blog_post import BlogPost, CollectedData


class TestBlogPostGenerator:
    """BlogPostGeneratorのテスト。"""

    @pytest.fixture
    def generator(self, tmp_project_dir: Path) -> BlogPostGenerator:
        return BlogPostGenerator(base_dir=tmp_project_dir)

    class TestGetTemplate:
        """get_templateのテスト。"""

        def test_returns_template(self, tmp_project_dir: Path) -> None:
            """テンプレートを取得できる。"""
            gen = BlogPostGenerator(base_dir=tmp_project_dir)
            template = gen.get_template("weekly-ai-news")
            assert template.content_type == "weekly-ai-news"

    class TestBuildPromptContext:
        """build_prompt_contextのテスト。"""

        def test_includes_template_info(self, tmp_project_dir: Path) -> None:
            """テンプレート情報がコンテキストに含まれる。"""
            gen = BlogPostGenerator(base_dir=tmp_project_dir)
            template = gen.get_template("weekly-ai-news")
            context = gen.build_prompt_context(template, topic="AI最新ニュース")
            assert "週刊AIニュースハイライト" in context
            assert "AI最新ニュース" in context
            assert "3000" in context

        def test_includes_collected_data(self, tmp_project_dir: Path) -> None:
            """収集データがコンテキストに含まれる。"""
            gen = BlogPostGenerator(base_dir=tmp_project_dir)
            template = gen.get_template("weekly-ai-news")
            data = [
                CollectedData(
                    source="test",
                    title="テストデータ",
                    content="テストコンテンツ",
                    collected_at=datetime.now(UTC),
                )
            ]
            context = gen.build_prompt_context(template, collected_data=data)
            assert "テストデータ" in context
            assert "テストコンテンツ" in context

    class TestGenerate:
        """generateのテスト。"""

        async def test_generates_blog_post(self, tmp_project_dir: Path) -> None:
            """BlogPostオブジェクトが生成される。"""
            gen = BlogPostGenerator(base_dir=tmp_project_dir)
            post = await gen.generate(
                content_type="weekly-ai-news",
                title="テスト記事",
                content="# テスト\nコンテンツ",
            )
            assert post.title == "テスト記事"
            assert post.content_type == "weekly-ai-news"
            assert post.status == "draft"
            assert post.slug

        async def test_generates_blog_post_with_subtitle(self, tmp_project_dir: Path) -> None:
            """subtitle付きBlogPostオブジェクトが生成される。"""
            gen = BlogPostGenerator(base_dir=tmp_project_dir)
            post = await gen.generate(
                content_type="weekly-ai-news",
                title="テスト記事",
                content="# テスト\nコンテンツ",
                subtitle="サブタイトル補足",
            )
            assert post.subtitle == "サブタイトル補足"

    class TestSaveDraft:
        """save_draftのテスト。"""

        async def test_saves_as_markdown_with_frontmatter(self, tmp_project_dir: Path) -> None:
            """front matter付きMarkdownとして保存される。"""
            gen = BlogPostGenerator(base_dir=tmp_project_dir)
            post = BlogPost(
                title="保存テスト",
                content="# テスト\nコンテンツ",
                content_type="weekly-ai-news",
                slug="save-test",
                created_at=datetime(2026, 2, 13, 12, 0, 0, tzinfo=UTC),
            )
            path = await gen.save_draft(post)

            assert path.exists()
            content = path.read_text()
            assert "title: 保存テスト" in content
            assert "type: weekly-ai-news" in content
            assert "# テスト" in content

        async def test_saves_subtitle_in_frontmatter(self, tmp_project_dir: Path) -> None:
            """subtitle付きBlogPostを保存するとfrontmatterにsubtitleが含まれる。"""
            gen = BlogPostGenerator(base_dir=tmp_project_dir)
            post = BlogPost(
                title="サブタイトル保存テスト",
                subtitle="補足情報",
                content="# テスト\nコンテンツ",
                content_type="weekly-ai-news",
                slug="subtitle-save-test",
                created_at=datetime(2026, 2, 13, 12, 0, 0, tzinfo=UTC),
            )
            path = await gen.save_draft(post)
            content = path.read_text()
            assert "subtitle: 補足情報" in content

        async def test_saves_without_subtitle_key(self, tmp_project_dir: Path) -> None:
            """subtitleなしBlogPostを保存するとfrontmatterにsubtitleキーが含まれない。"""
            gen = BlogPostGenerator(base_dir=tmp_project_dir)
            post = BlogPost(
                title="保存テスト",
                content="# テスト\nコンテンツ",
                content_type="weekly-ai-news",
                slug="save-no-sub-test",
                created_at=datetime(2026, 2, 13, 12, 0, 0, tzinfo=UTC),
            )
            path = await gen.save_draft(post)
            content = path.read_text()
            assert "subtitle:" not in content

    class TestLoadDraft:
        """load_draftのテスト。"""

        async def test_loads_saved_draft(self, tmp_project_dir: Path) -> None:
            """保存したドラフトを読み込める。"""
            gen = BlogPostGenerator(base_dir=tmp_project_dir)
            post = BlogPost(
                title="読み込みテスト",
                content="# テスト\nコンテンツ",
                content_type="weekly-ai-news",
                slug="load-test",
                created_at=datetime(2026, 2, 13, 12, 0, 0, tzinfo=UTC),
            )
            path = await gen.save_draft(post)
            loaded = await gen.load_draft(path)

            assert loaded.title == "読み込みテスト"
            assert loaded.content_type == "weekly-ai-news"
            assert "テスト" in loaded.content

        async def test_loads_draft_with_subtitle(self, tmp_project_dir: Path) -> None:
            """subtitle付きドラフトを読み込むとsubtitleが復元される。"""
            gen = BlogPostGenerator(base_dir=tmp_project_dir)
            post = BlogPost(
                title="サブタイトル復元テスト",
                subtitle="復元される補足情報",
                content="# テスト\nコンテンツ",
                content_type="weekly-ai-news",
                slug="subtitle-load-test",
                created_at=datetime(2026, 2, 13, 12, 0, 0, tzinfo=UTC),
            )
            path = await gen.save_draft(post)
            loaded = await gen.load_draft(path)
            assert loaded.subtitle == "復元される補足情報"

        async def test_loads_draft_without_subtitle(self, tmp_project_dir: Path) -> None:
            """subtitleなしドラフトを読み込むとsubtitleがNoneになる。"""
            gen = BlogPostGenerator(base_dir=tmp_project_dir)
            post = BlogPost(
                title="サブタイトルなし復元テスト",
                content="# テスト\nコンテンツ",
                content_type="weekly-ai-news",
                slug="no-subtitle-load-test",
                created_at=datetime(2026, 2, 13, 12, 0, 0, tzinfo=UTC),
            )
            path = await gen.save_draft(post)
            loaded = await gen.load_draft(path)
            assert loaded.subtitle is None

    class TestMoveToPublished:
        """move_to_publishedのテスト。"""

        async def test_moves_draft_to_posts(self, tmp_project_dir: Path) -> None:
            """ドラフトがpostsディレクトリに移動される。"""
            gen = BlogPostGenerator(base_dir=tmp_project_dir)
            post = BlogPost(
                title="移動テスト",
                content="# テスト",
                content_type="weekly-ai-news",
                slug="move-test",
                created_at=datetime(2026, 2, 13, 12, 0, 0, tzinfo=UTC),
            )
            draft_path = await gen.save_draft(post)
            assert draft_path.exists()

            dest_path = await gen.move_to_published(post, draft_path)

            assert dest_path.exists()
            assert not draft_path.exists()
            assert "posts" in str(dest_path)
