import socket
import ssl
import tkinter
import tkinter.font


class URL:
    def __init__(self, url) -> None:
        self.url = url
        
    def parse_url(self):
        scheme, url = self.url.split("://", 1)
        assert scheme in ["http", "https"], "Unknown scheme {}".format(scheme)

        if "/" not in url:
            url = url + "/"
        host, path = url.split("/", 1)
        
        # ポート番号指定があれば
        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)
        else:
            port = None
            
        return (scheme, host, "/" + path, port)

    def request(self):
        scheme, host, path, port = self.parse_url()
        
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        # HTTPS の場合ソケットを SSL でラップ
        if scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=host)
        
        # ポートを指定
        if port:
            pass
        elif scheme == "http":
            port = 80 
        elif scheme == "https":
            port = 443
        
        s.connect((host, port))

        s.send(
            "GET {} HTTP/1.0\r\n".format(path).encode("utf8") + "Host: {}\r\n\r\n".format(host).encode("utf8")
        )

        # read bits of response have already arrived
        response = s.makefile("r", encoding="utf8", newline="\r\n")

        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        assert status == "200", "{}: {}".format(
            status, 
            explanation
        )

        headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            headers[header.lower()] = value.strip()
            
        assert "transfer-encoding" not in headers
        assert "content-encoding" not in headers

        body = response.read()
        s.close()
        return headers, body
                
# ウィンドウの縦横幅
WIDTH, HEIGHT = 800, 600

class Browser:
    def __init__(self) -> None:
        # ウィンドウを作成
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width = WIDTH, height = HEIGHT)
        self.canvas.pack()    
        
        # 表示配置        
        self.layout = Layout()
        
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
        self.display_list = self.layout.parse(token_list=self.token_list)
        self.draw()
    
    def reduce(self, e):
        # 最小文字サイズ
        if self.layout.font_size > self.layout.minimum_font_size:
            # 文字サイズの更新
            self.layout.font_size -= 10
            # 文字位置の更新と再描画
            self.display_list = self.layout.parse(token_list=self.token_list)
            self.draw()
    
    def load(self, url):
        headers, body = URL(url).request()
        self.token_list = self.lex(body)
        self.display_list = self.layout.parse(token_list=self.token_list)
        # ウィンドウに表示
        self.draw()
        
class Text:
        def __init__(self, text) -> None:
            self.text = text
        
class Tag:
    def __init__(self, tag) -> None:
        self.tag = tag
        
class Layout:
    def __init__(self) -> None:        
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
            if self.cursor_x >= WIDTH - w: # 画面横幅を越えたら、改行
                self.cursor_y += font.metrics("linespace") * 1.25
                self.cursor_x = self.HSTEP

            self.display_list.append((self.cursor_x, self.cursor_y, word, font))
            self.cursor_x += w + font.measure(" ")
                
if __name__ == "__main__":
    import sys
    Browser().load(sys.argv[1])
    tkinter.mainloop()