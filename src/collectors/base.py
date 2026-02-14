"""Collector共通インターフェース。"""

from typing import Protocol

from src.models.blog_post import CollectedData


class CollectorProtocol(Protocol):  # pragma: no cover
    """情報収集の共通プロトコル。"""

    async def collect(self, query: str, **kwargs: object) -> list[CollectedData]:
        """指定クエリで情報を収集する。

        Args:
            query: 検索クエリまたはキーワード
            **kwargs: Collector固有のパラメータ

        Returns:
            収集結果のリスト
        """
        ...
