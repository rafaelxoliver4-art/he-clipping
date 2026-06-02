# claude_reasoning.py — Claude API reasoning layer
# Job 1: Categorize and rank headlines into the report structure
# Job 2: Fetch upcoming earnings/events via web search
#
# Auth priority:
#   1. ANTHROPIC_API_KEY in env  → direct API call (billed separately)
#   2. No API key                → Claude Code CLI using Max plan subscription

import json
import os
import re
import subprocess
import urllib.request
import urllib.error
from datetime import datetime
from typing import List, Dict, Tuple

from config import SECTORS, LOCAL_TZ, MAX_DIGEST_ITEMS
from wiki_context import ANALYST_CONTEXT

API_URL    = "https://api.anthropic.com/v1/messages"
MODEL      = "claude-sonnet-4-6"

# Claude Code CLI — used as fallback when ANTHROPIC_API_KEY is not set.
# Runs against the user's Max plan subscription (no extra billing).
CLAUDE_CLI = r"C:\Users\Rafael\AppData\Roaming\Claude\claude-code\2.1.111\claude.exe"

# ── Covered universe flat list ────────────────────────────────────────────────
COVERED_NAMES = []
for _data in SECTORS.values():
    COVERED_NAMES.extend(_data["covered"])
COVERED_NAMES = list(dict.fromkeys(COVERED_NAMES))

# ── CLI call helper (Max plan, no API key required) ───────────────────────────
def _find_claude_exe() -> str:
    """
    Return the path to claude.exe from the VS Code extension install.
    This is a real Windows filesystem path accessible from any process context
    (unlike AppData\\Roaming\\Claude\\claude-code which is a Store-app VFS overlay).
    Raises RuntimeError if not found.
    """
    import glob as _glob
    ext_dir = os.path.join(os.path.expanduser("~"), ".vscode", "extensions")
    pattern = os.path.join(ext_dir, "anthropic.claude-code-*",
                           "resources", "native-binary", "claude.exe")
    matches = sorted(_glob.glob(pattern))   # sorted → latest version last
    if not matches:
        raise RuntimeError(
            f"claude.exe not found under {ext_dir}/anthropic.claude-code-*. "
            "Please install the Claude Code VS Code extension."
        )
    return matches[-1]


def _call_claude_cli(user_message: str, system: str,
                     timeout: int = 180,
                     tools: str = "") -> str:
    """
    Invoke the Claude Code CLI in non-interactive print mode.

    Uses file-based stdin/stdout (not pipes) to avoid Windows named-pipe
    buffer deadlocks with large prompts (200 KB+).  Both stdin and stdout are
    routed through temp files so claude.exe never blocks on buffer back-pressure.
    """
    import tempfile

    claude_exe = _find_claude_exe()

    # Windows CreateProcess has a ~32K char limit for the entire command line.
    # When the system prompt is small, pass it as a CLI arg (cleanest separation —
    # model follows JSON instructions more reliably). When it's large (after we
    # inject ANALYST_CONTEXT + watchlist + topics + style examples), fold it into
    # stdin instead. The model is still instructed correctly, just framed as
    # "<<< SYSTEM >>>" / "<<< USER >>>" delimiters in one stdin payload.
    SAFE_ARG_THRESHOLD = 6000   # well under Windows CMD limit, leaves headroom

    if len(system) > SAFE_ARG_THRESHOLD:
        # Fold system into stdin with explicit delimiters
        combined = (
            "<<< SYSTEM INSTRUCTIONS — follow exactly >>>\n"
            f"{system}\n\n"
            "<<< END SYSTEM INSTRUCTIONS >>>\n\n"
            "<<< USER MESSAGE >>>\n"
            f"{user_message}"
        )
        cmd = [claude_exe, "-p", "--output-format", "text", "--no-session-persistence"]
        user_bytes = combined.encode("utf-8")
    else:
        cmd = [claude_exe, "-p", "--output-format", "text", "--no-session-persistence",
               "--system-prompt", system]
        user_bytes = user_message.encode("utf-8")

    if tools:
        cmd += ["--tools", tools]

    tmp_in  = tmp_out = tmp_err = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix="_in.txt")  as f:
            f.write(user_bytes);  tmp_in  = f.name
        with tempfile.NamedTemporaryFile(delete=False, suffix="_out.txt") as f:
            tmp_out = f.name
        with tempfile.NamedTemporaryFile(delete=False, suffix="_err.txt") as f:
            tmp_err = f.name

        with open(tmp_in,  "rb") as fin, \
             open(tmp_out, "wb") as fout, \
             open(tmp_err, "wb") as ferr:
            proc = subprocess.run(
                cmd,
                stdin=fin,
                stdout=fout,
                stderr=ferr,
                timeout=timeout,
            )

        with open(tmp_out, encoding="utf-8", errors="replace") as f:
            stdout = f.read().strip()
        with open(tmp_err, encoding="utf-8", errors="replace") as f:
            stderr = f.read()

        # Save raw output for debugging (overwritten each run)
        try:
            debug_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "output", "claude_raw_output.txt"
            )
            os.makedirs(os.path.dirname(debug_path), exist_ok=True)
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(f"exit={proc.returncode}\n---STDOUT---\n{stdout}\n---STDERR---\n{stderr}")
        except OSError:
            pass

    finally:
        for p in [tmp_in, tmp_out, tmp_err]:
            if p:
                try: os.unlink(p)
                except OSError: pass

    if not stdout:
        raise RuntimeError(
            f"claude CLI returned no output (exit {proc.returncode}).\n"
            f"stderr: {stderr[:400]}"
        )
    return stdout

