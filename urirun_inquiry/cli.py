# Author: Tom Sapletta · Part of the ifURI solution.
"""urirun-inquiry CLI: start/rootcause/recommend an investigation."""
from __future__ import annotations
import argparse, json
from . import investigate


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="urirun-inquiry")
    ap.add_argument("goal"); ap.add_argument("--intent", default=""); ap.add_argument("--node", default="host")
    ap.add_argument("--evidence", default="{}", help="JSON: {scheme: result}")
    a = ap.parse_args(argv)
    print(json.dumps(investigate(a.goal, intent=a.intent, node=a.node, evidence=json.loads(a.evidence)), indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
