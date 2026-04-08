# Development & Architecture Notes: TP-Link Router 5G Monitor

## 1. Project Objective

To provide a high-performance Home Assistant custom component for TP-Link 5G Routers (specifically the Aginet NX510v). The integration leverages the `tplinkrouterc6u` library to extract exhaustive technical metrics, usage data, and atomic SMS/management controls.

## 2. Architecture & Requirements

### Core Standards

- **HA Version**: Requires **2025.1.0+** for native `asyncio.timeout` support and modern config entry APIs.
- **Asynchronous**: Native async/await throughout; library calls are offloaded to worker threads via `asyncio.to_thread`.
- **Sub-Device Architecture**: Entities are grouped via unique identifiers into linked devices (Main Router, Data Usage, SMS, Wi-Fi, Clients) using Home Assistant's `via_device` chaining.
- **Flat Identity Pattern**: The coordinator maintains flat attributes (`model`, `sw_version`, `mac`) populated from `ConfigEntry.data` at boot. This ensures the Device Registry is stable and populated instantly, even if the router is offline.

### Core Files

- **`api.py`**: Atomic session management. Outgoing commands (SMS, Reboot, Wi-Fi) handle their own `login`/`logout` cycle to prevent session exhaustion.
- **`coordinator.py`**: Centralized polling engine with a 30s global timeout.
- **`sensor.py`**: Implements a declarative `value_fn` callback architecture for technical metrics.
- **`binary_sensor.py`**: Contains specialized logic for network health and connectivity status.

## 3. Implementation Details

### Data Integrity: Declarative Guard Bands

To protect Home Assistant's long-term statistics from "ghost" zeros or impossible raw data spikes (e.g., a 200dBm signal), we use a **Guard Band** system.

- **Implementation**: `min_limit` and `max_limit` are defined directly in the `EntityDescription`.
- **Logic**: The base sensor class verifies these bounds before passing the value to Home Assistant. If a value is outside the band, it is returned as `None` (`Unavailable`).
- **Hardware Workarounds**: Specific metrics like `5G Cell ID` and `5G TAC` use a `min_limit: 1` to filter out hardware-specific "stuck at zero" reporting gaps.

### Advanced Logic: Potential-Based "Best Connection"

The `Best Connection` binary sensor uses a hybrid algorithm (Option D) to reflect the **potential** for high-speed performance, even when the router is idle.

- **Why**: TP-Link routers often put Carrier Aggregation into "sleep" when quiet.
- **Algorithm**: Turns ON if `5G ENDC Support` is active AND both the LTE and 5G legs meet minimum health thresholds for either Power (RSRP) or Quality (SNR).
- **Documentation**: See `docs/best_connection.md` for the specific algorithm thresholds.

### Modern Lifecycle Management

- **Background Setup**: Integration startup uses `entry.async_create_background_task`. This ensures the setup sequence is formally tracked by Home Assistant and automatically cancelled if the integration is unloaded.
- **Clean Unloading**: Standardized cleanup removes the `DOMAIN` key from `hass.data` if no entries remain, preventing memory fragmentation.

## 4. Challenges & Successes

### Uptime Discovery

- **WAN (MBB) Uptime**: Successfully identified the `X_TP_Uptime` attribute within the `MBB` interface of the `DEV2_ADT_WAN` OID.
- **Implementation**: The integration converts this raw seconds value into a stable Home Assistant `TIMESTAMP` rounded to the nearest minute, preventing UI "bouncing" caused by small polling offsets.

### Signal Scaling

Many technical OIDs (like SNR and Transmit Power) report raw integers that are 10x the actual value. The integration applies a 0.1 scaling factor and 1-decimal precision to these sensors to ensure accurate real-world representation.

## 5. Hardware Identity & Non-Blocking Startup

To achieve a **0ms startup impact**, the integration treats persistent metadata as the authoritative identity at boot.

### Discovery & Persistence

- **Initial Setup**: During the configuration flow, a one-time "Identity Fetch" retrieves the Model, MAC, and Firmware versions.
- **Storage**: This data is persisted in `ConfigEntry.data`.
- **Initialization**: On Home Assistant restart, the `TPLinkRouterDataUpdateCoordinator` initializes its identity attributes directly from this memory-resident data before any network calls occur.
