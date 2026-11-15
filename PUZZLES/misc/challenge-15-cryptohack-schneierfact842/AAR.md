# AAR — schneierfact842 (Misc 100) — SOLVED 2026-10-20 (+100)
Flag: [flag value withheld — real-flag strings live only under FLAGS/]

check(): password \w* with digit+upper+lower; np.array(ord).sum() AND .prod() must be prime.
Prod of >=2 codes >1 is composite UNLESS int64 overflow (server = 64-bit Linux numpy).
Emulate: prod mod 2^64 signed. Random search L=12..20, prime sum (~1/7) AND prime wrapped prod
(~1/44): ~1/300 hit rate. PITFALL: Windows numpy defaults to int32 — emulate int64 explicitly.
First candidate mK9uYOE7y9ymA -> flag.
## Vulnerability (plain words)
The server accepts a password when the sum *and* the product of its character codes are prime — both computed with 64-bit numpy. A product of >= 2 integers > 1 can never be prime mathematically, but int64 multiplication silently wraps modulo 2^64, and the wrapped residue *can* be prime. Integer overflow turns an impossible check into a ~1/44 probabilistic one.

## How the answer follows
1. Mirror the server's arithmetic exactly: the product check is the signed int64 residue of prod(ord(c)) mod 2^64 (server = 64-bit Linux numpy); the sum check is exact and prime with probability ~1/7.
2. Random search over passwords of length 12..20 satisfying the class rule (digit+upper+lower): joint hit rate ~ 1/7 * 1/44 ~ 1/300 — a few thousand candidates suffice; first passing candidate `mK9uYOE7y9ymA` was submitted.
3. The service hands over the flag on a passing password: `[flag value withheld — real-flag strings live only under FLAGS/]` (+100, 2026-10-20) — flag provenance is the listener, not retrieval.

## Limitations / attempts that failed
- Local primality checks disagreed until the int32-vs-int64 pitfall was caught: Windows numpy defaults to int32, so early local emulation wrapped the product at the wrong width; fixed by explicit int64 (signed mod 2^64) emulation.
- No other failed attempts recorded in run logs.

## Sources
Own search scripts `find_pw.py` / `find_pw2.py`; numpy integer-wrap semantics (documented two's-complement wrap). No writeups consulted.
