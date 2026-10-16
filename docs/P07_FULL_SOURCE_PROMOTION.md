# P07 — Complete source candidate and promotion gate

This staged source candidate combines the unmodified 87-file FCF v0.4.0 public-safe release ZIP with four P07 import-admission files. It is a PR candidate, **not** a stable OpenViking-integrated release.

Upstream public archive SHA-256: `85efa981d87eae498f15c752942ba94472f25a3773b66c44b0f63566a5e08044`.
The upstream `SHA256SUMS.txt` covers exactly 86 source files and is never rewritten to include independently maintained P07 scripts and docs.

## Verification

```bash
python scripts/p07_import_audit.py --repo .
PYTHONPATH=src python -m fcf.kbi.validate --root .kbi
PYTHONPATH=src python -m unittest discover -s tests -v
python -m unittest discover -s tests/bootstrap -p 'test_p07_*.py' -v
PYTHONPATH=src python validation/check_schemas.py
PYTHONPATH=src python cases/dft_reference_case.py
```

Only after remote GitHub Actions confirms full manifest and complete test suite on the exact branch head may this package be merged. Real OpenViking server deployment, multi-tenant access enforcement, disaster recovery, upstream license diligence, and production authorization remain **HOLD**.

Google Drive canonical R&D documents control research state. GitHub main tracks reviewed public source and release tags, not internal Drive documents. KBI_KERNEL handles bounded reasoning; KBI_EPISTEMIC handles sources, claims and evidence. The local structural validator cannot grant tool permissions.
