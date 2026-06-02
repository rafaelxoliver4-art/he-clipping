# merge_and_clean.py — Merge, deduplicate, score and cap headlines for Claude

import json
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from config import SECTORS, MAX_HEADLINES_PER_SECTOR, MAX_TOTAL_HEADLINES, LOCAL_TZ

# ── Keyword → sector map (lowercase, built once) ─────────────────────────────
def _build_kw_sector_map() -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    # Priority order: covered > keywords > peers (later writes win for peers)
    for sector, data in SECTORS.items():
        for item in data["peers"] + data["keywords"]:
            mapping[item.lower()] = sector
        for item in data["covered"]:          # covered names override
            mapping[item.lower()] = sector
    return mapping

KW_TO_SECTOR = _build_kw_sector_map()

# Flat set of all covered ticker/name strings (lowercase)
COVERED_LOWER = {
    name.lower()
    for data in SECTORS.values()
    for name in data["covered"]
}


def _guess_sector(row: Dict) -> str:
    """Heuristically assign a sector using keyword + title scan."""
    keyword  = (row.get("keyword") or "").lower()
    title    = (row.get("title")   or "").lower()

    # 1. Keyword directly in map
    if keyword in KW_TO_SECTOR:
        return KW_TO_SECTOR[keyword]

    # 2. Keyword from direct scraper is already a sector name
    if keyword in {s.lower() for s in SECTORS}:
        for s in SECTORS:
            if s.lower() == keyword:
                return s

    # 3. Scan title for known names (longest match wins to avoid false positives)
    matches = []
    for kw_lower, sector in KW_TO_SECTOR.items():
        if len(kw_lower) >= 4 and re.search(r"\b" + re.escape(kw_lower) + r"\b", title):
            matches.append((len(kw_lower), sector))
    if matches:
        matches.sort(reverse=True)
        return matches[0][1]

    return "General"


def _relevance_score(row: Dict) -> int:
    """Lower score = higher priority.
       0 = covered ticker mentioned in title
       1 = keyword match (sector-relevant but not covered)
       2 = general / direct source fallback
    """
    title   = (row.get("title") or "").lower()
    keyword = (row.get("keyword") or "").lower()

    if keyword in COVERED_LOWER:
        return 0
    for name in COVERED_LOWER:
        if len(name) >= 3 and re.search(r"\b" + re.escape(name) + r"\b", title):
            return 0
    if keyword in KW_TO_SECTOR:
        return 1
    return 2


def assign_sectors(rows: List[Dict]) -> List[Dict]:
    for row in rows:
        row["sector"] = _guess_sector(row)
    return rows


def cap_per_sector(rows: List[Dict]) -> List[Dict]:
    """Keep at most MAX_HEADLINES_PER_SECTOR per sector, total ≤ MAX_TOTAL_HEADLINES.

    PRIORITY RULE (added 2026-05-22): direct-source rows are sorted first so
    they are NEVER displaced by EXT items when the cap is reached. EXT items
    fill the remaining capacity.
    """
    direct_info = _direct_source_names()

    def _row_is_direct(r):
        return _is_direct(r, direct_info)

    rows_sorted = sorted(rows, key=lambda r: 0 if _row_is_direct(r) else 1)

    counts: Dict[str, int] = {}
    out: List[Dict] = []
    for row in rows_sorted:
        sec = row.get("sector", "General")
        counts.setdefault(sec, 0)
        if counts[sec] < MAX_HEADLINES_PER_SECTOR and len(out) < MAX_TOTAL_HEADLINES:
            out.append(row)
            counts[sec] += 1
    return out


import unicodedata as _ud


def _strip_accents(s: str) -> str:
    if not s:
        return ""
    nfkd = _ud.normalize("NFKD", s)
    return "".join(c for c in nfkd if not _ud.combining(c))


