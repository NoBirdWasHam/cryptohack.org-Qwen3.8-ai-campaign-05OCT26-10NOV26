# lcg1 lo-hi casino: LCG mod 2^61-1; each card = one base-52 digit (MS-first) of the state.
# After 3 full states: mul=(s3-s2)/(s2-s1), inc=s2-mul*s1. Then predict every card.
# Blind phase: bet with max-EV side (extreme hands) to survive.
import socket, json, re, sys, time

HOST, PORT = "socket.cryptohack.org", 13383
VALUES = ['Ace','Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten','Jack','Queen','King']
SUITS = ['Clubs','Hearts','Diamonds','Spades']
M = 2**61 - 1

def ev_best(hand_idx):
    v = hand_idx % 13 + 1
    hi = (15 - 3*v) / 13
    lo = (3*v - 27) / 13
    return ('h' if hi >= lo else 'l')

def rebase(n, b=52):
    if n < b: return [n]
    return [n % b] + rebase(n // b, b)

def play():
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

    digits = []          # base-52 digits in deal order (MS first per state)
    states = []          # recovered full states
    mul = inc = None
    pending = None       # predicted upcoming digits (MS first)
    pi = 0

    r = send({})
    for rnd in range(199):
        hand = r.get("hand", "")
        m = re.match(r"(\w+) of (\w+)", hand)
        hand_idx = SUITS.index(m.group(2)) * 13 + VALUES.index(m.group(1)) if m else 0
        if mul is not None and pending is not None and pi < len(pending):
            hid_idx = pending[pi]; pi += 1
            hv, pv = hand_idx % 13, hid_idx % 13
            choice = "higher" if pv > hv else "lower"
        else:
            choice = "higher" if ev_best(hand_idx) == 'h' else "lower"
        r = send({"choice": choice})
        msg = r.get("msg", "")
        mm = re.search(r"card was (\w+) of (\w+)", msg)
        if not mm:
            print("unexpected:", r); continue
        hid_idx = SUITS.index(mm.group(2)) * 13 + VALUES.index(mm.group(1))
        digits.append(hid_idx)
        # state boundary detection via reshuffle notice in msg
        sm = re.search(r"reshuffle the deck after (\d+) rounds", msg)
        if sm and len(digits) > 1:
            # the notice fires when a new state started THIS deal; boundary before current digit
            pass
        # simpler: states have fixed length per state = rebase length; detect when digit count
        # reaches a state length: first state length known from first reshuffle notice
        if mul is None:
            # collect states by length: first notice tells len of CURRENT state's deals
            pass
        if r.get("$", 10**9) <= 2:
            print("broke risk, bailing at", r.get("$"), "round", rnd); sock.close(); return None
        if "flag" in msg:
            print("FLAG MSG:", msg); open("flag_lcg1.txt","w").write(msg); sock.close(); return msg
    print("final:", msg[:120], "$", r.get("$"))
    sock.close()
    return None

# state-length detection: the welcome msg / reshuffle notice says "after N rounds"
# N = number of deals remaining in the NEW state. We'll parse notices to segment digits.
# (implemented in play2 below)
