# Author: Tom Sapletta · Part of the ifURI solution.
"""Case store — an investigation has memory, not just a conversation.

Every inquiry is a case://host/cases/<id> with a goal, intent, target node, hypotheses,
evidence (each an addressable URI-proof), a root cause, and a status. "Don't debug logs —
investigate the URI graph": every claim gets an address so questions can be asked of the
case later.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


def _dir() -> Path:
    d = Path(os.environ.get("URIRUN_INQUIRY_DIR") or "~/.urirun/inquiry").expanduser()
    d.mkdir(parents=True, exist_ok=True)
    return d


def _path(case_id: str) -> Path:
    return _dir() / f"{case_id}.json"


def create(goal: str, *, intent: str = "", node: str = "host", clock: float | None = None) -> dict[str, Any]:
    ts = clock if clock is not None else time.time()
    cid = "CASE-" + str(int(ts))[-8:]
    case = {"id": cid, "uri": f"case://host/cases/{cid}", "goal": goal, "intent": intent,
            "target_node": node, "status": "investigating", "created": ts,
            "hypotheses": [], "evidence": [], "root_cause": None, "next_uris": [], "missing": []}
    _path(cid).write_text(json.dumps(case, indent=1, default=str), encoding="utf-8")
    return case


def load(case_id: str) -> dict | None:
    p = _path(case_id)
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def save(case: dict) -> dict:
    _path(case["id"]).write_text(json.dumps(case, indent=1, default=str), encoding="utf-8")
    return case


def add_evidence(case: dict, uri: str, result: Any, *, supports: str | None = None,
                 refutes: str | None = None) -> dict:
    """Attach a URI-proof to the case: which query ran, what it returned, and which
    hypothesis it supports/refutes."""
    case["evidence"].append({"uri": uri, "result": result, "supports": supports, "refutes": refutes})
    return save(case)


def set_root_cause(case: dict, root_cause: str, next_uris: list[str], missing: list[str]) -> dict:
    case["root_cause"] = root_cause
    case["next_uris"] = next_uris
    case["missing"] = missing
    case["status"] = "resolved" if not missing else "blocked_on_input"
    return save(case)


def all_cases() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(_dir().glob("CASE-*.json"))]
