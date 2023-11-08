from __future__ import annotations
from typing import Union, Optional, List, Tuple
import tkinter
import tkinter.font
from tkinter.font import Font
from html_parser import Text, Element


# BlockLayout の親ノードとしての DocumentLayout
class DocumentLayout:
    def __init__(
        self,
        dom: Union[Text, Element],
        width: int = 800,
        height: int = 600,
        font_family: Optional[str] = None,
        font_size: int = 16,
        maximum_font_size: int = 32,
        minimum_font_size: int = 4,
    ) -> None:
        # ウィンドウプロパティ
        self.width = width
        self.height = height

        # DOM ツリー
        self.dom = dom

        # レイアウトツリー
        self.children = []  # 子ノード

        # 文字プロパティ
        self.font_family = font_family
        self.font_size = font_size
        self.maximum_font_size = maximum_font_size
        self.minimum_font_size = minimum_font_size
        self.font_weight = "normal"
        self.font_style = "roman"

        # 描画開始位置の縦横幅
        self.HSTEP, self.VSTEP = 13, 16

        # 描画リスト
        self.display_list = []

    def layout(self):
        child = BlockLayout(
            dom=self.dom,
            parent=self,
            previous=None,
            width=self.width,
            height=self.height,
            font_size=self.font_size,
        )
        self.children.append(child)

        self.display_list = child.layout()
        return self.display_list


