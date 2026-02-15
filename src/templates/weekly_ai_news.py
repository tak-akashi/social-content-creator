"""週刊AIニュースハイライト テンプレート。"""

from src.models.template import ContentTemplate, TemplateSection


def create_template() -> ContentTemplate:
    """週刊AIニュースハイライトのテンプレートを作成する。"""
    return ContentTemplate(
        content_type="weekly-ai-news",
        name="週刊AIニュースハイライト",
        description="過去1週間のAI関連ニュースを厳選して紹介する記事",
        min_words=3000,
        max_words=5000,
        sections=[
            TemplateSection(
                title="今週のハイライト",
                description="最も注目すべきニュース1〜2件を詳しく解説",
            ),
            TemplateSection(
                title="主要ニュースまとめ",
                description="3〜5件のニュースを簡潔にまとめる",
            ),
            TemplateSection(
                title="業界動向・トレンド",
                description="今週のニュースから読み取れる業界全体の動きを分析",
            ),
            TemplateSection(
                title="注目の新サービス・ツール",
                description="新しくリリースされたAI関連サービスやツールを紹介",
                required=False,
            ),
            TemplateSection(
                title="まとめと来週の注目ポイント",
                description="今週の総括と来週注目すべきイベント・リリース",
            ),
        ],
        style_guide="です・ます調。丁寧かつ親しみやすいトーン。"
        "技術的な内容は具体例を交えてわかりやすく解説する。"
        "タイトルは「【週刊AIニュースハイライト】（{年}年{月}月第{週}週）〜{トピック1}、{トピック2}、{トピック3}〜」の形式とする。"
        "見出し（h2/h3/h4）には「1. 」のような番号を付けないこと。"
        "WordPressテーマ（Cocoon）が目次を自動生成する際に二重番号になるため。",
    )
