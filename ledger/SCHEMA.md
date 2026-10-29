# Receipt ledger schema

**Machine receipts. Append-only. v0.** One JSON object per line in [receipts.jsonl](receipts.jsonl). Fork freely.

Human narrative still uses [RECEIPTS-TEMPLATE.md](../RECEIPTS-TEMPLATE.md) (promise → build → proof). The check sequence is still [CLARITY-ENGINE-NOTES.md](../CLARITY-ENGINE-NOTES.md) A→F. A ledger line is the machine receipt of that check or event — a boring twin, not a replacement manifesto.

The human remix table stays in [INVITE-FORKS.md](../INVITE-FORKS.md). This schema does not fill it.

No live rows ship with this file. The first line lands only when a real event happens.

---

## Event types

| type | meaning |
|------|---------|
| `clarity_stamp` | Verdict from the Clarity engine notes (match / partial / no_match) on a named piece |
| `fork` | Someone forked or copied a UniversalOS piece (link + what they took) |
| `remix` | A remix shipped. Also add a row to the human remix table when you append the line |
| `sanctuary_onboard` | Onboarding / sanctuary event (who, what door, date). No private detail beyond what they already published |
| `signal` | Who noticed a checkable thing, and where to look. A written credit. Nothing is minted |
| `correction` | Points at a prior receipt id and states what was wrong |

---

## Required fields

Every event. Closed set. No extra keys.

| field | rule |
|-------|------|
| `v` | Integer `0`. Schema version. |
| `id` | `rcpt_` plus a ULID or a UUID. Stable. Never reused. |
| `type` | One of the types above. |
| `ts` | ISO-8601, UTC, `Z` suffix. Example shape: `2026-10-29T18:00:00Z`. Fractional seconds allowed. |
| `actor` | Who is writing the receipt. Public handle, e.g. `github:<handle>`. |
| `subject` | What the event is about. Path or URL. |
| `promise` | One sentence, written before the build when a promise applies. |
| `build` | Path or URL of what exists. |
| `proof` | One concrete verify step. |
| `verdict` | `match`, `partial`, `no_match`, or `n/a`. |
| `refs` | Array of related URLs or paths (receipt markdown, PR, issue). Empty array if none. |
| `corrects` | `null`, or a prior receipt `id`. Non-null only when `type` is `correction`. |
| `content_hash` | Lowercase hex SHA-256 of the canonical payload. See below. |
| `prev_hash` | Lowercase hex SHA-256 of the previous line, or the sentinel `genesis` on the first line. |

Shape only — not a receipt. Do not append this:

```json
{
  "v": 0,
  "id": "rcpt_<ulid-or-uuid>",
  "type": "clarity_stamp",
  "ts": "2026-10-29T18:00:00Z",
  "actor": "github:<handle>",
  "subject": "path-or-url",
  "promise": "one sentence, written before build when applicable",
  "build": "path or URL of what exists",
  "proof": "one concrete verify step",
  "verdict": "match",
  "refs": [],
  "corrects": null,
  "content_hash": "<sha256 hex>",
  "prev_hash": "genesis"
}
```

Gaps stay labeled inside `promise`, `build`, and `proof`. An empty `promise` is allowed only when the event truly has no promise: then `verdict` is `n/a` and `proof` says why. `build` and `proof` stay non-empty.

`id` forms:

- `rcpt_` + UUID (`rcpt_01234567-89ab-cdef-0123-456789abcdef`)
- `rcpt_` + ULID, 26 Crockford characters (`rcpt_01ARZ3NDEKTSV4RRFFQ69G5FAV`)

Letters `I`, `L`, `O`, and `U` are not in a ULID. Case is kept as written. Do not reuse an id.

---

## Canonical payload and hashes

`content_hash` covers the event fields. `prev_hash` covers the previous stored line.

**content_hash**

1. Take every field except `content_hash` and `prev_hash`.
2. Serialize UTF-8 JSON with Python `json.dumps` rules as used in [scripts/append-receipt.py](../scripts/append-receipt.py): keys sorted by Unicode code point, separators `,` and `:` with no spaces, Unicode characters left as themselves (not `\u` escapes). Control characters are escaped. `refs` order is kept. `null` stays `null`. `v` is a number.
3. SHA-256 those bytes. Write lowercase hex into `content_hash`.

Sorted field names: `actor`, `build`, `corrects`, `id`, `promise`, `proof`, `refs`, `subject`, `ts`, `type`, `v`, `verdict`.

**prev_hash**

- Ledger missing, zero bytes, or only blank lines: `prev_hash` is the string `genesis`. That sentinel is not a hash. It means nothing is before this line.
- Otherwise: SHA-256 of the previous line's exact UTF-8 text. The line terminator (LF or CRLF) is not part of the input. Lowercase hex. Do not re-serialize the previous object before hashing.

Printed lines use this key order, compact, one object per line:

`v`, `id`, `type`, `ts`, `actor`, `subject`, `promise`, `build`, `proof`, `verdict`, `refs`, `corrects`, `content_hash`, `prev_hash`

Do not pretty-print. Do not rewrite a line after it is merged. A spacing change breaks the next `prev_hash`.

[scripts/append-receipt.py](../scripts/append-receipt.py) computes both hashes and prints the line. It does not write the file.

---

## Append-only rules

1. New events go at the end. One line. Nothing inserted in the middle.
2. Merged lines stay as merged. Git history is the audit trail.
3. A wrong line stays in place. Fix it with a new `correction` event.
4. No silent writes. A person opens a PR that appends the line. Merge is the public write.
5. Empty is honest. No placeholder event ships in `receipts.jsonl`.

---

## Correction events

`type` is `correction`. `corrects` is the prior receipt `id`. `promise`, `build`, and `proof` say what was wrong and what the record should say now. `verdict` is the verdict on that correction (`n/a` when the fix is clerical and has no match check).

The old line remains. Readers follow `corrects` to the later word.

The script checks that `corrects` looks like a receipt id and is not the new line's own id. It does not require that id to already sit in the file — the prior line might be landing in the same change. Before merge, a person still confirms the id exists on an earlier line when it should.

Other types keep `corrects` at `null`.

---

## Pairing

| Doc | Job |
|-----|-----|
| [RECEIPTS-TEMPLATE.md](../RECEIPTS-TEMPLATE.md) | Human page: promise, build, proof |
| [CLARITY-ENGINE-NOTES.md](../CLARITY-ENGINE-NOTES.md) | Checklist A→F and the verdict words |
| This schema | Machine line for that check or event |
| [INVITE-FORKS.md](../INVITE-FORKS.md) | Human remix rows. A `remix` event should match a row there |

Notes say Match / Partial / No match. The ledger stores `match`, `partial`, `no_match`. Use `n/a` when the event is not a match check.

---

## Rules

1. Receipts over slogans. Fields are concrete, or an empty promise is labeled with `n/a` and a proof that says why.
2. Incomplete beats cosplay. An empty ledger beats a fake first row.
3. Append-only. Corrections are new lines.
4. This ledger records events. It does not mint or spend.

*Out of many, one. For real this time.*
