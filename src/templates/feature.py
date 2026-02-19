"""特集記事 テンプレート。"""

from src.models.template import ContentTemplate, TemplateSection


def create_template() -> ContentTemplate:
    """特集記事のテンプレートを作成する。"""
    return ContentTemplate(
        content_type="feature",
        name="特集記事",
        description="特定テーマを深堀りする大型特集記事",
        min_words=15000,
        max_words=20000,
        sections=[
            TemplateSection(
                title="イントロダクション",
                description="テーマの重要性と記事全体の構成を説明",
            ),
            TemplateSection(
                title="背景・歴史",
                description="テーマの背景や発展の経緯を解説",
            ),
            TemplateSection(
                title="現状分析",
                description="現在の技術・市場・業界の状況を多角的に分析",
            ),
            TemplateSection(
                title="詳細解説（パート1）",
                description="テーマの核心部分を掘り下げて解説",
            ),
            TemplateSection(
                title="詳細解説（パート2）",
                description="別の角度から深堀りした解説",
            ),
            TemplateSection(
                title="実践・ケーススタディ",
                description="実際の事例やハンズオンコンテンツ",
            ),
            TemplateSection(
                title="今後の展望",
                description="将来のトレンドや期待される発展",
            ),
            TemplateSection(
                title="まとめ",
                description="記事全体の要約と読者へのメッセージ",
            ),
        ],
        style_guide="です・ます調。大型記事のため、目次や小見出しを効果的に使い、"
        "読者が途中から読んでも理解できる構成にする。"
        "図表、コード例、事例を豊富に含める。"
        "メインタイトルは30文字以内目安。補足情報はサブタイトルとして分離する。",
    )
