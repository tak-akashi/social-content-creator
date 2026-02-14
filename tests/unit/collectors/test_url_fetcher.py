"""URLFetcherCollectorのテスト。"""

import httpx
import pytest

from src.collectors.url_fetcher import URLFetcherCollector
from src.errors import CollectionError


class TestURLFetcherCollector:
    """URLFetcherCollectorのテスト。"""

    @pytest.fixture
    def collector(self) -> URLFetcherCollector:
        return URLFetcherCollector()

    async def test_collect_html_page(self, respx_mock: object) -> None:
        """HTMLページからテキストを取得できる。"""
        import respx as respx_lib

        mock = respx_lib.get("https://example.com/article").mock(
            return_value=httpx.Response(
                200,
                text="<html><head><title>Test Page</title></head>"
                "<body><p>Hello World</p></body></html>",
                headers={"content-type": "text/html"},
            )
        )

        collector = URLFetcherCollector()
        results = await collector.collect("https://example.com/article")

        assert len(results) == 1
        assert results[0].source == "url_fetcher"
        assert results[0].title == "Test Page"
        assert "Hello World" in results[0].content
        assert results[0].url == "https://example.com/article"
        assert mock.called

    async def test_collect_plain_text(self, respx_mock: object) -> None:
        """プレーンテキストを取得できる。"""
        import respx as respx_lib

        respx_lib.get("https://example.com/data.txt").mock(
            return_value=httpx.Response(
                200,
                text="Plain text content",
                headers={"content-type": "text/plain"},
            )
        )

        collector = URLFetcherCollector()
        results = await collector.collect("https://example.com/data.txt")

        assert len(results) == 1
        assert results[0].content == "Plain text content"

    async def test_collect_http_error_raises_collection_error(self, respx_mock: object) -> None:
        """HTTPエラー時にCollectionErrorが発生する。"""
        import respx as respx_lib

        respx_lib.get("https://example.com/404").mock(return_value=httpx.Response(404))

        collector = URLFetcherCollector()
        with pytest.raises(CollectionError):
            await collector.collect("https://example.com/404")

    def test_extract_text_from_html(self) -> None:
        """HTMLからテキストを正しく抽出できる。"""
        html = (
            "<html><head><script>var x=1;</script></head>"
            "<body><h1>Title</h1><p>Content</p></body></html>"
        )
        text = URLFetcherCollector._extract_text_from_html(html)
        assert "Title" in text
        assert "Content" in text
        assert "var x=1" not in text

    def test_extract_title(self) -> None:
        """HTMLからタイトルを正しく抽出できる。"""
        html = "<html><head><title>My Title</title></head></html>"
        title = URLFetcherCollector._extract_title(html)
        assert title == "My Title"

    def test_extract_title_missing(self) -> None:
        """タイトルがないHTMLではUntitledを返す。"""
        html = "<html><body>No title</body></html>"
        title = URLFetcherCollector._extract_title(html)
        assert title == "Untitled"
