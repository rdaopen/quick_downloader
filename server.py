
import threading
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import queue

class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server, url_queue):
        self.url_queue = url_queue
        super().__init__(request, client_address, server)

    def do_POST(self):
        if self.path == '/add':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                url = data.get('url')
                
                if url:
                    self.url_queue.put(url)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*') # Allow from extension
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'ok', 'message': 'URL received'}).encode('utf-8'))
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'error', 'message': 'No URL provided'}).encode('utf-8'))
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': 'Invalid JSON'}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        pass # Suppress logging

class BackgroundServer(threading.Thread):
    def __init__(self, url_queue, port=6006):
        super().__init__()
        self.url_queue = url_queue
        self.port = port
        self.daemon = True # Kill server when app closes
        self.server = None

    def run(self):
        def handler_factory(*args, **kwargs):
            return RequestHandler(*args, **kwargs, url_queue=self.url_queue)

        try:
            self.server = HTTPServer(('localhost', self.port), handler_factory)
            print(f"Server started on port {self.port}")
            self.server.serve_forever()
        except OSError as e:
            print(f"Could not start server on port {self.port}: {e}")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
