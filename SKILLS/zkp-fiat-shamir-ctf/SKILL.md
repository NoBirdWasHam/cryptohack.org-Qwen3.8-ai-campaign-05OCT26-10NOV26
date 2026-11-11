---
name: zkp-fiat-shamir-ctf
description: Use on ZKP and Fiat-Shamir CTF forges and nonce breaks.
---

# Zero-knowledge proof systems — CTF attack surface

## Theory anchors (cite in AARs)
- GMR (Goldwasser–Micali–Rackoff, SIAM J. Comp. 16(3), 1985): defines interactive proofs + zero knowledge;
  completeness/soundness (perfect/statistical/computational).
- GMW (Goldreich–Micali–Wigderson, J. ACM 38(3), 1991): every NP language has ZK — via reduction to
  graph 3-coloring + bit-commitment. CTF ZKP puzzles are usually 3-coloring or Hamiltonicity on a small graph.
- Fiat–Shamir (CRYPTO 1986, LNCS 263): make a 3-move Sigma protocol non-interactive by setting
  challenge e = H(commitment a); Schnorr identification is the archetype (a = g^r, e = H(a), s = r + e·x).
- Random oracle model (Fischlin EUROCRYPT 1994, LNCS 1008, for methodology): FS soundness only argues in
  ROM — CTF breaks exploit the REAL hash, not the idealized one.

