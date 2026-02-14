"""画像認識・コンピュータビジョン テンプレート。"""

from src.models.template import ContentTemplate, TemplateSection


def create_template() -> ContentTemplate:
    """画像認識・コンピュータビジョンのテンプレートを作成する。"""
    return ContentTemplate(
        content_type="cv",
        name="画像認識・コンピュータビジョン",
        description="画像認識やコンピュータビジョンの技術解説・実践記事",
        min_words=3000,
        max_words=8000,
        sections=[
            TemplateSection(
                title="技術の概要",
                description="扱う技術やタスクの概要と応用分野",
            ),
            TemplateSection(
                title="アルゴリズム・モデル解説",
                description="使用するアルゴリズムやモデルの仕組みを解説",
            ),
            TemplateSection(
                title="実装・コード例",
                description="Pythonコード例を用いた実装の詳細",
            ),
            TemplateSection(
                title="結果の可視化・評価",
                description="処理結果の可視化と性能評価",
            ),
            TemplateSection(
                title="まとめ・応用例",
                description="技術の要約と実世界での応用可能性",
            ),
        ],
        style_guide="です・ます調。図や画像を多用し、視覚的に理解しやすい記事を心がける。"
        "コード例はPyTorch/OpenCV等の主要フレームワークを使用する。",
    )
