# Author: Tom Sapletta · Part of the ifURI solution.
"""The investigative checklist — the standard questions, each a URI probe.

For any failed process, the system asks the SAME systemic questions (not manual
intuition): does the URI exist, is the node ready (not just online), is the connector
current, does the response carry provenance, did policy allow it, did the postcondition
hold, is there a known-good episode / antipattern, is there a cheaper fallback, is a human
needed or just a connector. Each returns a URI to run for evidence.
"""
from __future__ import annotations

from typing import Any

# (question, evidence URI template) — {node}/{intent} filled per case
CHECKLIST: list[tuple[str, str]] = [
    ("What was the intent?", "intent://host/prompt/command/resolve"),
    ("Which URI should realize it?", "capability://host/graph/query/resolve"),
    ("Is the URI served in routes?", "runtime://{node}/routes/query/list"),
    ("Is the node ready, or only online?", "fleet://host/node/query/readiness"),
    ("Is the connector installed?", "node://{node}/connector/query/discover"),
    ("Is the connector current?", "node://{node}/runtime/query/state"),
    ("Does the response carry provenance?", "provenance://host/run/query/meta"),
    ("Did policy allow execution?", "policy://host/action/query/allowed"),
    ("Did the postcondition hold?", "verify://host/run/query/postcondition"),
    ("Is there a known-good episode?", "experience://host/episode/query/similar"),
    ("Is there an antipattern for this?", "antipattern://host/rules/query/match"),
    ("Is there a cheaper fallback?", "capability://host/graph/query/fallbacks"),
    ("Human needed, or just a connector?", "connector://host/catalog/query/search"),
]


def questions(node: str = "host", intent: str = "") -> list[dict[str, Any]]:
    return [{"q": q, "uri": u.replace("{node}", node).replace("{intent}", intent)}
            for q, u in CHECKLIST]


# --- the "command only after query" safety rule ---------------------------------
def command_before_query(flow: list[str]) -> list[str]:
    """Return command URIs that appear BEFORE any query in the flow — a violation of the
    investigate-first rule. A good flow queries + classifies + checks policy BEFORE any
    mutating command."""
    seen_query = False
    violations = []
    for uri in flow:
        if "/query/" in uri:
            seen_query = True
        elif "/command/" in uri and not seen_query and not uri.startswith("approval://"):
            violations.append(uri)
    return violations
