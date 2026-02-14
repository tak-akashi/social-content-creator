"""WebSearchCollectorのテスト。"""

from src.collectors.web_search import WebSearchCollector


class TestWebSearchCollector:
    """WebSearchCollectorのテスト。"""

    async def test_collect_from_results(self) -> None:
        """検索結果をCollectedDataに変換できる。"""
        results = [
            {"title": "Result 1", "url": "https://example.com/1", "content": "Content 1"},
            {"title": "Result 2", "url": "https://example.com/2", "content": "Content 2"},
        ]

        collector = WebSearchCollector()
        collected = await collector.collect("AI news", results=results)

        assert len(collected) == 2
        assert collected[0].title == "Result 1"
        assert collected[0].source == "web_search"
        assert collected[1].url == "https://example.com/2"

    async def test_collect_empty_results(self) -> None:
        """空の結果で空リストが返る。"""
        collector = WebSearchCollector()
        collected = await collector.collect("query", results=[])
        assert collected == []

    async def test_collect_no_results_kwarg(self) -> None:
        """resultsが渡されない場合は空リストが返る。"""
        collector = WebSearchCollector()
        collected = await collector.collect("query")
        assert collected == []

    async def test_collect_invalid_results(self) -> None:
        """不正なresultsでも空リストが返る。"""
        collector = WebSearchCollector()
        collected = await collector.collect("query", results="not a list")
        assert collected == []

    async def test_collect_skips_invalid_items(self) -> None:
        """不正な項目はスキップされる。"""
        results = [
            {"title": "Valid", "url": "https://example.com", "content": "OK"},
            "invalid item",
        ]

        collector = WebSearchCollector()
        collected = await collector.collect("query", results=results)

        assert len(collected) == 1
        assert collected[0].title == "Valid"
