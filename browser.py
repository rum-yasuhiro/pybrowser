import tkinter

from url import URL
from layout import Layout, Text, Tag

                
# ウィンドウの縦横幅
WIDTH, HEIGHT = 800, 600

class Browser:
    def __init__(self) -> None:
        # ウィンドウを作成
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width = WIDTH, height = HEIGHT)
        self.canvas.pack()    
        
        # 表示配置        
        self.layout = Layout(width=WIDTH, height=HEIGHT)
        
        # スクロール
        self.scroll = 0
        self.SCROLL_STEP = 18

        # ユーザーインタラクションのバインド
        self.window.bind("<Down>", self.scroll_down)
        self.window.bind("<Up>", self.scroll_up)
        self.window.bind("+", self.magnify)
        self.window.bind("-", self.reduce)

    # body の要素を解体し text に結合
    def lex(self, body):
        token_list = []
        text = ""
        in_tag = False
        for c in body:
            if c == "<":
                in_tag = True
                if text:
                    token_list.append(Text(text))
                text = ""
            elif c == ">":
                in_tag = False
                token_list.append(Tag(text))
                text = ""
            else:
                text += c
        if not in_tag and text:
            token_list.append(Text(text))
        return token_list
    
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
        # 文字サイズの更新
        self.layout.font_size += 10
        # 文字位置の更新と再描画
        self.display_list = self.layout.arrange(token_list=self.token_list)
        self.draw()
    
    def reduce(self, e):
        # 最小文字サイズ
        if self.layout.font_size > self.layout.minimum_font_size:
            # 文字サイズの更新
            self.layout.font_size -= 10
            # 文字位置の更新と再描画
            self.display_list = self.layout.arrange(token_list=self.token_list)
            self.draw()
    
    def load(self, url):
        headers, body = URL(url).request()
        self.token_list = self.lex(body)
        self.display_list = self.layout.arrange(token_list=self.token_list)
        # ウィンドウに表示
        self.draw()
                
if __name__ == "__main__":
    import sys
    Browser().load(sys.argv[1])
    tkinter.mainloop()