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
- **Deep 5G Metrics**: Discovered and implemented OID `DEV2_LTE_SERVING_CELL_INFO` via Get List (`GL`) operation to provide:
  - 5G NR: SS-RSRP, SS-RSRQ, SS-SINR, Band (Nxx), DL/UL Modulation, Bandwidth (MHz).
  - 5G Tower: PCI, TAC, Cell ID, ARFCN.
  - 5G Capability: Binary sensor for ENDC (Dual Connectivity) support.
- **LTE Anchor Metrics**: Separate tracking for the 4G anchor cell including RSRP, RSSI, Band, and Bandwidth.
- **Enhanced Data Tracking**: Added sensors for Daily Data Usage, configured Data Limit, and Data Reset Day.
- **Wi-Fi Control**: 9 specialized switches providing independent control over 2.4G, 5G, and 6G bands for Main, Guest, and IoT networks.
- **SMS Infrastructure**: 
  - Reliable Unread SMS counter.
  - `tplink_router_5g.send_sms` service for outgoing messages.
  - Diagnostic sensors for Last Send Result and Network Cause codes.
- **Extended Diagnostics**: 
  - Network: WAN Gateway, Primary/Secondary DNS servers, WAN Uptime.
  - System: CPU and Memory usage percentages.
  - Connectivity: Binary sensor for Roaming status.
- **Decoded Sensors**: Human-readable strings for Connection Status (Connected/Disconnected), Network Type (5G NR/4G LTE), and detailed SIM Status.
- **Localization**: Full translation support via `strings.json` and `en.json`.

### Changed
- **Performance Engine**: Migrated to `DataUpdateCoordinator` pattern to centralize polling and ensure only one session is active per cycle.
- **Async Implementation**: All library calls are now offloaded to worker threads via `asyncio.to_thread` to protect the Home Assistant event loop.
- **Device Identification**: Switched to using the LAN MAC address as the primary identifier for more stable device entries.
- **Device Info Up-front**: Setup logic now fetches hardware and firmware versions immediately, ensuring the device card is fully populated upon first visibility.
- **UI Formatting**: Standardized sub-device display names (e.g., "SMS" and "Wi-Fi") and manufacturer branding ("TP-Link").

### Fixed
- **Blocking Call Bug**: Resolved "detected blocking call" errors by removing library constructor logic from the main event loop.
- **Service Registration**: Added missing `services.yaml` to resolve startup errors.
- **Speed Statistics**: Corrected download/upload speed entities to use `device_class: data_rate` for proper Home Assistant long-term statistics.

### Technical Notes
- **Discovery**: Extensive probing documented in `docs/GETTING_5G_INFO.md` and `docs/SMS_OPTIONS_CHECKED.md`.
- **Bridge Mode Optimization**: Specifically tuned to maintain accurate signal metrics even when the router is in Bridge Mode.
