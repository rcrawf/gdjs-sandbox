#!/usr/bin/env python3
# Claude Code proxy for gdjs-sandbox
# Usage: python3 proxy.py
# Then open index.html and select "Claude Code (local)" in the AI panel.

import json
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 3001


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress default access log noise

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        try:
            body = json.loads(self.rfile.read(length))
        except Exception:
            self.send_response(400)
            self._cors()
            self.end_headers()
            return

        prompt = body.get('prompt', '')
        system = body.get('system', '')
        full_prompt = f"{system}\n\n{prompt}" if system else prompt

        try:
            result = subprocess.run(
                ['claude', '-p', full_prompt],
                capture_output=True,
            )
            output = result.stdout
            if result.returncode != 0 and not output:
                err = result.stderr.decode(errors='replace')
                output = f'[claude error: {err}]'.encode()
        except FileNotFoundError:
            output = b"Error: 'claude' not found. Is Claude Code installed and on PATH?"
        except Exception as e:
            output = f'Error: {e}'.encode()

        self.send_response(200)
        self._cors()
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(output)))
        self.end_headers()
        self.wfile.write(output)

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')


if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', PORT), Handler)
    print(f'Claude Code proxy listening on http://127.0.0.1:{PORT}')
    print('Open gdjs-sandbox/index.html and select "Claude Code (local)" in the AI panel.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
