"""テンプレートレジストリ。"""

from src.errors import TemplateNotFoundError
from src.models.blog_post import ContentType
from src.models.template import ContentTemplate
from src.templates.cv import create_template as cv_template
from src.templates.feature import create_template as feature_template
from src.templates.market_analysis import create_template as market_analysis_template
from src.templates.ml_practice import create_template as ml_practice_template
from src.templates.paper_review import create_template as paper_review_template
from src.templates.project_intro import create_template as project_intro_template
from src.templates.tool_tips import create_template as tool_tips_template
from src.templates.weekly_ai_news import create_template as weekly_ai_news_template

_REGISTRY: dict[ContentType, ContentTemplate] = {}


def _init_registry() -> None:
    """レジストリを初期化する。"""
    if _REGISTRY:
        return
    creators = [
        weekly_ai_news_template,
        paper_review_template,
        project_intro_template,
        tool_tips_template,
        market_analysis_template,
        ml_practice_template,
        cv_template,
        feature_template,
    ]
    for creator in creators:
        template = creator()
        _REGISTRY[template.content_type] = template


def get_template(content_type: ContentType) -> ContentTemplate:
    """指定タイプのテンプレートを取得する。

    Args:
        content_type: コンテンツタイプ

    Returns:
        対応するテンプレート

    Raises:
        TemplateNotFoundError: テンプレートが見つからない場合
    """
    _init_registry()
    template = _REGISTRY.get(content_type)
    if template is None:
        raise TemplateNotFoundError(content_type=content_type)
    return template


def list_templates() -> list[ContentTemplate]:
    """全テンプレートのリストを返す。

    Returns:
        登録済みテンプレートのリスト
    """
    _init_registry()
    return list(_REGISTRY.values())
