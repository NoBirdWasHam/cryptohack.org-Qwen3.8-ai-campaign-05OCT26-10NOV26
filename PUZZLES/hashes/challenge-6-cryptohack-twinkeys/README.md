# Twin Keys  ·  `twinkeys`
- **Category:** hashes · **Points:** 100 · **Solved:** 2026-11-06 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/twinkeys/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** OPEN: needs MD5 collision with W0-W5 word-forcing (one msg byte19=0x61, other 0xE1, bytes 0-18+20-21 = KEY_START). fastcoll brute-force fails (2^-128 IHV cond); chosen-prefix (hashclash cpc) hours-CPU. Full forcing plan …

**Skills exercised:** —
**Concepts:** [`groebner-sat`](../../../TAGS/groebner-sat.md)
**Scripts here:** `solve.py`

Full record: [AAR.md](AAR.md)
