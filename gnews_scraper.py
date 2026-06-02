# gnews_scraper.py — parallel Google News RSS harvester
#
# Key change from original: source allowlist is NO LONGER a hard filter.
# Google News already curates relevant sources. Filtering by source name
# was discarding legitimate results from Bloomberg, Reuters, etc.
# The allowlist is now only used for deduplication priority scoring.

from urllib.parse import quote_plus
from urllib.request import urlopen, Request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta
from time import sleep
import unicodedata, re, os, ssl, socket, sys
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import (
    get_query_tasks, LOCAL_TZ, GNEWS_WHEN, SLEEP_S, MAX_AGE_HOURS,
    current_max_age_hours, current_gnews_when,
)

INSECURE_ENV_FLAG = os.environ.get("GNEWS_INSECURE", "0") == "1"
MAX_WORKERS      = 20
FETCH_TIMEOUT_S  = 10
FETCH_RETRIES    = 2
PER_TASK_TIMEOUT = 25  # seconds — abandon a task that hangs past this

# ── Source blocklist ──────────────────────────────────────────────────────────
# Aggregators and syndicators that republish old articles with updated timestamps,
# causing stale news to appear fresh. Match is case-insensitive substring of
# the Google News <source> tag text.
BAD_SOURCES: set = {
    # Aggregators / syndicators (recycle old content with new timestamps)
    "msn",
    "yahoo",          # yahoo news, yahoo finance
    "flipboard",
    "smartnews",
    "upstract",
    "ground news",
    "allsides",
    "newsnow",
    # Financial data aggregators (low editorial value, often duplicate wires)
    "seeking alpha",  # contributor-driven, recycles wires & PR, low edit quality
    "marketbeat",
    "quiver quantitative",
    "markets mojo",
    "stock traders daily",
    "simply wall st",
    "defense world",
    "etf daily news",
    "the fly",
    "benzinga",       # often syndicates press releases as news
    "insider monkey",
    "zacks",          # similar profile to seeking alpha
    "investorplace",
    "247 wall st",
    "barchart",
    # Sports / entertainment (no TMT value)
    "espn",
    "tnt sports",
    "bolavip",
    "imdb",
    "cricbuzz",
    # Generic noise
    "x.com",
    # ── H&E-specific blocklist (added after first run surfaced noise) ──
    # SEO content farms / German aggregators that produced junk in initial scrape
    "ad hoc news",
    "ad-hoc-news",
    "savingadvice",
    "aol.com",
    "portal tela",
    "onefootball",
    # Regional sites that produce lots of low-relevance reajuste / hospital stories
    "tribuna de minas",
    "mix vale",
    "repórter maceió",
    "reporter maceio",
    "rádio itatiaia",
    "radio itatiaia",
    "olhar direto",
    # Civil-service exam content — irrelevant for investor-focused clipping
    "academia concursos",
    "uniten",
    # Low-quality healthcare blogs / patient-info sites (often republish old WHO/Anvisa content)
    "savingadvice.com",
    "tua saúde", "tuasaude",
    "minha vida", "minhavida",
    # Auto-generated stock-news content farms (Rafael flagged Stock Titan specifically)
    "stock titan", "stocktitan",
    "stockanalysis", "stocks to trade", "stockstotrade",
    "investorshub",
    "guia do investidor", "guiadoinvestidor",   # SEO-heavy aggregator
    "acionista.com.br",                          # aggregator-style stock-news site
    "ad-hoc news", "adhoc news",                 # already blocked but variant naming
    # Generic Brazilian noise sites that surface a lot but rarely carry real signal
    "vermelho.org.br",                           # political opinion, not finance
    # ── User-flagged channels to exclude (gathered 2026-05-20, batch 1) ──
    # Substring match (case-insensitive) against Google News <source> tag text.
    "bombabomba",                    # bombabomba.com.br
    "polemica paraíba", "polemica paraiba", "polêmica paraíba",  # Polêmica Paraíba variants
    "mauriliojunior", "maurilio junior",          # mauriliojunior.com
    "apufsc",                        # apufsc.org.br (university-union political)
    "balneário camboriú", "balneario camboriu",   # Notícias Balneário Camboriú
    "newsrondonia", "news rondonia", "news rondônia",   # newsrondonia.com.br (incl. accent variant)
    "portalmarcossantos", "portal marcos santos", "portal do marcos santos",  # portalmarcossantos.com.br variants
    "portalolavodutra", "portal olavo dutra", "olavo dutra",  # catches "Coluna Olavo Dutra" and Portal variants
    "naoviu", "não viu",                          # naoviu.com.br
    "midiajur", "mídiajur",                       # midiajur.com.br
    # ── User-flagged H&E noise channels (batch 2, 2026-05-20) ──
    "98fmnatal", "98 fm natal", "portal 98 fm natal",  # 98fmnatal.com.br — local radio Natal (incl. space variants)
    "acessa.com.br", "acessa.com", "acessa ",  # acessa.com.br — regional Brazilian (incl. .com variant)
    "jornal mais bragança", "jornal mais braganca",  # jornalmaisbragança
    "jornalmaisbragan",              #   one-string variant
    "debatejuridico", "debate jurídico", "debate juridico",   # debatejuridico
    "revistacobertura", "revista cobertura",      # revistacobertura
    "hipernoticias", "hipernotícias", "hnt.com.br",  # hnt.com.br / Hipernotícias
    "imaranhese", "imaranhense",     # imaranhese.com — regional Maranhão (incl. spelling variant)
    "quatrorodas", "quatro rodas",   # quatrorodas.abril.com.br — cars magazine
    "muitainformacao", "muita informação", "muita informacao",  # muitainformacao.com.br
    "jornalpanoramaminas", "jornal panorama minas",  # jornalpanoramaminas.com.br
    "revistasegurancaeletronica", "revista segurança eletrônica",
    "revista seguranca eletronica",  # revistasegurancaeletronica.com.br
    # ── User-flagged H&E noise channels (batch 3, 2026-05-20) ──
    "sbnoticias", "sb notícias", "sb noticias",          # sbnoticias.com.br
    "agorarn", "agora rn",                               # agorarn.com.br
    "acritica.com", "acritica.net", "a crítica", "a critica",  # acritica.com / .net
    "mais.opovo", "mais opovo", "opovo mais",            # mais.opovo.com.br
    "ancora1",                                           # ancora1.com
    "ndmais", "nd mais",                                 # ndmais.com.br
    "campograndenews", "campo grande news",              # campograndenews.com.br
    "bol.uol", "bol uol", "bol notícias", "bol noticias",  # bol.uol.com.br (avoid bare "bol" — too short)
    "propmark",                                          # propmark.com.br (advertising trade)
    "correio24horas", "correio 24 horas",                # correio24horas.com.br
    "jornaltribuna", "jornal tribuna",                   # jornaltribuna.com.br
    "lide.com.br", "noticias.lide", "lide notícias", "lide noticias", "notícias lide",  # noticias.lide.com.br
    # ── User-flagged H&E noise channels (batch 4, 2026-05-21) ──
    "rede hits fm", "redehits",          # redehits.fm — small regional radio
    "reportermt", "reporter mt", "repórtermt", "repórter mt",  # reportermt.com.br — Mato Grosso (incl. accent variants)
    "clarim araxá", "clarim araxa", "clarimaraxa",  # clarimaraxa.com.br — MG small-town
    "agência sertão", "agencia sertao", "agenciasertao",  # agenciasertao.com.br — regional
    "brasil.perfil", "perfil brasil",    # brasil.perfil.com — Argentine site BR section
    "gp1.com", "gp1 notícias", "gp1 noticias", "gp1 piauí", "gp1 piaui",  # gp1.com.br — Piauí (avoid bare "gp1" — too short)
    "folha pe", "folha de pernambuco", "folhape",   # folhape.com.br
    "esportesenoticias", "esportes e noticias",  # esportesenoticias.com.br — sports
    "gazeta digital", "gazetadigital",   # gazetadigital.com.br — MT regional
    "o tempo", "otempo",                 # otempo.com.br — MG (analyst-flagged as noise for H&E)
    "folha do estado da bahia", "folhadoestadodabahia",  # BA regional
    "oeste mais", "oestemais",           # oestemais.com.br — regional
    "012 news", "012news",               # 012news.com.br
    "sampi", "sampi.net",                # sampi.net.br — Campinas/SP regional
    # ── User-flagged H&E noise channels (batch 5, 2026-05-21) ──
    # Futuro da Saúde deliberately KEPT (healthcare-specialist direct source).
    "gazeta news guarulhos", "gazetanews guarulhos",  # SP regional
    "ceará agora", "ceara agora", "cearaagora",       # CE regional
    "diarinho",                                       # Itajaí SC daily
    "conectado news", "conectadonews",                # small site
    "revista ana maria",                              # women's mag (avoid bare "ana maria" — too generic)
    "diário dos campos", "diario dos campos", "diariodoscampos",  # PR regional
    "xv curitiba", "xvcuritiba",                      # PR regional
    "cliquef5", "clique f5",                          # small site
    "portal manaus alerta", "manaus alerta", "manausalerta",  # AM regional
    "sou patos", "soupatos",                          # Patos/PB regional
    "radiomissioneira", "rádio missioneira", "radio missioneira",  # RS regional radio
    "jasb",                                           # JASB sports
    "es hoje", "eshoje",                              # Espírito Santo regional
}


