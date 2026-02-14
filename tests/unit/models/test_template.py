"""ContentTemplate, TemplateSection のテスト。"""

from src.models.template import ContentTemplate, TemplateSection


class TestTemplateSection:
    """TemplateSectionのテスト。"""

    def test_create_required_section(self) -> None:
        """必須セクションを生成できる。"""
        section = TemplateSection(title="はじめに", description="イントロダクション")
        assert section.required is True

    def test_create_optional_section(self) -> None:
        """任意セクションを生成できる。"""
        section = TemplateSection(title="補足", description="補足情報", required=False)
        assert section.required is False


class TestContentTemplate:
    """ContentTemplateのテスト。"""

    def test_create_template(self) -> None:
        """テンプレートを生成できる。"""
        template = ContentTemplate(
            content_type="weekly-ai-news",
            name="テスト",
            description="テスト用",
            min_words=1000,
            max_words=3000,
            sections=[
                TemplateSection(title="セクション1", description="説明1"),
            ],
            style_guide="です・ます調",
        )
        assert template.content_type == "weekly-ai-news"
        assert len(template.sections) == 1
        assert template.min_words == 1000
