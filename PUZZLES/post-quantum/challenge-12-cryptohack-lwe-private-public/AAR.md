# AAR — lwe-private-public (CryptoHack Post-Quantum/LWE, 25 pts)

Date: 2026-10-14 · Status: SOLVED (server-verified, flag `1568`)

## Result
Flag `1568` (bare integer) accepted.

## Attack
Pure knowledge question: **Kyber1024 (ML-KEM-1024) public key = 1568 bytes**
(per the NIST FIPS 203 parameter table: ML-KEM-512 pk=800 B, ML-KEM-768 pk=1184 B,
ML-KEM-1024 pk=1568 B; secret keys 3932/3888/6368… precisely: sk 1632/2560/3968 B
for 512/768/1024). The LWE public-key discussion in the statement (O(n² log q)
scaling) is the setup; the answer is the standard's parameter.

## Verification
- Cross-checked against the published Kyber/FIPS 203 parameter table (pk_1024 = 1568).
- Server: `submit_flag.py lwe-private-public 1568` → accepted.

## Lessons
- CryptoHack "Post-Quantum" LWE track mixes real crypto with trivia; read the whole
  statement — the last line is the actual question.
- Kyber parameter sizes (FIPS 203): pk 800/1184/1568 B, sk 1632/2560/3968 B,
  ct 768/1088/1568 B, shared 32 B.

## Evidence
- This folder: site.md, flag.txt


## Vulnerability (plain words)
None — this is a knowledge-retrieval item, stated plainly: it asks you to look up a standardized parameter size, not to break anything. The conceptual link to the track is that an LWE public key (a square matrix plus a vector) costs O(n² log q) bits, and real standards pin exact byte counts for each security level.

## How the answer follows
The statement's closing question asks for the public-key size of the largest Kyber/ML-KEM parameter set. The FIPS 203 parameter table answers it directly: pk = 800 B (ML-KEM-512) / 1184 B (ML-KEM-768) / **1568 B (ML-KEM-1024 = Kyber1024)**. `1568` submitted BARE and accepted; live-verified 2026-10-13. Cross-checked at solve time against the published Kyber/FIPS 203 table (pk 800/1184/1568, sk 1632/2560/3968, ct 768/1088/1568, ss 32).

## Limitations / attempts that failed
- Pure retrieval — no derivation exists to record; nothing failed. The specific document copy consulted at solve time is not named in the run logs (only the cross-check outcome is recorded).

## Sources
- FIPS 203 (ML-KEM) / Kyber published parameter table — a standard, not a writeup.
- Course statement page https://cryptohack.org/challenges/post-quantum/lwe-private-public/ (cached). No solution artifacts consulted.
