# Author: Tom Sapletta · Part of the ifURI solution.
"""Root cause from evidence — the investigation's verdict, with the next URI and missing inputs.

Investigation does not end at "Thunderbird missing". It reasons over the collected
evidence to the real cause ("wrong strategy on a stale node — GUI unnecessary"), names
the recommended next URI, and lists the only genuinely-missing inputs (e.g. a secret).
Consumes urirun-mind memory (episodes/antipatterns) when present; degrades without it.
"""
from __future__ import annotations

from typing import Any


def summarize(case: dict) -> dict[str, Any]:
    """Fold the case's evidence into a root cause + recommended next URIs + missing inputs."""
    ev = case.get("evidence") or []
    facts = {e["uri"].split("://", 1)[0]: e["result"] for e in ev}
    findings: list[str] = []
    next_uris: list[str] = []
    missing: list[str] = []

    node_stale = _truthy_contains(facts.get("fleet"), ("stale", "blocked")) or \
        _truthy_contains(facts.get("node"), ("stale",))
    gui_absent = _truthy_contains(facts.get("shell"), ("not found", "not_found", "")) and \
        "thunder" in str(case.get("goal", "")).lower()
    has_headless = _truthy_contains(facts.get("capability"), ("headless", "email://", "move")) or \
        _truthy_contains(facts.get("experience"), ("headless", "known"))
    antipattern = _truthy_contains(facts.get("antipattern"), ("avoid",))

    if node_stale:
        findings.append("target node is stale/blocked (not merely online)")
    if gui_absent:
        findings.append("the GUI client is unavailable")
    if has_headless:
        findings.append("a headless capability satisfies the same intent")
    if antipattern:
        findings.append("an antipattern warns against the GUI strategy here")

    # the classic verdict: wrong strategy, not a missing app
    if has_headless and (node_stale or gui_absent):
        root = "Wrong strategy, not a missing app — the GUI path is unnecessary and blocked; use the headless capability."
        next_uris = _headless_next(case)
    elif node_stale:
        root = "Node is stale — reconcile before running the task."
        next_uris = [f"fleet://host/node/command/reconcile"]
    elif not ev:
        root = "No evidence collected yet — run the investigative probes first."
    else:
        root = "; ".join(findings) or "Inconclusive — gather more evidence."

    # a secret referenced but not present is the only genuinely-missing input
    for e in ev:
        r = str(e.get("result", ""))
        if "secret" in r.lower() and ("required" in r.lower() or "missing" in r.lower()):
            missing.append("secret://mail/main")
    if case.get("intent") == "email.spam.review" and "secret://mail/main" not in missing and has_headless:
        missing.append("secret://mail/main")

    return {"question": f"Why did '{case.get('goal')}' fail?", "root_cause": root,
            "findings": findings, "supporting_evidence": [e["uri"] for e in ev],
            "recommended_next_uris": next_uris, "missing_inputs": sorted(set(missing))}


def _headless_next(case: dict) -> list[str]:
    node = case.get("target_node", "host")
    # command ONLY after query (probes.command_before_query enforces this shape)
    return [f"email://host/folders/query/list", f"email://host/inbox/query/list",
            f"email://host/message/query/classify", "policy://host/action/query/allowed",
            "approval://human/mailbox/command/review", f"email://host/message/command/move"]


def _truthy_contains(value: Any, needles: tuple) -> bool:
    s = str(value).lower()
    return any(n.lower() in s for n in needles if n != "") or (value in (None, "", []) and "" in needles)
