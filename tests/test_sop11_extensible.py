import shutil
import yaml
from app.policies.loader import load_sops
from app.policies.evaluator import sop_matches


def test_add_sop_11_and_load(tmp_path):
    src = "policies/sops.yaml"
    dst = tmp_path / "sops_copy.yaml"
    shutil.copy(src, dst)

    # append a new SOP-11
    with open(dst, "a", encoding="utf-8") as f:
        f.write(
            """
  - id: SOP-11
    name: 'Test SOP 11'
    category: 'test'
    severity: 'LOW'
    activities:
      - testing
    conditions:
      - name: always_true
        field: current.temperature_2m
        operator: ">="
        value: -100
    guidance: 'Default test SOP.'
    priority: 10
"""
        )

    sops = load_sops(str(dst))
    assert any(s.id == "SOP-11" for s in sops)

    # evaluator should be able to match it deterministically
    weather = {"current": {"temperature_2m": 10}}
    intent = {"activity": "testing"}
    matched = [s for s in sops if s.id == "SOP-11" and sop_matches(s, weather, intent)]
    assert matched
