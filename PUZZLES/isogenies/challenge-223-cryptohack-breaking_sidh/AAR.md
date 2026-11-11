# AAR — breaking_sidh (223, 250 pts, isogenies) — SOLVED 2026-10-22

Flag: `crypto{welcome_to_the_future_of_isogenies}` (submitted, score_delta +250, verified by API).

## What this was
Full Castryck–Decru key-recovery attack on SIDH (p = 45·2^117·3^73−1, f=45) — recover
Bob's 73 ternary secret digits from his public key via the gluing oracle, then compute
the shared j-invariant and AES-decrypt the flag. No local Sage on this host.

## What I did
- **SageCell as a remote Sage**: `POST /sockjs/kernel/info` + WebSocket `execute`
  (sagecell_client.py). ~40 s CPU per cell → work chunked to ≤6 oracle calls/cell,
  SETUP block (field/curves/bases, ~2.5 s) prepended to every cell (no state persists),
  `kernel_dead` → retry, digits checkpointed to `skB_state.json` after every chunk.
- Ported jack4818/Castryck-Decru-SageMath (richelot_aux + uvtable) into that harness.
- Fixed four real bugs (each verified, not guessed):
  1. Original code shadows `i` (=√−1) with a loop variable → NameError after first loop.
  2. Original K-search `2^a·3^(b−1)·R until order 3` only terminates for f=1; f=45 needs
     K = ((p+1)/3)·R.
  3. Off-by-one: original `i` is the 1-based digit number → 0-based digit di uses
     expdata[di], kernel 3^(b−di−1), chain length di+1; prolongation digits are even di≥2.
  4. **K→alternativeK swap is permanent**: after digit di=2 needs the alt prolongation
     (it did — K gave all-splits), every later prolongation digit must use the alt chain.
     My resume logic re-defaulted to the K chain each cell → digits ≥4 silently became
     default-2 (all-False oracle). Caught by auditing split patterns + last-3 j-match
     failing (TNONE over all 27 candidates).
- Last-3 disambiguation: cand = key + t·3^70, t ∈ 0..26, test j(E0/⟨P3+cand·Q3⟩)==j(EB).
- Shared secret: 73-step 3-chain from EA with kernel ⟨φA(P3)+sB·φA(Q3)⟩;
  key = sha256(str(j)) with Sage format `<im>*i + <re>`; AES-CBC → flag.

## Verification chain
torsion basis pairing asserts; phase-1 unique-split out of 8; digit-2 unique split under
alt chain; per-digit audit (genuine unique split vs default) for di=3,4,5; last-3 j-match
hit exactly one t; AES plaintext starts `crypto{`.

## Limitations
- Digits 4..69 were re-run with the alt chain; only di∈{3,4,5} were individually audited
  for split-genuineness — the rest rely on the final j-match + decrypt hit (which is a
  complete check of the whole key, so this is fine).
- SageCell is a shared public service; the run took ~25 min wall across ~40 cells.

## Configuration
- Windows 11, git-bash; python3 = 3.10 (websocket-client); gp64 2.17.4 for cross-checks.
- Working dir: `~\Practice_runs\cryptohack_org\challenge-223-cryptohack-breaking_sidh`
  (run_attack.py = driver, sagecell_client.py = transport, final2.py = chunked last-3,
  decrypt.py = AES; run_full2.log = clean run).
- submit_flag.py breaking_sidh → +250.

## Vulnerability (plain words)
SIDH published, alongside Bob's curve, the images of Alice's torsion basis under Bob's secret isogeny (and vice versa) — i.e. the public key carries the *footprint of the secret walk*. The Castryck–Decru (2022) break: glue Alice's and Bob's curves into one abelian surface (dimension 2), where a deliberately longer auxiliary isogeny walk can be taken; measuring how the glued surface splits as the walk proceeds exposes Bob's secret ternary digits one at a time. Recover the digits, redo the short 3-chain walk, and the shared j-invariant is the AES key. The mathematics is heavy; for this run the *engineering* was the wall (no local Sage on the host).

## How the answer follows
1. From the instance (p = 45·2^117·3^73−1, f=45): E0, Bob's public key (EB, φB(P4), φB(Q4)), plus the AES blob keyed by sha256 of the shared j.
2. Gluing walk over the surface E0×EB gives an oracle: for each secret digit di, the three candidate prolongations of the current chain are tested and the one with a *unique split pattern* is the digit (digit 2 needed the alternative prolongation chain, which then stays permanent for all later prolongations).
3. Last digits are jointly ambiguous: enumerate cand = key + t·3^70, t ∈ 0..26, keep the t with j(E0/⟨P3+cand·Q3⟩) == j(EB) — exactly one hit.
4. With recovered sB: 73-step 3-isogeny chain from EA with kernel ⟨φA(P3)+sB·φA(Q3)⟩ → shared j → key = sha256(str(j)) in Sage `<im>*i + <re>` format → AES-CBC decrypt → plaintext starting `crypto{`.
5. Execution: each Sage cell ran on SageCell (WebSocket, ~40 s CPU cap) — stateless SETUP block prepended, ≤6 oracle calls per cell, digits checkpointed to skB_state.json, kernel-death retries (run_attack.py + sagecell_client.py).

## Limitations / attempts that failed
- Four real port bugs of the Richelot/gluing framework (shadowed `i`, K-search valid only for f=1 — needed K=((p+1)/3)·R, digit-index off-by-one, and the non-permanent K→alt-chain switch in resume logic that silently defaulted digits ≥4 to 2); each caught by split-pattern audits + the last-3 j-match failing (TNONE over all 27), then fixed deliberately.
- Digits 4..69 not individually audited for split-genuineness (only di∈{3,4,5}); the final j-match + successful AES decrypt are the complete key check, per the AAR.
- SageCell is a shared public service: ~25 min wall over ~40 cells with death/retry cycles.

## Sources
Statement + provided instance files. Mathematics: Castryck–Decru key-recovery attack on SIDH (2022 paper); the run ported the jack4818/Castryck–Decru–SageMath implementation of that paper's math as recorded in the AAR (attack-algorithm reference, not a challenge writeup). No CryptoHack solutions pages, solve threads, or third-party challenge writeups consulted; verification = pairing asserts, unique-split audits, single t-match, and the `crypto{` plaintext.
