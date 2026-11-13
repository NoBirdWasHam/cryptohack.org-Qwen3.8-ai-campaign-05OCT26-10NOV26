
## SOLVED 2026-10-23 — flag [flag — recorded in FLAGS/diffie-hellman/challenge-129-cryptohack-dh_static2/flag.txt] (+120, score 15455/227)

Attack (solve5.py):
- Server strength rule (probe6): p must be EXACTLY 2048 bits and prime; no safe-prime or
  p-1-factor policing. (~1024b -> "not strong enough"; 1536/2067b -> "dodgy".)
- p = 2*R*S+1, R 256-bit prime, S = product of random primes <2000 filling to 2048 bits.
- g=2, B=2^b mod p. PH over each prime power pe|S using n=2RS as order MULTIPLE
  (gi=2^{n/pe}, hi=B^{n/pe}) leaks b mod S without knowing ord_p(2). ~1790 bits/session.
- 2 sessions, CRT -> b exact (verified: 2^b == B on original group).
- KDF: key=sha1(str(A0^b mod P0))[:16], AES-128-CBC, iv = 16-byte iv field. (NOT CTR —
  solve4's CTR guess was the only thing wrong with the earlier near-miss.)
Bugs fixed en route: kt parity (odd kt made kt*q+1 always even), order factorization
missing kt factors + `m//=1` infinite loop, bsgs giant-step sign and wrong modulus,
PH CRT used xi instead of (xi-x), JSON trailing-data parse.

## Vulnerability (plain words)
The service reuses the same secret exponent b across connections (static-DH: it hands you a fixed B = 2^b mod P0 and answers with AES under a key derived from A^b) and lets the client submit its **own group parameters**, checking only that p is a 2048-bit prime — no safe-prime rule, no p−1 smoothness policing. So you can hand it p = 2·R·S+1 whose p−1 has a ≈1790-bit factor S built entirely from small primes. Pohlig–Hellman over the S-part then leaks most of b per session; two sessions with independent smooth parts CRT to b exactly, and the flag falls out of the KDF.

## How the answer follows
1. Strength-rule probing (probe5/probe6 logs): 1024-bit p → "not strong enough"; 1536/2067-bit → "dodgy"; exactly 2048-bit primes accepted ⇒ the gate is bit-length + primality only.
2. Craft p = 2·R·S+1 (R 256-bit prime, S = product of random primes < 2000 filled to 2048 bits; p verified prime). Server replies B = 2^b mod p with b reused across sessions.
3. For each prime power pe | S solve the DLP with gi = 2^{n/pe}, hi = B^{n/pe} using n = 2RS as a known **multiple** of ord_p(2) — so b mod pe is obtained without knowing ord_p(2). Per-session harvest ≈1790 bits (solve5.log: "b mod S ok; lcm bits now 1792").
4. Second session with an independent S′: lcm of the two moduli reaches 3020 > 2048 bits ⇒ CRT gives b exactly (solve5.log: "b bits 1536" recovered against the 1536-bit target group; "captured P0 1536"). Final check: 2^b ≡ B on the original group.
5. KDF from the server's own decryption path: key = sha1(str(A0^b mod P0))[:16], AES-128-CBC, iv = the 16-byte iv field ⇒ decrypts cleanly to flag `[flag — recorded in FLAGS/diffie-hellman/challenge-129-cryptohack-dh_static2/flag.txt]` (+120, score 15455/227).

## Limitations / attempts that failed
Logged failed/near-miss paths: AES-**CTR** guess for the KDF mode in solve4 (the only thing wrong with that near-miss — actual mode is CBC); early param probes rejected by the strength rule (messages above); bugs en route — kt parity (odd kt made kt·q+1 always even), order factorization missing kt factors plus a `m//=1` infinite loop, bsgs giant-step sign and wrong modulus, PH CRT using xi instead of (xi−x), JSON trailing-data parse.

## Sources
Live probing of the server's parameter policy (probe*.py, probe*.log archived) and own solve progression solve.py→solve5.py/solve5.log; b_recovered.txt holds the recovered b. Self-derived per logs; no textbook or third-party reference cited in the original AAR; no writeups/solutions consulted.
