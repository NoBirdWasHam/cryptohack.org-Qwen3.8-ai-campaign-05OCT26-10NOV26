# Unbalanced RSA small-d floor (unbalanced-icc_athens2022 case study)

Regime: N 1024-bit, p=N^{1/4}, d≈N^{0.293} prime, e=d^{-1} mod phi, offline.

Dead ends (all measured on real+synthetic, do not re-attempt expecting different results):
- Wiener/Dujella extended-Wiener: gap k(p+q)/N ≈ 2^{45}.
- BD (p+q poly): s≈N^{0.75} ≫ N^{0.5}.
- (k,p) mod-e shifted-power lattices (any region/m/BKZ/MSB-windows): min scaled norm PINNED at
  e^m·(1+eps) (the e^m·1 vector, Y-independent), which is 1.5-3 bits BELOW HG bound but its value
  is e^m·(±1) — never vanishing. Vanishing vectors only exist ~300 bits above bound.
- (e·p)^m bonus divisibility (G(k,p)=p·e·d exactly; known multiple e·N): unusable because A(w)=2w(N-P)
  middle coefficients create u^{m-1}-shadows ≈2^{1808m-469} > (ep)^m bound 2^{1277m} for all m≥1.
- Pure f^m lattices: (1,1)^m shadow 2^{1024m+600m} > 810m LM.

Lesson: with root box X·Y ≈ 2^{1024+} and coefficient structure 2^{1024}-middle-coeffs, the
vanishing-norm floor ≈ 2^{1024}·(X Y)/(root product) pins margin at −2.5..−3; the author's
'0.292+unbalanced' defense is sound for these families. Official solution likely uses extra
structure (2 listed solutions not read per provenance rule). Check literature on e·p-divisibility
(Herrmann-May unravelled linearization refinements) before retrying.
