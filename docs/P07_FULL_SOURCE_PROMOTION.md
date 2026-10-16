# P07 — Full source promotion and release admission

**Status:** staged review. This branch adds a falsifiable full-source admission checker. It is not itself the 87-file release.

## Authoritative input
- Public-safe v0.4.0 ZIP SHA-256: `85efa981d87eae498f15c752942ba94472f25a3773b66c44b0f63566a5e08044`
- Exact ZIP member root: `FCF_v0.4.0_public_source/`
- 87 tracked file entries, including `SHA256SUMS.txt` with 86 digest records.
- Personal/private R&D ZIP must **never** be imported into this public repository.

## Release gates
1. Verify ZIP against pinned SHA-256, reject duplicate/unsafe paths and compare every digest.
2. Commit all public-safe tracked files to a fresh branch, not directly to main.
3. Run `python scripts/p07_import_audit.py --repo .` with the expected manifest and compare byte-for-byte contents. This check returns code 2 (HOLD) until all files are present; a green bootstrap CI does **not** mean full-source parity.
4. Run full 99-test reference suite under Python 3.10 and 3.12 using the v0.4.0 requirements and commands in the ZIP's `.github/workflows/reference-tests.yml`.
5. Review licensing, privacy and security separately. Reconcile README/AGENTS.md against native canonical Drive state. Merge only after parity and remote CI are confirmed.
6. Do not create a stable release tag until genuine OpenViking integration and publication approval gates are explicitly addressed; code-candidate tagging is a separate authorization.

## Evidence boundary
OpenViking v0.5.0 at commit `20f9c11362ad16193b0daa4a414e1095061af427` is a **pinned external dependency**, not a tested native FCF installation. Simulated HTTP tests do not establish upstream interoperability, tenant isolation or runtime recovery. KBI checks are structural, not scientific truth certification.
