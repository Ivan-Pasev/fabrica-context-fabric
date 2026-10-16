# FABRICA Context Fabric (FCF)

Independent constitutional context-governance research for AI agents, supporting project-scoped **KBI_KERNEL** (Kernel-Based Intelligence) and **KBI_EPISTEMIC** (Knowledge Boundary Intelligence), within FAB.SYS / CodexStation Ω.

> **PUBLIC BOOTSTRAP — NOT A STABLE v0.4.0 RELEASE.** The complete 87-file v0.4.0 source archive and its 99 local tests have not yet been imported or rerun on GitHub. This branch contains a functional, isolated KBI constitutional bootstrap with its own limited tests and CI.

## What this repository demonstrates

A local structural verifier checks a nine-node KBI prerequisite lattice, rejects cycles, unknown identities and promoted claims, and requires all sensitive gates to remain **HOLD**. That checker does **not** control agent permissions or prove the truth of generated research.

```bash
python scripts/verify_bootstrap.py
python -m unittest discover -s tests/bootstrap -v
```

**Authority:** live, project-authorized Google Drive documents for canonical research; reviewed GitHub source for public versioned code; [OpenViking](https://github.com/volcengine/OpenViking) as optional derived context substrate. Retrieved text, hashes, memory and skill manifests grant neither truth nor authority.

**Dual KBI:** KBI_KERNEL routes bounded reasoning/invariant checks. KBI_EPISTEMIC classifies sources, evidence and contradictions. They are not synonyms. Read [AGENTS.md](AGENTS.md), [Architecture](docs/ARCHITECTURE.md), [Release gates](docs/RELEASE_GATES.md), [Source import](docs/SOURCE_IMPORT_RUNBOOK.md), [Security](SECURITY.md), and [P06 status](docs/P06_STATUS.md).

## Current gates

| Gate | Result |
| --- | --- |
| Executable bootstrap | Local structural test; remote CI pending |
| Full v0.4.0 package | HOLD — import and exact-commit parity pending |
| Genuine OpenViking v0.5.0 server | NOT RUN |
| Real multi-tenant isolation and recovery | NOT RUN |
| Stable release tag | HOLD |
| Production authorization | HOLD |

FCF is independently authored and distributed under Apache-2.0. OpenViking's main implementation is AGPL-3.0 and is not vendored here. See [NOTICE.md](NOTICE.md).
