# Collision / birthday HUNT diagnostics

Use when a collision hunt reports many hits but zero verified finds, and always BEFORE launching a multi-hour walk.

## Diagnostic ladder
1. Small-scale harness FIRST: reduce the match width (e.g. capacity match 3-4 bytes) so real collisions arrive in seconds, plant a KNOWN pair, and run the full detect -> harvest -> verify pipeline end-to-end. Planted pairs discarded = code bug, not bad luck; never size the big-hunt fix until the toy harness passes.
2. Many hits / zero fires: if the table keys are EXACT (full target slice, no fuzzy compare), false-positive different-m hits are impossible by construction — the hits are same-state re-encounters or the collision model is wrong. Zero fires is math, not misfortune; do not extend the run hoping.
3. Plateau detector: distinct distinguished-point keys = insertions - hits. Flat across progress means the walk stopped covering new states. Instrument a debug walker with hit-reason counters (self / same-m / different-m) to attribute hits directly.
4. Generator/verifier byte parity: serialization between the C walker and the Python harvest must be byte-identical (endianness!). Prove it on ONE sample message against the reference hash; a mismatch kills real finds at harvest even when detection is perfect.

## Walk-validity rules
- Rho walks close cycles at ~sqrt(|state space|): folding/truncating the walk state into a space SMALLER than the target set (e.g. folding an 80-bit capacity into a 64-bit register) closes cycles at ~2^32 and merges parallel walks onto shared cycles — coverage plateaus while steps keep counting.
- Distinguished-point / VOW schemes are valid only when the sample space is at least as large as the target set; sampling a smaller space turns every hit into a self-revisit.
- The steps metric must measure unique coverage (distinct DP keys or first-revisit count). Compute P(collision | true coverage), never P | raw steps: a plateaued walk at 2.5e10 coverage against a 2^40 birthday target sits at P ~ 2.6e-4 no matter how many 'ETA-percent' it logs.

## Revised cost after any fix
Birthday success P = 1 - exp(-k^2 / 2^(w+1)) for target width w. Budget wall-time from throughput measured at the FINAL thread budget allowed on the host, not from peak-core benchmarks.
