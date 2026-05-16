# MeshRadio Node Runtime

Baseline runtime for all hiker/field nodes.

## Includes
- telemetry collection (`scripts/telemetry_collector.py`)
- store-and-forward sync (`scripts/telemetry_sync_spool.sh`)
- standardized diagnostics + provisioning stubs

## Offline/mobile behavior
- Node writes telemetry locally first (`raw/` + `jsonl/`).
- Loss of Internet does **not** stop collection.
- Sync job retries every 2 minutes and forwards backlog when link returns.

## Deploy sync spool
Copy files to target Pi and enable timer:

```bash
sudo install -m 0755 scripts/telemetry_sync_spool.sh /home/pump/telemetry_sync_spool.sh
sudo install -m 0644 services/telemetry_sync_spool.service /etc/systemd/system/telemetry_sync_spool.service
sudo install -m 0644 services/telemetry_sync_spool.timer /etc/systemd/system/telemetry_sync_spool.timer
sudo systemctl daemon-reload
sudo systemctl enable --now telemetry_sync_spool.timer
sudo systemctl start telemetry_sync_spool.service
sudo systemctl status telemetry_sync_spool.timer --no-pager
```
