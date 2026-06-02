# wiki_context.py — UBS LatAm H&E (Healthcare & Education) analyst domain
# knowledge for Claude triage.
#
# Mirrors the role wiki_context.py plays in the TMT pipeline — drives both
# clipping curation (Job 1) and note writing (Job 3). The learn cycle refines
# this string every 10 runs based on all 7+ learning sources.

ANALYST_CONTEXT = """## UBS LatAm H&E — Analyst Triage Context

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
- Dr. Consulta, Athena, Alliança Saúde, Kora, Amico → smaller hospital / outpatient
  peers; distress or expansion events are read-across to RDOR (M&A target landscape)
  and ONCO (sector cost-of-capital signal)
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
  sensitive to financing conditions. **In 2026 ONCO has been in a credit /
  going-concern crisis** — any incremental signal on Q1 prejuízo, OPA pressure
  at CVM, PwC continuity flags, debt restructuring, controller transactions,
  or covenant negotiations is HIGH-priority full note territory. SUS-channel
  oncology contract wins (e.g., the Lula R$-package of 23 new high-cost
  oncology medicines) are a separate ONCO/BLAU thread — material when scope
  or eligibility is clarified.

**HEALTH PLANS (PAYERS):**
- HAPV (Hapvida): Largest verticalized payer post-GNDI merger. Triggers:
  MLR / sinistralidade prints (the single most-watched metric), ANS reajuste
  decisions (individual + collective plans), portability rule changes, GLP-1
  cost pass-through, network consolidation, court rulings on rol de
  procedimentos. KEY THESIS: synergies from Intermédica integration.
- ODPV (Odontoprev): Dental plan leader. Triggers: corporate plan demand,
  Bradesco distribution (key partner), small-dent market consolidation,
  Bradesco-Caixa dental partnership news, capex mix / tech investments
  (ODPV has flagged ~96% of capex on tech — anything that shifts unit
  economics or B2B retention is the angle, not generic dental-market color).
- SAUD (Bradsaúde): Newer listing, Bradesco's health-plan vehicle. Triggers:
  growth in lives covered, distribution synergies with Bradesco Seguros,
  competitive dynamics vs HAPV / SulAmérica / Amil.

**DIAGNOSTICS:**
- FLRY (Fleury): Diagnostic-imaging + clinical-analysis leader. Triggers: B2C
  (Hermes Pardini integration), B2B/lab-to-lab business, payer reimbursement
  rates, GLP-1 effect on diagnostic-test demand (some tests up, some down),
  AI-driven imaging cost pressure, expansion of premium "Saúde iD"
  vertical-care offering, **premium-hospital partnerships** (Sírio-Libanês,
  Einstein, Mater Dei diagnostic-services deals are direct B2B revenue
  signals and read-across to the premium-network strategy). Note: FLRY is
  consistently curated but rarely promoted — tighten to: only full-note FLRY
  on partnership announcements, payer-reimbursement rulings, B2B contract
  wins, or material capacity expansion. Generic AI-in-radiology color = Other.

**PHARMA:**
- BLAU (Blau Farmacêutica): Hospital-channel specialty pharma (biológicos,
  alta complexidade). Triggers: SUS purchasing decisions (largest customer
  segment — the SUS high-cost oncology package is the single biggest 2026
  story line), ANVISA approvals/registrations, biosimilar competition, new
  contract wins, court rulings on judicialização medicamento. Note: routine
  ANVISA approvals of non-BLAU drugs are Other News unless they affect a
  segment where BLAU competes — tighten the bar here.

**HIGHER EDUCATION:**
- YDUQ (YDUQS): Multi-brand for-profit (Estácio core). Triggers: medicine
  vagas (high-margin product), EAD enrollment trends, MEC EAD rule changes
  (regulação EAD has been the dominant 2024-2026 risk), FIES/PROUNI policy
  shifts, ticket médio dynamics.
- COGN (Cogna): Kroton legacy + Vasta (K-12 publishing). Triggers: same EAD/MEC
  dynamics as YDUQS, K-12 textbook cycle (Vasta), medicine vagas allocation,
  capital structure (deleveraging story). Vasta's Nasdaq delisting (completed
  early 2026) saves ~R$15mn/yr — already in price; further structural moves
  on COGN's capital allocation remain material.
- ANIM (Ânima): Premium higher-ed + Inspirali (medicine school chain).
  Triggers: medicine vagas (Inspirali is a major beneficiary), MEC inspections,
  M&A in medical-school space.
- AFYA (NASDAQ AFYA): Medical-education pure-play (Brazil). Triggers: new
  medicine vagas authorization, digital health services (MedTech), USD-BRL
  (NASDAQ-listed = forex P&L), US peer multiples re-rating.
- LAUR (Laureate, NASDAQ LAUR): Multi-country LatAm (Brazil + Mexico + Peru).
  Triggers: same Brazil higher-ed dynamics as YDUQ/COGN, Mexican higher-ed
  policy, capital returns (ongoing share repurchase / dividend story).
  **LAUR BLIND-SPOT FLAG:** Rafael has written 6 Observer notes on LAUR but
  curated items rarely surface LAUR by name. Treat any Mexico/Peru higher-ed
  policy story, any LAUR capital-return announcement (buyback, special
  dividend), and any LAUR-cohort earnings preview as Tier-1 candidates. The
  default should be to surface, not omit.

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

**Wegovy patent expiry (Mar 2026) / semaglutide generics:** Patent loss should
gradually relieve cost pressure on payers (HAPV/SAUD) as biosimilar/generic
semaglutide enters the BR market; near-term it ALSO drives a wave of pricing
moves (Novo Nordisk bundle discounts, Rybelsus markdowns) that are leading
indicators of ANS rol-inclusion economics. Any concrete generic-launch or
ANS coverage decision tied to post-patent semaglutide is full-note material.

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
- Suspension of plan-sales lists (monthly "Venda de planos suspensa" releases)
  — concrete operator-named signal, often full-note when a covered or close
  peer is on the list
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
   and the lab-to-lab consolidation story; premium-hospital partnership
   announcements (Sírio-Libanês, Einstein) are a subset of this thread
8. **"ANS reajuste cycle"** — annual June/July decision; both individual and
   collective plan reajuste; the single biggest HAPV pricing event
9. **"FIES recovery / Pé-de-Meia"** — government student financing programs;
   affects all higher-ed names but YDUQ/COGN most exposed
10. **"AFYA / LAUR USD-BRL sensitivity"** — NASDAQ-listed names with most
    revenue in BRL → quarterly forex P&L volatility
11. **"Judicialização da saúde"** — court rulings that mandate procedure or
    drug coverage; recurring HAPV/SAUD/SulAmérica cost pressure
12. **"ONCO credit / going-concern crisis"** — 2026 story line. Trigger items:
    Q1 prejuízo, CVM OPA pressure, PwC continuity flags, debt restructuring,
    controller / sponsor transactions, covenant negotiations. Default to
    full note on any concrete development.
13. **"SUS high-cost oncology package"** — Lula-government rollout of new
    oncology medicines through SUS (23-drug package and successors). Read-
    across: BLAU (supply-side beneficiary), ONCO (private-clinic mix shift if
    reimbursement gaps narrow), and indirectly RDOR oncology service lines.
14. **"Falso coletivo / STJ jurisprudence"** — STJ rulings consolidating that
    small-group "false collective" plans must be treated as individual for
    reajuste purposes. Incremental headwind to collective-plan pricing
    flexibility for HAPV/SAUD; track each new precedent.
15. **"Sell-side preference shifts (higher-ed cohort)"** — periodic broker
    refreshes (e.g., Bradesco BBI top-pick rotations) within the
    YDUQ/COGN/ANIM/AFYA cohort can be a stand-alone Sell-side note,
    especially when a name is added or dropped from top picks.
16. **"Wegovy / semaglutide patent expiry & generics"** — Mar-2026 patent
    expiry triggering Novo Nordisk pricing moves and prospective generic
    entry in BR; flips the GLP-1 cost-pressure narrative for HAPV/SAUD over
    time.

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
- Apply the same lens to ONCO itself when it is the distressed name — see
  Active Running Story #12

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

**Epidemiology / outbreak events (multi-name read-across — KEEP and place
in the "Epidemiology / Public Health" sector):**
Diseases that move medical utilization are MATERIAL across the universe.
Don't dismiss them as generic health news.
- **Dengue / arboviroses / Zika / chikungunya / febre amarela** (BR summer
  recurrence; El Niño years are worse):
  → HAPV / SAUD MLR pressure (more outpatient + ICU claims)
  → RDOR / ONCO occupancy (positive top-line, negative mix vs elective)
  → FLRY diagnostic test volumes (positive: dengue NS1, IgM/IgG, sorologia)
  → BLAU hemoderivados (anti-D, immunoglobulins)
- **Influenza / SRAG / respiratory virus surges** (winter recurrence):
  same pattern — HAPV MLR, RDOR occupancy, FLRY respiratory panels.
- **Sarampo / meningite / new-variant COVID** — same logic, less seasonal.
- **Vaccination campaigns / coverage** — BLAU (adjuvants, immunoglobulins),
  and indirectly payer cost (reduced future claims).
- Frame each story with the specific covered-name transmission. Generic
  "Brazil reports X cases" without operator angle = Other News or omit.

**Multi-ticker tagging for higher-ed sector-wide events:**
When a regulatory/policy event affects multiple covered higher-ed names,
use a multi-ticker tag. Examples that always hit ≥3 names:
- **ENEM rule changes** (auto-enrollment, new test sites, exam format):
  affects YDUQ / COGN / ANIM most directly (BR public-school funnel); AFYA
  partially (medical-school applications); LAUR weakest (Mexico/Peru-heavy).
  Tag: `YDUQ/COGN/ANIM` (or add AFYA if the rule is specifically about
  medicine admissions).
- **MEC EAD rules** (course authorization, polos limits): all 5 are exposed
  but YDUQ / COGN / ANIM most. Tag: `YDUQ/COGN/ANIM`.
- **FIES / PROUNI / Pé-de-Meia changes**: similar — `YDUQ/COGN/ANIM` (AFYA
  / LAUR less exposed).
- **Medicine-vagas authorization batches**: tag the BR ones most exposed —
  usually `YDUQ/ANIM/AFYA` (these have biggest medical-school footprints).
- Do NOT default to a single ticker (LAUR or AFYA only) for sector-wide
  events just because one name is mentioned first in the source.
- **Tax reform health/education** → Brazilian tax reform (reforma tributária)
  has special provisions for healthcare and education services; any update is
  material across the universe
- **Judicialização rulings (STF/STJ)** → affect cost structure for HAPV/SAUD
  even when about specific drugs or specific care; the precedent matters.
  STJ "falso coletivo" line of cases is its own running story (see #14).
- **MEC EAD rulings** → multiples for entire for-profit higher-ed cohort
  re-rate on each rule
- **K-12 textbook cycle (Vasta)** → COGN-specific, FNDE purchasing decisions

---

### Curator calibration notes (from corpus analysis)

These names are curated 3+ times but rarely promoted to a full note — tighten
or expand the materiality bar accordingly so the curator and note-writer agree:

- **ANVISA (26x, 0 notes):** Tighten. Default ANVISA drug approvals belong in
  Other News. Promote only when: (i) approval is in a BLAU-competing segment;
  (ii) approval is a GLP-1 or semaglutide-generic event; (iii) ANVISA acts on
  a covered name directly (audit, license, recall touching BLAU); (iv) ANVISA
  changes a class-level rule (cannabis medicinal, biosimilares, clinical-trial
  framework).
- **FLRY (23x, 0 notes):** Tighten — see Diagnostics section above. Default to
  Other News unless the story is a B2B contract, partnership with a premium
  hospital, reimbursement ruling, or capacity move.
- **ANS / HAPV/SAUD (15x / 10x, 0 notes):** Expand. ANS suspensions, RN
  publications with reajuste mechanics, and STJ rulings against operators are
  all full-note candidates, not just Sector tags.
- **ODPV (9x, 0 notes):** Expand. ODPV-specific capex / tech / Bradesco-
  distribution stories merit full notes; generic dental-market growth color
  stays in Other News.
- **MEC / YDUQ-COGN-ANIM (8x / 5x, 0 notes):** Expand. Any concrete MEC EAD
  portaria with operator-named impact should be a full note, not a Sector tag.
- **AFYA (6x, 0 notes):** Expand for medicine-vagas events and US-listed
  multiple events; keep new-campus openings as Other News.

These adjustments target the gap between F (what gets curated) and H (what
Rafael actually writes about).

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
Dr. Consulta = outpatient-clinic peer (relevant to ONCO / FLRY thinking)
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
CVM      = Comissão de Valores Mobiliários (securities regulator — relevant
           for ONCO OPA pressure, related-party disclosures)

### Multi-Ticker Format
When a single story directly affects 2-3 covered names, join tickers with "/":
  "HAPV/RDOR"       — payer + hospital story (e.g., HAPV-RDOR contract dispute)
  "YDUQ/COGN/ANIM"  — MEC EAD ruling affecting multiple higher-ed names
  "AFYA/LAUR"       — NASDAQ-listed pair, USD-BRL or US higher-ed comps
  "HAPV/SAUD"       — payer-specific regulatory story
  "ONCO/BLAU"       — SUS oncology package, oncology drug coverage events
Max 3 tickers. Only use when BOTH names have a named investment angle.

### Read-Across Tag Style
For peer headlines with a clear covered-stock investment angle, lead with
covered ticker: "HAPV: DASA: Dasa lança plano de telemedicina premium"
means HAPV is the investment angle; DASA is the subject of the news.
Only use when read-across is explicit and direct, and the peer is Brazilian
(US peers are out of scope)."""
