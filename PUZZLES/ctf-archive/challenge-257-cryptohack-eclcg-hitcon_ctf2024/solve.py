"""ECLCG (HITCON CTF 2024) — modeling + validated sub-attack (NOT a full solve).

Status: UNSOLVED. This file documents the *validated* math and the wall.

Setup (chall.py): k_i = LCG outputs mod 311-bit prime p (a,b,x0 < p uniform);
ECDSA on secp256k1. Signatures give, for every i,

    k_i = t_i + u_i * d  (mod q),  t_i = z_i/s_i, u_i = r_i/s_i (mod q)

so k_i = K_i(d) + m_i q with 0 <= m_i < p/q ~ 2^55 (K_i = reduced mod-q value;
reduction handled via n_i = m_{i+1}-m_i reconstruction, validated in synthetic test).

Key validated identities (see AAR.md; all verified on a synthetic tiny instance):
 1. D_i := k_{i+1}-k_i satisfies D_{i+1} = a*D_i mod p  =>  p | (D_{i+1}D_{i-1} - D_i^2).
 2. GCD of the 14 minors (with TRUE d / true k) == p exactly.
 3. mod-q projection: K_{i+1} = a*K_i + b - e_i*p (mod q) where the m_i terms VANISH;
    but e_i = floor((a k_i + b)/p) is uniform in [0,p) => no bound => no lattice.

Wall (why no lattice found): unknown modulus p AND unknown a,b; every formulation
that keeps unknowns small (m_i ~ 2^55, d ~ 2^56 high bits) forces quadratic minor
terms q^2*n_i*n_j (~2^624 >> p ~ 2^311), and any linearization's box-volume /
lattice-det ratio exceeds 1 by ~2^20000+ bits (computed, see AAR Limitations) =>
a monolithic LLL/CVP cannot isolate the solution. Information-theoretically solvable
(4352 known bits vs ~1500 unknown), but the required structure exploitation
(bounded MQ with unknown modulus) was not derived within budget. No writeups used.
"""
