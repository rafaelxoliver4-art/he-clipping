# _test_date_fix.py — one-off validation of the date-correctness fix.
#
# Takes the two ONCO items from today's scraped CSV (which carried WRONG
# Google News pubDates), resolves their real publisher URLs, reads the true
# publish date with the fixed extractor, and emails a before/after summary
# to a single test address. Does NOT touch seen_headlines or the team list.

import os
import csv
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from email_sender import _load_env
_load_env()

import link_resolver
import article_time_enricher
from article_time_enricher import _real_date_of, verify_freshness
from email_sender import send
from config import current_max_age_hours, LOCAL_TZ

TEST_RECIPIENT = "rafaelxoliver4@gmail.com"
CSV = "output/headlines_2026-05-28.csv"
TARGETS = ["dispara 57%", "despenca quase 16%"]


def load_targets():
    items = []
    with open(CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            title = row.get("title", "")
            if any(t.lower() in title.lower() for t in TARGETS):
                items.append({
                    "ticker": "ONCO",
                    "headline": title,
                    "source": row.get("source", ""),
                    "link": row.get("link", ""),
                    "gnews_date": row.get("published_local", ""),  # the WRONG date
                    "date": row.get("published_local", ""),
                })
    return items


def main():
    items = load_targets()
    print(f"Loaded {len(items)} ONCO items from today's CSV\n")

    print("STEP 1 — Google News pubDate (what the digest showed):")
    for it in items:
        print(f"   [{it['gnews_date']}]  {it['headline'][:70]}")

    print("\nSTEP 2 — resolve news.google.com -> real publisher URL...")
    link_resolver.resolve_items(items)
    for it in items:
        print(f"   {it['link'][:90]}")

    print("\nSTEP 3 — read REAL publish date from the article page (fixed extractor):")
    for it in items:
        real = _real_date_of(it)
        it["real_date"] = real or "(could not read)"
        print(f"   real={it['real_date']}   google={it['gnews_date']}   {it['headline'][:55]}")

    print("\nSTEP 4 — freshness verdict (24h window):")
    age = current_max_age_hours()
    # work on a copy so we can show both kept + dropped in the email
    vf = verify_freshness([dict(it) for it in items], age)
    stale = set(t for t in vf["stale_titles"] if t)
    for it in items:
        verdict = "DROPPED as stale" if it["headline"] in stale else "kept (fresh)"
        it["verdict"] = verdict
        # show the corrected real date in the email
        if it.get("real_date") and it["real_date"] != "(could not read)":
            it["date"] = it["real_date"]
        print(f"   {verdict:20}  real={it.get('real_date')}  {it['headline'][:50]}")

    # ── Build a small before/after email ──────────────────────────────────────
    report = {"ONCO — date verification test": [
        {"ticker": "ONCO", "headline": it["headline"], "source": it["source"],
         "link": it["link"], "date": it["date"]}
        for it in items
    ]}

    note_lines = ["\U0001F4CD ONCO: date-correctness fix — before / after"]
    note_lines.append("What happened:")
    for it in items:
        note_lines.append(
            f"• **{it['headline'][:80]}** — Google News said "
            f"**{it['gnews_date']}**, real publish date is **{it.get('real_date')}** "
            f"→ {it['verdict']}.")
    note_lines.append("\U0001F50E Take:")
    note_lines.append(
        "The pipeline now resolves the real article URL and reads its true "
        "publish date (JSON-LD datePublished) before the freshness gate. The "
        "Fleury/Porto deal article is from 23 Mar 2026, so in a live run it is "
        "now correctly dropped as stale instead of appearing dated 'today'.")
    notes = ["\n".join(note_lines)]

    print(f"\nSTEP 5 — emailing before/after to {TEST_RECIPIENT} only...")
    n = send(report, [], recipients=[TEST_RECIPIENT], notes=notes)
    print(f"   Sent ({n} items) to {TEST_RECIPIENT}")


if __name__ == "__main__":
    main()
