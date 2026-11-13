# Test if concat of R bytes looks like contiguous MT19937 output.
import ast
src = open('output.txt').read()
ns = {}
exec(src, ns)
R = ns['R']
blob = b''.join(x.to_bytes(128,'big') for x in R)
print('blob len', len(blob))

def untemper(y):
    y ^= y >> 11
    y ^= (y << 7) & 0x9d2c5680
    y ^= (y << 15) & 0xefc60000
    y ^= y >> 18
    return y & 0xffffffff

words = [int.from_bytes(blob[i:i+4],'big') for i in range(0, len(blob)-3)]
nw = len(words)
u = [untemper(w) for w in words]
# MT twist relation: x[i] = x[i-627] ^ ((msb(x[i-624])|lsb(x[i-623]))>>1...) standard:
# x[i] = x[i-627] ^ (((x[i-624] & 0x80000000) | (x[i-623] & 1)) >> 1) ^ (x[i-624+397] ^ MAG[(x[i-623]&1)])
MAG = [0, 0x9908b0df]
def check(align):
    # state positions 0..623 = u[align..align+623]; verify words 624..624+300
    good = 0
    for k in range(300):
        i = align + 624 + k
        x = u[align+k-627+0] if False else None
        a = u[align+k+397-624]      # x[i-627] -> index align+k-230... compute directly
        # indices: target x[t] with t=k(0-based state). x[t]=x[t-627]^ f(x[t-624],x[t-623])
        t = 624 + k
        p627 = align + t - 627; p624 = align + t - 624; p623 = align + t - 623
        if p627 < 0: return -1
        pred = u[p627] ^ (((u[p624] & 0x80000000) | (u[p623] & 1)) >> 1)
        if u[p623] & 1: pred ^= 0x9908b0df
        pred &= 0xffffffff
        if pred == u[i]: good += 1
        else: return good
    return good

best = (0, 0)
for align in range(0, len(blob)//4 - 624 - 300):
    g = check(align)
    if g > best[0]:
        best = (g, align)
        if g > 100:
            print('MATCH align', align, 'good', g); break
print('best', best)
