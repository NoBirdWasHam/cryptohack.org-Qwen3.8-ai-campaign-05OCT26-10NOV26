# GLP420 (HackTM CTF 2023) — archive page facts

- Slug: glp420-hacktm_ctf2023 | Category: ctf-archive | Points: 0 | 33 solves
- Listener: `archive.cryptohack.org 26931`
- File: server.sage (downloaded as ./server.sage, 114 lines)

## Scheme (from server.sage)
- R_q = Z_q[x]/(x^420 - 1), q = 8383489, b = 16383, w = 3, n = 420
- keygen: s, e coefficients in {-1,0,1}; t = a*s + e
- sign(m): y1,y2 ~ [-b,b]; c = hash2poly(sha256(encode(a*y1+y2)+m));
  z1 = s*c+y1, z2 = e*c+y2; reject if any |z|_centered > b-w
- hash2poly: bits of the 256-bit sha256 digest → c[i] = bit i (so c deg <= 255, coeffs in {0,1})
- verify: bounds on z1,z2 (centered <= b-w) AND c == hash2poly(sha256(encode(a*z1+z2-t*c)+m))
- server: no signing oracle; prints a_enc, t_enc; asks z1,z2,c for m = b"sign me!"

## Attack (implemented in solve.py)
1. CVP in L = {M*s + q*v} (M = circulant of a, dim 420, det q^420, GH ~4.2e7)
   with target t. True error is e with ||e|| ~ 17 → gap ~2.4e6 → BKZ+Babai/CVP trivial.
2. s = (t - e) * a^{-1} in R_q via extended Euclid (x^420-1 squarefree, q prime).
3. Forge: y1=y2=0, c = hash2poly(sha256(encode(0)+m)); z1 = s*c, z2 = e*c.
   Then a*z1+z2-t*c = 0 → hash gives back c. |z| <= ~280 << 16380, bounds pass.
