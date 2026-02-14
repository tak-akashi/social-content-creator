"""Gemini CLI Collector。"""

import asyncio
from datetime import UTC, datetime

from src.errors import CollectionError
from src.models.blog_post import CollectedData


class GeminiCollector:
    """Gemini CLIをサブプロセスで実行し、調査レポートを取得するCollector。"""

    def __init__(self, timeout: float = 120.0) -> None:
        self._timeout = timeout

    async def collect(self, query: str, **kwargs: object) -> list[CollectedData]:
        """Gemini CLIで調査を実行する。

        Args:
            query: 調査クエリ
            **kwargs: 未使用

        Returns:
            調査結果のリスト

        Raises:
            CollectionError: CLI実行に失敗した場合
        """
        try:
            process = await asyncio.create_subprocess_exec(
                "gemini",
                "-p",
                query,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self._timeout)
        except FileNotFoundError as e:
            raise CollectionError(source="gemini", message="gemini CLIが見つかりません") from e
        except TimeoutError as e:
            raise CollectionError(
                source="gemini", message=f"タイムアウト ({self._timeout}秒)"
            ) from e

        if process.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace").strip()
            raise CollectionError(source="gemini", message=f"実行エラー: {error_msg}")

        content = stdout.decode("utf-8", errors="replace").strip()
        return [
            CollectedData(
                source="gemini",
                title=f"Gemini調査: {query[:80]}",
                content=content,
                collected_at=datetime.now(UTC),
            )
        ]
