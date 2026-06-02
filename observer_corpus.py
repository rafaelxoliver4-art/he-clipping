# observer_corpus.py — Parse Rafael's published notes from
# TMT Online Observer Data.docx into structured data, then expose it as the
# HIGHEST-WEIGHT learning signal in the system.
#
# WHY THIS IS THE STRONGEST SIGNAL:
#   The Observer file contains every note Rafael actually published. It's the
#   ground truth of "what was material enough to write about." Anything we
#   curate that he writes about: confirmed material. Anything he writes about
#   that we miss: a curation gap.
#
# WHAT IT DOES:
#   1. Parses the .docx into individual notes (split on 📍 ticker markers)
#   2. Extracts ticker(s), headline, "What happened" body, "UBS's take",
#      and the directional signal (Positive / Negative / Neutral / etc.)
#   3. Caches the parsed result keyed on file mtime — only reparses when
#      Rafael edits the file
#   4. Provides query API for downstream:
#        - Ticker frequency (which names get notes)
#        - Recent notes (for style examples in the note writer prompt)
#        - Signal vocabulary (which signals he uses for which situations)
#
# WHO USES IT:
#   - topics.py:  reinforce_from_observer() boosts topics by +10 per Rafael note
#   - claude_reasoning.py:  injects 2-3 recent real notes as style anchors
#   - learn.py:  feeds structured statistics to the deep learn cycle

import json
import os
import re
import sys
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from claude_data_reader import read_docx_text, CLAUDE_DATA_DIR

# ── Paths ─────────────────────────────────────────────────────────────────────
OBSERVER_FILENAME = "H&E Online Observer Data.docx"
OBSERVER_PATH     = os.path.join(CLAUDE_DATA_DIR, OBSERVER_FILENAME)

_HERE       = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH  = os.path.join(_HERE, "output", "observer_corpus_cache.json")

# ── Note-format markers (from tmt-report-format.md spec) ──────────────────────
_NOTE_START      = "📍"
_TAKE_MARKER     = "🔎"
_WHAT_HAPPENED   = "What happened"
_TAKE_HEADER     = "UBS's take"

# Directional signal vocabulary (from spec) — captured in priority order so
# "Slightly positive" matches before "Positive"
_SIGNAL_PHRASES = [
    "Doesn't move the needle",
    "Mixed but skewed positive",
    "Mixed but skewed negative",
    "Mixed read",
    "Slightly positive",
    "Slightly negative",
    "Positive",
    "Negative",
    "Neutral",
]


# ── Cache helpers ─────────────────────────────────────────────────────────────
def _file_signature(path: str) -> str:
    """Returns 'mtime|size' — cheap signature to detect file changes."""
    try:
        st = os.stat(path)
        return f"{st.st_mtime}|{st.st_size}"
    except OSError:
        return ""


def _load_cache() -> Optional[Dict]:
    if not os.path.exists(CACHE_PATH):
        return None
    try:
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _save_cache(data: Dict) -> None:
    try:
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"  [WARN] Could not write observer cache: {e}")


