# H&E News Clipping — Project Context & Operating Manual

> **Read this first.** It's the onboarding doc for a fresh Claude Code chat or a
> new person: what this project is, how it works, what's been done, and the rules
> for changing it. This file is auto-loaded by Claude Code when working in this
> folder. Keep it up to date (see "Working conventions" below).

---

## ⚠️ Operating principles (do not violate)

1. **Never make the clipping worse.** Both clippings (this one and TMT) were
   already running *well* before recent changes. Every change must **improve or
   at least hold** output quality vs. before — never regress coverage, add noise,
   or break delivery. If a change *might* worsen things, test first and be ready
   to revert. If quality drops, **roll back and re-evaluate** (git history is the
   safety net).
2. **Test before trusting a risky change.** The owner (Rafael) spot-checks via a
   personal address **rafaelxoliver4@gmail.com**. To send a test there without
   hitting the UBS team, call `email_sender.send(report, events,
   recipients=["rafaelxoliver4@gmail.com"], notes=notes)`, or reuse the
   `_run_catchup.py` / `_test_send_nonotes.py` patterns (recipient override).
   Never test-send to the real `EMAIL_RECIPIENTS`.
3. **Keep this file and GitHub current** — see "Working conventions" at the
   bottom. Every change → update this doc → commit → push.

---

## What this is
An **automated daily news-clipping pipeline for UBS LatAm H&E (Healthcare &
Education) equity research**. It scrapes the day's news, has Claude curate the
*material* items for the covered universe, and emails a formatted clipping to the
analyst team. Runs unattended via Windows Task Scheduler.

- **Owner:** Rafael Oliveira (UBS LatAm equity research).
- **Companion pipeline:** the TMT clipping (Telecom/Media/Tech) — separate repo
  `tmt-clipping`, near-identical code, **no shared state**. Fixes usually belong
  in **both**; check consistency when changing shared logic.

## Goal
Every weekday, deliver a concise, **material-only** digest of news relevant to the
covered names and their sectors, so the analyst never misses anything important.
Quality over volume — the curator deliberately drops noise.

