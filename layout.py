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
        node: Union[Text, Element],
        width: int = 800,
        height: int = 600,
        font_family: Optional[str] = None,
        font_size: int = 16,
        maximum_font_size: int = 32,
        minimum_font_size: int = 4,
    ) -> None:
        # DOM ツリーのノード
        self.node = node

        # レイアウトツリーの子ノード
        self.children = []

        # 文字プロパティ
        self.font_family = font_family
        self.font_size = font_size
        self.maximum_font_size = maximum_font_size
        self.minimum_font_size = minimum_font_size
        self.font_weight = "normal"
        self.font_style = "roman"

        # 描画開始位置の縦横幅
        self.HSTEP, self.VSTEP = 13, 16

        # レイアウト位置プロパティ
        self.x = self.HSTEP
        self.y = self.VSTEP
        self.width = width - 2*self.HSTEP
        self.height = None

        # 描画リスト
        self.display_list = []

    def layout(self):
        child = BlockLayout(
            node=self.node,
            parent=self,
            previous=None,
            width=self.width,
            height=self.height,
            font_size=self.font_size,
        )
        self.children.append(child)
        child.layout()
        self.height = child.height
        self.display_list = child.display_list
        return self.display_list


BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary"
]
# TODO DOM ツリーを、再帰的な BlockLayout の重ね合わせのレイアウトツリーに変換

class BlockLayout(DocumentLayout):
    def __init__(
        self,
        node: Union[Text, Element],
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
            node=node,
            width=width,
            height=height,
            font_family=font_family,
            font_size=font_size,
        )

        # ブロックレイアウトツリー
        self.parent = parent  # 親ブロックノードのポインタ
        self.previous = previous  # 一つ前のブロックノードのポインタ
        self.children = []  # 子ノード

        # 文字プロパティ
        self.tmp_font_size = self.font_size  # フォントサイズ保持のための一時変数
        self.font_cache = {}  # フォントをキャッシュすることで高速化

        # レイアウト位置プロパティ
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0

        # カーソル位置プロパティ
        self.cursor_x, self.cursor_y = 0, 0

    def layout(self):
        self.width = self.parent.width  # 親ブロックノードと自ブロックノードの width は同じ
        self.x = self.parent.x  # 親ブロックノードの左端から自ブロックノードの x 開始

        if self.previous:
            # 兄弟ブロックがある場合、前のブロックの直後の高さから自ブロックの y 開始
            self.y = self.previous.y + self.previous.height
        else:
            # 兄弟ブロックがない場合、親ブロックの上端から自ブロックの y 開始
            self.y = self.parent.y

        mode = self.layout_mode()
        if mode == "block":
            # block モードの場合、DOM ツリーの構造に対応するレイアウトツリーを再帰的に構築
            previous = None
            for child in self.node.children:
                # FIXME BLOCK_ELEMENTS 以外のtagの場合、BlockLayoutにまとめて渡せるように修正する
                next = BlockLayout(node=child, parent=self, previous=previous)
                self.children.append(next)
                previous = next

        else:
            # inline モードの場合、DOM ノードの内容を再帰的に display_list に掃き出す
            self.cursor_x = 0
            self.cursor_y = 0
            self.weight = "normal"
            self.style = "roman"
            self.size = 16

            self.line = []  # 文字位置修正のためのバッファ
            self.recurse(self.node)  # 再帰的に DOM Tree をパース
            self.set_position()  # 残りの全ての self.line の単語を display_list に掃き出す

            self.height = self.cursor_y

        for child in self.children:
            child.layout()
            self.display_list.extend(child.display_list)

    def layout_mode(self):
        if isinstance(self.node, Text):
            return "inline"
        elif any(
            [
                isinstance(child, Element) and child.tag in BLOCK_ELEMENTS for child in self.node.children
            ]
        ):
            return "block"
        elif self.node.children:
            return "inline"
        else:
            return "block"

    def recurse(self, node: Union[Text, Element]):
        if isinstance(node, Text):
            self.set_text(node)
        else:
            # タグオープン
            self.open_tag(tag=node.tag)

            for child in node.children:
                self.recurse(child)

            # タグクローズ
            self.close_tag(tag=node.tag)

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

        for relative_x, word, font in self.line:
            x = self.x + relative_x
            y = self.y + baseline - 1.25 * font.metrics("ascent")
            self.display_list.append((x, y, word, font))

            # cursor 位置を次の行に更新
            self.cursor_x = 0
            self.cursor_y = baseline + 1.25 * max_descent

        # バッファをフラッシュ
        self.line = []
