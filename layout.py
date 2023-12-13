from __future__ import annotations
from typing import Union, Optional, List, Tuple
import tkinter
import tkinter.font
from tkinter.font import Font
from html_parser import Text, Element

def layout_tree(layout_object: Union[DocumentLayout, BlockLayout], display_list: list):
    """レイアウトツリーを再帰的に処理し display_layout へ一次元配列として掃き出す。

    Args:
        layout_object (Union[DocumentLayout, BlockLayout]): レイアウトツリーのノード
        display_list (list): Browser.draw で使用される一次元配列
    """
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        layout_tree(child, display_list)

# BlockLayout の親ノードとしての DocumentLayout
class DocumentLayout:
    def __init__(
        self,
        dom_node: Union[Text, Element],
        width: int = 800,
        font_family: Optional[str] = None,
        font_size: int = 16,
        maximum_font_size: int = 32,
        minimum_font_size: int = 4,
    ) -> None:
        # DOM ツリーのノード
        self.dom_node = dom_node

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

    def paint(self):
        """ layout_tree 関数の内部処理の初期化をする。

        Returns:
            list: display_layout を初期化
        """
        return []

    def layout(self):
        """ 
        DOM ツリーの各ノードの画面に対する表示位置を決定するレイアウトツリーを作成。
        DocumentLayout をルートノード、BlockLayout をその子ノードとして
        DOM ツリーに対応する各要素の位置情報を持ったツリー構造を再帰的に作成する。
        """
        child = BlockLayout(
            dom_node=self.dom_node,
            parent=self,
            previous=None,
            width=self.width,
            font_size=self.font_size,
        )
        self.children.append(child)
        child.layout()
        self.height = child.height


BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary"
]

