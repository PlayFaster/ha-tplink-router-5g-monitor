# Changelog: TP-Link Router 5G Monitor

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-04-07

### Added

- **WAN Uptime Sensor**: Restored the WAN Uptime sensor using the `MBB` interface uptime, converted to a stable Home Assistant timestamp (rounded to the minute).

### Fixed

- **Data Tracking**: Corrected "Monthly Data Remaining" logic to use `totalStatistics` subtracted from the data limit.
- **Wi-Fi Control**: Fixed functional regressions in Wi-Fi toggles by adopting the `Connection` Enum and correcting internal property mapping (removing `wifi_` prefix from status checks).
- **Task Automation**: Refactored VS Code `tasks.json` to use native `dependsOn` sequences, ensuring validation steps run reliably even after linting fixes.
- **Test Suite**: Updated 56 unit tests to align with the improved API logic and Enum-based Wi-Fi control.

## [1.0.0] - 2026-04-06

### Added

- **Sub-Device Architecture**: Entities are now logically grouped into linked devices (Main, Data, SMS, Wi-Fi, Clients).
- **Deep 5G & LTE Metrics**: Exhaustive mapping for NR (5G) and LTE Anchor cells including Frequencies, Modulation (256QAM), MCS, and Advanced RF diagnostics (CQI, PMI, RI, etc.).
- **Comprehensive Test Suite**: 30+ Pytest unit tests covering API, Coordinator, Config Flow, and all Entity platforms.
- **Input Validation**: Added strict range validation (30s - 7200s) for the polling interval in the configuration flow.
- **Robust Session Management**: Atomic `login`/`logout` handling within `send_sms`, `reboot`, and Wi-Fi toggles to prevent session leaks.
- **Native Async Timeouts**: Implemented native `asyncio.timeout` for all polling cycles.

### Changed

- **HA Requirement**: Increased minimum Home Assistant version to **2025.1.0** to leverage native async features.
- **Standardized Polling**: Set the default polling interval to **120 seconds** for improved router stability.
- **Diagnostic Categorization**: Moved technical/signal sensors and binary sensors to the `DIAGNOSTIC` entity category for a cleaner main UI.
- **Performance Engine**: Optimized `req_act` calls to fetch all technical metrics in a single session.
- **Type Safety**: Applied comprehensive Python type hints across the entire codebase.

### Fixed

- **Ruff Compliance**: Resolved 100+ linting errors (E501, E701, etc.) for PEP-8 compliance.
- **YAML Standards**: Fixed missing document start in `services.yaml`.
- **Race Conditions**: Implemented `asyncio.Lock` in API initialization to prevent concurrent client creation.
- **Task Leaks**: Added proper cleanup for debounced tasks in `number.py`.

### Removed

- **Uptime Sensors**: Removed unstable `Device Uptime` and `WAN Uptime` sensors due to firmware reporting inconsistencies. Documentation for future restoration is preserved in `docs/finding_time.md`.

---

### Format

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
