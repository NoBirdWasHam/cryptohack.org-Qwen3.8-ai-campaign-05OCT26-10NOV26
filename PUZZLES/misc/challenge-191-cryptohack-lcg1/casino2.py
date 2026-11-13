# lcg1 lo-hi casino — full solution.
import socket, json, re

HOST, PORT = "socket.cryptohack.org", 13383
VALUES = ['Ace','Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten','Jack','Queen','King']
SUITS = ['Clubs','Hearts','Diamonds','Spades']
M = 2**61 - 1

def digits_ms(n):
    d = []
    while n >= 52:
        d.append(n % 52); n //= 52
    d.append(n)
    return d[::-1]

def from_ms(ds):
    n = 0
    for d in ds: n = n * 52 + d
    return n

def blind_choice(v):                 # v = hand value 0..12
    return "higher" if (15 - 3*(v+1)) >= (3*(v+1) - 27) else "lower"

def run_once(verbose=False):
    sock = socket.create_connection((HOST, PORT), timeout=30)
    f = sock.makefile("rwb")
    def rjson():
        while True:
            line = f.readline()
            if not line: raise EOFError()
            s = line.decode().strip()
            if not s: continue
            try: return json.loads(s)
            except Exception: continue
    def send(obj):
        sock.sendall((json.dumps(obj) + "\n").encode())
        return rjson()

    states = []
    cur = []
    mul = inc = None
    pending = None; pi = 0

    r = rjson()   # server sends round 1 immediately on connect; do NOT send {}
    m = re.match(r"(\w+) of (\w+)", r["hand"])
    first = SUITS.index(m.group(2)) * 13 + VALUES.index(m.group(1))
    cur.append(first % 52)

    msg = ""
    for rnd in range(200):   # 200th choice triggers the round==200 flag check
        m = re.match(r"(\w+) of (\w+)", r["hand"])
        hv = (SUITS.index(m.group(2)) * 13 + VALUES.index(m.group(1))) % 13
        if pending is not None and pi < len(pending):
            pv = pending[pi] % 13
            choice = "higher" if pv > hv else ("lower" if pv < hv else "higher")
        else:
            choice = blind_choice(hv)
        pi += 1
        r = send({"choice": choice})
        msg = r.get("msg", "")
        mm = re.search(r"card was (\w+) of (\w+)", msg)
        if not mm:
            if "flag" in msg:
                open("flag_lcg1.txt","w").write(msg)
                print("FLAG:", msg); sock.close(); return msg
            print("odd resp:", str(r)[:120]); continue
        hid = SUITS.index(mm.group(2)) * 13 + VALUES.index(mm.group(1))
        notice = re.search(r"reshuffle the deck after (\d+) rounds", msg)
        if notice:
            # the notice fires WITH the last digit of the old state; new state starts next round
            cur.append(hid % 52)
            states.append(from_ms(cur))
            cur = []
            if len(states) >= 3 and mul is None:
                s1, s2, s3 = states[-3], states[-2], states[-1]
                try:
                    mul = (s3 - s2) * pow((s2 - s1) % M, -1, M) % M
                    inc = (s2 - mul * s1) % M
                    if verbose: print(f"[{rnd}] recovered mul/inc after {len(states)} states")
                except ValueError:
                    pass
            if mul is not None:
                pending = digits_ms((mul * states[-1] + inc) % M); pi = 0
        else:
            cur.append(hid % 52)
        if r.get("$", 99) <= 3:
            if verbose: print("bailing $", r.get("$"), "rnd", rnd)
            sock.close(); return None
    sock.close()
    if verbose: print("end $", r.get("$"), "|", msg[:90])
    return msg if "flag" in msg else None

for attempt in range(12):
    try:
        res = run_once(verbose=(attempt == 0))
        if res and "flag" in res:
            print("DONE:", res); break
        print("attempt", attempt, "no flag")
    except Exception as ex:
        print("attempt", attempt, "err:", str(ex)[:100])
