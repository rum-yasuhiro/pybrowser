import socket
import ssl
import tkinter

class Browser:
    def __init__(self) -> None:
        # ウィンドウを作成
        self.WIDTH, self.HEIGHT = 800, 600
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width = self.WIDTH, height = self.HEIGHT)
        self.canvas.pack()
        
        # 文字の縦横幅
        self.HSTEP, self.VSTEP = 13, 18

    
    def parse_url(self, url):
        scheme, url = url.split("://", 1)
        assert scheme in ["http", "https"], "Unknown scheme {}".format(scheme)

        if "/" not in url:
            url = url + "/"
        host, path = url.split("/", 1)
        return (scheme, host, "/" + path)

    def request(self, url, port=None): # テスト用にポート番号を指定できる
        scheme, host, path = self.parse_url(url)
        
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
        cursor_x, cursor_y = self.HSTEP, self.VSTEP
        for c in text:
            display_list.append((cursor_x, cursor_y, c))
            cursor_x += self.HSTEP
            # 画面横幅を越えたら、改行
            if cursor_x >= self.WIDTH - self.HSTEP:
                cursor_y += self.VSTEP
                cursor_x = self.HSTEP
        return display_list
    
    # canvas に text を描画
    def draw(self, display_list):
        for cursor_x, cursor_y, c in display_list:
            self.canvas.create_text(cursor_x, cursor_y, text=c)
    
    def load(self, url):
        headers, body = self.request(url)
        text = self.lex(body)
        display_list = self.layout(text)
        # ウィンドウに表示
        self.draw(display_list)
        
    
if __name__ == "__main__":
    import sys
    Browser().load(sys.argv[1])
    tkinter.mainloop()