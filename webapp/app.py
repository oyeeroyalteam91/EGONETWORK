from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer


class AZAIWebApp(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        html = """
        <!doctype html>
        <html>
        <head>
            <meta charset='utf-8'>
            <meta name='viewport' content='width=device-width, initial-scale=1'>
            <title>AZAI Dashboard</title>
            <style>
                body { background:#050505; color:#f5d27a; font-family:Arial,sans-serif; padding:30px; }
                .card { border:1px solid #8b6b22; border-radius:18px; padding:24px; max-width:760px; margin:auto; }
                h1 { margin-top:0; }
                p { color:#f2f2f2; line-height:1.6; }
                code { color:#f5d27a; }
            </style>
        </head>
        <body>
            <div class='card'>
                <h1>AZAI Dashboard</h1>
                <p>EGO NETWORK control panel placeholder.</p>
                <p>Future modules: verification, group settings, leaderboard, saved pics, warning records, and owner tools.</p>
                <p>Set <code>WEBAPP_URL</code> to your public deployment URL after hosting.</p>
            </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = HTTPServer((host, port), AZAIWebApp)
    server.serve_forever()


if __name__ == "__main__":
    run()
