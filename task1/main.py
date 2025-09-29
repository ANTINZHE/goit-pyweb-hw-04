from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import pathlib
import mimetypes
import socket
import json
from pathlib import Path
from datetime import datetime
import threading

STORAGE = Path("storage")
STORAGE.mkdir(exist_ok=True)
DATA_FILE = STORAGE / "data.json"

class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())

        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        print(data_dict)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(json.dumps(data_dict).encode("utf-8"), ("127.0.0.1", 5000))
        sock.close()

        self.send_response(302)
        self.send_header('Location', '/message')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

def run_udp_server(host="127.0.0.1", port=5000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"UDP сервер запущений {host}:{port}")

    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode("utf-8")
        print(f"Отримано від {addr}: {message}")

        try:
            data_dict = json.loads(message)
        except json.JSONDecodeError:
            continue

        # Читаємо старі дані
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                old_data = json.load(f)
        else:
            old_data = {}

        # Додаємо нові
        date_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        old_data[date_stamp] = data_dict

        # Записуємо назад
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(old_data, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    t1 = threading.Thread(target=run)
    t2 = threading.Thread(target=run_udp_server)
    t1.start()
    t2.start()

