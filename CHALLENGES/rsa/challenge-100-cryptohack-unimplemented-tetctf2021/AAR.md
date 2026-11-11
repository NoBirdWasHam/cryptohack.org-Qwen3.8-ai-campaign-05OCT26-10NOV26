# AAR — unimplemented-tetctf2021 (CryptoHack CTF archive)

## Solved: yes
Flag: derived locally from provided output.txt; verified by re-encrypting the recovered plaintext and matching the given ciphertext byte-for-byte; then accepted by the site (ok:true, solved count 282→283, score_delta 0 as expected for 0-pt archive).

## The vulnerability
The challenge "invents" RSA over Gaussian integers: message m = (re, im) pair, ciphertext = m^65537 computed with complex multiplication mod n where n = p²q² (2021 bits). Decryption is "unimplemented".

The flaw is trivial: `output.txt` prints the private key `(p, q)` itself. So the task reduces to writing the missing decrypt.

## The attack
- Z/p²[i] unit-group order, from first principles (local ring with maximal ideal (p), residue ring Z/p²[i]/(p)):
  - p ≡ 3 mod 4 (inert): residue field F_{p²}, |R*| = p²(p²−1)
  - p ≡ 1 mod 4 (split): R ≅ Z/p² × Z/p², |R*| = p²(p−1)²
- d = e⁻¹ mod lcm(order(p), order(q)); decrypt by complex exponentiation mod p² and mod q² separately, then CRT both components.
- Strip padding: pad_data (bytes 1–255, no zeros) + \x00 + flag; first \x00 in the 504-byte plaintext is the separator.

## Key numbers
- n = p²q², 2021 bits; L = 253-byte ct halves; padded plaintext 504 bytes.

## Glue bugs caught by the in-process round-trip fuzz (per brief's NEW pre-wall rule)
1. CRT: used `1−a` for the second cofactor — that identity only holds for prime moduli, not prime *squares*. Fixed with the true inverses a=(q²)⁻¹ mod p², b=(p²)⁻¹ mod q².
2. Unpad alignment: encrypt left-pads each 252-byte half with a zero byte via `to_bytes(253)`; naive `to_bytes(L)` reconcatenation shifted the plaintext by 2 bytes and split on a stray pad-boundary zero. Fixed by rebuilding halves at 252 bytes.
Both caught in minutes by the standalone encrypt→decrypt round-trip assert before ever trusting the final answer.

## Limitations
None — direct solve, no wall. No external writeups/solutions consulted (0 solutions exist on site anyway). Flag provenance: purely local derivation from provided files + site acceptance.

## Files
- solve.py (runnable: `python3 solve.py` in this folder)
- verify.py (re-encrypt match + primality check)
- flag_unimplemented-tetctf2021.txt

## Vulnerability (plain words)
The challenge "invents" RSA over Gaussian integers: a message is a pair (re, im), ciphertext = m^65537 under complex multiplication mod n = p²q² (2021 bits), and decryption is deliberately "unimplemented". The actual flaw is dumber than the algebra: `output.txt` prints the private primes `(p, q)` themselves. So the task reduces to writing the missing decrypt — no factoring, just the correct unit-group orders over Z/p²[i] and a CRT that is valid for prime *squares*.

## How the answer follows
1. Read `(p, q)` from the provided `output.txt` (the statement's own output leaks the private key).
2. Per prime, compute |Z/p²[i]ˣ| by p mod 4 (derived from first principles — local ring with maximal ideal (p)): inert p ≡ 3 mod 4 → p²(p²−1); split p ≡ 1 mod 4 → p²(p−1)².
3. d = e⁻¹ mod lcm(order_p, order_q); raise both ciphertext halves (253-byte halves, L recorded) to d in Z[i] mod p² and mod q² separately; CRT the components with the TRUE inverses a=(q²)⁻¹ mod p², b=(p²)⁻¹ mod q² — the `1−a` cofactor shortcut is valid only for prime moduli (glue bug #1, caught by round-trip fuzz).
4. Rebuild the 504-byte padded plaintext from two 252-byte halves (encrypt zero-left-pads via `to_bytes(253)`; naive `to_bytes(L)` reconcatenation shifts by 2 bytes — glue bug #2, also fuzz-caught), then split on the first \x00 separating pad_data (bytes 1–255, no zeros) from the flag.
5. Verify: re-encrypt the recovered plaintext and match the given ciphertext byte-for-byte (verify.py); site accepted the flag (ok:true, solved 282→283).

## Limitations / attempts that failed
First-try solve on the math; the two failed paths logged are glue bugs, not wrong mathematics (CRT cofactor identity for prime squares; unpad alignment) — both caught in minutes by a standalone encrypt→decrypt round-trip assert before trusting the answer. No external writeups consulted; flag provenance purely local derivation + site acceptance.

## Sources
Provided files only: statement.txt and output.txt (which leaks p, q). Per the original AAR, the Z/p²[i]ˣ order formulas were derived from first principles in-session; no textbook or third-party solution cited ("self-derived per logs"). 0 solutions exist on-site for this archive challenge.