def _ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    if INSECURE_ENV_FLAG:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx

_SSL = _ssl_context()


def gnews_url(query: str, lang: str, country: str, when: str = None) -> str:
    # Resolve `when` at call time so Monday's 3d window always wins
    if when is None:
        when = current_gnews_when()
    if when:
        query = f"{query} when:{when}"
    q = quote_plus(query)
    return (
        f"https://news.google.com/rss/search"
        f"?q={q}&hl={lang}&gl={country}&ceid={country}:{lang}"
    )


def _strip_source_suffix(title: str, source: str) -> str:
    """Google News titles often end with ' - Source Name'; remove it for cleaner search."""
    if not source:
        return title
    suffix = f" - {source}"
    if title.endswith(suffix):
        return title[: -len(suffix)].strip()
    return title


def _rewrite_link(link: str, title: str, source_url: str, source: str) -> str:
    """
    Google News RSS links (`https://news.google.com/rss/articles/CBMi...`) often
    fail when clicked because they require a JS-rendered redirect with consent
    cookies. Replace them with a Google search URL that reliably finds the
    article on the publisher's site.

    Direct publisher URLs (everything else) are returned unchanged — they work.
    """
    if not link.startswith("https://news.google.com/"):
        return link

    clean_title = _strip_source_suffix(title, source)
    if not clean_title:
        return link

    # Truncate so the URL doesn't get absurdly long
    short_title = clean_title[:140]

    # Extract a "site:" hint from the source URL if we have one
    site_filter = ""
    if source_url:
        try:
            from urllib.parse import urlparse
            netloc = urlparse(source_url).netloc.lower().lstrip("www.")
            if netloc and "." in netloc:
                site_filter = f" site:{netloc}"
        except Exception:
            pass

    query = f'"{short_title}"{site_filter}'
    return f"https://www.google.com/search?q={quote_plus(query)}"


