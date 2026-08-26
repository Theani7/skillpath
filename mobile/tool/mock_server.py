"""Minimal mock of the SkillPath FastAPI for emulator smoke tests.

Serves only the endpoints the Flutter app touches at startup and while
navigating tabs. Run:  python3 tool/mock_server.py [port]
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

USER = {"role": "user", "full_name": "Test User", "username": "tester"}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload, cookies=()):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        for c in cookies:
            self.send_header("Set-Cookie", c)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authed(self):
        return "skillpath_access=" in self.headers.get("Cookie", "")

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n).decode()
        if self.path == "/api/auth/login":
            form = parse_qs(raw)
            if (
                form.get("username", [""])[0] == "tester"
                and form.get("password", [""])[0] == "secret123"
            ):
                self._send(
                    200,
                    USER,
                    cookies=[
                        "skillpath_access=mock-access; Path=/; Max-Age=1800",
                        "skillpath_refresh=mock-refresh; Path=/api/auth; Max-Age=2592000",
                    ],
                )
            else:
                self._send(401, {"detail": "Incorrect username or password"})
        elif self.path == "/api/auth/logout":
            self._send(200, {"message": "Logged out successfully"})
        elif self.path == "/api/auth/refresh":
            self._send(401, {"detail": "Invalid refresh token"})
        else:
            self._send(404, {"detail": "not found"})

    def do_GET(self):
        base = self.path.split("?")[0]
        if base == "/api/auth/me":
            if not self._authed():
                self._send(401, {"detail": "Not authenticated"})
            else:
                self._send(200, USER)
            return
        table = {
            "/api/job-roles": {"roles": ["Software Engineer", "Data Scientist"]},
            "/api/user/latest-analysis": {"found": False},
            "/api/user/history": {"history": []},
            "/api/mock-interview": {"roles": ["Software Engineer"]},
            "/api/user/roadmap-progress": {"progress": {}},
        }
        if base in table:
            self._send(200, table[base])
        else:
            self._send(404, {"detail": "not found"})

    def log_message(self, fmt, *args):
        print("[mock]", fmt % args, flush=True)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
