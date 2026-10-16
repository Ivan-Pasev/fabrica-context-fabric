"""Example of a declared scientific contradiction remaining on HOLD."""
from fcf.kernel import observed_source, propose_memory, assess_proposal

raw = b"H1: lambda=0; H2: lambda!=0; neither proven."
rec = observed_source(project_id="dft-research", source_system="local_fixture",
                      source_uri="fixture://dft-competing-hypotheses",
                      revision="r-001", content=raw)
proposal = propose_memory("dft-research", "H1 is correct", [rec], conflict_keys=["H1:H2"])
assessment = assess_proposal(proposal, {rec["record_sha256"]:(rec,raw)},
                             principal_id="demo-reviewer", principal_role="reviewer")
assert assessment["outcome"] == "HOLD", assessment
assert assessment["canonical_write_performed"] is False
print("PASS: competing hypotheses preserved under HOLD")
