# wiki_context.py — UBS LatAm H&E (Healthcare & Education) analyst domain
# knowledge for Claude triage.
#
# Mirrors the role wiki_context.py plays in the TMT pipeline — drives both
# clipping curation (Job 1) and note writing (Job 3). The learn cycle refines
# this string every 10 runs based on all 7+ learning sources.

ANALYST_CONTEXT = """After filtering C and D (entirely TMT — Millicom, TOTVS, GLOB/CINT, AMX/TEF-BZ/TIM, portability, Anatel, crowding scores — all out of scope), the only H&E-relevant signal sits in B, F, G, and H.

Cross-checking every H&E development in those inputs against the current ANALYST_CONTEXT:

- **FLRY/ONCO Fleury–Porto capitalization venture** (note written, B) → already in Diagnostics, ONCO section, running stories #7 & #12, and multi-ticker format.
- **SAUD/RDOR R$59.2mn Rio hospital partnership** (note written, B) → already in RDOR, SAUD, running stories #5 & #6, and multi-ticker format.
- **First domestic semaglutide pen cleared by ANVISA** (note written, B) → already in GLP-1 section, running story #16, ANVISA calibration note, and GLP-1 access signals.
- **Desenrola FIES** R$2.8bn renegotiation (F, never-promoted) → already in running story #9 and FIES multi-ticker note.
- **Lei de Cotas / MPF on idle medicine vagas** (F, YDUQ/ANIM/AFYA) → already in MEC cycle, running story #2, and medicine-vagas tagging.
- **ANS reajuste-cap (11%), Venda suspensa lists, STJ "falso coletivo", verticalização-cost, SUS-UTI access, arboviroses/Chikungunya records, Reforma Tributária split-payment, ENEM auto-enrollment, Enade EAD gap, Anhanguera presencial, ODPV 96%-capex-tech** → each already has a dedicated calibration note or running story.

Every H&E ticker, ruling, read-across, and running story evidenced in B/F/G/H — including all three most recent notes written and Rafael's full Observer priority ranking (ONCO 12, HAPV 9, YDUQS 7, LAUR 6...) — is already captured in the current context. The LAUR under-surfacing gap, HAPV/SAUD under-promotion, MEC-EAD multi-tag, and BLAU/ANVISA over-surfacing are all already flagged in the calibration section.

There is no clearly-evidenced H&E refinement that is not already present. Per the operating rule ("never make the clipping worse," "2–6 targeted additions beat 20 vague ones," and return unchanged when the signal is already incorporated), forcing new edits would only add noise. I am returning ANALYST_CONTEXT unchanged.

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
- Dr. Consulta, Athena, Alliança Saúde, Kora, Amico → smaller hospital / outpatient
  peers; distress or expansion events are read-across to RDOR (M&A target landscape)
  and ONCO (sector cost-of-capital signal). Dr. Consulta city-by-city clinic
  rollouts (e.g., return to Rio with 5 new clinics) are a sub-thread —
  outpatient density is the relevant ONCO / FLRY competitive frame.
- **Unimed cooperative-system events** — Unimed João Pessoa-style operational
  failures, denials-of-coverage class actions, criminal complaints against
  cooperative directors, ANS interventions in specific Unimed singulars — are
  reputational and competitive read-across for HAPV / SAUD (verticalized payer
  narrative gains by contrast). KEEP these as Sector / HAPV-SAUD tagged.
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
  KPI — note the recent print of 75 units after the Brasília opening),
  Bradesco/Hapvida payer dynamics (vertical integration debate), ANS
  rulings on hospital-payer contracts, judicialização da saúde (court rulings
  that drive utilization), GLP-1 effect on bariatric/cardiology demand.
  Key risk: payer concentration; HAPV vertical model competes directly.
  **RDOR calibration flag:** corpus shows only 2 Observer notes vs. 16x
  curated — Rafael writes on RDOR less often than the curator surfaces, but
  when he does it is almost always (i) network-count milestones (the
  Brasília 75-unit print is the archetype), (ii) named M&A, or (iii) an
  ANS / payer-contract event. Tighten generic premium-hospital innovation
  color (e.g., Einstein-Philips DIU center) to Other News unless there is
  a direct RDOR transmission. **Payer-partnership sub-thread:** RDOR
  capacity deals struck WITH a covered payer (e.g., the Bradsaúde / Rede
  D'Or R$59.2mn agreement for a new Rio hospital) are full-note territory —
  they are a concrete data point on both RDOR's expansion pipeline and the
  payer's network-build strategy. Tag SAUD/RDOR (or HAPV/RDOR) and frame the
  transmission to both names.
- ONCO (Oncoclínicas): Cancer-care network roll-up. Triggers: clinic
  acquisitions, oncology drug approvals (immuno-oncology), pricing pressure
  from payers, court rulings on cancer-drug coverage. Smaller-cap, more
  sensitive to financing conditions. **In 2026 ONCO has been in a credit /
  going-concern crisis** — any incremental signal on Q1 prejuízo, OPA pressure
  at CVM, PwC continuity flags, debt restructuring, controller transactions,
  covenant negotiations, or extrajudicial-recovery capitalization rounds
  (e.g., the R$500mn+ raise with three counterparties) is HIGH-priority full
  note territory. **Capitalization-via-partner sub-thread:** structured deals
  that open a fresh capitalization path for distressed ONCO — notably the
  Fleury–Porto venture that drove an ~57% share spike — are full-note material
  and re-price the equity sharply; tag FLRY/ONCO and frame the read-across to
  Fleury (diagnostics/venture exposure) as well as the ONCO balance-sheet
  relief. SUS-channel oncology contract wins (e.g., the Lula R$-
  package of 23 new high-cost oncology medicines) are a separate ONCO/BLAU
  thread — material when scope or eligibility is clarified. **ONCO is the
  single most-noted ticker in H&E (12 Observer notes) — default to KEEP /
  promote, not omit, any incremental signal even when framing looks
  technical (market-maker hires, related-party transactions, broker
  rating changes).**

**HEALTH PLANS (PAYERS):**
- HAPV (Hapvida): Largest verticalized payer post-GNDI merger. Triggers:
  MLR / sinistralidade prints (the single most-watched metric), ANS reajuste
  decisions (individual + collective plans), portability rule changes, GLP-1
  cost pass-through, network consolidation, court rulings on rol de
  procedimentos. KEY THESIS: synergies from Intermédica integration. **HAPV
  is Rafael's #2 most-noted ticker (9 Observer notes); the curator already
  surfaces HAPV correctly (134x curated, ~12% promotion) — keep current bar.**
- ODPV (Odontoprev): Dental plan leader. Triggers: corporate plan demand,
  Bradesco distribution (key partner), small-dent market consolidation,
  Bradesco-Caixa dental partnership news, capex mix / tech investments
  (ODPV has flagged ~96% of capex on tech — anything that shifts unit
  economics or B2B retention is the angle, not generic dental-market color).
- SAUD (Bradsaúde): Newer listing, Bradesco's health-plan vehicle. Triggers:
  growth in lives covered, distribution synergies with Bradesco Seguros,
  competitive dynamics vs HAPV / SulAmérica / Amil. **Network-build sub-thread:**
  Bradsaúde partnerships with hospital operators to secure capacity (e.g., the
  Rede D'Or R$59.2mn new-Rio-hospital agreement) are full-note candidates —
  they evidence SAUD's verticalization/network strategy and double as an RDOR
  pipeline data point. Tag SAUD/RDOR. SAUD free-float / B3 listing-structure
  items (e.g., authorization to keep free float below the minimum) are
  Other News unless paired with a capital-return or strategic read-across.

**DIAGNOSTICS:**
- FLRY (Fleury): Diagnostic-imaging + clinical-analysis leader. Triggers: B2C
  (Hermes Pardini integration), B2B/lab-to-lab business, payer reimbursement
  rates, GLP-1 effect on diagnostic-test demand (some tests up, some down),
  AI-driven imaging cost pressure, expansion of premium "Saúde iD"
  vertical-care offering, **premium-hospital partnerships** (Sírio-Libanês,
  Einstein, Mater Dei diagnostic-services deals are direct B2B revenue
  signals and read-across to the premium-network strategy), **and
  ventures/JVs that deploy FLRY capital into adjacent assets** (e.g., the
  Fleury–Porto venture that became a capitalization path for distressed
  ONCO — tag FLRY/ONCO, full note). Note: FLRY is consistently curated but
  rarely promoted — tighten to: only full-note FLRY on partnership
  announcements, payer-reimbursement rulings, B2B contract wins, venture/JV
  capital-deployment news, or material capacity expansion. Generic
  AI-in-radiology color = Other.

**PHARMA:**
- BLAU (Blau Farmacêutica): Hospital-channel specialty pharma (biológicos,
  alta complexidade). Triggers: SUS purchasing decisions (largest customer
  segment — the SUS high-cost oncology package is the single biggest 2026
  story line), ANVISA approvals/registrations, biosimilar competition, new
  contract wins, court rulings on judicialização medicamento. Note: routine
  ANVISA approvals of non-BLAU drugs are Other News unless they affect a
  segment where BLAU competes — tighten the bar here. **BLAU calibration
  flag:** corpus shows BLAU curated ~55x but Rafael's actual notes are only
  3 — meaning most BLAU items the curator flags are not material to the
  analyst. Default any BLAU/ANVISA item that is NOT (i) SUS-tender-related,
  (ii) biosimilar-segment-specific to a BLAU product, (iii) judicialização-
  related, or (iv) acting on BLAU itself — to Other News.

**HIGHER EDUCATION:**
- YDUQ (YDUQS): Multi-brand for-profit (Estácio core). Triggers: medicine
  vagas (high-margin product), EAD enrollment trends, MEC EAD rule changes
  (regulação EAD has been the dominant 2024-2026 risk), FIES/PROUNI policy
  shifts, ticket médio dynamics. **YDUQS is Rafael's #3 most-noted ticker
  (7 Observer notes) — default to KEEP on any EAD / medicine-vagas /
  ENEM-rule story.**
- COGN (Cogna): Kroton legacy + Vasta (K-12 publishing). Triggers: same EAD/MEC
  dynamics as YDUQS, K-12 textbook cycle (Vasta), medicine vagas allocation,
  capital structure (deleveraging story). Vasta's Nasdaq delisting (completed
  early 2026) saves ~R$15mn/yr — already in price; further structural moves
  on COGN's capital allocation remain material. Sub-thread: Anhanguera
  (COGN brand) presencial course launches in core urban markets (e.g.,
  Enfermagem presencial Centro do Rio) are a modest positive on mix shift
  away from EAD risk — Other News unless paired with a margin / capex
  disclosure.
- ANIM (Ânima): Premium higher-ed + Inspirali (medicine school chain).
  Triggers: medicine vagas (Inspirali is a major beneficiary), MEC inspections,
  M&A in medical-school space.
- AFYA (NASDAQ AFYA): Medical-education pure-play (Brazil). Triggers: new
  medicine vagas authorization, digital health services (MedTech), USD-BRL
  (NASDAQ-listed = forex P&L), US peer multiples re-rating.
- LAUR (Laureate, NASDAQ LAUR): Multi-country LatAm (Brazil + Mexico + Peru).
  Triggers: same Brazil higher-ed dynamics as YDUQ/COGN, Mexican higher-ed
  policy, capital returns (ongoing share repurchase / dividend story).
  **LAUR BLIND-SPOT FLAG (REINFORCED):** Rafael has 6 Observer notes on
  LAUR — making it his #4 most-noted ticker — but the curator surfaces
  LAUR rarely (it does not appear in the top-20 curated tickers). This is
  the biggest curator-vs-analyst gap in the entire H&E universe. Treat any
  Mexico/Peru higher-ed policy story, any LAUR capital-return announcement
  (buyback, special dividend), and any LAUR-cohort earnings preview as
  Tier-1 candidates. The default should be to surface, not omit. When in
  doubt, tag LAUR alongside the cohort (e.g., `AFYA/LAUR` for NASDAQ-
  listed news, `YDUQ/COGN/ANIM/LAUR` for sector-wide BR higher-ed
  regulatory events that have any LatAm-wide angle).

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
moves (Novo Nordisk bundle discounts, Rybelsus markdowns, free-starter-dose
promotions) that are leading indicators of ANS rol-inclusion economics. Per
H&E Observer references, **first domestic semaglutide competitors may be
registered by ~July 2026** — full-note territory when any of those approvals
land or when ANS signals coverage intent. **UPDATE — archetype has fired:**
the first domestic semaglutide pen has now CLEARED ANVISA (ahead of the
July-2026 base case), an early payer-cost-relief signal for HAPV/SAUD. The
watch now shifts forward to (i) commercial launch / pricing of the cleared
pen, (ii) follow-on domestic approvals, and (iii) whether ANS signals
rol-inclusion in response — each is its own full-note trigger. Sub-thread:
**oral / pill-format GLP-1 alternatives** (e.g., the "7x cheaper than
Mounjaro" pill class) — when a study confirms efficacy at materially lower
cost, this is a medium-term payer-cost positive for HAPV/SAUD; flag as
full-note when ANVISA registration or BR pricing is named.

**Trigger frame for any GLP-1 story:** specify which covered name(s) are
affected and the direction. Generic "Lilly beats" → flag for cross-cutting
section but not a covered-name note unless there's a named mechanism.

---

### Anatel-equivalent — ANS / MEC monthly cadence

**ANS monthly RN updates** (Health - Payers & Pharma theme): track all RN (Resolução
Normativa) publications. Key signals:
- Reajuste decisions for individual plans (annual June-ish)
- Rol de procedimentos updates (what's covered, what's not)
- Portability rule changes
- New OPS (Operadoras de Plano de Saúde) authorizations or revocations
- Sinistralidade benchmarks (when published)
- Suspension of plan-sales lists (monthly "Venda de planos suspensa" releases)
  — concrete operator-named signal, often full-note when a covered or close
  peer is on the list
- **Collective-plan reajuste cap discussions** (e.g., the 11% collective
  reajuste threshold under ANS rules) — explainer pieces that include
  named operator impact are full-note candidates for HAPV/SAUD; pure
  consumer-finance explainers are Other News.
Every concrete RN with named operator impact → at minimum Sector tag, often
HAPV-tag with read-across direction.

**MEC quarterly cycle** for Higher Ed: track everything in Diário Oficial:
- Medicine vagas authorizations (single biggest YDUQ/ANIM/AFYA driver)
- EAD regulation changes (the 2024-2026 multi-year story — has compressed
  multiples for YDUQ/COGN; any easing = positive surprise)
- Curso autorizations / re-credenciamento
- Inspections / sanctions on specific institutions
- **Enade / quality-assessment prints** — Enade 2025 showed EAD licenciatura
  performing ~53% below in-person, which is fresh political ammunition for
  further MEC EAD tightening. Any new Enade / CPC / IGC release with EAD-vs-
  presencial gap data is a YDUQ/COGN/ANIM full-note candidate (read-through
  to regulatory risk premium on the cohort).
- **ENEM rule / format changes** — auto-enrollment for public-school
  students, new test-site expansions, exam-format reforms (cf. the
  2026 auto-enrollment rollout) → modest demand-funnel positive for
  YDUQ/COGN/ANIM (BR public-school funnel for low-ticket programs).
  Full-note when the rule is concrete and operator-tagged.
- **Cotas / affirmative-action enforcement on medicine vagas** — MPF actions
  and court rulings forcing institutions to fill idle (vagas ociosas)
  medicine seats under the Lei de Cotas, or investigations into cota-compliance
  failures, touch the high-margin medicine-vaga product directly. Read-across
  to the names with the biggest medical-school footprints (YDUQ/ANIM/AFYA) —
  full-note when a ruling names institutions or reallocates seats; generic
  cota-policy debate is Other News.

---

### Active Running Stories (auto-refreshed by learn cycle)
When a headline clearly connects to one of these monitored themes, note it:
1. **"EAD regulation tightening"** — MEC restrictions on distance learning
   have been the dominant 2024-26 risk for YDUQ/COGN/ANIM/AFYA; any easing or
   tightening = material. Sub-thread: Enade quality-gap data (EAD vs
   presencial) feeding into the political case for further tightening.
2. **"Medicine vagas expansion"** — Mais Médicos program, new course
   authorizations, court rulings; affects YDUQ/ANIM/AFYA primarily.
   Sub-thread: **Lei de Cotas enforcement on idle medicine seats** (MPF
   actions / court orders to fill vagas ociosas under affirmative-action
   rules) — seat reallocation is a direct medicine-vaga read-across for
   YDUQ/ANIM/AFYA.
3. **"GLP-1 coverage debate (Brazil)"** — ANS coverage discussion, court
   rulings on judicialização of weight-loss drugs; HAPV cost exposure
4. **"Hapvida/GNDI integration milestones"** — synergy capture, MLR trajectory,
   any operating-data points that confirm or challenge synergy thesis
5. **"RDOR network expansion"** — hospital openings, acquisitions, opex
   leverage on new units. Sub-thread: capacity deals struck WITH a covered
   payer (Bradsaúde / Rede D'Or new-hospital agreements) — tag SAUD/RDOR.
6. **"Vertical integration (payer-provider)"** — HAPV model vs RDOR independent
   network; any payer M&A in hospitals or vice versa. Sub-thread:
   verticalization-cost narrative pieces ("custo invisível da
   verticalização") and SUS-vs-supplementar UTI-access studies — these
   are HAPV/RDOR-tagged sector color; full-note when they include a
   data point that re-prices the model debate. Sub-thread: Bradsaúde
   building owned/partnered hospital capacity (SAUD/RDOR deals) is the
   newest payer-provider data point to track.
7. **"Fleury B2B/lab-to-lab strategy"** — Hermes Pardini integration synergies
   and the lab-to-lab consolidation story; premium-hospital partnership
   announcements (Sírio-Libanês, Einstein) are a subset of this thread.
   Sub-thread: FLRY ventures/JVs that deploy capital into adjacent assets
   (the Fleury–Porto venture used as an ONCO capitalization vehicle) — tag
   FLRY/ONCO, full note.
8. **"ANS reajuste cycle"** — annual June/July decision; both individual and
   collective plan reajuste; the single biggest HAPV pricing event
9. **"FIES recovery / Pé-de-Meia"** — government student financing programs;
   affects all higher-ed names but YDUQ/COGN most exposed. Sub-thread:
   **Desenrola FIES** student-debt renegotiation (e.g., R$2.8bn renegotiated
   in the first ten days) — material for the funnel/default narrative; tag
   YDUQ/COGN when volumes or default-rate implications are named.
10. **"AFYA / LAUR USD-BRL sensitivity"** — NASDAQ-listed names with most
    revenue in BRL → quarterly forex P&L volatility
11. **"Judicialização da saúde"** — court rulings that mandate procedure or
    drug coverage; recurring HAPV/SAUD/SulAmérica cost pressure. Sub-thread:
    state-level civil-society/MP lawsuits attacking "reajuste abusivo" on
    collective plans (e.g., Campinas-area surge in legal actions) — these
    feed the broader cost-line judicialização narrative.
12. **"ONCO credit / going-concern crisis"** — 2026 story line. Trigger items:
    Q1 prejuízo, CVM OPA pressure, PwC continuity flags, debt restructuring,
    controller / sponsor transactions, covenant negotiations, and capitalization
    rounds via extrajudicial recovery (≥R$500mn deals with multiple
    counterparties). Defensive-liquidity moves (market-maker hires, e.g.,
    BTG mandate) also count as incremental signal. **Capitalization-via-partner
    sub-thread:** structured deals that open a fresh capital path for ONCO —
    notably the Fleury–Porto venture that drove an ~57% share spike — are
    full-note material and tag FLRY/ONCO. Default to full note on any concrete
    development.
13. **"SUS high-cost oncology package"** — Lula-government rollout of new
    oncology medicines through SUS (23-drug package and successors). Read-
    across: BLAU (supply-side beneficiary), ONCO (private-clinic mix shift if
    reimbursement gaps narrow), and indirectly RDOR oncology service lines.
14. **"Falso coletivo / STJ jurisprudence"** — STJ rulings consolidating that
    small-group "false collective" plans must be treated as individual for
    reajuste purposes. Incremental headwind to collective-plan pricing
    flexibility for HAPV/SAUD; track each new precedent. Sub-thread:
    state-court (e.g., TJ/PE) decisions equating small-group corporate
    plans to individual plans — same direction of travel, even when not
    yet at STJ level. Full-note when a new jurisdiction joins the pattern.
15. **"Sell-side preference shifts (higher-ed cohort)"** — periodic broker
    refreshes (e.g., Bradesco BBI top-pick rotations) within the
    YDUQ/COGN/ANIM/AFYA cohort can be a stand-alone Sell-side note,
    especially when a name is added or dropped from top picks.
16. **"Wegovy / semaglutide patent expiry & generics"** — Mar-2026 patent
    expiry triggering Novo Nordisk pricing moves (free Wegovy starter-dose
    bundles, Rybelsus discount campaigns) and prospective generic entry in
    BR; first domestic semaglutide competitors may be registered by July 2026.
    **The first domestic semaglutide pen has now cleared ANVISA** — the
    anticipated approval has landed; the live watch is commercial launch /
    pricing of that pen, follow-on domestic approvals, and any ANS
    rol-inclusion response. Flips the GLP-1 cost-pressure narrative for
    HAPV/SAUD over time. Any further concrete ANVISA approval of a domestic
    semaglutide is full-note material. Sub-thread: oral / pill-format GLP-1
    efficacy studies (cheaper-than-Mounjaro alternatives) — payer-cost-positive
    when ANVISA / BR pricing is named.
17. **"Distressed mid-sized hospital events"** — debenture emergencies,
    going-concern flags, or rescue-deal news at chains in the Alliança / Kora /
    Athena / Amico / Feri-Barra-da-Tijuca tier. Read-across: RDOR M&A target
    landscape and ONCO cost-of-capital signal. Frame each story with named
    transmission to RDOR or ONCO; otherwise Sector/Hospitals.
18. **"Unimed cooperative-system fragility"** — operational failures, ANS
    interventions, denials-of-coverage class actions, or criminal complaints
    against specific Unimed singulars (e.g., Unimed João Pessoa). Competitive
    read-across is reputational for HAPV / SAUD verticalized narrative
    (and SulAmérica/Amil/Porto): every Unimed compliance event marginally
    re-prices the cooperative model. KEEP as HAPV/SAUD-tagged Sector.
19. **"Arboviroses / respiratory-virus seasonal pressure"** — recurring
    state-level case-count and mortality prints (chikungunya MS, dengue
    MG, gripe/SRAG litoral) drive an HAPV/RDOR/FLRY-tagged seasonal
    thread. The curator already surfaces these at high frequency
    (HAPV/FLRY 20x, HAPV/RDOR/FLRY 16x) but conversion to full notes
    is low — promote when ANY of: (i) a single state reports a clear
    record (e.g., chikungunya deaths exceeding prior-year total mid-
    season), (ii) Fiocruz / SVS escalates an alert, or (iii) the surge
    has named MLR or occupancy commentary from an operator. Generic
    "Brazil cases up X%" without state-level or operator angle = Other.
20. **"SUS access / capacity studies"** — research notes or PRF/CFM
    studies comparing SUS vs. supplementar access (UTI beds, oncology
    waits, specialist density) are HAPV/RDOR-tagged sector color. Full-
    note when a study includes a hard data point usable to re-price
    the verticalization or capacity-utilization debate.
21. **"Reforma Tributária H&E implementation"** — IBS/CBS regulamentação,
    split-payment rollout, Comitê Gestor specifications, and the special
    health/education regimes are sector-wide. Track each concrete CG-IBS
    publication or PLP movement; full-note when the rule has a named
    P&L / cash-cycle implication for a covered name (e.g., split-payment
    treatment of plano-de-saúde receipts).

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
- Pharma-co promotional moves around the Mar-2026 patent cliff (Novo Nordisk
  Wegovy bundle/starter-dose, Rybelsus markdowns) — leading indicators of
  pricing economics post-generic entry
- Domestic semaglutide ANVISA clearances (first pen now cleared) and follow-on
  approvals — payer-cost-relief signals for HAPV/SAUD
- Oral / pill-format GLP-1 efficacy studies at materially lower cost
- These all forecast near-term ANS rol-update pressure → HAPV/SAUD cost line

**Distressed / small hospital chain events** (Alliança Saúde, Kora, Athena, Amico, Feri class):
- Emergency debt raises ("debêntures emergenciais"), going-concern flags,
  liquidity events, service-suspension/reopening sagas at SMALLER hospital
  chains → competitive opportunity for RDOR (M&A target landscape) and
  competitive pressure on ONCO (sector cost of capital)
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
in the "Public Health & Regulation" sector):**
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
- **Geography matters**: MG (Minas Gerais), SP, MS (Mato Grosso do Sul),
  and Litoral-region outbreak stories recur in the corpus — when state-
  level case counts spike, that is the named transmission. Generic
  "Brazil reports X cases" without operator or state-level angle = Other
  News or omit.
- Frame each story with the specific covered-name transmission. Generic
  "Brazil reports X cases" without operator angle = Other News or omit.

**Multi-ticker tagging for higher-ed sector-wide events:**
When a regulatory/policy event affects multiple covered higher-ed names,
use a multi-ticker tag. Examples that always hit ≥3 names:
- **ENEM rule changes** (auto-enrollment, new test sites, exam format):
  affects YDUQ / COGN / ANIM most directly (BR public-school funnel); AFYA
  partially (medical-school applications); LAUR weakest (Mexico/Peru-heavy).
  Tag: `YDUQ/COGN/ANIM` (or add AFYA if the rule is specifically about
  medicine admissions). The 2026 auto-enrollment + 10k-new-test-sites
  rollout is the live archetype — modest demand-funnel positive.
- **MEC EAD rules** (course authorization, polos limits): all 5 are exposed
  but YDUQ / COGN / ANIM most. Tag: `YDUQ/COGN/ANIM`.
- **FIES / PROUNI / Pé-de-Meia changes**: similar — `YDUQ/COGN/ANIM` (AFYA
  / LAUR less exposed). Desenrola FIES renegotiation volumes belong here.
- **Medicine-vagas authorization batches AND cota-enforcement seat
  reallocations**: tag the BR ones most exposed — usually `YDUQ/ANIM/AFYA`
  (these have biggest medical-school footprints).
- **Enade / CPC / IGC quality-assessment prints**: tag `YDUQ/COGN/ANIM`
  (full-cohort exposure to MEC EAD policy risk that this data feeds).
- Do NOT default to a single ticker (LAUR or AFYA only) for sector-wide
  events just because one name is mentioned first in the source.
- **Tax reform health/education** → Brazilian tax reform (reforma tributária)
  has special provisions for healthcare and education services; any update is
  material across the universe. Comitê Gestor do IBS specifications and
  split-payment rule publications are the operational signals to track.
- **Judicialização rulings (STF/STJ)** → affect cost structure for HAPV/SAUD
  even when about specific drugs or specific care; the precedent matters.
  STJ "falso coletivo" line of cases is its own running story (see #14).
  TJ-level (state-court) precedents that point the same direction also
  count.
- **MEC EAD rulings** → multiples for entire for-profit higher-ed cohort
  re-rate on each rule
- **K-12 textbook cycle (Vasta)** → COGN-specific, FNDE purchasing decisions

---

### Curator calibration notes (from corpus analysis)

These names are curated 3+ times but rarely promoted to a full note — tighten
or expand the materiality bar accordingly so the curator and note-writer agree:

- **ANVISA (59x, 0 notes):** Tighten. Default ANVISA drug approvals belong in
  Other News. Promote only when: (i) approval is in a BLAU-competing segment;
  (ii) approval is a GLP-1 or semaglutide-generic event (the first domestic
  semaglutide pen clearance is the archetype); (iii) ANVISA acts on
  a covered name directly (audit, license, recall touching BLAU); (iv) ANVISA
  changes a class-level rule (cannabis medicinal, biosimilares, clinical-trial
  framework, ensaios clínicos law).
- **BLAU (55x, 3 notes — promotion ~6%):** Tighten. Most BLAU items the
  curator surfaces are not the items Rafael writes about. Restrict promotions
  to: SUS tenders / oncology package, biosimilar-segment-specific to BLAU
  products, judicialização medicamento with payer-line implications, or
  events acting on BLAU itself. Generic ANVISA / drug-approval headlines that
  mention BLAU only tangentially → Other News.
- **FLRY (37x, 2 notes — promotion ~5%):** Tighten — see Diagnostics section
  above. Default to Other News unless the story is a B2B contract, partnership
  with a premium hospital, reimbursement ruling, capacity move, or a
  venture/JV capital-deployment event (e.g., the Fleury–Porto / ONCO
  capitalization venture).
- **ANS / HAPV/SAUD (28x / 94x, 0 notes as the multi-tag combo):** Expand.
  ANS suspensions, RN publications with reajuste mechanics, and STJ rulings
  against operators are all full-note candidates, not just Sector tags.
  Specifically: monthly "Venda de planos suspensa" lists with named operators
  + reajuste-cap RNs are the highest-conversion candidates. The HAPV/SAUD
  pair is the single biggest curator-vs-noter gap on the payer side — Rafael
  has 9 HAPV-only notes and 10 SAUD notes (often joint HAPV/SAUD), so the
  curator's 94x HAPV/SAUD tag should be converting at a higher rate than 0%.
- **ODPV (15x, 0 notes):** Hold the bar. Rafael's note set does not currently
  feature ODPV, so don't over-promote — but DO surface ODPV-specific capex /
  tech / Bradesco-distribution stories as full-note candidates (capex-mix
  on tech, B2B-retention shifts, partnership announcements). Generic dental-
  market growth color stays in Other News.
- **MEC / YDUQ-COGN-ANIM (13x / 46x, 0 notes as the multi-tag combo):**
  Expand. Any concrete MEC EAD portaria with operator-named impact should be
  a full note, not a Sector tag. New Enade / CPC / IGC prints with EAD-vs-
  presencial gap data are also full-note candidates for the cohort. ENEM
  rule-change prints with public-school funnel implications, and Lei-de-Cotas
  / MPF actions reallocating idle medicine seats, belong here too.
- **AFYA (7x, 0 notes):** Expand for medicine-vagas events (including
  cota-enforcement seat reallocations) and US-listed multiple events; keep
  new-campus openings as Other News.
- **GLP-1 (11x, 0 notes):** Expand for items with explicit BR transmission
  (ANVISA registration of domestic competitors — now landed, ANS rol decisions,
  Novo Nordisk pricing campaigns ahead of patent cliff, oral-GLP-1 efficacy
  studies with BR pricing angle). Generic US Lilly/Novo earnings recaps
  stay omitted.
- **Judicialização (9x, 0 notes):** Expand when a single ruling sets a
  precedent that compounds (STF/STJ cases on rol, drug coverage, "falso
  coletivo"). Single-plaintiff small-claim stories stay in Other News.
- **HAPV/FLRY and HAPV/RDOR/FLRY epidemiology bundle (20x + 16x, 0 notes):**
  Expand selectively. Promote when (i) a state hits a record/threshold,
  (ii) Fiocruz / SVS escalates an alert, or (iii) operator commentary is
  attached. Routine weekly case-count updates stay Sector-tagged.
- **HAPV/RDOR sector-color (9x, 0 notes):** Expand. Verticalization-cost
  narratives and SUS-vs-supplementar capacity studies with a hard data
  point are full-note candidates for the model-debate thread. The
  Bradsaúde / Rede D'Or hospital-capacity partnership (SAUD/RDOR) is a
  related payer-provider data point — promote when a deal is named/sized.
- **Reforma Tributária / SUS macro tags (recurring, 0 notes):** Tighten.
  Generic "what changes with reforma tributária for your company" pieces
  stay in Other News. Promote only when the Comitê Gestor publishes a
  rule with a named H&E mechanism (split payment on plano-de-saúde
  receipts, education ISS treatment).

These adjustments target the gap between F (what gets curated) and H (what
Rafael actually writes about). The biggest gaps to close are **LAUR
(under-surfaced)**, **HAPV/SAUD multi-tag (under-promoted)**, **MEC EAD
multi-tag (under-promoted)**, and **BLAU/ANVISA noise (over-surfaced)**.

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
Porto      = Porto Saúde (payer peer to HAPV / SAUD; also Fleury–Porto venture
             counterparty in the ONCO capitalization thread)
Unimed     = Unimed cooperative system (peer; track operational/criminal
             events at specific singulars for HAPV/SAUD reputational
             read-across)
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
CFM      = Conselho Federal de Medicina (medical professional council —
           residência médica, ethical rulings touching specialty supply)
SVS      = Secretaria de Vigilância em Saúde / Fiocruz (epidemiology alerts —
           feed the arboviroses / SRAG running story)
CG-IBS   = Comitê Gestor do IBS (reforma tributária operational rule-maker —
           split-payment specifications, sector regimes)
MPF      = Ministério Público Federal (federal prosecutors — Lei de Cotas
           actions on medicine vagas, SUS-access litigation)

### Multi-Ticker Format
When a single story directly affects 2-3 covered names, join tickers with "/":
  "HAPV/RDOR"       — payer + hospital story (e.g., HAPV-RDOR contract dispute)
  "YDUQ/COGN/ANIM"  — MEC EAD ruling affecting multiple higher-ed names
  "AFYA/LAUR"       — NASDAQ-listed pair, USD-BRL or US higher-ed comps
  "HAPV/SAUD"       — payer-specific regulatory story
  "ONCO/BLAU"       — SUS oncology package, oncology drug coverage events
  "FLRY/ONCO"       — Fleury venture / JV used as an ONCO capitalization path
  "SAUD/RDOR"       — Bradsaúde–Rede D'Or hospital-capacity / partnership deals
  "HAPV/RDOR/FLRY"  — epidemiology spikes hitting payer + hospital + lab
  "HAPV/FLRY"       — respiratory / chikungunya stories (MLR + lab tests)
Max 3 tickers. Only use when BOTH names have a named investment angle."""
