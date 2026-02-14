"""テンプレート関連のデータモデル。"""

from pydantic import BaseModel

from src.models.blog_post import ContentType


class TemplateSection(BaseModel):
    """テンプレートのセクション定義。"""

    title: str
    description: str
    required: bool = True


class ContentTemplate(BaseModel):
    """コンテンツテンプレートのデータモデル。"""

    content_type: ContentType
    name: str
    description: str
    min_words: int
    max_words: int
    sections: list[TemplateSection]
    style_guide: str
