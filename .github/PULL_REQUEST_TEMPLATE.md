## Scope
What changed, what project boundary is affected, and why?

## Evidence and provenance
Source/commit references, exact versions and reproduction commands:

## Validation
- [ ] `PYTHONPATH=src python -m unittest discover -s tests -v`
- [ ] `PYTHONPATH=src python -m fcf.kbi.validate --root .kbi`
- [ ] `PYTHONPATH=src python validation/check_schemas.py`
- [ ] No secrets/private research or upstream AGPL files copied
- [ ] Bounded claims: simulated != genuine OpenViking; checksum != truth
- [ ] Canonical Drive source revisions consulted where relevant

## Constitutional and publication gates
List affected KBI invariants, missing evidence, unresolved contradictions and authorization. Do not check a box as a substitute for an independent remote review.
