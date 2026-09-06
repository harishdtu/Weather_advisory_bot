# Weather-Advisory Support Bot

This repository implements a deterministic weather-advisory assistant. It uses live Open-Meteo geocoding and forecast data, evaluates externally stored SOPs, and composes responses only from data returned by the weather client plus the matching policy.

The safety decision is not LLM-driven. The model parses the user request and the application evaluates deterministic policy conditions before producing an answer.

Contents:
- `app/` – application source
- `policies/sops.yaml` – externally stored Standard Operating Procedures
- `app/ui/streamlit_app.py` – Streamlit frontend
- `tests/` – pytest regression tests
- `evals/` – evaluation cases and runner

Quick start:

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env
python -m streamlit run app/ui/streamlit_app.py --server.headless true --server.port 8501
```

Running tests and evals:

```bash
python -m pytest -q
python -m evals.run_evals
```

Environment variables:
- `OPENAI_API_KEY` – optional for any future LLM wrapper integration, but current safety logic is deterministic and does not require it for core behavior.
- `STREAMLIT_SERVER_PORT` – optional override for the Streamlit app.

LangGraph architecture:
- `app/graph/langgraph_graph.py` builds an upstream `StateGraph` from `langgraph.graph`.
- The graph has real nodes: parse, resolve location, fetch weather, match SOPs, compose response.
- It uses `START`, `END`, and conditional edges built with `add_conditional_edges()`.
- `app/graph/workflow.py` executes the compiled graph via `invoke()` and maintains per-session location/context memory.

SOP configuration:
- Policies are stored in `policies/sops.yaml` and loaded through `app/policies/loader.py`.
- Matching and ranking happen in `app/policies/evaluator.py`.
- Adding or changing a policy does not require modifying Python control flow.

Open-Meteo integration:
- Geocoding uses `https://geocoding-api.open-meteo.com/v1/search`.
- Forecasts use `https://api.open-meteo.com/v1/forecast`.
- The app passes latitude and longitude explicitly and requests current/hourly/daily forecast fields.

Safety note:
- Weather failure, no-policy situations, and adversarial instructions all produce honest, deterministic fallback answers instead of fabricated weather advice.

