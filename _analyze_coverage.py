import os, sys, re, glob, collections
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from config import SECTORS

print("=== KEYWORDS & COVERED NAMES PER SECTOR ===")
edu_kw = health_kw = 0
for s, d in SECTORS.items():
    nk = len(d.get("keywords", []))
    cov = d.get("covered", [])
    print(f"  {nk:3} kw | covered={cov}  <- {s}")

print("\n=== ITEMS PER SECTOR fed to the curator (today's claude_input) ===")
files = sorted(glob.glob("output/claude_input_2026-06-0*.txt"))
if files:
    text = open(files[-1], encoding="utf-8").read()
    tags = re.findall(r'<(?:DIRECT|EXT)>\s*\[([^\]]+)\]', text)
    c = collections.Counter(tags)
    total = sum(c.values())
    print(f"  file: {files[-1]}  (total {total} items)")
    for s, n in c.most_common():
        print(f"   {n:3}  ({100*n/total:4.1f}%)  {s}")

# Delivered-digest distribution (last 6 vault clippings)
print("\n=== ITEMS PER SECTION in delivered digests (vault, last 6) ===")
vault = os.path.join(os.path.expanduser("~"), "OneDrive", "Documentos",
                     "Obsidian Vault", "raw", "clippings_he")
mds = sorted(glob.glob(os.path.join(vault, "*.md")))[-6:]
EDU = {"Higher Education", "Education"}
agg = collections.Counter()
edu_total = health_total = 0
for m in mds:
    lines = open(m, encoding="utf-8").read().splitlines()
    sec = None; per = collections.Counter()
    for ln in lines:
        if ln.startswith("## "):
            sec = ln[3:].strip()
        elif ln.startswith("- ") and sec:
            per[sec] += 1
    edu = sum(v for k, v in per.items() if k in EDU)
    health = sum(v for k, v in per.items()
                 if k not in EDU and "Next" not in k and "Forced" not in k)
    edu_total += edu; health_total += health
    print(f"  {os.path.basename(m):22}  edu={edu:2}  health/other={health:2}")
print(f"  ---- totals: education={edu_total}  health/other={health_total}")
