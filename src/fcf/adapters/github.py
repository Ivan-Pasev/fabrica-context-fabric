"""Read-only GitHub pinned-content adapter with injectable transport.

Caller must independently establish that a repository/revision is in scope.
Using HTTPS GitHub does not constitute a cryptographic proof of authenticity.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import PurePosixPath
import re
from urllib.request import Request, build_opener, HTTPRedirectHandler
from fcf.kernel import FCFError, observed_source

_IDENT = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise FCFError("redirects are not followed")


def _fetch(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "FCF-reference-0.1", "Accept": "text/plain"})
    with build_opener(NoRedirect()).open(req, timeout=10) as response:
        data = response.read(8 * 1024 * 1024 + 1)
        if len(data) > 8 * 1024 * 1024:
            raise FCFError("source too large")
        return data


@dataclass
class GitHubPinnedReader:
    fetcher: object = _fetch

    def capture(self, *, project_id: str, owner: str, repo: str, commit: str, path: str):
        if not _IDENT.fullmatch(owner) or not _IDENT.fullmatch(repo):
            raise FCFError("invalid owner/repository")
        if not _COMMIT.fullmatch(commit):
            raise FCFError("GitHub sources require a full 40-hex commit SHA")
        if not isinstance(path, str) or not path or path.startswith("/") or "\\" in path or any(
            part in {"", ".", ".."} for part in path.split("/")):
            raise FCFError("unsafe file path")
        if str(PurePosixPath(path)) != path:
            raise FCFError("noncanonical file path")
        if any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~/" for c in path):
            raise FCFError("nonportable path; URI encoding unavailable in reference adapter")
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{commit}/{path}"
        raw = self.fetcher(url)
        record = observed_source(project_id=project_id, source_system="github", source_uri=url,
                                 revision=commit, content=raw, mime_type="application/octet-stream")
        return record, raw
