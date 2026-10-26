"""Loopback-only static UI and JSON API without runtime dependencies."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import json
from .api import diagnose
ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT/'frontend/dist'),**kwargs)
    def do_POST(self):
        if self.path!='/api/diagnose': self.send_error(404); return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<8192: raise ValueError('request too large')
            payload=json.loads(self.rfile.read(length)); data=diagnose(payload); status=200
        except (ValueError,TypeError,AttributeError): data={'error':'Invalid request. Use bounded numeric family, seed, budget and valid policy.'};status=400
        body=json.dumps(data).encode(); self.send_response(status); self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
if __name__=='__main__':
    print('ChipSentinel: http://127.0.0.1:8101',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8101),Handler).serve_forever()
