"""Notion Google Alertニュース Collector。"""

from datetime import UTC, datetime, timedelta

from src.models.blog_post import CollectedData


class NotionNewsCollector:
    """スキル層から渡されたNotion MCPのGoogle Alertデータを変換するCollector。

    実際のNotion MCP呼び出しはClaude Codeスキル層が実行し、
    その結果をこのCollectorに渡す設計。
    """

    async def collect(self, query: str, **kwargs: object) -> list[CollectedData]:
        """Notion MCPのニュースデータをCollectedDataに変換する。

        Args:
            query: フィルタキーワード（空文字で全件）
            **kwargs:
                pages: Notion MCPから取得したページデータのリスト
                days: 過去何日間のデータを対象にするか（デフォルト: 7）

        Returns:
            変換されたCollectedDataのリスト
        """
        pages = kwargs.get("pages", [])
        if not isinstance(pages, list):
            return []

        days_val = kwargs.get("days", 7)
        days = int(days_val) if isinstance(days_val, (int, str)) else 7
        cutoff = datetime.now(UTC) - timedelta(days=days)

        collected: list[CollectedData] = []
        for page in pages:
            if not isinstance(page, dict):
                continue

            saved_at_str = str(page.get("saved_at", ""))
            if saved_at_str:
                try:
                    saved_at = datetime.fromisoformat(saved_at_str)
                    if saved_at.tzinfo is None:
                        saved_at = saved_at.replace(tzinfo=UTC)
                    if saved_at < cutoff:
                        continue
                except ValueError:
                    pass

            title = str(page.get("title", "Untitled"))
            if query and query.lower() not in title.lower():
                content_text = str(page.get("summary", ""))
                if query.lower() not in content_text.lower():
                    continue

            collected.append(
                CollectedData(
                    source="notion_news",
                    title=title,
                    url=str(page.get("url", "")) or None,
                    content=str(page.get("summary", "")),
                    collected_at=datetime.now(UTC),
                )
            )
        return collected
