"""NotionPaperCollectorのテスト。"""

from datetime import UTC, datetime, timedelta

from src.collectors.notion_paper import NotionPaperCollector


class TestNotionPaperCollector:
    """NotionPaperCollectorのテスト。"""

    async def test_collect_recent_papers(self) -> None:
        """最近の論文が取得できる。"""
        now = datetime.now(UTC)
        pages = [
            {
                "title": "Attention Is All You Need",
                "url": "https://arxiv.org/abs/1706.03762",
                "authors": "Vaswani et al.",
                "abstract": "Transformer architecture",
                "category": "cs.CL",
                "saved_at": now.isoformat(),
            },
        ]

        collector = NotionPaperCollector()
        results = await collector.collect("", pages=pages)

        assert len(results) == 1
        assert results[0].title == "Attention Is All You Need"
        assert "Vaswani et al." in results[0].content
        assert "cs.CL" in results[0].content

    async def test_filter_by_keyword(self) -> None:
        """キーワードでフィルタリングできる。"""
        now = datetime.now(UTC)
        pages = [
            {
                "title": "Vision Transformer",
                "abstract": "Image classification with transformers",
                "category": "cs.CV",
                "saved_at": now.isoformat(),
            },
            {
                "title": "BERT Fine-tuning",
                "abstract": "NLP with BERT",
                "category": "cs.CL",
                "saved_at": now.isoformat(),
            },
        ]

        collector = NotionPaperCollector()
        results = await collector.collect("Vision", pages=pages)

        assert len(results) == 1
        assert results[0].title == "Vision Transformer"

    async def test_filter_old_papers(self) -> None:
        """古い論文がフィルタリングされる。"""
        now = datetime.now(UTC)
        old = now - timedelta(days=10)
        pages = [
            {"title": "New", "abstract": "New paper", "saved_at": now.isoformat()},
            {"title": "Old", "abstract": "Old paper", "saved_at": old.isoformat()},
        ]

        collector = NotionPaperCollector()
        results = await collector.collect("", pages=pages, days=7)

        assert len(results) == 1
        assert results[0].title == "New"

    async def test_empty_pages(self) -> None:
        """空リストで空が返る。"""
        collector = NotionPaperCollector()
        results = await collector.collect("", pages=[])
        assert results == []
