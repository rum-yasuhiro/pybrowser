from typing import Tuple
import socket
import ssl


class URL:
    def __init__(self, url: str) -> None:
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
        self.scheme, self.host, self.path, self.port = self.parse_url()

        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        # HTTPS の場合ソケットを SSL でラップ
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        # ポートを指定
        if self.port:
            pass
        elif self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        s.connect((self.host, self.port))

        s.send(
            "GET {} HTTP/1.0\r\n".format(self.path).encode("utf8")
            + "Host: {}\r\n\r\n".format(self.host).encode("utf8")
        )

        # read bits of response have already arrived
        response = s.makefile("r", encoding="utf8", newline="\r\n")

        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        assert status == "200", "{}: {}".format(status, explanation)

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

    def resolve(self, url: str) -> "URL":
        """相対 URL の場合に補完し完全 URL へ変換する

        （注） アノテーションは、PEP 673 に従い "URL" で指定
        https://docs.python.org/ja/3/library/typing.html#typing.Self

        Args:
            url (str): 補完したい URL 文字列

        Returns:
            URL: 補完した完全 URL の URL インスタンス
        """
        if "://" in url:  # スキーム、ホスト、パスなどを指定する通常の完全 URL の場合
            return URL(url)
        if not url.startswith("/"):  # / で始まらず、ファイル名のように解決されるパス相対 URL の場合
            dir, _ = self.path.rsplit("/", 1)
            while url.startswith("../"):  # 相対 URL の親ディレクトリ .. を解決
                _, url = url.split("/", 1)
                if "/" in dir:
                    dir, _ = dir.rsplit("/", 1)
            url = dir + "/" + url
        if url.startswith("//"):  # // で始まるスキーム相対 URL の場合
            return URL(self.scheme + ":" + url)
        else:  # / で始まるが、既存のスキームとホストを再利用するホスト相対 URL の場合
            return URL(self.scheme + "://" + self.host + ":" + str(self.port) + url)
