"""Markdownユーティリティのテスト（count_characters中心）。"""

from src.utils.markdown import count_characters


class TestCountCharacters:
    """count_characters()のテスト。"""

    def test_plain_text(self) -> None:
        """プレーンテキストの文字数を正しくカウントする。"""
        assert count_characters("Hello World") == 11

    def test_heading_removal(self) -> None:
        """見出し記号を除去してカウントする。"""
        text = "# 見出し1\n## 見出し2\n本文"
        result = count_characters(text)
        # "見出し1\n見出し2\n本文" = 見出し1(4) + \n(1) + 見出し2(4) + \n(1) + 本文(2) = 12
        assert result == 12

    def test_link_removal(self) -> None:
        """リンク記法を除去してテキスト部分のみカウントする。"""
        text = "[リンクテキスト](https://example.com)"
        result = count_characters(text)
        assert result == len("リンクテキスト")

    def test_image_removal(self) -> None:
        """画像記法を除去してaltテキスト部分のみカウントする。"""
        text = "![代替テキスト](https://example.com/image.png)"
        result = count_characters(text)
        assert result == len("代替テキスト")

    def test_bold_removal(self) -> None:
        """強調記法を除去してカウントする。"""
        text = "**太字テキスト**と*斜体テキスト*"
        result = count_characters(text)
        assert result == len("太字テキストと斜体テキスト")

    def test_code_block_removal(self) -> None:
        """コードブロックを除去してカウントする。"""
        text = "本文\n```python\nprint('hello')\n```\n残り"
        result = count_characters(text)
        assert result == len("本文\n\n残り")

    def test_inline_code_removal(self) -> None:
        """インラインコードの記法を除去してカウントする。"""
        text = "変数`foo`の値"
        result = count_characters(text)
        assert result == len("変数fooの値")

    def test_empty_string(self) -> None:
        """空文字列は0を返す。"""
        assert count_characters("") == 0

    def test_whitespace_only(self) -> None:
        """空白のみのテキストは0を返す。"""
        assert count_characters("   \n\n  ") == 0

    def test_complex_markdown(self) -> None:
        """複合的なMarkdown記法が正しく処理される。"""
        text = (
            "# タイトル\n\n"
            "これは**太字**と[リンク](https://example.com)を含む段落です。\n\n"
            "```\ncode\n```\n\n"
            "`inline`も含む。"
        )
        result = count_characters(text)
        plain = "タイトル\n\nこれは太字とリンクを含む段落です。\n\n\n\ninlineも含む。"
        expected = count_characters(plain)
        assert result == expected