def _direct_source_names():
    """Returns list of {name, brand, domain} dicts for direct sources.
       See TMT merge_and_clean for matching algorithm rationale."""
    try:
        from config import DIRECT_SOURCES
        from urllib.parse import urlparse
    except Exception:
        return []
    out = []
    for s in DIRECT_SOURCES:
        name = _strip_accents((s.get("name") or "").strip().lower())
        url  = s.get("url") or ""
        try:
            netloc = urlparse(url).netloc.lower()
            if netloc.startswith("www."):
                netloc = netloc[4:]
        except Exception:
            netloc = ""
        # Brand = leading distinctive token(s).
        # 3+ char acronym (CFM, ANS, MEC, JOTA) → use as brand.
        # 1-2 char article (o, el, la) → combine with next word.
        words = name.split()
        if not words:
            brand = ""
        elif len(words[0]) >= 3:
            brand = words[0]
        elif len(words) >= 2:
            brand = words[0] + " " + words[1]
            if len(brand) < 4:
                brand = ""
        else:
            brand = ""
        out.append({"name": name, "brand": brand, "domain": netloc})
    return out


def _is_direct(row: Dict, direct_info) -> bool:
    if (row.get("source_type") or "").strip().lower() == "direct":
        return True
    src_raw = (row.get("source") or "").strip().lower()
    if not src_raw:
        return False
    src = _strip_accents(src_raw)
    for info in direct_info:
        if src == info["name"]:
            return True
        if info["brand"] and src == info["brand"]:
            return True
        if info["brand"] and src.startswith(info["brand"] + " "):
            return True
        if info["domain"] and info["domain"] in src:
            return True
    return False


def _is_direct_strict(row: Dict, direct_info) -> bool:
    """Stricter direct-source check (no brand-prefix). Use for the safety net.

    The general _is_direct uses brand-prefix matching ("folha " matches
    "Folha Equilíbrio e Saúde"), which catches legitimate variants like
    "Valor Investe" but also misfires on unrelated regionals like
    "Folha do ES" or "Folha do Estado da Bahia". For the covered-name
    safety net we don't want those false positives.
    """
    if (row.get("source_type") or "").strip().lower() == "direct":
        return True
    src_raw = (row.get("source") or "").strip().lower()
    if not src_raw:
        return False
    src = _strip_accents(src_raw)
    for info in direct_info:
        if src == info["name"]:
            return True
        if info["brand"] and src == info["brand"]:
            return True
        if info["domain"] and info["domain"] in src:
            return True
    return False


def format_for_claude(rows: List[Dict]) -> str:
    """
    Compact plain-text block for Claude.
    Format: N. <DIRECT|EXT> [Sector] Source (published): Title [lang]

    The <DIRECT|EXT> tag tells the curator which items come from the curated
    reliable-source list (DIRECT_SOURCES) vs Google News only (EXT).
    CATEGORISE_SYSTEM enforces: prefer DIRECT items; include AT MOST 5 EXT
    items across all sectors, and only if EXTREMELY material to coverage.

    NOTE: We do NOT pass the link to Claude. Link plumbing is 100% the code's
    responsibility — Claude focuses on triage and tagging only. After Claude
    returns curated items, the link is re-attached by (headline, source)
    match against the raw rows.
    """
    direct_names = _direct_source_names()
    lines = []
    for i, r in enumerate(rows, 1):
        sector = r.get("sector", "General")
        source = r.get("source", "?")
        title  = r.get("title", "")
        lang   = r.get("edition_lang", "")
        pub    = r.get("published_local", "")
        tag    = "DIRECT" if _is_direct(r, direct_names) else "EXT"
        lang_tag = f" [{lang}]" if lang and lang != "mixed" else ""
        # Show explicit "date unknown" so curator can apply title-based judgment
        pub_tag  = f" ({pub})" if pub else " (date unknown)"
        lines.append(f"{i:3}. <{tag}> [{sector}] {source}{pub_tag}: {title}{lang_tag}")
    return "\n".join(lines)


# ── Re-attach link + source_url after the curator returns ─────────────────────
# Claude only emits {ticker, headline, source, date} — links live with the code.
# We match curator output back to raw rows by (normalised headline, source) and
# attach `link` + `source_url` so the link resolver can decode and the email
# can render the right href.

def _covered_names():
    """Set of covered tickers + COVERED_NAME_ALIASES (lowercase, accent-stripped)."""
    try:
        from config import SECTORS, COVERED_NAME_ALIASES
    except Exception:
        try:
            from config import SECTORS
            COVERED_NAME_ALIASES = {}
        except Exception:
            return set()
    out = set()
    for sec, info in SECTORS.items():
        for name in info.get("covered", []) or []:
            n = _strip_accents(str(name).lower()).strip()
            if n and len(n) >= 3:
                out.add(n)
    for ticker, aliases in (COVERED_NAME_ALIASES or {}).items():
        for alias in aliases:
            n = _strip_accents(str(alias).lower()).strip()
            if n and len(n) >= 3:
                out.add(n)
    return out


