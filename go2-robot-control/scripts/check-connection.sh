#!/usr/bin/env bash
set -euo pipefail

GO2_IP="192.168.123.161"

echo "Checking connection to Unitree Go2 at $GO2_IP ..."

if ping -c 3 -W 2 "$GO2_IP" > /dev/null 2>&1; then
    echo "✓ Go2 is reachable at $GO2_IP"
    exit 0
else
    echo "✗ Cannot reach Go2 at $GO2_IP"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Make sure Go2 is powered on"
    echo "  2. Connect to WiFi hotspot: Unitree_Go2_XXXX"
    echo "  3. Your IP should be in 192.168.123.x range"
    exit 1
fi
