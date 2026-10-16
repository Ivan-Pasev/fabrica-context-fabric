"""P03 live-socket emulation tests. These DO NOT claim a real OpenViking server was run."""
import json
import threading
import unittest
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit,parse_qs

from fcf.integration.conformance import LiveProbe
from fcf.integration.p03 import P03Probe, require_project_leaf
from fcf.kernel import FCFError

PROJECT='fcf-p03-synthetic'
ROOT='viking://resources/'+PROJECT
FILE=ROOT+'/synthetic_note.md'
BODY=b'# P03 isolated synthetic note\n\nFCF-P03-SENTINEL-f12e92\n'
DIGEST=sha256(BODY).hexdigest()


class P03Handler(BaseHTTPRequestHandler):
    health={'status':'ok','healthy':True,'version':'0.5.0','auth_mode':'api_key'}
    acl={'acl_mode':'restricted','effective_entries':[{'principal':'user:fcf-p03-owner','level':'read'}]}
    consistency={'status':'ok','result':{'ok':True,'missing_records':[]}}
    file=BODY
    exposed=False
    calls=[]

    def log_message(self,*args): pass

    def reply(self,status,obj):
        raw=json.dumps(obj).encode('utf-8')
        self.send_response(status);self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)

    def do_GET(self):
        u=urlsplit(self.path);q=parse_qs(u.query);k=self.headers.get('X-API-Key')
        type(self).calls.append(('GET',u.path,k))
        if u.path=='/health':return self.reply(200,self.health)
        if u.path=='/ready':return self.reply(200,{'status':'ready'})
        if u.path=='/api/v1/system/status':
            if k=='owner-secret':return self.reply(200,{'status':'ok','result':{'initialized':True,'user':'fcf-p03-owner'}})
            if k=='foreign-secret':return self.reply(200,{'status':'ok','result':{'initialized':True,'user':'fcf-p03-foreign'}})
            return self.reply(401,{'status':'error'})
        if u.path=='/api/v1/acl':
            if k!='owner-secret':return self.reply(403,{'status':'error'})
            if q.get('uri') != [ROOT]:return self.reply(400,{'status':'error'})
            return self.reply(200,{'status':'ok','result':self.acl})
        if u.path=='/api/v1/fs/stat':
            if k=='foreign-secret':return self.reply(403,{'status':'error'})
            return self.reply(200,{'status':'ok','result':{'uri':ROOT,'isDir':True}})
        if u.path=='/api/v1/content/download':
            if k!='owner-secret':return self.reply(403,{'status':'error'})
            if q.get('uri') != [FILE]:return self.reply(404,{'status':'error'})
            b=self.file
            self.send_response(200);self.send_header('Content-Type','application/octet-stream')
            self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
            return
        return self.reply(404,{'status':'error'})

    def do_POST(self):
        u=urlsplit(self.path);k=self.headers.get('X-API-Key')
        type(self).calls.append(('POST',u.path,k))
        if k!='owner-secret':return self.reply(403,{'status':'error'})
        n=int(self.headers.get('Content-Length','0'))
        if n>8192:return self.reply(413,{'status':'error'})
        try:r=json.loads(self.rfile.read(n))
        except ValueError:return self.reply(400,{'status':'error'})
        if u.path=='/api/v1/search/find':
            if r.get('target_uri')!=ROOT or r.get('context_type')!='resource':return self.reply(400,{'status':'error'})
            return self.reply(200,{'status':'ok','result':{'resources':[{'uri':FILE,'score':0.95}]}})
        if u.path=='/api/v1/system/consistency':
            if r!={'uri':ROOT}:return self.reply(400,{'status':'error'})
            return self.reply(200,self.consistency)
        return self.reply(404,{'status':'error'})