def _alias_to_ticker():
    try:
        from config import COVERED_NAME_ALIASES
    except Exception:
        return {}
    out = {}
    for ticker, aliases in (COVERED_NAME_ALIASES or {}).items():
        for alias in aliases:
            out[_strip_accents(str(alias).lower()).strip()] = ticker
    return out


_AMBIGUOUS_ALIASES = {
    # Common surnames / French town names that collide with covered names
    "fleury",
    # Common verbs / words
    "claro",   # "claro" = clear in Portuguese (also Claro telco)
    "vivo",
    "afya",    # "afya" is rare in PT but better safe
    "laureate",  # "Nobel Laureate" / "Pulitzer Laureate" — common phrase
}

_CORPORATE_QUALIFIERS = {
    # Brazilian financial / corporate vocabulary that disambiguates
    "acoes", "acao", "anuncia", "anunciou", "reporta", "reportou",
    "lucro", "prejuizo", "receita", "ebitda", "trimestre", "resultado",
    "balanco", "grupo", "holding", "participacoes", "s.a", "s/a", "sa",
    "investidor", "investidores", "bovespa", "b3", "rating", "guidance",
    "ipo", "follow-on", "follow on", "oferta", "secundaria", "primaria",
    "btg", "itau bba", "itau bb", "xp", "bradesco bbi", "safra", "morgan",
    "goldman", "ubs", "target", "preco-alvo", "compra", "venda", "neutro",
    "outperform", "overweight", "underweight", "underperform",
    "dividendo", "dividendos", "jcp", "juros sobre capital proprio",
    "controlada", "subsidiaria", "ms&a", "fusao", "aquisicao",
    "earnings", "results", "press release", "press-release",
}


def enforce_covered_inclusion(report: dict, raw_rows: list, max_add: int = 10,
                              max_per_ticker: int = 2) -> dict:
    """Server-side safety net (added 2026-05-25; extended to all sources
    2026-05-28): force-include any row whose title contains a covered name,
    regardless of source (DIRECT or Google News). Tagged with the proper ticker.

    Uses _is_direct_strict (no brand-prefix matching) to avoid false-positive
    direct tagging like "folha do es" matching "Folha Equilíbrio e Saúde".

    For ambiguous aliases (Fleury, Claro, Vivo, etc.), requires either the
    ticker form to also appear in the title OR a corporate qualifier
    nearby — otherwise a sports headline like "FLEURY Vs DERRIERE" would
    fire on the "fleury" alias.
    """
    direct_info = _direct_source_names()
    covered = _covered_names()
    alias_map = _alias_to_ticker()
    if not covered:
        return {"added": 0, "already_present": 0, "skipped": 0}

    in_digest_titles = set()
    in_digest_urls = set()
    for sec, items in report.items():
        if sec == "_raw" or not isinstance(items, list):
            continue
        for it in items:
            t = _norm_title(it.get("headline", ""))
            if t:
                in_digest_titles.add(t)
            u = _norm_url_key(it.get("link", ""))
            if u:
                in_digest_urls.add(u)

    counter = {"added": 0, "already_present": 0, "skipped": 0}
    added_keys = set()
    per_ticker = {}   # cap forced additions per ticker so one busy name (e.g.
                      # ONCO in crisis) can't flood the digest with 16 variants
    import re as _re

    for row in raw_rows:
        if counter["added"] >= max_add:
            break
        # Covered-name stories must survive regardless of source. Until
        # 2026-05-28 this was DIRECT-only; extended to ALL sources (incl.
        # Google News) so a covered-name story carried only by gnews (e.g.
        # "Bradesco Saúde lança plano Regional" via Monitor Mercantil) is not
        # dropped by the EXT cap or curator. The covered-name-in-title check
        # plus the ambiguity guard below keep false positives out, and the
        # downstream freshness check still drops stale items.
        title = row.get("title", "") or ""
        title_norm = _strip_accents(title.lower())
        # Pick the LEFTMOST covered name (primary subject of the headline)
        best_pos = None
        hit_name = None
        for cn in covered:
            if cn in title_norm:
                pat = r"(?:^|[^a-z0-9])" + _re.escape(cn) + r"(?:[^a-z0-9]|$)"
                m = _re.search(pat, title_norm)
                if m and (best_pos is None or m.start() < best_pos):
                    best_pos = m.start()
                    hit_name = cn
        if not hit_name:
            continue
        # Ambiguity guard: if alias is ambiguous, require ticker form OR a
        # corporate qualifier in the title. Otherwise drop (e.g. "Fleury" in
        # a sports headline).
        if hit_name in _AMBIGUOUS_ALIASES:
            ticker_guess = alias_map.get(hit_name, hit_name.upper())
            has_ticker = ticker_guess.lower() in title_norm or \
                         (ticker_guess + "3").lower() in title_norm
            has_qualifier = any(q in title_norm for q in _CORPORATE_QUALIFIERS)
            if not (has_ticker or has_qualifier):
                counter["skipped"] += 1
                continue
        tk = _norm_title(title)
        uk = _norm_url_key(row.get("link", ""))
        if tk in in_digest_titles or (uk and uk in in_digest_urls):
            counter["already_present"] += 1
            continue
        if tk in added_keys:
            continue
        ticker = alias_map.get(hit_name, hit_name.upper())
        # Per-ticker cap: surface a name's top story or two, not every variant.
        if per_ticker.get(ticker, 0) >= max_per_ticker:
            counter["skipped"] += 1
            continue
        added_keys.add(tk)
        per_ticker[ticker] = per_ticker.get(ticker, 0) + 1
        sec_name = "Forced inclusion (covered name)"
        if sec_name not in report:
            report[sec_name] = []
        report[sec_name].append({
            "ticker": ticker,
            "headline": title,
            "source": row.get("source", ""),
            "date": row.get("published_local", ""),
            "link": row.get("link", ""),
        })
        counter["added"] += 1
    return counter


