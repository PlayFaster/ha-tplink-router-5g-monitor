# Uptime Retrieval: Options Checked (NX510v)

This document records the technical attempts and research performed to find valid uptime metrics (System Uptime or WAN Connection Uptime) for the TP-Link NX510v (Aginet series) 5G router.

## Overview
The goal was to find a numeric value (seconds) or a timestamp representing how long the device or the internet connection has been active. Despite exhaustive probing of common TP-Link OIDs and CGIs, these values remain unidentified for this specific hardware/firmware combination.

## 1. OID Probing (GET/GL Operations)
We used manual `req_act` calls to probe various Object Identifiers (OIDs) across multiple "stacks".

### OIDs Targeted:
*   **`DEV2_DEV_INFO`**: Usually the primary source for system metadata. We probed for `upTime`, `uptime`, `X_TP_UpTime`, `X_TP_Uptime`, and `UpTime`.
    *   *Result*: Successfully returns model and firmware versions, but all uptime attribute variations returned `null` or were ignored by the router.
*   **`DEV2_ADT_WAN`**: Probed for connection-specific timing.
    *   *Result*: Correctily returns IPv4 Address and Gateway, but does not contain an uptime attribute in its list.
*   **`DEV2_LTE_NET_STATUS`**: Probed for LTE/5G session duration.
    *   *Result*: Provides comprehensive signal metrics and SMS counts, but no timing information.
*   **`DEV2_SYS_STATUS` & `DEV2_XTP_SYS_STATUS`**:
    *   *Result*: These OIDs appear to be unsupported or require a different access level/stack on the NX510v.

## 2. CGI Probing
We attempted to bypass the OID system by calling internal Common Gateway Interface (CGI) scripts used by the web interface.

### Paths Tested:
*   `/cgi/getStatus`
*   `/cgi/getSysStatus`
*   `/cgi/getDevInfo`
*   `/cgi/getSystemInfo`

*   *Result*: These calls frequently resulted in `RemoteDisconnected` errors or empty responses, suggesting the NX510v Aginet firmware uses a more restricted or differently named CGI structure than the standard Archer/MR series.

## 3. Attribute Guessing
We performed "Get List" (GL) operations with empty attribute arrays to see if the router would reveal its internal keys.
*   While this worked for `DEV2_LTE_NET_STATUS` (revealing keys like `connStat` and `smsUnreadCount`), it did not reveal any keys related to time, duration, or timestamps.

## 4. Considerations for Bridge Mode
The router is currently operating in **Bridge Mode**. 
*   In many TP-Link firmwares, Bridge Mode disables the standard WAN management engine, which can cause WAN-specific uptime OIDs to report as `0` or become entirely inaccessible.
*   However, **Device Uptime** (System Boot Time) is typically an OS-level metric that should remain available. Its absence suggests a non-standard OID name unique to the Aginet/AX series.

## 5. Current Status: Disabled
To maintain a clean and accurate user interface, the following sensors have been removed from the component until a valid data source is found:
*   `sensor.wan_uptime`
*   `sensor.device_uptime`

## Future Directions for Research
1.  **Web UI Sniffing**: If a user can access the router's web interface and use Browser DevTools (Network tab), they can look for the JSON response that populates the "Status" or "Advanced" pages to see exactly which OID/Attribute is providing the uptime.
2.  **Aginet Specifics**: Research into the specific Aginet management protocol (often used by ISPs) may reveal a different set of `X_TP_` prefixed OIDs specifically for maintenance and monitoring.
