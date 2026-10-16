"""P03 executable read-only observation gates for OpenViking v0.5.0.

Safety boundary:
 - All requests are restricted to one validated project URI subtree.
 - Source bytes are SHA-256 compared with an operator-supplied expected digest.
 - Matching hashes establish byte agreement, NOT authentic source identity or truth.
 - POST /system/consistency is non-mutating per v0.5.0 API documentation.
 - No canonical promotion, resource write, privilege assignment or webhook side effects.
 - A response that claims v0.5.0 is not cryptographic proof of genuine server identity.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, build_opener

from fcf.adapters.openviking import NoRedirect
from fcf.integration.conformance import LiveProbe, HTTPStatus, unbox
from fcf.kernel import FCFError, check_sha

MAX_DOWNLOAD_BYTES = 8 * 1024 * 1024
MAX_JSON_BYTES = 2 * 1024 * 1024


def _get_bytes(url: str, headers: dict[str,str]) -> bytes:
    req = Request(url, headers=headers, method="GET")
    try:
        with build_opener(NoRedirect()).open(req, timeout=15) as response:
            data = response.read(MAX_DOWNLOAD_BYTES + 1)
            if len(data) > MAX_DOWNLOAD_BYTES:
                raise FCFError("oversized source content")
            return data
    except HTTPError as e:
        raise HTTPStatus(e.code) from None
    except URLError as e:
        raise FCFError("source transport unavailable") from None


def _post_consistency(url: str, request_body: bytes, headers: dict[str,str]) -> dict:
    req = Request(url, data=request_body, headers=headers, method="POST")
    try:
        with build_opener(NoRedirect()).open(req, timeout=30) as response:
            data = response.read(MAX_JSON_BYTES + 1)
            if len(data) > MAX_JSON_BYTES:
                raise FCFError("oversized index-consistency response")
            obj = json.loads(data)
            if not isinstance(obj, dict):
                raise FCFError("invalid index-consistency envelope")
            return obj
    except HTTPError as e:
        raise HTTPStatus(e.code) from None
    except (URLError, UnicodeError, json.JSONDecodeError):
        raise FCFError("index-consistency transport or envelope failure") from None


def require_project_leaf(root: str, uri: str) -> str:
    """Disallow root or ancestor downloads, dot segments and query decorations."""
    if not isinstance(uri,str) or not uri.startswith(root + '/'):
        raise FCFError("expected file must be a descendant of project root")
    tail = uri[len(root)+1:]
    if not tail or any(p in ('','.','..') for p in tail.split('/')):
        raise FCFError("invalid descendant file URI")
    if any(c in tail for c in ('?', '#', '\x00', '\r', '\n', '%')):
        raise FCFError("file URI contains forbidden delimiters")
    return uri


@dataclass
class P03Probe:
    preflight_probe: LiveProbe
    downloader: Callable[[str,dict[str,str]],bytes] = _get_bytes
    consistency_poster: Callable[[str,bytes,dict[str,str]],dict] = _post_consistency

    def _headers(self) -> dict[str,str]:
        return {"X-API-Key":self.preflight_probe.api_key}

    def verify_download(self, *, file_uri: str, expected_sha256: str) -> dict[str,Any]:
        p = self.preflight_probe
        require_project_leaf(p.project_uri, file_uri)
        check_sha(expected_sha256)
        url = p.base_url + '/api/v1/content/download?' + urlencode({'uri':file_uri})
        data = self.downloader(url, self._headers())
        actual = sha256(data).hexdigest()
        return {
            "file_uri": file_uri,
            "byte_count": len(data),
            "expected_sha256":expected_sha256,
            "observed_sha256":actual,
            "byte_integrity":"PASS" if data and actual == expected_sha256 else "HOLD",
            "source_authenticity":"NOT_PROVEN",
            "semantic_truth":"NOT_PROVEN",
        }

    def check_consistency(self) -> dict[str,Any]:
        p = self.preflight_probe
        body = json.dumps({'uri':p.project_uri},sort_keys=True).encode('utf-8')
        obj = self.consistency_poster(p.base_url+'/api/v1/system/consistency',body,
                                      {**self._headers(),"Content-Type":"application/json"})
        report = unbox(obj)
        # Current upstream documentation returns .ok and counts. The full index
        # report is advisory only: a fresh content digest is the separate gate.
        status = "PASS" if report.get('ok') is True else "HOLD"
        return {"index_consistency":status,"scope":p.project_uri,
                "server_reported_ok":report.get('ok') is True}

    def assert_foreign_download_denied(self, *, file_uri: str, foreign_api_key: str) -> dict[str,Any]:
        p = self.preflight_probe
        require_project_leaf(p.project_uri, file_uri)
        if not foreign_api_key or foreign_api_key == p.api_key or any(c in foreign_api_key for c in '\r\n'):
            raise FCFError("distinct foreign credential required")
        url = p.base_url + '/api/v1/content/download?' + urlencode({'uri':file_uri})
        try:
            self.downloader(url, {'X-API-Key':foreign_api_key})
        except HTTPStatus as e:
            if e.status_code in {403,404}:
                return {'status':'PASS','file_read':'DENIED','http_status':e.status_code}
            raise
        raise FCFError('foreign user can download project content')

    def execute(self, *, file_uri: str, expected_sha256: str, search_query: str,
                foreign_api_key: str, foreign_user: str) -> dict[str,Any]:
        p = self.preflight_probe
        report = p.preflight()
        out:dict[str,Any] = {"phase":"P03", "upstream_release":"v0.5.0",
              "project_id":p.project_id,"preflight":report,
              "source_authenticity":"NOT_PROVEN", "production_authorized":False}
        if report['outcome'] != 'PASS':
            out['outcome']='HOLD'
            return out
        found = p.read_only_find(search_query, limit=10)
        uris = [x.get('uri') for x in found.get('resources',[])]
        out['retrieval']={"result_count":len(uris),"expected_hit":"PASS" if file_uri in uris else "HOLD"}
        out['download']=self.verify_download(file_uri=file_uri, expected_sha256=expected_sha256)
        out['index']=self.check_consistency()
        out['non_owner']=p.assert_forbidden_user(foreign_api_key=foreign_api_key,
                                                 foreign_expected_user=foreign_user)
        out['non_owner_download']=self.assert_foreign_download_denied(file_uri=file_uri,foreign_api_key=foreign_api_key)
        out['outcome']='PASS' if (
            out['retrieval']['expected_hit']=='PASS' and
            out['download']['byte_integrity']=='PASS' and
            out['index']['index_consistency']=='PASS' and
            out['non_owner']['outcome']=='PASS' and
            out['non_owner_download']['status']=='PASS') else 'HOLD'
        out['genuine_upstream_server_verified']='NOT_ESTABLISHED_BY_HTTP_RESPONSES'
        return out