def _norm_title(s: str) -> str:
    """Normalise a title for fuzzy matching:
       NFKD-fold accents, lowercase, strip all non-alphanumeric.
       Google News often appends ' - Source Name' to titles; strip that first
       so the normalised form matches whether the curator preserved it or not.
    """
    import re as _re, unicodedata
    if not s:
        return ""
    s = s.strip()
    s = _re.sub(r"\s+[-–—|]\s+[^-–—|]{2,60}$", "", s)
    nfkd = unicodedata.normalize("NFKD", s)
    ascii_only = "".join(c for c in nfkd if not unicodedata.combining(c))
    return _re.sub(r"[^a-z0-9]+", "", ascii_only.lower()).strip()


def enforce_ext_cap(report: Dict, raw_rows: List[Dict], max_ext: int = 5) -> Dict[str, int]:
    """
    Code-level safety net for the 'max 5 EXT items' rule.
    Drops surplus non-direct-source items in place. Returns counters.
    """
    direct_names = _direct_source_names()
    counters = {"direct_kept": 0, "ext_kept": 0, "ext_dropped": 0}

    ext_locations = []
    for sector, items in report.items():
        if sector == "_raw" or not isinstance(items, list):
            continue
        for idx, it in enumerate(items):
            if _is_direct({"source": it.get("source",""), "source_type": ""}, direct_names):
                counters["direct_kept"] += 1
            else:
                ext_locations.append((sector, idx, it))

    if len(ext_locations) <= max_ext:
        counters["ext_kept"] = len(ext_locations)
        return counters

    to_keep = set(id(loc[2]) for loc in ext_locations[:max_ext])
    counters["ext_kept"] = max_ext
    for sector, items in report.items():
        if sector == "_raw" or not isinstance(items, list):
            continue
        kept = []
        for it in items:
            if _is_direct({"source": it.get("source",""), "source_type": ""}, direct_names):
                kept.append(it)
            elif id(it) in to_keep:
                kept.append(it)
            else:
                counters["ext_dropped"] += 1
        report[sector] = kept
    return counters


