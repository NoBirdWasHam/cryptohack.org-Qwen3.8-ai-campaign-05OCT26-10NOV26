exec(open("selftest.py").read().split("# run guess loop")[0])
s1true = 0
for j, bit in enumerate(kbits[19:46]):
    if bit: s1true += (1 << j)
bad = 0
for i in range(N):
    if b0[i]:
        v = bin(r1[i] & s1true).count("1") % 2
        if v != b1[i]: bad += 1
print("true-state eq violations:", bad, "of", sum(b0))
st = [1] + [0]*26
out = sim([27,26,25,22], st, 10)
mask = 1
rows = [bin(r1[i] & mask).count("1") % 2 for i in range(10)]
print("sim:", out)
print("row:", rows)