# ── API call helper (direct API, requires ANTHROPIC_API_KEY) ─────────────────
def _call_claude_api(messages: List[Dict], system: str,
                     tools: List[Dict] = None,
                     max_tokens: int = 2000,
                     use_web_search: bool = False) -> Dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    payload = {
        "model":      MODEL,
        "max_tokens": max_tokens,
        "system":     [
            {
                "type": "text",
                "text": system,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        "messages": messages,
    }
    if tools:
        payload["tools"] = tools

    data = json.dumps(payload).encode()
    headers = {
        "Content-Type":      "application/json",
        "x-api-key":         api_key,
        "anthropic-version": "2023-06-01",
        "anthropic-beta":    "prompt-caching-2024-07-31",
    }
    if use_web_search:
        headers["anthropic-beta"] += ",web-search-2025-03-05"

    req = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"Claude API HTTP {e.code}: {body[:400]}") from e

# ── Legacy shim — keeps old call sites working ────────────────────────────────
def _call_claude(messages: List[Dict], system: str,
                 tools: List[Dict] = None,
                 max_tokens: int = 2000,
                 use_web_search: bool = False) -> Dict:
    return _call_claude_api(messages, system, tools, max_tokens, use_web_search)


def _extract_text(response: Dict) -> str:
    return "".join(
        block.get("text", "")
        for block in response.get("content", [])
        if block.get("type") == "text"
    )


def _clean_json(raw: str) -> str:
    """Strip markdown fences and leading/trailing whitespace."""
    text = raw.strip()
    text = re.sub(r"^```[a-z]*\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    # Extract first JSON object/array if there's surrounding text
    m = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    return m.group(0) if m else text


# ── Job 1: Curate the daily news clipping ─────────────────────────────────────
CATEGORISE_SYSTEM = f"""You are a senior LatAm Healthcare & Education (H&E) equity
research analyst at UBS.
Your job: read a numbered list of today's scraped news headlines and produce a
tight, high-signal daily news clipping — the top {MAX_DIGEST_ITEMS} most material items,
curated with analyst judgment and grouped by sector. This is the "News Clipping" format
from the H&E Online Observer editorial spec — not an analytical note.

{ANALYST_CONTEXT}

---

SECTORS — use EXACTLY these JSON keys (omit any sector with zero material items):
- "Hospitals and Health Services"
- "Health Plans"
- "Diagnostics"
- "Pharma"
- "Higher Education"
- "Cross-cutting (GLP-1)"           ← weight-loss-drug stories with multi-sector read-across
- "Epidemiology / Public Health"    ← outbreaks (dengue, flu, zika, COVID, sarampo) → HAPV MLR / RDOR utilization / FLRY tests / BLAU pharma
- "General Regulatory / Macro"      ← ANS/MEC/ANVISA/STF rulings, tax reform, macro
- "Sell-side"                       ← broker rating changes / TP revisions / initiations

TAG CONVENTION — the "ticker" field is the short label shown before each headline.

COVERED TICKER ALIASES — use these EXACT short forms:
  RDOR    = Rede D'Or São Luiz
  ONCO    = Oncoclínicas
  HAPV    = Hapvida (post-GNDI integration)
  ODPV    = Odontoprev
  SAUD    = Bradsaúde
  FLRY    = Fleury
  BLAU    = Blau Farmacêutica
  YDUQ    = YDUQS (Estácio)
  COGN    = Cogna (Kroton / Vasta / Saber)
  ANIM    = Ânima (Inspirali)
  AFYA    = Afya (NASDAQ-listed)
  LAUR    = Laureate (NASDAQ-listed)

PEER TICKER ALIASES — short forms for Brazilian peers only:
  DASA       = Dasa (integrated hospital + lab peer to RDOR / FLRY)
  Einstein   = Hospital Albert Einstein (premium hospital peer)
  Sírio      = Hospital Sírio-Libanês (premium hospital peer)
  Mater Dei  = Mater Dei hospital chain
  SulAmérica = SulAmérica saúde (payer peer to HAPV / SAUD)
  Amil       = Amil (payer peer to HAPV / SAUD)
  Porto      = Porto Saúde (payer peer to HAPV / SAUD)
  Unimed     = Unimed cooperative system
  Eurofarma, EMS, Hypera, Aché, Cristália — Brazilian pharma peers (BLAU)
  Cruzeiro   = Cruzeiro do Sul (higher-ed peer to YDUQ / COGN)

US PEERS ARE NOT IN SCOPE for this pipeline. Do NOT tag with US tickers
(UNH, HCA, LLY, NVO, DGX, LH, ATGE, STRA, etc.). If a US story has a clear
Brazilian read-across, tag with the affected covered ticker and explain the
mechanism in the headline phrasing — do not give a US-only story its own slot.

REGULATOR / AGENCY tags (use these when a story is regulator-driven with no
single-company angle yet):
  ANS     = health-plan regulator   | MEC     = education regulator
  ANVISA  = drug/device regulator   | FNDE    = textbook procurement (Cogna/Vasta)
  STF / STJ = Supreme courts        | FIES / PROUNI = student-financing programs
  SUS     = public health system

MULTI-TICKER — when a story DIRECTLY affects 2–3 covered names, join with "/":
  "HAPV/RDOR"        — payer-provider story affecting both
  "YDUQ/COGN/ANIM"   — MEC EAD ruling affecting multiple higher-ed names
  "AFYA/LAUR"        — NASDAQ-listed pair (USD-BRL or US higher-ed comp)
  "HAPV/SAUD"        — payer-specific regulatory story
  Limit to 3 tickers max. Do not multi-tag just because two names appear — only when
  both names have a clear, named investment angle in the headline.

TAG PRIORITY ORDER:
  1. COVERED TICKER(S) — when the story is directly about or clearly reads across to covered name(s)
  2. PEER SHORT FORM — when a non-covered peer dominates and has a named read-across
  3. REGULATOR TAG (ANS/MEC/ANVISA/STF/STJ) — for regulatory/macro with no single-company angle
  4. THEME — title case: GLP-1, M&A, EAD, Vagas Medicina, Reforma Tributária, Judicialização
  5. "Sector" — last resort

READ-ACROSS TAG STYLE: when the headline is about a Brazilian peer but the investment
angle is a covered name, lead with the covered ticker: "HAPV: DASA: Dasa launches
premium telemedicine plan" means HAPV is the investment angle even though the story
is about Dasa. Only use when the read-across is explicit and direct, and the peer
is Brazilian. US peer stories are out of scope — drop them.

OUTPUT FORMAT — return ONLY valid JSON, no markdown fences, no preamble.
Each item MUST include the "date" field — copy it verbatim from the input
(the value shown in parentheses after the source name in the headline list).
If the input has no date in parentheses for that item, use "" (empty string).

DO NOT include a "link" field — link plumbing is handled by the code,
not by you. Focus on triage and tagging only.

{{
  "Hospitals and Health Services": [
    {{"ticker": "RDOR",       "headline": "exact headline text", "source": "Source Name", "date": "2026-05-19 14:30"}},
    {{"ticker": "HAPV/RDOR",  "headline": "...",                 "source": "...",         "date": "2026-05-19"}},
    {{"ticker": "Sector",     "headline": "...",                 "source": "...",         "date": ""}}
  ],
  "Health Plans": [...],
  "Higher Education": [...],
  "Cross-cutting (GLP-1)": [
    {{"ticker": "HAPV", "headline": "ANS opens consultation on GLP-1 coverage in rol",
      "source": "Valor", "date": "2026-05-19 09:15"}}
  ],
  "Sell-side": [
    {{"ticker": "HAPV", "headline": "Hapvida upgraded to Buy from Neutral at Itaú BBA",
      "source": "...", "date": "2026-05-19"}}
  ]
}}

CURATION RULES:
0. SOURCE DISCIPLINE — STRICT, NON-NEGOTIABLE:
   Each input line is tagged <DIRECT> or <EXT> at the start.
   - <DIRECT> = item came from our curated reliable-source list. PREFER THESE.
   - <EXT>    = item came from Google News only (random outlet, less trusted).

   RULES — <DIRECT> items:
   - MULTI-PASS SCAN: do at least THREE passes over the DIRECT items before
     finalising:
       Pass 1 — covered-name hits: every DIRECT item whose title contains a
                covered company NAME, SUBSIDIARY, or TICKER must be flagged
                for INCLUSION. Subsidiaries: Estácio→YDUQ, Kroton/Vasta→COGN,
                Notre Dame Intermédica/GNDI→HAPV, Inspirali→ANIM, Anhembi→LAUR,
                Telcel/Telmex/Claro→AMX, Tigo→TIGO, KaBuM/Magalu→MLAS, etc.
       Pass 2 — material sector/regulator news: ANS/Anvisa/MEC/Inep/CADE/
                Anatel/IFT decisions, M&A in sector, peer earnings.
       Pass 3 — sell-side coverage: BTG/Itaú/XP/Bradesco BBI views on
                covered names.
   - VIP SOURCES — Valor (Saúde, Educação, Econômico, Pipeline) and O Globo
     are the HIGHEST-TRUST direct sources. If a covered-name story appears
     from these, it is ALMOST CERTAINLY material. NEVER skip a Valor/O Globo
     item that mentions a covered name or its subsidiaries.
   - You MUST include every DIRECT item that meets the MATERIALITY BAR.
     Do not skip a material DIRECT item because you "already have enough"
     in that sector.
   - HARD RULE (added 2026-05-25): if a <DIRECT> item's title contains the
     NAME, SUBSIDIARY or TICKER of any covered company, you MUST include
     it. This rule overrides every other consideration — materiality bar,
     sector balance, digest size, even your own judgment. Missing such an
     item = SYSTEM FAILURE. The code also enforces this server-side as a
     safety net (any item you miss will be force-added in a "Forced
     inclusion" section), but you should never make the safety net work
     — pick them yourself.
   - CORE RULE: if a story is MATERIAL to a covered name, include it.
     Materiality (not novelty, not theme freshness) is the only test.
   - SAME EVENT, multiple outlets → include only ONE (the most specific /
     most authoritative). Example: 5 outlets reporting "ANS approves GLP-1
     in Rol" → pick the ANS Notícias version. Don't repeat the same event.
   - Two genuinely different material stories that happen to share a theme
     → both go in. Two outlets running the same wire-service story → one.
   - Specialist health press (MedicinaS/A, Futuro da Saúde, Saúde Business)
     and Valor/Folha/Veja Saúde almost always beat generalist outlets for
     sector materiality. Do not down-weight them.
   - Regulator pages (ANS, Anvisa, Ministério da Saúde, MEC, Inep, CADE)
     are very high-signal: when they appear, include them unless clearly
     irrelevant to coverage.
   - JOTA, Endpoints News, Anahp are direct sources too — treat them as
     analyst-grade.

   RULES — items tagged "(date unknown)":
   - Some items have "(date unknown)" because the source didn't expose a
     publication date in its RSS/HTML. These are NOT automatically old —
     can be very fresh (regulator landing pages, association newsrooms).
   - Judge such items by title. If the title is materially relevant to a
     covered name (concrete event, named ticker, regulatory action),
     INCLUDE — analyst verifies by clicking. If generic / evergreen
     ("Trends in oncology"), DROP.
   - Same DIRECT/EXT discipline applies.

   RULES — <EXT> items:
   - You MAY include AT MOST 2 <EXT> items TOTAL across the entire digest.
     Lowered from 5 on 2026-05-22 — analyst flagged noise from non-reliable
     outlets in H&E clipping. Be ruthless: an EXT item must be an obvious,
     unambiguous hit on a covered name to make it past this cap.
   - An <EXT> item is allowed ONLY if it is EXTREMELY material to a covered
     name — e.g. covered-ticker M&A, ANS/Anvisa/MEC decision with concrete
     mechanism, GLP-1 pricing/access shift, hospital network event, oncology
     pipeline data a sophisticated H&E analyst would flag immediately.
   - Generic sector color, opinion, lifestyle pieces, or "interesting but
     soft" stories from <EXT> MUST be dropped.
   - If unsure whether an <EXT> item meets the bar, DROP IT. Default = exclude.
   - This rule supersedes everything else: even if an <EXT> story looks
     compelling, the 5-item cap holds and code will trim overage anyway.

1. AT MOST {MAX_DIGEST_ITEMS} items total across all sectors. Fewer is fine. Uneven
   distribution is EXPECTED — some sectors may have 15, others 0. Distribution follows
   materiality, not equality.
2. Omit a sector entirely if nothing in it is material — do not emit empty arrays.
3. DISCARD: duplicates of the same story across outlets, PR puff, sports, entertainment,
   general politics with no H&E angle, lifestyle filler, old pinned posts, ads.
4. INCLUDE sector-level news even when no covered company is named — ANS/MEC/ANVISA
   rulings, court decisions on judicialização, tax-reform updates for healthcare/
   education, peer earnings with clear read-across (UNH/HCA/LLY/ATGE class). This is
   where analyst judgment matters — keyword filters miss these.
5. One story → one sector (pick the most specific, actionable match).
6. Keep the headline EXACTLY as given. Do NOT translate or paraphrase. Language stays
   original (pt-BR / en).
7. Preserve the "date" field exactly as received (the value in parentheses
   after the source name in the input). If no date in parentheses, use "".
   Never invent dates. Do NOT emit a "link" field — code handles links.
8. Within each sector: order by materiality, most important first.
9. Prefer covered-ticker stories over peer stories; prefer fresh material events
   (M&A, regulatory decisions, new disclosures) over general sector color.

MATERIALITY BAR — include a story only if at least ONE is true:
- Direct M&A / strategic deal / regulatory event for a covered name
- Peer result or announcement with a clear read-across to a covered name (UNH/HCA/LLY/NVO/ATGE...)
- ANS / MEC / ANVISA / STF / STJ ruling with a concrete mechanism to a covered stock
- GLP-1 development that reframes payer-cost or hospital-procedure economics
- New medicine-vagas authorization or rejection (YDUQ/ANIM/AFYA/COGN/LAUR)
- Reforma tributária development with named transmission to H&E names
- Sector consolidation / new entrants / competitive dynamics in covered markets
- Story affects the competitive NARRATIVE or valuation multiple for a covered name,
  even if direct financial impact is uncertain (e.g., AI-driven diagnostic disruption,
  GLP-1 share-of-script milestones, vertical-integration debate)

REASONING DISCIPLINE — for EVERY headline you keep, you must be able to silently answer:
"Which covered ticker does this affect, and how?" If you cannot answer with a specific
named transmission mechanism, OMIT it. Volume of input does not justify volume of output —
many sources (general financial wires, macro feeds) will produce headlines with NO
H&E investment angle. Reject those even if they look "healthcare-related" or
"education-related".

ALWAYS OMIT (never include as a clipping item):
- Routine fines below ~R$10mn with no thesis implication
- Debt tender offers / liability management (no P&L read-across) — EXCEPTION: include in
  Sell-side section if a broker published a note as a result
- CSR / ESG / community-health / scholarship-PR with no financial mechanism
- Legislative committees presenting agendas (no concrete measure passed yet)
- General hospital-bed or doctors-per-capita statistics without operator angle
- Sports, entertainment, lifestyle, celebrity-health stories

- ⚠ COVERED-NAME EARNINGS COVERAGE — OMIT (this is the ONLY thing being filtered here).
  Rafael already tracks results directly for every covered company (RDOR, ONCO, HAPV,
  ODPV, SAUD, FLRY, BLAU, YDUQ, COGN, ANIM, AFYA, LAUR). This rule applies STRICTLY
  to earnings/results stories. It does NOT touch general corporate news.

  DROP these (covered name + earnings angle is the headline's main subject):
    • "Q1/Q2/Q3/Q4 results", "earnings", "EBITDA beat/miss", "captação sobe", "MLR sobe"
    • "Earnings preview", "earnings reaction", "earnings recap", "post-earnings"
    • Generic price-action commentary tied to results ("X sobe/cai após resultado")
    • Analyst notes recapping results without a NEW rating/TP action

  KEEP these even when the subject is a covered name (NOT routine results coverage):
    • ★ ALL non-results corporate news — M&A, hospital openings, network expansion,
      product launches, partnerships, regulatory wins/losses, court rulings, executive
      appointments outside the earnings cycle, capital raises, refinancings with
      strategic intent, new market entries, new disclosures or business segments
    • Surprise material miss/beat that re-prices the thesis
    • Guidance update or material outlook revision (margin, EBITDA, captação, MLR)
    • M&A or strategic announcement made AT earnings
    • New disclosure (segment reporting change, new KPI, capital return policy)
    • CFO / CEO transition announced at results
    • Earnings-tied broker rating changes → put in Sell-side section

- ✓ EARNINGS / RESULTS FROM BRAZILIAN PEERS — KEEP when there's named transmission:
    • Dasa results / strategy → integrated hospital+lab peer for RDOR / FLRY
    • Mater Dei results → hospital peer for RDOR
    • SulAmérica / Amil / Porto Saúde / Unimed → payer peers for HAPV / SAUD
    • Eurofarma / EMS / Hypera / Aché → pharma peers for BLAU
    • Cruzeiro do Sul → higher-ed peer for YDUQ / COGN

- ✗ US PEER RESULTS — OUT OF SCOPE. Do not include UnitedHealth / HCA /
  Quest / LabCorp / Lilly / Novo / Adtalem / etc. results recaps, even
  when frame says "read-across to Brazilian peer". The signal-to-noise on
  these is too low for our coverage focus. The ONLY US-listed exception:
  named GLP-1 regulatory or pricing events with explicit Brazilian
  transmission (ANVISA, ANS, judicialização) — those go to the
  Cross-cutting (GLP-1) sector tagged with the affected covered name.

  DECISION TEST: ask "is this story PRIMARILY a results recap of a covered name?"
  If YES → OMIT. If NO (anything else, including general news about a covered name,
  or any peer story) → evaluate normally on materiality.

Anything else: OMIT.

SELL-SIDE SECTION — include ONLY:
- Broker rating changes (upgrade/downgrade) for any covered or closely related name
- Target price revisions with explicit old→new TP or directional flag
- New analyst initiations on covered names or direct peers
- Do NOT include research notes without a rating/TP action"""


def _inject_watchlist(base_system: str) -> str:
    """
    Append per-run learning context to the base system prompt.

    Three layers, in priority order:
      1. RAFAEL'S ANALYTICAL ANGLES per covered name — extracted from his
         published Observer notes. Shows WHAT he writes about per ticker, not
         just topic frequency. Tells Claude the SUBJECT MATTER and ANALYTICAL
         LENS he uses. (Strongest signal — most-recent notes refresh on every
         run via the Observer file cache.)
      2. Auto-discovered topics (topics.py — scored, decayed, no human input)
      3. Manual watchlist (watchlist.py — optional override, only if file exists)
    """
    extras: List[str] = []

    # 1. Observer-derived per-ticker angles (the strongest learning signal)
    try:
        from observer_corpus import build_per_ticker_angles_block
        angles = build_per_ticker_angles_block()
        if angles:
            extras.append(angles)
    except Exception as e:
        print(f"  [WARN] per-ticker angles injection skipped: {e}")

    # 2. Auto-discovered topics scoreboard
    try:
        from topics import build_prompt_injection as build_auto_topics
        auto = build_auto_topics()
        if auto:
            extras.append(auto)
    except Exception as e:
        print(f"  [WARN] auto-topic injection skipped: {e}")

    # 3. Manual watchlist override (optional)
    try:
        from watchlist import build_watchlist_text
        manual = build_watchlist_text()
        if manual:
            extras.append(manual)
    except Exception as e:
        print(f"  [WARN] manual watchlist injection skipped: {e}")

    if extras:
        return base_system + "\n\n" + "\n\n".join(extras)
    return base_system


def categorise_headlines(claude_input: str) -> Dict:
    """Send headline list to Claude → returns {sector: [{ticker, headline, source, link}]}."""
    today = datetime.now(LOCAL_TZ).strftime("%B %d, %Y")
    user_message = (
        f"Today is {today}.\n\n"
        "Here are today's news headlines (format: [pre-assigned sector] Source: Title [lang]):\n\n"
        f"{claude_input}\n\n"
        "Categorise them, pick the most material ones, and return the JSON report."
    )

    # Inject the current watchlist (manual + auto) at call time so vault edits
    # propagate immediately to the very next run.
    system_with_watchlist = _inject_watchlist(CATEGORISE_SYSTEM)

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        # Direct API path (billed separately)
        resp     = _call_claude_api([{"role": "user", "content": user_message}],
                                    system_with_watchlist, max_tokens=4000)
        raw_text = _extract_text(resp)
    else:
        # CLI path — uses Max plan subscription, no extra billing
        raw_text = _call_claude_cli(user_message, system_with_watchlist, timeout=1500)

    try:
        return json.loads(_clean_json(raw_text))
    except json.JSONDecodeError:
        return {"_raw": raw_text}


# ── Job 2: Upcoming earnings & events ─────────────────────────────────────────
EVENTS_SYSTEM = """You are a financial research assistant.
Search the web and return a JSON array of upcoming earnings dates, investor days,
product launches, and relevant TMT sector conferences.

Return ONLY a valid JSON array — no markdown, no explanation:
[
  {"date": "YYYY-MM-DD", "ticker_or_name": "VTEX",   "event": "Q1 2025 Earnings"},
  {"date": "YYYY-MM-DD", "ticker_or_name": "Sector", "event": "MWC Barcelona 2025"}
]

Rules:
- Events in the NEXT 60 days only.
- Omit events you cannot confirm with a specific date.
- Use ticker symbol when available; otherwise company name.
- "event" descriptions: max 8 words.
- Sort by date ascending."""

WEB_SEARCH_TOOL = [{"type": "web_search_20250305", "name": "web_search"}]


_EVENTS_CACHE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "output", "events_cache.json"
)
_EVENTS_CACHE_TTL_H = 20  # skip re-fetch if cache is fresher than this


def _load_events_cache() -> List[Dict]:
    """Return cached events if they are less than _EVENTS_CACHE_TTL_H hours old."""
    if not os.path.exists(_EVENTS_CACHE_PATH):
        return []
    try:
        mtime = datetime.fromtimestamp(os.path.getmtime(_EVENTS_CACHE_PATH), tz=LOCAL_TZ)
        age_h = (datetime.now(LOCAL_TZ) - mtime).total_seconds() / 3600
        if age_h > _EVENTS_CACHE_TTL_H:
            return []
        with open(_EVENTS_CACHE_PATH, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return []


def _save_events_cache(events: List[Dict]) -> None:
    os.makedirs(os.path.dirname(_EVENTS_CACHE_PATH), exist_ok=True)
    try:
        with open(_EVENTS_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def fetch_upcoming_events() -> List[Dict]:
    """Use Claude + web search to find upcoming earnings/events.
    Results are cached for _EVENTS_CACHE_TTL_H hours to avoid redundant API calls.
    """
    cached = _load_events_cache()
    if cached:
        print(f" (cached, {len(cached)} events)", end="", flush=True)
        return cached

    universe_str = ", ".join(COVERED_NAMES)
    today_str    = datetime.now(LOCAL_TZ).strftime("%B %d, %Y")
    user_message = (
        f"Today is {today_str}. "
        f"Search for upcoming earnings dates, investor days, product launches, "
        f"and major TMT/telecom/tech conferences in the next 60 days for: {universe_str}. "
        "Return a JSON array as specified."
    )

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    try:
        if api_key:
            # Direct API with web-search beta
            resp     = _call_claude_api([{"role": "user", "content": user_message}],
                                        EVENTS_SYSTEM,
                                        tools=WEB_SEARCH_TOOL, max_tokens=1500,
                                        use_web_search=True)
            raw_text = _extract_text(resp)
        else:
            # CLI with WebSearch tool enabled
            raw_text = _call_claude_cli(user_message, EVENTS_SYSTEM,
                                        tools="WebSearch", timeout=180)

        events = json.loads(_clean_json(raw_text))
        events.sort(key=lambda e: e.get("date", "9999"))
        _save_events_cache(events)
        return events
    except Exception as e:
        print(f"\n  [WARN] Events fetch failed: {e}")
        return []


# ── Job 3: Write analytical notes for top curated items ───────────────────────
NOTE_WRITER_CONTEXT = """
## NOTE FORMAT — match this exactly (sourced from tmt-report-format.md)

📍 [TICKER(s)]: [Headline — frames investment relevance for the stock, not just the event]

What happened:

• [Opening bullet — pick the matching opener verbatim:]
   - "According to [Source], [company] announced [event]."
   - "Management noted at [event/call] that..."
   - "At [event/conference], [person/company] [stated/highlighted/noted that]..."
   - "We met with [company/person] to discuss [topic]. Key takeaways were:"
   - "In a note by [Analyst Name], [team] reviewed [doc] to assess [topic]. Key takeaways were:"

• **[Bold sub-header — sentence case, 4–8 words, compresses the bullet's idea]:** [2–4 sentences. Factual. Attributed. One idea per bullet.]

• **[Bold sub-header]:** [2–4 sentences. Factual. Attributed.]

[1–4 content bullets total. Never invent data not visible in the source.]

🔎 UBS's take:

[Signal] read for [TICKER(s)]. [3–6 sentences. Analysis only — never restate the factual section.
Why it matters for the stock. Close with a forward-looking point or monitoring flag.]

DIRECTIONAL SIGNAL VOCABULARY (use one):
- Positive / Slightly positive
- Neutral
- Mixed read / Mixed but skewed [positive/negative]
- Slightly negative / Negative
- "Doesn't move the needle" — when impact is real but immaterial at the stock level

SUB-HEADER EXAMPLES (sentence case, 4–8 words, conveys the idea):
- **Claro/Desktop overhang addressed directly:**
- **Effects deferred to 2027; broader precedent potential:**
- **CCB growth missed the bonus target, but FCF beat saved full payout:**
- **AI lowers the cost to build, shifts the edge to problem understanding:**

WRITING RULES:
- ★ LANGUAGE: ALL note content (headline, "What happened" bullets, sub-headers,
  "UBS's take") MUST be in ENGLISH. The article title in the clipping section
  retains its original language (Portuguese for BR sources), but YOUR note framing
  is always English. When citing a Portuguese article, summarize the relevant
  point in English; never copy/paste the Portuguese headline as your note headline.
- Brevity over completeness. Fewer words = better when meaning is preserved.
- Factual section: 100% grounded in the article. No inferences. Attribute everything.
- Take section: hedging required (may, might, could, suggest, indicate, in our view, we believe).
  Never assert certainty. Never restate facts. Cross-reference prior views with
  "as we previously highlighted" or "consistent with our view".
- BANNED phrases: "rather than", "linger", "long-term platform enabler", "DIY", "UI", "SoR"
- Numbers: bn/mn (not B/M); ~X% for approximations; ppts (percentage points); bps (basis points)
- Multiples: [xx]x P/E (vs. [xx]x L3Y avg.)
- Periods: MoM, YoY, QoQ, LTM (Last Twelve Months), fwd (forward) — standard abbreviations OK
"""

NOTE_SYSTEM = f"""You are a senior LatAm TMT equity research analyst at UBS writing the TMT Online Observer daily note.

{ANALYST_CONTEXT}

{NOTE_WRITER_CONTEXT}

TASK: You receive today's curated news clipping as JSON. Select the 1–2 most material items
and write a full note for each. For each selected item, search the web to read the actual
article first, then write the note in the format above.

DEFAULT TO WRITING. Aim for 2 notes per day, 1 if material is thin, ZERO only if the
clipping is genuinely empty of anything worth a take. The reader expects daily takes.

⚠ LANGUAGE RULE — WRITE THE ENTIRE NOTE IN ENGLISH.
The note headline (📍 line), all "What happened" bullets, sub-headers, and the
"UBS's take" must be in ENGLISH regardless of the source article's language.
The article title in the clipping section stays in its original language (that's
the source's writing, not ours), but YOUR note framing is ALWAYS in English.
When you cite a Portuguese article, summarize the relevant point in English
and attribute the source. Do NOT copy/paste the Portuguese headline as your
note headline.

SELECTION PRIORITY — pick from any of these, ordered by usefulness:

  1. NON-EARNINGS NEWS ABOUT COVERED NAMES (highest priority — this is the
     core daily-clipping signal we need to convert into takes):
       • M&A / strategic deals (RDOR hospital acquisitions, ONCO clinic rollups,
         HAPV operator deals, FLRY lab-to-lab moves, BLAU contract wins, etc.)
       • ANS / MEC / ANVISA regulatory rulings, court decisions, rule changes
       • Hospital openings, network expansion announcements
       • New product / contract / partnership wins
       • Medicine-vagas authorizations or rejections (YDUQ / ANIM / AFYA / COGN / LAUR)
       • Executive appointments, board changes (outside earnings)
       • Capital raises, refinancings with strategic intent
       • New disclosure: segment reporting, KPI introduction, capital-return policy

  2. CROSS-CUTTING THEMES with Brazilian transmission:
       • GLP-1 ANVISA approvals, ANS coverage debates, judicialização rulings
       • Tax-reform updates for healthcare / education sectors
       • MEC EAD policy shifts, FIES / PROUNI / Pé-de-Meia program changes
       • STF / STJ rulings on healthcare / education matters

  3. BRAZILIAN PEER EVENTS with clear read-across to a covered name:
       • Dasa, Mater Dei, SulAmérica, Amil, Eurofarma, Cruzeiro do Sul, etc.
       • Only when there's a NAMED transmission to a covered ticker

  4. EARNINGS-EXCEPTION ITEMS for covered names — write these only when the
     story is genuinely about ONE of these, not a routine recap:
       • Surprise material miss/beat that re-prices the thesis
       • Guidance update or material outlook revision (margin, EBITDA, captação, MLR)
       • Strategic announcement made AT earnings
       • CFO/CEO transition announced at results

WHAT NOT TO WRITE (out of scope — drop entirely):
  • Routine quarterly earnings recaps of covered names ("HAPV Q1 MLR beats", etc.)
  • Generic post-earnings price-action commentary
  • Earnings previews for covered names
  • US peer results (UnitedHealth, HCA, Lilly, Novo, Adtalem etc.) WITHOUT
    explicit Brazilian transmission — these are not in our coverage focus

OUTPUT — return ONLY a valid JSON array of note strings, one string per note:
["full note 1 text", "full note 2 text"]

If only 1 item clears the bar: ["full note text"].
Returning [] is acceptable only when EVERY item in the clipping is either a routine
earnings recap (which we filter) or trivial sector color. Default to writing."""


def write_top_notes(report: Dict, max_notes: int = 2) -> List[str]:
    """
    Pick the top items from the curated report and write full analytical notes.
    Uses web search to read each article before writing the take.
    """
    import json as _json

    # Build a simplified view of the clipping for the prompt
    items_for_claude = []
    for sector, items in report.items():
        if sector == "_raw" or not isinstance(items, list):
            continue
        for item in items:
            items_for_claude.append({
                "sector": sector,
                "ticker": item.get("ticker", ""),
                "headline": item.get("headline", ""),
                "source": item.get("source", ""),
                "link": item.get("link", ""),
            })

    if not items_for_claude:
        return []

    today = datetime.now(LOCAL_TZ).strftime("%B %d, %Y")
    user_message = (
        f"Today is {today}.\n\n"
        f"Here is today's curated news clipping (JSON):\n\n"
        f"{_json.dumps(items_for_claude, ensure_ascii=False, indent=2)}\n\n"
        f"Select up to {max_notes} of the most material items per the SELECTION PRIORITY "
        f"in your instructions. Default to writing — regulatory decisions, M&A, strategic "
        f"announcements, hospital openings, medicine-vagas authorizations, ANS/MEC/ANVISA "
        f"rulings, and product launches all qualify. Skip routine earnings recaps of covered "
        f"names and US peer earnings (out of scope). Search the web to read each selected "
        f"article before writing. Return the JSON array of notes. "
        f"REMINDER: all note content must be written in ENGLISH, including the headline. "
        f"If the source article is in Portuguese, summarize and quote attribution in English."
    )

    # Inject the current watchlist so note selection prioritizes hot topics
    note_system_with_watchlist = _inject_watchlist(NOTE_SYSTEM)

    # Inject 2-3 of Rafael's most recent REAL published notes as style anchors
    # so the writer matches his actual voice, not just the abstract format spec.
    # Live-read every call — no upload step, updates as Rafael writes.
    try:
        from observer_corpus import build_style_examples
        style_block = build_style_examples(n=3, max_chars_per_note=900)
        if style_block:
            note_system_with_watchlist += "\n\n" + style_block
    except Exception as e:
        print(f"  [WARN] Observer style examples skipped: {e}")

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    try:
        if api_key:
            resp = _call_claude_api(
                [{"role": "user", "content": user_message}],
                note_system_with_watchlist,
                tools=WEB_SEARCH_TOOL,
                max_tokens=6000,
                use_web_search=True,
            )
            raw_text = _extract_text(resp)
        else:
            raw_text = _call_claude_cli(
                user_message, note_system_with_watchlist, tools="WebSearch", timeout=300
            )

        notes = json.loads(_clean_json(raw_text))
        if isinstance(notes, list):
            return [n for n in notes if isinstance(n, str) and n.strip()]
        return []
    except Exception as e:
        print(f"\n  [WARN] Note writing failed: {e}")
        return []


# ── Learning log ──────────────────────────────────────────────────────────────
def log_run(report: Dict, notes: List[str], elapsed_s: float = 0.0) -> None:
    """
    Append this run's curated items and notes to output/learning_log.jsonl.
    The learn.py script reads this file to identify patterns and refine wiki_context.py.
    """
    log_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "output", "learning_log.jsonl"
    )
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    curated_items = []
    for sector, items in report.items():
        if sector == "_raw" or not isinstance(items, list):
            continue
        for item in items:
            curated_items.append({
                "sector": sector,
                "ticker": item.get("ticker", ""),
                "headline": item.get("headline", ""),
                "source": item.get("source", ""),
            })

    entry = {
        "date":          datetime.now(LOCAL_TZ).strftime("%Y-%m-%d"),
        "timestamp":     datetime.now(LOCAL_TZ).isoformat(),
        "elapsed_s":     round(elapsed_s, 1),
        "total_items":   len(curated_items),
        "curated_items": curated_items,
        "notes_written": notes,
    }

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"\n  [WARN] Could not write learning log: {e}")


def _count_log_runs() -> int:
    """Return the total number of pipeline runs recorded in learning_log.jsonl."""
    log_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "output", "learning_log.jsonl"
    )
    if not os.path.exists(log_path):
        return 0
    try:
        with open(log_path, encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())
    except OSError:
        return 0


