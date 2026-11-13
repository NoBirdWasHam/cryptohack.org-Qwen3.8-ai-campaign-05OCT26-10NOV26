# AAR — smithing_contest-ecsc_2024_it (SOLVED)

flag: [flag — recorded in FLAGS/ctf-archive/challenge-293-cryptohack-smithing_contest-ecsc_2024_it/flag.txt]  (service-derived, live listener archive.cryptohack.org:25469; submitted ok:true, solved count 285→286)

## The scheme
IBE-style Boneh–Boyen signatures over a random 128-bit-bit BN curve (k=12, p=36u⁴−36u³+24u²−6u+1, u=1605213242,
b=11, twist E′: y²=x³+11/eps over Fp2, a²=−a+1 model, Fp12=Fp2[z]/(z⁶−eps)). PKG secrets s,u public:
P_G1=u·G1, P_G2=u·G2, Q=s·P_G1. User key: (s·Qid, s⁻¹·Qid), Qid=H0(uid) in G2-subgroup via cofactor hash.
Goal: convince **admin** verifier of a signature by 'admin' on a fixed target message — we only get a key for
our own non-admin username.

## The vulnerability
The interactive blinded verification (verifier sends C=x·y·R for secret x,y; "signer" replies t,r) is
**existentially forgeable for any (R,S) by anyone**: both check equations

  (0) e(R,S)^x = e(Q,Qid)^(x) · r^(H(m)·y⁻¹)
  (1) r^(y⁻¹) · t^x · e(P_G1,Qid)^x = e(R+Q,P_G2)^x

are satisfied by publicly-computable pairings once we choose R and S with matching pairing-profiles.
The two-round blinding stops a cheating *signer*, not a forger who never needs the secret key.
(Not an implementation bug in the pairing/PKG — those are fine, as the header claims.)

## The forgery (no s, no u, no dlog)
- R := Q ; S := H(m)·G2 + Qid_admin ⇒ e(R,S) = e(Q,Qid)·e(Q,G2)^{H(m)}
- r := e(C,G2) ⇒ r^{y⁻¹} = e(Q,G2)^x, and r^{H(m)y⁻¹} matches the extra factor in eq(0).
- t := e(Q,(2u−1)G2)/e(P_G1,Qid_ad) = e(2Q,P_G2)·e(Q,G2)⁻¹·e(P_G1,Qid)⁻¹ — note (2u−1)G2 = 2·P_G2−G2 is PUBLIC.
  Then eq(1): e(Q,G2)^x · [e(2Q,P_G2)/(e(Q,G2)e(P_G1,Qid))]^x · e(P_G1,Qid)^x = e(2Q,P_G2)^x ✓.
- t,r ∈ μ_n, ≠1 ⇒ pass server guards t^n=r^n=1.
Server accepts ⇒ prints flag for (True,'admin',target).

