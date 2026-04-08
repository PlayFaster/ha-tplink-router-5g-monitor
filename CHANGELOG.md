# Changelog: TP-Link Router 5G Monitor

All notable changes to this project will be documented in this file.

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

- **Improved Signal Accuracy**: Applied precision scaling to signal metrics (Transmit Power, SNR) to reflect accurate real-world values.
- **Diagnostic Categorization**: Technical and signal-specific sensors are now categorized as "Diagnostic" entities to keep the main UI decluttered.
- **Instant Startup**: Home Assistant now starts instantly without waiting for the router to respond; initial data is fetched quietly in the background.
- **System Requirements**: This integration now requires **Home Assistant 2025.1.0** or newer.

### Fixed

- **MCS Data Handling**: Improved support for advanced MCS states, preventing sensors from showing as "Unknown" during high-performance data transfers.
- **Data Tracking**: Corrected "Monthly Data Remaining" logic based on monthly limits.
- **Wi-Fi Control**: Fixed issues where specific Wi-Fi band toggles would occasionally fail.
- **Auto-Updating Identity**: The integration now automatically detects router firmware updates and refreshes device information.
- **Connection Resilience**: Improved handling of intermittent network drops to prevent entity flickering.

---

### Format

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
