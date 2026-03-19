"""
Minimal backend to issue ephemeral OpenAI Realtime keys.
Run with: python server.py
Then start the Vite dev server: npm run dev (in my-voice-agent-project/)
"""

import os
import json
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/session":
            self._issue_ephemeral_key()
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self._send_cors_headers(200)
        self.end_headers()

    def _issue_ephemeral_key(self):
        if not OPENAI_API_KEY:
            self._json_response({"error": "OPENAI_API_KEY not set"}, 500)
            return

        payload = json.dumps({
            "session": {"type": "realtime", "model": "gpt-realtime"}
        }).encode()

        req = urllib.request.Request(
            "https://api.openai.com/v1/realtime/client_secrets",
            data=payload,
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
                self._json_response({"apiKey": data["value"]})
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            self._json_response({"error": error_body}, e.code)

    def _json_response(self, data, status=200):
        body = json.dumps(data).encode()
        self._send_cors_headers(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_cors_headers(self, status):
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "http://localhost:5173")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format, *args):
        print(f"[server] {self.address_string()} - {format % args}")


if __name__ == "__main__":
    port = 3001
    print(f"Backend running on http://localhost:{port}")
    print(f"API key set: {'yes' if OPENAI_API_KEY else 'NO — set OPENAI_API_KEY first'}")
    HTTPServer(("localhost", port), Handler).serve_forever()