## The recurring CTF break patterns (all = "the oracle isn't random")
1. NONCE REUSE: same commitment a (same r) for two challenges e,e' -> x = (s-s')/(e-e') leaks the secret
   (Schnorr/DSA/ECDLP nonce reuse — same algebra as ecdsa-nonce-xor-lattice skill).
2. CHALLENGE PREDICTABILITY: server e from weak PRNG (MT19937 -> ctf-mt19937-cracking) or e = H(public stuff).
3. HASH SUBSTITUTION: verifier accepts e = H(a || filler) and you control filler -> grind until the derived
   challenge opens a forged path (proof-of-work style search).
4. PARSE/TRUST BUG: verifier state machine accepts replays or skips the binding check — read the verifier first.
5. COMMITMENT CHEAT (GMW-style puzzles): malleable/non-binding bit-commitment -> open 3-coloring commitments adaptively after seeing challenges.
6. MISSING BIJECTION CHECK: verifier permutes the reference with the prover's index vector without checking
   it is a bijection (permute_graph(G,N,perm) with repeated/negative indices) -> the accept-set widens to
   matrices B_p[i][j]=G[p_i][p_j] for ANY p; a dual-strategy commitment (opens as permuted-G for e=0 AND
   reveals a target cycle for e=1) exists iff some B_p contains the target cycle. Decide it by brute force
   over |V|^|V| index vectors, or structurally: a Hamiltonian cycle in B_p = closed walk of length |V| in G
   under i->p_i, so a disconnected G with component cycle-lengths that cannot sum to |V| (e.g. 3+2 digraph,
   |V|=5 odd walk impossible across components) kills the attack and restores soundness
   (hamiltonicity_2, CryptoHack ctf-archive 2024, port 34597).
7. SHAPE-EXCLUSION (batch FS): when responses z are sent SIMULTANEOUSLY with the commitments (bits
   computed only after ALL commitments arrive), audit whether ONE z object can answer whichever branch
   the bit picks. If the branches demand incompatible z shapes (5 cycle tuples vs 5 permutation ints),
   per-round survival = every bit matching the pre-chosen form = 2^-rounds under the model — run this
   audit BEFORE investing in binding-break/DLP compute. But treat the resulting "unwinnable" as a
   HYPOTHESIS under heavy burden of falsification, never a filed verdict: a traceback from a MALFORMED
   probe (client sent "0" where JSON was expected) proves nothing about branch compatibility, and public
   solve counts override the proof — humans solving it means a premise is wrong. Falsification battery:
   (a) determinism — send identical payloads twice; same bits ⇒ no server randomness, offline precompute
   valid; (b) cascade — perturb one never-checked "junk" entry and see whether ALL bits move; (c) prefix
   oracle — a verifier that prints per-round checks after ingesting everything leaks the bit sequence up
   to the first failure; (d) remember that branches rarely validate all of A (e.g. testcycle touches only
   the claimed cycle entries) and the FS hash usually ingests str() of EVERY entry, so unchecked slots are
   free hash-space; commitments need not be real commitments (h1 with r=0 is a valid "commitment to 1"
   whenever the code opens via pedersen_open(comm,1,r)).
   (hamiltonicity_2, CryptoHack ctf-archive 2024, port 34597 — pattern 6's closed-walk kill AND this
   pattern's 2^-rounds read BOTH stood while ~200 public solves said otherwise; the solvable path was
   still live on the same port. Do not file "needs provider redeploy, not work" while the solves page
   shows fresh solves. The falsification battery eventually cracked it: determinism + cascade results
   fed pattern 8, the actual solve. Run the pattern-8 stream-ambiguity check BEFORE any 2^-rounds filing.)

8. DUAL-SERIALIZATION COLLISION (hamiltonicity_2 SOLVED 2026-11-10, kills pattern 7's 2^-rounds read):
   when the verifier hashes ''.join(str(x) for entries), binding is over the DIGIT-STREAM, not the parsed
   matrix. One stream admits many 5x5 re-parses: merge entries (int("".join(digits))) and split another
   entry into fragments (cuts avoiding leading zeros) so the re-parsed matrix places the 1-commitments at
   the other branch's checked slots (testcycle touches ONLY the 5 claimed cycle entries — every other slot
   is free re-chunk space needing no opening at all). Degenerate perm (pattern 6's lenient perm) supplies
   1-committed chunks at convenient flat indices. Since bits derive from the stream alone, the prover
   computes all bits locally and per round sends whichever parse matches that bit: per-round equivocation
   with ZERO probability loss. 'No matrix opens both ways' stays true and irrelevant — matrix-level
   exclusivity says nothing about stream-level equivocation. Corroborated by public writeup ctfbase.com
   'dual serialization collision / misaligned tiling'. Exploit: challenge-237 folder exploit_dualparse.py
   (local replica + live both 128/128).

## Walk+gate+harvest chain pattern (294 SOLVED 2026-11-10, walked collision closed 313)
Long horizon collision searches generalize into: (1) native walkers writing hits to found_PROD_<n>.txt (PROD-name-gated harvester: NEVER glob found*.txt — selftest artifacts must be unable to trigger a live submit); (2) a gate_keeper polling both hit files and a PRE-REGISTERED Poisson gate sum(k_i^2/2S) >= 3.0 (fire = harvest owns submit; keeper exits); (3) harvester rebuilds messages, verifies the collision under an independent reference implementation BEFORE any network contact, then sends to the named service and takes the flag from service output. A hit arriving before the gate milestone is a lucky Poisson draw, not an anomaly — pre-register and say so in the AAR.
Host-safety from the same run: ~18 h of dual-walker CPU on a consumer box preceded a BSOD bugcheck 0x154 (correlation, unproven causation) — sustained fleets: owner OK first, watchdogs must not auto-resurrect jobs post-close.

## Method
Reconstruct the verifier's equality checks from source; write the algebra (a,e,s) per round; ask which
quantity is NOT fresh or NOT hidden; that quantity IS the attack. Prove a forgery locally against the
extracted verifier before touching the server.

## Canonical references
[R5] GMR, SIAM J. Comp. 16(3), 1985. [R6] GMW, J. ACM 38(3), 1991. [R7] Fiat–Shamir, CRYPTO'86, LNCS 263, pp.186-194.
[R8] Fischlin, EUROCRYPT 1994, LNCS 1008 (random-oracle methodology). https://en.wikipedia.org/wiki/Random_oracle
