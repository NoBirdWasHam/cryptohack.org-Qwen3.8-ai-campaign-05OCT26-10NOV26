# z3solve.py — twinkeys: encode fastcoll find_block0 as BV-SAT, force W0..W4 + W5 low16 = prefix.
# External technique refs (user-supplied, labeled in AAR): differential-path-as-equations framing
# (Biham-Shamir DCS; Dunkelman Lec2; theamazingking SDES DDT; Wikipedia differential cryptanalysis).
import sys, json
import z3
from z3 import BitVec, BitVecVal, BitVecSort, sat, RotateLeft, RotateRight, If, And, Or, Not, URem

u32 = lambda n: BitVecVal(n, 32)
IV = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]

AC = [0xd76aa478,0xe8c7b756,0x242070db,0xc1bdceee,0xf57c0faf,0x4787c62a,0xa8304613,0xfd469501,
0x698098d8,0x8b44f7af,0xffff5bb1,0x895cd7be,0x6b901122,0xfd987193,0xa679438e,0x49b40821,
0xf61e2562,0xc040b340,0x265e5a51,0xe9b6c7aa,0xd62f105d,0x02441453,0xd8a1e681,0xe7d3fbc0,
0x21e1cde6,0xc33707d6,0xf4d50d87,0x455a14ed,0xa9e3e905,0xfcefa3f8,0x676f02d9,0x8d2a4c8a,
0xfffa3942,0x8771f681,0x6d9d6122,0xfde5380c,0xa4beea44,0x4bdecfa9,0xf6bb4b60,0xbebfbc70,
0x289b7ec6,0xeaa127fa,0xd4ef3085,0x04881d05,0xd9d4d039,0xe6db99e5,0x1fa27cf8,0xc4ac5665,
0xf4292244,0x432aff97,0xab9423a7,0xfc93a039,0x655b59c3,0x8f0ccc92,0xffeff47d,0x85845dd1,
0x6fa87e4f,0xfe2ce6e0,0xa3014314,0x4e0811a1,0xf7537e82,0xbd3af235,0x2ad7d2bb,0xeb86d391]
SH = [7,12,17,22]*4 + [5,9,14,20]*4 + [4,11,16,23]*4 + [6,10,15,21]*4

FF = lambda b,c,d: d ^ (b & (c ^ d))
GG = lambda b,c,d: c ^ (d & (b ^ c))
HH = lambda b,c,d: b ^ c ^ d
II = lambda b,c,d: c ^ (b | ~d)

# ---- sampled registers (Qoff-shifted names R_t == Q[Qoff+t]) ----
r1  = BitVec('r1', 32)
r3  = BitVec('r3', 32)
r7  = BitVec('r7', 32)
r8  = BitVec('r8', 32)
r10 = BitVec('r10', 32)
r11 = BitVec('r11', 32)
r12 = BitVec('r12', 32)
r13 = BitVec('r13', 32)
r14 = BitVec('r14', 32)
r15 = BitVec('r15', 32)
r16 = BitVec('r16', 32)
r17 = BitVec('r17', 32)
k4  = BitVec('k4', 4)    # counter2 index
k3  = BitVec('k3', 3)    # counter3 index
j4  = BitVec('j4', 16)   # counter4 index

R0, Rm1, Rm2 = u32(IV[3]), u32(IV[2]), u32(IV[1])  # Q[Qoff-1]=Q[2]=IV[2]? careful below
# Q[] raw array: Q0=IV0,Q1=IV3,Q2=IV2,Q3=IV1 ; R_t = Q[3+t]
Q = {}
Q[0]=u32(IV[0]); Q[1]=u32(IV[3]); Q[2]=u32(IV[2]); Q[3]=u32(IV[1])
R = lambda t: Q[3+t]

R[4]  = None
Q[4]  = (r3 & u32(0xfe87bc3f)) | u32(0x017841c0)          # q3 (r3 reused below for q1? no) -- names:
# NOTE: sampling lines verbatim from find_block0:
Q[4]  = (r3 & u32(0xfe87bc3f)) | u32(0x017841c0)          # Q[Qoff+3]
Q[5]  = (r7 & u32(0x44000033)) | u32(0x000002c0) | (Q[4] & u32(0x0287bc00))   # q4 (r7=rng4)
Q[6]  = u32(0x41ffffc8) | (Q[5] & u32(0x04000033))         # q5
Q[7]  = u32(0xb84b82d6)                                     # q6 const
Q[8]  = (r8 & u32(0x68000084)) | u32(0x02401b43)            # q7  (r8=rng7)
Q[9]  = (j4 & u32(0) if False else Q[9]) if False else None
rng8 = BitVec('rng8',32)
Q[9]  = (rng8 & u32(0x2b8f6e04)) | u32(0x005090d3) | (~Q[8] & u32(0x40000000))  # q8
Q[10] = u32(0x20040068) | (Q[9] & u32(0x00020000)) | (~Q[9] & u32(0x40000000))  # q9 (derived)
Q[11] = (r10 & u32(0x40000000)) | u32(0x1040b089)          # q10 (r10=rng10)
Q[12] = (r11 & u32(0x10408008)) | u32(0x0fbb7f16) | (~Q[11] & u32(0x40000000))  # q11
Q[13] = (r12 & u32(0x1ed9df7f)) | u32(0x00022080) | (~Q[12] & u32(0x40200000))  # q12
Q[14] = (r13 & u32(0x5efb4f77)) | u32(0x20049008)          # q13
Q[15] = (r14 & u32(0x1fff5f77)) | u32(0x0000a088) | (~Q[14] & u32(0x40000000))  # q14
Q[16] = (r15 & u32(0x5efe7ff7)) | u32(0x80008000) | (~Q[15] & u32(0x00010000))  # q15
Q[17] = (r16 & u32(0x1ffdffff)) | u32(0xa0000000) | (~Q[16] & u32(0x40020000))  # q16
Q[1]  = r1 if False else Q[1]
rng1 = BitVec('rng1',32)
Q[4+0]  # noop
Q[Qoff1:=4]
Q[4]
# Q[Qoff+1]:
Q[4-0]
# The code: Q[Qoff + 1] = xrng64();  -> Q[4]?? NO: Qoff=3 -> Q[Qoff+1]=Q[4]!!! 
# CAREFUL: Q[Qoff+1] = Q[4]! But sampling line order in code:
#   Q[Qoff+1]=xrng ; Q[Qoff+3]=... ; Q[Qoff+4]=... ; ... 
# So Q[Qoff+1] = Q[4] was overwritten?? code samples q1 = Q[4]?? RE-READ: their lines:
#   Q[Qoff + 1] = xrng64();
#   Q[Qoff + 3] = (xrng64() & 0xfe87bc3f) | 0x017841c0;
#   Q[Qoff + 4] = (xrng64() & 0x44000033) ...
# So "q1"=Q[4]?? and "q3"=Q[6]?? -- NO: Qoff+3 = Q[6]. REDO mapping: R_t := Q[3+t] was WRONG.
print("MAPPING CHECK: Qoff=3; Q[Qoff+1]=Q[4] is q1; Q[Qoff+3]=Q[6] q3; Q[Qoff+16]=Q[19] q16")
sys.exit(3)
