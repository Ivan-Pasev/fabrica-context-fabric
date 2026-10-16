# Distribution profiles (design stubs, not installed plugins)

- `local-python`: import `fcf.kernel` for offline integrity/proposal work.
- `github-readonly`: `GitHubPinnedReader` accepts only an explicit full commit SHA and validated path.
- `google-drive-connector`: `DriveExportReader` accepts user-authorized connector export bytes; contains no connector invocation or credential automation.
- `openviking-readonly`: `OpenVikingReadOnly` performs project-scoped `find` on a configured v0.5.0 service; require operator HTTPS allowlist, user-bound API key and server ACLs.

**Future**: Codex, Claude Code, OpenCode and compatible API gateway distributions require independent trust and lifecycle testing. No automatic memory injection hooks are installed by this package.
