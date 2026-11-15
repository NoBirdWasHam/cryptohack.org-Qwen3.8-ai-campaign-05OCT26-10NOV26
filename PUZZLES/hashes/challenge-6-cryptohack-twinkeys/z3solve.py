# z3solve.py — twinkeys: fastcoll find_block0 as bit-vector SAT, forcing W0..W4 + W5 low16 = prefix.
# Differential-path-as-equations framing per user-supplied refs (labeled in AAR as external knowledge):
# Biham-Shamir DCS (doi 10.1007/BF00630563), Dunkelman BlockCipherSeminar Lec2, theamazingking SDES DDT.
# All step/condition data is AUTO-PARSED from hashclash/src/md5fastcoll/block0.cpp (no manual transcription).
import sys, re, json, struct, os
import z3
from z3 import BitVec, BitVecVal, sat, RotateLeft, ZeroExt
ZE = lambda x: ZeroExt(32 - x.size(), x)
RotateRight = lambda x, n: RotateLeft(x, (32 - (n % 32)) % 32)

SRC = "hashclash/src/md5fastcoll/block0.cpp"
txt = open(SRC, "rb").read().decode("latin-1").replace("\x00", "")

u32 = lambda n: BitVecVal(n & 0xFFFFFFFF, 32)
IV = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]
FF = lambda b,c,d: d ^ (b & (c ^ d))
GG = lambda b,c,d: c ^ (d & (b ^ c))
HH = lambda b,c,d: b ^ c ^ d
II = lambda b,c,d: c ^ (b | ~d)

# ---- register DAG exactly as sampled in find_block0 (q_t = Q[Qoff+t]) ----
free = {}
def fr(name):
    v = BitVec(name, 32); free[name] = v; return v
q1  = fr('q1')
q3  = (fr('r3') & u32(0xfe87bc3f)) | u32(0x017841c0)
q4  = (fr('r4') & u32(0x44000033)) | u32(0x000002c0) | (q3 & u32(0x0287bc00))
q5  = u32(0x41ffffc8) | (q4 & u32(0x04000033))
q6  = u32(0xb84b82d6)
q7  = (fr('r7') & u32(0x68000084)) | u32(0x02401b43)
q8  = (fr('r8') & u32(0x2b8f6e04)) | u32(0x005090d3) | (~q7 & u32(0x40000000))
q9  = u32(0x20040068) | (q8 & u32(0x00020000)) | (~q8 & u32(0x40000000))
q10 = (fr('r10') & u32(0x40000000)) | u32(0x1040b089)
q11 = (fr('r11') & u32(0x10408008)) | u32(0x0fbb7f16) | (~q10 & u32(0x40000000))
q12 = (fr('r12') & u32(0x1ed9df7f)) | u32(0x00022080) | (~q11 & u32(0x40200000))
q13 = (fr('r13') & u32(0x5efb4f77)) | u32(0x20049008)
q14 = (fr('r14') & u32(0x1fff5f77)) | u32(0x0000a088) | (~q13 & u32(0x40000000))
q15 = (fr('r15') & u32(0x5efe7ff7)) | u32(0x80008000) | (~q14 & u32(0x00010000))
q16 = (fr('r16') & u32(0x1ffdffff)) | u32(0xa0000000) | (~q15 & u32(0x40020000))
q_1, q_2, q_3 = u32(IV[2]), u32(IV[3]), u32(IV[0])   # Q[Qoff-1]=Q[2]=IV[2], Q[1]=IV[3], Q[0]=IV[0]
q0  = u32(IV[1])

k4 = BitVec('k4', 5)    # counter2 index (0..15)
k3 = BitVec('k3', 4)    # counter3 index (0..7)
j4 = BitVec('j4', 16)   # counter4 index
s.add if False else None
CONDOK = os.environ.get("NOCOND","0") != "1"
S = z3.Solver()
from z3 import ULT
S.add(ULT(k4, 16), ULT(k3, 8))

