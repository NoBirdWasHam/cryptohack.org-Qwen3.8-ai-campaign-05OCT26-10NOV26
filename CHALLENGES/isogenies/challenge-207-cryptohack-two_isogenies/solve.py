# Independent cross-check (rational j formula) of the PARI result.
p = 2**18*3**13-1
A = 11
B2 = -196          # (14i)^2 = 196 * i^2 = -196, i^2 = -1
j = (6912*A**3) // (4*A**3 + 27*B2)
assert j == 287496
print("j(E') =", j)
# non-singularity
assert -16*(4*A**3 + 27*B2) != 0
print("discriminant nonzero: OK  ->  flag: 287496 (bare)")
