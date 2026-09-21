#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
GATEWAY_DIR="$PROJECT_DIR/gateway"

# Set CycloneDDS network config — wildcard works for macOS WiFi
export CYCLONEDDS_URI='<CycloneDDS><Domain><General><Interfaces><NetworkInterface name="*"/></Interfaces></General></Domain></CycloneDDS>'

echo "Starting Go2 OpenClaw Gateway..."
echo "Make sure you are connected to Go2 WiFi hotspot (192.168.123.161)"

cd "$GATEWAY_DIR"
exec python main.py