def reattach_links(report: Dict, raw_rows: List[Dict]) -> Dict[str, int]:
    """
    Walk the curated report and attach `link` (and `source_url` when known)
    to each item by matching against raw_rows. Returns counters.

    Match cascade:
      1. Exact normalised (headline, source)
      2. Exact normalised headline only
      3. Substring (curator's headline contained in raw, or vice versa)
    """
    counters = {"matched": 0, "headline_only": 0,
                "substring": 0, "unmatched": 0}

    by_title_source: Dict[tuple, Dict] = {}
    by_title: Dict[str, Dict] = {}
    norm_rows: List[tuple] = []
    for r in raw_rows:
        t = _norm_title(r.get("title", ""))
        if not t:
            continue
        src = (r.get("source") or "").strip().lower()
        by_title_source.setdefault((t, src), r)
        by_title.setdefault(t, r)
        norm_rows.append((t, r))

    def _substring_lookup(needle: str) -> Optional[Dict]:
        if not needle or len(needle) < 12:
            return None
        for t, r in norm_rows:
            if t.startswith(needle) or needle.startswith(t):
                return r
        if len(needle) >= 20:
            for t, r in norm_rows:
                if needle in t or t in needle:
                    return r
        return None

    for sector, items in report.items():
        if sector == "_raw" or not isinstance(items, list):
            continue
        for it in items:
            headline = it.get("headline", "")
            source   = (it.get("source") or "").strip().lower()
            t = _norm_title(headline)
            hit = by_title_source.get((t, source))
            if hit:
                counters["matched"] += 1
            else:
                hit = by_title.get(t)
                if hit:
                    counters["headline_only"] += 1
                else:
                    hit = _substring_lookup(t)
                    if hit:
                        counters["substring"] += 1
            if hit:
                it["link"] = hit.get("link", "")
                if hit.get("source_url"):
                    it["source_url"] = hit["source_url"]
            else:
                counters["unmatched"] += 1
                it.setdefault("link", "")
    return counters


# ── Cross-run dedup ───────────────────────────────────────────────────────────
# Same article often surfaces over consecutive days in Google News. Track
# normalized title keys with their first-seen date and skip recent repeats.
_SEEN_PATH       = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "output", "seen_headlines.jsonl"
)
_SEEN_TTL_DAYS   = 1   # 2026-05-22: 24h window per analyst preference. Items
                       # sent in last 24h are blocked from repeating; items
                       # older than 24h are free to re-appear if newly material.


def _norm_key(title: str) -> str:
    return re.sub(r"[^\w\s]", "", (title or "").lower()).strip()


def _norm_url_key(link: str) -> str:
    """Canonical URL key for dedup. Drops query+fragment+www+trailing slash."""
    if not link:
        return ""
    try:
        from urllib.parse import urlparse
        p = urlparse(link.strip().lower())
        netloc = p.netloc[4:] if p.netloc.startswith("www.") else p.netloc
        path = p.path.rstrip("/")
        if "google.com/search" in p.netloc or "news.google.com" in p.netloc:
            return ""
        if not netloc or not path:
            return ""
        return netloc + path
    except Exception:
        return ""