def parse_items(xml_bytes: bytes) -> List[Dict]:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []
    channel = root.find("channel")
    if channel is None:
        return []
    items = []
    for it in channel.findall("item"):
        title   = (it.findtext("title") or "").strip()
        link    = (it.findtext("link") or "").strip()
        pub_raw = (it.findtext("pubDate") or "").strip()
        src_el  = it.find("source")
        source  = src_el.text.strip() if (src_el is not None and src_el.text) else ""
        # The <source url="..."> attribute gives us the publisher's homepage —
        # used to build a precise site:domain search query when rewriting links.
        source_url = src_el.attrib.get("url", "") if src_el is not None else ""

        # NOTE (2026-05-21): we used to eagerly rewrite news.google.com URLs to
        # Google search URLs here. That worked but lost the original encoded
        # link before we had a chance to resolve it to the real publisher URL.
        # Now we keep the raw news.google.com URL all the way to email render
        # time, where link_resolver.py decodes it via the Google News
        # batchexecute API. If decoding fails, email_sender falls back to a
        # Google search URL built from the headline + source domain.

        try:
            dt = parsedate_to_datetime(pub_raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except Exception:
            dt = None
        if title:
            items.append({
                "title": title, "link": link, "source": source,
                "source_url": source_url,
                "published_dt": dt, "published_raw": pub_raw,
            })
    return items


def filter_recent(items: List[Dict]) -> List[Dict]:
    # Resolve max age at call time so Monday's 72h window always wins,
    # regardless of import order anywhere in the call graph.
    max_age = current_max_age_hours()
    cutoff = datetime.now(LOCAL_TZ) - timedelta(hours=max_age)
    out = []
    for x in items:
        dt = x.get("published_dt")
        if dt is None:
            # Undated gnews item — keep with empty date marker.
            x["published_local"] = ""
            out.append(x)
            continue
        local = dt.astimezone(LOCAL_TZ)
        if local >= cutoff:
            x["published_local"] = local.strftime("%Y-%m-%d %H:%M")
            out.append(x)
        # else: parseable date older than cutoff → drop
    return out


def filter_sources(items: List[Dict]) -> List[Dict]:
    """Drop articles from aggregators/syndicators in BAD_SOURCES.
    Matching is case-insensitive substring so e.g. 'msn' blocks 'MSN',
    'MSN Noticias', 'MSN Money', etc.
    """
    out = []
    for x in items:
        src_lower = x.get("source", "").lower()
        if any(bad in src_lower for bad in BAD_SOURCES):
            continue
        out.append(x)
    return out


def dedupe(items: List[Dict]) -> List[Dict]:
    seen: set = set()
    out: List[Dict] = []
    for x in items:
        # Normalise title for dedup: lowercase, strip punctuation
        key = re.sub(r"[^\w\s]", "", x["title"].lower()).strip()
        if key not in seen:
            seen.add(key)
            out.append(x)
    return out


def fetch_bytes(url: str, timeout: int = FETCH_TIMEOUT_S) -> bytes:
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    })
    last_err = None
    for _ in range(FETCH_RETRIES):
        try:
            with urlopen(req, timeout=timeout, context=_SSL) as r:
                return r.read()
        except (ssl.SSLError, socket.timeout, socket.gaierror, OSError) as e:
            last_err = e
            sleep(0.3)
    raise last_err or RuntimeError("Unknown fetch error")


