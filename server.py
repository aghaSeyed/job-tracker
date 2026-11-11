#!/usr/bin/env python3
"""Job tracker web app. Run: python3 server.py  -> http://127.0.0.1:8765"""
import os, json, threading, pathlib, datetime, traceback
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import crawl

D = pathlib.Path(__file__).parent
DATA = crawl.DATA; DATA.mkdir(parents=True, exist_ok=True)
TRACK, MANUAL = DATA / "tracker.json", DATA / "manual.json"
lock = threading.Lock()
crawl_state = {"running": False, "error": None, "finished": None}

def load(p, default):
    try: return json.loads(p.read_text("utf8"))
    except Exception: return default

def save(p, data):
    tmp = p.with_suffix(".tmp"); tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), "utf8"); tmp.replace(p)

def run_crawl():
    try: crawl.main()
    except Exception: crawl_state["error"] = traceback.format_exc()[-400:]
    else: crawl_state["error"] = None
    crawl_state["running"] = False
    crawl_state["finished"] = datetime.datetime.now().isoformat(timespec="seconds")

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def body(self):
        return json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)) or 0) or b"{}")
    def do_GET(self):
        if self.path == "/":
            return self.send(200, (D / "static/index.html").read_bytes(), "text/html")
        if self.path == "/api/data":
            jobs = load(DATA / "jobs.json", {"crawled": "never", "jobs": []})
            return self.send(200, {"crawled": jobs["crawled"], "jobs": jobs["jobs"] + load(MANUAL, []),
                                   "companies": load(D / "companies.json", []), "tracker": load(TRACK, {}), "crawl": crawl_state})
        self.send(404, {"error": "not found"})
    def do_POST(self):
        d = self.body()
        if self.path == "/api/track":      # {key, status?, note?}
            with lock:
                t = load(TRACK, {}); r = t.setdefault(d["key"], {})
                for k in ("status", "note"):
                    if k in d: r[k] = d[k]
                r["updated"] = datetime.datetime.now().isoformat(timespec="minutes")
                if r.get("status") == "applied" and not r.get("applied_on"): r["applied_on"] = r["updated"][:10]
                save(TRACK, t)
            return self.send(200, {"ok": True, "record": r})
        if self.path == "/api/manual":     # {title, company, url}
            if not d.get("url") or not d.get("title"): return self.send(400, {"error": "title and url required"})
            with lock:
                m = load(MANUAL, [])
                if not any(x["url"] == d["url"] for x in m):
                    m.append({"source": "manual", "title": d["title"], "company": d.get("company", ""), "url": d["url"],
                              "posted": datetime.date.today().isoformat(), "salary": d.get("salary", ""),
                              "target": d.get("company") or None, "group": "Manual"})
                    save(MANUAL, m)
            return self.send(200, {"ok": True})
        if self.path == "/api/crawl":
            if crawl_state["running"]: return self.send(409, {"error": "already running"})
            crawl_state.update(running=True, error=None)
            threading.Thread(target=run_crawl, daemon=True).start()
            return self.send(200, {"ok": True})
        self.send(404, {"error": "not found"})

if __name__ == "__main__":
    host, port = os.environ.get("HOST", "127.0.0.1"), int(os.environ.get("PORT", 8765))
    print(f"Job tracker on http://{host}:{port}")
    ThreadingHTTPServer((host, port), H).serve_forever()
