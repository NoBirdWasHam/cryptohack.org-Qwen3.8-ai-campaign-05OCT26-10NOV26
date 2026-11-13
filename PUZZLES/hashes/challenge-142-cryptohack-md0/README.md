# MD0  ·  `md0`
- **Category:** hashes · **Points:** 80 · **Solved:** 2026-10-12 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/md0/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** MD length extension: sign(msg1=a*15)->sig1=hash(key||a*15||0x01); block2=pad("admin=Trueaaaaa"); forged=AES(block2).enc(sig1)^sig1; msg2=a*15||0x01||admin=Trueaaaaa

**Skills exercised:** —
**Concepts:** [`aes-gcm`](../../../TAGS/aes-gcm.md), [`hash-extension`](../../../TAGS/hash-extension.md)
**Scripts here:** `solve.py`

Full record: [AAR.md](AAR.md)
