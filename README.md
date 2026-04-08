# TP-Link Router 5G Monitor for Home Assistant

![HACS Integration](https://img.shields.io/badge/HACS-Integration-orange.svg) ![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5?logo=homeassistant&logoColor=white) ![Latest Release](https://img.shields.io/github/v/release/PlayFaster/ha-tplink-router-5g-monitor?label=Release&logo=github) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![Validate](https://github.com/PlayFaster/ha-tplink-router-5g-monitor/actions/workflows/validate.yaml/badge.svg)](https://github.com/PlayFaster/ha-tplink-router-5g-monitor/actions/workflows/validate.yaml) ![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/PlayFaster/ha-tplink-router-5g-monitor/python-coverage-comment-action-data/coverage-badge.json) ![Last Commit](https://img.shields.io/github/last-commit/PlayFaster/ha-tplink-router-5g-monitor?label=Last%20commit)

Home Assistant integration for TP-Link NX510v 5G Router that provides detailed signal statistics and data usage tracking.

A high-performance Home Assistant integration specifically designed for the **TP-Link NX510v 5G Router**. This component provides exhaustive signal diagnostics and data tracking that go far beyond standard router integrations.

> [!NOTE] This project extends the excellent work of [AlexandrErohin/home-assistant-tplink-router](https://github.com/AlexandrErohin/home-assistant-tplink-router). It is optimized for 5G/LTE metrics and modern Home Assistant standards.

---

- This integration is based on the excellent [TP-Link Router](https://github.com/AlexandrErohin/home-assistant-tplink-router) Integration, and has been expanded to provide a larger amount of 5G/LTE signal metrics.
- If you have an NX510v and want to closely monitor your connection, this integration is for you!
- If you are looking for a general TP-Link Router integration, I highly recommend [TP-Link Router](https://github.com/AlexandrErohin/home-assistant-tplink-router).

## 🔧 Compatibility & Requirements

**Router Hardware:**

- **Supported**: **TP-Link NX510v** – TP-Link Aginet AX3000 5G Indoor Router with WiFi 6
  - _May work with other TP-Link 5G devices, but has only been tested with NX510v_
- **Potentially Compatible**: Other TP-Link 5G routers using the Aginet firmware.
- **Not Supported**: Non-TP-Link hardware or older TP-Link models without 5G.

**Network:**

- Local network access to the router is required. (Cloud login is not used).

**Home Assistant Version:**

- Minimum: Home Assistant **2025.1**

---

## ✅ Features

### 📡 Advanced 5G/LTE Diagnostics

- **Detailed Signal Metrics**: RSRP, RSRQ, RSSI, and SNR for both the 5G (NR) and the LTE Anchor cell.
- **RF Engineering Data**: Monitor CQI, Modulation (up to 256QAM), MCS, Resource Blocks, and Transmit Power.
- **Frequency Tracking**: Identify active 5G/LTE bands and ARFCN channels.

### 📊 Comprehensive Monitoring

- **Sub-Device Organization**: Entities are automatically grouped into logical devices: **Main Router**, **Data Usage**, **SMS**, **Wi-Fi**, and **Clients**.
- **Data Usage Tracking**: Real-time daily/monthly usage stats, limits, and remaining balance.
- **Device Health**: Monitor Router CPU and Memory load.
- **Client Tracking**: Total client counts with connection type breakdown (Wired vs Wi-Fi).

### ⚡ Performance & UX

- **Zero-Blocking Startup**: Home Assistant starts instantly. Hardware identity is loaded from memory, while the first poll happens quietly in the background.
- **Flat Identity Pattern**: Device information (Model, MAC, Version) remains stable and visible even if the router is temporarily offline.
- **Native Resilience**: Built-in 30s timeouts and automatic retry logic ensure UI stability during intermittent network glitches.

### Core Monitoring

- **5G/LTE Signal Metrics**: RSRP, RSRQ, RSSI, SNR for both 5G and anchor LTE connections
- **Advanced 5G Data**: CQI, Modulation, MCS, Resource Blocks, TX Power
- **Plus Core Features** from original integration.
  - **Data Usage Tracking**: Real-time daily and monthly usage, monthly limits, remaining data
  - **Connected Clients**: Total count, breakdown by connection type (WiFi/Wired)
  - **Basic SMS Management**: Unread SMS flag, Send SMS service
  - **Router Management**: Reboot control, WiFi control switches
  - **Router Stats**: CPU and Memory percentage.

### Smart Features

- **Pause Polling**: Switch to stop polling when you need direct router access (TP-Link limits one login)
- **Configurable Update Interval**: From 30 seconds to 1 hour
- **Organized Device Grouping**: Entities logically organized by function - 5G/LTE, Data Usage, SMS and WiFi
- **Resilient Polling**: Automatic retry with grace period prevents "Unavailable" flickering
- **WiFi Band Control**: Manage 2.4G/5G/6G separately for Main, Guest, and IoT networks

### Why This Integration?

- ✅ **5G-specific metrics** not in base TP-Link integration
- ✅ **Signal analytics** for troubleshooting connection issues
- ✅ **Plus Core Features** from original integration.
  - ✅ **Data usage tracking** with monthly limits and remaining data
  - ✅ **Granular WiFi control** (separate main/guest/IoT networks)

## 📊 What You Get

This integration provides **90+ entities** across several platforms:

| Type               | Count | Primary Functions                                |
| :----------------- | :---- | :----------------------------------------------- |
| **Sensors**        | 70+   | Signal strength, data usage, uptime, device info |
| **Switches**       | 10    | Pause Polling or Toggle Wi-Fi                    |
| **Binary Sensors** | 3     | Roaming status, 5G support, Best Connection      |
| **Controls**       | 3     | Reboot, Polling Interval, SMS service            |

Organized into logical devices: **Main Router**, **Data Usage**, **Wi-Fi Control**

> [!TIP]
>
> **Clean up your UI: Disable Unnecessary Devices or Entities**
>
> - If you are running in Bridge Mode you may not be interested in WiFi controls or client data.
> - These devices and their entities can be disabled from the main device page (three dots menu per device, "Disable Device").
> - Individual entities can, as alway in Home Assistant, by disabled via the entity properties, or in bulk on the entities list page.

## ❔ What's Missing?

- SMS Management: While the integration provides unread SMS counts and a Send SMS service, reading SMS messages or managing the Router SMS Inbox requires using the router's web interface.

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

1. Download the [latest release](https://github.com/PlayFaster/ha-tplink-router-5g-monitor/releases).

1. Copy the `custom_components/tplink_router_5g` folder to your Home Assistant `custom_components` directory
1. Restart Home Assistant
1. Go to **Settings > Devices & Services > Add Integration** and search for "TP-Link Router 5G Monitor"

## ⚙️ Configuration

Setup is handled entirely via the UI under **Settings > Devices & Services > Add Integration**.

Setup is handled entirely via the UI. You will need:

- **IP Address**: The local IP of your router (e.g., `192.168.1.1`).
- **Username**: Usually `user` or `admin`.
- **Password**: Your local admin password (not your TP-Link Cloud password).
- **Scan Interval**: Default is 2 minutes (adjustable from 30s to 1 hour).

- **Router IP Address** (e.g., 192.168.1.1)
- **Router Username** ( try `user` or `admin` )
- **Admin Password** (your local login, a TP-Link cloud login will not work)
- **Scan Interval** (optional, default 2 minutes, range 30s to 1 hour)
- **Verify SSL** (optional, for HTTPS connections)

After setup, you can modify options (i.e. password change etc). anytime: **Settings > Devices & Services > TP-Link Router 5G Monitor > Options**

---

## ❓ FAQ & Troubleshooting

**Q: Why can't I access the router web UI while this is connected?**  
A: TP-Link routers often limit sessions to one simultaneous login. Use the **Pause Polling** switch in Home Assistant to temporarily release the session.

**Q: My entities are showing "Unavailable" or "Unknown".**  
A: This is normal during a router reboot or if the router is unreachable. The integration will automatically recover once connection is restored. Check your Home Assistant logs for specific error messages.

**Q: Does this work with mesh satellites?**  
A: No. This integration should be installed on the **Main Router** only.

---

## ❓ FAQ

**Q: Does this work with [my router model]?**  
A: Only tested with TP-Link NX510v. May work with other TP-Link 5G models, but untested.

**Q: Why can't I access the router web UI while Home Assistant is connected?**  
A: TP-Link limits one simultaneous login. Use the "Pause Polling" switch in Home Assistant to temporarily stop polling, then access the router. Resume polling when done.

**Q: How many sensors and switches will be created?**  
A: Approximately 90+ entities total (sensors, switches, binary sensors, buttons, numbers). See table above. Individual sub-device or entities can be disabled if not required, as per Home Assistant normal use.

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

**Questions or Issues?** Visit the [GitHub repository](https://github.com/PlayFaster/ha-tplink-router-5g-monitor). r).
