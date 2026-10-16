"""Pure/simulated P09 gates: does not assert genuine-server execution."""
import io,json,unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from fcf.integration.p09_gate import observation_report,hold_report
from fcf.integration.p09_cli import main
from fcf.kernel import FCFError

PROJECT="fcf-p09-synthetic"
ROOT="viking://resources/"+PROJECT
SHA="a"*64

def sample():
    return {"project_id":PROJECT,"outcome":"PASS",
      "preflight":{"outcome":"PASS","checks":{k:"PASS" for k in
        ("health","version","auth_mode","ready","principal","acl_structure")}},
      "retrieval":{"expected_hit":"PASS","result_count":1},
      "download":{"file_uri":ROOT+"/synthetic_note.md","byte_count":7,
                  "expected_sha256":SHA,"observed_sha256":SHA,"byte_integrity":"PASS"},
      "index":{"index_consistency":"PASS","scope":ROOT,"server_reported_ok":True},
      "non_owner":{"outcome":"PASS","non_owner_stat":"DENIED","status":403},
      "non_owner_download":{"status":"PASS","file_read":"DENIED","http_status":403}}

def evaluate(doc,**kwargs):
    return observation_report(project_id=PROJECT,pinned_process_sha256=SHA,
                              p03=doc,operator_reference="p09-run",**kwargs)

class P09GateTests(unittest.TestCase):
    def test_simulated_success_never_promotes_native(self):
        r=evaluate(sample())
        self.assertEqual(r["functional_contract"],"OBSERVED_PASS")
        self.assertEqual(r["evidence_disposition"],"READY_FOR_INDEPENDENT_REVIEW")
        self.assertEqual(r["genuine_native_gate"],"HOLD")
        self.assertEqual(r["cross_account_isolation"],"NOT_ESTABLISHED")
        self.assertFalse(r["production_authorized"])
    def test_missing_preflight_check_holds(self):
        d=sample();d["preflight"]["checks"].pop("health")
        self.assertEqual(evaluate(d)["functional_contract"],"HOLD")
    def test_unknown_preflight_field_holds(self):
        d=sample();d["preflight"]["checks"]["other"]="PASS"
        self.assertEqual(evaluate(d)["functional_contract"],"HOLD")
    def test_foreign_file_holds(self):
        d=sample();d["download"]["file_uri"]="viking://resources/other/file"
        self.assertEqual(evaluate(d)["functional_contract"],"HOLD")
    def test_missing_scope_holds(self):
        d=sample();d["index"]["scope"]="viking://resources/other"
        self.assertEqual(evaluate(d)["functional_contract"],"HOLD")
    def test_content_mismatch_holds(self):
        d=sample();d["download"]["observed_sha256"]="b"*64
        self.assertEqual(evaluate(d)["functional_contract"],"HOLD")
    def test_outsider_read_allowed_holds(self):
        d=sample();d["non_owner_download"]["http_status"]=200
        self.assertEqual(evaluate(d)["functional_contract"],"HOLD")
    def test_invalid_hash_fails_closed(self):
        with self.assertRaises(FCFError):
            observation_report(project_id=PROJECT,pinned_process_sha256="garbage",
                               p03=sample(),operator_reference="safe")
    def test_invalid_operator_label_fails_closed(self):
        with self.assertRaises(FCFError):
            observation_report(project_id=PROJECT,pinned_process_sha256=SHA,
                               p03=sample(),operator_reference="https://token.example")
    def test_wrong_project_fails_closed(self):
        with self.assertRaises(FCFError):
            observation_report(project_id="other",pinned_process_sha256=SHA,
                               p03=sample(),operator_reference="safe")
    def test_no_execute_causes_no_network(self):
        args=["--project",PROJECT,"--expected-user","owner","--foreign-user","outsider",
              "--file-uri",ROOT+"/synthetic_note.md","--expected-sha256",SHA,
              "--query","fake","--operator-reference","p09-run"]
        with patch("fcf.integration.p09_cli.LiveProbe",side_effect=AssertionError("network")):
            out=io.StringIO()
            with redirect_stdout(out): rc=main(args)
        self.assertEqual(rc,2)
        self.assertEqual(json.loads(out.getvalue())["reason_code"],"NOT_EXECUTED")
    def test_no_credentials_holds_and_no_network(self):
        args=["--execute","--project",PROJECT,"--expected-user","owner","--foreign-user","outsider",
              "--file-uri",ROOT+"/synthetic_note.md","--expected-sha256",SHA,
              "--query","fake","--operator-reference","p09-run"]
        with patch.dict("os.environ",{"FCF_P09_OWNER_KEY":"","FCF_P09_OUTSIDER_KEY":""}):
            out=io.StringIO()
            with redirect_stdout(out): rc=main(args)
        self.assertEqual(rc,2)
        self.assertEqual(json.loads(out.getvalue())["reason_code"],"MISSING_CREDENTIALS")

if __name__=="__main__":
    unittest.main()
