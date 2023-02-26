from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import json
from datetime import datetime


DIR = pathlib.Path()
class HttpHandler(BaseHTTPRequestHandler):
    def write_data(self, data):
        with open(DIR.joinpath('storage\data.json')) as f:
            if f:
                data_in_file = json.load(f)

        with open(DIR.joinpath('storage\data.json'), 'w', encoding='utf-8') as file:
            if data_in_file:
                data_in_file.update(data)
                json.dump({str(datetime.now()): data_in_file}, file, ensure_ascii=False)
            else:
                json.dump({str(datetime.now()): data}, file, ensure_ascii=False)



    def do_POST(self):
        body = self.rfile.read(int(self.headers.get('Content-Length')))
        body = urllib.parse.unquote_plus(body.decode())
        payload = {key: value for key, value in [el.split('=') for el in body.split('&')]}
        self.write_data(payload)
        print(payload)

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


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 8000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()