# _test_send_nonotes.py — one-off: render today's H&E clipping with notes OFF
# and email it to a single test address only. Mirrors run_daily Steps 3-5 but
# (a) skips cross-run dedup so today's already-seen items still appear, and
# (b) sends only to TEST_RECIPIENT — never the team list. Does not write vault.

import os, csv
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from email_sender import _load_env
_load_env()

from merge_and_clean import (run as merge_run, reattach_links,
                             enforce_ext_cap, enforce_covered_inclusion)
import claude_reasoning, article_time_enricher, link_resolver
from email_sender import send
from config import current_max_age_hours

TEST_RECIPIENT = "rafaelxoliver4@gmail.com"
CSV = "output/headlines_2026-05-28.csv"


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return [dict(r) for r in csv.DictReader(f)]


def main():
    rows = load_csv(CSV)
    gnews  = [r for r in rows if r.get("source_type") == "gnews"]
    direct = [r for r in rows if r.get("source_type") == "direct"]
    print(f"Loaded {len(gnews)} gnews + {len(direct)} direct from {CSV}")

    # Step 3 — merge/clean WITHOUT cross-run dedup (so today's items appear)
    merged, claude_input = merge_run(gnews, direct, apply_cross_run_dedup=False)
    print(f"Merged -> {len(merged)} items")

    # Step 4 — curate with notes OFF (write_notes=False)
    report, events, notes = claude_reasoning.run(claude_input, write_notes=False)
    print(f"Curated. notes returned = {len(notes)} (expect 0)")

    reattach_links(report, merged)
    enforce_ext_cap(report, merged, max_ext=2)
    enforce_covered_inclusion(report, merged, max_add=20)

    # Resolve gnews links, then freshness-verify + drop stale (the date fix)
    all_items = [it for sec, items in report.items()
                 if sec != "_raw" and isinstance(items, list) for it in items]
    if all_items:
        try:
            link_resolver.resolve_items(all_items)
        except Exception as e:
            print(f"  [WARN] link resolve: {e}")
        vf = article_time_enricher.verify_freshness(all_items, current_max_age_hours())
        stale = set(t for t in vf["stale_titles"] if t)
        if stale:
            for sec in list(report.keys()):
                if sec == "_raw" or not isinstance(report[sec], list):
                    continue
                report[sec] = [it for it in report[sec]
                               if it.get("headline", "") not in stale]
                if not report[sec]:
                    del report[sec]
        print(f"  Freshness: {vf['corrected']} corrected, {len(stale)} stale dropped "
              f"(of {vf['checked']} checked)")

    total = sum(len(v) for v in report.values() if isinstance(v, list))
    print(f"Sending {total} items, {len(events)} events, {len(notes)} notes "
          f"to {TEST_RECIPIENT} ...")
    n = send(report, events, recipients=[TEST_RECIPIENT], notes=notes)
    print(f"Sent ({n} items) to {TEST_RECIPIENT}")


if __name__ == "__main__":
    main()
