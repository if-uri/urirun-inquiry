# Author: Tom Sapletta · Part of the ifURI solution.
"""Investigation-by-URI: evidence → root cause (not 'app missing') → next URI + koru ticket.
Command-only-after-query is enforced; the loop always emits a next step."""
import pytest

from urirun_inquiry import case_store, investigate, probes, rootcause


@pytest.fixture(autouse=True)
def isolate(tmp_path, monkeypatch):
    monkeypatch.setenv("URIRUN_INQUIRY_DIR", str(tmp_path))


def test_command_before_query_is_flagged():
    bad = ["email://h/message/command/delete", "email://h/inbox/query/list"]
    assert probes.command_before_query(bad) == ["email://h/message/command/delete"]
    good = ["email://h/inbox/query/list", "email://h/message/query/classify",
            "approval://human/x/command/review", "email://h/message/command/move"]
    assert probes.command_before_query(good) == []


def test_checklist_has_the_systemic_questions():
    qs = probes.questions(node="lenovo")
    schemes = {q["uri"].split("://", 1)[0] for q in qs}
    assert {"fleet", "runtime", "provenance", "policy", "experience", "antipattern",
            "capability", "node"} <= schemes


def test_investigation_reaches_strategy_not_missing_app():
    # THE flagship: email spam on lenovo — stale node, no thunderbird, headless available
    out = investigate("Przenieś spam do Junk na Lenovo przez Thunderbirda",
                      intent="email.spam.review", node="lenovo",
                      evidence={"fleet": "stale", "shell": "not found",
                                "capability": "headless email:// move available",
                                "antipattern": "avoid-thunderbird_gui-on-node_stale"})
    assert "Wrong strategy" in out["root_cause"] and "headless" in out["root_cause"].lower()
    assert "secret://mail/main" in out["missing_inputs"]      # the only real missing input
    assert out["recommended_next_uris"][-1].endswith("message/command/move")
    assert out["flow_safe"] is True                            # command only after query


def test_investigation_emits_next_step_ticket_for_koru():
    out = investigate("email spam on lenovo", intent="email.spam.review", node="lenovo",
                      evidence={"fleet": "stale", "capability": "headless available",
                                "experience": "headless_imap known-good"})
    t = out["ticket"]
    assert t["priority"] == "high" and t["case"].startswith("CASE-")
    assert "secret://mail/main" in t["title"] or t["next_uris"]   # always a concrete next step


def test_node_stale_without_headless_recommends_reconcile():
    out = investigate("run task on lenovo", intent="generic", node="lenovo",
                      evidence={"fleet": "stale"})
    assert "reconcile" in out["root_cause"].lower() or "stale" in out["root_cause"].lower()


def test_case_persists_with_evidence_graph():
    out = investigate("x", intent="y", node="host", evidence={"fleet": "ready"})
    case = case_store.load(out["case"])
    assert case and case["uri"].startswith("case://host/cases/") and case["evidence"]
