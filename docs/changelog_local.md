# Changelog: TP-Link Router 5G Monitor

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-04-08

### Added

- **Option C Guard Bands**: Implemented a declarative guard band system for 50+ sensors. Impossible values (e.g., 200dBm signal) or raw data spikes are automatically marked as `Unavailable` to protect UI data integrity.
- **Improved 5G Accuracy**: Applied `min_limit: 1` to 5G Cell ID, 5G TAC, and 5G Uplink Frequency to handle hardware-specific "stuck at zero" reporting.
- **Potential-Based "Best Connection"**: Refactored the `Best Connection` binary sensor using a hybrid algorithm (Option D) that accounts for both Signal Power (RSRP) and Signal Quality (SNR). This ensures the sensor reflects "potential" performance even during idle periods.
- **Persistent Metadata**: The integration fetches and stores the hardware model, MAC address, and firmware versions in the `ConfigEntry` during setup.
- **WAN Uptime Sensor**: Restored the WAN Uptime sensor using the `MBB` interface uptime, converted to a stable Home Assistant timestamp (rounded to the minute).
- **Sub-Device Architecture**: Entities are logically grouped into linked devices (Main, Data, SMS, Wi-Fi, Clients).
- **Deep 5G & LTE Metrics**: Exhaustive mapping for NR (5G) and LTE Anchor cells.
- **Comprehensive Test Suite**: 50+ Pytest unit tests.
- **Robust Session Management**: Atomic `login`/`logout` handling within administrative commands.

### Changed

- **Signal Scaling (0.1x)**: Applied correct 0.1 scaling and 1-decimal precision to 5G Transmit Power, 5G SNR, and LTE Anchor SNR to reflect real-world values.
- **MCS Retransmission Support**: Increased maximum MCS limits from 28 to 31 to accommodate HARQ retransmission states reported by the router.
- **Modern Background Tasks**: Migrated the non-blocking startup sequence to the modern `entry.async_create_background_task` API.
- **Non-Blocking Startup**: Removed the initial blocking data fetch during integration setup.
- **HA Requirement**: Increased minimum Home Assistant version to **2025.1.0**.
- **Standardized Polling**: Set the default polling interval to **120 seconds**.
- **Diagnostic Categorization**: Moved technical/signal sensors to the `DIAGNOSTIC` entity category.

### Fixed

- **Domain Cleanup**: Standardized unloading logic to ensure the `DOMAIN` key is scrubbed from memory when no entries remain.
- **Firmware Update Handling**: Added background logic to detect firmware version changes and update stored metadata.
- **Data Tracking**: Corrected "Monthly Data Remaining" logic.
- **Wi-Fi Control**: Fixed functional regressions in Wi-Fi toggles.
- **Race Conditions**: Implemented `asyncio.Lock` in API initialization.
- **Task Leaks**: Added proper cleanup for debounced tasks in `number.py`.

---

### Format

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
