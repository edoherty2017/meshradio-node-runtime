#!/usr/bin/env python3
"""PASS/FAIL probe for the hiker node: serial, collector health, sync backlog.

Runs ON the Pi hiker node. Exits 0 (PASS) if all checks clear, 1 (FAIL) otherwise.

Checks:
  - /dev/lora_radio is present
  - telemetry_collector.service is active
  - telemetry_sync_spool.timer is active
  - JSONL is not stale (last record < 5 min old)
  - connectivity_mode.state file exists

Usage:
  python3 scripts/node_probe.py
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

SERIAL_PORT = os.environ.get("LORA_PORT", "/dev/lora_radio")
OUT_DIR     = os.environ.get("OUT_DIR",   "/home/pump/telemetry")

JSONL_STALE_SECONDS = 300


def svc_state(name: str) -> str:
    r = subprocess.run(["systemctl", "is-active", name], capture_output=True, text=True)
    return r.stdout.strip()


def jsonl_age(jsonl_path: Path) -> float | None:
    if not jsonl_path.exists():
        return None
    size = jsonl_path.stat().st_size
    last_ts = None
    try:
        with jsonl_path.open("rb") as f:
            f.seek(max(0, size - 8192))
            tail = f.read().decode("utf-8", errors="ignore").splitlines()
        for line in reversed(tail):
            try:
                obj = json.loads(line)
                ts = obj.get("timestamp_utc")
                if ts:
                    last_ts = ts
                    break
            except Exception:
                pass
    except Exception:
        return None
    if not last_ts:
        return None
    try:
        ts_dt = dt.datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
        return (dt.datetime.now(dt.timezone.utc) - ts_dt).total_seconds()
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=OUT_DIR)
    args = ap.parse_args()

    out_dir  = Path(args.out_dir)
    jsonl    = out_dir / "jsonl" / "telemetry_stream.jsonl"
    now      = dt.datetime.now(dt.timezone.utc).isoformat()

    results: list[dict] = []

    # 1. Serial port
    port_present = Path(SERIAL_PORT).exists()
    results.append({
        "check": "serial_port_present",
        "ok": port_present,
        "path": SERIAL_PORT,
        "device": str(Path(SERIAL_PORT).resolve()) if port_present else None,
    })

    # 2. Collector service
    col_state = svc_state("telemetry_collector.service")
    results.append({
        "check": "collector_service_active",
        "ok": col_state == "active",
        "state": col_state,
    })

    # 3. Sync timer
    sync_state = svc_state("telemetry_sync_spool.timer")
    results.append({
        "check": "sync_timer_active",
        "ok": sync_state == "active",
        "state": sync_state,
    })

    # 4. JSONL freshness
    age = jsonl_age(jsonl)
    jsonl_ok = age is not None and age < JSONL_STALE_SECONDS
    results.append({
        "check": "jsonl_fresh",
        "ok": jsonl_ok,
        "age_seconds": round(age) if age is not None else None,
        "path": str(jsonl),
    })

    # 5. Connectivity mode state file
    state_path = out_dir / "connectivity_mode.state"
    results.append({
        "check": "connectivity_mode_state",
        "ok": state_path.exists(),
        "path": str(state_path),
    })

    overall = all(r["ok"] for r in results)
    report = {
        "pass": overall,
        "probed_at_utc": now,
        "checks": results,
    }
    print(json.dumps(report, indent=2))
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