# ---- block[] words from reverse-step equations (verbatim constants) ----
q17 = (fr('r17') & u32(0x3ffd7ff7)) | (q16 & u32(0xc0008008))
q17 = q17 ^ u32(0x40000000)
b0 = RotateRight(q1 - q0, 7) - FF(q0, q_1, q_2) - q_3 - u32(0xd76aa478)
b6 = RotateRight(q7 - q6, 17) - FF(q6, q5, q4) - q3 - u32(0xa8304613)
b7a = RotateRight(q8 - q7, 22) - FF(q7, q6, q5) - q4 - u32(0xfd469501)
b11 = RotateRight(q12 - q11, 22) - FF(q11, q10, q9) - q8 - u32(0x895cd7be)
b14 = RotateRight(q15 - q14, 17) - FF(q14, q13, q12) - q11 - u32(0xa679438e)
b15 = RotateRight(q16 - q15, 22) - FF(q15, q14, q13) - q12 - u32(0x49b40821)
tt1  = FF(q1, q0, q_1) + q_2 + u32(0xe8c7b756)
tt17 = GG(q16, q15, q14) + q13 + u32(0xf61e2562)
tt18 = q14 + u32(0xc040b340) + b6
tt19 = q15 + u32(0x265e5a51) + b11
tt20 = q16 + u32(0xe9b6c7aa) + b0
q18 = RotateLeft(GG(q17, q16, q15) + tt18, 9) + q17
if os.environ.get("NOCOND","0") != "1":
    if CONDOK: S.add(((q18 ^ q17) & u32(0xa0020000)) == u32(0x00020000))
q19 = RotateLeft(GG(q18, q17, q16) + tt19, 14) + q18
if CONDOK: S.add((q19 & u32(0x80020000)) == u32(0x80000000))
q20 = RotateLeft(GG(q19, q18, q17) + tt20, 20) + q19
if CONDOK: S.add(((q20 ^ q19) & u32(0x80040000)) == u32(0x00040000))
b1 = RotateRight(q17 - q16, 5) - tt17
q2 = RotateLeft(b1 + tt1, 12) + q1
b2 = RotateRight(q3 - q2, 17) - FF(q2, q1, q0) - q_1 - u32(0x242070db)

# counter2: q4 perturbation (mask expression from source)
q4mask = ((((ZE(k4)) << 2) ^ ((ZE(k4)) << 26)) & u32(0x38000004))
q4v = q4 ^ q4mask
b5 = RotateRight(q6 - q5, 12) - FF(q5, q4v, q3) - q2 - u32(0x4787c62a)
tt21 = GG(q20, q19, q18) + q17 + u32(0xd62f105d)
q21 = RotateLeft(tt21 + b5, 5) + q20
if CONDOK: S.add(((q21 ^ q20) & u32(0x80020000)) == u32(0))
b3 = RotateRight(q4v - q3, 22) - FF(q3, q2, q1) - q0 - u32(0xc1bdceee)
b4 = RotateRight(q5 - q4v, 7) - FF(q4v, q3, q2) - q1 - u32(0xf57c0faf)
b7 = RotateRight(q8 - q7, 22) - FF(q7, q6, q5) - q4v - u32(0xfd469501)
tt22 = GG(q21, q20, q19) + q18 + u32(0x02441453)
tt23 = q19 + u32(0xd8a1e681) + b15
tt24 = q20 + u32(0xe7d3fbc8) + b4
tt8  = FF(q8, q7, q6) + q5 + u32(0x698098d8)
tt9  = q6 + u32(0x8b44f7af)
tt10 = q7 + u32(0xffff5bb1)
tt12 = RotateRight(q13 - q12, 7) - u32(0x6b901122)
tt13 = RotateRight(q14 - q13, 12) - FF(q13, q12, q11) - u32(0xfd987193)

# counter3
m9mask = ((((ZE(k3)) << 13) ^ ((ZE(k3)) << 4)) & u32(0x2060))
q10v = q10 ^ (m9mask & u32(0x60))
q9v  = q9 ^ (m9mask & u32(0x2000))
m10 = RotateRight(q11 - q10v, 17) - FF(q10v, q9v, q8) - tt10
aa = q21
dd = RotateLeft(tt22 + m10, 9) + aa
if CONDOK: S.add((dd & u32(0x80000000)) == u32(0x80000000))
cc = tt23 + GG(dd, aa, q20)
if CONDOK: S.add((cc & u32(0x00020000)) == u32(0))
cc = RotateLeft(cc, 14) + dd
if CONDOK: S.add((cc & u32(0x80000000)) == u32(0))
bb = tt24 + GG(cc, dd, aa)
bb = RotateLeft(bb, 20) + cc
if CONDOK: S.add((bb & u32(0x80000000)) != u32(0))
b10 = m10
b13 = tt13 - q10v