# ── Note extraction ───────────────────────────────────────────────────────────
def _split_notes(full_text: str) -> List[str]:
    """
    Split the document into individual notes.

    Two formats supported (auto-detected per file):
      • STRICT (TMT-style): notes start with 📍 emoji
      • LOOSE  (H&E-style): notes start with "TICKER: headline" on their own
        line, where TICKER is a known covered/peer name. No emoji required.

    The H&E Observer file uses the LOOSE format (Rafael's actual writing
    pattern: daily sections with "Daily DD/MM" + sector headers + multiple
    "TICKER: ..." note blocks).
    """
    # STRICT format — if the file uses 📍 markers, parse that way (TMT-compat)
    if _NOTE_START in full_text:
        chunks = full_text.split(_NOTE_START)
        return [_NOTE_START + c.strip() for c in chunks[1:] if c.strip()]

    # LOOSE format — split on "TICKER: ..." lines where TICKER is recognised
    # Build the valid-ticker set from the H&E config
    valid: set = set()
    try:
        import config  # type: ignore
        for sector_data in config.SECTORS.values():
            for t in sector_data.get("covered", []):
                if t: valid.add(t.upper())
            # Also accept peer short forms that often appear as tags
            for p in sector_data.get("peers", []):
                # Only single-word uppercase peers (e.g. "DASA", "BLAU")
                pu = p.strip().upper()
                if pu and pu.isalpha() and len(pu) <= 8:
                    valid.add(pu)
    except Exception:
        pass

    if not valid:
        return []

    # Find every line that starts with TICKER: where TICKER is recognised
    pat = re.compile(r"^([A-Z][A-Z0-9/\-\.&]{1,40}?):\s", re.MULTILINE)
    starts: list = []
    for m in pat.finditer(full_text):
        candidate = m.group(1).strip().upper()
        # Accept multi-ticker tags if ANY part matches valid set
        parts = [p for p in candidate.split("/") if p]
        if any(p in valid for p in parts):
            starts.append(m.start())

    if not starts:
        return []

    # Carve out each note as text from this start position to next start
    chunks_out: list = []
    for i, pos in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(full_text)
        chunks_out.append(full_text[pos:end].strip())
    return chunks_out


def _extract_ticker(note_text: str) -> str:
    """
    Extract ticker(s) from a note's first line. Handles both formats:
      STRICT: '📍 GLOB: AI positioning...'        → 'GLOB'
      LOOSE:  'HAPV: Investor focus after Q1...'   → 'HAPV'
      Multi:  'HAPV/RDOR: ...'                     → 'HAPV/RDOR'
      Bracket:'[AMX]: ...'                         → 'AMX'
    """
    if not note_text:
        return ""
    first_line = note_text.lstrip(_NOTE_START).strip().splitlines()[0]
    m = re.match(r"^\s*\[?([A-Z][A-Z0-9/\-\.&]{0,40}?)\]?\s*:", first_line)
    return m.group(1).strip() if m else ""


def _extract_headline(note_text: str) -> str:
    """Everything after 'TICKER:' on the first line."""
    if not note_text:
        return ""
    first_line = note_text.lstrip(_NOTE_START).strip().splitlines()[0]
    if ":" in first_line:
        return first_line.split(":", 1)[1].strip()
    return first_line.strip()


# Markers that indicate the start of the "take" section, in priority order.
# Both strict (🔎 + "UBS's take") and loose ("UBS's take" alone) supported.
_TAKE_START_MARKERS = (
    _TAKE_MARKER,           # 🔎
    "UBS's take",           # bare phrase (ASCII apostrophe)
    "UBS’s take",      # bare phrase (curly apostrophe — what Word inserts)
)

# Markers that indicate the start of the "what happened" section.
# Rafael often writes "What happened?" (question) instead of "What happened:"
_WHAT_HAPPENED_MARKERS = (
    "What happened?",
    "What happened:",
    "What happened ",   # loose fallback
)


def _extract_take(note_text: str) -> str:
    """Find and return the UBS take section, terminating before the next note."""
    for marker in _TAKE_START_MARKERS:
        if marker in note_text:
            after = note_text.split(marker, 1)[1]
            # Stop at common "next-section" delimiters
            for stop in (_NOTE_START, "\nKey investor takeaway", "\nKey takeaway",
                         "\nNext Results", "\nNext Earnings"):
                if stop in after:
                    after = after.split(stop)[0]
            return after.lstrip(":").strip()
    return ""


def _extract_what_happened(note_text: str) -> str:
    """Find and return the 'What happened' section."""
    for marker in _WHAT_HAPPENED_MARKERS:
        if marker in note_text:
            after = note_text.split(marker, 1)[1]
            # Stop at take marker or next note
            for stop in _TAKE_START_MARKERS + (_NOTE_START,):
                if stop in after:
                    after = after.split(stop)[0]
            return after.lstrip(":?").strip()
    return ""


