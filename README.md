# Payment reconciliation

Works out how much money was actually collected from a raw export of payment events, and checks the result against the finance team's hand count.

Forked from [quadri40/koya-payment-reconciliation](https://github.com/quadri40/koya-payment-reconciliation), where the original script did not produce the right figures. The fix is in `reconcile.py`.

## How the data works

- `payments.jsonl` holds one event per line: `txn_id`, `status` (`success`, `failed` or `pending`), `amount` in naira, `currency`, and `ts` (when it happened, UTC).
- A payment can be attempted more than once. Every attempt has the same `txn_id`, and only the latest attempt counts.
- A payment counts as collected only if its latest attempt is `success`.
- The export comes from a production system and isn't perfectly clean. Lines that can't be read, and events without a `txn_id`, are ignored.
- `expected.txt` holds the number of successful payments counted by hand. The script checks itself against it.

## What was fixed

1. **Retries.** About 7,800 of the 30,000 payments had more than one attempt. The original counted every successful attempt; the fix keeps only the latest attempt per `txn_id` (by timestamp) and counts it only if it succeeded.
2. **Corrupt rows.** 25 truncated lines and 15 events with no `txn_id` crashed the original. They are now skipped.
3. **Amounts stored as text.** About 2,300 amounts arrived as strings with thousands separators, such as `"55,707.77"`. They are now parsed correctly.

## Run it

```bash
python reconcile.py
```

```
Check passed: 22733 successful payments.
```

The count matches the finance team's figure in `expected.txt`.
