# Development & Architecture Notes: TP-Link Router 5G Monitor

## 1. Project Objective
To develop a high-performance Home Assistant custom component for monitoring and managing TP-Link 5G Routers (specifically NX510v and compatible models). The integration leverages the `tplinkrouterc6u` library to extract exhaustive technical signal metrics, data usage statistics, and SMS controls into the Home Assistant ecosystem.

## 2. Architecture & File Structure
The integration follows a modern, asynchronous sub-device architecture, ensuring high performance and logical entity grouping.

### Core Files (`custom_components/tplink_router_5g/`)
- **`api.py`**: A robust async wrapper for the `tplinkrouterc6u` library. It implements traffic consolidation, multi-OID fetching via `req_act`, and specialized parsers for uptime strings.
- **`coordinator.py`**: Centralized `DataUpdateCoordinator`. Manages single-session polling cycles with a 30-second global timeout, built-in resilience, and 0.5s "breathing" delays between calls.
- **`sensor.py`**: Implements 50+ technical and diagnostic sensors, utilizing `SensorDeviceClass.TIMESTAMP` for uptimes.
- **`binary_sensor.py`**: Houses connectivity logic, including the "Best Connection" and "5G ENDC Support" sensors.
- **`switch.py`**: Provides 9 specialized Wi-Fi band controls and the global "Pause Polling" toggle.
- **`button.py` & `number.py`**: Handle stateless actions (Reboot) and runtime configuration (Polling Interval).

## 3. Implementation Details

### Sub-Device Pattern
To prevent UI clutter and mirror the router's internal logic, entities are grouped into five distinct devices:
1.  **Main**: Signal health, system diagnostics, and tower identifiers.
2.  **Data**: Usage statistics, real-time speeds (Downlink/Uplink), and allowance tracking.
3.  **SMS**: Messaging service and diagnostic counters.
4.  **Wi-Fi**: Band-specific toggles for Main, Guest, and IoT networks.
5.  **Clients**: Connected device counts (Wired, Wi-Fi, Guest, IoT).

### 5G & LTE Technical Discovery
Deep technical parity with the router's GUI was achieved by exploiting the `DEV2_LTE_SERVING_CELL_INFO` OID using the Get List (`GL`) operation.
- **Metrics Extracted**: SS-RSRP, SS-RSRQ, SS-SINR, SNR, Modulation (e.g., 256QAM), MCS, Frequencies (DL/UL), Bandwidth (MHz), and Advanced RF (CQI, RI, PMI, TBS, RBS).
- **Consolidation**: All technical OIDs are requested in a single `req_act` array to prevent session drops.

### High-Fidelity Uptime
The NX510v reports uptime as formatted strings (e.g., "0 days 08:47:33"). The `api.py` includes a specialized regex parser that converts these strings into total seconds, allowing Home Assistant to display them as accurate, localized `TIMESTAMP` sensors.

## 4. Performance, Resilience & Code Quality

### Concurrency & Thread Safety
- **Initialization Lock**: The `api.py` utilizes an `asyncio.Lock()` within `_ensure_client` to prevent race conditions when multiple platforms attempt to initialize the library client simultaneously.
- **Non-Blocking**: All library interactions are offloaded to worker threads via `asyncio.to_thread`.

### Robustness & Timeouts
- **Global Timeout**: The `DataUpdateCoordinator` wraps the entire polling cycle in a 30-second `asyncio.timeout` to prevent hung API calls from blocking integration updates.
- **Authoritative Switching**: Wi-Fi switches request an immediate full coordinator refresh after a toggle operation. This ensures the Home Assistant UI reflects the actual state reported by the router rather than an optimistic local mutation.
- **Resource Cleanup**: The Polling Interval entity (`number.py`) implements `async_will_remove_from_hass` to cleanly cancel any pending debounced update tasks upon integration reload.

### Device Identification & Identity
- **Safe Identifiers**: The integration uses the router's LAN MAC address as the primary identifier. If the MAC is unavailable during initial setup, it falls back to a prefixed `host_[IP]` string to prevent device registry conflicts.
- **Standardized Model**: Falls back to "TP-Link Router" if the specific model cannot be probed, ensuring a professional appearance in the HA UI.

### SMS Service
- **Service Registration**: Implements the `tplink_router_5g.send_sms` service, enabling automated outgoing messages. The `api.py` includes a verified `send_sms` method with support check logic.
