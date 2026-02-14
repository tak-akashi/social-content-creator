"""NotionNewsCollectorのテスト。"""

from datetime import UTC, datetime, timedelta

from src.collectors.notion_news import NotionNewsCollector


class TestNotionNewsCollector:
    """NotionNewsCollectorのテスト。"""

    async def test_collect_recent_news(self) -> None:
        """最近のニュースが取得できる。"""
        now = datetime.now(UTC)
        pages = [
            {
                "title": "AIニュース1",
                "url": "https://example.com/news1",
                "summary": "最新のAI動向",
                "saved_at": now.isoformat(),
            },
            {
                "title": "AIニュース2",
                "url": "https://example.com/news2",
                "summary": "新しいモデルの発表",
                "saved_at": now.isoformat(),
            },
        ]

        collector = NotionNewsCollector()
        results = await collector.collect("", pages=pages)

        assert len(results) == 2
        assert results[0].title == "AIニュース1"
        assert results[0].source == "notion_news"

    async def test_filter_old_news(self) -> None:
        """古いニュースがフィルタリングされる。"""
        now = datetime.now(UTC)
        old = now - timedelta(days=10)
        pages = [
            {"title": "最新", "summary": "新しい", "saved_at": now.isoformat()},
            {"title": "古い", "summary": "古い", "saved_at": old.isoformat()},
        ]

        collector = NotionNewsCollector()
        results = await collector.collect("", pages=pages, days=7)

        assert len(results) == 1
        assert results[0].title == "最新"

    async def test_filter_by_keyword(self) -> None:
        """キーワードでフィルタリングできる。"""
        now = datetime.now(UTC)
        pages = [
            {"title": "LLMの進化", "summary": "大規模言語モデル", "saved_at": now.isoformat()},
            {"title": "ロボット工学", "summary": "自律走行", "saved_at": now.isoformat()},
        ]

        collector = NotionNewsCollector()
        results = await collector.collect("LLM", pages=pages)

        assert len(results) == 1
        assert results[0].title == "LLMの進化"

    async def test_empty_pages_returns_empty(self) -> None:
        """空のページリストで空リストが返る。"""
        collector = NotionNewsCollector()
        results = await collector.collect("", pages=[])
        assert results == []

    async def test_invalid_pages_returns_empty(self) -> None:
        """不正なpagesでも空リストが返る。"""
        collector = NotionNewsCollector()
        results = await collector.collect("", pages="not a list")
        assert results == []
