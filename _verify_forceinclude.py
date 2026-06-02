# _verify_forceinclude.py — confirm covered-name force-include now catches
# Google News items (not just DIRECT). Uses today's real scraped rows.
import os, csv, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from merge_and_clean import enforce_covered_inclusion

rows = []
with open("output/headlines_2026-05-28.csv", newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rows.append({"title": r.get("title",""), "source": r.get("source",""),
                     "link": r.get("link",""), "published_local": r.get("published_local",""),
                     "source_type": r.get("source_type","")})

report = {}  # empty digest → everything covered-name must be force-added
res = enforce_covered_inclusion(report, rows, max_add=40)
forced = report.get("Forced inclusion (covered name)", [])
print(f"counters: {res}")
print(f"force-included: {len(forced)} items")
gnews_forced = 0
brad = False
for it in forced:
    st = next((r["source_type"] for r in rows if r["title"] == it["headline"]), "?")
    if st == "gnews":
        gnews_forced += 1
    if "bradesco sa" in it["headline"].lower() and "regional" in it["headline"].lower():
        brad = True
    print(f"  [{it['ticker']:5}] ({st:6}) {it['headline'][:70]}")
print(f"\ngnews items force-included: {gnews_forced}  (was 0 before the change)")
print(f"Bradesco Saúde regional plan present: {brad}")