# TODO DOM ツリーを、再帰的な BlockLayout の重ね合わせとしてレイアウトする
class BlockLayout(DocumentLayout):
    def __init__(
        self,
        dom: Union[Text, Element],
        parent: Union[DocumentLayout, BlockLayout],
        previous: BlockLayout,
        width: int = 800,
        height: int = 600,
        font_family: Optional[str] = None,
        font_size: int = 16,
    ) -> None:
        """
        ユーザーインタラクションで可変の変数（画面サイズやフォントサイズなど）は、
        再描画時に反映するためにコンストラクタの引数にとる。
        """
        super().__init__(
            dom=dom,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
        )

        # レイアウトツリー
        self.parent = parent  # 親ノードのポインタ
        self.previous = previous  # 一つ前のノードのポインタ
        self.children = []  # 子ノード

        # 文字プロパティ
        self.tmp_font_size = self.font_size  # フォントサイズ保持のための一時変数
        self.font_cache = {}  # フォントをキャッシュすることで高速化

        # カーソル位置プロパティ
        self.cursor_x, self.cursor_y = self.HSTEP, self.VSTEP

    def layout(self) -> List[Tuple[float, float, str, Font]]:
        self.line = []  # 文字位置修正のためのバッファ

        # 再帰的に DOM Tree を解析する
        self.recurse(self.dom)

        # 残りの全ての単語を display_list に掃き出す
        self.set_position()

        return self.display_list

    def recurse(self, dom: Union[Text, Element]):
        if isinstance(dom, Text):
            self.set_text(dom)
        else:
            # タグオープン
            self.open_tag(tag=dom.tag)

            for child in dom.children:
                self.recurse(child)

            # タグクローズ
            self.close_tag(tag=dom.tag)

    def set_text(self, text_node: Text):
        font = self.get_font(
            font_family=self.font_family,
            font_size=self.font_size,
            font_weight=self.font_weight,
            font_style=self.font_style,
        )
        for word in text_node.text.split():
            w = font.measure(word)
            # 横幅まで達したら、改行するためにバッファの単語を掃き出す
            if self.cursor_x + w >= self.width and self.width > w:
                self.set_position()
            self.line.append((self.cursor_x, word, font))
            self.cursor_x += w + font.measure(" ")

    def get_font(
        self, font_family: str,
        font_size: int, font_weight: str, font_style: str
    ):
        """フォントをキャッシュすることで高速化"""
        key = (font_family, font_size, font_weight, font_style)
        if key not in self.font_cache:
            font = tkinter.font.Font(
                family=font_family, size=font_size, weight=font_weight, slant=font_style
            )
            self.font_cache[key] = font
        return self.font_cache[key]

    def open_tag(self, tag: str):
        # タグに沿って文字フォント更新
        if tag == "b":
            self.font_weight = "bold"
        elif tag == "i":
            self.font_style = "italic"
        elif tag == "small":
            self.font_size -= 2
        elif tag == "big":
            self.font_size += 4
        elif tag == "br" or tag == "br/" or tag == "br /":
            self.set_position()
        elif tag == "p":
            self.set_position()
            self.cursor_y += self.font_size
        elif tag == "h1":
            self.set_position()
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 3)
            self.font_weight = "bold"
            self.cursor_y += self.font_size/4
        elif tag == "h2":
            self.set_position()
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 2)
            self.font_weight = "bold"
            self.cursor_y += self.font_size/4
        elif tag == "h3":
            self.set_position()
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 1.5)
            self.font_weight = "bold"
            self.cursor_y += self.font_size/4
        elif tag == "h4":
            self.set_position()
            self.font_size = self.tmp_font_size
            self.font_size = int(self.font_size * 1.1)
            self.font_weight = "bold"
            self.cursor_y += self.font_size/4
        elif tag == "h5":
            self.set_position()
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 0.8)
            self.font_weight = "bold"
            self.cursor_y += self.font_size/4
        elif tag == "h6":
            self.set_position()
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 0.5)
            self.font_weight = "bold"
            self.cursor_y += self.font_size/4

    def close_tag(self, tag: str):
        # 閉タグに沿って文字フォントを戻す
        if tag == "b":
            self.font_weight = "normal"
        elif tag == "i":
            self.font_style = "roman"
        elif tag == "small":
            self.font_size += 2
        elif tag == "big":
            self.font_size -= 4
        elif tag == "p":
            self.set_position()
            self.cursor_y += self.font_size
        elif tag == "h1":
            self.set_position()
            self.cursor_y += self.font_size/2
            self.font_size = self.tmp_font_size
            self.font_weight = "normal"
        elif tag == "h2":
            self.set_position()
            self.cursor_y += self.font_size/2
            self.font_size = self.tmp_font_size
            self.font_weight = "normal"
        elif tag == "h3":
            self.set_position()
            self.cursor_y += self.font_size/2
            self.font_size = self.tmp_font_size
            self.font_weight = "normal"
        elif tag == "h4":
            self.set_position()
            self.cursor_y += self.font_size/2
            self.font_size = self.tmp_font_size
            self.font_weight = "normal"
        elif tag == "h5":
            self.set_position()
            self.cursor_y += self.font_size/2
            self.font_size = self.tmp_font_size
            self.font_weight = "normal"
        elif tag == "h6":
            self.set_position()
            self.cursor_y += self.font_size/2
            self.font_size = self.tmp_font_size
            self.font_weight = "normal"

    def set_position(self) -> List[Tuple[float, float, str, Font]]:
        """
        呼び出された時点までに self.line に格納されている要素を
        払い出して、縦軸の描画位置を計算する

        1. 行の最も背の高いフォントに各単語の baseline を揃える
        2. display_list に単語を追加する
        3. cursor_x と cursor_y を更新する
        """

        if not self.line:
            return
        metrics = [font.metrics() for _, _, font in self.line]

        # この行の縦軸のベースライン
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent

        # 次の行の位置はフォントの底辺位置より下回っている必要がある
        max_descent = max([metric["descent"] for metric in metrics])

        for x, word, font in self.line:
            y = baseline - 1.25 * font.metrics("ascent")

            self.display_list.append((x, y, word, font))

            # cursor 位置を次の行に更新
            self.cursor_x = self.HSTEP
            self.cursor_y = baseline + 1.25 * max_descent

        # バッファをフラッシュ
        self.line = []
