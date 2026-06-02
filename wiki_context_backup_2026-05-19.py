# wiki_context.py — UBS LatAm H&E (Healthcare & Education) analyst domain
# knowledge for Claude triage.
#
# Mirrors the role wiki_context.py plays in the TMT pipeline — drives both
# clipping curation (Job 1) and note writing (Job 3). The learn cycle refines
# this string every 10 runs based on all 7+ learning sources.

ANALYST_CONTEXT = """
## UBS LatAm H&E — Analyst Triage Context

### Triage Decision — Full Note vs. Other News vs. Omit

**Full Note** — ALL must apply:
(1) Fresh, material event: regulatory ruling with concrete P&L mechanism, M&A
    of consequence (size or strategic fit), pricing decision (ANS reajuste, MEC
    EAD changes, FIES/PROUNI policy), major operational data with named
    transmission to a covered stock, GLP-1 inflection news with read-across.
(2) Clear investment read-across to ≥1 covered ticker — thesis, near-term
    estimate, or valuation.
(3) New information — not a duplicate or already-known outcome.

**Other News** — sector-relevant but: no covered-ticker read-across, minor
fines, routine filings, small deals below materiality, preliminary/rumour-stage
regulatory items, general sector color, PR/ESG.

**Omit** — no H&E sector connection, duplicate story, pure PR, irrelevant
geography.

---

### Explicit OMIT Examples
- Routine fines below ~R$10mn with no thesis implication
- Debt tender offers / liability management → routine refinancing, no P&L read-across
- CSR/ESG with no financial mechanism: hospital community programs, education
  scholarship PR, vaccination campaigns
- Legislative committees presenting agendas (no concrete measure passed yet)
- General health sector statistics without per-operator angle ("Brazil has X
  hospital beds per capita")
- Stale news recycled with new timestamp
- General macro stories (interest rates) unless they have a named transmission
  to H&E names (e.g., FIES default rate, hospital capex financing)

---

### Earnings / Results: covered vs. peers (CRITICAL FILTER)

This rule applies STRICTLY to results coverage of covered names. It does NOT
filter general corporate news about covered names — those stay important.

Rafael tracks earnings directly for every covered company. The clipping should
not duplicate that channel by recapping what he already follows.

**OMIT routine RESULTS COVERAGE of covered names (this is the only filter):**
- "Hapvida Q1 EBITDA", "RDOR Q2 results", "YDUQS captação 2T25 sobe",
  "Cogna 4Q recap", "AFYA earnings preview", "Fleury Q1 net income up X%",
  earnings call recaps, post-earnings price-action, analyst recap notes
  without rating/TP action.

**KEEP all NON-results news about covered names — this is NOT what we filter:**
- M&A / strategic deals (RDOR hospital acquisitions, ONCO clinic rollups,
  Hapvida integration milestones, YDUQS / COGN / ANIM consolidation moves)
- ANS / MEC / ANVISA regulatory rulings, court decisions, rule changes
- Hospital openings, network expansion announcements
- New product / contract / partnership wins
- Executive appointments OUTSIDE earnings (board changes, hires)
- Capital raises, refinancings with strategic intent
- New disclosure: segment reporting, KPI introduction, capital-return policy

**KEEP earnings exceptions even for covered names:**
- Surprise material miss/beat that re-prices the thesis
- Guidance update or material outlook revision (margin, EBITDA, captação, MLR)
- M&A or strategic announcement made AT the earnings call
- CFO / CEO transition announced at results
- Earnings-tied broker rating change → Sell-side section

**KEEP Brazilian peer news — competitive context for covered names:**
- Dasa results / strategy → integrated hospital+lab peer for RDOR and FLRY
- Albert Einstein, Sirio Libanês, Mater Dei, Hcor → competing premium hospitals (RDOR)
- SulAmérica, Amil, Porto Saúde, Unimed, Prevent Senior → competing payers (HAPV/SAUD)
- Eurofarma, EMS, Hypera, Aché, Cristália → pharma peers (BLAU)
- Cruzeiro do Sul → higher-ed peer (YDUQ/COGN/ANIM)
- GLP-1 stories with Brazilian transmission (ANVISA approval, ANS coverage debate,
  judicialização, payer cost commentary) — NOT generic US Lilly/Novo earnings recaps

NOTE: US peers (UnitedHealth, HCA, Quest, LabCorp, Eli Lilly, Novo Nordisk,
Adtalem, etc.) are intentionally NOT in scope. We focus on covered names + BR
competitive context to keep signal density high.

**Decision test:** "Is this story PRIMARILY a results recap of a covered name?"
- YES → OMIT
- NO (any other angle, even involving the same company, or any peer) → evaluate
  normally on materiality. The default for non-routine-results stories about
  covered names is KEEP.

---

### Coverage Universe & Read-Across Triggers

**HOSPITALS / HEALTH SERVICES:**
- RDOR (Rede D'Or São Luiz): Largest private hospital network in Brazil.
  Triggers: new hospital openings or acquisitions (hospital count is a key
  KPI), Bradesco/Hapvida payer dynamics (vertical integration debate), ANS
  rulings on hospital-payer contracts, judicialização da saúde (court rulings
  that drive utilization), GLP-1 effect on bariatric/cardiology demand.
  Key risk: payer concentration; HAPV vertical model competes directly.
- ONCO (Oncoclínicas): Cancer-care network roll-up. Triggers: clinic
  acquisitions, oncology drug approvals (immuno-oncology), pricing pressure
  from payers, court rulings on cancer-drug coverage. Smaller-cap, more
  sensitive to financing conditions.

**HEALTH PLANS (PAYERS):**
- HAPV (Hapvida): Largest verticalized payer post-GNDI merger. Triggers:
  MLR / sinistralidade prints (the single most-watched metric), ANS reajuste
  decisions (individual + collective plans), portability rule changes, GLP-1
  cost pass-through, network consolidation, court rulings on rol de
  procedimentos. KEY THESIS: synergies from Intermédica integration.
- ODPV (Odontoprev): Dental plan leader. Triggers: corporate plan demand,
  Bradesco distribution (key partner), small-dent market consolidation,
  Bradesco-Caixa dental partnership news.
- SAUD (Bradsaúde): Newer listing, Bradesco's health-plan vehicle. Triggers:
  growth in lives covered, distribution synergies with Bradesco Seguros,
  competitive dynamics vs HAPV / SulAmérica / Amil.

**DIAGNOSTICS:**
- FLRY (Fleury): Diagnostic-imaging + clinical-analysis leader. Triggers: B2C
  (Hermes Pardini integration), B2B/lab-to-lab business, payer reimbursement
  rates, GLP-1 effect on diagnostic-test demand (some tests up, some down),
  AI-driven imaging cost pressure, expansion of premium "Saúde iD"
  vertical-care offering.

**PHARMA:**
- BLAU (Blau Farmacêutica): Hospital-channel specialty pharma (biológicos,
  alta complexidade). Triggers: SUS purchasing decisions (largest customer
  segment), ANVISA approvals/registrations, biosimilar competition, new
  contract wins, court rulings on judicialização medicamento.

**HIGHER EDUCATION:**
- YDUQ (YDUQS): Multi-brand for-profit (Estácio core). Triggers: medicine
  vagas (high-margin product), EAD enrollment trends, MEC EAD rule changes
  (regulação EAD has been the dominant 2024-2026 risk), FIES/PROUNI policy
  shifts, ticket médio dynamics.
- COGN (Cogna): Kroton legacy + Vasta (K-12 publishing). Triggers: same EAD/MEC
  dynamics as YDUQS, K-12 textbook cycle (Vasta), medicine vagas allocation,
  capital structure (deleveraging story).
- ANIM (Ânima): Premium higher-ed + Inspirali (medicine school chain).
  Triggers: medicine vagas (Inspirali is a major beneficiary), MEC inspections,
  M&A in medical-school space.
- AFYA (NASDAQ AFYA): Medical-education pure-play (Brazil). Triggers: new
  medicine vagas authorization, digital health services (MedTech), USD-BRL
  (NASDAQ-listed = forex P&L), US peer multiples re-rating.
- LAUR (Laureate, NASDAQ LAUR): Multi-country LatAm (Brazil + Mexico + Peru).
  Triggers: same Brazil higher-ed dynamics as YDUQ/COGN, Mexican higher-ed
  policy, capital returns (ongoing share repurchase / dividend story).

---

### Cross-Cutting Theme: GLP-1 (Ozempic / Wegovy / Mounjaro / Zepbound)

This is the single biggest cross-cutting story across H&E in 2025-2026,
analogous to AI for TMT. Different read-across by sub-sector:

**Payers (HAPV, SAUD):** Cost pressure as GLP-1 share-of-script climbs.
Brazilian rol de procedimentos coverage debate. ANS may eventually mandate
coverage → MLR pressure → premium repricing. Net: **slightly negative** near
term, **uncertain** medium term depending on ANS framework.

**Hospitals (RDOR, ONCO):** Modest near-term — fewer bariatric procedures
(negative for RDOR's surgical mix), but secondary effects in cardiology,
endocrinology, ortho/musculoskeletal possibly positive over time. Net:
**slightly negative** near term for bariatric-heavy lines.

**Diagnostics (FLRY):** Mixed. Lab tests for diabetes/lipids/cardiometabolic
status could increase (more screening); some procedure-specific imaging
demand may shift. Net: **mixed but skewed neutral**.

**Pharma (BLAU):** Indirect — not a GLP-1 producer; hospital channel still
sells GLP-1 (small share but growing). Net: **neutral**.

**Trigger frame for any GLP-1 story:** specify which covered name(s) are
affected and the direction. Generic "Lilly beats" → flag for cross-cutting
section but not a covered-name note unless there's a named mechanism.

---

### Anatel-equivalent — ANS / MEC monthly cadence

**ANS monthly RN updates** for Health Plans: track all RN (Resolução
Normativa) publications. Key signals:
- Reajuste decisions for individual plans (annual June-ish)
- Rol de procedimentos updates (what's covered, what's not)
- Portability rule changes
- New OPS (Operadoras de Plano de Saúde) authorizations or revocations
- Sinistralidade benchmarks (when published)
Every concrete RN with named operator impact → at minimum Sector tag, often
HAPV-tag with read-across direction.

**MEC quarterly cycle** for Higher Ed: track everything in Diário Oficial:
- Medicine vagas authorizations (single biggest YDUQ/ANIM/AFYA driver)
- EAD regulation changes (the 2024-2026 multi-year story — has compressed
  multiples for YDUQ/COGN; any easing = positive surprise)
- Curso autorizations / re-credenciamento
- Inspections / sanctions on specific institutions

---

### Active Running Stories (auto-refreshed by learn cycle)
When a headline clearly connects to one of these monitored themes, note it:
1. **"EAD regulation tightening"** — MEC restrictions on distance learning
   have been the dominant 2024-26 risk for YDUQ/COGN/ANIM/AFYA; any easing or
   tightening = material
2. **"Medicine vagas expansion"** — Mais Médicos program, new course
   authorizations, court rulings; affects YDUQ/ANIM/AFYA primarily
3. **"GLP-1 coverage debate (Brazil)"** — ANS coverage discussion, court
   rulings on judicialização of weight-loss drugs; HAPV cost exposure
4. **"Hapvida/GNDI integration milestones"** — synergy capture, MLR trajectory,
   any operating-data points that confirm or challenge synergy thesis
5. **"RDOR network expansion"** — hospital openings, acquisitions, opex
   leverage on new units
6. **"Vertical integration (payer-provider)"** — HAPV model vs RDOR independent
   network; any payer M&A in hospitals or vice versa
7. **"Fleury B2B/lab-to-lab strategy"** — Hermes Pardini integration synergies
   and the lab-to-lab consolidation story
8. **"ANS reajuste cycle"** — annual June/July decision; both individual and
   collective plan reajuste; the single biggest HAPV pricing event
9. **"FIES recovery / Pé-de-Meia"** — government student financing programs;
   affects all higher-ed names but YDUQ/COGN most exposed
10. **"AFYA / LAUR USD-BRL sensitivity"** — NASDAQ-listed names with most
    revenue in BRL → quarterly forex P&L volatility
11. **"Judicialização da saúde"** — court rulings that mandate procedure or
    drug coverage; recurring HAPV/SAUD/SulAmérica cost pressure

---

### Second-Order Read-Across (perception and multiple effects)

A story is material even when direct financial impact is uncertain if it
affects the competitive narrative or valuation multiple for a covered stock.
Examples:

- **Brazilian peer events (Dasa, Einstein, Sírio, Mater Dei, SulAmérica, Amil,
  Eurofarma, EMS, Hypera, Cruzeiro do Sul)** → set the BR competitive tone
  for covered names; include with named transmission to a covered name
- **GLP-1 events with Brazilian transmission** (ANVISA approval, ANS rol-
  inclusion debate, judicialização rulings, payer cost commentary) → cost-
  pressure read-across for HAPV/SAUD; secondary effects on RDOR/ONCO/FLRY
  procedure mix. Generic US Lilly/Novo earnings recaps are NOT in scope —
  filter as noise unless there is an explicit BR transmission.

### Specifically material story types (often missed at first glance — KEEP these):

**GLP-1 access / demand-pressure signals** (even if framed as crime/social news):
- Black-market / contraband / illegal smuggling stories — signal demand
  exceeds legal supply → SUS/ANS pressure to expand coverage rising
- Waiting-list (fila) stories — same signal
- Senate / congressional discussion of SUS coverage of Mounjaro/Ozempic/Wegovy
- Regional shortages, price spikes, importation discussions
- These all forecast near-term ANS rol-update pressure → HAPV/SAUD cost line

**Distressed / small hospital chain events** (Alliança Saúde, Kora, Athena, Amico class):
- Emergency debt raises ("debêntures emergenciais"), going-concern flags,
  liquidity events at SMALLER hospital chains → competitive opportunity
  for RDOR (M&A target landscape) and competitive pressure on ONCO (sector
  cost of capital)
- Tag as Hospitals sector with RDOR/ONCO read-across, NOT Diagnostics

**Pharma AI / drug discovery (BLAU long-term competitive frame):**
- Isomorphic Labs / AlphaFold / DeepMind pharma announcements
- Brazilian biotech AI events
- Long-term: changes specialty-pharma competitive moat assumptions

**Hospital labor supply (RDOR / ONCO cost-line signal):**
- Medical residency expansions (MEC residência médica)
- Nursing residency expansions (residências enfermagem)
- Mais Médicos program changes (when affecting private-network labor pool)
- Generally: anything that changes supply of healthcare professionals →
  hospital wage line over the next 2-4 quarters
- **Tax reform health/education** → Brazilian tax reform (reforma tributária)
  has special provisions for healthcare and education services; any update is
  material across the universe
- **Judicialização rulings (STF/STJ)** → affect cost structure for HAPV/SAUD
  even when about specific drugs or specific care; the precedent matters
- **MEC EAD rulings** → multiples for entire for-profit higher-ed cohort
  re-rate on each rule
- **K-12 textbook cycle (Vasta)** → COGN-specific, FNDE purchasing decisions

---

### Ticker Cross-Reference (editorial short forms used in the clipping)
RDOR     = Rede D'Or São Luiz
ONCO     = Oncoclínicas
HAPV     = Hapvida (post-GNDI integration name)
ODPV     = Odontoprev
SAUD     = Bradsaúde
FLRY     = Fleury
BLAU     = Blau Farmacêutica
YDUQ     = YDUQS (Estácio)
COGN     = Cogna (Kroton/Vasta/Saber)
ANIM     = Ânima (Inspirali)
AFYA     = Afya (NASDAQ)
LAUR     = Laureate (NASDAQ)

Brazilian peer aliases (use these short forms when tagging a peer story):
DASA       = Dasa (integrated hospital + lab peer to RDOR / FLRY)
Einstein   = Hospital Albert Einstein (premium hospital peer)
Sírio      = Hospital Sírio-Libanês (premium hospital peer)
Mater Dei  = Mater Dei hospital chain
Hcor       = HCor hospital
SulAmérica = SulAmérica saúde (payer peer to HAPV / SAUD)
Amil       = Amil (payer peer to HAPV / SAUD)
Porto      = Porto Saúde (payer peer to HAPV / SAUD)
Unimed     = Unimed cooperative system
Eurofarma  = pharma peer to BLAU
EMS        = pharma peer to BLAU
Hypera     = HYPE3 — pharma peer to BLAU
Cruzeiro   = Cruzeiro do Sul (higher-ed peer to YDUQ / COGN)

US PEERS NOT IN SCOPE for this pipeline (intentional — focus on coverage,
drop US peer noise). Do not tag any story with US-only tickers (UNH, HCA,
LLY, NVO, DGX, LH, ATGE, etc.) — if a US story has Brazilian read-across,
tag it with the affected covered ticker.

Regulator / agency aliases:
ANS      = Agência Nacional de Saúde Suplementar (health-plan regulator)
ANVISA   = Agência Nacional de Vigilância Sanitária (drug/medical-device reg.)
MEC      = Ministério da Educação (education regulator)
FNDE     = Fundo Nacional de Desenvolvimento da Educação (textbook procurement)
SUS      = Sistema Único de Saúde (public health system)
STF      = Supremo Tribunal Federal (Brazilian Supreme Court)
STJ      = Superior Tribunal de Justiça

### Multi-Ticker Format
When a single story directly affects 2-3 covered names, join tickers with "/":
  "HAPV/RDOR"       — payer + hospital story (e.g., HAPV-RDOR contract dispute)
  "YDUQ/COGN/ANIM"  — MEC EAD ruling affecting multiple higher-ed names
  "AFYA/LAUR"       — NASDAQ-listed pair, USD-BRL or US higher-ed comps
  "HAPV/SAUD"       — payer-specific regulatory story
Max 3 tickers. Only use when BOTH names have a named investment angle.

### Read-Across Tag Style
For peer headlines with a clear covered-stock investment angle, lead with
covered ticker: "HAPV: DASA: Dasa lança plano de telemedicina premium"
means HAPV is the investment angle; DASA is the subject of the news.
Only use when read-across is explicit and direct, and the peer is Brazilian
(US peers are out of scope).
"""
