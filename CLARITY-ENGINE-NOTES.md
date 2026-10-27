# Clarity engine notes

**How "receipts match blueprint" gets checked.** Notes, not software. Fork freely.

This is the last Phase 1 foundation piece: a plain checklist for deciding whether a UniversalOS build matches its promise. No dashboard. No score. Pass / fail / unfinished — labeled.

Pairs with:
- [RECEIPTS-TEMPLATE.md](RECEIPTS-TEMPLATE.md) — promise → build → proof
- [TRANSPARENCY-STUB.md](TRANSPARENCY-STUB.md) — decisions/data open by default
- [LENS-FIRST-RULE.md](LENS-FIRST-RULE.md) — diagnose the framework before conclusions
- [CLARITY-PLEDGE.md](CLARITY-PLEDGE.md) — the five lines everyone agrees to

---

## What "match" means
A piece **matches** when:

1. A **promise** was written *before* the build (name, one sentence, who it's for, what "done" means).
2. A **build** exists at a checkable place (path, link, date).
3. **Proof** steps let a stranger verify without vibes.
4. Gaps are **labeled**, not hidden.
5. Facts stay **facts** — no alchemy into slogans.

If any of 1–3 fail, it isn't done. Say so.

---

## Check sequence (run in order)

### A. Blueprint present?
- [ ] Promise fields filled (not invented after shipping)
- [ ] "Done" is testable in one sentence
- [ ] Audience is named

**Fail:** no promise → stop. Cosplay.

### B. Build present?
- [ ] Artifact exists where claimed
- [ ] Date is real
- [ ] Unfinished items are listed (even if "none")

**Fail:** promise with no build → unfinished. Label it.

### C. Proof runnable?
- [ ] Steps are concrete (do X, see Y)
- [ ] A person who wasn't in the room can follow them
- [ ] "What matches" / "What doesn't" both filled

**Fail:** vibes-only proof → not done.

### D. Openness (transparency layer)
- [ ] Closed bits have a written why
- [ ] No secret gaps dressed as polish

**Fail:** unlabeled closed → cosplay transparency.

### E. Lens (when the topic is charged)
- [ ] Lens was named *before* conclusions (power strategy / truth claim / narrative weapon — or an equivalent ask)
- [ ] Analysis didn't shape the narrative around curiosity first

**Fail:** conclusions before lens → re-run with the ask.

### F. Verdict
Pick one and write it on the receipt:

- **Match** — promise, build, and proof line up
- **Partial** — some fields match; gaps labeled; next ugly ship named
- **No match** — build does not meet promise; say how

No averages. No green dashboards that hide red cells.

---

## Who runs the check
Anyone. Fork the receipt, run A→F, publish the verdict next to the piece. Bot or human — same checklist.

What's unfinished here (labeled): no automated runner; no CI hook; notes only. Next ugly ship could be a one-page "verdict" template or a bot prompt that walks A→F.

---

## Rules
1. Checklist before costume.
2. Incomplete beats cosplay.
3. Forkable. Steal this without asking.
4. If it doesn't match the promise, it isn't done — and the engine's job is to make that visible.

*Out of many, one. For real this time.*
