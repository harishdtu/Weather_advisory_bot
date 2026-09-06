from typing import Dict, Any


def compose_response(decision: Dict[str, Any]) -> str:
    # deterministic composer using template - the LLM is not trusted to invent facts
    if decision.get("status") != "success":
        return decision.get("message", "I cannot provide a recommendation.")

    policy = decision["policy"]
    weather = decision["weather"]
    loc = decision.get("location")

    lines = []
    lines.append("Recommendation:")
    lines.append(decision.get("recommendation"))
    lines.append("")
    lines.append("Current conditions:")
    cw = weather.get("current", {})
    for k in ["wind_speed_10m", "temperature_2m", "precipitation_probability", "uv_index", "wind_gusts_10m"]:
        if k in cw and cw.get(k) is not None:
            lines.append(f"- {k.replace('_', ' ').title()}: {cw.get(k)}")

    lines.append("")
    lines.append("Policy applied:")
    # policy may be a dict
    pid = policy.get("id") if isinstance(policy, dict) else getattr(policy, "id", "unknown")
    pname = policy.get("name") if isinstance(policy, dict) else getattr(policy, "name", "unknown")
    psev = policy.get("severity") if isinstance(policy, dict) else getattr(policy, "severity", "unknown")
    lines.append(f"{pid} — {pname}\nSeverity: {psev}")
    lines.append("")
    lines.append("Why this policy matched:")
    lines.append(decision.get("reason", ""))

    return "\n".join(lines)
