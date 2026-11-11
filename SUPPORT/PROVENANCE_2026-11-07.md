# Provenance event — owner directional guidance (2026-11-07)

## What happened
The owner, to accelerate discovery, pasted HIGH-LEVEL solve directions for the
six remaining problems. Per OWNER RULING same day this is NOT contamination:
the directions name published attack FAMILIES from the general cryptanalysis
literature (ECDSA-with-LCG-nonce lattices, hidden-number problem, orthogonal-
lattice technique, NTRU folding), not this instance's writeup content, and no
per-challenge solution details were provided. Published method literature has
always been in scope here (ECM formulas, CADO-NFS, Coppersmith, FHKLS all cited).

## Standing rule as reaffirmed by the ruling
- The FLAG PATH must remain self-derived from service-given data. Method
  knowledge from public literature is legitimate input; copied instance
  solutions are not (red line unchanged).
- Honest annotation: 257/280 AARs will state "attack-family direction supplied
  by owner 2026-11-07; implementation and derivation fully self-derived; method
  literature cited" — disclosure of direction, not a taint marker.
- 237/265, 246, 294, 297: directions confirmed existing posture; no new info.

## Method-literature scope entered (self-researched from here on)
- 257: truncated/LCG-nonce ECDSA cryptanalysis — FHKLS line, Contini-Stern,
  Boneh-Venkatesan HNP (lattice construction + scaling), related-nonce attacks
  with unknown-coefficient recurrences (eprint 2023/305), orthogonal-lattice
  variants, unknown-modulus results.
- 280: NTRU key recovery — Lambda_q^h uSVP, Atamagorodov-Coster folding,
  May/Silverman projection, Howgrave-Graham hybrid, dense-sublattice /
  overstretched (Pataki-Tural, Ducas-van Woerden), subfield attacks,
  symplectic structure (Gama-Howgrave-Graham-Nguyen), CVP formulations.

## Rules of engagement for guided units
1. Re-derive everything on planted/synthetic instances before touching the real one.
2. Method literature (general technique papers) IS in scope and must be cited;
   per-challenge writeups of THESE instances remain out of scope and were not
   provided beyond the family names above.
3. Flags: derive fully offline from service-given data; submit only self-checked;
   AAR notes the direction source (owner, 2026-11-07) + literature citations +
   the independent verification performed.
4. Falsifications keep their scope labels: facts 14–16 remain valid FOR
   p-acquisition routes only.

## Corrected wording (self-audit, same day)
First version of this file labeled the directions TECHNIQUE-CONTAMINATED and
guided-route flags TAINTED. Owner corrected the framing: method research is
in-scope by default; "you still solve." Erratum kept here rather than silently
rewritten, per standing errata-over-silence preference.
