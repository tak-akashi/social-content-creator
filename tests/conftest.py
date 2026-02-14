"""共通テストフィクスチャ。"""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.models.blog_post import BlogPost, CollectedData, PublishResult


@pytest.fixture
def sample_blog_post() -> BlogPost:
    """テスト用のBlogPostを返す。"""
    return BlogPost(
        title="テスト記事タイトル",
        content="# テスト記事\n\nこれはテスト記事です。",
        content_type="weekly-ai-news",
        status="draft",
        slug="test-article",
        categories=["AI", "ニュース"],
        tags=["テスト"],
        created_at=datetime(2026, 2, 13, 12, 0, 0, tzinfo=UTC),
    )


@pytest.fixture
def sample_collected_data() -> CollectedData:
    """テスト用のCollectedDataを返す。"""
    return CollectedData(
        source="test_source",
        title="テスト収集データ",
        url="https://example.com/test",
        content="テスト用の収集データコンテンツです。",
        collected_at=datetime(2026, 2, 13, 12, 0, 0, tzinfo=UTC),
    )


@pytest.fixture
def sample_publish_result() -> PublishResult:
    """テスト用の成功PublishResultを返す。"""
    return PublishResult(
        success=True,
        post_id=123,
        url="https://example.com/blog/test-article",
    )


@pytest.fixture
def tmp_project_dir(tmp_path: Path) -> Path:
    """テスト用のプロジェクトディレクトリを返す。"""
    drafts = tmp_path / "docs" / "drafts" / "weekly-ai-news"
    drafts.mkdir(parents=True)
    posts = tmp_path / "docs" / "posts"
    posts.mkdir(parents=True)
    return tmp_path
