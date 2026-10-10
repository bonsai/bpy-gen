#!/usr/bin/env python3
"""Append render metadata to JSONL ledger."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LEDGER = Path.home() / "bpy-gen" / "outputs" / ".ledger.jsonl"


def append(model: str, output: str, status: str, duration_sec: float | None = None):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "output": output,
        "status": status,
        "duration_sec": duration_sec,
    }
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    output = sys.argv[2] if len(sys.argv) > 2 else ""
    status = sys.argv[3] if len(sys.argv) > 3 else "ok"
    append(model, output, status)
