# Contributing

We welcome scoped improvements to the independent FCF reference implementation. Open an issue first for changes affecting API contracts, `.kbi` schema, release gates or constitutional invariants. Keep each change bounded and independently testable. Follow `AGENTS.md`. Include failing regression and negative-case tests for a bug fix, tests and source provenance for new behavior, and updates to documentation/source registry for changed surfaces.

Run `PYTHONPATH=src python -m unittest discover -s tests -v`, `PYTHONPATH=src python -m fcf.kbi.validate --root .kbi`, and `python validation/check_schemas.py` before PR submission. Document which checks used an emulated HTTP server versus a genuine OpenViking v0.5.0 runtime. Do not publish secrets, tokens, private manuscripts, user personal data or upstream AGPL source in this repository. Any claim of safety, interoperability or proof must be bounded by reproducible evidence and review.
