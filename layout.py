import tkinter
import tkinter.font
        
class Layout:
    def __init__(self, width=800, height=600) -> None:        
        # ウィンドウプロパティ
        self.width = width
        self.height = height
        
        # 文字プロパティ
        self.font_family = None
        self.font_size = 16
        self.minimum_font_size = 16
        self.font_weight = "normal"
        self.font_style = "roman"
        
        # 配置
        self.HSTEP, self.VSTEP = 13, 18 # 描画開始位置の縦横幅
        self.newline = False
        self.new_paragraph = False
        
    def parse(self, token_list):
        self.line = [] # 文字位置修正のためのバッファ
        self.cursor_x, self.cursor_y, self.baseline = self.HSTEP, self.VSTEP, self.VSTEP
        for token in token_list:
            self._parse(token)
        return self.set_position()
            
    def _parse(self, token):
        if isinstance(token, Text):
            self.set_text(token)
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
            elif token.tag == "small":
                self.font_size -=2
            elif token.tag == "/small":
                    self.font_size +=2
            elif token.tag == "big":
                self.font_size +=4
            elif token.tag == "/big":
                self.font_size -=4
            elif token.tag == "br" or token.tag == "br/" or token.tag == "br /":
                self.newline = True
            elif token.tag == "p":
                self.new_paragraph = True
            elif token.tag == "/p":
                self.new_paragraph = True
    
    def set_text(self, token):
        font = tkinter.font.Font( 
            family = self.font_family, 
            size = self.font_size, 
            weight = self.font_weight,
            slant=self.font_style
        )
        for word in token.text.split():
            self.line.append((word, font, self.newline, self.new_paragraph))
            self.newline = False
            self.new_paragraph = False
                
    def set_position(self):
        display_list = []
        max_ascent = max([font.metrics("ascent") for _, font, _, _ in self.line])    
        for word, font, newline, new_paragraph in self.line:
            # 文字表示位置
            w = font.measure(word)
            if self.cursor_x >= self.width - w: # 画面横幅を越えたら、改行
                self.baseline += max_ascent * 1.25
                self.cursor_x = self.HSTEP
            elif newline == True:
                self.baseline += max_ascent * 1.25
                self.cursor_x = self.HSTEP
            elif new_paragraph == True:
                self.baseline += max_ascent * 1.25 + self.VSTEP
                self.cursor_x = self.HSTEP
            else:
                pass
            
            # ベースラインに揃えてwordを描画するために cursor_x と cursor_y を追加する
            self.cursor_y = self.baseline + (max_ascent - font.metrics("ascent")) * 1.25
            display_list.append((self.cursor_x, self.cursor_y, word, font))
            self.cursor_x += w + font.measure(" ")
            
        return display_list
        
class Text:
        def __init__(self, text) -> None:
            self.text = text
        
class Tag:
    def __init__(self, tag) -> None:
        self.tag = tag