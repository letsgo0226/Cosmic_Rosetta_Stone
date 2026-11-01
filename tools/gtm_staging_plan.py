#!/usr/bin/env python3
"""TM-008 metadata-only staging planner. No subprocess, network or deploy action."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "永久記憶" / "圖靈機" / "machine_registry.json"

def plan(registry_path=REGISTRY):
    base = registry_path.parent.resolve()
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["execution_policy"] == "metadata-only; no automatic execution or deployment"
    entries = data["entries"]
    assert len(entries) == 8
    assert [item["id"] for item in entries] == [f"TM-{i:03d}" for i in range(1, 9)]
    records = []
    for item in entries:
        path = (base / item["record"]).resolve()
        assert path.parent == base, "registry path escape"
        assert path.is_file(), f"missing record: {item['id']}"
        records.append({"id": item["id"], "record": item["record"], "status": "validated_metadata"})
    return {"controller": "TM-008", "mode": "dry-run", "target": "staging-plan-only",
            "deployment_executed": False, "prototype_execution": False,
            "sha_algorithm_used": False, "records": records}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="write plan JSON to a local path")
    args = parser.parse_args()
    result = plan()
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
