"""ツール・Tips紹介 テンプレート。"""

from src.models.template import ContentTemplate, TemplateSection


def create_template() -> ContentTemplate:
    """ツール・Tips紹介のテンプレートを作成する。"""
    return ContentTemplate(
        content_type="tool-tips",
        name="ツール・Tips紹介",
        description="AI開発に役立つツールやTipsを紹介する記事",
        min_words=3000,
        max_words=5000,
        sections=[
            TemplateSection(
                title="はじめに",
                description="紹介するツール/Tipsの概要と、なぜ今注目すべきか",
            ),
            TemplateSection(
                title="セットアップ・導入方法",
                description="インストール手順や初期設定をステップバイステップで解説",
            ),
            TemplateSection(
                title="基本的な使い方",
                description="主要な機能や使い方をコード例・スクリーンショット付きで紹介",
            ),
            TemplateSection(
                title="実践的な活用例",
                description="実際のプロジェクトでの活用シーンやユースケース",
            ),
            TemplateSection(
                title="まとめ・他のツールとの比較",
                description="メリット・デメリットの整理と類似ツールとの比較",
            ),
        ],
        style_guide="です・ます調。ハンズオン形式で読者が手を動かしながら読めるように。"
        "コマンドやコード例は正確に記載する。"
        "メインタイトルは30文字以内目安。補足情報はサブタイトルとして分離する。",
    )
