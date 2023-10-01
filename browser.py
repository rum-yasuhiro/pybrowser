import tkinter

from url import URL
from html_parser import HTMLParser
from layout import Layout

                
# ウィンドウの縦横幅
WIDTH, HEIGHT = 800, 600

class Browser:
    def __init__(self) -> None:
        # ウィンドウを作成
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width = WIDTH, height = HEIGHT)
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
    def draw(self):
        self.canvas.delete("all")
        for cursor_x, cursor_y, c, font in self.display_list:
            # 画面外は描画しないことで高速化
            if cursor_y > self.scroll + HEIGHT: continue
            if cursor_y  + font.metrics("linespace") < self.scroll: continue
            
            # 描画
            self.canvas.create_text(
                cursor_x, 
                cursor_y - self.scroll, 
                text=c, 
                font=font,
                anchor='nw'
            )
    
    # ユーザーインタラクション
    def scroll_down(self, e):
        self.scroll += self.SCROLL_STEP
        self.draw()
    
    def scroll_up(self, e): 
        if self.scroll > 0:
            self.scroll -= self.SCROLL_STEP
            self.draw()
    
    def magnify(self, e):
        # TODO 最大文字サイズを決める
        # 文字サイズの更新
        self.document.font_size += 10
        # 文字位置の更新と再描画
        self.display_list = self.document.layout()
        self.draw()
    
    def reduce(self, e):
        # 最小文字サイズ
        if self.document.font_size > self.document.minimum_font_size:
            # 文字サイズの更新
            self.document.font_size -= 10
            # 文字位置の更新と再描画
            self.display_list = self.document.layout()
            self.draw()
    
    def load(self, url):
        headers, body = URL(url).request()
        self.dom = HTMLParser(body).parse()
        self.document = Layout(dom=self.dom, width=WIDTH, height=HEIGHT)
        self.display_list = self.document.layout()
        # ウィンドウに表示
        self.draw()
                
if __name__ == "__main__":
    import sys
    Browser().load(sys.argv[1])
    tkinter.mainloop()