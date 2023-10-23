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

        # 配置
        self.HSTEP, self.VSTEP = 13, font_size  # 描画開始位置の縦横幅

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

        # 改行ステータスを初期化
        self.newline = False  # 改行するためのフラグ
        self.additional_V_space = False  # Headingや段落の際に上下余白をつけるためのフラグ

    def layout(self) -> List[Tuple[float, float, str, Font]]:
        self.line = []  # 文字位置修正のためのバッファ
        self.cursor_x, self.cursor_y, self.baseline = self.HSTEP, self.VSTEP, self.VSTEP

        # 再帰的に DOM Tree を解析する
        self.recurse(self.dom)

        # テキスト描画位置を計算
        display_list = self.set_position()
        return display_list

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
            self.line.append((word, font, self.newline, self.additional_V_space))
            # 改行ステータスを初期化
            self.newline = False
            self.additional_V_space = False

    def get_font(
        self, font_family: str, font_size: int, font_weight: str, font_style: str
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
            self.newline = True
        elif tag == "p":
            self.additional_V_space = True
        elif tag == "h1":
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 3)
            self.font_weight = "bold"
            self.additional_V_space = True
        elif tag == "h2":
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 2)
            self.font_weight = "bold"
            self.additional_V_space = True
        elif tag == "h3":
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 1.5)
            self.font_weight = "bold"
            self.additional_V_space = True
        elif tag == "h4":
            self.font_size = self.tmp_font_size
            self.font_size = int(self.font_size * 1.1)
            self.font_weight = "bold"
            self.additional_V_space = True
        elif tag == "h5":
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 0.8)
            self.font_weight = "bold"
            self.additional_V_space = True
        elif tag == "h6":
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 0.5)
            self.font_weight = "bold"
            self.additional_V_space = True

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
            self.additional_V_space = True
        elif tag == "h1":
            self.font_size = self.tmp_font_size
            self.font_weight = "normal"
            self.additional_V_space = True
        elif tag == "h2":
            self.font_size = self.tmp_font_size
            self.font_weight = "normal"
            self.additional_V_space = True
        elif tag == "h3":
            self.font_size = self.tmp_font_size
            self.font_weight = "normal"
            self.additional_V_space = True
        elif tag == "h4":
            self.font_size = self.tmp_font_size
            self.font_weight = "normal"
            self.additional_V_space = True
        elif tag == "h5":
            self.font_size = self.tmp_font_size
            self.font_weight = "normal"
            self.additional_V_space = True
        elif tag == "h6":
            self.font_size = self.tmp_font_size
            self.font_weight = "normal"
            self.additional_V_space = True

    def set_position(self) -> List[Tuple[float, float, str, Font]]:
        """
        呼び出された時点までに self.line に格納されている要素を
        払い出して、描画位置を計算する

        描画位置計算手順
        1. 先にバッファに同じ行のテキストを追加
        2. 改行のタイミングでバッファの中で最も
           背の高いフォントに合わせて、描画位置を計算
        3. バッファをクリアして次の行のテキストをバッファに追加 (2に戻る)
        """
        display_list = []
        _buffer = []
        for word, font, newline, additional_V_space in self.line:
            w = font.measure(word)
            # 改行条件
            if (
                (self.cursor_x >= self.width - w and self.width > w)
                or newline
                or additional_V_space
            ):
                # バッファ中のテキストで最も背の高いフォントにベースラインを揃える
                display_list = self.set_baseline(display_list, _buffer)
                # 縦横位置とバッファを初期化
                _buffer = []
                self.cursor_x = self.HSTEP
                self.baseline += self.max_ascent * 1.25
            # 段落の場合縦スペースを追加
            if additional_V_space:
                self.baseline += self.VSTEP

            _buffer.append((self.cursor_x, word, font))
            self.cursor_x += w + font.measure(" ")

        # バッファ中の残りの文字も追加
        display_list = self.set_baseline(display_list, _buffer)

        return display_list

    def set_baseline(
        self, display_list: List[Tuple[float, float, str, Font]], buffer: list
    ) -> List[Tuple[float, float, str, Font]]:
        """バッファ中のテキストで最も背の高いフォントに表示位置のベースラインを揃えてdisplay_listに追加"""
        self.max_ascent = max([_font.metrics("ascent") for _, _, _font in buffer])
        for _x, _word, _font in buffer:
            self.cursor_y = (
                self.baseline + (self.max_ascent - _font.metrics("ascent")) * 1.25
            )
            display_list.append((_x, self.cursor_y, _word, _font))
        return display_list
