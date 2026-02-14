"""AI×株式投資・企業分析 テンプレート。"""

from src.models.template import ContentTemplate, TemplateSection


def create_template() -> ContentTemplate:
    """AI×株式投資・企業分析のテンプレートを作成する。"""
    return ContentTemplate(
        content_type="market-analysis",
        name="AI×株式投資・企業分析",
        description="AI技術を活用した株式投資分析や企業分析の記事",
        min_words=3000,
        max_words=8000,
        sections=[
            TemplateSection(
                title="分析対象の概要",
                description="分析対象の企業・セクター・テーマの概要",
            ),
            TemplateSection(
                title="AI分析手法の説明",
                description="使用したAI分析手法やモデルの解説",
            ),
            TemplateSection(
                title="分析結果",
                description="データに基づく分析結果の詳細",
            ),
            TemplateSection(
                title="市場動向との関連",
                description="マクロ経済やAI業界動向との関連性を考察",
            ),
            TemplateSection(
                title="まとめ・投資の視点",
                description="分析の要約と投資判断に関する考察",
            ),
        ],
        style_guide="です・ます調。データに基づく客観的な分析を心がける。"
        "投資助言ではなく情報提供・分析共有のスタンスを明確にする。"
        "免責事項を記載する。",
    )
