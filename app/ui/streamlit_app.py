from pathlib import Path
import sys
import uuid

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from app.graph.workflow import LangGraphRunner
from app.llm.composer import compose_response

st.set_page_config(page_title="Weather Advisory Support Bot", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f5fbff 0%, #edf6ff 100%);
        color: #0f172a;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .topbar {
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%);
        color: white;
        padding: 1.5rem 1.25rem;
        border-radius: 1rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.18);
    }
    .header-kicker {
        font-size: 0.78rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: rgba(255,255,255,0.75);
        margin-bottom: 0.4rem;
    }
    .header-title {
        font-size: clamp(2rem, 3vw, 2.5rem);
        font-weight: 800;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .header-subtitle {
        font-size: 1rem;
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
        max-width: 720px;
    }
    .welcome-card {
        background: rgba(255,255,255,0.8);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 1rem;
        padding: 1.25rem;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
        margin-bottom: 1rem;
    }
    .metric-box {
        background: white;
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 0.8rem;
        padding: 0.9rem 1rem;
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.03);
    }
    .policy-badge {
        display: inline-block;
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.78rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .severity-low { background: #dcfce7; color: #166534; }
    .severity-moderate { background: #fef3c7; color: #92400e; }
    .severity-high { background: #fee2e2; color: #991b1b; }
    .severity-critical { background: #f1f5f9; color: #1e293b; border: 1px solid rgba(15, 23, 42, 0.15); }
    .sidebar .block-container { background: rgba(255,255,255,0.65); }
    .stChatMessage {
        margin-bottom: 0.9rem;
    }
    .stChatMessage > div {
        border-radius: 1rem;
        padding: 0.9rem 1rem;
    }
    [data-testid="stChatMessageAssistant"] > div {
        background: white;
        border: 1px solid rgba(148, 163, 184, 0.26);
    }
    [data-testid="stChatMessageUser"] > div {
        background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
        border: 1px solid rgba(59, 130, 246, 0.18);
    }
    .stExpander {
        margin-top: 0.75rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_decision(decision):
    if not decision:
        st.error("No decision produced.")
        return

    status = decision.get("status")
    policy = decision.get("policy") or {}
    location = decision.get("location") or {}
    weather = decision.get("weather") or {}
    current = weather.get("current") or {}

    if status == "success":
        recommendation = decision.get("recommendation") or "No recommendation available."
        st.success(recommendation)

        policy_id = policy.get("id", "Unknown") if isinstance(policy, dict) else "Unknown"
        policy_name = policy.get("name", "Policy") if isinstance(policy, dict) else "Policy"
        severity = (policy.get("severity") or "UNKNOWN").upper() if isinstance(policy, dict) else "UNKNOWN"
        severity_class = severity.lower().replace(" ", "-")

        cols = st.columns(4)
        with cols[0]:
            st.markdown(f"<div class='metric-box'><strong>Policy</strong><br>{policy_id}</div>", unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"<div class='metric-box'><strong>Severity</strong><br><span class='policy-badge severity-{severity_class}'>{severity}</span></div>", unsafe_allow_html=True)
        with cols[2]:
            name = location.get("name") or location.get("city") or "Unknown location"
            st.markdown(f"<div class='metric-box'><strong>Location</strong><br>{name}</div>", unsafe_allow_html=True)
        with cols[3]:
            st.markdown(f"<div class='metric-box'><strong>Policy name</strong><br>{policy_name}</div>", unsafe_allow_html=True)

        if decision.get("reason"):
            st.caption(decision["reason"])

        with st.expander("Weather and policy details"):
            st.json({"policy": policy, "weather": weather, "location": location})

    elif status == "no_policy":
        st.warning(decision.get("message") or "No applicable safety SOP was found.")
        if weather:
            with st.expander("Live weather data returned"):
                st.json(weather)
    elif status == "weather_unavailable":
        st.error(decision.get("message") or "Live weather data could not be retrieved.")
    else:
        st.info(decision.get("message") or "The system could not provide a recommendation.")

    if current:
        st.subheader("Current conditions")
        current_fields = [
            ("temperature_2m", "Temperature (°C)"),
            ("wind_speed_10m", "Wind speed (km/h)"),
            ("wind_gusts_10m", "Wind gusts (km/h)"),
            ("precipitation_probability", "Precipitation probability (%)"),
            ("precipitation", "Precipitation (mm)"),
            ("uv_index", "UV index"),
            ("weather_code", "Weather code"),
        ]
        metrics = []
        for key, label in current_fields:
            if key in current and current.get(key) is not None:
                metrics.append((label, current.get(key)))
        if metrics:
            cols = st.columns(min(len(metrics), 3))
            for idx, (label, value) in enumerate(metrics):
                with cols[idx % 3]:
                    st.markdown(f"<div class='metric-box'><strong>{label}</strong><br>{value}</div>", unsafe_allow_html=True)


if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "runner" not in st.session_state:
    st.session_state.runner = LangGraphRunner()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown(
    """
    <div class="topbar">
        <div class="header-kicker">Live Safety Guidance</div>
        <div class="header-title">🌦️ Weather Advisory Support Bot</div>
        <div class="header-subtitle">AI-powered outdoor safety guidance based on live weather and operational safety policies.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("Weather Advisory Bot")
st.sidebar.caption("Uses live Open-Meteo weather data and external safety SOPs.")

st.sidebar.subheader("Safety behavior")
st.sidebar.write(
    "- Weather data is live.\n"
    "- Recommendations are grounded in operational SOPs.\n"
    "- If no SOP applies, the bot says so.\n"
    "- If weather data is unavailable, it does not fabricate a forecast."
)

st.sidebar.subheader("Example questions")
for example in [
    "Is it safe to cycle today in Hyderabad?",
    "Can I go running today in Bangalore?",
    "Is today suitable for a picnic?",
    "Should I take my kid to the park?",
    "Is it safe to hike today?",
]:
    if st.sidebar.button(example, use_container_width=True):
        st.session_state.pending_prompt = example
        st.rerun()

if not st.session_state.chat_history:
    st.markdown(
        """
        <div class="welcome-card">
            <h3 style='margin-top: 0;'>Plan outdoor activities with confidence.</h3>
            <p>Ask whether today's weather conditions are suitable for cycling, running, hiking, picnics, parks, and other activities covered by the safety policies.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

for message in st.session_state.chat_history:
    role = message.get("role")
    content = message.get("content")
    decision = message.get("decision")
    with st.chat_message(role):
        if role == "user":
            st.write(content)
        else:
            st.markdown(content)
            render_decision(decision)

prompt = st.session_state.get("pending_prompt") if "pending_prompt" in st.session_state else None
if prompt:
    st.session_state.pending_prompt = ""
else:
    prompt = st.chat_input("Ask a weather safety question...")

if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Checking live weather and safety policies..."):
            state = st.session_state.runner.run(st.session_state.session_id, prompt)
        decision = state.get("decision") or {}
        assistant_text = compose_response(decision) if decision.get("status") == "success" else (decision.get("message") or "I couldn't provide a recommendation.")
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_text, "decision": decision})
        st.markdown(assistant_text)
        render_decision(decision)