# counter4
def q9mask_expr(j):
    x = 0
    for sh in (1,2,5,7,8,10,11,13):
        x = x ^ ((ZE(j) << sh))
    return x & u32(0x0eb94f16)
q9c = q9v ^ q9mask_expr(j4)
b12 = tt12 - FF(q12, q11, q10v) - q9c
b8  = RotateRight(q9c - q8, 7) - tt8
b9  = RotateRight(q10v - q9c, 12) - FF(q9c, q8, q7) - tt9

blocks = {0:b0,1:b1,2:b2,3:b3,4:b4,5:b5,6:b6,7:b7,8:b8,9:b9,10:b10,11:b11,12:b12,13:b13,14:b14,15:b15}

# ---- forward sweep steps 24..63, AUTO-PARSED from block0.cpp (verbatim order) ----
sweep = []   # (F, reg, wordidx, ac, rc) with conditions applied AFTER the step
steps = re.findall(r"MD5_STEP\((\w+),\s*(\w),\s*\w,\s*\w,\s*\w,\s*(?:block\[(\d+)\]|(m\w+)),\s*(0x[0-9a-fA-F]+),\s*(\d+)\);", txt)
conds = re.findall(r"if \(0 (!=|==) \(\((\w)\^(\w)\) (?:>> 31|& 0x80000000)\)\) continue;", txt)
# manual HH c-step with 0x8000 cond + rot16, and the special 'if (0 == (bb & 0x80000000)) continue' are
# already fixed above (cc/bb). For the sweep we need each MD5_STEP followed (optionally) by an if-line.
lines = txt.splitlines()
sweep_full = []
cur_regs = ['a','b','c','d']
i = 0
manual_c = None
while i < len(lines):
    L = lines[i].strip()
    m = re.match(r"MD5_STEP\((\w+),\s*([abcd]),\s*([abcd]),\s*([abcd]),\s*([abcd]),\s*(?:block\[(\d+)\]|(m\w+)),\s*(0x[0-9a-fA-F]+),\s*(\d+)\);", L)
    if m:
        f, reg = m.group(1), m.group(2)
        word = int(m.group(6)) if m.group(6) else None
        mv   = m.group(7)
        ac, rc = int(m.group(8),16), int(m.group(9))
        cond = None
        j = i+1
        nxt = lines[j].strip() if j < len(lines) else ""
        mc = re.match(r"if \(0 (!=|==) \(\((\w)\^(\w)\) >> 31\)\) continue;", nxt)
        if mc:
            cond = (mc.group(2), mc.group(3), mc.group(1))  # xor pair, != means must-equal-bits31
            i = j
        else:
            mc2 = re.match(r"if \(0 (!=|==) \(\((\w)\^(\w)\) & 0x80000000\)\) continue;", nxt)
            if mc2:
                cond = (mc2.group(2), mc2.group(3), mc2.group(1)); i = j
        sweep_full.append((f, reg, word, mv, ac, rc, cond, (m.group(3), m.group(4), m.group(5))))
    else:
        mc3 = re.match(r"c \+= HH\(d, a, b\) \+ block\[(\d+)\] \+ (0x[0-9a-fA-F]+);", L)
        if mc3:
            # next line: if (0 != (c & (1 << 15))) continue;  then: c = (c<<16 | c>>16) + d;
            cond = ('c15',)
            sweep_full.append(('HHc','c', int(mc3.group(1)), None, int(mc3.group(2),16), 16, cond, ('d','a','b')))
            i += 2
    i += 1
print(f"parsed {len(sweep_full)} sweep steps")

