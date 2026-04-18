# Changelog: TP-Link Router 5G Monitor

All notable changes to this project will be documented in this file.

## [1.0.1] - Unreleased

### Added

- **Custom User Naming**: Users can now define a custom prefix (e.g., "MyRouter") for all devices and entities during initial setup or via the Options flow.
- **Tiered Sub-Device Architecture**: Entities are now logically partitioned into five distinct sub-devices: `System`, `Signal`, `Home Network`, `Data`, and `SMS`.
- **Improved Registry Hierarchy**: All sub-devices now explicitly use `via_device` linking to the `System` root device, ensuring a clean and structured representation in the Home Assistant device registry.
- **Expanded Data Validation**: Guard bands now protect all numeric sensors, including Data Usage (Daily/Monthly/Remaining), ensuring long-term statistics remain clean from negative values or corruption spikes.
- **Realistic Resource Caps**: Added safety limits for data throughput (10Gbps) and client counts (max 512) to improve dashboard stability.
- **Physical Range Enforcement**: Technical identifiers (PCI, ARFCN) are now validated against industry-standard ranges to filter out invalid OID data.
- **Expanded Guard Band Logic**: Implemented `min_limit` and `max_limit` across all remaining numeric sensors (Data Usage, Rates, Clients, and IDs).
- **Data Integrity Protection**: Specifically hardened the Data Usage platform to ignore negative values or 100TB+ spikes, protecting Home Assistant's internal database from corrupted OID data.
- **ID Validation**: Applied physical limits to PCI (0-1007) and ARFCN (up to 3.3M) to filter hardware-specific reporting gaps.

### Changed

- **Standardized Naming**: Entity and Device names now consistently follow the `[Custom Name] [Group]` pattern for improved readability and organization.
- **Refactored Entity Grouping**: Migrated Wi-Fi controls to the `Home Network` group and polling controls to the `System` group to better align with hardware functions.

### Fixed

- **Code Integrity**: Resolved a startup SyntaxError and cleaned up duplicate entity definitions in the sensor platform.
- **Sensor Cleanup**: Resolved a SyntaxError caused by a trailing brace and eliminated duplicate entity registrations in the technical metrics platform.

## [1.0.0] - 2026-04-08

Initial GitHub release for this Home Assistant custom component specifically designed for the **TP-Link NX510v 5G Router**, focused on providing as much 5G/LTE signal data as possible, along with the standard router features.

### Added

- **Signal Guard Bands**: Implemented automatic validation for 50+ sensors. Impossible signal spikes or zero-values for specific metrics are now correctly filtered, keeping your dashboard clean and reliable.
- **Potential-Based "Best Connection"**: The `Best Connection` binary sensor now uses a hybrid algorithm. It correctly reflects your network's potential even when the router is idle, by balancing signal power and quality.
- **Sub-Device Architecture**: Entities are now logically grouped into linked devices (Main Router, Data Usage, SMS, Wi-Fi, and Clients) for a cleaner interface.
- **Deep 5G & LTE Metrics**: Comprehensive support for advanced signal diagnostics, including 5G (NR) and LTE Anchor cell frequencies, modulation (256QAM), MCS, and technical RF diagnostics.
- **Persistent Metadata**: Hardware model, MAC address, and firmware versions are now stored within Home Assistant, ensuring device information remains stable even if the router is offline.
- **WAN Uptime Sensor**: A stable WAN Uptime sensor provides a reliable timestamp of when your internet connection was established.
- **Guard Bands**: Implemented a declarative guard band system for 50+ sensors. Impossible values (e.g., 200dBm signal) or raw data spikes are automatically marked as `Unavailable` to protect UI data integrity.
- **Improved 5G Accuracy**: Applied `min_limit: 1` to 5G Cell ID, 5G TAC, and 5G Uplink Frequency to handle hardware-specific "stuck at zero" reporting.
- **Potential-Based "Best Connection"**: Refactored the `Best Connection` binary sensor using a hybrid algorithm (Option D) that accounts for both Signal Power (RSRP) and Signal Quality (SNR). This ensures the sensor reflects "potential" performance even during idle periods.
- **Persistent Metadata**: The integration fetches and stores the hardware model, MAC address, and firmware versions in the `ConfigEntry` during setup.
- **WAN Uptime Sensor**: Restored the WAN Uptime sensor using the `MBB` interface uptime, converted to a stable Home Assistant timestamp (rounded to the minute).
- **Sub-Device Architecture**: Entities are logically grouped into linked devices (Main, Data, SMS, Wi-Fi, Clients).
- **Deep 5G & LTE Metrics**: Exhaustive mapping for NR (5G) and LTE Anchor cells.
- **Comprehensive Test Suite**: 50+ Pytest unit tests.
- **Robust Session Management**: Atomic `login`/`logout` handling within administrative commands.

### Changed

- **Diagnostic Categorization**: Static (or rarely changing) sensors are now categorized as "Diagnostic" entities to keep the main UI decluttered.
- **Instant Startup**: Home Assistant now starts instantly without waiting for the router to respond; initial data is fetched quietly in the background.
- **System Requirements**: This integration now requires **Home Assistant 2025.1.0** or newer.
- **MCS Retransmission Support**: Increased maximum MCS limits from 28 to 31 to accommodate HARQ retransmission states reported by the router.
- **Modern Background Tasks**: Migrated the non-blocking startup sequence to the modern `entry.async_create_background_task` API.
- **Non-Blocking Startup**: Removed the initial blocking data fetch during integration setup.
- **HA Requirement**: Increased minimum Home Assistant version to **2025.1.0**.
- **Standardized Polling**: Set the default polling interval to **120 seconds**.
- **Diagnostic Categorization**: Moved technical/signal sensors to the `DIAGNOSTIC` entity category.

### Fixed

- **Corrected Power and SNR**: Applied correct scaling (deivide by 10) 5G Transmit Power, 5G SNR, and LTE Anchor SNR values.
- **MCS Data Handling**: Improved support for advanced MCS states, preventing sensors from showing as "Unknown" during high-performance data transfers.
- **Data Tracking**: Corrected "Monthly Data Remaining" logic based on monthly limits.
- **Wi-Fi Control**: Fixed issues where specific Wi-Fi band toggles would occasionally fail.
- **Auto-Updating Identity**: The integration now automatically detects router firmware updates and refreshes device information.
- **Connection Resilience**: Improved handling of intermittent network drops to prevent entity flickering.
- **Signal Scaling (0.1x)**: Applied correct 0.1 scaling and 1-decimal precision to 5G Transmit Power, 5G SNR, and LTE Anchor SNR to reflect real-world values.
- **Domain Cleanup**: Standardized unloading logic to ensure the `DOMAIN` key is scrubbed from memory when no entries remain.
- **Firmware Update Handling**: Added background logic to detect firmware version changes and update stored metadata.
- **Data Tracking**: Corrected "Monthly Data Remaining" logic.
- **Wi-Fi Control**: Fixed functional regressions in Wi-Fi toggles.
- **Race Conditions**: Implemented `asyncio.Lock` in API initialization.
- **Task Leaks**: Added proper cleanup for debounced tasks in `number.py`.

---

### Format

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
