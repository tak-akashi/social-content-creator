"""Web検索結果Collector。"""

from datetime import UTC, datetime

from src.models.blog_post import CollectedData


class WebSearchCollector:
    """スキル層から渡された検索結果データをCollectedDataに変換するCollector。

    実際のWeb検索はClaude CodeのWebSearchツールがスキル層で実行し、
    その結果をこのCollectorに渡す設計。
    """

    async def collect(self, query: str, **kwargs: object) -> list[CollectedData]:
        """検索結果データをCollectedDataに変換する。

        Args:
            query: 検索クエリ（メタデータ用）
            **kwargs:
                results: 検索結果のリスト（dict形式）
                    各dictは title, url, content キーを含む

        Returns:
            変換されたCollectedDataのリスト
        """
        results = kwargs.get("results", [])
        if not isinstance(results, list):
            return []

        collected: list[CollectedData] = []
        now = datetime.now(UTC)
        for item in results:
            if not isinstance(item, dict):
                continue
            collected.append(
                CollectedData(
                    source="web_search",
                    title=str(item.get("title", "Untitled")),
                    url=str(item.get("url", "")),
                    content=str(item.get("content", "")),
                    collected_at=now,
                )
            )
        return collected
