# Key recovery (DCTF)  ·  `key_recovery-dctf2022`
- **Category:** ctf-archive · **Points:** 0 · **Solved:** 2026-11-02 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/key_recovery-dctf2022/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** The inherited `solve.py/solve2.py/solve3.py` modeled the round as `sub(x⊕k)` (XOR before S-box) and searched for an integral test invariant under key-byte conjugation — every such test is provably blind to half the bits …

**Skills exercised:** —
**Concepts:** —
**Scripts here:** `attack.py`, `dbg.py`, `dbg2.py`, `probe.py`, `probe2.py`, `probe3.py`, `solve.py`, `solve2.py`, `solve3.py`, `solve4.py`

Full record: [AAR.md](AAR.md)
