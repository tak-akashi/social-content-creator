"""URL取得Collector。"""

import re
from datetime import UTC, datetime
from urllib.parse import urlparse

import httpx

from src.errors import CollectionError
from src.models.blog_post import CollectedData


class URLFetcherCollector:
    """指定URLの内容を取得し、テキスト抽出するCollector。"""

    def __init__(self, timeout: float = 30.0) -> None:
        self._timeout = timeout

    @staticmethod
    def _validate_url(url: str) -> None:
        """URLの安全性を検証する。"""
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise CollectionError(
                source="url_fetcher",
                message=f"サポートされていないスキーム: {parsed.scheme}",
            )
        if parsed.hostname in ("localhost", "127.0.0.1", "::1"):
            raise CollectionError(
                source="url_fetcher",
                message="ローカルホストへのアクセスは禁止されています",
            )

    async def collect(self, query: str, **kwargs: object) -> list[CollectedData]:
        """URLからコンテンツを取得する。

        Args:
            query: 取得対象のURL
            **kwargs: 未使用

        Returns:
            取得結果のリスト（1件）

        Raises:
            CollectionError: 取得に失敗した場合
        """
        url = query
        self._validate_url(url)
        try:
            async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
        except httpx.HTTPError as e:
            raise CollectionError(source="url_fetcher", message=str(e)) from e

        content_type = response.headers.get("content-type", "")
        if "html" in content_type:
            text = self._extract_text_from_html(response.text)
        else:
            text = response.text

        title = self._extract_title(response.text) if "html" in content_type else url

        return [
            CollectedData(
                source="url_fetcher",
                title=title,
                url=url,
                content=text,
                collected_at=datetime.now(UTC),
            )
        ]

    @staticmethod
    def _extract_text_from_html(html: str) -> str:
        """HTMLからテキストを抽出する。"""
        # scriptとstyleタグを除去
        cleaned = re.sub(r"<(script|style)[^>]*>[\s\S]*?</\1>", "", html, flags=re.IGNORECASE)
        # HTMLタグを除去
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        # 連続する空白を整理
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()

    @staticmethod
    def _extract_title(html: str) -> str:
        """HTMLからtitleタグの内容を抽出する。"""
        match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return "Untitled"
