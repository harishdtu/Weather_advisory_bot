from typing import Dict, Any
from .langgraph_graph import build_graph


class LangGraphRunner:
    """Runner that executes the compiled LangGraph and maintains session memory."""

    def __init__(self):
        self.graph = build_graph()
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def run(self, session_id: str, user_input: str) -> Dict[str, Any]:
        prev = self.sessions.get(session_id, {})
        state: Dict[str, Any] = {"session_id": session_id, "raw_input": user_input}
        if prev:
            state.update({k: v for k, v in prev.items() if k in ["location", "intent"] and v})
            if prev.get("intent"):
                state["intent"] = dict(prev.get("intent", {}))
            if prev.get("location"):
                state["location"] = prev.get("location")

        # Compiled LangGraph is a Runnable; call invoke() to execute synchronously
        result = self.graph.invoke(state)

        # persist session-scoped memory (location and intent only)
        self.sessions[session_id] = {"location": result.get("location"), "intent": result.get("intent")}
        return result
