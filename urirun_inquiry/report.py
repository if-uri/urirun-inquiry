# Author: Tom Sapletta · Part of the ifURI solution.
"""Investigation artifacts — every inquiry ends in an addressable report + a next step.

The report (json + markdown) is written as an artifact, and — crucially for continuous
operation — a NEXT-STEP ticket is emitted so koru always has something to run. The system
never dead-ends on "it failed"; it produces "here is the root cause and the next URI".
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _dir() -> Path:
    d = Path(os.environ.get("URIRUN_INQUIRY_DIR") or "~/.urirun/inquiry").expanduser()
    (d / "reports").mkdir(parents=True, exist_ok=True)
    return d / "reports"


def write(case: dict, root: dict) -> dict[str, Any]:
    cid = case["id"]
    doc = {"case": cid, "goal": case.get("goal"), "intent": case.get("intent"),
           "node": case.get("target_node"), **root}
    jp = _dir() / f"{cid}.report.json"
    jp.write_text(json.dumps(doc, indent=1, default=str), encoding="utf-8")
    mp = _dir() / f"{cid}.report.md"
    mp.write_text(_markdown(case, root), encoding="utf-8")
    return {"json": str(jp), "md": str(mp), "artifact_uri": f"artifact://host/inquiry/{cid}.report.json"}


def _markdown(case: dict, root: dict) -> str:
    lines = [f"# Inquiry {case['id']}", "", f"**Goal:** {case.get('goal')}",
             f"**Intent:** {case.get('intent')}  ·  **Node:** {case.get('target_node')}", "",
             "## Root cause", root.get("root_cause", "—"), "", "## Evidence"]
    for e in case.get("evidence", []):
        lines.append(f"- `{e['uri']}` → {str(e.get('result'))[:120]}")
    lines += ["", "## Recommended next URIs (command only after query)"]
    lines += [f"- `{u}`" for u in root.get("recommended_next_uris", [])] or ["- —"]
    if root.get("missing_inputs"):
        lines += ["", "## Missing inputs", *[f"- `{m}`" for m in root["missing_inputs"]]]
    return "\n".join(lines) + "\n"


def to_ticket(case: dict, root: dict) -> dict[str, Any]:
    """The next-step ticket for koru — so the loop never idles after an investigation."""
    miss = root.get("missing_inputs") or []
    if miss:
        title = f"Provide {', '.join(miss)} to run: {case.get('goal')}"
        prio = "high"
        reason = f"Inquiry {case['id']}: root cause = {root.get('root_cause')}. Only missing: {miss}."
    elif root.get("recommended_next_uris"):
        title = f"Execute recommended flow for: {case.get('goal')}"
        prio = "high"
        reason = f"Inquiry {case['id']}: {root.get('root_cause')}. Next: {root['recommended_next_uris']}."
    else:
        title = f"Continue investigation: {case.get('goal')}"
        prio = "normal"
        reason = f"Inquiry {case['id']}: gather more evidence."
    return {"title": title, "priority": prio, "reason": reason, "case": case["id"],
            "next_uris": root.get("recommended_next_uris", []), "missing": miss}
