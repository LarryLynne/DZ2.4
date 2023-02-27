from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import json
from datetime import datetime
import socket
from threading import Thread


SOCKET_IP = '127.0.0.1'
SOCKET_PORT = 5000
DIR = pathlib.Path()
class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers.get('Content-Length')))
        send_data_to_socket(body)
        self.send_response(302)
        self.send_header('Location', '/message.html')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message.html':
            self.send_html_file('message.html')
        elif pr_url.path == '/logo.png':
            self.send_html_file('logo.png')
        elif pr_url.path == '/style.css':
            self.send_html_file('style.css')    
        else:
            self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        mt, *rest = mimetypes.guess_type(filename)
        if mt:
            self.send_header('Content-type', mt)
        else:
            self.send_header('Content-type', 'text/plain')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())


def write_data(data):
    with open(DIR.joinpath('storage\data.json')) as f:
        if f:
            data_in_file = json.load(f)

    with open(DIR.joinpath('storage\data.json'), 'w', encoding='utf-8') as file:
        if data_in_file:
            data_in_file.update(data)
            json.dump({str(datetime.now()): data_in_file}, file, ensure_ascii=False)
        else:
            json.dump({str(datetime.now()): data}, file, ensure_ascii=False)


def send_data_to_socket(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, (SOCKET_IP, SOCKET_PORT))
    sock.close()


def run_socket_server(ip=SOCKET_IP, port=SOCKET_PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    try:
        while True:
            data, address = sock.recvfrom(1024)
            data = urllib.parse.unquote_plus(data.decode())
            payload = {key: value for key, value in [el.split('=') for el in data.split('&')]}
            print(payload)
            write_data(payload)
    except KeyboardInterrupt:
        sock.close()


def run_http_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 8000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def run():
    http_server = Thread(target=run_http_server)
    socket_sever = Thread(target=run_socket_server)
    http_server.start()
    socket_sever.start()



if __name__ == '__main__':
    run()