def _fetch_one(kw: str, ed: dict) -> List[Dict]:
    try:
        url  = gnews_url(kw, lang=ed["lang"], country=ed["country"])
        xml  = fetch_bytes(url)
        rows = parse_items(xml)
        rows = filter_recent(rows)
        rows = filter_sources(rows)
        for r in rows:
            r["keyword"]         = kw
            r["edition_lang"]    = ed["lang"]
            r["edition_country"] = ed["country"]
            r["source_type"]     = "gnews"
        return rows
    except Exception as e:
        print(f"\n  [WARN] gnews '{kw}' [{ed['country']}] -> {e}", file=sys.stderr)
        return []


def run() -> List[Dict]:
    tasks    = get_query_tasks()
    total    = len(tasks)
    all_rows = []
    done     = 0
    hung     = 0

    print(f"  Google News: {total} queries, {MAX_WORKERS} threads", flush=True)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_fetch_one, kw, ed): (kw, ed) for kw, ed in tasks}
        for future in as_completed(futures):
            done += 1
            pct  = int(done / total * 100)
            kw, ed = futures[future]
            label  = f"{kw[:28]:<28} [{ed['country']}]"
            try:
                rows = future.result(timeout=PER_TASK_TIMEOUT)
                all_rows.extend(rows)
            except Exception:
                hung += 1
            print(
                f"\r  Google News  [{pct:3d}%]  {done}/{total}  {label}"
                f"  (+{len(all_rows)} raw)",
                end="", flush=True,
            )

    print()
    if hung:
        print(f"  [note] {hung} queries skipped (timeout/error)")
    deduped = dedupe(all_rows)
    print(f"  -> {len(deduped)} unique headlines (from {len(all_rows)} raw)")
    return deduped


if __name__ == "__main__":
    rows = run()
    print(f"\nSample:")
    for r in rows[:5]:
        print(f"  [{r['source']}] {r['title'][:80]}")
