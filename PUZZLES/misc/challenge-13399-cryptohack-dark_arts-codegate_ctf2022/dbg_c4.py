import hashlib, random
import c4lib2 as C
G = C.g["Generator4"]()
p, q = G.p, G.q
n = 80
xs = list(range(1, n+1))
fs = [G.func_gen(x) for x in xs]
Kp, H = C.gp_cvp(p, q, xs, fs)
Kp_true = [sum(G.key[i]*H[j][i] for i in range(16)) % p for j in range(n)]
sol = C.gauss_mod_p([[H[j][i] for i in range(16)] for j in range(16)], Kp[:16], p)
print("key match:", sol == G.key)
d = [(Kp[j]-Kp_true[j]) % p for j in range(n)]
print("first 5 diffs mod p bit-lengths:", [x.bit_length() for x in d[:5]])
# true centered error between target and true point:
err = [ (fs[j]-q//2) - Kp_true[j] for j in range(n)]
print("true err bitlens:", [abs(x).bit_length() for x in err[:8]])
