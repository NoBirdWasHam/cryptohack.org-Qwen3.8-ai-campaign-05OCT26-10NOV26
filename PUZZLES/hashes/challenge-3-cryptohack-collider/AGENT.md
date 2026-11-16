---
record: agent-aar
puzzle: challenge-3-cryptohack-collider
category: Hash Functions
url: https://cryptohack.org/challenges/collider/
status: solved
date: 2026-10-14
flag_ref: "FLAGS/hashes/challenge-3-cryptohack-collider/flag.txt"
flag_sha256: 11718b5349ed80ace2facd8eacf4d02d27d3808c2921a4a3112140ea57af592a
skills: []
human_twin: AAR.md
---

# AGENT — Challenge 13389: Collider (50 pts, hash functions → collisions)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
The document system keys stored documents by MD5 and treats "same hash, different
content" as a crash that leaks the flag. Two facts decided the exploit:

1. **State is per-connection** (fresh `Challenge()` per socket), so a collision pair sent
   on two connections can never collide — and the two pre-stored docs' hash keys match
   their content exactly, so colliding *with them* would need a second preimage on MD5
   (~2^123, infeasible).
2. **The listener keeps the connection open and accepts multiple JSON lines per session.**
   Documents added early in the session are still in the dict later in the session.
   Within one connection: send A (added), then B with md5(B)=md5(A), B≠A → crash.

So a **generic** MD5 collision pair (not a second preimage) is all that's needed.

## reusable-rules
- **Always probe socket-challenge state lifetime before designing the exploit.**
  The per-connection vs per-session distinction turned an infeasible problem
  (second preimage, 2^123) into a trivial one (generic collision). The probe is cheap:
  send the same random input on two connections and compare "added" vs "already exists".
- **CryptoHack JSON-line listeners keep the connection open for multiple requests** —
  treat each session as a stateful conversation, not a one-shot RPC.
- **Generic MD5 collisions are a commodity** once you have md5fastcoll/hashclash built:
  seconds on a laptop, no GPU. Keep the built tool in the toolbox.
- When a service stores `hash → content`, check whether the stored keys actually match
  the stored contents (extract the real bytes from the source, don't trust a copy-pasted
  string). Consistent storage ⇒ only second preimages reach it; inconsistent storage
  (swapped/mismatched keys) ⇒ sending the stored content itself crashes it.

## anti-patterns / limits
The second-preimage path was eliminated by source verification rather than attempted; the naive two-connection plan was voided by the per-connection-state probe before it was exploited (probe evidence above). No further failed paths recorded in run logs — exploit worked first try against live.

## artifacts [OBSERVED]
- code: 13389.py, solve.py
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided server source `13389.py`; tool source: Marc Stevens' hashclash/md5fastcoll collision core (unmodified core, own driver — cited in the original AAR, `md5fastcoll/BUILD.md`); Python `hashlib` for verification. Method self-derived from statement + live probing; no solutions page, no writeups used.
