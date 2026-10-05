"""Explicit local Shadow loop. No market transport or commerce adapter is imported."""
import argparse
import json
from pathlib import Path

from research_lab.shadow_repository import JsonShadowRepository
from research_lab.shadow_state import build_validation_snapshot
from research_lab.shadow_validation import create_shadow_candidate, add_shadow_observation, complete_shadow


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("candidate", "observe", "outcome", "snapshot"))
    parser.add_argument("--store", required=True, help="single-process local JSON repository")
    parser.add_argument("--as-of", required=True, help="timezone-aware ISO evaluation timestamp")
    parser.add_argument("--input", help="JSON evidence packet; never contains credentials")
    parser.add_argument("--id", help="shadow_candidate_id")
    args = parser.parse_args(argv)
    if args.command in ("candidate", "observe") and not args.input:
        parser.error("candidate/observe require --input")
    if args.command in ("observe", "outcome") and not args.id:
        parser.error("observe/outcome require --id")
    repo = JsonShadowRepository(args.store)
    packet = json.loads(Path(args.input).read_text(encoding="utf-8")) if args.input else None
    if args.command == "candidate":
        result = create_shadow_candidate(packet["candidate"], packet["assessment"], repository=repo, as_of=args.as_of)
    elif args.command == "observe":
        result = add_shadow_observation(repo, args.id, packet, as_of=args.as_of)
    elif args.command == "outcome":
        result = complete_shadow(repo, args.id, as_of=args.as_of)
    else:
        result = build_validation_snapshot(repository=repo, maturity_stage="shadow", as_of=args.as_of)
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
    return result


if __name__ == "__main__":
    main()
