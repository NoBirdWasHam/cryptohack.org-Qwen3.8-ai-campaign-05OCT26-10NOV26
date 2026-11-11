# AAR — scriptkiddie (70 pts)

**Result:** SOLVED — flag submitted, `score_delta: 70`. Date: 2026-10-15 (UTC).

## Sources

- Statement: https://cryptohack.org/challenges/diffie-hellman/ (slug `scriptkiddie`)
- Files: `script.provided`, `output.provided` (URLs in site.md)
- **NOT consulted:** /solutions/, /solves/, any external writeups.

## Flag

`crypto{b3_c4r3ful_w1th_y0ur_n0tati0n}`

## How it was solved

1. Read `script.provided`. The "DH" functions are:
   `generate_public_int(g, a, p): return g ^ a % p` and
   `generate_shared_secret(A, b, p): return A ^ b % p`.
   Python precedence: `%` binds tighter than `^`, so these compute
   **bitwise XOR**: `B = g XOR (b % p)`, `secret = A XOR (b % p)`.
   The author meant modular exponentiation `pow(g, a, p)` — classic script-kiddie bug.
2. Everything needed is in `output.provided` (p, g=2, A, B, iv, ciphertext).
   Invert the XOR: `a = A XOR g`, `b = B XOR g`; shared secret = `A XOR (b % p)`.
   (No discrete log at all — "DH" here was XOR, which is its own inverse.)
3. Reused the script's own key derivation: key = SHA1(str(secret))[:16],
   AES-128-CBC with the given iv, strip PKCS7 → flag.

## Exact commands

```
~/tools/crypto-ctf/venv/Scripts/python.exe -u solve.py
cd ~/Practice_runs/cryptohack_org && python submit_flag.py scriptkiddie "crypto{b3_c4r3ful_w1th_y0ur_n0tati0n}"
```

## Exact outputs

`solve.py` (full in `live_transcript_2026-10-15.txt`):
```
a        = 539556019868756019035615487062583764545019803793635712947528463889304486869497162061335997527971977050049337464152478479265992127749780103259420400564906895897077512359628760656227084039215210033374611483959802841868892445902197049235745933150328311259162433075155095844532813412268773066318780724878693701177217733659861396010057464019948199892231790191103752209797118863201066964703008895947360077614198735382678809731252084194135812256359294228383696551949880
b        = 652888676809466256406904653886313023288609075262748718135045355786028783611182379919130347165201199876762400523413029908630805888567578414109983228590188758171259420566830374793540891937904402387134765200478072915215871011267065310188328883039327167068295517693269989835771255162641401501080811953709743259493453369152994501213224841052509818015422338794357540968552645357127943400146625902468838113443484208599332251406190345653880206706388377388164982846343349
secret   = 1168437420478847128567287495143285894399296237433016158919001493779411967894206164077206908954446484725389599764567727952622594610684934485141885926703436206642200142494285546376255875774700779917367973365741551091767048386085714152231865882567523710833481816949106535050911248007261385879313717460702906628745931918159028073548099220012902186566302657796028622790643541788969391922680522075556816558276927136104225021342933713272949133441034264101082531947970191
PLAINTEXT: crypto{b3_c4r3ful_w1th_y0ur_n0tati0n}
```

`submit_flag.py scriptkiddie "crypto{b3_c4r3ful_w1th_y0ur_n0tati0n}"`:
```json
{"submitted": "crypto{b3_c4r3ful_w1th_y0ur_n0tati0n}", "submit": {"ok": true, "status": 200, "body": "Flag submitted. Press back to return to the challenge. Please enable JavaScript for a better experience"}, "before": {"score": 7535, "solved": 161}, "after": {"score": 7605, "solved": 162}, "score_delta": 70}
```

## Verification

- Decryption produced a clean ASCII flag with valid PKCS7 padding.
- `score_delta: 70` from the user API — ground truth.

## Lessons

- **`g ^ a % p` is `g XOR (a % p)`, not `g^a mod p`.** In Python `^` is XOR and `%`
  binds tighter; modular exponentiation is `pow(g, a, p)`. Any home-grown crypto
  using `^` for "exponentiation" is XOR — trivially invertible (XOR is its own
  inverse). The flag says it: "be careful with your notation".
- Reading the provided source and matching each expression's *actual* Python
  semantics (precedence!) is the whole challenge — no server, no log needed.

## What I did / did not do

- Read both provided files, inverted the XOR, decrypted, submitted.
- Did not run the provided script interactively (not needed; all inputs known).

## Limitations

None. Flag submitted and API-verified (score_delta > 0).

## Configuration

- Date: 2026-10-15 (UTC); host: Windows 11, git-bash; user OWNER.
- Interpreter: `~/tools/crypto-ctf/venv/Scripts/python.exe` (PyCryptodome).
- Working dir: `~\Practice_runs\cryptohack_org\challenge-125-cryptohack-scriptkiddie`.
- Network: cryptohack.org only (file downloads + submit/API). No socket.
- Evidence: `solve.py`, `script.provided`, `output.provided`, `live_transcript_2026-10-15.txt`, `flag.txt`.
