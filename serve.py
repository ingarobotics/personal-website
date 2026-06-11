#!/usr/bin/env python3
"""python3 serve.py  →  http://localhost:8000 (falls back to next free port)"""
import http.server, socketserver, os, sys, json

os.chdir(os.path.dirname(os.path.abspath(__file__)))

CONTENT_FILE = 'content.js'
PREFIX = 'window.CONTENT = '


def read_content():
    try:
        with open(CONTENT_FILE) as f:
            text = f.read().strip()
        return json.loads(text[len(PREFIX):].rstrip(';').strip())
    except Exception:
        return {}


def write_content(data):
    tmp = CONTENT_FILE + '.tmp'
    with open(tmp, 'w') as f:
        f.write(PREFIX + json.dumps(data, indent=2) + ';\n')
    os.replace(tmp, CONTENT_FILE)


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      '.md': 'text/plain'}

    def end_headers(self):
        # Never cache during local development — always serve fresh files
        self.send_header('Cache-Control', 'no-store, max-age=0')
        super().end_headers()

    def translate_path(self, path):
        # Clean-URL fallback: /writing → writing.html, /sequence → sequence.html
        # Mirrors Vercel's cleanUrls behavior so links work the same locally.
        full = super().translate_path(path)
        if (not os.path.exists(full)
                and not full.endswith('/')
                and not full.endswith('.html')
                and os.path.exists(full + '.html')):
            return full + '.html'
        return full

    def do_POST(self):
        if self.path != '/save':
            self.send_error(404)
            return
        try:
            length = int(self.headers.get('Content-Length', 0))
            payload = json.loads(self.rfile.read(length))
            page = os.path.basename(payload['page'])  # strip any path
            content = read_content()
            content[page] = payload['data']
            write_content(content)
        except Exception as e:
            self.send_error(400, str(e))
            return
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"ok":true}')


handler = Handler


class Server(socketserver.TCPServer):
    allow_reuse_address = True  # avoids "Address already in use" on restart


def run(start_port=8000, tries=10):
    for port in range(start_port, start_port + tries):
        try:
            httpd = Server(('', port), handler)
        except OSError:
            continue
        with httpd:
            print(f'→  http://localhost:{port}   (Ctrl+C to stop)')
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print('\nstopped.')
            return
    sys.exit(f'No free port in range {start_port}-{start_port + tries - 1}.')


if __name__ == '__main__':
    run()
