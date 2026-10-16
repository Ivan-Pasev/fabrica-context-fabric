"""Fail-closed, dependency-free verifier for the P04 public source archive.

Modes:
    --archive ZIP : audit exact public artifact (expected SHA pinned below).
    --repo ROOT   : audit a checked-out repository against expected SHA256SUMS.txt.
                    If manifest absent, emit HOLD not PASS.
Never mutates a repository, Drive or GitHub.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, re, sys, zipfile

ARCHIVE_SHA256 = '85efa981d87eae498f15c752942ba94472f25a3773b66c44b0f63566a5e08044'
PREFIX = 'FCF_v0.4.0_public_source/'
EXPECTED_FILES = 87
SUMS = 'SHA256SUMS.txt'
HEX = re.compile(r'^[0-9a-f]{64}$')
# Pinned legacy bootstrap blobs retained next to the complete P04 manifest.
PINNED_BOOTSTRAP_BLOBS = {
  ".github/workflows/bootstrap-contract.yml": "9b742cfbffc02eaec46a3160e59e1a17848d9c05",
  "docs/ARCHITECTURE.md": "16da288280d8850d52b5fc63395630ba7f68a961",
  "docs/P06_STATUS.md": "db1b579ac72e188a40272bac31cdbeb35e274757",
  "docs/RELEASE_GATES.md": "4b01b81199716c9225cc3f5f6d01715e46260d2a",
  "docs/SOURCE_IMPORT_RUNBOOK.md": "4dd3525ac6143d25d579ae487a191f38470276c6",
  "scripts/verify_bootstrap.py": "b8c084b0ba3499f08d9e753fb1a3e3fde41e4298",
  "tests/bootstrap/test_contract.py": "555f8477b79826c73c6cbe4abb02c1eeebbb3083"
}
STAGING_AUDIT_FILES = [
  ".github/workflows/p07-import-audit.yml",
  "docs/P07_FULL_SOURCE_PROMOTION.md",
  "scripts/p07_import_audit.py",
  "tests/bootstrap/test_p07_import_audit.py",
  "tests/bootstrap/test_p08_parity.py"
]

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + bytes([0]) + data).hexdigest()


class ImportAuditError(ValueError):
    pass

def _check_name(name: str) -> None:
    p = pathlib.PurePosixPath(name)
    if not name or name.startswith('/') or '\\' in name or any(x in ('', '.', '..') for x in name.split('/')) or p.as_posix() != name:
        raise ImportAuditError('unsafe archive path: ' + repr(name))

def _verify(files: dict[str, bytes]) -> dict:
    if SUMS not in files:
        return {'status': 'HOLD', 'reason': 'SHA256SUMS.txt missing; full-source parity not demonstrated', 'file_count': len(files)}
    lines = files[SUMS].decode('utf-8').splitlines()
    declared: dict[str, str] = {}
    for line in lines:
        digest, sep, path = line.partition('  ')
        if not sep or not HEX.fullmatch(digest) or path in declared:
            raise ImportAuditError('invalid or duplicate SHA256SUMS entry')
        _check_name(path)
        declared[path] = digest
    actual = set(files) - {SUMS}
    if set(declared) != actual:
        raise ImportAuditError('manifest path mismatch: missing=%s unexpected=%s' % (sorted(actual-set(declared)), sorted(set(declared)-actual)))
    for path in sorted(actual):
        if hashlib.sha256(files[path]).hexdigest() != declared[path]:
            raise ImportAuditError('digest mismatch at ' + path)
    if len(files) != EXPECTED_FILES:
        raise ImportAuditError('unexpected file count: %d != %d' % (len(files), EXPECTED_FILES))
    return {'status': 'PASS', 'file_count': len(files), 'manifest_entries': len(declared), 'content_verified': True}

def audit_archive(path: pathlib.Path) -> dict:
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if sha != ARCHIVE_SHA256:
        raise ImportAuditError('archive SHA-256 differs from canonical public source')
    files: dict[str, bytes] = {}
    with zipfile.ZipFile(path) as z:
        for member in z.infolist():
            if member.is_dir():
                continue
            if not member.filename.startswith(PREFIX):
                raise ImportAuditError('out-of-scope ZIP member')
            name = member.filename[len(PREFIX):]
            _check_name(name)
            if name in files:
                raise ImportAuditError('duplicate ZIP path')
            files[name] = z.read(member)
    result = _verify(files)
    result.update({'archive_sha256': sha, 'mode': 'archive'})
    return result

def audit_repo(root: pathlib.Path) -> dict:
    if not root.is_dir():
        raise ImportAuditError('repository path missing')
    files = {}
    for p in root.rglob('*'):
        if not p.is_file() or '.git' in p.parts or '__pycache__' in p.parts or p.suffix == '.pyc':
            continue
        rel = p.relative_to(root).as_posix()
        if rel in STAGING_AUDIT_FILES:
            continue  # exact staging-only paths
        data = p.read_bytes()
        if rel in PINNED_BOOTSTRAP_BLOBS:
            if git_blob_sha(data) != PINNED_BOOTSTRAP_BLOBS[rel]:
                raise ImportAuditError('retained bootstrap file changed without reviewed manifest: ' + rel)
            continue
        files[rel] = data
    result = _verify(files)
    result.update({'mode': 'repo'})
    return result

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--archive', type=pathlib.Path)
    group.add_argument('--repo', type=pathlib.Path)
    ns = parser.parse_args(argv)
    try:
        result = audit_archive(ns.archive) if ns.archive else audit_repo(ns.repo)
    except (ImportAuditError, OSError, zipfile.BadZipFile, UnicodeError) as e:
        result = {'status': 'FAIL', 'reason': str(e)}
    print(json.dumps(result, sort_keys=True))
    return {'PASS': 0, 'HOLD': 2, 'FAIL': 1}[result['status']]

if __name__ == '__main__':
    raise SystemExit(main())
