import json
import pathlib
import sys
import tempfile
import unittest
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from verify_bootstrap import check

class ContractTests(unittest.TestCase):
    def test_baseline(self):
        self.assertEqual(check()["nodes"], 9)
    def exercise(self,poison):
        with tempfile.TemporaryDirectory() as tmp:
            folder=pathlib.Path(tmp)/".kbi"
            folder.mkdir()
            for name in ("lattice.json","promotion-gates.json","claims.json"):
                doc=json.loads((ROOT/".kbi"/name).read_text())
                poison(name,doc)
                (folder/name).write_text(json.dumps(doc))
            with self.assertRaises(ValueError):
                check(tmp)
    def test_cycle_rejected(self):
        self.exercise(lambda n,d: d["edges"].append({"from":"publish_candidate","to":"sense"}) if n=="lattice.json" else None)
    def test_gate_rejected(self):
        self.exercise(lambda n,d: d["gates"]["GITHUB_RELEASE"].update(default="ALLOW") if n=="promotion-gates.json" else None)
    def test_identity_rejected(self):
        self.exercise(lambda n,d: d.update(project_id="other") if n=="claims.json" else None)
    def test_claim_inflation_rejected(self):
        self.exercise(lambda n,d: d["claims"][0].update(status="PASS") if n=="claims.json" else None)

if __name__=="__main__":
    unittest.main()
