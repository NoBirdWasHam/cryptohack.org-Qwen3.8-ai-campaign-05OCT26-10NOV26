# AAR — noleaks (Misc 100) — SOLVED 2026-10-20 (+100)
Flag: [flag value withheld — real-flag strings live only under FLAGS/]

OTP with assert ct[i]!=flag[i] (otp byte != 0): each ct byte is uniform over 255 values
EXCLUDING flag[i]. Collect ~5500 ciphertexts (socket loop, ~9min); per position the byte that
NEVER appears = flag byte. Decoys average ~21 hits; P(decoy never appears) ~ 3e-9.
## Vulnerability (plain words)
An OTP whose code asserts `ct[i] != flag[i]`: the key byte is never allowed to be 0 (key 0 would output the flag byte), which deletes exactly one ciphertext value per position — the flag byte itself. Each ciphertext byte is then uniform over the 255 values *excluding* flag[i]. Re-encrypting the same fixed plaintext under fresh keys turns the anti-leak assert into a membership oracle, and exhaustion finishes the message.

## How the answer follows
1. Collect ~5500 ciphertexts of the same plaintext (socket loop, ~9 min, `collect.py`).
2. Per position, find the byte value that never appeared. The flag byte never appears *by construction*; every decoy byte appears ~ N/255 ~ 21.5 times on average (observed average ~21 hits), so P(some decoy stays unseen) = (254/255)^5500 ~ 3e-9 — across 255 decoys/position the chance of a wrong "never seen" byte is negligible, and empirically every position had a unique missing byte.
3. Concatenate the never-observed bytes -> flag `[flag value withheld — real-flag strings live only under FLAGS/]` (+100, 2026-10-20), server-confirmed.

## Limitations / attempts that failed
- Nothing recorded as failed in run logs; the collect-and-exclude route was executed in one pass. (Sample-size tuning beyond the ~5500 collected is not recorded.)

## Sources
Own collection scripts/logs `collect.py`, `collect.log`, `cts.json`; coupon-collector probability (standard). No writeups consulted.
