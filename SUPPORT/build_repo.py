
#!/usr/bin/env python3
"""build_repo.py — constructs the publishable campaign repo from the working corpus.
Deterministic: same input tree => same output tree. Ships in TOOLS/ of the output repo."""
import json, os, re, shutil, sys
from pathlib import Path

SRC = Path(os.environ.get("CAMPAIGN_SRC", "CAMPAIGN-SRC"))  # working corpus root
OUT = Path(os.environ["REPO_OUT"])
DRY = "--dry" in sys.argv

progress = json.loads((SRC/"progress.json").read_text(encoding="utf-8"))
cats = progress["cat_order"]

# ---------- provenance class map from ledgers ----------
prov = {}
for md in sorted(SRC.glob("PROVENANCE_*.md")):
    txt = md.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"(\d{1,4})\D+(WALKED|SERVICE-GIVEN|SOURCE[_ ]ASSISTED[^\n|]*)", txt):
        prov.setdefault(int(m.group(1)), m.group(2).strip())

# ---------- per-file include policy ----------
# NEVER re-host (authors' works / secrets / noise):
EXACT_EXCLUDE = {"statement.txt","flag.txt","output_provided.txt","Dockerfile","server.py",
    "source_provided.py","source.sage","chall.py","chal.py","challenge.py","source.py",
    "task.txt","instance-info.txt"}
PATTERN_EXCLUDE = [re.compile(p) for p in
    [r"^api_.*\.json$", r".*\.html$", r".*\.png$", r".*\.zip$", r"__pycache__", r".*\.pyc$",
     r"^output\.txt$", r"ctfarchive.*", r"^plog.*", r"card.*\.log$"]]
# INCLUDE only our own artifacts:
PATTERN_INCLUDE = [re.compile(p) for p in
    [r"^AAR\.md$", r"^site\.md$", r"^solve.*\.py$", r"^solve.*\.log$", r"^exploit.*\.py$",
     r"^probe.*\.py$", r"^probe_sessions\.json$", r"^diag.*\.py$", r"^selftest.*\.py$", r"^_selftest.*\.json$",
     r"^check.*\.py$", r"^gen.*\.py$", r"^run.*\.py$", r"^build.*\.py$", r"^attack.*\.py$",
     r"^walk.*\.py$", r"^submit.*\.py$", r"^reprobe.*\.sh$", r"^_driver.*\.sh$", r"^_diag.*\.py$",
     r"^live_.*\.py$", r"^live_.*\.log$", r"^banner.*\.txt$", r".*\.gp$", r"^kangaroo.*\.py$",
     r"^test_.*\.py$", r"^sanity.*\.py$", r"^verify.*\.py$", r"^atoms.*\.py$", r"^dbg.*\.py$",
     r"^local.*\.py$", r"^engine\.py$", r"^conv_test\.py$", r"^diffuse_test\.py$", r"^solve_online\.py$",
     r"^flag_[a-z0-9_\-]+\.txt$", r"^example\.py$", r"^handoff.*\.md$"]]
MAX_FILE = 500_000   # bytes per file cap

def include(name):
    if name in EXACT_EXCLUDE: return False
    if any(p.search(name) for p in PATTERN_EXCLUDE): return False
    return any(p.match(name) for p in PATTERN_INCLUDE)

# ---------- sanitization ----------
SUBS = [
 (re.compile(r"[A-Za-z]:[\/]+Users[\/]+[\w.-]+", re.I), "~"),
 (re.compile(r"/c/Users/[\w.-]+", re.I), "~"),
   (re.compile(r"192\.168\.\d+\.\d+"), "LAN-HOST"),
 (re.compile("(?i)" + "st" + "rata"), "GPU-HOST"),
 (re.compile(r'(_csrf_token["\']?\s*[:=]\s*["\'])([A-Za-z0-9]{16,})(["\'])'), r'\1REDACTED\3'),
]
_U = "GT" + "F69"
LITERAL_SUBS = [
    ("C:" + chr(92) + "Users" + chr(92) + _U, "~"),          # single backslashes
    ("C:" + chr(92)*2 + "Users" + chr(92)*2 + _U, "~"),      # doubled in source
    ("C:/Users/" + _U, "~"), ("/c/Users/" + _U, "~"),
    ("C:" + chr(92) + "users" + chr(92) + _U.lower(), "~"),
    (_U, "<USER>"), (_U.lower(), "<USER>"),
]
def sanitize(text):
    hits = 0
    for lit, rep in LITERAL_SUBS:
        c = text.count(lit)
        if c: text = text.replace(lit, rep); hits += c
    for pat, rep in SUBS:
        text, n = pat.subn(rep, text); hits += n
    return text, hits

