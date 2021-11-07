# -*- coding: utf-8 -*-
# !/usr/bin/env python
from http.server import HTTPServer, BaseHTTPRequestHandler


class RequestHandler(BaseHTTPRequestHandler):
    @staticmethod
    def api_get(data):
        api_get_result = 'What are you doing here?'
        return api_get_result

    @staticmethod
    def api_download(data):
        api_get_result = 'This is Pythooooon!!!'
        return api_get_result

    def do_POST(self):
        if self.path != '/api/upload':
            payload_size = int(self.headers['Content-Length'])
            payload = self.rfile.read(payload_size)

            self.send_response(200, 'OK '+str(payload))
            self.end_headers()
            self.wfile.write(payload)

    def do_GET(self):
        send_uri = self.path
        self.send_response(200, 'OK')
        self.end_headers()
        if send_uri == '/api/get':
            self.wfile.write(bytes(self.api_get(send_uri), 'UTF-8'))
        elif send_uri == '/api/download':
            self.wfile.write(bytes(self.api_download(send_uri), 'UTF-8'))

    def do_DELETE(self):
        self.send_response(200, 'Oh my God! They killed Kenny!')
        self.end_headers()


if __name__ == "__main__":
    server = HTTPServer(('127.0.0.1', 10001), RequestHandler)
    server.serve_forever()
