"""テンプレートレジストリのテスト。"""

import pytest

from src.errors import TemplateNotFoundError
from src.templates import get_template, list_templates


class TestGetTemplate:
    """get_templateのテスト。"""

    def test_get_weekly_ai_news_template(self) -> None:
        """weekly-ai-newsテンプレートを取得できる。"""
        template = get_template("weekly-ai-news")
        assert template.content_type == "weekly-ai-news"
        assert template.min_words == 3000
        assert template.max_words == 5000
        assert len(template.sections) > 0

    def test_get_paper_review_template(self) -> None:
        """paper-reviewテンプレートを取得できる。"""
        template = get_template("paper-review")
        assert template.content_type == "paper-review"
        assert template.min_words == 5000

    def test_get_feature_template(self) -> None:
        """featureテンプレートを取得できる。"""
        template = get_template("feature")
        assert template.content_type == "feature"
        assert template.min_words == 15000

    def test_all_content_types_have_templates(self) -> None:
        """全8タイプのテンプレートが存在する。"""
        types = [
            "weekly-ai-news",
            "paper-review",
            "project-intro",
            "tool-tips",
            "market-analysis",
            "ml-practice",
            "cv",
            "feature",
        ]
        for ct in types:
            template = get_template(ct)  # type: ignore[arg-type]
            assert template.content_type == ct

    def test_templates_have_required_fields(self) -> None:
        """全テンプレートが必須フィールドを持つ。"""
        for template in list_templates():
            assert template.name
            assert template.description
            assert template.min_words > 0
            assert template.max_words > template.min_words
            assert len(template.sections) > 0
            assert template.style_guide

    def test_invalid_type_raises_error(self) -> None:
        """無効なタイプでTemplateNotFoundErrorが発生する。"""
        with pytest.raises(TemplateNotFoundError):
            get_template("invalid-type")  # type: ignore[arg-type]


class TestListTemplates:
    """list_templatesのテスト。"""

    def test_returns_all_templates(self) -> None:
        """全8テンプレートが返される。"""
        templates = list_templates()
        assert len(templates) == 8

    def test_all_have_unique_types(self) -> None:
        """全テンプレートのタイプがユニーク。"""
        templates = list_templates()
        types = [t.content_type for t in templates]
        assert len(types) == len(set(types))
