"""Integration checks added after transcript recovery to the Linux host."""
import json
import unittest
from threading import Thread
from http.server import ThreadingHTTPServer
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from chipsentinel.server import Handler

class HTTPTests(unittest.TestCase):
 def test_real_http_static_and_simulation(self):
  server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
  worker=Thread(target=server.serve_forever,daemon=True);worker.start()
  try:
   base=f'http://127.0.0.1:{server.server_port}'
   # A build is required for static content; API remains independently testable.
   from chipsentinel.server import ROOT
   if (ROOT/'frontend/dist/index.html').exists(): self.assertEqual(urlopen(base).status,200)
   req=Request(base+'/api/diagnose',json.dumps({'family':7,'seed':31,'budget':4}).encode(),{'Content-Type':'application/json'})
   result=json.load(urlopen(req));self.assertEqual(len(result['observations']),4)
   for payload in [{'budget':99},[],{'budget':True}]:
    with self.assertRaises(HTTPError) as error:
     urlopen(Request(base+'/api/diagnose',json.dumps(payload).encode(),{'Content-Type':'application/json'}))
    self.assertEqual(error.exception.code,400)
  finally:
   server.shutdown();server.server_close();worker.join()

class FastAPITests(unittest.TestCase):
 def test_adapter(self):
  try:
   from fastapi.testclient import TestClient
   from chipsentinel.api import app
  except ImportError: self.skipTest('Optional FastAPI test dependencies not installed')
  if app is None: self.skipTest('Optional FastAPI adapter not installed')
  with TestClient(app) as client:
   self.assertEqual(client.get('/api/health').status_code,200)
   response=client.post('/api/diagnose',json={'family':6,'seed':31,'budget':4})
   self.assertEqual(response.status_code,200);self.assertEqual(len(response.json()['observations']),4)
   self.assertEqual(client.post('/api/diagnose',json={'budget':100}).status_code,422)
