# TP-Link Router 5G Monitor for Home Assistant

![HACS Integration](https://img.shields.io/badge/HACS-Integration-orange.svg) ![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5?logo=homeassistant&logoColor=white) ![Latest Release](https://img.shields.io/github/v/release/PlayFaster/ha-tplink-router-5g-monitor?label=Release&logo=github) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![Validate](https://github.com/PlayFaster/ha-tplink-router-5g-monitor/actions/workflows/validate.yaml/badge.svg)](https://github.com/PlayFaster/ha-tplink-router-5g-monitor/actions/workflows/validate.yaml) ![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/PlayFaster/ha-tplink-router-5g-monitor/python-coverage-comment-action-data/coverage-badge.json) ![Last Commit](https://img.shields.io/github/last-commit/PlayFaster/ha-tplink-router-5g-monitor?label=Last%20commit)

Home Assistant integration for TP-Link NX510v 5G Router that provides detailed signal statistics and data usage tracking.

- This integration is based on the excellent [TP-Link Router](https://github.com/AlexandrErohin/home-assistant-tplink-router) Integration, and has been expanded to provide a large amount of 5G/LTE signal metrics.
- If you have an NX510v and want to closely monitor your connection, this integration is for you!
- If you are looking for a general TP-Link Router integration, I highly recommend [TP-Link Router](https://github.com/AlexandrErohin/home-assistant-tplink-router).

**Note:** This integration is based on and extends the [TP-Link Router](https://github.com/AlexandrErohin/home-assistant-tplink-router) integration. It focuses on **5G/LTE signal metrics** not available in the base integration. For general TP-Link router monitoring, see the [original integration](https://github.com/AlexandrErohin/home-assistant-tplink-router).

## 🔧 Requirements & Compatibility

**Home Assistant:**

- Minimum: Home Assistant 2025.1

**Router:**

- **Tested**: TP-Link NX510v *May work with other TP-Link 5G devices, but has only been tested with NX510v.*
- **Not compatible**: Non-TP-Link routers, older TP-Link models without 5G

**Network:**

- Router must be accessible from your Home Assistant instance

## Supported Models

- **TP-Link NX510v** – TP-Link Aginet AX3000 5G Indoor Router with WiFi 6
 
*May work with other TP-Link 5G devices, but has only been tested with NX510v.*

## ✅ Features 

### Core Monitoring

- **5G/LTE Signal Metrics**: RSRP, RSRQ, RSSI, SNR for both 5G and anchor LTE connections
- **Advanced 5G Data**: CQI, Modulation, MCS, Resource Blocks, TX Power
- **Data Usage Tracking**: Real-time daily and monthly usage, monthly limits, remaining data
- **Connected Clients**: Total count, breakdown by connection type (WiFi/Wired)
- **Basic SMS Management**: Unread SMS flag.
- **Router Management**: Reboot control, separate WiFi band management
- **Router Stats**: CPU and Memory percentage.

### Smart Features

- **Resilient Polling**: Automatic retry with grace period prevents "Unavailable" flickering
- **WiFi Band Control**: Manage 2.4G/5G/6G separately for Main, Guest, and IoT networks
- **Pause Polling**: Switch to stop polling when you need direct router access (TP-Link limits one login)
- **Configurable Update Interval**: From 30 seconds to 1 hour.
- **Organized Device Grouping**: Entities logically organized by function - 5G/LTE, Data Usage, SMS and WiFi.

### Why This Integration?

- ✅ **5G-specific metrics** not in base TP-Link integration
- ✅ **Signal analytics** for troubleshooting connection issues
- ✅ **Granular WiFi control** (separate main/guest/IoT networks)
- ✅ **Data usage tracking** with monthly limits and remaining data

## 📊 What You Get

This integration creates approximately **60+ entities**:

| Type | Count | Examples |
|------|-------|----------|
| Sensors | 40+ | Signal strength, data usage, uptime, device info |
| Switches | 10 | Wi-Fi control (2.4G/5G/6G), Pause Polling |
| Binary Sensors | 3 | Roaming status, 5G support, Best Connection |
| Buttons | 1 | Reboot |
| Numbers | 1 | Polling interval control |

Organized into logical devices: **Main Router**, **Data Usage**, **Wi-Fi Control**

> [!TIP]
>
> **You can Disable Unnecessary Devices**
>
> - If you are running in Bridge Mode you may not be interested in WiFi controls or client data.
> - These devices and their entities can be disabled from the main device page.
>   - Three dots menu per device, "Disable Device"

## ❔ Whats Missing?

- SMS Management: The integration has a sensor for unread SMS, but to read SMS or manage the Router SMS Inbox you must use the device GUI.


## 📸 Screenshots

### Integration Overview

![Integration](.github/images/TP-Link_5g_integration_screen.png)

### Signal & Controls

![Sensors](.github/images/TP-Link_5g_sensor_control_info.png)

### Data Usage

![Data](.github/images/TP-Link_5g_data_info.png)

### SMS Management

![SMS](.github/images/TP-Link_5g_sms_info.png)

## ✨ Installation

### HACS (Recommended)

1. Add this repository as a **Custom Repository** in HACS:
   - Open HACS in Home Assistant
   - Click **Custom repositories** (⋮ menu)
   - Add repository URL and Type: `Integration`
2. Search for "TP-Link Router 5G Monitor" and click **Download**
3. Restart Home Assistant
4. Go to **Settings > Devices & Services > Add Integration** and search for "TP-Link Router 5G Monitor"

### Manual Installation

1. Download the repository
2. Copy the `custom_components/tplink_router_5g` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. Go to **Settings > Devices & Services > Add Integration** and search for "TP-Link Router 5G Monitor"

## ⚙️ Configuration

Setup is handled entirely via the UI. You will need:

- **Router IP Address** (e.g., 192.168.1.1)
- **Router Username** ( try `user` or `admin` )
- **Admin Password** (your local login, a TP-Link cloud login will not work)
- **Scan Interval** (optional, default 2 minutes, range 30s to 1 hour)
- **Verify SSL** (optional, for HTTPS connections)

After setup, you can modify options (i.e. password change etc). anytime: **Settings > Devices & Services > TP-Link Router 5G Monitor > Options**

## ❓ FAQ

**Q: Does this work with [my router model]?**  
A: Only tested with TP-Link NX510v. May work with other TP-Link 5G models, but untested.

**Q: Why can't I access the router web UI while Home Assistant is connected?**  
A: TP-Link limits one simultaneous login. Use the "Pause Polling" switch in Home Assistant to temporarily stop polling, then access the router. Resume polling when done.

**Q: How many sensors and switches will be created?**  
A: Approximately 60+ entities total (sensors, switches, binary sensors, buttons, numbers). See table above.

**Q: How often does it update?**  
A: Default every 2 minutes. Configurable from 30 seconds to 1 hour during setup or in options.

**Q: Does this require cloud connectivity?**  
A: No. This is local-only. Your router does not a TP-Link cloud account for this integration.

## 🔧 Troubleshooting

### "Failed to connect to router"

- Verify the IP address is correct (check your router or DHCP settings)
- Confirm username is set (`user` or `admin` for TP-Link)
- Verify password is correct (case-sensitive)
- Ensure the router is powered on and not rebooting

### Only some sensors showing, or showing "Unavailable" or "Unknown"

- Your router firmware may differ from the tested version
- Some metrics may not be available on your specific model
- Check logs for errors during initialization

## 📝 Maintenance Status

This is a **personal project**. Support and updates are provided on a **"best-effort"** basis only. While I use this integration daily and aim to keep it functional with the latest Home Assistant releases, I cannot guarantee immediate fixes for issues or compatibility with all router firmware versions.

## 🤝 Contributors & Acknowledgements

- 🙏 Special Thanks: This project is based on the original work done by @AlexandrErohin and contributors on the TP-Link Router [API](https://github.com/AlexandrErohin/TP-Link-Archer-C6U) and [Integration](https://github.com/AlexandrErohin/home-assistant-tplink-router). A big thanks for the heavy lifting!
- This project was developed with the assistance of AI to ensure code quality and adherence to best practices.

## 📄 License [![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This project is licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

---

**Questions or Issues?** Visit the [GitHub repository](https://github.com/PlayFaster/ha-tplink-router-5g-monitor).
