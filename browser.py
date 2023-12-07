from typing import Union, Optional, List, Tuple
import tkinter

from url import URL
from html_parser import HTMLParser
from layout import DocumentLayout, BlockLayout

# ウィンドウの縦横幅
WIDTH, HEIGHT = 800, 600


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
        headers, body = URL(url).request()
        self.dom_node = HTMLParser(body).parse()
        self.document = DocumentLayout(dom_node=self.dom_node, width=WIDTH)
        self.document.layout()
        self.display_list = []
        layout_tree(self.document, self.display_list)
        # ウィンドウに表示
        self.draw()


# HACK display_list をクラスとして定義する。この変数の目的を明確にする。
# HACK description を追加する
def layout_tree(layout_object: Union[DocumentLayout, BlockLayout], display_list: list):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        layout_tree(child, display_list)


if __name__ == "__main__":
    import sys

    Browser().load(sys.argv[1])
    tkinter.mainloop()
