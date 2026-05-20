#!/usr/bin/env bash
# Install meshradio-node-runtime on a fresh Pi hiker node.
# Run as root (or with sudo) from the repo directory on the Pi.
#
# Usage:
#   sudo bash provisioning/install.sh
#
# Assumes:
#   - Repo cloned at /home/pump/projects/manet/meshradio-node-runtime
#   - User 'pump' exists
#   - python3 and pyserial/meshtastic installed system-wide or in /home/pump/.venvs/meshtastic

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_SRC="$REPO_DIR/scripts"
SERVICES_SRC="$REPO_DIR/services"
DEPLOY_USER="${DEPLOY_USER:-pump}"
SCRIPTS_DEST="/home/$DEPLOY_USER"
SYSTEMD_DIR="/etc/systemd/system"

echo "==> meshradio-node-runtime install"
echo "    repo:     $REPO_DIR"
echo "    user:     $DEPLOY_USER"
echo "    scripts → $SCRIPTS_DEST"
echo ""

# 1. Deploy scripts
cp "$SCRIPTS_SRC/telemetry_collector.py"   "$SCRIPTS_DEST/telemetry_collector.py"
cp "$SCRIPTS_SRC/telemetry_sync_spool.sh"  "$SCRIPTS_DEST/telemetry_sync_spool.sh"
chmod +x "$SCRIPTS_DEST/telemetry_sync_spool.sh"
chown "$DEPLOY_USER:$DEPLOY_USER" \
    "$SCRIPTS_DEST/telemetry_collector.py" \
    "$SCRIPTS_DEST/telemetry_sync_spool.sh"
echo "[ok] scripts deployed"

# 2. Deploy readiness/probe scripts (useful for ops remote probing)
for script in node_readiness_report.py node_probe.py; do
    if [ -f "$SCRIPTS_SRC/$script" ]; then
        cp "$SCRIPTS_SRC/$script" "$SCRIPTS_DEST/$script"
        chown "$DEPLOY_USER:$DEPLOY_USER" "$SCRIPTS_DEST/$script"
    fi
done
echo "[ok] probe scripts deployed"

# 3. Install systemd units
cp "$SERVICES_SRC/telemetry_collector.service"   "$SYSTEMD_DIR/"
cp "$SERVICES_SRC/telemetry_sync_spool.service"  "$SYSTEMD_DIR/"
cp "$SERVICES_SRC/telemetry_sync_spool.timer"    "$SYSTEMD_DIR/"
echo "[ok] systemd units installed"

# 4. Create data directories
DATA_DIR="/home/$DEPLOY_USER/telemetry"
mkdir -p "$DATA_DIR/jsonl" "$DATA_DIR/raw"
chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DATA_DIR"
echo "[ok] data directories: $DATA_DIR"

# 5. Reload and enable
systemctl daemon-reload
systemctl enable --now telemetry_collector.service
systemctl enable --now telemetry_sync_spool.timer
echo "[ok] services enabled"

echo ""
echo "==> Verify:"
echo "    systemctl is-active telemetry_collector.service"
echo "    systemctl is-active telemetry_sync_spool.timer"
echo "    python3 $SCRIPTS_DEST/node_probe.py"
echo ""

# Quick status check
systemctl is-active telemetry_collector.service  && echo "    collector: ACTIVE" || echo "    collector: INACTIVE (check journalctl -u telemetry_collector.service)"
systemctl is-active telemetry_sync_spool.timer   && echo "    sync:      ACTIVE" || echo "    sync:      INACTIVE"
