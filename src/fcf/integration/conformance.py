"""P02 read-only OpenViking 0.5.0 conformance gates.

No OpenViking writes or upstream code dependency. A successful result means only that
these specific observable checks passed with the operator's credentials. It is NOT
independent proof of permissions across tenants or of semantic correctness.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from urllib.parse import urlencode
from urllib.request import Request, build_opener
from urllib.error import HTTPError, URLError
from typing import Callable, Any
import json

from fcf.adapters.openviking import NoRedirect, OpenVikingReadOnly, _validate_base
from fcf.kernel import FCFError, check_project, SnapshotStore, verify_source

RELEASE_VERSION = "0.5.0"

class HTTPStatus(FCFError):
    def __init__(self, status_code: int):
        self.status_code = status_code
        super().__init__(f"HTTP_STATUS_{status_code}")


def get_json(url: str, headers: dict[str, str]) -> dict:
    """GET with no redirects, 2MiB cap, fixed timeout. No auth secrets in errors."""
    req = Request(url, headers=headers, method="GET")
    try:
        with build_opener(NoRedirect()).open(req, timeout=10) as response:
            content = response.read(2 * 1024 * 1024 + 1)
            if len(content) > 2 * 1024 * 1024:
                raise FCFError("oversized response")
            decoded = json.loads(content)
            if not isinstance(decoded, dict):
                raise FCFError("invalid response envelope")
            return decoded
    except HTTPError as exc:
        raise HTTPStatus(exc.code) from None
    except (URLError, UnicodeError, json.JSONDecodeError) as exc:
        raise FCFError("transport or response decoding failed") from exc


def unbox(response: dict[str, Any]) -> dict:
    if response.get("status") == "error":
        raise FCFError("upstream signaled error")
    obj = response.get("result", response.get("data", response))
    if not isinstance(obj, dict):
        raise FCFError("invalid upstream result")
    return obj


def require_restricted_acl(acl: dict, *, expected_principal: str) -> None:
    """Restrictive check of project root ACL; server enforcement is a distinct gate."""
    if acl.get("acl_mode") != "restricted":
        raise FCFError("project ACL must be restricted")
    entries = acl.get("effective_entries")
    if not isinstance(entries, list):
        raise FCFError("ACL effective entries not available")
    principals = set()
    for item in entries:
        if not isinstance(item, dict) or not isinstance(item.get("principal"), str):
            raise FCFError("malformed ACL entry")
        principals.add(item["principal"])
    if "user:*" in principals or any(x == "group:*" for x in principals):
        raise FCFError("wildcard ACL inherited")
    if expected_principal not in principals:
        raise FCFError("expected user missing from effective ACL")


@dataclass
class LiveProbe:
    base_url: str
    api_key: str
    project_id: str
    expected_user_id: str
    allowed_https_hosts: frozenset[str] = frozenset()
    getter: Callable[[str, dict[str, str]], dict] = get_json
    poster: Callable | None = None

    def __post_init__(self):
        self.base_url = _validate_base(self.base_url)
        check_project(self.project_id)
        if not isinstance(self.api_key, str) or not self.api_key.strip() or any(x in self.api_key for x in "\r\n"):
            raise FCFError("user-scoped API key required, even for loopback")
        if not isinstance(self.expected_user_id, str) or not self.expected_user_id or any(x in self.expected_user_id for x in "\r\n/"):
            raise FCFError("bounded expected user required")
        self.reader = OpenVikingReadOnly(self.base_url, api_key=self.api_key,
                             allowed_https_hosts=self.allowed_https_hosts,
                             **({"poster":self.poster} if self.poster is not None else {}))

    def _get(self, path: str, *, query: dict[str,str] | None = None) -> dict:
        if path not in {"/health", "/ready", "/api/v1/system/status", "/api/v1/acl", "/api/v1/fs/stat"}:
            raise FCFError("endpoint not on read-only allowlist")
        url = self.base_url + path + ("?" + urlencode(query) if query else "")
        return self.getter(url, {"X-API-Key": self.api_key})

    def preflight(self) -> dict[str, Any]:
        """Only PASS if actual response claims healthy v0.5.0 + API-key auth + named user."""
        checks: dict[str, str] = {}
        health = self._get("/health")
        checks["health"] = "PASS" if health.get("healthy") is True and health.get("status") == "ok" else "FAIL"
        checks["version"] = "PASS" if health.get("version") == RELEASE_VERSION else "FAIL"
        checks["auth_mode"] = "PASS" if health.get("auth_mode") == "api_key" else "FAIL"
        ready = self._get("/ready")
        checks["ready"] = "PASS" if ready.get("status") == "ready" else "FAIL"
        identity = unbox(self._get("/api/v1/system/status"))
        checks["principal"] = "PASS" if identity.get("user") == self.expected_user_id and identity.get("initialized") is True else "FAIL"
        acl = unbox(self._get("/api/v1/acl", query={"uri":self.project_uri}))
        try:
            require_restricted_acl(acl, expected_principal=f"user:{self.expected_user_id}")
            checks["acl_structure"] = "PASS"
        except FCFError:
            checks["acl_structure"] = "FAIL"
        result = {"runtime": "upstream_api_probe", "target_version": RELEASE_VERSION,
                  "project_id": self.project_id, "checks":checks,
                  "outcome": "PASS" if all(x == "PASS" for x in checks.values()) else "HOLD"}
        return result

    @property
    def project_uri(self) -> str:
        return f"viking://resources/{self.project_id}"

    def read_only_find(self, query: str, *, limit: int = 5) -> dict:
        return self.reader.find(project_id=self.project_id, query=query, limit=limit)

    def assert_forbidden_user(self, *, foreign_api_key: str, foreign_expected_user: str) -> dict:
        """Require explicit non-owner identity and 403/404 on root stat.

        This checks ONE non-owner principal against ONE protected project path.
        It is not a proof of universal tenant isolation.
        """
        if not foreign_api_key or foreign_api_key == self.api_key:
            raise FCFError("separate foreign user credential is required")
        foreign = LiveProbe(base_url=self.base_url,api_key=foreign_api_key,
                            project_id=self.project_id,expected_user_id=foreign_expected_user,
                            allowed_https_hosts=self.allowed_https_hosts, getter=self.getter,poster=self.poster)
        identity = unbox(foreign._get("/api/v1/system/status"))
        if identity.get("user") != foreign_expected_user or foreign_expected_user == self.expected_user_id:
            raise FCFError("foreign identity was not independently established")
        try:
            foreign._get("/api/v1/fs/stat",query={"uri":self.project_uri})
        except HTTPStatus as err:
            if err.status_code in {403,404}:
                return {"outcome":"PASS", "non_owner_stat":"DENIED", "status":err.status_code}
            raise
        raise FCFError("foreign user could access restricted project root")


def evidence_bindings(retrieved: dict, index: dict[str,str], store: SnapshotStore) -> dict:
    """Bind hits only when a trusted LOCAL record index points to intact snapshot bytes.

    `index` is a caller-supplied mapping of OpenViking URI to a captured FCF record
    digest. It is not built from model output. Correct binding doesn't establish
    remote server source authenticity or semantic truth.
    """
    if retrieved.get("status") != "UNTRUSTED_RETRIEVAL":
        raise FCFError("only untrusted retrieval envelopes are admissible")
    project = check_project(retrieved.get("project_id"))
    roots = f"viking://resources/{project}"
    items = retrieved.get("resources")
    if not isinstance(items, list):
        raise FCFError("malformed retrieval items")
    bound = []
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("uri"),str):
            raise FCFError("malformed retrieval hit")
        uri = item["uri"]
        if uri != roots and not uri.startswith(roots + "/"):
            raise FCFError("out of scope URI")
        ref = index.get(uri)
        if ref is None:
            bound.append({"uri":uri,"status":"UNBOUND","source_record_sha256":None})
            continue
        record, raw = store.retrieve(ref)
        if record["project_id"] != project or not verify_source(record,raw):
            raise FCFError("invalid bound source record")
        bound.append({"uri":uri,"status":"LOCAL_SNAPSHOT_INTEGRITY_VERIFIED",
                      "source_record_sha256":ref,"content_sha256":sha256(raw).hexdigest(),
                      "source_authenticity":"NOT_VERIFIED"})
    return {"project_id":project,"results":bound,"semantic_truth":"NOT_PROVEN",
            "canonical_promotion":False}
