# _probe_sources.py — test whether url_scraper can extract articles from
# candidate sources. One-off diagnostic; safe (no email, no state writes).
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from url_scraper import scrape_site

candidates = [
    {"name": "MedicinaS/A (sanity)", "url": "https://medicinasa.com.br/ultimas-noticias/",
     "rss": "https://medicinasa.com.br/feed/", "sector": "Health"},
    {"name": "Sampi Bauru", "url": "https://sampi.net.br/bauru",
     "rss": "", "sector": "General"},
    {"name": "Sampi root", "url": "https://sampi.net.br/",
     "rss": "", "sector": "General"},
]

for src in candidates:
    try:
        rows = scrape_site(src)
        print(f"\n=== {src['name']}  ->  {len(rows)} items ===")
        for r in rows[:6]:
            print(f"   [{r.get('published_local','')}] {r.get('title','')[:75]}")
            print(f"       {r.get('link','')[:95]}")
    except Exception as e:
        print(f"\n=== {src['name']}  ->  ERROR: {e} ===")
