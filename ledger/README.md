# Receipt ledger

**Append-only machine receipts.** Stub. The file is empty until a real event.

- Shape: [SCHEMA.md](SCHEMA.md)
- Lines: [receipts.jsonl](receipts.jsonl) — empty on purpose. No genesis line.
- Writer: [scripts/append-receipt.py](../scripts/append-receipt.py) — prints one line; does not write this file

First real row only. An empty file means the next `prev_hash` is the sentinel `genesis`. That note lives here, not as a fake line in `receipts.jsonl`.

Human promise → build → proof stays in [RECEIPTS-TEMPLATE.md](../RECEIPTS-TEMPLATE.md). Run Clarity A→F in [CLARITY-ENGINE-NOTES.md](../CLARITY-ENGINE-NOTES.md) before you stamp a verdict. The remix table people read is still [INVITE-FORKS.md](../INVITE-FORKS.md). This directory is the machine twin of those events.

---

## How to append

1. Fill the [receipts template](../RECEIPTS-TEMPLATE.md) and/or run Clarity A→F. Write the promise before the build when a promise applies.
2. Run the script with the fields (flags, stdin JSON, or both). It checks the schema, sets `prev_hash` from the last line (or `genesis` when the file is empty), and prints one JSON line.

```bash
python3 scripts/append-receipt.py --help

python3 scripts/append-receipt.py \
  --id rcpt_<ulid-or-uuid> \
  --type clarity_stamp \
  --ts 2026-10-29T18:00:00Z \
  --actor github:<handle> \
  --subject path-or-url \
  --promise "one sentence" \
  --build path-or-url \
  --proof "one concrete verify step" \
  --verdict match \
  --ref path-or-url
```

3. Open a PR that appends exactly that line to `ledger/receipts.jsonl`. For `remix`, also add the matching row in [INVITE-FORKS.md](../INVITE-FORKS.md). Do not invent a row to make the table look lived-in.
4. Merge is the public write. Git history is the audit trail.

The script does not commit, push, or edit the ledger. No silent rows.

Stdin JSON uses the same field names. Flags override stdin keys when you pass both. Any `--ref` replaces stdin `refs`. `content_hash` and `prev_hash` in the input are ignored; the script computes them.

`--ledger` points at the file to read for `prev_hash`. Default is `ledger/receipts.jsonl`. The flag does not create or change that file.

---

## How to verify

On a non-empty file, check each line against [SCHEMA.md](SCHEMA.md):

1. It parses as one JSON object. `v` is `0`. `type` and `verdict` are in the allowed sets. `id` is `rcpt_` plus a UUID or ULID.
2. Recompute `content_hash`: canonical JSON of every field except `content_hash` and `prev_hash` (sorted keys, no spaces, UTF-8), then SHA-256, lowercase hex.
3. First line: `prev_hash` is `genesis`. Each later line: `prev_hash` is SHA-256 of the previous line's exact UTF-8 text, line terminator excluded.
4. A `correction` line sets `corrects` to an earlier `id`. Other types have `corrects` null.
5. `git log -p -- ledger/receipts.jsonl` shows appends. Old lines stay put.

Empty file: nothing to verify. That is the current state. Do not add a line to make the check look busy.

---

## What's unfinished (labeled)

- No CI rejection of a bad line yet.
- No automated fork discovery. Remix rows stay manual.
- `receipts.jsonl` has no live rows. The first line waits for a real event.

---

## Rules

1. Receipts over slogans.
2. Incomplete beats cosplay.
3. A person appends the line in a PR. The script only prints it.
4. This ledger records events. It does not mint or spend.

*Out of many, one. For real this time.*
