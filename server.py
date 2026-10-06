#!/usr/bin/env python3
"""
Localhost Web GUI Server for Project-Based Learning.
Serves the web application and interactive REST APIs.
Requires Python 3 stdlib only (zero dependencies).
"""

import http.server
import socketserver
import os
import sys
import json
import urllib.parse

PORT = 5050
HOST = "localhost"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
DATA_FILE = os.path.join(WEB_DIR, "data", "projects.json")

# Ensure projects.json exists
if not os.path.exists(DATA_FILE):
    print("[INFO] projects.json not found, generating now from README.md...")
    try:
        from scripts.parse_to_json import parse_readme_to_projects
        parse_readme_to_projects()
    except Exception as e:
        print(f"[ERROR] Failed to generate projects.json: {e}")

class PBLRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler serving the web portal and JSON APIs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # API Endpoints
        if path == "/api/health":
            self.send_json({"status": "ok", "app": "Project-Based Learning Explorer", "port": PORT})
            return

        if path == "/api/stats":
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.send_json(data.get("metadata", {}))
            else:
                self.send_json({"error": "Data file not found"}, status=404)
            return

        if path == "/api/projects":
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                projects = data.get("projects", [])

                # Optional filtering
                lang = query.get("lang", [None])[0]
                diff = query.get("diff", [None])[0]
                q = query.get("q", [None])[0]

                if lang and lang != "all":
                    projects = [p for p in projects if p["language"].lower() == lang.lower()]
                if diff and diff != "all":
                    try:
                        diff_val = int(diff)
                        projects = [p for p in projects if p["difficulty"] == diff_val]
                    except ValueError:
                        pass
                if q:
                    q_lower = q.lower()
                    projects = [
                        p for p in projects
                        if q_lower in p["title"].lower() or
                           q_lower in p.get("summary_vi", "").lower() or
                           any(q_lower in t.lower() for t in p.get("tags", []))
                    ]

                self.send_json({
                    "count": len(projects),
                    "total": len(data.get("projects", [])),
                    "projects": projects
                })
            else:
                self.send_json({"error": "Data file not found"}, status=404)
            return

        # Serve static web directory
        if path == "/" or path == "/index.html":
            self.path = "/index.html"
            return super().do_GET()

        return super().do_GET()

    def send_json(self, data, status=200):
        content = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        # Keep logs clean and quiet
        pass

def find_available_port(start_port=5050):
    import socket
    port = start_port
    while port < start_port + 50:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
        port += 1
    return start_port

def run_server():
    global PORT
    PORT = find_available_port(5050)
    server_address = (HOST, PORT)

    # Use ThreadingTCPServer to handle concurrent requests
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(server_address, PBLRequestHandler) as httpd:
        url = f"http://{HOST}:{PORT}"
        print("=" * 60)
        print(" PROJECT-BASED LEARNING EXPLORER (LOCAL GUI)")
        print("=" * 60)
        print(f" [OK] Server dang chay tai: {url}")
        print(f" [OK] Truy cap trinh duyet: {url}")
        print(f" [OK] Thu muc web: {WEB_DIR}")
        print(" Nhan Ctrl+C de dung server.")
        print("=" * 60)
        sys.stdout.flush()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[INFO] Dang dung server...")
            httpd.server_close()
            print("[OK] Server da dung.")

if __name__ == "__main__":
    run_server()
