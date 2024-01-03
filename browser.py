from typing import Union, Optional, List, Tuple
import tkinter

from url import URL
from html_parser import HTMLParser, Element, Text
from css_parser import style, CSSParser
from layout import layout_tree, DocumentLayout, BlockLayout

# ウィンドウの縦横幅
WIDTH, HEIGHT = 800, 600

# デフォルトのスタイルシート
DEFAULT_STYLE_SHEET = CSSParser(open("browser.css").read()).parse()


class Browser:
    def __init__(self) -> None:
        # ウィンドウを作成
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()

        # スクロール
        self.scroll = 0
        self.SCROLL_STEP = 18

        # ユーザーインタラクションのバインド
        self.window.bind("<Down>", self.scroll_down)
        self.window.bind("<Up>", self.scroll_up)
        self.window.bind("+", self.magnify)
        self.window.bind("-", self.reduce)

    # canvas に描画
    def draw(self):  # HACK description 追加
        self.canvas.delete("all")
        for cmds in self.display_list:
            # 画面外は描画しないことで高速化
            if cmds.top > self.scroll + HEIGHT: continue
            if cmds.bottom < self.scroll: continue
            # 描画
            cmds.execute(self.scroll, self.canvas)

    # ユーザーインタラクション
    def scroll_down(self, e):
        max_y = max(self.document.height + 2*self.document.VSTEP - HEIGHT, 0)
        if self.scroll < max_y: # ページ最下層よりも下にスクロールしない条件
            self.scroll += self.SCROLL_STEP
        self.draw()

    def scroll_up(self, e):
        if self.scroll > 0: # ページ最上部よりも上にスクロールしない条件
            self.scroll -= self.SCROLL_STEP
            self.draw()

    def magnify(self, e):
        # 最大文字サイズ以下の場合、フォントサイズ拡大
        if self.document.font_size < self.document.maximum_font_size:
            # フォントサイズとレイアウトツリーの更新
            self.document = DocumentLayout(
                dom_node=self.dom_node,
                width=WIDTH,
                font_size=self.document.font_size
            )
            self.document.font_size += 4
            # 文字位置の更新と再描画
            self.document.layout()
            self.display_list = []
            layout_tree(self.document, self.display_list)
            self.draw()

    def reduce(self, e):
        # 最小文字サイズ以上の場合、フォントサイズ縮小
        if self.document.font_size > self.document.minimum_font_size:
            # フォントサイズとレイアウトツリーの更新
            self.document = DocumentLayout(
                dom_node=self.dom_node,
                width=WIDTH,
                font_size=self.document.font_size
            )
            self.document.font_size -= 4
            # 文字位置の更新と再描画
            self.document.layout()
            self.display_list = []
            layout_tree(self.document, self.display_list)
            self.draw()

    def load(self, url: str):
        url = URL(url)
        headers, body = url.request()
        self.dom_node = HTMLParser(body).parse()

        # ブラウザのデフォルトスタイルシートを取得
        rules = DEFAULT_STYLE_SHEET.copy()

        # リンクされたスタイルシートがあれば URL から取得し、適用
        links = [
            node.attribute["href"]
            for node in tree_to_list(self.dom_node, [])
            if isinstance(node, Element)
            and node.tag == "link"
            and node.attribute.get("rel") == "stylesheet"
            and "href" in node.attribute
        ]
        for link in links:
            try:
                _, body = url.resolve(link).request()
            except:
                continue
            rules.extend(CSSParser(body).parse())
        style(self.dom_node, rules)

        # DOM 要素を表示形式に変換
        self.document = DocumentLayout(dom_node=self.dom_node, width=WIDTH)
        self.document.layout()
        self.display_list = []
        layout_tree(self.document, self.display_list)

        # ウィンドウに表示
        self.draw()


def tree_to_list(
    tree: Union[DocumentLayout, BlockLayout, Element, Text], list: list
) -> list:
    """再帰的に、木構造オブジェクトを一次元配列に変換するヘルパー関数

    Args:
        tree (Union[DocumentLayout, BlockLayout, Element, Text]): 木構造を持つオブジェクト
        list (list): 一次元配列

    Returns:
        list: 木構造オブジェクトを再帰的に一次元配列に変換したもの
    """
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list


if __name__ == "__main__":
    import sys

    Browser().load(sys.argv[1])
    tkinter.mainloop()