class P03HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),P03Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.base='http://127.0.0.1:'+str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=3)

    def setUp(self):
        P03Handler.health={'status':'ok','healthy':True,'version':'0.5.0','auth_mode':'api_key'}
        P03Handler.acl={'acl_mode':'restricted','effective_entries':[{'principal':'user:fcf-p03-owner','level':'read'}]}
        P03Handler.consistency={'status':'ok','result':{'ok':True,'missing_records':[]}}
        P03Handler.file=BODY
        P03Handler.calls=[]
        self.probe=P03Probe(LiveProbe(self.base,'owner-secret',PROJECT,'fcf-p03-owner'))

    def run_probe(self,sha=DIGEST,uri=FILE):
        return self.probe.execute(file_uri=uri,expected_sha256=sha,
          search_query='FCF-P03-SENTINEL-f12e92',foreign_api_key='foreign-secret',
          foreign_user='fcf-p03-foreign')

    def test_end_to_end_simulated_contract_pass(self):
        r=self.run_probe()
        self.assertEqual(r['outcome'],'PASS');self.assertEqual(r['download']['byte_integrity'],'PASS')
        self.assertEqual(r['index']['index_consistency'],'PASS')
        self.assertFalse(r['production_authorized'])
        self.assertEqual(r['genuine_upstream_server_verified'],'NOT_ESTABLISHED_BY_HTTP_RESPONSES')

    def test_download_digest_mismatch_fails_closed(self):
        r=self.run_probe(sha='0'*64)
        self.assertEqual(r['outcome'],'HOLD')
        self.assertEqual(r['download']['byte_integrity'],'HOLD')

    def test_server_file_mutation_detected(self):
        P03Handler.file=b'altered version of synthetic note'
        self.assertEqual(self.run_probe()['download']['byte_integrity'],'HOLD')

    def test_missing_index_holds(self):
        P03Handler.consistency={'status':'ok','result':{'ok':False,'missing_records':[{'uri':FILE}]}}
        self.assertEqual(self.run_probe()['outcome'],'HOLD')

    def test_malformed_index_envelope_holds(self):
        P03Handler.consistency={'status':'ok','result':{'missing_records':[]}}
        self.assertEqual(self.run_probe()['index']['index_consistency'],'HOLD')

    def test_false_api_claim_holds_preflight(self):
        P03Handler.health['version']='0.5.1'
        result=self.run_probe()
        self.assertEqual(result['outcome'],'HOLD')
        self.assertNotIn('download',result)

    def test_bad_acl_holds_before_download(self):
        P03Handler.acl['acl_mode']='inherit'
        self.assertEqual(self.run_probe()['outcome'],'HOLD')
        self.assertFalse(any(p=='/api/v1/content/download' for _,p,_ in P03Handler.calls))

    def test_bad_digest_format_rejected(self):
        with self.assertRaises(FCFError):self.probe.verify_download(file_uri=FILE,expected_sha256='not-a-hash')

    def test_outside_project_file_rejected(self):
        for v in ['viking://resources/other/private.md','viking://user/other/memories/private.md',ROOT]:
            with self.subTest(v=v):
                with self.assertRaises(FCFError):self.probe.verify_download(file_uri=v,expected_sha256=DIGEST)

    def test_prefix_confusion_rejected(self):
        with self.assertRaises(FCFError):require_project_leaf(ROOT,ROOT+'-evil/file.md')

    def test_traversal_and_encoded_delimiters_rejected(self):
        for v in [ROOT+'/../private.md',ROOT+'/%2e%2e/private.md',ROOT+'/foo?bar',ROOT+'/foo#bar',ROOT+'//tmp.md']:
            with self.subTest(v=v):
                with self.assertRaises(FCFError):require_project_leaf(ROOT,v)

    def test_no_mutating_endpoint_called(self):
        self.run_probe()
        safe={'/health','/ready','/api/v1/system/status','/api/v1/acl',
              '/api/v1/search/find','/api/v1/system/consistency',
              '/api/v1/content/download','/api/v1/fs/stat'}
        self.assertTrue(all(p in safe for _,p,_ in P03Handler.calls))

    def test_full_probe_does_not_export_api_key(self):
        self.assertNotIn('owner-secret',json.dumps(self.run_probe()))
        self.assertNotIn('foreign-secret',json.dumps(self.run_probe()))

    def test_server_status_must_be_true_boolean(self):
        P03Handler.consistency={'status':'ok','result':{'ok':'true'}}
        self.assertEqual(self.run_probe()['outcome'],'HOLD')

    def test_honest_statement_source_authenticity(self):
        self.assertEqual(self.run_probe()['download']['source_authenticity'],'NOT_PROVEN')
        self.assertEqual(self.run_probe()['download']['semantic_truth'],'NOT_PROVEN')

    def test_negative_binary_download_denied(self):
        result=self.run_probe()
        self.assertEqual(result['non_owner_download']['status'],'PASS')
        self.assertEqual(result['non_owner_download']['file_read'],'DENIED')

    def test_foreign_key_must_be_distinct(self):
        with self.assertRaises(FCFError):
            self.probe.assert_foreign_download_denied(file_uri=FILE,foreign_api_key='owner-secret')

    def test_exact_sha256_operator_supplied(self):
        r=self.run_probe()
        self.assertEqual(r['download']['observed_sha256'],DIGEST)
        self.assertEqual(r['download']['expected_sha256'],DIGEST)


if __name__=='__main__':unittest.main()
