# Retrieving 5G NR Metrics from TP-Link Routers (NX510v)

This guide outlines the technical discovery and implementation details for retrieving detailed 5G NR (New Radio) metrics from TP-Link 5G routers, such as the NX510v and Aginet series.

## The Challenge

Standard API calls used for LTE routers (like `get_lte_status` in the `tplinkrouterc6u` library) often return `0` or `null` for RSRP, RSRQ, and SNR when the router is operating in 5G mode. This is because many TP-Link 5G routers store 5G-specific metrics in separate data blocks or list-based structures that are not captured by standard 4G/LTE queries.

## The Discovery

During the development of this integration, it was discovered that detailed metrics for both the 4G LTE Anchor and the 5G NR cell are available via the **`DEV2_LTE_SERVING_CELL_INFO`** OID.

### Key Technical Details

- **OID**: `DEV2_LTE_SERVING_CELL_INFO`
- **Operation**: Get List (`GL`)
- **Structure**: Returns a list of cell objects. Usually:
  - Index 1: LTE Anchor Cell
  - Index 2: 5G NR Cell (if connected)

## Available 5G Metrics

When querying this OID using the `GL` operation, the following fields become available for the 5G NR cell (`networkType: 8`):

| Metric | Field Name | Description |
| :-- | :-- | :-- |
| **SS-RSRP** | `SSRSRP` | Synchronization Signal Reference Signal Received Power |
| **SS-RSRQ** | `SSRSRQ` | Synchronization Signal Reference Signal Received Quality |
| **SS-SINR** | `SSSINR` | Synchronization Signal Signal-to-Interference-plus-Noise Ratio |
| **Band** | `band` | The 5G frequency band (e.g., `28` for N28) |
| **DL Modulation** | `downlinkModType` | e.g., QPSK, 16QAM, 64QAM, 256QAM |
| **UL Modulation** | `uplinkModType` | e.g., QPSK, 16QAM, 64QAM, 256QAM |
| **PCI** | `PCI` | Physical Cell ID |

## Implementation Logic

To extract this data using the `tplinkrouterc6u` library, you must use the underlying `req_act` method found in the `TPLinkEXClient` or `TPLinkMRClient` classes.

### Python Example

```python
from tplinkrouterc6u import TplinkRouterProvider

# ... setup client ...

def get_5g_data(client):
    ActItem = client.ActItem
    # Create an action to Get List (GL) of serving cells
    act = ActItem(ActItem.GL, 'DEV2_LTE_SERVING_CELL_INFO', '0,0,0,0,0,0', attrs=[])

    # Execute the request
    _, values = client.req_act([act])

    cells = values[0]
    for cell in cells:
        if cell.get('networkType') == '8' and cell.get('cellConnectionStatus') == '1':
            print(f"5G Band: N{cell.get('band')}")
            print(f"5G RSRP: {cell.get('SSRSRP')} dBm")
            print(f"5G RSRQ: {cell.get('SSRSRQ')} dB")
```

## Retrieving WAN Uptime (MBB)

Standard device uptime (`DEV2_SYS_STATUS`) often resets independently of the actual internet connection. For accurate monitoring, the **`DEV2_ADT_WAN`** OID provides the uptime specifically for the WAN interface.

### Key Technical Details

- **OID**: `DEV2_ADT_WAN`
- **Operation**: Get List (`GL`)
- **Key Attribute**: `X_TP_Uptime` (Uptime in seconds)
- **Filtering**: Search for the entry where `name == "MBB"` (Mobile Broadband).

### Implementation

To ensure the Home Assistant UI remains stable, this uptime should be converted into a `TIMESTAMP` sensor representing the moment the connection was established.

```python
# Logic to calculate a stable timestamp (rounded to the minute)
uptime_seconds = int(wan.get("X_TP_Uptime"))
uptime_delta = timedelta(seconds=uptime_seconds)
connected_at = dt_util.now() - uptime_delta
# Rounding to the minute prevents the sensor state from "bouncing" on every poll
stable_timestamp = connected_at.replace(second=0, microsecond=0)
```

## Why Bridge Mode Matters

If your router is in **Bridge Mode**, some standard status OIDs (like `DEV2_LTE_NET_STATUS`) may stop updating or report zeros. The list-based serving cell info OID remains active and accurate even in Bridge Mode, making it the most reliable source for signal monitoring.
