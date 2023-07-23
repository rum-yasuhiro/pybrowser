import socket


def parse_url(url):
    scheme, url = url.split("://", 1)
    if "/" not in url:
        url = url + "/"
    host, path = url.split("/", 1)
    return (scheme, host, "/" + path)

def request(url):
    scheme, host, path = parse_url(url)
    
    s = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_STREAM,
        proto=socket.IPPROTO_TCP,
    )
    s.connect((host, 80))

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
