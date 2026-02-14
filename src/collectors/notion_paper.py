"""Notion Arxiv論文 Collector。"""

from datetime import UTC, datetime, timedelta

from src.models.blog_post import CollectedData


class NotionPaperCollector:
    """スキル層から渡されたNotion MCPのArxiv論文データを変換するCollector。

    実際のNotion MCP呼び出しはClaude Codeスキル層が実行し、
    その結果をこのCollectorに渡す設計。
    """

    async def collect(self, query: str, **kwargs: object) -> list[CollectedData]:
        """Notion MCPの論文データをCollectedDataに変換する。

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
            authors = str(page.get("authors", ""))
            abstract = str(page.get("abstract", ""))
            category = str(page.get("category", ""))

            if query:
                searchable = f"{title} {abstract} {category}".lower()
                if query.lower() not in searchable:
                    continue

            content_parts = []
            if authors:
                content_parts.append(f"Authors: {authors}")
            if category:
                content_parts.append(f"Category: {category}")
            if abstract:
                content_parts.append(f"\n{abstract}")

            collected.append(
                CollectedData(
                    source="notion_paper",
                    title=title,
                    url=str(page.get("url", "")) or None,
                    content="\n".join(content_parts),
                    collected_at=datetime.now(UTC),
                )
            )
        return collected
