# AAR — dh_additive (70 pts)

**Result:** SOLVED — flag submitted, `score_delta: 70`. Date: 2026-10-15 (UTC).

## Sources

- Statement: https://cryptohack.org/challenges/diffie-hellman/ (category page, slug `dh_additive`)
- Service: `socket.cryptohack.org:13380` (passive; fresh values per connection)
- Decrypt script: "Deriving Symmetric Keys" = `challenge-75-cryptohack-dh-starter-5/decrypt_provided.py` (from the dh-starter-5 course challenge, already in this repo)
- **NOT consulted:** /solutions/, /solves/, any external writeups.

## Flag

`[flag — recorded in FLAGS/diffie-hellman/challenge-9-cryptohack-dh_additive/flag.txt]`

## How it was solved

1. Connected to `socket.cryptohack.org:13380` (no input needed). The server prints
   the intercepted DHKE traffic: Alice's `{p, g, A}`, Bob's `{B}`, and Alice's
   `{iv, encrypted}` (AES-128-CBC, per the "Deriving Symmetric Keys" script).
2. The statement's hint: they did DHKE in an **additive** group (Z_p under addition)
   instead of multiplicative. In the additive group the "discrete log" is trivial:
   `A = a·g (mod p)` ⇒ `a = A · g⁻¹ (mod p)` — just multiply by the inverse of g.
3. Computed `a = A * pow(2, -1, p) % p` and `b = B * pow(2, -1, p) % p`.
4. Shared secret of additive DH: `secret = a·B % p` (= `b·A % p` = `a·b·g mod p`;
   asserted both sides equal).
5. Key = `SHA1(str(secret))[:16]`; AES-128-CBC decrypt with the server's `iv`;
   strip PKCS7 → `[flag — recorded in FLAGS/diffie-hellman/challenge-9-cryptohack-dh_additive/flag.txt]`.

## Exact commands

```
~/tools/crypto-ctf/venv/Scripts/python.exe -u solve.py
cd ~/Practice_runs/cryptohack_org && python submit_flag.py dh_additive "[flag — recorded in FLAGS/diffie-hellman/challenge-9-cryptohack-dh_additive/flag.txt]"
```

## Exact outputs

`solve.py` printed (abridged — full in `live_transcript_2026-10-15.txt`):
```
a = 1605483906634457744337671772406177806928745981659688225200154205710691314071995833904932680041196853665895488528128418148606142506201508350566561733264410589329103836027481875084153445221491894010600175179208181811326363433555466074768539511062175392250150402299935043069059304216911963160437914328091519858526923074675052567612970016448913974877713853382618159585073424452035578870127405308608163418271633709433619111404153222119645849432645989922399672085029978
b = 1489519098049959538289971840284871068945959125716610015006549582720393427308371973885293565681075333295867539382993243102643597513385781222332165709763602854337637546288603296577250392047630991299100316654360779143646382438097602193673665354979244807088323628255271435718019892847125959110827270607148516149224092930154758831748132175514640257078339258051821101362341226641552630705982708516547821382813671941587264782007315889079606168961641756978637455235634118
secret = 1035957283239886472374974009901448422707024253041695476284303679253847930398071625182398596659460693625469598026695214429340584220010972534818850756703211327711687736035144215113810651154011967826480617768512198836627602426084225477813075920453098975003022451324267087964829247397594766248516376025329324163296028122517019058879808584507141328024880241889123548374535697754153356326958235608225582615818305797857121396261689119758130365361389267058579281309851389
PLAINTEXT: [flag — recorded in FLAGS/diffie-hellman/challenge-9-cryptohack-dh_additive/flag.txt]
```

`submit_flag.py dh_additive "[flag — recorded in FLAGS/diffie-hellman/challenge-9-cryptohack-dh_additive/flag.txt]"`:
```json
{"submitted": "[flag — recorded in FLAGS/diffie-hellman/challenge-9-cryptohack-dh_additive/flag.txt]", "submit": {"ok": true, "status": 200, "body": "Flag submitted. Press back to return to the challenge. Please enable JavaScript for a better experience"}, "before": {"score": 7465, "solved": 160}, "after": {"score": 7535, "solved": 161}, "score_delta": 70}
```

## Verification

- `a·B % p == b·A % p` asserted in-script (additive DH consistency).
- Decrypt produced a clean ASCII flag with valid PKCS7 padding (not garbage).
- `score_delta: 70` from the user API — ground truth.

## Lessons

- **Additive-group DLP is trivial.** In Z_p under addition, the map x ↦ x·g is a
  bijection, so "log_g(A)" = A·g⁻¹. The entire security of DH rests on the
  multiplicative group's log being hard; moving to the additive group removes the
  hardness entirely. (The flag itself says it: "cyclic group under addition".)
- When a DH challenge names an unusual group ("additive", a matrix, a curve), the
  first question is always: what does "discrete log" mean in THAT group, and is it
  solvable there?

## What I did / did not do

- Connected once, read the three intercepted lines, computed, decrypted, submitted.
- Did not probe beyond the statement (no input channel exists).

## Limitations

None. Flag submitted and API-verified (score_delta > 0).

## Configuration

- Date: 2026-10-15 (UTC); host: Windows 11, git-bash; user OWNER.
- Interpreter: `~/tools/crypto-ctf/venv/Scripts/python.exe` (PyCryptodome).
- Working dir: `~\Practice_runs\cryptohack_org\challenge-124-cryptohack-dh_additive`.
- Network: `socket.cryptohack.org:13380` (1 connection, 3 lines), cryptohack.org (submit/API).
- Evidence: `solve.py`, `live_transcript_2026-10-15.txt`, `flag.txt`.