gate_report = {}
def copy_file(src, dst):
    if src.stat().st_size > MAX_FILE: 
        gate_report.setdefault("oversize", []).append(str(src.relative_to(SRC)))
        return False
    try: text = src.read_text(encoding="utf-8")
    except (UnicodeDecodeError, ValueError):
        gate_report.setdefault("binary_skipped", []).append(str(src.relative_to(SRC)))
        return False
    text, hits = sanitize(text)
    if hits: gate_report.setdefault("sanitized", {}).update({str(src.relative_to(SRC)): hits})
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    return True

# ---------- walk challenges ----------
nn2cat = {}
counts = {}
for q in progress["queue"]:
    nn2cat[q["nn"]] = q["category"]
missing_folder = [q["nn"] for q in progress["queue"] if not q.get("folder")]
for q in progress["queue"]:
    if not q.get("folder"): continue
    d = SRC/q["folder"]
    if not d.is_dir(): continue
    m = re.match(r"challenge-(\d+)-", q["folder"])
    if not m: continue
    nn = int(m.group(1)); cat = nn2cat.get(nn, "misc")
    kept = 0
    for f in sorted(d.iterdir()):
        if f.is_file() and include(f.name):
            if not DRY:
                if copy_file(f, OUT/"CHALLENGES"/cat/q["folder"]/f.name): kept += 1
            else: kept += 1
    counts[q["folder"]] = kept

print(json.dumps({"dirs_with_files": sum(1 for v in counts.values() if v),
                  "files": sum(counts.values()), "zero_file_dirs": sum(1 for v in counts.values() if v==0)}, indent=1))
print("gate:", {k:(len(v) if isinstance(v,(list,dict)) else v) for k,v in gate_report.items()})

if not DRY:
    # ---------- FLAGS ----------
    OUT.joinpath("FLAGS").mkdir(parents=True, exist_ok=True)
    with open(OUT/"FLAGS"/"flags.jsonl","w",encoding="utf-8") as fh:
        for q in progress["queue"]:
            fh.write(json.dumps({
                "nn": q["nn"], "slug": q["slug"], "name": q.get("name"),
                "category": q["category"], "points": q.get("points"),
                "status": q["status"], "flag": q.get("flag"),
                "date_solved": q.get("date"),
                "provenance_class": prov.get(q["nn"], "PRE-LEDGER-ERA (class not individually recorded before 2026-11-06 ledgers)"),
                "flag_note": (None if q.get("flag") else ("FLAG-NOT-IN-LEDGER: solve verified via site solved-list; flag redacted in AAR — never fabricated here" if q["status"]=="solved" else None)),
                "url": f"https://cryptohack.org/challenges/{q['slug']}/",
            }, ensure_ascii=False)+"\n")
    # ---------- LEDGER sanitized ----------
    OUT.joinpath("LEDGER").mkdir(parents=True, exist_ok=True)
    led = json.loads(json.dumps(progress))
    for q in led["queue"]: q.pop("flag", None)
    (OUT/"LEDGER"/"progress_sanitized.json").write_text(json.dumps(led, indent=1, ensure_ascii=False), encoding="utf-8")
if not DRY:
    for md in sorted(SRC.glob("PROVENANCE_*.md")):
        copy_file(md, OUT/"FLAGS"/md.name)
    if (SRC/"HANDOFF.md").is_file():
        copy_file(SRC/"HANDOFF.md", OUT/"LEDGER"/"HANDOFF_sanitized.md")
print("done dry" if DRY else "BUILT ->", OUT)
