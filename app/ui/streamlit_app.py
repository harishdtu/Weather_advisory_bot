import streamlit as st
from app.graph.workflow import LangGraphRunner
from app.llm.composer import compose_response
import uuid

st.set_page_config(page_title="Weather Advisory Bot")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("Weather Advisory Support Bot")

user_input = st.text_input("Ask a weather safety question:")
if st.button("Send") and user_input:
    runner = LangGraphRunner()
    state = runner.run(st.session_state.session_id, user_input)
    decision = state.get("decision")
    if not decision:
        st.error("No decision produced")
    else:
        if decision.get("status") == "success":
            text = compose_response(decision)
            st.success(text)
            with st.expander("Policy & Weather Details"):
                st.json({"policy": decision.get("policy"), "weather": decision.get("weather")})
        else:
            st.warning(decision.get("message"))
