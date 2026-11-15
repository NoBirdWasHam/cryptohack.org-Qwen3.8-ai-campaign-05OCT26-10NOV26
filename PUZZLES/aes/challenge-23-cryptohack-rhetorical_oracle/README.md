# Rhetorical Oracle  ·  `rhetorical_oracle`
- **Category:** aes · **Points:** 100 · **Solved:** 2026-10-12 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/rhetorical_oracle/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** padding oracle; Beaulieu-Desmedt: c[i-1]=D(c[i])^P[i] (not P[i-1]); exact pos=0 via distinguishing probe; ~10k queries

**Skills exercised:** —
**Concepts:** [`aes-gcm`](../../../TAGS/aes-gcm.md), [`padding-oracle`](../../../TAGS/padding-oracle.md)
**Scripts here:** `solve.py`

Full record: [AAR.md](AAR.md)
