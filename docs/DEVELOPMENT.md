# Development & Architecture Notes: TP-Link Router 5G Monitor

## 1. Project Objective
To develop a high-performance Home Assistant custom component for monitoring and managing TP-Link 5G Routers (specifically NX510v and compatible models). The integration leverages the `tplinkrouterc6u` library to extract exhaustive technical signal metrics, data usage statistics, and SMS controls into the Home Assistant ecosystem.

## 2. Architecture & File Structure
The integration follows a modern, asynchronous sub-device architecture, ensuring high performance and logical entity grouping.

### Core Files (`custom_components/tplink_router_5g/`)
- **`api.py`**: A robust async wrapper for the `tplinkrouterc6u` library. It implements traffic consolidation, multi-OID fetching via `req_act`, and specialized parsers for uptime strings and decoded status codes.
- **`coordinator.py`**: Centralized `DataUpdateCoordinator`. Manages single-session polling cycles with built-in resilience, 0.5s "breathing" delays between calls, and "Pause Polling" logic.
- **`sensor.py`**: Implements 50+ technical and diagnostic sensors, utilizing `SensorDeviceClass.TIMESTAMP` for uptimes and `native_unit_of_measurement` for technical metrics.
- **`binary_sensor.py`**: Houses connectivity logic, including the "Best Connection" and "5G ENDC Support" sensors.
- **`switch.py`**: Provides 9 specialized Wi-Fi band controls and the global "Pause Polling" toggle.
- **`button.py` & `number.py`**: Handle stateless actions (Reboot) and runtime configuration (Polling Interval).

## 3. Implementation Details

### Sub-Device Pattern
To prevent UI clutter and mirror the router's internal logic, entities are grouped into five distinct devices:
1.  **Main**: Signal health, system diagnostics, and tower identifiers.
2.  **Data**: Usage statistics, real-time speeds, and allowance tracking.
3.  **SMS**: Messaging service and diagnostic counters.
4.  **Wi-Fi**: Band-specific toggles for Main, Guest, and IoT networks.
5.  **Clients**: Connected device counts (Wired, Wi-Fi, Guest, IoT).

### 5G & LTE Technical Discovery
Deep technical parity with the router's GUI was achieved by exploiting the `DEV2_LTE_SERVING_CELL_INFO` OID using the Get List (`GL`) operation.
- **Metrics Extracted**: SS-RSRP, SS-RSRQ, SS-SINR, SNR, Modulation (e.g., 256QAM), MCS, Frequencies (DL/UL), Bandwidth (MHz), and Advanced RF (CQI, RI, PMI, TBS, RBS).
- **Consolidation**: To prevent the router's web server from dropping connections (`RemoteDisconnected`), all technical OIDs are requested in a single `req_act` array.

### High-Fidelity Uptime
The NX510v reports uptime as formatted strings (e.g., "0 days 08:47:33"). The `api.py` includes a specialized regex parser that converts these strings into total seconds, allowing Home Assistant to display them as accurate, localized `TIMESTAMP` sensors.

### Device Identification
- **MAC-Based Identity**: The integration uses the router's LAN MAC address as the primary identifier in `identifiers` and `connections`. This ensures Home Assistant correctly displays the "MAC: ..." line in the UI and maintains identity stability across IP changes.
- **Manufacturer**: Standardized as "TP-Link" for consistent branding.

## 4. Performance & Stability
- **Non-Blocking**: All library interactions are offloaded to worker threads via `asyncio.to_thread`.
- **Session Management**: Each polling cycle explicitly manages `login` and `logout` to prevent session exhaustion on the router.
- **Data Resilience**: Numeric sensors use a `_safe_int` helper to handle float-string conversions (e.g., "123.0000") without crashing the update cycle.
