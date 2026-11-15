import gzip
with gzip.open("M_lll.txt.gz", "rt") as fin, open("real.fplll", "w") as fo:
    fo.write("[")
    for line in fin:
        toks = line.split()
        fo.write("[ " + " ".join(toks) + " ]")
    fo.write(" ]\n")
print("done", sum(1 for _ in open("real.fplll")))
