from velu_engine import *
p = 419
E = make_ec(p, 1, 0)
js = [j_short(1, 0, p)]
models = [(1, 0)]
for i in range(27):
    pts = find_order_l_points(E, 3)
    P = pts[0]
    K = [E["mul"](P, k) for k in range(1, 3)]
    xmap = velu_xmap(E, K)
    a1, b1 = reconstruct_codomain(E, K, xmap, 3)
    E = make_ec(p, a1, b1)
    js.append(j_short(a1, b1, p))
    models.append((a1, b1))
    if (a1, b1) == (1, 0):
        print(f"MODEL-LEVEL return to E0 at step {i+1}")
        break
print("j-seq: ", js)
print("first class-return (j=52) at step:", next((d for d in range(1, len(js)) if js[d] == 52), None))
