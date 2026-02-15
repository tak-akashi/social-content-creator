"""GitHub情報収集Collector。"""

import logging
import os
from datetime import UTC, datetime

import httpx
from dotenv import load_dotenv

from src.errors import CollectionError
from src.models.blog_post import CollectedData

logger = logging.getLogger(__name__)


class GitHubCollector:
    """GitHub APIでリポジトリ情報を取得するCollector。"""

    API_BASE = "https://api.github.com"

    def __init__(self, token: str | None = None) -> None:
        load_dotenv()
        self._token = token or os.environ.get("GITHUB_TOKEN", "")
        if not self._token:
            logger.warning(
                "GITHUB_TOKENが未設定です。認証なしでAPIを呼び出します。"
                "レート制限が厳しくなり、プライベートリポジトリにはアクセスできません。"
            )

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Accept": "application/vnd.github.v3+json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    async def collect(self, query: str, **kwargs: object) -> list[CollectedData]:
        """GitHubリポジトリの情報を収集する。

        Args:
            query: リポジトリのフルネーム（owner/repo形式）
            **kwargs: 未使用

        Returns:
            リポジトリ情報のリスト

        Raises:
            CollectionError: API呼び出しに失敗した場合
        """
        repo = query.strip("/")
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                repo_data = await self._fetch_repo(client, repo)
                default_branch = str(repo_data.get("default_branch", "main"))
                readme_content = await self._fetch_readme(client, repo)
                recent_commits = await self._fetch_recent_commits(client, repo)
                directory_tree = await self._fetch_directory_tree(client, repo, default_branch)
        except httpx.HTTPError as e:
            raise CollectionError(source="github", message=str(e)) from e

        parts = [
            f"# {repo_data.get('full_name', repo)}",
            f"\n{repo_data.get('description', 'No description')}",
            f"\nStars: {repo_data.get('stargazers_count', 0)} | "
            f"Forks: {repo_data.get('forks_count', 0)} | "
            f"Language: {repo_data.get('language', 'N/A')}",
        ]
        if readme_content:
            parts.append(f"\n## README\n{readme_content[:3000]}")
        if directory_tree:
            parts.append(f"\n## Directory Structure\n```\n{directory_tree}\n```")
        if recent_commits:
            parts.append("\n## Recent Commits")
            for commit in recent_commits[:5]:
                commit_data = commit.get("commit", {})
                if isinstance(commit_data, dict):
                    msg = str(commit_data.get("message", "")).split("\n")[0]
                else:
                    msg = ""
                parts.append(f"- {msg}")

        return [
            CollectedData(
                source="github",
                title=str(repo_data.get("full_name", repo)),
                url=str(repo_data.get("html_url", f"https://github.com/{repo}")),
                content="\n".join(parts),
                collected_at=datetime.now(UTC),
            )
        ]

    async def _fetch_repo(self, client: httpx.AsyncClient, repo: str) -> dict[str, object]:
        """リポジトリ情報を取得する。"""
        response = await client.get(f"{self.API_BASE}/repos/{repo}", headers=self._headers())
        response.raise_for_status()
        try:
            result: dict[str, object] = response.json()
        except ValueError as e:
            raise CollectionError(source="github", message=f"JSONパースエラー: {e}") from e
        return result

    async def _fetch_readme(self, client: httpx.AsyncClient, repo: str) -> str:
        """READMEの内容を取得する。"""
        try:
            response = await client.get(
                f"{self.API_BASE}/repos/{repo}/readme",
                headers={**self._headers(), "Accept": "application/vnd.github.v3.raw"},
            )
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError:
            return ""

    async def _fetch_directory_tree(
        self, client: httpx.AsyncClient, repo: str, default_branch: str
    ) -> str:
        """リポジトリのディレクトリ構造を取得する。"""
        try:
            response = await client.get(
                f"{self.API_BASE}/repos/{repo}/git/trees/{default_branch}",
                headers=self._headers(),
                params={"recursive": "1"},
            )
            response.raise_for_status()
            try:
                data: dict[str, object] = response.json()
            except ValueError:
                return ""
            tree = data.get("tree", [])
            if not isinstance(tree, list):
                return ""
            lines: list[str] = []
            for item in tree:
                if isinstance(item, dict):
                    path = str(item.get("path", ""))
                    item_type = str(item.get("type", ""))
                    if item_type == "tree":
                        lines.append(f"{path}/")
                    else:
                        lines.append(path)
            return "\n".join(lines[:200])
        except httpx.HTTPStatusError:
            return ""

    async def _fetch_recent_commits(
        self, client: httpx.AsyncClient, repo: str
    ) -> list[dict[str, object]]:
        """最新のコミットを取得する。"""
        try:
            response = await client.get(
                f"{self.API_BASE}/repos/{repo}/commits",
                headers=self._headers(),
                params={"per_page": 5},
            )
            response.raise_for_status()
            try:
                result: list[dict[str, object]] = response.json()
            except ValueError:
                return []
            return result
        except httpx.HTTPStatusError:
            return []
