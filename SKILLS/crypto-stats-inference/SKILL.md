---
name: crypto-stats-inference
description: Use for GLRT/Fano CTF distinguishing and guessing bounds.
version: 1.0.0
author: GT
license: MIT
metadata:
  hermes:
    tags: [crypto, statistics, ctf]
    related_skills: [ctf-side-channels, ctf-crypto-attacks]
---

# Statistical inference for crypto CTFs (GLRT, Fano)

## When to Use
A challenge asks you to DISTINGUISH two distributions, decide a hidden bit from noisy observations, or
claims a task is information-theoretically impossible — or a side-channel needs a decision rule.

## Generalized likelihood ratio test (GLRT)
- Composite hypotheses (unknown nuisance params): plug in MLEs -> Lambda(x) = sup_{theta in H1} L / sup_{theta in H0} L,
  threshold it. Use when side-channel traces have unknown offset/scale but the keyed hypothesis changes the
  distribution SHAPE (Wikipedia 'Generalized likelihood ratio test' as quick reference).
- Calibration rule: ALWAYS threshold by simulation under H0 (empirical percentile), never by asymptotic
  chi-square, when n is small or noise non-Gaussian — cite the sim.

## Fano's inequality (impossibility + budgeting)
- If X -> Y (any estimator pipeline), P(error) >= (H(X) - I(X;Y) - 1) / log|X|. In plain CTF terms: if the
  observations carry fewer than k-1 bits about a k-bit secret, no compute closes the gap.
- Use in BOTH directions: to refuse brute force when leakage is provably short (write the bound in the AAR —
  it converts 'we failed' into 'the task as posed is unsolvable', which is a result), and to catch challenge
  authors' own over-shrunken noise (if their intended solver needs more bits than provided, hunt the extra
  leakage channel — it exists).

## Canonical references
[R21] Generalized likelihood ratio test. https://en.wikipedia.org/wiki/Generalized_likelihood_ratio_test
[R22] Fano's inequality. https://en.wikipedia.org/wiki/Fano%27s_inequality

## Verify
Any 'impossible by Fano' claim must show the entropy computation (source of H(X), the leakage model, I(X;Y)
estimate) — an unquantified impossibility claim is prose, not a result.

## Phase-style leakage (timing traces, D7 residual)
Clock-cycle/timing observations are CIRCULAR (wrap at the modulus): model phase error on the circle, not the
line — use von Mises (circular normal) or wrapped distributions; linear-Gaussian GLRT thresholds are biased
near the wrap point. Practical rule: unwrap only within a single hypothesis's cluster, or work with chord
distance |e^{iθ1} − e^{iθ2}|/2 in the likelihood.