## Coverage universe (`config.py` → `SECTORS`)
| Sector | Covered tickers |
|---|---|
| Hospitals & Health Services | RDOR (Rede D'Or), ONCO (Oncoclínicas) |
| Health Plans | HAPV (Hapvida), ODPV (Odontoprev), SAUD (Bradsaúde) |
| Diagnostics | FLRY (Fleury) |
| Pharma | BLAU (Blau) |
| Higher Education | YDUQ, COGN, ANIM, AFYA, LAUR |
| Cross-cutting (GLP-1) | weight-loss drugs → payers/hospitals/diagnostics |
| Epidemiology / Public Health | outbreaks → MLR, hospital occupancy, test volumes |
| General Regulatory / Macro | ANS / ANVISA / SUS / tax reform |

12 Brazilian names + 2 NASDAQ LatAm names (AFYA, LAUR). Mostly Brazil/Portuguese;
US edition only for AFYA/LAUR/GLP-1/global pharma.

## How it works — `run_daily.py` orchestrates 5 steps
1. **Scrape** — `gnews_scraper.py` (Google News RSS, smart keyword×edition routing)
   + `url_scraper.py` (direct sources, RSS-first then HTML fallback; cap 30/source).
2. **Merge/clean** — `merge_and_clean.py`: drop empty titles → **opinion filter**
   (`_is_opinion`) → cross-source + cross-run dedup (24h) → sector assignment →
   relevance scoring → cap 80/sector & 400 total.
3. **Curate** — `claude_reasoning.py` → Claude (Claude Code CLI on the Max plan,
   or the API if `ANTHROPIC_API_KEY` is set) categorises into sector buckets using
   the editorial rules in `wiki_context.py` (`ANALYST_CONTEXT`). **Notes/"UBS's
   take" are disabled** (`write_notes=False`).
4. **Safety nets** — `reattach_links`, `enforce_ext_cap` (≤2 Google-News items),
   `enforce_covered_inclusion` (force-include any covered-name story from ANY
   source, ≤2/ticker, **skipping the company's own website**), then link-resolve →
   `verify_freshness` (reads each article's *real* publish date, drops stale).
   **Empty digests are NOT sent** (skip-empty guard).
5. **Deliver** — `email_sender.py` (Gmail SMTP) + markdown to vault `raw/clippings_he/`.

**Self-learning:** `topics.py` (scores/decays watch topics); `learn.py` (every 10
runs, refines `ANALYST_CONTEXT` — note: this **modifies `wiki_context.py`** on its
own; commit it so the backup stays current).

## Run it (from INSIDE this folder — `OUTPUT_DIR` is relative)
```
python run_daily.py            # full run + send to team
python run_daily.py --test     # sample data, no internet, no email
python run_daily.py --skip-scrape   # reuse last CSV
python run_daily.py --no-email      # print JSON, don't send (skips cross-run dedup)
python run_daily.py --dry-email     # render HTML preview, don't send
```

## Schedule (Windows Task Scheduler, weekdays Mon–Fri, BRT)
**06:40 and 17:00** (2 runs/day). `StartWhenAvailable=true` (a missed run fires
when the PC next powers on — so the laptop should be on by ~06:40). Task names
still read "07-00"/"17-00 BRT" but the morning one fires **06:40**.

## Secrets & config
- **`.env` (gitignored — NOT in the repo):** `FROM_EMAIL=ibotatom@gmail.com`,
  `EMAIL_APP_PASSWORD=<Gmail app password>`. **Recreate this file to run.**
- `EMAIL_RECIPIENTS` in `config.py`: rafael.oliveira / eduardo.resende / leonardo.olmos @ubs.com.
- Editorial rules: `wiki_context.py` → `ANALYST_CONTEXT`.

## Change log (most recent first — APPEND here on every change)
- **2026-06-03** — **Restructured into 6 themes** (3 health + GLP-1 separate + 2
  education): "Health - Providers", "Health - Payers & Pharma",
  "Cross-cutting (GLP-1)", "Public Health & Regulation", "Education - Companies",
  "Education - Policy & Medicine". Education input doubled (2×80 cap vs 1×80).
  Touched `config.py` (SECTORS + SECTOR_ORDER), `claude_reasoning.py` (bucket
  prompt + example), `wiki_context.py` (sector refs). Verified end-to-end +
  test-sent to rafaelxoliver4@gmail.com.
- **2026-06-03** — Audit fixes: skip empty-digest send; block company-own-site
  force-include ("Afya | Home", "Rede D'Or" marketing); committed the auto-learn
  `wiki_context.py`; gitignored stray probe/backup files.
- **2026-06-02** — GitHub backup created (private repo) + this CLAUDE.md.
  Education de-noising: removed ambiguous keywords (`Saber`/`Anima`/`Vasta`/
  `Laureate`/`Una`/`Cruzeiro do Sul`) that flooded Higher Education with noise.
  Added education sources: **Revista Ensino Superior**, **Agência Brasil Educação**,
  **O Globo Educação** (pox feed, 100-deep), **G1 Educação** upgraded HTML→RSS.
  Repointed **Valor Educação/Saúde** to their dedicated pox section feeds. Added
  **opinion filter** (drops "Opinião"/`/colunas/`). Fixed "Laur" guitarist match.
- **2026-06-01** — Valor section feeds 404'd → repointed + added **Valor Impresso**
  (print). (Root cause of earlier thin education/health.)
- **2026-05-28** — Stale-date fix (read real `data_publicacao`/JSON-LD
  `datePublished`, fetch window 220 KB, resolve gnews links before freshness).
  Notes/"UBS's take" disabled. Force-include extended to all sources + per-ticker
  cap (2). Morning runs moved to **06:40**.

## Known issues / fragilities
- **Email send has no retry** — a transient Gmail "connection closed" loses the
  run (happened once). *Candidate fix: retry-with-backoff in `email_sender.send()`.*
- **Claude CLI categorisation can time out** (1500s) and kill the run; recovers on
  a manual re-run (`_run_catchup.py`).
- **Morning runs (Tue–Fri) are the overnight delta** (cross-run dedup) → can be
  thin on quiet nights. Monday uses a 72h weekend look-back.
- **Education vs Health imbalance:** RESOLVED 2026-06-03 — restructured into 6
  themes (3 health + GLP-1 + 2 education); education input doubled. Note: digest
  *output* still reflects materiality, so on thin-news days education can be light
  (correct, not a regression).
- **Auto-learn rewrites `wiki_context.py`** periodically — remember to commit it.

## Gotchas
- OneDrive paths have spaces/accents/& — always run scripts **from this folder**;
  in tooling, prefer the Read tool with full paths (Glob/Bash globbing fails here).
- No `ANTHROPIC_API_KEY` → uses the Claude Code CLI (`claude.exe`).
- `git history is the source of truth` for rollbacks (`*_backup_*.py` are gitignored).

## 🔁 Working conventions (KEEP THESE)
**After ANY change to this pipeline, ALWAYS:**
1. **Update this `CLAUDE.md`** — add a dated line to the Change log and update any
   section that's now stale (sources, schedule, known issues, etc.).
2. **Commit + push to GitHub** so the backup and context stay current:
   ```
   git add -A && git commit -m "what changed" && git push
   ```
3. Verify it still **compiles** and (for risky changes) **test-send to
   rafaelxoliver4@gmail.com** before trusting it on the team.

This self-maintenance rule is itself part of the doc — do not drop it.

## Backup / version control
Private GitHub repo: **https://github.com/rafaelxoliver4-art/he-clipping** (branch `master`).
