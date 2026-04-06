# Development & Architecture Notes: TP-Link Router 5G Monitor

## 1. Project Objective
To develop a high-performance Home Assistant custom component for monitoring and managing TP-Link 5G Routers (specifically NX510v and compatible models). The integration leverages the `tplinkrouterc6u` library to extract signal metrics (RSRP, RSRQ, SNR, 5G Band, Modulation), and data usage features into the Home Assistant ecosystem.

## 2. Architecture & File Structure
The integration follows the standard Home Assistant Custom Component pattern, optimized for asynchronous performance.

### Core Files (`custom_components/tplink_router_5g/`)
- **`api.py`**: Async wrapper for the `tplinkrouterc6u` library. Handles authentication and provides a high-level interface for fetching standard and discovered 5G metrics.
- **`coordinator.py`**: Specialized `DataUpdateCoordinator` implementation. Centralizes polling logic to ensure only one session is used per refresh interval, distributing data to all entities. Includes retry logic and "Pause Polling" detection.
- **`__init__.py`**: Manages the integration lifecycle (setup/unload).
- **`sensor.py`**: Extracts technical metrics and handles transformations.
- **`switch.py`**: Implements "Pause Polling" to stop API traffic without disabling the integration.
- **`button.py`**: Triggers stateless actions (Reboot).
- **`number.py`**: Provides UI control over the `DataUpdateCoordinator` refresh interval with persistent storage in `ConfigEntry` options.
- **`config_flow.py`**: Manages initial setup and reconfiguration via `OptionsFlow`, storing credentials in `entry.options`.

## 3. Implementation Details
The project was refactored to follow a modern async architecture using `DataUpdateCoordinator` and `entry.options` for configuration persistence.

### 5G Metric Discovery
During development, it was discovered that 5G NR metrics (SS-RSRP, SS-RSRQ, etc.) are available on the NX510v via the `DEV2_LTE_SERVING_CELL_INFO` OID using a Get List (`GL`) operation. The `api.py` and `coordinator.py` were specifically updated to probe this OID and extract both LTE Anchor and 5G NR cell data.

## 4. Environment Constraints
- **Async API**: The integration uses asynchronous patterns throughout to avoid blocking the Home Assistant event loop.
- **Shared Session**: The integration uses `async_get_clientsession(hass)` where possible for efficient connection pooling.
