import tkinter
import tkinter.font

from html_parser import Text
        
class Layout:
    def __init__(self, width=800, height=600) -> None:        
        # ウィンドウプロパティ
        self.width = width
        self.height = height
        
        # 文字プロパティ
        self.font_family = None
        self.font_size = 16
        self.minimum_font_size = 16
        self.tmp_font_size = self.font_size # フォントサイズ保持のための一時変数
        self.font_weight = "normal"
        self.font_style = "roman"
        self.font_cache = {} # フォントをキャッシュすることで高速化
        
        # 配置
        self.HSTEP, self.VSTEP = 13, 18 # 描画開始位置の縦横幅
        # 改行ステータスを初期化
        self.newline = False
        self.new_paragraph = False
        
    def arrange(self, dom):
        self.line = [] # 文字位置修正のためのバッファ
        self.cursor_x, self.cursor_y, self.baseline = self.HSTEP, self.VSTEP, self.VSTEP

        # 再帰的に DOM Tree を解析する
        self.recurse(dom)

        # テキスト描画位置を計算
        display_list = self.set_position()
        return display_list
    
    def recurse(self, dom):
        if isinstance(dom, Text):
            self.set_text(dom)
        else:
            # タグオープン
            self.open_tag(tag=dom.tag)
            
            for child in dom.child:
                self.recurse(child)
                
            # タグクローズ
            self.close_tag(tag=dom.tag)
                
    def set_text(self, text_node):
        font = self.get_font(
            font_family=self.font_family,
            font_size=self.font_size,
            font_weight=self.font_weight,
            font_style=self.font_style
        )
        for word in text_node.text.split():
            self.line.append((word, font, self.newline, self.new_paragraph))
            # 改行ステータスを初期化
            self.newline = False
            self.new_paragraph = False

    def get_font(self, font_family, font_size, font_weight, font_style):
        """フォントをキャッシュすることで高速化"""
        key = (font_family, font_size, font_weight, font_style)
        if key not in self.font_cache:
            font = tkinter.font.Font( 
                family = font_family, 
                size = font_size, 
                weight = font_weight,
                slant=font_style
            )
            self.font_cache[key] = font
        return self.font_cache[key]
    
    def open_tag(self, tag):
        # タグに沿って文字フォント更新
        if tag == "b":
            self.font_weight = "bold"
        elif tag == "i":
            self.font_style="italic"
        elif tag == "small":
            self.font_size -=2
        elif tag == "big":
            self.font_size +=4
        elif tag == "br" or tag == "br/" or tag == "br /":
            self.newline = True
        elif tag == "p":
            self.new_paragraph = True
        elif tag == "h1":
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 3)
            self.newline = True
        elif tag == "h2":
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 2)
            self.newline = True
        elif tag == "h3":
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 1.5)
            self.newline = True
        elif tag == "h4":
            self.font_size = self.tmp_font_size
            self.font_size = int(self.font_size * 1.1)
            self.newline = True
        elif tag == "h5":
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 0.8)
            self.newline = True
        elif tag == "h6":
            self.tmp_font_size = self.font_size
            self.font_size = int(self.font_size * 0.5)
            self.newline = True
    
    def close_tag(self, tag):
        # 閉タグに沿って文字フォントを戻す
        if tag == "b":
            self.font_weight = "normal"
        elif tag == "i":
            self.font_style="roman"
        elif tag == "small":
                self.font_size +=2
        elif tag == "big":
            self.font_size -=4
        elif tag == "p":
            self.new_paragraph = True
        elif tag == "h1":
            self.font_size = self.tmp_font_size
            self.new_paragraph = True
        elif tag == "h2":
            self.font_size = self.tmp_font_size
            self.new_paragraph = True
        elif tag == "h3":
            self.font_size = self.tmp_font_size
            self.new_paragraph = True
        elif tag == "h4":
            self.font_size = self.tmp_font_size
            self.new_paragraph = True
        elif tag == "h5":
            self.font_size = self.tmp_font_size
            self.new_paragraph = True
        elif tag == "h6":
            self.font_size = self.tmp_font_size
            self.new_paragraph = True
        
    def set_position(self):
        """
        描画位置計算手順
        1. 先にバッファに同じ行のテキストを追加
        2. 改行のタイミングでバッファの中で最も背の高いフォントに合わせて、描画位置を計算
        3. バッファをクリアして次の行のテキストをバッファに追加 (2に戻る)
        """
        display_list = []
        _buffer=[]
        for word, font, newline, new_paragraph in self.line:
            
            w = font.measure(word)
            # 改行条件
            if (self.cursor_x >= self.width - w and self.width > w) or newline or new_paragraph: 
                # バッファ中のテキストで最も背の高いフォントにベースラインを揃える
                display_list = self.set_baseline(display_list, _buffer)
                # 縦横位置とバッファを初期化
                _buffer=[]
                self.cursor_x = self.HSTEP         
                self.baseline += self.max_ascent * 1.25
            # 段落の場合縦スペースを追加
            if new_paragraph:
                self.baseline += self.VSTEP
        
            _buffer.append((self.cursor_x, word, font))
            self.cursor_x += w + font.measure(" ")
        
        # バッファ中の残りの文字も追加    
        display_list = self.set_baseline(display_list, _buffer)
        
        return display_list
        
    def set_baseline(self, display_list, buffer):
        """バッファ中のテキストで最も背の高いフォントに表示位置のベースラインを揃えてdisplay_listに追加"""
        self.max_ascent = max([_font.metrics("ascent") for _, _, _font in buffer])
        for _x, _word, _font in buffer:
            self.cursor_y = self.baseline + (self.max_ascent - _font.metrics("ascent")) * 1.25
            display_list.append((_x, self.cursor_y, _word, _font))
        return display_list