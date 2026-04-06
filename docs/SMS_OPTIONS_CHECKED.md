# SMS Message Retrieval: Options Checked (NX510v)

This document records the technical attempts and research performed to retrieve actual SMS message content (text, sender, timestamp) from the TP-Link NX510v (Aginet series) 5G router.

## Overview

While the router correctly reports the **Unread SMS Count** via the standard `DEV2_LTE_NET_STATUS` OID, the actual message list and content proved difficult to retrieve using standard library methods or common TP-Link OIDs.

## 1. Library Limitations

The `tplinkrouterc6u` library identifies the NX510v as a `TPLinkEXClient`. Unlike the `TPLinkMRClient` (used for older 4G models), the `EX` client does **not** have a native `get_sms` implementation. It only extracts the unread count from the main status block.

## 2. OIDs Probed

We used manual `req_act` calls to probe various OIDs known to handle SMS in other TP-Link hardware.

### OIDs Targeted

- `DEV2_SMS_RECVMSGENTRY`
- `DEV2_SMS_DATA_ENTRY`
- `DEV2_SMS_INBOX_ENTRY`
- `X_TP_SMS_RECVMSGENTRY`
- `LTE_SMS_RECVMSGENTRY`

### Operations Tested

- **Get List (GL)**: Most common for message lists. Returned empty lists `[]`.
- **Get Object (GO)**: Returned empty or errors.
- **Get (GET)**: Explicitly requested specific indices (e.g., `1,0,0,0,0,0`). Returned empty.

## 3. Sequence logic

Based on `mr.py` source code, we attempted to "trigger" the mailbox population before querying:

1. **Action**: `SET` on `DEV2_SMS_RECVMSGBOX` with `attrs=['PageNumber=1']`. (This operation was successful/accepted by the router).
2. **Action**: `GL` or `GET` on `DEV2_SMS_RECVMSGENTRY`. (Returned no data).

## 4. Attribute Name Variations

Since the "Get List" operation requires attribute names, we probed the following variations:

- **Content**: `content`, `textContent`, `X_TP_Content`, `text`.
- **Sender**: `from`, `phoneNumber`, `X_TP_From`, `sender`.
- **Time**: `receivedTime`, `timeStamp`, `X_TP_ReceivedTime`, `time`.
- **Status**: `unread`, `readStatus`, `X_TP_Unread`.

None of these returned non-zero/non-empty data during discovery.

## 5. Raw Response Sniffing

We implemented a wrapper to sniff every `req_act` response during a standard update cycle. We confirmed that the router **does not** include SMS content in its standard status packets; it only includes the `smsUnreadCount` integer.

## 6. Current Status: Parked

The feature is currently "parked." The integration includes the following SMS infrastructure which is verified working:

- **Unread SMS Count**: Working (mapped to `DEV2_LTE_NET_STATUS`).
- **SMS Sub-device**: Created and linked to the main router.
- **Send SMS Service**: Working (`tplink_router_5g.send_sms` service).
- **SMS Diagnostics**: Sensors for **Last Send Result** and **Cause** are active.

## Future Directions

If a future firmware update or further reverse engineering reveals the correct OID or CGI path for the inbox (possibly a `DEV2_` variant of the `sms_data_total` command used by some models), the logic in `api.py` can be easily re-enabled.
