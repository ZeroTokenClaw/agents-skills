"""Configuration constants for Go2 gateway."""

# Unitree Go2 WiFi hotspot IP (fixed when connected to Go2's AP)
GO2_IP = "192.168.123.161"

# Gateway HTTP server
GATEWAY_HOST = "0.0.0.0"
GATEWAY_PORT = 8520

# Safety limits
MAX_SPEED = 0.5        # m/s — hard cap enforced at gateway level
DEFAULT_SPEED = 0.3    # m/s — used when caller omits speed
DEFAULT_DURATION = 1.0 # seconds — default movement duration
MAX_DURATION = 10.0    # seconds — max single movement duration

# CycloneDDS network config (wildcard for macOS WiFi interface)
CYCLONEDDS_URI = """<?xml version="1.0" encoding="UTF-8" ?>
<CycloneDDS xmlns="https://cdds.io/config">
  <Domain>
    <General>
      <Interfaces>
        <NetworkInterface name="*" />
      </Interfaces>
    </General>
  </Domain>
</CycloneDDS>"""

# Battery threshold for dangerous actions
BATTERY_MIN_FOR_BACKFLIP = 20  # percent