# TODO nav class="link" タグをうすい灰色の背景にする
# TODO ol タグでインデント+番号つきリストに対応
# TODO nav ="toc" タグで、目次を追加
class BlockLayout(DocumentLayout):
    def __init__(
        self,
        dom_node: Union[Text, Element],
        parent: Union[DocumentLayout, BlockLayout],
        previous: BlockLayout,
        width: int = 800,
        font_family: Optional[str] = None,
        font_size: int = 16,
    ) -> None:
        """ 
        DOM ツリーのノードをパースし、レイアウト情報を持つ各ブロックノード (BlockLayout) の
        重ね合わせであるレイアウトツリーとして再構築。「ブロックノード」とはレイアウトツリーの
        各ノードである。「レイアウトツリー」とは HTML の各要素をブロックのタイルと考え、
        DOM ツリーの各要素をブロックの重ね合わせとしてレイアウトすることを目的とした構造である。

        ユーザーインタラクションで可変の変数（画面サイズやフォントサイズなど）は、
        再描画時に反映するためにコンストラクタの引数にとる。

        Args:
            dom_node (Union[Text, Element]): DOM ツリーのノード
            parent (Union[DocumentLayout, BlockLayout]): 親ブロックノード
            previous (BlockLayout): 同じ親ブロックノードを持つ兄弟ノード。同じレイヤーに順に並んで表示する。
            width (int, optional): ブロックノードの横幅。 Defaults to 800.
            font_family (Optional[str], None): フォント名。 Defaults to None.
            font_size (int, optional): フォントサイズ。 Defaults to 16.
        """
        super().__init__(
            dom_node=dom_node,
            width=width,
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

        # レイアウト絶対位置プロパティ
        self.x = 0
        self.y = 0
        self.height = None

        # レイアウト総体位置プロパティ
        self.cursor_x =  0
        self.cursor_y =  0

        # 描画リスト
        self.display_list = []
        

    def paint(self):
        """ layout_tree 関数の内部処理で、レイアウトツリーに沿って
        再帰的に DrawText、DrawRect で表示要素を追加する。

        Returns:
            List[DrawText, DrawRect]: display_list の部分要素。
        """
        cmds = []
        if isinstance(self.dom_node, Element) and self.dom_node.tag == "pre":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = DrawRect(x1=self.x, y1=self.y, x2=x2, y2=y2, color="gray")
            cmds.append(rect)
        
        if self.layout_mode() == "inline":
            for x, y, word, font in self.display_list:
                cmds.append(DrawText(x, y, word, font))
        return cmds

    def layout(self):
        """
        入力の DOM ツリーを再帰的にパースし、レイアウト情報を持つ各ブロック (BlockLayout) の重ね合わせであるレイアウトツリーとして再構築。
        """
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
            text_like_nodes = []
            for child in self.dom_node.children:
                if isinstance(child, Element) and child.tag == "head":
                    # head 要素の場合、表示しないのでとばす
                    continue
                # 子 DOM ノードの mode が inline の場合、1 つにまとめてからBlockLayout に渡す
                # HACK ここの if の書き方がイケてないから修正したい
                elif isinstance(child, Element) and child.tag not in BLOCK_ELEMENTS or isinstance(child, Text):
                    text_like_nodes.append(child)
                else:
                    # ここまででまとめた子 DOM ノードがあれば、BlockLayout に渡す
                    if text_like_nodes:
                        tmp_node = Element(tag="text-like-elements", attribute=None, parent=self.dom_node)
                        tmp_node.children.extend(text_like_nodes)
                        next = BlockLayout(
                            dom_node=tmp_node, 
                            parent=self, 
                            previous=previous, 
                            width=self.width,
                            font_size=self.font_size,
                        )
                        self.children.append(next)
                        previous = next
                        text_like_nodes = []
                    
                    next = BlockLayout(
                        dom_node=child, 
                        parent=self, 
                        previous=previous, 
                        width=self.width,
                        font_size=self.font_size,
                    )
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
            self.recurse(self.dom_node)  # 再帰的に DOM Tree をパース
            self.set_position()  # 残りの全ての self.line の単語を display_list に掃き出す

            self.height = self.cursor_y

        for child in self.children:
            child.layout()
        
        # 自ブロックの高さを子ブロックの高さの合計として計算
        if mode == "block":
            self.height = sum(
                [child.height for child in self.children]
            )
        
    def layout_mode(self):
        # HACK リファクタリング。inline と block の条件が交互になっているので綺麗に書き分ける
        # HACK description を追加して、inline と block の違いと役割を整理して説明する
        if isinstance(self.dom_node, Text):
            return "inline"
        elif any(
            [
                isinstance(child, Element) and child.tag in BLOCK_ELEMENTS for child in self.dom_node.children
            ]
        ):
            return "block"
        elif self.dom_node.children:
            return "inline"
        else:
            return "block"

    def recurse(self, dom_node: Union[Text, Element]):
        """ DOM ツリーの子ノードを再帰的にループし文字位置を計算。

        Args:
            dom_node (Union[Text, Element]): DOM ツリーのノード
        """
        if isinstance(dom_node, Text):
            self.set_text(dom_node)
        else:
            # タグオープン
            self.open_tag(dom_node)

            for child in dom_node.children:
                self.recurse(child)

            # タグクローズ
            self.close_tag(dom_node)

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

    def open_tag(self, dom_node: Element):
        # タグに沿って文字フォント更新
        if dom_node.tag == "b":
            self.font_weight = "bold"
        elif dom_node.tag == "i":
            self.font_style = "italic"
        elif dom_node.tag == "small":
            self.font_size -= 2
        elif dom_node.tag == "big":
            self.font_size += 4
        elif dom_node.tag == "br" or dom_node.tag == "br/" or dom_node.tag == "br /":
            self.set_position()
        elif dom_node.tag == "p":
            self.cursor_y += self.font_size
        elif dom_node.tag == "li":
            if dom_node.parent.tag == "ul" and self.previous == None:
                self.parent.x += 2 * self.font_size
                self.x += 2 * self.font_size
            bullet = "•"
            dom_node.children.insert(0, Text(bullet, dom_node))
        elif dom_node.tag == "h1":
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 3)
            self.font_weight = "bold"
            self.cursor_y += self.font_size/4
        elif dom_node.tag == "h2":
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 2)
            self.font_weight = "bold"
            self.cursor_y += self.font_size/4
        elif dom_node.tag == "h3":
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 1.5)
            self.font_weight = "bold"
            self.cursor_y += self.font_size/4
        elif dom_node.tag == "h4":
            self.font_size = self.tmp_font_size
            self.font_size = int(self.font_size * 1.1)
            self.font_weight = "bold"
            self.cursor_y += self.font_size/4
        elif dom_node.tag == "h5":
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 0.8)
            self.font_weight = "bold"
            self.cursor_y += self.font_size/4
        elif dom_node.tag == "h6":
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 0.5)
            self.font_weight = "bold"
            self.cursor_y += self.font_size/4

    def close_tag(self, dom_node: Element):
        # 閉タグに沿って文字フォントを戻す
        if dom_node.tag == "b":
            self.font_weight = "normal"
        elif dom_node.tag == "i":
            self.font_style = "roman"
        elif dom_node.tag == "small":
            self.font_size += 2
        elif dom_node.tag == "big":
            self.font_size -= 4
        elif dom_node.tag == "p":
            self.set_position()
            self.cursor_y += self.font_size
        elif dom_node.tag == "li":
            pass
        elif dom_node.tag == "h1":
            self.set_position()
            self.cursor_y += self.font_size/2
            self.font_size = self.tmp_font_size
            self.font_weight = "normal"
        elif dom_node.tag == "h2":
            self.set_position()
            self.cursor_y += self.font_size/2
            self.font_size = self.tmp_font_size
            self.font_weight = "normal"
        elif dom_node.tag == "h3":
            self.set_position()
            self.cursor_y += self.font_size/2
            self.font_size = self.tmp_font_size
            self.font_weight = "normal"
        elif dom_node.tag == "h4":
            self.set_position()
            self.cursor_y += self.font_size/2
            self.font_size = self.tmp_font_size
            self.font_weight = "normal"
        elif dom_node.tag == "h5":
            self.set_position()
            self.cursor_y += self.font_size/2
            self.font_size = self.tmp_font_size
            self.font_weight = "normal"
        elif dom_node.tag == "h6":
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


