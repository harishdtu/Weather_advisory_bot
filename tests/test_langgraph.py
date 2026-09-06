from app.graph.langgraph_graph import build_graph


def test_langgraph_compiles():
    g = build_graph()
    assert g is not None
    # graph should have nodes we expect
    assert "parse_user_request" in g.nodes
    assert "compose_response" in g.nodes
