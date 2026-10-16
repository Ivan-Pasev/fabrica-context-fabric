"""Bounded CLI: source observation, integrity verification, proposal and assessment.
No command performs writes to OpenViking/Drive/GitHub or canonical promotion.
"""
import argparse
import json
from pathlib import Path
from fcf.kernel import (FCFError, SnapshotStore, observed_source, propose_memory,
                        assess_proposal, canonical_json)


def main():
    parser = argparse.ArgumentParser(prog="fcf", description="FCF reference kernel (no remote writes)")
    commands = parser.add_subparsers(dest="command", required=True)
    for action in ("capture", "verify"):
        p = commands.add_parser(action)
        p.add_argument("--store", required=True)
        if action == "capture":
            p.add_argument("--file", required=True)
            p.add_argument("--project", required=True)
            p.add_argument("--uri", required=True)
            p.add_argument("--revision", required=True)
        else:
            p.add_argument("--record", required=True)
    p = commands.add_parser("propose")
    p.add_argument("--store", required=True)
    p.add_argument("--record", required=True)
    p.add_argument("--claim", required=True)
    p = commands.add_parser("assess")
    p.add_argument("--store", required=True)
    p.add_argument("--proposal", required=True)
    p.add_argument("--principal-id", required=True)
    p.add_argument("--role", required=True)
    args = parser.parse_args()
    try:
        if args.command == "capture":
            raw = Path(args.file).read_bytes()
            record = observed_source(project_id=args.project, source_system="local_fixture",
                                     source_uri=args.uri, revision=args.revision, content=raw)
            rid = SnapshotStore(Path(args.store)).capture(record, raw)
            result = {"record_sha256": rid, "content_sha256": record["content_sha256"], "status": "OBSERVED"}
        elif args.command == "verify":
            record, raw = SnapshotStore(Path(args.store)).retrieve(args.record)
            result = {"record_sha256": args.record, "verified": True,
                      "content_bytes": len(raw), "semantic_truth": "NOT_PROVEN"}
        elif args.command == "propose":
            record, _ = SnapshotStore(Path(args.store)).retrieve(args.record)
            result = propose_memory(record["project_id"], args.claim, [record])
        else:
            proposal = json.loads(Path(args.proposal).read_text("utf-8"))
            store = SnapshotStore(Path(args.store))
            evidence = {}
            for rid in proposal.get("source_record_sha256", []):
                try:
                    evidence[rid] = store.retrieve(rid)
                except (FCFError, OSError, ValueError):
                    pass
            result = assess_proposal(proposal, evidence, principal_id=args.principal_id, principal_role=args.role)
        print(canonical_json(result).decode("utf-8"))
    except (FCFError, OSError, ValueError, KeyError) as exc:
        parser.exit(2, f"FCF HOLD: {exc}\n")


if __name__ == "__main__":
    main()
