# Changelog: TP-Link Router 5G Monitor

All notable changes to this project will be documented in this file.

## [1.1.1] - Unreleased

### Changed

- **Library Update**: Verified with supporting TP-Link Router [library](https://github.com/AlexandrErohin/TP-Link-Archer-C6U) v5.18.1 (from v5.17.1).
- **Data Usage Naming**: Renamed "Daily Data Usage" to **"Monthly Download"** and "Total Data Statistics" to **"Monthly Usage"** to better reflect actual hardware reporting behavior and monthly reset cycles.

## [1.1.0] - 2026-04-08

### Added

- **Custom User Naming**: Users can now define a custom prefix (e.g., "MyRouter") for all devices and entities during initial setup or via the Options flow.
- **Tiered Sub-Devices**: Entities are now logically partitioned into five distinct sub-devices: `System`, `Signal`, `Home Network`, `Data`, and `SMS`.
- **Expanded Data Validation**: Added guard band limits to all remaining numeric sensors, including Data Usage and Client Counts, to ensure invalid hardware data is rejected.

### Changed

- **Standardized Naming**: Entity and Device names now consistently follow the `[Custom Name] [Group]` pattern for improved readability and organization.
- **Refactored Entity Grouping**: Migrated Wi-Fi controls to the `Home Network` group and polling controls to the `System` group to better align with hardware functions.

## [1.0.0] - 2026-04-08

Initial GitHub release for this Home Assistant custom component specifically designed for the **TP-Link NX510v 5G Router**, focused on providing as much 5G/LTE signal data as possible, along with the standard router features.

### Added

- **Signal Guard Bands**: Implemented automatic validation for 50+ sensors. Impossible signal spikes or zero-values for specific metrics are now correctly filtered, keeping your dashboard clean and reliable.
- **Potential-Based "Best Connection"**: The `Best Connection` binary sensor now uses a hybrid algorithm. It correctly reflects your network's potential even when the router is idle, by balancing signal power and quality.
- **Sub-Device Architecture**: Entities are now logically grouped into linked devices (Main Router, Data Usage, SMS, Wi-Fi, and Clients) for a cleaner interface.
- **Deep 5G & LTE Metrics**: Comprehensive support for advanced signal diagnostics, including 5G (NR) and LTE Anchor cell frequencies, modulation (256QAM), MCS, and technical RF diagnostics.
- **Persistent Metadata**: Hardware model, MAC address, and firmware versions are now stored within Home Assistant, ensuring device information remains stable even if the router is offline.
- **WAN Uptime Sensor**: A stable WAN Uptime sensor provides a reliable timestamp of when your internet connection was established.

### Changed

- **Diagnostic Categorization**: Static (or rarely changing) sensors are now categorized as "Diagnostic" entities to keep the main UI decluttered.
- **Instant Startup**: Home Assistant now starts instantly without waiting for the router to respond; initial data is fetched quietly in the background.
- **System Requirements**: This integration now requires **Home Assistant 2025.1.0** or newer.

### Fixed

- **Corrected Power and SNR**: Applied correct scaling (deivide by 10) 5G Transmit Power, 5G SNR, and LTE Anchor SNR values.
- **MCS Data Handling**: Improved support for advanced MCS states, preventing sensors from showing as "Unknown" during high-performance data transfers.
- **Data Tracking**: Corrected "Monthly Data Remaining" logic based on monthly limits.
- **Wi-Fi Control**: Fixed issues where specific Wi-Fi band toggles would occasionally fail.
- **Auto-Updating Identity**: The integration now automatically detects router firmware updates and refreshes device information.
- **Connection Resilience**: Improved handling of intermittent network drops to prevent entity flickering.

---

### Format

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