def _extract_signal(take_text: str) -> str:
    """Find which directional signal phrase Rafael used in the take."""
    if not take_text:
        return ""
    take_lower = take_text.lower()
    for phrase in _SIGNAL_PHRASES:
        if phrase.lower() in take_lower:
            return phrase
    return ""


def _parse_one_note(raw_text: str, position: int) -> Dict:
    ticker        = _extract_ticker(raw_text)
    headline      = _extract_headline(raw_text)
    what_happened = _extract_what_happened(raw_text)
    take          = _extract_take(raw_text)
    signal        = _extract_signal(take)
    return {
        "position":        position,    # ordering in file (newer notes = later)
        "ticker":          ticker,
        "tickers_split":   [t for t in ticker.split("/") if t.strip()],
        "headline":        headline[:300],
        "what_happened":   what_happened[:1500],
        "take":            take[:1500],
        "signal":          signal,
        "char_count":      len(raw_text),
    }


# ── Public API ────────────────────────────────────────────────────────────────
def parse_observer_doc(force_reparse: bool = False) -> Dict:
    """
    Parse the Observer file into structured notes. Returns:
      {
        "file_signature": "mtime|size",
        "parsed_at": iso_timestamp,
        "total_notes": int,
        "notes": [ {position, ticker, headline, ...}, ... ],
        "ticker_frequency": {TICKER: count},
        "signal_distribution": {Signal: count},
      }

    Cached on file mtime+size — only reparses when the .docx actually changes.
    """
    sig = _file_signature(OBSERVER_PATH)
    if not sig:
        return {"error": f"file not found: {OBSERVER_PATH}", "total_notes": 0,
                "notes": [], "ticker_frequency": {}, "signal_distribution": {}}

    if not force_reparse:
        cache = _load_cache()
        if cache and cache.get("file_signature") == sig:
            return cache  # cache hit — file unchanged

    # Cache miss — reparse
    full_text = read_docx_text(OBSERVER_PATH)
    if not full_text:
        return {"error": "could not read file", "total_notes": 0, "notes": [],
                "ticker_frequency": {}, "signal_distribution": {}}

    raw_notes = _split_notes(full_text)
    parsed: List[Dict] = []
    for i, raw in enumerate(raw_notes):
        note = _parse_one_note(raw, i)
        if note["ticker"]:  # skip noise / non-note 📍 occurrences
            parsed.append(note)

    # Aggregate stats
    ticker_freq: Dict[str, int] = {}
    signal_dist: Dict[str, int] = {}
    for note in parsed:
        # Count each ticker in multi-ticker tags separately
        for t in note["tickers_split"]:
            ticker_freq[t] = ticker_freq.get(t, 0) + 1
        if note["signal"]:
            signal_dist[note["signal"]] = signal_dist.get(note["signal"], 0) + 1

    # Sort dicts by frequency desc for stable downstream use
    ticker_freq = dict(sorted(ticker_freq.items(), key=lambda x: -x[1]))
    signal_dist = dict(sorted(signal_dist.items(), key=lambda x: -x[1]))

    out = {
        "file_signature":     sig,
        "parsed_at":          datetime.now().isoformat(),
        "total_notes":        len(parsed),
        "notes":              parsed,
        "ticker_frequency":   ticker_freq,
        "signal_distribution": signal_dist,
    }
    _save_cache(out)
    return out


def get_recent_notes(n: int = 5) -> List[Dict]:
    """
    Return the last N notes (by file order — assuming newer notes are
    appended at the end). Used to give Claude real style examples when
    writing a new note.
    """
    data = parse_observer_doc()
    if not data.get("notes"):
        return []
    return data["notes"][-n:]


def get_ticker_frequency() -> Dict[str, int]:
    """Map each ticker to how many notes Rafael has written about it."""
    return parse_observer_doc().get("ticker_frequency", {})


def get_signal_distribution() -> Dict[str, int]:
    """Distribution of directional signals Rafael uses."""
    return parse_observer_doc().get("signal_distribution", {})


