"""GitHubプロジェクト紹介 テンプレート。"""

from src.models.template import ContentTemplate, TemplateSection


def create_template() -> ContentTemplate:
    """GitHubプロジェクト紹介のテンプレートを作成する。"""
    return ContentTemplate(
        content_type="project-intro",
        name="GitHubプロジェクト紹介",
        description="注目のGitHubリポジトリを紹介・レビューする記事",
        min_words=3000,
        max_words=5000,
        sections=[
            TemplateSection(
                title="プロジェクト概要",
                description="プロジェクトの目的、主要機能、対象ユーザーを紹介",
            ),
            TemplateSection(
                title="技術スタック・アーキテクチャ",
                description="使用されている技術やアーキテクチャの特徴",
            ),
            TemplateSection(
                title="インストール・使い方",
                description="セットアップ手順と基本的な使い方をコード例付きで解説",
            ),
            TemplateSection(
                title="特徴的な機能・設計",
                description="他のプロジェクトとの差別化ポイントや優れた設計思想",
            ),
            TemplateSection(
                title="まとめ・おすすめポイント",
                description="どんな場面で活用できるかの総括",
            ),
        ],
        style_guide="です・ます調。コード例を積極的に示し、実際に使えるイメージを伝える。"
        "読者が「試してみたい」と思えるような紹介を心がける。"
        "メインタイトルは30文字以内目安。補足情報はサブタイトルとして分離する。",
    )
