"""Optional developer-only JSON Schema validation. Runtime remains dependency-free."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from fcf.kernel import observed_source, propose_memory, assess_proposal

ROOT = Path(__file__).resolve().parents[1]
raw = b"fixture source"
r = observed_source(project_id="research-a", source_system="local_fixture", source_uri="fixture://record", revision="1", content=raw)
p = propose_memory("research-a", "provisional claim", [r])
a = assess_proposal(p, {r["record_sha256"]: (r, raw)}, principal_id="reviewer", principal_role="reviewer")
for filename, object_ in [
    ("source-record.schema.json", r),
    ("memory-proposal.schema.json", p),
    ("assessment.schema.json", a),
]:
    schema = json.loads((ROOT / "schemas" / filename).read_text("utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(object_)
    print(f"PASS {filename}")
