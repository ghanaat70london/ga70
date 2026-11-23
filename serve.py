"""Run the website on your own computer, forms included.

    python serve.py

Serves the site folder at http://localhost:8000. Every form and booking posts to a local stand in
for api/register.js, which prints the record it would send to GoHighLevel, so you can test the whole
site without Vercel. Press Ctrl+C to stop."""
import http.server, json, os, socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "site")
PORT = int(os.environ.get("PORT", "8000"))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=SITE, **k)

    def do_POST(self):
        if self.path.split("?")[0] != "/api/register":
            self.send_error(404)
            return
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode("utf-8", "replace")
        try:
            data = json.loads(body or "{}")
        except ValueError:
            data = {}
        ok = data.get("consent") == "yes"
        print("\nForm received, type", data.get("type"), "\n" + json.dumps(data, indent=1, ensure_ascii=False), flush=True)
        out = json.dumps({"ok": True} if ok else {"error": "Please tick the consent box."}).encode()
        self.send_response(200 if ok else 400)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def send_head(self):
        # clean URLs, as on Vercel: /tickets serves tickets.html, and a missing page shows 404.html
        path = self.path.split("?")[0]
        p = self.translate_path(path)
        if not os.path.exists(p) and os.path.exists(p + ".html"):
            self.path = path + ".html"
        elif not os.path.exists(p):
            self.path = "/404.html"
        return super().send_head()


socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Ghana at 70 UK running at http://localhost:{PORT}  (Ctrl+C to stop)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
