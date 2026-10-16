"""Explicit READ-ONLY OpenViking find adapter, pinned to v0.5.0 API contract.

Strict URI-scope and URL validation; no mutating methods, no redirects.
Retrieval hits are untrusted until their source bytes have been verified.
"""
from dataclasses import dataclass
import ipaddress
import json
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from fcf.kernel import FCFError


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise FCFError("redirect refused")


def _post(url: str, body: bytes, headers: dict[str, str]) -> bytes:
    req = Request(url, data=body, headers=headers, method="POST")
    with build_opener(NoRedirect()).open(req, timeout=15) as response:
        raw = response.read(2 * 1024 * 1024 + 1)
        if len(raw) > 2 * 1024 * 1024:
            raise FCFError("OpenViking response too large")
        return raw


def _validate_base(url: str) -> str:
    p = urlsplit(url)
    if p.scheme not in {"http", "https"} or not p.hostname or p.username or p.password or p.query or p.fragment:
        raise FCFError("unsafe OpenViking base URL")
    if p.path not in {"", "/"}:
        raise FCFError("OpenViking base URL must not contain a path")
    if p.scheme == "http":
        try:
            addr = ipaddress.ip_address(p.hostname)
        except ValueError as exc:
            raise FCFError("plaintext HTTP requires literal loopback IP") from exc
        if not addr.is_loopback:
            raise FCFError("plaintext remote OpenViking forbidden")
    return url.rstrip("/")


@dataclass
class OpenVikingReadOnly:
    base_url: str
    api_key: str | None = None
    poster: object = _post
    allowed_https_hosts: frozenset[str] = frozenset()

    def __post_init__(self):
        self.base_url = _validate_base(self.base_url)
        parsed = urlsplit(self.base_url)
        if parsed.scheme == "https" and parsed.hostname not in self.allowed_https_hosts:
            raise FCFError("remote HTTPS endpoint must be in operator allowlist")
        if self.api_key is not None and ("\n" in self.api_key or "\r" in self.api_key):
            raise FCFError("invalid credential")

    def find(self, *, project_id: str, query: str, limit: int = 5):
        # Fixed project-scoped retrieval root; no caller-provided cross-tenant target URI.
        from fcf.kernel import check_project
        check_project(project_id)
        if not isinstance(query, str) or not query.strip() or len(query) > 4096:
            raise FCFError("bounded query required")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 20:
            raise FCFError("limit must be 1..20")
        if self.base_url.startswith("https://") and not self.api_key:
            raise FCFError("remote HTTPS requires user-scoped API key")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        payload = {"query": query, "limit": limit,
                   "target_uri": f"viking://resources/{project_id}", "context_type": "resource"}
        raw = self.poster(self.base_url + "/api/v1/search/find", json.dumps(payload).encode("utf-8"), headers)
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise FCFError("invalid retrieval response")
        # The v0.5.0 HTTP contract commonly wraps results in "result";
        # some clients use "data", and local test doubles use a bare payload.
        if data.get("status") == "error":
            raise FCFError("OpenViking returned an error status")
        results = data.get("result", data.get("data", data))
        if not isinstance(results, dict):
            raise FCFError("invalid result envelope")
        allowed = f"viking://resources/{project_id}"
        hits = results.get("resources", [])
        if not isinstance(hits, list):
            raise FCFError("invalid resources list")
        for hit in hits:
            uri = hit.get("uri") if isinstance(hit, dict) else None
            if not isinstance(uri, str) or (uri != allowed and not uri.startswith(allowed + "/")):
                raise FCFError("out-of-scope retrieval result blocked")
        return {"status": "UNTRUSTED_RETRIEVAL", "project_id": project_id, "resources": hits}
