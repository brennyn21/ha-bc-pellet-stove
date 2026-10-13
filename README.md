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
5. Enter the stove's LAN IP address. Repeat for each stove. Each stove is named from its app username (`mqttUsername` in `/status`).

### Manual

1. Copy `custom_components/bc_pellet_stove` into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration** and search for **BC Pellet Stove**.
4. Enter the stove's LAN IP. Repeat **Add integration** for each additional stove.

### Finding the IP address

Open the stove's built-in web UI at `http://<ip>/`, or check your router's DHCP client list. The module hostname is usually `PellStoveWifi`.

## Configuration

| Setting | Description |
|---------|-------------|
| **Host** | IP address or hostname (e.g. `192.168.1.50`) |
| **Port** | HTTP port, default `80` |

Add the integration once per stove. Each stove is its own device. The device name is the module's MQTT username (`mqttUsername` in `/status`, for example `brennyn21`). If MQTT is disabled and that field is missing, the name falls back to `Pellet Stove (<ip>)`.

The integration polls `/status` every **10 seconds**.

### Changing the IP address

When a stove gets a new DHCP address:

1. Go to **Settings → Devices & services**.
2. Open **BC Pellet Stove** and select that stove.
3. Choose **Reconfigure** and enter the new IP (and port, if it is not 80).

The existing device and entity history stay in place. Home Assistant checks that the new address responds to `/status` before saving it.

## Entities

| Entity | Type | HTTP |
|--------|------|------|
| Power | Switch | `GET /power` (toggle when state must change) |
| Current temperature | Sensor | `/status` → `currentTemp` |
| Set temperature | Number | `GET /settemp?val=&unit=` |
| Burn level | Number (1–5) | `GET /level?val=` |
| Mode | Select | `GET /mode/manual`, `/mode/temp`, `/mode/thermostat`, `/mode/weekly` |
| Turn off above | Number (0–40, 0 = off). Hidden unless mode is Temp | `GET /turnoffabove?val=` |
| Turn on below | Number (0–40, 0 = off). Hidden unless mode is Temp | `GET /turnonbelow?val=` |
| Error | Binary sensor | `/status` → `error` |
| Error code | Sensor (diagnostic) | `/status` → `errorCode` |
| Child lock | Binary sensor (read-only) | `/status` → `childLock` |
| Initialized | Binary sensor (diagnostic) | `/status` → `initialized` |
| Firmware version | Sensor (diagnostic) | `/status` → `firmwareVersion` |
| WiFi RSSI | Sensor (diagnostic) | `/status` → `wifiRSSI` |

Child lock is read-only over local HTTP (no control endpoint on the device).

## Requirements

- Home Assistant 2024.11+
- Pellet Stove WiFi firmware with local HTTP API (`/status`, `/power`, `/settemp`, `/level`, `/mode/*`, `/turnoffabove`, `/turnonbelow`)
- Home Assistant on the same LAN as the stove

## Firmware

Pellet Stove WiFi module firmware and documentation: https://stove.bcinnovate.com/PelletStoveWifiModule.pdf