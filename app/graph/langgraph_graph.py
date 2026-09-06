from langgraph.graph import StateGraph, START, END
from typing import Dict, Any
from .nodes import (
    node_parse_user_request,
    node_resolve_location,
    node_fetch_weather,
    node_match_sops,
    node_compose_response,
)


def build_graph() -> StateGraph:
    # Use a simple dict schema to avoid LangGraph schema validation warnings
    # and speed up compilation during tests.
    g = StateGraph(dict)

    # Add nodes
    g.add_node("parse_user_request", node_parse_user_request)
    g.add_node("resolve_location", node_resolve_location)
    g.add_node("fetch_weather", node_fetch_weather)
    g.add_node("match_sops", node_match_sops)
    g.add_node("compose_response", node_compose_response)

    # Edges with conditions
    # START -> parse
    g.add_edge(START, "parse_user_request")

    # parse -> resolve
    g.add_edge("parse_user_request", "resolve_location")

    # resolve -> fetch_weather (conditional)
    g.add_conditional_edges(
        "resolve_location",
        lambda s: s.get("error") is None,
        path_map={True: "fetch_weather", False: "compose_response"},
    )

    # fetch -> match (conditional)
    g.add_conditional_edges(
        "fetch_weather",
        lambda s: s.get("error") is None,
        path_map={True: "match_sops", False: "compose_response"},
    )

    # match -> compose (no_policy and normal both go to compose)
    g.add_edge("match_sops", "compose_response")

    # compose -> END
    g.add_edge("compose_response", END)

    compiled = g.compile()
    return compiled
