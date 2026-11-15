"""Extract p from vanishing polys via msolve, then decrypt flag."""
import pickle, subprocess, re, sys, os
from Crypto.Util.number import long_to_bytes

MSOLVE = r"~\tools\msolvedir\ucrt64\bin\msolve.exe"


def poly_to_msolve(poly):
    terms = []
    for (a, b, cc), v in sorted(poly.items(), key=lambda kv: (-sum(kv[0]), kv[0])):
        if v == 0:
            continue
        mon = ""
        for deg, name in ((a, "x"), (b, "y"), (cc, "z")):
            if deg == 1:
                mon += "*" + name
            elif deg > 1:
                mon += f"*{name}^{deg}"
        term = str(v) + mon if mon else str(v)
        terms.append(term)
    return "+".join(terms).replace("+-", "-")


def run_msolve(polys, nvars_order=("x", "y", "z"), threads=8, timeout=1800):
    inp = "\n".join(nvars_order) + "\n0\n" + ",\n".join(polys) + "\n"
    with open("ms.in", "w") as f:
        f.write(inp)
    r = subprocess.run([MSOLVE, "-f", "ms.in", "-t", str(threads)],
                       capture_output=True, text=True, timeout=timeout)
    return r.stdout


def parse_points(out):
    """out like [0, [[ [a,b],[c,d],[e,f] ], ...]]: each [lo,hi] exact."""
    out = out.strip().rstrip(":")
    data = eval(out)  # literal list of ints/lists only
    if data[0] == -1:
        return []
    if data[0] == 1:
        raise RuntimeError("infinitely many solutions: " + out[:200])
    pts = []
    for pt in data[1]:
        coords = []
        for iv in pt:
            lo, hi = iv
            assert lo == hi, f"non-exact interval {iv}"
            coords.append(lo)
        pts.append(coords)
    return pts


def main():
    d = pickle.load(open("selected.pkl", "rb"))
    sel, N, e, c = d["sel"], d["N"], d["e"], d["c"]
    tried = []
    for nsel in (3, 2, 4, 5, 6, 1):
        if nsel > len(sel):
            continue
        polys = [poly_to_msolve(h) for h in sel[:nsel]]
        polys.append("y*z - " + str(N))
        print(f"msolve with {nsel} vanishing polys...", flush=True)
        out = run_msolve(polys)
        print(out[:400], flush=True)
        try:
            pts = parse_points(out)
        except Exception as ex:
            print("parse fail:", ex)
            continue
        for pt in pts:
            for coord in pt:
                if isinstance(coord, int) and 2 < coord < N and N % coord == 0:
                    p = coord
                    q = N // p
                    from sympy import isprime
                    if isprime(p) and isprime(q):
                        phi = (p - 1) * (q - 1)
                        dd = pow(e, -1, phi)
                        msg = pow(c, dd, N)
                        flag = long_to_bytes(msg)
                        print("FOUND p =", p)
                        print("FLAG BYTES:", flag)
                        pickle.dump({"p": p, "q": q, "d": dd, "flag": flag},
                                    open("solution.pkl", "wb"))
                        return
        print(f"no good root with {nsel} polys ({len(pts)} points)", flush=True)
    print("FAILED to extract p")


if __name__ == "__main__":
    main()
