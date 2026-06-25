# BC Pellet Stove — Home Assistant

Local Home Assistant integration for the BCInnovate Pellet Stove WiFi module. Polls `GET /status` on your LAN and controls the stove over simple HTTP GET requests. No cloud account or MQTT broker required.

Works entirely on your local network. Home Assistant must be able to reach the stove's IP address.

## Repository layout

This repository is the HACS integration only:

```
/
├── hacs.json
├── README.md
└── custom_components/
    └── bc_pellet_stove/
```

## Install

### HACS (recommended)

1. In HACS, open **Integrations** → **⋮** (top right) → **Custom repositories**.
2. Add `https://github.com/brenny21/ha-bc-pellet-stove`, category **Integration**, then click **Add**.
3. Search for **BC Pellet Stove**, install, and restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration** and select **BC Pellet Stove**.
5. Enter the stove's LAN IP address.

### Manual

1. Copy `custom_components/bc_pellet_stove` into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration** and search for **BC Pellet Stove**.
4. Enter the stove's LAN IP.

### Finding the IP address

Open the stove's built-in web UI at `http://<ip>/`, or check your router's DHCP client list. The module hostname is usually `PellStoveWifi`.

## Configuration

| Setting | Description |
|---------|-------------|
| **Host** | IP address or hostname (e.g. `192.168.1.50`) |
| **Port** | HTTP port, default `80` |

The integration polls `/status` every **10 seconds**. All entities appear under one **Pellet Stove** device.

## Entities

| Entity | Type | HTTP |
|--------|------|------|
| Power | Switch | `GET /power` (toggle when state must change) |
| Current temperature | Sensor | `/status` → `currentTemp` |
| Set temperature | Number | `GET /settemp?val=&unit=` |
| Burn level | Number (1–5) | `GET /level?val=` |
| Mode | Select | `GET /mode/manual`, `/mode/temp`, `/mode/thermostat`, `/mode/weekly` |
| Error | Binary sensor | `/status` → `error` |
| Error code | Sensor (diagnostic) | `/status` → `errorCode` |
| Child lock | Binary sensor (read-only) | `/status` → `childLock` |
| Initialized | Binary sensor (diagnostic) | `/status` → `initialized` |
| Firmware version | Sensor (diagnostic) | `/status` → `firmwareVersion` |
| WiFi RSSI | Sensor (diagnostic) | `/status` → `wifiRSSI` |

Child lock is read-only over local HTTP (no control endpoint on the device).

## Requirements

- Home Assistant 2023.8+
- Pellet Stove WiFi firmware with local HTTP API (`/status`, `/power`, `/settemp`, `/level`, `/mode/*`)
- Home Assistant on the same LAN as the stove

## Firmware

Pellet Stove WiFi module firmware and documentation: https://stove.bcinnovate.com/PelletStoveWifiModule.pdf