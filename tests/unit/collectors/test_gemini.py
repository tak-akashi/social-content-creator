"""GeminiCollectorのテスト。"""

from unittest.mock import AsyncMock, patch

import pytest

from src.collectors.gemini import GeminiCollector
from src.errors import CollectionError


class TestGeminiCollector:
    """GeminiCollectorのテスト。"""

    async def test_collect_success(self) -> None:
        """Gemini CLIの実行に成功する。"""
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(b"Research result content", b""))
        mock_process.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            collector = GeminiCollector()
            results = await collector.collect("AI trends 2026")

        assert len(results) == 1
        assert results[0].source == "gemini"
        assert results[0].content == "Research result content"
        assert "AI trends 2026" in results[0].title

    async def test_collect_cli_not_found(self) -> None:
        """CLIが見つからない場合にCollectionErrorが発生する。"""
        with patch(
            "asyncio.create_subprocess_exec",
            side_effect=FileNotFoundError("gemini not found"),
        ):
            collector = GeminiCollector()
            with pytest.raises(CollectionError, match="gemini CLI"):
                await collector.collect("test query")

    async def test_collect_cli_error(self) -> None:
        """CLI実行エラー時にCollectionErrorが発生する。"""
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(b"", b"Error message"))
        mock_process.returncode = 1

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            collector = GeminiCollector()
            with pytest.raises(CollectionError, match="実行エラー"):
                await collector.collect("test query")
