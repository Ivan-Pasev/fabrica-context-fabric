"""Dependency-free, fail-closed source snapshot and promotion proposal reference core.

Security contract:
- No remote source is silently trusted. Ingested bytes are immutable observations.
- No content-derived text is evaluated as code, instructions, or authorization.
- No canonical writes. Production identities must originate in a trusted gateway.
- Hashes establish integrity of captured bytes, not truth or source authenticity.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable
import json
import os
import re
import tempfile

PROJECT_ID = re.compile(r"^[a-z][a-z0-9-]{1,62}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
STATES = frozenset({"OBSERVED", "PROPOSED", "REVIEWED", "CANONICAL", "QUARANTINED", "SUPERSEDED"})
SOURCE_SYSTEMS = frozenset({"github", "google_drive", "local_fixture"})


class FCFError(ValueError):
    """A reference-kernel precondition failed; no promotion should occur."""


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest_bytes(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def object_digest(obj: dict[str, Any]) -> str:
    return digest_bytes(canonical_json(obj))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def check_project(value: str) -> str:
    if not isinstance(value, str) or not PROJECT_ID.fullmatch(value):
        raise FCFError("project_id must match [a-z][a-z0-9-]{1,62}")
    return value


def check_sha(value: str) -> str:
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise FCFError("invalid SHA-256 digest")
    return value


def check_source(source_system: str, source_uri: str, revision: str) -> None:
    if source_system not in SOURCE_SYSTEMS:
        raise FCFError("unsupported source system")
    if not isinstance(source_uri, str) or not source_uri or len(source_uri) > 2048:
        raise FCFError("source_uri must be a bounded nonempty string")
    if any(ch in source_uri for ch in ("\x00", "\r", "\n")):
        raise FCFError("control characters in source URI")
    if not isinstance(revision, str) or not revision.strip() or len(revision) > 256:
        raise FCFError("source revision must be provided")


def observed_source(*, project_id: str, source_system: str, source_uri: str,
                    revision: str, content: bytes, mime_type: str = "text/plain",
                    observed_at: str | None = None) -> dict[str, Any]:
    """Capture untrusted source bytes; never claim connector or canonical authority."""
    check_project(project_id)
    check_source(source_system, source_uri, revision)
    if not isinstance(content, bytes) or not content:
        raise FCFError("source content must be nonempty bytes")
    if len(content) > 8 * 1024 * 1024:
        raise FCFError("v0.1 maximum source snapshot is 8 MiB")
    if not isinstance(mime_type, str) or not mime_type or len(mime_type) > 100:
        raise FCFError("invalid MIME type")
    when = observed_at or utc_now()
    try:
        parsed = datetime.fromisoformat(when.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("naive timestamp")
    except (ValueError, TypeError, AttributeError) as exc:
        raise FCFError("observed_at must be timezone-aware ISO 8601") from exc
    record = {
        "schema_version": "fcf.source.v1",
        "project_id": project_id,
        "source_system": source_system,
        "source_uri": source_uri,
        "source_revision": revision,
        "mime_type": mime_type,
        "content_sha256": digest_bytes(content),
        "content_bytes": len(content),
        "observed_at": when,
        "state": "OBSERVED",
        "source_authenticity": "NOT_VERIFIED",
        "semantic_truth": "NOT_PROVEN",
    }
    record["record_sha256"] = object_digest(record)
    return record


def verify_source(record: dict[str, Any], content: bytes) -> bool:
    """Verify record integrity and byte equality, not external authenticity."""
    try:
        if not isinstance(record, dict):
            return False
        payload = {k: v for k, v in record.items() if k != "record_sha256"}
        check_project(payload["project_id"])
        check_source(payload["source_system"], payload["source_uri"], payload["source_revision"])
        return (payload["schema_version"] == "fcf.source.v1" and
                payload["state"] == "OBSERVED" and
                payload["source_authenticity"] == "NOT_VERIFIED" and
                payload["semantic_truth"] == "NOT_PROVEN" and
                isinstance(content, bytes) and payload["content_bytes"] == len(content) and
                digest_bytes(content) == check_sha(payload["content_sha256"]) and
                check_sha(record["record_sha256"]) == object_digest(payload) and
                set(payload) == {"schema_version", "project_id", "source_system", "source_uri",
                                 "source_revision", "mime_type", "content_sha256", "content_bytes",
                                 "observed_at", "state", "source_authenticity", "semantic_truth"})
    except (FCFError, KeyError, TypeError, ValueError):
        return False


def propose_memory(project_id: str, claim: str, source_records: Iterable[dict[str, Any]],
                   *, conflict_keys: Iterable[str] = ()) -> dict[str, Any]:
    """Construct a proposal. Input records must later be byte-verified by a caller."""
    check_project(project_id)
    if not isinstance(claim, str) or not claim.strip() or len(claim) > 20000:
        raise FCFError("claim must be 1..20000 characters")
    records = list(source_records)
    if not records:
        raise FCFError("memory proposal requires at least one source")
    if any(r.get("project_id") != project_id for r in records):
        raise FCFError("cross-project memory source rejected")
    digests = sorted(set(check_sha(r["record_sha256"]) for r in records))
    conflicts = sorted(set(str(k) for k in conflict_keys if str(k).strip()))
    proposal = {
        "schema_version": "fcf.proposal.v1", "project_id": project_id,
        "claim": claim, "source_record_sha256": digests,
        "conflict_keys": conflicts, "state": "PROPOSED",
        "authority": "NONE", "semantic_truth": "NOT_PROVEN",
    }
    proposal["proposal_sha256"] = object_digest(proposal)
    return proposal


def assess_proposal(proposal: dict[str, Any], source_content: dict[str, tuple[dict[str, Any], bytes]],
                    *, principal_id: str, principal_role: str) -> dict[str, Any]:
    """Reference appraisal. Never issues an authorization or canonical promotion.

    Caller-supplied principal is deliberately insufficient for production authorization.
    ELIGIBLE_FOR_HUMAN_REVIEW means structural checks passed, not truth or approval.
    """
    failures: list[str] = []
    try:
        claim_digest = proposal["proposal_sha256"]
        if check_sha(claim_digest) != object_digest({k: v for k, v in proposal.items() if k != "proposal_sha256"}):
            failures.append("PROPOSAL_TAMPERED")
        check_project(proposal["project_id"])
        if proposal["state"] != "PROPOSED" or proposal["authority"] != "NONE":
            failures.append("INVALID_AUTHORITY_OR_STATE")
        if proposal["semantic_truth"] != "NOT_PROVEN":
            failures.append("FALSE_TRUTH_PROMOTION")
        if proposal.get("conflict_keys"):
            failures.append("UNRESOLVED_DECLARED_CONFLICTS")
        src_ids = proposal["source_record_sha256"]
        if not src_ids or not isinstance(src_ids, list):
            failures.append("NO_SOURCES")
        else:
            for rid in src_ids:
                evidence = source_content.get(rid)
                if evidence is None:
                    failures.append("MISSING_SOURCE:" + str(rid)[:16])
                else:
                    record, raw = evidence
                    if record.get("project_id") != proposal["project_id"]:
                        failures.append("CROSS_PROJECT_SOURCE")
                    if rid != record.get("record_sha256") or not verify_source(record, raw):
                        failures.append("SOURCE_INTEGRITY_FAILURE")
        if not proposal.get("claim", "").strip():
            failures.append("EMPTY_CLAIM")
    except (KeyError, ValueError, TypeError, FCFError) as exc:
        failures.append("MALFORMED_PROPOSAL:" + type(exc).__name__)
    if principal_role not in {"reviewer", "operator"}:
        failures.append("UNAUTHORIZED_ROLE")
    if not isinstance(principal_id, str) or not principal_id.strip():
        failures.append("MISSING_PRINCIPAL")
    decision = {
        "schema_version": "fcf.assessment.v1",
        "proposal_sha256": proposal.get("proposal_sha256"),
        "principal_id": principal_id,
        "principal_role": principal_role,
        "outcome": "HOLD" if failures else "ELIGIBLE_FOR_HUMAN_REVIEW",
        "reasons": sorted(set(failures)),
        "canonical_write_performed": False,
        "semantic_truth": "NOT_PROVEN",
    }
    decision["assessment_sha256"] = object_digest(decision)
    return decision


@dataclass
class SnapshotStore:
    """Local append-only content-addressed staging store. Not a distributed transaction."""
    root: Path

    def __post_init__(self) -> None:
        self.root = Path(self.root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _safe_object_path(self, name: str, ext: str) -> Path:
        check_sha(name)
        return self.root / (name + ext)

    @staticmethod
    def _atomic_create(path: Path, data: bytes, *, fail_before_replace: bool = False) -> None:
        # A unique tmp sibling and atomic no-clobber hardlink prevent accidental replacement.
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=".fcf-", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            if fail_before_replace:
                raise OSError("injected failure before create")
            try:
                os.link(temp_name, path)  # fails if object already exists
            except FileExistsError:
                if path.read_bytes() != data:
                    raise FCFError("content-address collision or inconsistent stored bytes")
        finally:
            os.unlink(temp_name) if os.path.exists(temp_name) else None

    def capture(self, record: dict[str, Any], content: bytes) -> str:
        if not verify_source(record, content):
            raise FCFError("source record/content integrity failure")
        blob = self._safe_object_path(record["content_sha256"], ".blob")
        rec = self._safe_object_path(record["record_sha256"], ".json")
        self._atomic_create(blob, content)
        self._atomic_create(rec, canonical_json(record))
        return record["record_sha256"]

    def retrieve(self, record_sha256: str) -> tuple[dict[str, Any], bytes]:
        record_bytes = self._safe_object_path(record_sha256, ".json").read_bytes()
        record = json.loads(record_bytes)
        if canonical_json(record) != record_bytes:
            raise FCFError("record bytes not canonical")
        content = self._safe_object_path(record["content_sha256"], ".blob").read_bytes()
        if record.get("record_sha256") != record_sha256 or not verify_source(record, content):
            raise FCFError("stored object mismatch")
        return record, content
