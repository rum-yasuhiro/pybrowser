from typing import Tuple
import socket
import ssl

class URL:
    def __init__(self, url:str) -> None:
        self.url = url
        
    def parse_url(self) -> Tuple[str, str, str, int]:
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

    def request(self) -> Tuple[dict, str]:
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