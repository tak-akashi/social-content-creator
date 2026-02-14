"""Publisher共通インターフェース。"""

from typing import Protocol

from src.models.blog_post import BlogPost, PublishResult


class PublisherProtocol(Protocol):  # pragma: no cover
    """投稿先連携の共通プロトコル。"""

    async def publish(self, post: BlogPost, **kwargs: object) -> PublishResult:
        """記事を投稿する。

        Args:
            post: 投稿するBlogPost
            **kwargs: Publisher固有のパラメータ

        Returns:
            投稿結果
        """
        ...
