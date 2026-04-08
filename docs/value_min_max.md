# Signal Metric Guard Bands

To ensure the Home Assistant UI remains clean and professional, we apply "Guard Bands" to incoming router data. If a value falls outside these realistic physical limits, the sensor is marked as `Unavailable` to prevent misleading spikes or "ghost" zeros.

## Guard Band Strategy (Option C)

We use a **Declarative Validation** approach. Limits are defined directly within the `EntityDescription` for each sensor. The base sensor class automatically enforces these bounds before passing the value to Home Assistant.

### Why this approach?

- **Readability**: Limits are visible next to the sensor definition.
- **Maintainability**: Changing a limit requires updating only one number, not complex logic.
- **Stability**: Prevents impossible values (e.g., 200dBm signal) from polluting long-term statistics and database storage.

---

## Validated Signal Limits

| Metric Category    | Metric Name         | Min  | Max    | Action if Out of Bounds   |
| :----------------- | :------------------ | :--- | :----- | :------------------------ |
| **Signal Power**   | RSRP (5G/LTE)       | -140 | -40    | Set to `Unavailable`      |
|                    | RSRQ (5G/LTE)       | -25  | 0      | Set to `Unavailable`      |
|                    | RSSI (5G)           | -125 | -20    | Set to `Unavailable`      |
|                    | RSSI (LTE)          | -120 | -20    | Set to `Unavailable`      |
| **Signal Quality** | SNR / SINR          | -10  | 45     | Set to `Unavailable`      |
|                    | CQI                 | 1    | 15     | Set to `Unknown`          |
| **Efficiency**     | MCS (DL/UL)         | 0    | 31     | Set to `Idle` / `Unknown` |
|                    | RI (Rank)           | 1    | 4      | Set to `Unknown`          |
| **Performance**    | Resource Blocks     | 0    | 273    | Set to `Unavailable`      |
|                    | Transmit Power      | -40  | 25     | Set to `Unavailable`      |
| **Diagnostics**    | Cell ID / TAC       | 1    | -      | Set to `Unavailable` if 0 |
|                    | Uplink Frequency    | 100  | -      | Set to `Unavailable` if 0 |
|                    | PCI (LTE & 5G)      | 0    | 1007   | Set to `Unavailable`      |
|                    | ARFCN (LTE & 5G)    | 1    | 3.3M   | Set to `Unavailable`      |
| **Data Usage**     | Daily/Monthly Usage | 0    | 100TB  | Set to `Unavailable`      |
|                    | Data Remaining      | 0    | 100TB  | Set to `Unavailable`      |
|                    | Reset Day           | 1    | 31     | Set to `Unavailable`      |
| **Data Rates**     | Download/Upload     | 0    | 10Gbps | Set to `Unavailable`      |
| **Clients**        | Total/Wired/WiFi    | 0    | 512    | Set to `Unavailable`      |
| **SMS**            | Unread Count        | 0    | 1000   | Set to `Unavailable`      |
| **Environment**    | CPU / Memory        | 0    | 100    | Set to `Unavailable`      |

---

## Implementation Details

The `TPLinkSensorEntityDescription` dataclass includes:

- `min_limit`: The lowest physically possible value.
- `max_limit`: The highest physically possible value.

The `native_value` property in the sensor class performs the following check:

```python
if min_limit is not None and value < min_limit:
    return None
if max_limit is not None and value > max_limit:
    return None
```