def find_underrepresented_tickers(min_notes: int = 3,
                                  current_context: str = "") -> List[Tuple[str, int]]:
    """
    Tickers Rafael has written about ≥ min_notes times that are NOT
    explicitly mentioned in the current ANALYST_CONTEXT. These are
    blind spots in the curator.
    """
    freq = get_ticker_frequency()
    out: List[Tuple[str, int]] = []
    for ticker, count in freq.items():
        if count < min_notes:
            continue
        if not current_context or ticker.upper() not in current_context.upper():
            out.append((ticker, count))
    return out


# ── Style block builder for the note writer ───────────────────────────────────
def build_style_examples(n: int = 3, max_chars_per_note: int = 800) -> str:
    """
    Build a "real recent notes" block to inject into the note writer's prompt.
    These are Rafael's actual published notes — style ground truth.
    """
    notes = get_recent_notes(n)
    if not notes:
        return ""

    parts = [
        "### REAL RECENT NOTES (style ground truth — Rafael's actual published work)",
        "",
        "Match this voice, structure, and density. These are the most recent notes from",
        "the published Observer. Note how facts are attributed, takes are hedged, and",
        "signals are explicit.",
        "",
    ]
    for i, note in enumerate(notes, 1):
        ticker = note.get("ticker", "?")
        head   = note.get("headline", "")
        what   = note.get("what_happened", "")[:max_chars_per_note // 2]
        take   = note.get("take", "")[:max_chars_per_note // 2]
        sig    = note.get("signal", "")

        block = f"--- Example {i} | 📍 {ticker}: {head} ---\n"
        if what:
            block += f"What happened:\n{what}\n\n"
        if take:
            block += f"🔎 UBS's take:\n{take}"
        if sig:
            block += f"\n[Signal used: {sig}]"
        parts.append(block)

    return "\n\n".join(parts)


# ── Per-ticker analytical angles (the SUBJECT MATTER Rafael cares about) ────
def build_per_ticker_angles_block(top_n_tickers: int = 10,
                                  headlines_per_ticker: int = 6,
                                  include_take_snippet: bool = True) -> str:
    """
    Build a runtime-injection block that shows, per ticker, WHAT Rafael has
    been writing about — not just how many notes, but the actual angles,
    concerns, and analytical lens he uses for each name.

    This is the difference between:
      "HAPV: 13 notes" (mechanical — what we had before)
    and:
      "HAPV: Rafael's recurring concerns are MLR trajectory, balance sheet
       visibility, South operation divestment, short interest dynamics,
       court disputes on debt. When a story touches any of these → material."

    Claude reads this on EVERY pipeline run (cheap, no Claude call needed).
    """
    data = parse_observer_doc()
    if data.get("total_notes", 0) == 0:
        return ""

    # Bucket notes by individual ticker (multi-ticker tags credit each)
    by_ticker: Dict[str, List[Dict]] = {}
    for note in data["notes"]:
        for raw_t in note.get("tickers_split", []):
            # Apply same alias logic as topics.py so YDUQS rolls into YDUQ
            from topics import _normalize_name as _norm
            t = _norm(raw_t)
            if not t:
                continue
            by_ticker.setdefault(t, []).append(note)

    if not by_ticker:
        return ""

    # Sort tickers by note count
    sorted_tickers = sorted(by_ticker.items(), key=lambda x: -len(x[1]))[:top_n_tickers]

    parts = [
        "### RAFAEL'S ANALYTICAL ANGLES per covered name (from Observer notes)",
        "",
        "Below is what Rafael has ACTUALLY been writing about for each name —",
        "the recurring subjects, concerns, framing, and read-across logic he",
        "uses. Treat any incoming headline that touches these angles as MATERIAL",
        "even if the headline phrasing is different. This shows you what Rafael",
        "cares about, not just which tickers.",
        "",
    ]

    for ticker, notes in sorted_tickers:
        # Take most recent N notes (notes are in file order — newer = later position)
        notes_sorted = sorted(notes, key=lambda n: -n["position"])[:headlines_per_ticker]
        parts.append(f"**{ticker}** ({len(notes)} note{'s' if len(notes) != 1 else ''}):")
        for n in notes_sorted:
            head = (n.get("headline") or "").strip()
            if head:
                line = f"  • {head[:200]}"
                # Add a take snippet if available — shows Rafael's framing/signal
                if include_take_snippet:
                    take = (n.get("take") or "").strip()
                    if take:
                        snippet = take[:160].replace("\n", " ").strip()
                        line += f"\n      └ take: {snippet}…"
                parts.append(line)
        parts.append("")

    return "\n".join(parts).rstrip()


# ── Stats block for the learn cycle ───────────────────────────────────────────
def build_observer_stats_block() -> str:
    """
    Build a structured stats block for the deep learn cycle (every 10 runs).
    Surfaces what Rafael actually writes about — the ground-truth signal of
    materiality.
    """
    data = parse_observer_doc()
    if data.get("total_notes", 0) == 0:
        return "(no Observer notes parsed yet)"

    parts = [
        f"=== OBSERVER PUBLISHED NOTES ANALYSIS ({data['total_notes']} notes parsed) ===",
        "",
        "This is what Rafael actually wrote. Tickers below are MATERIAL by",
        "definition — the curator should never miss them.",
        "",
        "--- Top 20 most-noted tickers (Rafael's revealed priorities) ---",
    ]
    for ticker, count in list(data["ticker_frequency"].items())[:20]:
        parts.append(f"  {ticker:<14} {count} note(s)")

    if data["signal_distribution"]:
        parts.append("")
        parts.append("--- Directional signal usage (Rafael's calibration) ---")
        for sig, count in data["signal_distribution"].items():
            parts.append(f"  {sig:<32} {count}")

    return "\n".join(parts)


# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "summary"

    if cmd == "parse":
        data = parse_observer_doc(force_reparse=True)
        print(f"Parsed {data['total_notes']} notes")
        print(f"Cached to: {CACHE_PATH}")

    elif cmd == "tickers":
        freq = get_ticker_frequency()
        print(f"\n{len(freq)} unique tickers, top 30:\n")
        for t, n in list(freq.items())[:30]:
            print(f"  {t:<16} {n} note(s)")

    elif cmd == "signals":
        sigs = get_signal_distribution()
        print(f"\nSignal vocabulary distribution:\n")
        for s, n in sigs.items():
            print(f"  {s:<32} {n}")

    elif cmd == "recent":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        notes = get_recent_notes(n)
        print(f"\nLast {len(notes)} notes:\n")
        for note in notes:
            print(f"📍 {note['ticker']}: {note['headline']}")
            if note.get("signal"):
                print(f"   [{note['signal']}]")
            print(f"   ({note['char_count']} chars)\n")

    elif cmd == "style":
        print(build_style_examples(3))

    elif cmd == "stats":
        print(build_observer_stats_block())

    elif cmd == "gaps":
        from learn import _read_current_context
        ctx = _read_current_context()
        gaps = find_underrepresented_tickers(min_notes=3, current_context=ctx)
        if not gaps:
            print("\nNo blind spots — every frequently-noted ticker is in ANALYST_CONTEXT.")
        else:
            print(f"\nTickers noted 3+ times but missing from ANALYST_CONTEXT:\n")
            for t, n in gaps:
                print(f"  {t:<14} {n} note(s)")

    else:
        # Default summary
        data = parse_observer_doc()
        print(f"\nObserver file: {OBSERVER_PATH}")
        print(f"  Parsed notes: {data['total_notes']}")
        print(f"  Unique tickers: {len(data.get('ticker_frequency', {}))}")
        print(f"  Signal phrases used: {len(data.get('signal_distribution', {}))}")
        print(f"  Cache: {CACHE_PATH}")
        print(f"\nCommands: parse | tickers | signals | recent [N] | style | stats | gaps")


if __name__ == "__main__":
    main()