## Hard part: pure-Python clone of Sage's ate pairing (tower.py)
Server runs Sage `ate_pairing`; the forgery requires **exact** pairing agreement (a c-twisted clone e^c would
still pass all bilinearity tests but break eq(1)). Validated by: (a) Sage source `ell_point.py` —
`ate_pairing` = `Q._miller_(P, t−1)` then ^((q^k−1)/n); `_miller_` doubles the *argument*, processes all bits
below the top bit, t²·ℓ_ tangent/ℓ_ vertical — matches tower.miller orientation; (b) ground-truth: n·G=O, H2
(#E′(Fp2)/n, order-6 twist trace (t²−2p+√(3(4p²−(t²−2p)²)))/2) giving n-torsion cofactor hashes;
(c) live identity e(P_G1,du0)==e(Q,Qid_me) using the server's real du0 — this pins tower basis, H2, and H0
root-choice in one shot (passed with the min-y root, no flip needed).

## Glue bugs found (all caught, per "fuzz intermediates" rule)
1. `f12_powp` crash: `frob_setup()` never called before `ate()` (MBASE=None) → moved into discover().
2. **H(m) width**: PKG.H uses `digest()[:curve.bytes]` with bytes=ceil(128/8)=**16**, not the full 32-byte
   digest (old comment claimed "bytes=33"). Wrong Hm only corrupts eq(0) — silent 'oh noes' trap.
3. Server I/O: Sage `input()` prompts have no newline → prompts coalesce with the `C = [...]` reply into one
   line; must regex-search for `C = ` and for the verdict/flag inside accumulated lines.

## Key numbers
p=239019556058548081539763731767358519973, t=6u²+1=15460257313752903387? (printed in tower), n=p+1−t prime,
H2=#E′(Fp2)/n≈2.4e38 (exact int in tower.py, validated by n-torsion of H2·X for random lifts).

## Files
- tower.py — Fp2/Fp6/Fp12 tower + E(Fp),E(Fp2) EC ops + H0/Hm + exact-clone ate pairing (selftest `python3 tower.py`, EXIT=0)
- forge.py — end-to-end live forgery (run: `python3 forge.py`; log forge3.log ends with FLAG)
- scratch_ell_point.py — Sage ell_point.py source fetched to pin ate_pairing/_miller_ semantics (academic reference: SageMath source, sagemath/sage repo)

## Limitations / dead ends
- Earlier files attack.py/attacker.py/atk_run.py/fp2solve*.py/elim.py/identify.py/toy*.py explored
  extracting u or s via Fp2 dlog/tower identification (fp2solve*, identify, elim) — abandoned as ~2^64+ work
  once the key-free forge was seen; they are not needed.
- H0 root-choice ambiguity vs Sage `lift_x` was calibrated live (min-root matched; flip fallback coded but unused).
- Could not distinguish pairing e from e^c by any local test (bilinearity is c-invariant) — the decisive
  check was the live e(P_G1,du0)==e(Q,Qid_me) identity + final accepted verification.

## Vulnerability (plain words)
An IBE-style Boneh–Boyen signature whose interactive "blinded" verification (verifier sends C = x·y·R with secret x,y; "signer" replies t,r) is existentially forgeable by anyone, for any (R,S). Plain words for the pairing-identity collapse: the two check equations demand nothing more than *products of a handful of public pairing values, all raised to the same hidden exponent x*. Blinding hides the verifier's exponents from a cheating signer — it does nothing against a forger who never needs the secret key. Bilinearity turns "raise the pairing to a power" into "add points in the input slot", so the forger *constructs* the right exponents by adding points: choose S := H(m)·G2 + Qid_admin and R := Q, then e(R,S) is *exactly* e(Q,Qid)·e(Q,G2)^{H(m)}. Then r is defined BY the verifier as e(C,G2) = e(xy·Q,G2), so the forger gets r^{y⁻¹} = e(x·Q,G2) = e(Q,G2)^x for free — the verifier's own hidden y cancels in its own definition of r, and the surviving x-powers appear on BOTH sides of equation (1). What remains is bookkeeping among public μ_n values: t = e(2Q,P_G2)·e(Q,G2)⁻¹·e(P_G1,Qid_ad)⁻¹, and (2u−1)G2 = 2P_G2 − G2 is public, so both t and r are computable with no s, no u, no discrete log, and no signing oracle. The two-round protocol stops a cheating *signer*, not a forger.

## How the answer follows
1. Read the scheme from the provided source: PKG secrets published only as group elements P_G1=u·G1, P_G2=u·G2, Q=s·P_G1; we hold a key for our own non-admin uid; goal is the admin verifier on a fixed message.
2. Set R=Q, S=H(m)G2+Qid_ad, r=e(C,G2), t as above — every term from public data plus the verifier's own C ⇒ eq(0) and eq(1) both hold as identities; t,r ∈ μ_n\{1} pass the server guards.
3. Server pairing is Sage's ate pairing and a c-twisted clone e^c passes every local bilinearity test, so the forge needed an EXACT pairing clone: tower.py builds Fp2/Fp6/Fp12 (a²=−a+1, z⁶−eps over the random 128-bit BN curve, u=1605213242) with _miller_/ate orientation pinned from SageMath's own ell_point.py semantics.
4. Ground-truth pinning: n·G=O; H2=#E′(Fp2)/n with twist trace (t²−2p+√(3(4p²−(t²−2p)²)))/2; decisive live identity e(P_G1,du0)==e(Q,Qid_me) locked tower basis, H2 and the H0 root choice in one shot.
5. Live: forge.py sends the forged (R,S,t,r) → verdict (True,'admin',target) → flag printed (forge3.log); submitted ok:true.

## Limitations / attempts that failed
- First attack family tried to extract u or s via Fp2 dlog / tower identification (attack.py, fp2solve*, identify.py, elim.py) — ~2^64+ work, abandoned once the key-free forge was seen; kept on disk, unused.
- Glue bugs found by fuzzing intermediates: frob_setup() never called before ate(); H(m) truncated to 16 bytes (`digest()[:curve.bytes]`, bytes=ceil(128/8)) — a wrong Hm corrupts only eq(0), a silent trap; Sage input() prompts lack newlines so replies coalesce — regex parsing of `C = ` and the verdict.
- e vs e^c is locally indistinguishable by any bilinearity test; the decisive check was the live identity + the accepted verification. H0 root-choice calibrated live (min-root matched; flip fallback coded, unused).

## Sources
Challenge-provided scheme source + live listener (archive.cryptohack.org:25469). Academic reference named by the original AAR: SageMath source `ell_point.py` (sagemath/sage repo) fetched to pin ate_pairing/_miller_ semantics — a math/library reference, not a challenge writeup. Pairing/tower arithmetic from standard pairing literature. No third-party writeups consulted; flag handed by the live service after our own forgery was accepted.