FUN = {'GG': GG, 'HH': HH, 'II': II, 'FF': FF}
regs = {'a': aa, 'b': bb, 'c': cc, 'd': dd}
for (f, reg, word, mv, ac, rc, cond, ordt) in sweep_full:
    b_, c_, d_ = ordt
    w = blocks[word] if word is not None else None
    if cond and cond[0] == 'c15':
        v = regs[reg] + HH(regs['d'], regs['a'], regs['b']) + w + u32(ac)
        if CONDOK: S.add((v & u32(0x8000)) == u32(0))
        regs[reg] = RotateLeft(v, 16) + regs['d']
        continue
    v = regs[reg] + FUN[f](regs[b_], regs[c_], regs[d_]) + w + u32(ac)
    v = RotateLeft(v, rc) + regs[b_]
    if cond and os.environ.get("NOCOND","0") != "1":
        x, y, op = cond
        eq = ((regs[x] ^ v) if y == reg else (regs[x] ^ regs[y])) if False else None
        # condition evaluated on UPDATED registers: reg just became new value
        newr = dict(regs); newr[reg] = v
        condexpr = (newr[x] ^ newr[y]) & u32(0x80000000)
        if op == '!=':   # 'if (0 != cond) continue' -> require cond == 0
            S.add(condexpr == 0)
        else:            # 'if (0 == cond) continue' -> require cond != 0
            S.add(condexpr != 0)
    regs[reg] = v

# IHV filter (stevens || wang) verbatim
IHV1 = regs['b'] + u32(IV[1]); IHV2 = regs['c'] + u32(IV[2]); IHV3 = regs['d'] + u32(IV[3])
wang = z3.And(((IHV2 ^ IHV1) & u32(0x86000000)) == u32(0x02000000),
              ((IHV1 ^ IHV3) & u32(0x82000000)) == 0,
              (IHV1 & u32(0x06000020)) == 0)
stevens = z3.And((IHV1 >> 31) == (IHV2 >> 31), (IHV1 >> 31) == (IHV3 >> 31),
                 (IHV3 & u32(1<<25)) == 0, (IHV2 & u32(1<<25)) == 0, (IHV1 & u32(1<<25)) == 0,
                 ((IHV2 ^ IHV1) & u32(1)) == 0)
if os.environ.get("NOIHV","0") != "1":
    S.add(z3.Or(wang, stevens))

# ---- THE FORCING: prefix words ----
import os
FORCE = os.environ.get("FORCE", "1")
KS = b"CryptoHack Secure Safe"
W = [int.from_bytes(KS[4*i:4*i+4], 'little') for i in range(5)]
if FORCE != "0":
    nf = int(FORCE) if FORCE.isdigit() else 6
    for i in range(min(nf, 5)):
        S.add(blocks[i] == W[i])
    if nf >= 6:
        S.add(blocks[5] & u32(0xFFFF) == u32(0x6566))

timeout = int(sys.argv[1]) if len(sys.argv) > 1 else 240000
S.set("timeout", timeout)
r = S.check()
print("SAT result:", r)
if r == sat:
    M = S.model()
    def gv(e):
        v = z3.simplify(M.eval(e, model_completion=True))
        assert z3.is_value(v), str(v)
        return v.as_long()
    bw = [gv(blocks[i]) for i in range(16)]
    regs_m = {n: gv(regs[n]) for n in 'abcd'}
    qnames = ['q1','q2','q3','q4v','q5','q7','q8','q9c','q10v','q11','q12','q13','q14','q15','q16','q17','q18','q19','q20','q21']
    qvals = {}
    for nm, qe in zip(qnames, [q1,q2,q3,q4v,q5,q7,q8,q9c,q10v,q11,q12,q13,q14,q15,q16,q17,q18,q19,q20,q21]):
        qvals[nm] = gv(qe)
    qvals['bb'], qvals['cc'], qvals['dd'] = regs_m['b'], regs_m['c'], regs_m['d']
    qvals['k4'] = gv(k4); qvals['k3'] = gv(k3); qvals['j4'] = gv(j4)
    json.dump({'q': qvals}, open("qvals_z3.json","w"))
    print("BLOCK0 =", [hex(x) for x in bw])
    json.dump(bw, open("block0_z3.json","w"))
    print("saved block0_z3.json")
