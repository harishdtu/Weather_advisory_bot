from app.graph.workflow import LangGraphRunner


def test_graph_no_location(monkeypatch):
    runner = LangGraphRunner()
    state = runner.run("sess1", "Is it safe to cycle?")
    # No location provided; should return no_policy or error
    assert state.get("decision") is not None
