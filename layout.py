import tkinter
import tkinter.font
        
class Layout:
    def __init__(self, width=800, height=600) -> None:        
        # ウィンドウプロパティ
        self.width = width
        self.height = height
        
        # 文字プロパティ
        self.HSTEP, self.VSTEP = 0, 0 # 描画開始位置の縦横幅
        self.font_family = None
        self.font_size = 16
        self.minimum_font_size = 16
        self.font_weight = "normal"
        self.font_style = "roman"
        
    def parse(self, token_list):
        self.display_list = []
        self.cursor_x, self.cursor_y = self.HSTEP, self.VSTEP
        for token in token_list:
            self._parse(token)
        return self.display_list
            
    def _parse(self, token):
        if isinstance(token, Text):
            self.word(token)
        else:
            # タグに沿って文字フォント更新
            if token.tag == "b":
                self.font_weight = "bold"
            elif token.tag == "/b":
                self.font_weight = "normal"
            elif token.tag == "i":
                self.font_style="italic"
            elif token.tag == "/i":
                self.font_style="roman"

    def word(self, token):
        font = tkinter.font.Font( 
            family = self.font_family, 
            size = self.font_size, 
            weight = self.font_weight,
            slant=self.font_style
        )
        for word in token.text.split():            
            # 文字表示位置
            w = font.measure(word)
            if self.cursor_x >= self.width - w: # 画面横幅を越えたら、改行
                self.cursor_y += font.metrics("linespace") * 1.25
                self.cursor_x = self.HSTEP

            self.display_list.append((self.cursor_x, self.cursor_y, word, font))
            self.cursor_x += w + font.measure(" ")
            

class Text:
        def __init__(self, text) -> None:
            self.text = text
        
class Tag:
    def __init__(self, tag) -> None:
        self.tag = tag