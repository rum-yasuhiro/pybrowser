import socket
import ssl
import tkinter


class URL:
    def __init__(self, url) -> None:
        self.url = url
        
    def parse_url(self):
        scheme, url = self.url.split("://", 1)
        assert scheme in ["http", "https"], "Unknown scheme {}".format(scheme)

        if "/" not in url:
            url = url + "/"
        host, path = url.split("/", 1)
        return (scheme, host, "/" + path)

    def request(self, port=None): # テスト用にポート番号を指定できる
        scheme, host, path = self.parse_url()
        
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

# 文字の縦横幅
HSTEP, VSTEP = 13, 18

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

    # body の要素を解体し text に結合
    def lex(self, body):
        in_angle = False
        text=""
        for c in body:
            if c == "<":
                in_angle = True
            elif c == ">":
                in_angle = False
            elif not in_angle:
                text += c
        return text
    
    # ページ座標を計算
    def layout(self, text):
        display_list = []
        cursor_x, cursor_y = HSTEP, VSTEP
        for c in text:
            display_list.append((cursor_x, cursor_y, c))
            cursor_x += HSTEP
            # 画面横幅を越えたら、改行
            if cursor_x >= WIDTH - HSTEP:
                cursor_y += VSTEP
                cursor_x = HSTEP
        return display_list
    
    # canvas に text を描画
    def draw(self):
        self.canvas.delete("all")
        for cursor_x, cursor_y, c in self.display_list:
            # 画面外は描画しないことで高速化
            if cursor_y > self.scroll + HEIGHT: continue
            if cursor_y + VSTEP < self.scroll: continue
            
            # 描画
            self.canvas.create_text(cursor_x, cursor_y - self.scroll, text=c)
    
    # ユーザーインタラクション
    def scroll_down(self, e):
        self.scroll += self.SCROLL_STEP
        self.draw()
    
    def scroll_up(self, e): 
        if self.scroll > 0:
            self.scroll -= self.SCROLL_STEP
            self.draw()
    
    def load(self, url):
        headers, body = URL(url).request()
        text = self.lex(body)
        self.display_list = self.layout(text)
        # ウィンドウに表示
        self.draw()
        
    
if __name__ == "__main__":
    import sys
    Browser().load(sys.argv[1])
    tkinter.mainloop()