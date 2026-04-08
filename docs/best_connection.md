# Best Connection Strategy

The "Best Connection" binary sensor in this integration is designed to reflect the **Potential Performance** of the router, even when it is idle.

## The Problem

Many 5G routers (including the Aginet NX510v) aggressively put secondary carriers (Carrier Aggregation) and 5G legs into low-power "sleep" modes when no data is being transferred. If we only checked for "Active CA," the sensor would constantly flicker between On and Off, which is unhelpful for monitoring overall network health.

## The Solution: Option D (Hybrid Potential)

We use a hybrid algorithm that balances **Raw Power** (RSRP) against **Signal Purity** (SNR). This ensures that if the signal is strong (near a tower) OR exceptionally clean (far from a tower but no interference), the connection is considered "Best."

### The Algorithm

The sensor turns **ON** only if all three of the following stages are met:

1. **Network Support**:
   - `5G ENDC Support` must be **ON**.

2. **LTE Anchor Health**:
   - `LTE RSRP > -100 dBm` (Strong Signal)
   - **OR**
   - `LTE SNR > 15 dB` (Excellent Quality)

3. **5G Leg Health**:
   - `5G RSRP > -105 dBm` (Strong Signal)
   - **OR**
   - `5G SNR > 10 dB` (Excellent Quality)

## Benefits

- **Stability**: RSRP and SNR are measurable even when the modem is idle, preventing the sensor from "sleeping."
- **Accuracy**: By requiring both the LTE and 5G legs to be "Healthy," we ensure the hardware is actually ready for multi-homed (ENDC) performance.
- **Fair to Distance**: Users further from a tower can still achieve a "Best Connection" state if their SNR (quality) is high enough to support advanced modulation.
