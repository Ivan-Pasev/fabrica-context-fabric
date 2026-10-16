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

P09_REVIEWED_BLOBS = {
  "src/fcf/integration/p09_gate.py": "0e05ccbabc42c45952d5f1b0bb463a8855e6bfd6",
  "src/fcf/integration/p09_cli.py": "a85af1889b51c1c0f7de0b27e0c61d76b6ebbe7d",
  "tests/test_p09_gate.py": "055e1098a7fd01e7dcc845fb0a4522f4510ba6d3",
  ".github/workflows/p09-observation-contract.yml": "7e0287b7f07362dbf77447d824861927c7f1acd5",
  "fixtures/p09/synthetic_note.md": "6fe2a08da387aba3f3832c4b399e165cd394caae",
  "docs/P09_GENUINE_OPENVIKING_RUNBOOK.md": "7743093c8321116977537b170313a1ec9f5d2d8e",
  "docs/P09_EVIDENCE_AND_LICENSE_GATES.md": "009008a74f9cfb2475117326dbab379307f8c688"
}

P10_REVIEWED_BLOBS = {
  "scripts/p10_native_install_smoke.py": "ab23174858e8d1e86491c38d2319b9fa2b1c2da1",
  "tests/test_p10_native_install_smoke.py": "7c5147324afb2150f44dd950bc8257856b08010f",
  ".github/workflows/p10-pinned-upstream-install.yml": "6673a3c127aba7b91e5bf7adc7fa6d1b6c240369",
  "docs/P10_PINNED_UPSTREAM_INSTALL_AND_LIMITS.md": "9c83773458876f602846c292807282e8e4cc7d29"
}

P11_REVIEWED_BLOBS = {
  "scripts/p11_native_http_smoke.py": "4777ecf8e0fa89d63d5faeb0f9bbdd588cd5c4ae",
  "tests/test_p11_native_http_smoke.py": "a202c9691e1e581d481375d9ecdbc38741dc8b1f",
  ".github/workflows/p11-native-loopback-http.yml": "65c8cb62ef6f9d54d83bdfa5b47702c25de6b379",
  "docs/P11_NATIVE_BOOT_PROTOCOL.md": "6629b769766a86bb202fae65a3fecea345809f05"
}

P11_CORE_REVIEWED_BLOBS = {
  "scripts/p11_core_init_probe.py": "1fc8afa617844504ceddd7918f02e4011cbde232",
  "tests/test_p11_core_init_probe.py": "4858655fe15d22ea22b70235ec85997c838ebd4e",
  ".github/workflows/p11-core-init-diagnostic.yml": "c9a0beb391652d45f8791294f098f1e6293e61af",
  "docs/P11_DIRECT_CORE_INIT_DIAGNOSTIC.md": "7a52d50eed0c797f1adcab436ba52d3d635f44cf"
}

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
        if rel in P09_REVIEWED_BLOBS:
            if git_blob_sha(data) != P09_REVIEWED_BLOBS[rel]:
                raise ImportAuditError('P09 addon blob differs from reviewed pin: ' + rel)
            continue
        if rel in P10_REVIEWED_BLOBS:
            if git_blob_sha(data) != P10_REVIEWED_BLOBS[rel]:
                raise ImportAuditError('P10 addon blob differs from reviewed pin: ' + rel)
            continue
        if rel in P11_REVIEWED_BLOBS:
            if git_blob_sha(data) != P11_REVIEWED_BLOBS[rel]:
                raise ImportAuditError('P11 addon blob differs from reviewed pin: ' + rel)
            continue
        if rel in P11_CORE_REVIEWED_BLOBS:
            if git_blob_sha(data) != P11_CORE_REVIEWED_BLOBS[rel]:
                raise ImportAuditError('P11 core probe differs from reviewed pin: ' + rel)
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
