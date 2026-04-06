# Development & Architecture Notes: TP-Link Router 5G Monitor

## 1. Project Objective

To provide a high-performance Home Assistant custom component for TP-Link 5G Routers (NX510v). The integration leverages the `tplinkrouterc6u` library to extract exhaustive technical metrics, usage data, and basic SMS controls.

## 2. Architecture & Requirements

### Core Standards

- **HA Version**: Requires **2025.1.0+** for native `asyncio.timeout` support.
- **Asynchronous**: Native async/await throughout; library calls offloaded via `asyncio.to_thread`.
- **Sub-Device Architecture**: Entities are grouped via MAC/Host identifiers into linked devices (Main, Data, SMS, Wi-Fi, Clients) using `via_device` references.

### Core Files

- **`api.py`**: Atomic session management. Outgoing commands (SMS, Reboot, Wi-Fi) handle their own `login`/`logout` cycle.
- **`coordinator.py`**: Centralized polling with a 30s global timeout and 0.5s "breathing" delays between OID requests. Default interval is 120s.
- **`sensor.py` & `binary_sensor.py`**: Group diagnostic and technical metrics. All RF/technical metrics are marked as `EntityCategory.DIAGNOSTIC`.

## 3. Implementation Details

### Session Reliability

To prevent session leaks or router lockups, all administrative commands are wrapped in `try-finally` blocks to ensure `logout` is called even if the command fails. outgoing services like `send_sms` are atomic.

### Validation & Quality

- **Testing**: A full Pytest suite resides in `tests/`. It mocks the API and Coordinator to verify state logic without physical hardware.
- **Linting**: 100% compliant with `ruff` (PEP-8) and `yamllint`.
- **Typing**: Strict type hinting is used for all public setup and update functions.

## 4. Known Limitations

### Uptime Reporting

Device and WAN uptime reporting via standard OIDs is inconsistent on current NX510v firmware. These sensors have been fully removed to prevent UI clutter. Documentation for future probing is available in `docs/finding_time.md`.

### Translation Support

The polling interval number entity uses a `translation_key` corresponding to `strings.json` for proper localization.
