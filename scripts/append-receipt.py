#!/usr/bin/env python3
"""Print one validated receipt JSON line. Does not write the ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

GENESIS = "genesis"
TYPES = (
    "clarity_stamp",
    "fork",
    "remix",
    "sanctuary_onboard",
    "signal",
    "correction",
)
VERDICTS = ("match", "partial", "no_match", "n/a")
OUTPUT_KEYS = (
    "v",
    "id",
    "type",
    "ts",
    "actor",
    "subject",
    "promise",
    "build",
    "proof",
    "verdict",
    "refs",
    "corrects",
    "content_hash",
    "prev_hash",
)
PAYLOAD_KEYS = OUTPUT_KEYS[:-2]

UUID_ID = re.compile(
    r"^rcpt_[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
# Crockford base32, either case. Excludes I, L, O, U.
ULID_ID = re.compile(r"^rcpt_[0-9A-HJKMNP-TV-Za-hjkmnp-tv-z]{26}$")
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LEDGER = ROOT / "ledger" / "receipts.jsonl"


def die(message: str) -> None:
    print(f"append-receipt.py: {message}", file=sys.stderr)
    raise SystemExit(1)


def valid_id(value: str) -> bool:
    return bool(UUID_ID.fullmatch(value) or ULID_ID.fullmatch(value))


def valid_ts(value: str) -> bool:
    if not TS_RE.fullmatch(value):
        return False
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return True


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_payload(fields: dict) -> str:
    payload = {key: fields[key] for key in PAYLOAD_KEYS}
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )


def load_ledger(path: Path) -> list[tuple[str, dict]]:
    if not path.exists():
        return []
    if path.is_dir():
        die(f"ledger path is a directory: {path}")
    raw = path.read_bytes()
    if raw == b"":
        return []
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        die(f"ledger is not UTF-8: {exc}")
    rows: list[tuple[str, dict]] = []
    for number, line in enumerate(text.splitlines(), 1):
        if line.strip() == "":
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            die(f"ledger line {number} is not JSON ({exc})")
        if not isinstance(obj, dict):
            die(f"ledger line {number} is not a JSON object")
        rows.append((line, obj))
    return rows


def read_stdin() -> dict:
    if sys.stdin.isatty():
        return {}
    raw = sys.stdin.read()
    if raw.strip() == "":
        return {}
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        die(f"stdin is not JSON ({exc})")
    if not isinstance(obj, dict):
        die("stdin JSON must be an object")
    unknown = sorted(set(obj) - set(OUTPUT_KEYS))
    if unknown:
        die("unknown field(s): " + ", ".join(unknown))
    return obj


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="append-receipt.py",
        description=(
            "Print one validated receipt JSON line.\n"
            "Does not write, commit, or push. A human appends the line in a PR.\n"
            "\n"
            "Fields come from flags, stdin JSON, or both (flags win).\n"
            "content_hash and prev_hash are always computed.\n"
            "A missing or empty ledger sets prev_hash to the sentinel genesis."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--id", help="rcpt_<uuid> or rcpt_<ulid>")
    parser.add_argument("--type", help="clarity_stamp, fork, remix, sanctuary_onboard, signal, correction")
    parser.add_argument("--ts", help="ISO-8601 UTC timestamp ending in Z")
    parser.add_argument("--actor", help="public handle, e.g. github:<handle>")
    parser.add_argument("--subject", help="path or URL this event is about")
    parser.add_argument("--promise", help="one sentence; pass an empty string only with verdict n/a")
    parser.add_argument("--build", help="path or URL of what exists")
    parser.add_argument("--proof", help="one concrete verify step")
    parser.add_argument("--verdict", help="match, partial, no_match, or n/a")
    parser.add_argument(
        "--ref",
        action="append",
        dest="refs",
        help="related path or URL; repeat to add more. Replaces stdin refs",
    )
    parser.add_argument("--corrects", help="prior receipt id; required when type is correction")
    parser.add_argument("--v", type=int, help="schema version; only 0 is accepted (default 0)")
    parser.add_argument(
        "--ledger",
        type=Path,
        help="file to read for prev_hash (default: ledger/receipts.jsonl). Not written.",
    )
    return parser


def pick(flag_value, stdin_obj: dict, key: str):
    if flag_value is not None:
        return flag_value
    if key in stdin_obj:
        return stdin_obj[key]
    return None


def require_text(value, label: str, allow_empty: bool = False) -> str:
    if value is None:
        die(f"{label} is required")
    if not isinstance(value, str):
        die(f"{label} must be a string")
    if value.strip() == "" and not allow_empty:
        die(f"{label} is required")
    return value


def assemble(args: argparse.Namespace, stdin_obj: dict) -> dict:
    v = pick(args.v, stdin_obj, "v")
    if v is None:
        v = 0
    if type(v) is not int:
        die("v must be the integer 0")
    if v != 0:
        die("v must be 0")

    receipt_id = require_text(pick(args.id, stdin_obj, "id"), "id")
    if not valid_id(receipt_id):
        die("id must be rcpt_<uuid> or rcpt_<ulid>")

    event_type = pick(args.type, stdin_obj, "type")
    if event_type is None:
        die("type is required")
    if event_type not in TYPES:
        die("type must be one of: " + ", ".join(TYPES))

    ts = require_text(pick(args.ts, stdin_obj, "ts"), "ts")
    if not valid_ts(ts):
        die("ts must be ISO-8601 UTC with a Z suffix, e.g. 2026-10-29T18:00:00Z")

    actor = require_text(pick(args.actor, stdin_obj, "actor"), "actor")
    subject = require_text(pick(args.subject, stdin_obj, "subject"), "subject")
    promise = require_text(pick(args.promise, stdin_obj, "promise"), "promise", allow_empty=True)
    build = require_text(pick(args.build, stdin_obj, "build"), "build")
    proof = require_text(pick(args.proof, stdin_obj, "proof"), "proof")

    verdict = pick(args.verdict, stdin_obj, "verdict")
    if verdict is None:
        die("verdict is required")
    if verdict not in VERDICTS:
        die("verdict must be one of: " + ", ".join(VERDICTS))
    if promise.strip() == "" and verdict != "n/a":
        die("empty promise requires verdict n/a, and proof must say why")

    if args.refs is not None:
        refs = args.refs
    elif "refs" in stdin_obj:
        refs = stdin_obj["refs"]
    else:
        refs = []
    if not isinstance(refs, list) or not all(
        isinstance(item, str) and item.strip() != "" for item in refs
    ):
        die("refs must be an array of non-empty strings")

    if args.corrects is not None:
        corrects = args.corrects
    elif "corrects" in stdin_obj:
        corrects = stdin_obj["corrects"]
    else:
        corrects = None
    if corrects is not None and not isinstance(corrects, str):
        die("corrects must be a receipt id or null")
    if event_type == "correction":
        if not isinstance(corrects, str) or not valid_id(corrects):
            die("correction requires corrects set to a prior rcpt_ id")
        if corrects == receipt_id:
            die("corrects must be a different receipt id")
    elif corrects is not None:
        die("corrects must be null unless type is correction")

    return {
        "v": v,
        "id": receipt_id,
        "type": event_type,
        "ts": ts,
        "actor": actor,
        "subject": subject,
        "promise": promise,
        "build": build,
        "proof": proof,
        "verdict": verdict,
        "refs": refs,
        "corrects": corrects,
    }


def main() -> None:
    args = build_parser().parse_args()
    stdin_obj = read_stdin()
    flag_names = (
        "id",
        "type",
        "ts",
        "actor",
        "subject",
        "promise",
        "build",
        "proof",
        "verdict",
        "refs",
        "corrects",
        "v",
    )
    if not stdin_obj and all(getattr(args, name) is None for name in flag_names):
        die("pass receipt fields as flags and/or a JSON object on stdin")

    fields = assemble(args, stdin_obj)
    ledger_path = args.ledger if args.ledger is not None else DEFAULT_LEDGER
    rows = load_ledger(ledger_path)
    for _line, obj in rows:
        if obj.get("id") == fields["id"]:
            die(f"id already in ledger: {fields['id']}")

    prev_hash = GENESIS if not rows else sha256_text(rows[-1][0])
    receipt = dict(fields)
    receipt["content_hash"] = sha256_text(canonical_payload(fields))
    receipt["prev_hash"] = prev_hash
    ordered = {key: receipt[key] for key in OUTPUT_KEYS}
    sys.stdout.write(
        json.dumps(ordered, ensure_ascii=False, separators=(",", ":")) + "\n"
    )


if __name__ == "__main__":
    main()
