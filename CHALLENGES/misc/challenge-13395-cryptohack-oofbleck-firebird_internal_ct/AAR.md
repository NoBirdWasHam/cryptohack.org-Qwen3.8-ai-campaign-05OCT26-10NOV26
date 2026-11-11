# Oofbleck (Firebird Internal CTF) — AAR

**Solved:** yes. Flag: `firebird{unf0rtun4t3ly_1t_i5_s0_h4rd_t0_g3t_cryp70gr4phy_d0n3_r19h7}`
Submitted to slug `oofbleck-firebird_internal_ct`; solved-list verified via api_solved (259 entries, includes "Oofbleck (Firebird Internal CTF)"). Archive challenge → score_delta 0 (expected, 0-pt archive).

## The vulnerability (first-principles read of chall.py)
`encrypt()` calls `AES.new(iv, AES.MODE_OFB, key)` — **key/IV arguments swapped**.
Consequences:
- The AES key is `iv = os.urandom(16)`, and `iv` is **prepended to the ciphertext** in output.txt → attacker knows the AES key.
- The secret `key` (unknown) is merely the OFB initial feedback state X0.
- Keystream chain over 5 blocks (flag = 68 B, PKCS7 → 80 B): X1=E_K(X0), X_{i+1}=E_K(X_i). OFB itself is fine; this is a pure API-misuse bug ("unfortunately it is so hard to get cryptography done right").

## Attack
Known keystream material:
- X1[:9] = ct[:9] ⊕ 'firebird{' (regex-asserted header).
- X5[3:16]: flag layout = header(9) + \w{58} + '}'(1) = 68 B ⇒ byte 67 = '}', bytes 64–66 ∈ \w, pad = 0x0c×12 ⇒ X5[3:16] = ct[68:] ⊕ 0x0c, X5[2] = ct[67] ⊕ '}'.
So X5[:3] has only 62³ = 238,328 candidates. For each: X1 = D_K⁴(X5); accept iff X1[:9] matches known bytes and X1[9:16] ⊕ ct[9:16] ∈ \w⁷ (unique survivor; other candidates pass the 9-byte check with prob 2⁻⁷²). Then forward-decrypt all blocks with E_K chain.

## Key numbers
- 96 B output = 16 B iv (=AES key) + 80 B ct; 238k AES-128 ops; runtime < 1 s.

## Limitations / failures (evidenced)
- First solve.py wrongly modelled flag bytes 64–67 as \w⁴ (forgot byte 67 is '}') → full \w⁴ scan (14.8M candidates, 2m49s) returned "not found". Fixed tail model → \w³ + '}' solved instantly.
- Initially wasted calls on archive.cryptohack.org: TLS `SEC_E_WRONG_PRINCIPAL` and 404 for /static/challenges/…; live cryptohack.org serves the files.
- Considered (and rejected) ~2⁴² direct brute force of the X1 tail and X3-MITM before spotting the padding-block anchor.

## Learning point
When a stream-like mode's block key is recoverable from output, hunt for *known keystream* (headers + PKCS7 + fixed delimiters); a chain of E_K inversions converts a 56-bit search into a 3-char brute force. Mind off-by-one flag layout before sizing a brute force.

## Sources
Sources: challenge-provided materials only; self-derived per run logs.
