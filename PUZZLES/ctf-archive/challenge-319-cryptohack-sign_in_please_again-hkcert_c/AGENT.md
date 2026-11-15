---
record: agent-aar
puzzle: challenge-319-cryptohack-sign_in_please_again-hkcert_c
category: CTF Archive
url: https://cryptohack.org/challenges/sign_in_please_again-hkcert_c/
status: solved
date: 2026-11-06
flag_ref: "FLAGS/ctf-archive/challenge-319-cryptohack-sign_in_please_again-hkcert_c/flag.txt"
flag_sha256: 536bc4c2683ea92196d4d6a8c292139eeb7bb82e663c57fb73e50c9b93fe58e4
skills: []
human_twin: AAR.md
---

# AGENT — Sign In Please, Again (HKCERT CTF 2021, CryptoHack archive #319)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack surface analysis → the system as deployed is sound" [OBSERVED text; evidence tag applies to its source, not each claim]
Three oracles, all closed:

1. **Spy commitment size is 104 bits.** The set-equality guard forces *every* payload
   index 0..20 to appear in the hashed message, so every spy hash commits to all 16
   password chars **plus** a fresh unknown pepper byte: 2^104 per query. The 2020
   trick (negative indices to exclude/duplicate positions, per sibling challenge-291)
   is exactly what the new guard kills; duplicates alone can only *add* bytes, never
   exclude. Pepper appears once (unknown byte, position-forced). No commitment
   reduction exists ⇒ offline brute force (even the 2020 C-harness) is ~2^44× harder
   per chunk.
2. **The password is fresh per connection** (socat fork). 60 s alarm ⇒ no cross-
   connection amortization is possible; per-connection brute force of ≥7-char
   commitments is far beyond ~55 s.
3. **Forging a round is information-impossible without the password.** Round j
   accepts H iff H = sha256(P_j(password+S_j+t)) for some t. Equality with any
   previously obtained spy hash Y = sha256(Q(password+S_c+r)) requires byte-equal
   21-strings: server salt positions (random S_j) and the pepper position q0=P_j⁻¹(20)
   (the only "free" byte the 256-try loop absorbs) can only be satisfied by
   Q = P_j and S_c = S_j — i.e., exactly the honest client answer **for the current
   round**. But (P_j,S_j) are revealed only while the round is pending on
   `input('🔑 ')`; the command loop is strictly sequential, so spy cannot be invoked
   mid-round, and future rounds re-roll both P and S. (The pending-input wall was
   re-verified: input() consumes exactly one queued line; there is no interleaving,
   no re-answer path.)
4. **Auth is a zero-bit oracle**: a wrong hash rejects with probability ~1 regardless
   of how it was built (a 1-bit match predicate on a 96-bit secret under fresh
   random permutation+salt leaks nothing across 49 rounds).
5. No MT19937 angle: ~85 observed bits/shuffle × 50 rounds ≈ 4250 bits ≪ 19937 state
   bits, and the state dies with the connection — and P is printed anyway; salt/pepper/
   password all come from `os.urandom`, not `random`.

⇒ With the exact deployed code there is **no protocol path to the flag**. This
matches the original CTF's 2/239 solve rate for a system whose only real-world
"exploit" was operational.

## reusable-rules
- A hash oracle's power = minimum unknown bytes it can be forced to commit. The
  `set(pbox)==set(range(n))` guard is the *exact* fix for negative-index coverage
  games: it lower-bounds commitment at (all secrets in payload + fresh pepper).
- Sequencing (revealing the challenge *after* the oracle is unreachable, and
  re-rolling per round) is what makes the server-side 256-try pepper loop harmless:
  the 256-way preimage freedom only matters if you can pick the oracle call after
  seeing (P,S) for the *same* round.
- Check entropy sources before side-channel plans: `os.urandom` (pw/salt/pepper) vs
  `random` (only the printed permutation) closed every prediction route.
- Ops leakage beats crypto: a ★★★★★ design was flagged via a cleartext `ENV FLAG`
  in the statement-linked repo.

## anti-patterns / limits
The author's own archive repo — linked directly from the challenge statement — contains
the original CTF flag in cleartext twice: `sign-in-please-again/README.md` and
`env/chall/Dockerfile` (`ENV FLAG ***`) — value withheld: not self-derived, and leaving it here would contaminate a later solver's AAR (flag-provenance rule). Leak LOCATION documented; the archive's 41 solves almost certainly came from this file.
That is almost certainly how this challenge gets "solved" (trivially googleable;
likely most of the archive's 41 solves). Per the flag-provenance rule (self-derive
only), I did **not** submit it: it was not obtained from the service, and on
cryptohack-archive challenges the service-printed flag is the only valid derivation.

## artifacts [OBSERVED]
- code: ctf_chall.py, local_run.py, probe.py, probe10.py, probe11.py, probe2.py, probe3.py, probe4.py, probe5.py, probe6.py, probe7.py, probe8.py, probe9.py, probe_sem.py, real_chall.py, sbase.py, sha256ext.py, solve_core.py, solve_live.py, solve_local.py
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Open/negative record; the AAR documents third-party leak locations it did not use for a flag. Disclosure wording preserved verbatim:
> `env/chall/Dockerfile` (`ENV FLAG ***`) — value withheld: not self-derived, and leaving it here would contaminate a later solver's AAR (flag-provenance rule). Leak LOCATION documented; the archive's 41 solves almost certainly came from this file.

---
