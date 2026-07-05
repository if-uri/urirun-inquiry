# Author: Tom Sapletta · https://tom.sapletta.com
# Part of the ifURI solution.
"""urirun-inquiry — investigation by URI graph, not log debugging.

Turn a problem into a graph of addressable questions: every claim has a URI-proof, every
repair is a URI-plan, every lesson returns to memory. And — the answer to "why do you
stop?" — every inquiry ends by emitting a NEXT-STEP ticket for koru, so the loop always
has a next action and the system runs continuously.

    intent:// → fleet:// → routes:// → policy:// → provenance:// → event://
    → experience:// → hypothesis:// → evidence:// → rootcause://
    → repair:// → verify:// → reflection:// → skill:// / antipattern:// / task://
"""
from __future__ import annotations

from typing import Any

from . import case_store, probes, report, rootcause

__all__ = ["case_store", "probes", "report", "rootcause", "investigate"]


def investigate(goal: str, *, intent: str = "", node: str = "host",
                evidence: dict | None = None) -> dict[str, Any]:
    """Run a full inquiry from evidence to root cause + report + next-step ticket.

    ``evidence`` maps a probe scheme (fleet/shell/capability/experience/antipattern/…) to a
    result; in production these come from actually running the probe URIs. Returns the case,
    the root cause, the report artifact, and the koru ticket that keeps the loop alive."""
    case = case_store.create(goal, intent=intent, node=node)
    for scheme, result in (evidence or {}).items():
        case_store.add_evidence(case, f"{scheme}://{node}/probe/query", result)
    case = case_store.load(case["id"])
    root = rootcause.summarize(case)
    case = case_store.set_root_cause(case, root["root_cause"], root["recommended_next_uris"],
                                     root["missing_inputs"])
    art = report.write(case, root)
    ticket = report.to_ticket(case, root)
    return {"case": case["id"], "root_cause": root["root_cause"],
            "recommended_next_uris": root["recommended_next_uris"],
            "missing_inputs": root["missing_inputs"], "report": art, "ticket": ticket,
            "flow_safe": not probes.command_before_query(root["recommended_next_uris"])}
