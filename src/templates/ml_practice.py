"""AI×データ分析・ML開発 テンプレート。"""

from src.models.template import ContentTemplate, TemplateSection


def create_template() -> ContentTemplate:
    """AI×データ分析・ML開発のテンプレートを作成する。"""
    return ContentTemplate(
        content_type="ml-practice",
        name="AI×データ分析・ML開発",
        description="データ分析やML開発の実践的なノウハウを共有する記事",
        min_words=3000,
        max_words=8000,
        sections=[
            TemplateSection(
                title="課題設定",
                description="解決したい課題やプロジェクトの背景",
            ),
            TemplateSection(
                title="データの準備・前処理",
                description="使用するデータの概要と前処理パイプライン",
            ),
            TemplateSection(
                title="モデル設計・実装",
                description="モデルの選定理由と実装の詳細をコード付きで解説",
            ),
            TemplateSection(
                title="評価・結果",
                description="モデルの評価方法と実験結果",
            ),
            TemplateSection(
                title="実運用のポイント",
                description="デプロイメント、監視、改善サイクルなど実運用の知見",
                required=False,
            ),
            TemplateSection(
                title="まとめ・学び",
                description="プロジェクトの総括と得られた知見",
            ),
        ],
        style_guide="です・ます調。コード例やデータの可視化を積極的に含める。"
        "再現可能な内容を心がけ、ライブラリのバージョン情報も記載する。"
        "メインタイトルは30文字以内目安。補足情報はサブタイトルとして分離する。",
    )