# ── Public entry point ────────────────────────────────────────────────────────
def run(claude_input: str, write_notes: bool = True) -> Tuple[Dict, List[Dict], List[str]]:
    _start = datetime.now(LOCAL_TZ)

    print("  Claude: categorising headlines...", end="", flush=True)
    report = categorise_headlines(claude_input)
    print(" done")

    print("  Claude: fetching upcoming events...", end="", flush=True)
    events = fetch_upcoming_events()
    print(f" done ({len(events)} events)")

    notes: List[str] = []
    if write_notes:
        print("  Claude: writing top analytical notes...", end="", flush=True)
        notes = write_top_notes(report)
        print(f" done ({len(notes)} note{'s' if len(notes) != 1 else ''})")

    elapsed = (datetime.now(LOCAL_TZ) - _start).total_seconds()
    log_run(report, notes, elapsed)

    return report, events, notes


if __name__ == "__main__":
    sample = """  1. [Software & AI] Valor Econômico: TOTVS conclui aquisição da Linx por R$7 bilhões [pt-BR]
  2. [IT Services] Economic Times: TCS is asking staff to use AI even if it hits revenues [en]
  3. [Telecom LatAm] El Economista: AMX reporta caída de 3% en ingresos del 4T24 [es-MX]"""

    report, events, notes = run(sample)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("\nEvents:", json.dumps(events, indent=2))
    print(f"\nNotes ({len(notes)}):", notes)