class DrawText:
    def __init__(self, x1, y1, text, font):
        """ BlockLayout に対応してブラウザ上で表示するテキスト。位置、表示文字、フォントを指定できる。

        Args:
            x1 (float): テキストの左端位置
            y1 (float): テキストの上端位置
            text (string): 表示するテキスト
            font (Font): フォント
        """
        self.left = x1
        self.top = y1
        self.text = text
        self.font = font
        self.bottom = y1 + font.metrics("linespace") # 底辺を定義。画面外の非描画条件に使用する。
        
    def execute(self, scroll, canvas):
        canvas.create_text(
            self.left, self.top - scroll,
            text=self.text,
            font=self.font,
            anchor='nw'
        )
        
class DrawRect:
    def __init__(self, x1, y1, x2, y2, color):
        """ BlockLayout に対応してブラウザ上で表示するボックス状のブロック。位置と背景色を指定できる。

        Args:
            x1 (float): ボックスの左端位置
            y1 (float): ボックスの上端位置
            x2 (float): ボックスの右端位置
            y2 (float): ボックスの下端位置
            color (string): 背景色
        """
        self.left = x1
        self.top = y1
        self.right = x2
        self.bottom = y2
        self.color = color

    def execute(self, scroll, canvas):
        canvas.create_rectangle(
            self.left, self.top - scroll,
            self.right, self.bottom - scroll,
            width=0, # デフォルトでは黒の縁取り線があるので、幅を 0 に設定し削除
            fill=self.color # 指定の色に塗りつぶす
        )