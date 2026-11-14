#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py

Rules (from the README):
- Every attempt for a payment shares a txn_id; only the latest attempt counts.
- A payment is collected only if its latest attempt is "success".
- Skip lines that can't be parsed and events without a txn_id.
"""
import json
from datetime import datetime


def parse_amount(value):
    """Amounts arrive as numbers or as strings with thousands separators ("55,707.77")."""
    if isinstance(value, str):
        value = value.replace(",", "").strip()
    return float(value)


def parse_ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


latest = {}  # txn_id -> (timestamp, line number, event)
skipped = 0

with open("payments.jsonl", encoding="utf-8") as f:
    for line_no, line in enumerate(f):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1  # truncated or corrupt line
            continue
        txn_id = event.get("txn_id") if isinstance(event, dict) else None
        if not txn_id:
            skipped += 1
            continue
        key = (parse_ts(event["ts"]), line_no)  # later line wins if timestamps tie
        if txn_id not in latest or key > latest[txn_id][:2]:
            latest[txn_id] = (*key, event)

total = 0.0
count = 0
for _, _, event in latest.values():
    if event["status"] == "success":
        total += parse_amount(event["amount"])
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
