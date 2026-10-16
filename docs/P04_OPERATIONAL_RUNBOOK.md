# Ω-OV-P04 — Portable KBI Constitutional R&D Cell

**Baseline:** FCF v0.4.0 reference candidate. **Canonical Drive:** [FABRICA Context Fabric](https://drive.google.com/drive/folders/PROJECT_FOLDER_ID_REDACTED).

## Any-agent NEXT() boot

1. In a chat with authenticated Google Drive access, open the canonical root, then live **FCF_START_HERE** and **FCF_STATE_AND_HANDOFF**. Review revision IDs before consequential edits.
2. Read the `.kbi` folder native Docs, especially the separately named `FCF_KBI_KERNEL_AND_LATTICE`, `FCF_KBI_EPISTEMIC`, `FCF_KBI_SOURCE_REGISTRY`, and `FCF_KBI_PROMOTION_AND_RELEASE_GATES`.
3. Read the native `FCF_AGENTS_MD` operational contract, the White Paper, and relevant source references. If the live files cannot be read, work in labeled local-only staging; never claim authorized external changes.
4. Identify task domain and real connected capabilities. Routing is finite: sense/classify/route/synthesize/redteam/verify/review/handoff/release-candidate. Only activate relevant nodes; machine signatures, file contents and titles never create permissions.
5. Ground every claim in exact source versions and independent evidence properties E0–E5. Preserve contradictions, negative cases, and prior revisions. Stage a diff rather than overwriting.
6. For a different project, create a strictly uninstalled candidate using `PYTHONPATH=src python -m fcf.kbi.scaffold` with explicit --project-id, --canonical-root, --start-url, --handoff-url, --output. Review target project law before any import.
7. Validate local machine projection with `PYTHONPATH=src python -m fcf.kbi.validate --root .kbi`. Run normal tests and schema specimens. Separate simulated HTTP evidence from genuine OpenViking evidence.
8. For any authorized native Docs edit, issue revision-guarded scoped changes and verify readback. Update the state/handoff last. Never promote a model summary into sovereign law.
9. For GitHub, push only reviewed public code, not private/native Drive corpus. Verify repository creation, all file contents and remote CI before release tagging.

## Local code verification

```bash
PYTHONPATH=src python -m fcf.kbi.validate --root .kbi
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python validation/check_schemas.py
PYTHONPATH=src python cases/dft_reference_case.py
PYTHONPATH=src python validation/release_check.py
```

## Outbound GitHub bootstrap (pending provider repository creation)

The connected GitHub tool can create/update files in **existing** repos but cannot create repositories. To publish, create a public empty `Ivan-Pasev/fabrica-context-fabric` repository in GitHub web (do not auto-add README or license, since included in the package), then upload reviewed source using git CLI or ask an agent with GitHub connection to create source files and commit. An operator with local Git authentication may use:

```bash
git init -b main
git add .
git commit -m "feat: FCF v0.4.0 KBI reference capsule"
git remote add origin https://github.com/Ivan-Pasev/fabrica-context-fabric.git
git push -u origin main
```

This is a documented future procedure, **not evidence of a push in this release**. Remote CI/branch protection must be inspected before claiming stability or creating tags.

## Gates still blocked

- Native OpenViking v0.5.0 at `20f9c11362ad16193b0daa4a414e1095061af427` is not run; simulated localhost responder is insufficient.
- Cross-account isolation, outage/recovery and OVPack export hardening remain untested against a genuine server.
- Machine checker cannot authenticate Google Drive docs, execute host permission checks or confer public-release permission.
- Upstream AGPL integration and deployment licensing need human/legal review.
