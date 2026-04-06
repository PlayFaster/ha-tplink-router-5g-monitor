# Changelog: TP-Link Router 5G Monitor

All notable changes to the `tplink_router_5g` custom component will be documented in this file.

## [1.0.0] - 2026-04-06

### Added

- **Sub-Device Architecture**: Entities are now logically grouped into linked devices:
  - **Main**: Diagnostic and signal health.
  - **Data**: Usage statistics and speed metrics.
  - **SMS**: Messaging controls and counters.
  - **Wi-Fi**: Comprehensive network toggles.
  - **Clients**: Connected device counts.
- **Deep 5G & LTE Metrics**: Discovered and implemented exhaustive technical mapping for both NR (5G) and LTE Anchor cells:
  - **Frequencies**: Added Downlink/Uplink frequency sensors for both cells.
  - **Modulation & Coding**: Added DL/UL Modulation (e.g., 256QAM) and MCS (Modulation and Coding Scheme) sensors.
  - **Advanced RF**: Added CQI, PMI, RI, TBS, and RBS diagnostics for precise link quality monitoring.
  - **Signal Fidelity**: Added dedicated "Signal Strength %" sensors matching the router's GUI bars.
- **Enhanced Uptime Tracking**:
  - Restored **Device Uptime** and **WAN Uptime** as high-fidelity `TIMESTAMP` sensors.
  - Implemented string-to-seconds parsing to handle the router's formatted uptime display ("X days HH:MM:SS").
- **Best Connection Sensor**: New binary sensor that indicates an optimal connection when 5G ENDC is active and 256QAM modulation is achieved.
- **Data Remaining Sensor**: Added a real-time calculation of remaining data allowance based on limit and usage.
- **Registration & Service Status**: Decoded sensors for human-readable network states (e.g., "Full Service", "Registered", "Roaming").
- **LTE Anchor Detail**: Added dedicated TAC and Cell ID sensors for the 4G anchor tower.
- **Additional Client Tracking**: Added specialized counters for "Total Guest" and "Total IoT" clients.

### Changed

- **Traffic Consolidation**: Merged multiple OID requests into a single efficient `req_act` call to reduce session overhead and prevent router timeouts.
- **Performance Engine**: Migrated to `DataUpdateCoordinator` pattern with 0.5s "breathing" delays between independent library calls for increased stability.
- **Device Identification**: Switched to using the LAN MAC address as the primary identifier and included it in the `connections` attribute for full Home Assistant UI support.
- **UI Formatting**: Unified icons across bands (`mdi:radio-tower`) and standardized manufacturer branding as "TP-Link".
- **Future-Proofing**: Updated `via_device` references to ensure compatibility with Home Assistant 2025.12+ architecture.

### Fixed

- **Numeric Measurement Errors**: Resolved `ValueError` crashes by ensuring all technical metrics return raw numbers instead of formatted strings.
- **Object Attribute Errors**: Fixed `AttributeError` by isolating custom-probed data into the `extra_lte_status` dictionary.
- **Unique ID Conflicts**: Eliminated duplicate SIM Status sensors causing registry errors.
- **Service Registration**: Fully implemented `services.yaml` for the `send_sms` service.

### Technical Documentation

- **Discovery Logs**: Detailed research documented in:
  - `docs/GETTING_5G_INFO.md` (5G NR technicals)
  - `docs/SMS_OPTIONS_CHECKED.md` (Inbox probing attempts)
  - `docs/Uptime_Checks.md` (Uptime OID discovery)
