"""論文解説 テンプレート。"""

from src.models.template import ContentTemplate, TemplateSection


def create_template() -> ContentTemplate:
    """論文解説のテンプレートを作成する。"""
    return ContentTemplate(
        content_type="paper-review",
        name="論文解説",
        description="AI/ML分野の注目論文を分かりやすく解説する記事",
        min_words=5000,
        max_words=8000,
        sections=[
            TemplateSection(
                title="論文の概要",
                description="タイトル、著者、発表先、キーワードを含む概要",
            ),
            TemplateSection(
                title="背景と課題",
                description="この研究の背景と解決しようとしている課題",
            ),
            TemplateSection(
                title="提案手法",
                description="論文で提案されている手法の詳細な解説",
            ),
            TemplateSection(
                title="実験結果",
                description="主要な実験結果とベースラインとの比較",
            ),
            TemplateSection(
                title="考察・インパクト",
                description="実務への応用可能性や業界へのインパクトを考察",
            ),
            TemplateSection(
                title="まとめ",
                description="論文の要点まとめと今後の展望",
            ),
        ],
        style_guide="です・ます調。技術的に正確でありつつ、専門外の読者にも理解できるよう"
        "噛み砕いた表現を心がける。図表の説明を丁寧に行う。",
    )
