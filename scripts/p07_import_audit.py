"""Fail-closed source parity verifier for public FCF v0.4.0.

Usage: python scripts/p07_import_audit.py --archive <zip>
       python scripts/p07_import_audit.py --repo .
Runs locally, never writes to GitHub or Drive.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import re
import zipfile

ARCHIVE_SHA256 = "85efa981d87eae498f15c752942ba94472f25a3773b66c44b0f63566a5e08044"
PREFIX = "FCF_v0.4.0_public_source/"
EXPECTED_FILES = 87
SUMS = "SHA256SUMS.txt"
HEX = re.compile(r"^[0-9a-f]{64}$")

class ImportAuditError(ValueError):
    pass

def _check_name(name: str) -> None:
    p = pathlib.PurePosixPath(name)
    if (not name or name.startswith("/") or "\\" in name or
        any(x in ("", ".", "..") for x in name.split("/")) or
        p.as_posix() != name):
        raise ImportAuditError("unsafe archive path: " + repr(name))

def _verify(files: dict[str, bytes]) -> dict:
    if SUMS not in files:
        return {"status": "HOLD",
                "reason": "SHA256SUMS.txt missing; full-source parity not demonstrated",
                "file_count": len(files)}
    declared: dict[str, str] = {}
    for line in files[SUMS].decode("utf-8").splitlines():
        digest, sep, path = line.partition("  ")
        if not sep or not HEX.fullmatch(digest) or path in declared:
            raise ImportAuditError("invalid or duplicate SHA256SUMS entry")
        _check_name(path)
        declared[path] = digest
    actual = set(files) - {SUMS}
    if set(declared) != actual:
        raise ImportAuditError("manifest path mismatch")
    for path in sorted(actual):
        if hashlib.sha256(files[path]).hexdigest() != declared[path]:
            raise ImportAuditError("digest mismatch at " + path)
    if len(files) != EXPECTED_FILES:
        raise ImportAuditError("unexpected file count: %d" % len(files))
    return {"status": "PASS", "file_count": len(files),
            "manifest_entries": len(declared), "content_verified": True}

def audit_archive(path: pathlib.Path) -> dict:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != ARCHIVE_SHA256:
        raise ImportAuditError("archive SHA-256 differs from canonical public source")
    files: dict[str, bytes] = {}
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            if not member.filename.startswith(PREFIX):
                raise ImportAuditError("out-of-scope ZIP member")
            name = member.filename[len(PREFIX):]
            _check_name(name)
            if name in files:
                raise ImportAuditError("duplicate ZIP path")
            files[name] = archive.read(member)
    result = _verify(files)
    result.update({"archive_sha256": digest, "mode": "archive"})
    return result

def audit_repo(root: pathlib.Path) -> dict:
    if not root.is_dir():
        raise ImportAuditError("repository path missing")
    files = {}
    for path in root.rglob("*"):
        if (not path.is_file() or ".git" in path.parts or
            "__pycache__" in path.parts or path.suffix == ".pyc"):
            continue
        rel = path.relative_to(root).as_posix()
        if (rel.startswith("scripts/p07_") or rel.startswith("docs/P07_") or
            rel.startswith("tests/bootstrap/test_p07_") or
            rel == ".github/workflows/p07-import-audit.yml"):
            continue
        files[rel] = path.read_bytes()
    result = _verify(files)
    result["mode"] = "repo"
    return result

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--archive", type=pathlib.Path)
    group.add_argument("--repo", type=pathlib.Path)
    args = parser.parse_args(argv)
    try:
        result = audit_archive(args.archive) if args.archive else audit_repo(args.repo)
    except (ImportAuditError, OSError, zipfile.BadZipFile, UnicodeError) as exc:
        result = {"status": "FAIL", "reason": str(exc)}
    print(json.dumps(result, sort_keys=True))
    return {"PASS": 0, "HOLD": 2, "FAIL": 1}[result["status"]]

if __name__ == "__main__":
    raise SystemExit(main())
