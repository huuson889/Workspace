"""Optional local functional harness. Not required to open the standalone deliverable."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import os
root=Path(__file__).resolve().parent.parent
os.chdir(root)
class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path!='/report':self.send_error(404);return
        size=int(self.headers.get('Content-Length','0'))
        if size>2_000_000:self.send_error(413);return
        (root/'qa-results.json').write_bytes(self.rfile.read(size))
        self.send_response(200);self.end_headers()
    def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
print('QA: http://localhost:8132/source/qa.html',flush=True)
ThreadingHTTPServer(('0.0.0.0',8132),Handler).serve_forever()
