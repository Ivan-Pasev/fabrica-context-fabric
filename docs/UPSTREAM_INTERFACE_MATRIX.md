# OpenViking API and integration evidence

## Stable evaluation target: v0.5.0

- Git ref: `20f9c11362ad16193b0daa4a414e1095061af427`.
- `POST /api/v1/search/find` with `{query, target_uri, context_type, limit}` is documented in [v0.5.0 retrieval API](https://github.com/volcengine/OpenViking/blob/20f9c11362ad16193b0daa4a414e1095061af427/docs/en/api/06-retrieval.md).
- `OpenVikingReadOnly` implements this single operation, enforces project URI scope, and uses a bounded HTTP POST. The adapter's response parser is tested with mock envelopes. **No actual OpenViking server communication occurred.**
- A directory hit and its `.abstract.md` are not primary proof; an authorized source read plus source digest comparison is required separately for evidence promotion.

## External import boundaries

- Public GitHub file snapshots use `https://raw.githubusercontent.com/{owner}/{repo}/{full_commit_sha}/{path}`. This interface is not an authenticated Git commit verifier. Only content bytes + supplied commit metadata are recorded.
- Google Drive byte snapshots must be supplied by a user-authorized connector (with file ID, revision ID, MIME, and raw export bytes). No direct Drive API calls or OAuth credentials are part of FCF. Native Docs/Sheets/Slides may need export in a chosen representation; the original format is authoritative.

## Release/main drift

- The v0.5.0 README lists AGPL main, Apache CLI and examples. Inspect the exact component licenses for distributed dependencies.
- At the 16 October 2026 main snapshot, the README also contains additional whole-rewrite/translation permission language that is not present in the v0.5.0 README. Legal interpretation is pending and no upstream source is bundled here.
- Future upstream capabilities described in main documentation are **not** assumed present in v0.5.0.

## P02 live test obligations

`ov status` / health, read-only `find`, synthetic import, ACL-denied read, index consistency, memory commit task status, backup-restore, restart recovery, URI escape, and source-version drift must all be run against a real pinned server before calling the integration verified.