def _load_seen() -> Tuple[Dict[str, str], Dict[str, str]]:
    """Return ({title_key: date}, {url_key: date}). Drops entries past TTL."""
    out_t: Dict[str, str] = {}
    out_u: Dict[str, str] = {}
    if not os.path.exists(_SEEN_PATH):
        return out_t, out_u
    cutoff = (datetime.now(LOCAL_TZ) - timedelta(days=_SEEN_TTL_DAYS)).strftime("%Y-%m-%d")
    try:
        with open(_SEEN_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    key  = rec.get("k", "")
                    ukey = rec.get("u", "")
                    date = rec.get("d", "")
                    if not date or date < cutoff:
                        continue
                    if key:
                        if key not in out_t or date < out_t[key]:
                            out_t[key] = date
                    if ukey:
                        if ukey not in out_u or date < out_u[ukey]:
                            out_u[ukey] = date
                except json.JSONDecodeError:
                    pass
    except OSError:
        pass
    return out_t, out_u


def _save_seen(seen_t: Dict[str, str], seen_u: Dict[str, str]) -> None:
    """Rewrite the seen file. Schema: {"k": title, "u": url, "d": date}."""
    try:
        os.makedirs(os.path.dirname(_SEEN_PATH), exist_ok=True)
        written_urls = set()
        with open(_SEEN_PATH, "w", encoding="utf-8") as f:
            for k, d in seen_t.items():
                f.write(json.dumps({"k": k, "d": d}, ensure_ascii=False) + "\n")
            for u, d in seen_u.items():
                if u in written_urls:
                    continue
                f.write(json.dumps({"u": u, "d": d}, ensure_ascii=False) + "\n")
                written_urls.add(u)
    except OSError:
        pass


def _cross_run_dedupe(rows: List[Dict]) -> Tuple[List[Dict], int]:
    """Drop rows whose normalized title OR canonical URL was seen in the last
    _SEEN_TTL_DAYS days."""
    seen_t, seen_u = _load_seen()
    today = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d")
    kept: List[Dict] = []
    dropped = 0
    for row in rows:
        key  = _norm_key(row.get("title", ""))
        ukey = _norm_url_key(row.get("link", ""))
        if (key and key in seen_t) or (ukey and ukey in seen_u):
            dropped += 1
            continue
        if key:
            seen_t[key] = today
        if ukey:
            seen_u[ukey] = today
        kept.append(row)
    _save_seen(seen_t, seen_u)
    return kept, dropped


def _cross_dedupe(rows: List[Dict]) -> List[Dict]:
    """
    Deduplicate across the combined gnews + direct list.
    Normalises titles to lowercase stripped of punctuation (same logic as
    gnews_scraper.dedupe). Direct-source rows are kept over gnews duplicates
    because they carry a canonical URL and source name.
    """
    seen: set = set()
    out: List[Dict] = []
    # Stable sort so direct rows come first (source_type != "gnews")
    prioritised = sorted(rows, key=lambda r: 0 if r.get("source_type") != "gnews" else 1)
    for row in prioritised:
        title = (row.get("title") or "").strip()
        key   = re.sub(r"[^\w\s]", "", title.lower()).strip()
        if key and key not in seen:
            seen.add(key)
            out.append(row)
    return out


def run(gnews_rows: List[Dict], direct_rows: List[Dict],
        apply_cross_run_dedup: bool = True) -> Tuple[List[Dict], str]:
    """
    Merge, assign sectors, sort by relevance, cap, and format.
    Returns: (merged_rows, claude_input_string)

    `apply_cross_run_dedup`: pass False in TEST_MODE so sample headlines
    aren't dropped (and don't pollute) the seen_headlines memory.
    """
    all_rows = gnews_rows + direct_rows

    # Drop empty titles
    all_rows = [r for r in all_rows if (r.get("title") or "").strip()]

    # Cross-source dedup (same story from gnews AND a direct RSS feed)
    before = len(all_rows)
    all_rows = _cross_dedupe(all_rows)
    dropped = before - len(all_rows)
    if dropped:
        print(f"  -> cross-source dedup: removed {dropped} duplicates")

    # Cross-run dedup (story already seen in the last 3 days).
    # Skipped in TEST_MODE so iterative testing doesn't poison the dedup memory
    # with sample headlines, and doesn't get blocked by previous test runs.
    if apply_cross_run_dedup:
        all_rows, dropped_run = _cross_run_dedupe(all_rows)
        if dropped_run:
            print(f"  -> cross-run dedup: removed {dropped_run} headlines seen in last "
                  f"{_SEEN_TTL_DAYS} days")

    # Assign sectors
    assign_sectors(all_rows)

    # Score and sort: covered tickers first, then keyword matches, then general
    all_rows.sort(key=_relevance_score)

    # Cap per sector
    capped = cap_per_sector(all_rows)

    # Format for Claude
    claude_input = format_for_claude(capped)

    return capped, claude_input


if __name__ == "__main__":
    test = [
        {"title": "TOTVS conclui aquisição da Linx por R$7 bilhões",
         "source": "Valor Econômico", "keyword": "TOTVS", "edition_lang": "pt-BR",
         "source_type": "gnews", "link": "https://valor.globo.com/totvs"},
        {"title": "TCS is asking staff to use AI even if it hits revenues",
         "source": "Economic Times", "keyword": "TCS", "edition_lang": "en",
         "source_type": "gnews", "link": ""},
    ]
    rows, text = run(test, [])
    print(text)
