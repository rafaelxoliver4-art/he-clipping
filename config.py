# config.py — H&E News Clipping: Universe, Sectors, Sources
#
# Coverage: 12 Brazilian + 2 NASDAQ-listed LatAm Healthcare & Education names.
# Three runs per day (06h / 16h30 / 18h BRT).
#
# This is a SEPARATE pipeline from the TMT scraper. No state is shared.

from zoneinfo import ZoneInfo

# ── Timezone & schedule ───────────────────────────────────────────────────────
LOCAL_TZ   = ZoneInfo("America/Sao_Paulo")
GNEWS_WHEN = "1d"  # Google News-side hint; real cutoff enforced client-side
MAX_AGE_HOURS = 24  # strict rolling window for published-at filter
SLEEP_S    = 0.5

OUTPUT_DIR = "output"


# ── Lookback window — same dynamic logic as TMT ───────────────────────────────
# 24h rolling normally, 72h on Monday to catch Friday afternoon + weekend.
# All 3 daily runs (06h / 16h30 / 18h BRT) use 24h rolling. Cross-run dedup
# ensures the same story doesn't appear in two runs the same day.
def current_max_age_hours() -> int:
    """Return 72 only on Monday morning (before noon BRT). 24h otherwise.
    The Monday 07:00 BRT run catches the weekend backlog (Fri pm + Sat + Sun).
    Monday 17:00 BRT run uses 24h since the morning run already covered it.
    """
    from datetime import datetime
    now = datetime.now(LOCAL_TZ)
    return 72 if (now.weekday() == 0 and now.hour < 12) else MAX_AGE_HOURS


def current_gnews_when() -> str:
    """Google News `when:` hint — 3d on Monday morning only, 1d otherwise."""
    from datetime import datetime
    now = datetime.now(LOCAL_TZ)
    return "3d" if (now.weekday() == 0 and now.hour < 12) else GNEWS_WHEN


# ── Covered-name aliases (used by enforce_covered_inclusion safety net) ─────
# Maps ticker → list of company-name strings that mean the same thing in
# news headlines. Any DIRECT-source headline containing one of these names
# is FORCE-INCLUDED in the digest (curator cannot drop it).
# Added 2026-05-25 after Cogna arbitração story was at risk of being missed.
COVERED_NAME_ALIASES = {
    # Hospitals — subsidiaries, brand names, ticker variants
    # NB: "São Luiz" removed — collides with city name "São Luiz do Paraitinga"
    "RDOR":  ["Rede D'Or", "Rede DOr", "Rede d'Or", "RedeDor", "Rede D Or",
              "RDOR3", "SulAmérica", "SulAmerica"],
    "ONCO":  ["Oncoclínicas", "Oncoclinicas", "Oncoclínica", "Oncoclinica",
              "ONCO3", "Grupo Oncoclínicas"],
    # Health plans
    "HAPV":  ["Hapvida", "Notre Dame Intermédica", "Notre Dame Intermedica",
              "NotreDame", "GNDI", "HAPV3", "Maxihealth"],
    "ODPV":  ["Odontoprev", "ODPV3", "OdontoPrev"],
    "SAUD":  ["Bradsaúde", "Bradesco Saúde", "BradSaúde", "Bradsaude",
              "SAUD3", "Bradesco Saude"],
    # Diagnostics
    "FLRY":  ["Fleury", "FLRY3", "Grupo Fleury", "Diagnóstika",
              "a+ Medicina Diagnóstica"],
    # Pharma
    "BLAU":  ["Blau Farmacêutica", "Blau Farmaceutica", "BLAU3"],
    # Higher Education — subsidiaries are KEY
    # NB: "Saber" removed — collides with Portuguese verb "to know"
    # NB: "Vasta" removed — collides with adj "vast"
    # NB: "Anima"/"Anima Educacao" require accented "Ânima Educação" form
    #     because "anima" is a common Portuguese verb ("to liven up")
    "YDUQ":  ["YDUQS", "Yduqs", "Estácio", "Estacio", "YDUQ3", "Adtalem Brasil",
              "Damásio Educacional", "Wyden", "iBMEC"],
    "COGN":  ["Cogna", "Kroton", "COGN3", "PNLD Cogna"],
    "ANIM":  ["Ânima Educação", "Ânima Holding", "ANIM3", "UniBH",
              "UniRitter", "Inspirali", "Faseh"],
    "AFYA":  ["Afya", "Afya Educacional"],
    "LAUR":  ["Laureate", "Anhembi Morumbi"],
}


# ── Coverage Universe — Sectors ───────────────────────────────────────────────
#
# Tickers (12 total + 2 US peers worth tracking closely):
#   Hospitals / Health Services:   RDOR, ONCO
#   Health Plans (Payers):          HAPV, ODPV, SAUD
#   Diagnostics:                    FLRY
#   Pharma:                         BLAU
#   Higher Education:               YDUQ, COGN, ANIM, AFYA, LAUR
#
# Peer companies are non-covered names whose news still matters for read-across.

# ── SECTORS — restructured 2026-06-03 into 6 themes (3 health + GLP-1 + 2 edu) ──
# Goal: rebalance vs the old 6-health-vs-1-education layout, GLP-1 kept separate,
# education split into Companies vs Policy/Medicine. No keywords lost in the merge.
SECTORS = {
    "Health - Providers": {
        # Hospitals and Health Services + Diagnostics consolidated
        "covered": ["RDOR", "ONCO", "FLRY"],
        "peers": [
            # Hospitals
            "Rede D'Or", "Rede DOr", "Sao Luiz",
            "Oncoclinicas", "Oncoclínicas",
            "Albert Einstein", "Sirio Libanes", "Sírio Libanês",
            "Dasa hospital", "Mater Dei", "Hospital BP", "Beneficência Portuguesa",
            "Hospital 9 de Julho", "Hospital Samaritano",
            "Hospital Moinhos de Vento", "Hcor",
            "Alliança Saúde", "Allianca Saude", "Alliança hospital",
            "Kora Saúde", "Kora Saude",
            "Athena Saúde", "Athena Saude",
            "Amico", "Hospital São Camilo", "São Camilo",
            # Diagnostics
            "Fleury", "Dasa", "Pardini", "Hermes Pardini", "Sabin",
            "Alvorada laboratório", "Salomão Zoppi",
        ],
        "keywords": [
            # Hospitals — covered company variants
            "Rede D'Or", "Rede DOr", "RDOR", "São Luiz", "Sao Luiz",
            "Hospital São Luiz", "DF Star", "Quinta D'Or", "Caxias D'Or",
            "Rede D'Or São Luiz", "RDOR3",
            "Oncoclínicas", "Oncoclinicas", "ONCO3", "ONCO oncologia",
            "Oncoclínicas clínicas", "Oncoclínicas radioterapia",
            "Onco imuno-oncologia", "Onco infusão",
            # Hospitals — operational signals
            "leitos hospital", "leitos privados", "hospital privado Brasil",
            "rede hospitalar", "expansão hospitalar", "novo hospital Brasil",
            "M&A hospital Brasil", "consolidação hospitalar",
            "oncologia Brasil", "tratamento câncer Brasil", "imuno-oncologia Brasil",
            "tratamento oncológico Brasil", "radioterapia Brasil",
            "verticalização HMO Brasil",
            "Mater Dei hospital", "Dasa hospitais", "Albert Einstein hospital",
            "Sírio Libanês hospital", "Hcor hospital",
            "Beneficência Portuguesa hospital", "Hospital 9 de Julho",
            "Alliança Saúde", "Allianca Saude", "Kora Saúde",
            "Athena Saúde", "Amico hospital",
            "residência médica Brasil", "residência enfermagem Brasil",
            "falta de médicos hospital", "déficit enfermeiros Brasil",
            "MEC residência médica", "expansão residência saúde",
            # Diagnostics — covered company variants
            "Fleury", "FLRY", "FLRY3", "Fleury B2B", "Fleury lab to lab",
            "Fleury patologia", "Fleury imagem", "Fleury medicina diagnóstica",
            "Hermes Pardini Fleury", "Saúde iD Fleury", "Saúde iD premium",
            "Dasa diagnóstico", "Pardini lab", "Sabin diagnóstico",
            "laboratório clínico Brasil", "análises clínicas Brasil",
            "diagnóstico por imagem Brasil", "medicina diagnóstica Brasil",
            "exames laboratoriais Brasil", "diagnóstico Brasil",
            "consolidação laboratórios Brasil",
        ],
    },

    "Health - Payers & Pharma": {
        # Health Plans + Pharma consolidated
        "covered": ["HAPV", "ODPV", "SAUD", "BLAU"],
        "peers": [
            # Payers
            "Hapvida", "Notre Dame Intermedica", "Notre Dame Intermédica", "GNDI",
            "Bradesco Saúde", "Bradsaude", "SulAmérica saúde", "SulAmerica saude",
            "Amil", "Porto Saúde", "Porto Seguro saude",
            "Odontoprev", "Caixa Seguros odonto",
            "Unimed", "Prevent Senior",
            # Pharma
            "Blau Farmacêutica", "Blau Farmaceutica", "BLAU",
            "Eurofarma", "EMS farmacêutica", "Aché", "Hypera",
            "Cristália farma",
        ],
        "keywords": [
            # Payers — covered company variants
            "Hapvida", "HAPV", "HAPV3", "GNDI", "Intermédica",
            "Notre Dame Intermédica", "Hapvida verticalização",
            "rede própria Hapvida", "MLR Hapvida",
            "Bradesco Saúde", "Bradsaúde", "SAUD",
            "Bradesco Seguros saúde", "vidas BradSaúde",
            "Odontoprev", "ODPV", "ODPV3", "plano odontológico",
            "SulAmérica saúde", "Amil", "Porto Saúde", "Unimed",
            "Prevent Senior", "Hapvida vs Amil",
            # Payers — regulator & KPIs
            "ANS", "ANS reajuste", "ANS regulação", "ANS portabilidade",
            "ANS resolução normativa", "ANS RN", "ANS RN reajuste",
            "ANS rol de procedimentos", "ANS notícias",
            # ANS DATA releases — recurring monthly beneficiários/vidas data,
            # material for HAPV/SAUD/ODPV (added 2026-06-03 after the "ANS divulga
            # números de beneficiários" release wasn't tracked cleanly).
            "ANS divulga dados", "ANS divulga beneficiários", "ANS beneficiários",
            "ANS números beneficiários", "beneficiários planos de saúde",
            "vidas planos de saúde", "ANS dados saúde suplementar",
            "ANS painel beneficiários",
            "MLR Brasil", "MLR plano saúde", "sinistralidade plano saúde",
            "sinistralidade saúde suplementar", "MCR plano de saúde",
            "VCMH variação custo médico", "inflação médica",
            "reajuste plano de saúde", "reajuste plano coletivo",
            "reajuste plano individual", "rol procedimentos ANS",
            "plano de saúde individual", "plano de saúde coletivo",
            "verticalização saúde", "operadora plano de saúde",
            "preço plano de saúde", "tabela plano saúde",
            "carência plano de saúde", "portabilidade plano saúde",
            "frequência utilização saúde", "diagnoses related group DRG Brasil",
            # Pharma — covered company variants
            "Blau Farmacêutica", "Blau Farmaceutica", "BLAU", "BLAU3",
            "Blau hemoderivados", "Blau biológicos", "Blau especialidades",
            "Blau hospital channel", "Blau alta complexidade",
            "Eurofarma", "EMS farmacêutica", "Hypera farma", "Aché farma",
            "Cristália farma",
            "medicamento Brasil", "biossimilar Brasil", "biológicos Brasil",
            "ANVISA", "ANVISA aprovação", "ANVISA registro",
            "PNI vacinas", "compras governo medicamento",
            "alta complexidade medicamento", "alto custo medicamento",
            "PCDT protocolo clínico", "judicialização medicamento",
            "CMED preço medicamento", "lista CMED",
            "medicamento órfão Brasil",
            # Pharma — drug-discovery / AI
            "drug discovery AI", "pharma AI", "descoberta de medicamentos IA",
            "Isomorphic Labs", "AlphaFold pharma",
            "biotech IA Brasil", "farma inteligência artificial",
            "automação descoberta fármacos",
        ],
    },

    "Cross-cutting (GLP-1)": {
        # GLP-1 affects payers (HAPV/SAUD) and hospitals (RDOR/ONCO) and diagnostics (FLRY)
        # Kept as its OWN theme per owner request (restructure 2026-06-03).
        "covered": [],
        "peers": ["Mounjaro", "Ozempic", "Wegovy", "Zepbound"],
        "keywords": [
            "GLP-1 Brasil", "GLP-1 reembolso", "GLP-1 cobertura",
            "GLP1 Brasil", "anti-obesidade medicamento",
            "semaglutida Brasil", "tirzepatida Brasil",
            "Ozempic Brasil", "Wegovy Brasil", "Mounjaro Brasil",
            "rol GLP-1", "ANS GLP-1", "cobertura emagrecedor",
            "judicialização GLP-1", "plano saúde cobertura emagrecedor",
            "ANVISA emagrecedor", "ANVISA GLP-1",
            "contrabando emagrecedor", "contrabando Ozempic",
            "Mounjaro SUS", "GLP-1 SUS", "Ozempic SUS",
            "fila Mounjaro", "fila Ozempic", "falta Wegovy",
            "Mounjaro mercado paralelo", "Ozempic ilegal",
            "Senado Mounjaro", "Senado SUS Mounjaro",
            "ampliação acesso Mounjaro", "ampliação cobertura GLP-1",
        ],
    },

    "Public Health & Regulation": {
        # Epidemiology/outbreaks + general health regulation & macro consolidated.
        "covered": [],
        "peers": [],
        "keywords": [
            # Epidemiology / outbreaks
            "dengue Brasil", "surto dengue", "epidemia dengue", "alerta dengue",
            "casos dengue Brasil", "alerta arboviroses",
            "zika Brasil", "chikungunya Brasil", "febre amarela Brasil",
            "gripe H1N1 Brasil", "Influenza Brasil", "Influenza surto",
            "vírus respiratório Brasil", "SRAG Brasil",
            "COVID Brasil 2026", "nova variante COVID Brasil",
            "sarampo Brasil", "meningite Brasil", "hepatite surto Brasil",
            "vacinação Brasil 2026", "cobertura vacinal Brasil",
            "PNI vacinação", "campanha vacinação",
            "Ministério Saúde alerta", "Anvisa alerta epidemiológico",
            "Fiocruz alerta", "boletim epidemiológico Brasil",
            "El Niño dengue", "clima dengue Brasil",
            # Health regulation & macro
            "ANVISA notícias", "ANVISA regulação",
            "judicialização saúde",
            "Saúde Suplementar", "SUS Brasil",
            "reforma tributária saúde", "imposto serviços saúde", "CVM saúde",
        ],
    },

    "Education - Companies": {
        # Company-specific education news (earnings, M&A, ratings, brands, KPIs)
        "covered": ["YDUQ", "COGN", "ANIM", "AFYA", "LAUR"],
        "peers": [
            "YDUQS", "Estácio", "Estacio",
            "Cogna", "Kroton", "Vasta Educação",
            "Ânima Educação", "Inspirali",
            "Afya", "Afya Educacional",
            "Laureate Educação", "Adtalem", "Strategic Education", "Grand Canyon",
            "Cruzeiro do Sul Educacional", "Adtalem Brasil",
        ],
        "keywords": [
            # Tickers + parent names (ambiguous bare words removed 2026-06-02 —
            # "Saber"/"Anima"/"Vasta"/"Laureate" flooded the sector with noise)
            # "Estácio" qualified 2026-06-03 — bare "Estácio" pulled Rio-
            # neighborhood noise (crashes, Sesc events). Company is still caught
            # via YDUQS/YDUQ3 and the qualified brand queries below.
            "YDUQS", "YDUQ", "universidade Estácio", "Estácio YDUQS",
            "Cogna", "COGN", "Kroton", "Vasta Educação",
            "Ânima Educação", "ANIM", "Inspirali",
            "Afya", "AFYA",
            "Laureate Educação", "LAUR",
            # Subsidiary brands
            "Anhanguera", "Pitágoras", "Uniderp", "Unime",
            "Wyden", "iThink Medical", "Medcel",
            "Centro Universitário Una", "UniBH", "Unifacs", "São Judas",
            "Anhembi Morumbi", "UAM Anhembi",
            "Cruzeiro do Sul Educacional",
            # Operating KPIs
            "captação aluno", "captação alunos", "captação ensino superior",
            "ticket médio ensino superior", "ticket médio aluno",
            "evasão ensino superior", "evasão graduação",
            "mensalidade faculdade", "reajuste mensalidade",
        ],
    },

    "Education - Policy & Medicine": {
        # Regulation, EAD, financing, medicine vagas, quality assessments — sector/policy
        "covered": [],
        "peers": [],
        "keywords": [
            # MEC regulation + key programs
            "MEC", "MEC EAD", "MEC regulação", "portaria MEC", "decreto educação",
            "recredenciamento MEC", "credenciamento institucional",
            "CNE Conselho Nacional Educação", "MEC notícias", "MEC portaria",
            "MEC EAD regulação",
            # EAD as the dominant regulatory story
            "EAD", "ensino a distância", "ensino à distância", "ensino digital",
            "polos EAD", "polo de apoio presencial", "lei EAD",
            "regulamentação EAD",
            # Higher-ed market
            "educação superior Brasil", "ensino superior Brasil",
            "IES instituição ensino superior", "IES privada",
            # Government student-financing programs
            "FIES", "PROUNI", "Pé-de-meia",
            "inadimplência FIES", "calote FIES", "default FIES",
            # Medicine vagas (single biggest driver for YDUQ/ANIM/AFYA)
            "medicina vagas", "vagas medicina", "abertura vagas medicina",
            "mais médicos", "Programa Mais Médicos",
            "escolas de medicina Brasil", "curso de medicina autorização",
            # Quality assessments (MEC-administered)
            "ENEM", "ENADE", "CPC Conceito Preliminar",
            "IGC Índice Geral Cursos",
            # CNE / CES regulatory acts
            "CNE/CES", "CNE resolução", "CNE parecer", "CNE/CES resolução",
            "Conselho Nacional Educação resolução",
            "resolução educação superior", "parecer CNE",
            "Diário Oficial educação", "Diário Oficial MEC",
            "DOU resolução educação",
            # K-12
            "novo ensino médio", "reforma ensino médio",
            "educação profissional", "ensino técnico",
            "PNAE livros didáticos", "FNDE compra livros",
            "PNE Plano Nacional Educação",
            # Education macro/tax
            "PEC educação", "reforma tributária educação", "imposto educação",
            "CVM educação",
        ],
    },
}


# ── Flat keyword list (auto-derived) ──────────────────────────────────────────
def get_all_keywords():
    seen = set()
    out  = []
    for sector_data in SECTORS.values():
        for kw in sector_data["keywords"]:
            if kw not in seen:
                seen.add(kw)
                out.append(kw)
    return out

ALL_KEYWORDS = get_all_keywords()


# ── Google News editions ──────────────────────────────────────────────────────
EDITIONS = [
    {"lang": "pt-BR", "country": "BR"},
    {"lang": "en",    "country": "US"},
]

ED_BR  = EDITIONS[0]
ED_US  = EDITIONS[1]


# ── Keyword → edition routing ─────────────────────────────────────────────────
# H&E coverage is overwhelmingly Brazilian. We use BR edition for almost
# everything, US edition only for: AFYA, LAUR (NASDAQ-listed), GLP-1 themes,
# and global pharma peers.

_BR_MARKERS = (
    # Brazilian indicators — broad match
    "brasil", "brasileir", "ans", "mec", "anvisa", "fies", "prouni", "sus",
    "rede d'or", "rdor", "hapvida", "hapv", "gndi", "intermédica",
    "bradesco saúde", "sulamérica", "amil", "porto saúde",
    "odontoprev", "odpv", "saud",
    "oncoclínicas", "onco oncologia",
    "fleury", "flry", "dasa", "pardini", "sabin",
    "blau", "eurofarma", "ems", "hypera",
    "yduqs", "yduq", "estácio", "cogna", "cogn", "kroton", "vasta", "saber",
    "ânima", "anim", "inspirali",
    "albert einstein", "sirio", "mater dei",
    "leitos", "sinistralidade", "mlr", "reajuste plano",
    "ensino", "educação superior", "medicina vagas", "ead",
    "judicialização", "saúde suplementar",
    "anatel", "cvm", "pec",
    "tabela plano", "rol procedimentos",
    "pé-de-meia",
)

_US_MARKERS = (
    # US-listed / English-language indicators — kept minimal per Rafael's rule:
    # focus on coverage, drop US peer noise. Only AFYA + LAUR (which trade on
    # NASDAQ and have US-listed coverage) and English-language search terms
    # for global drug names trigger US edition.
    "afya", "laureate", "laur",
    "obesity drug",
)

# Universal — fire across both editions
_UNIVERSAL = (
    "afya", "laur",  # cross-listed names
)


def _match_any(text_lower: str, markers) -> bool:
    for m in markers:
        if m.startswith("^"):
            if text_lower.startswith(m[1:]):
                return True
        elif m in text_lower:
            return True
    return False


def keyword_editions(kw: str):
    """Return the editions to query for a given keyword."""
    kw_lower = kw.lower()
    if _match_any(kw_lower, _UNIVERSAL):
        return EDITIONS
    if _match_any(kw_lower, _US_MARKERS):
        return [ED_US]
    if _match_any(kw_lower, _BR_MARKERS):
        return [ED_BR]
    # Default for H&E: Brazilian edition (vast majority of coverage is local)
    return [ED_BR]


def get_query_tasks():
    """Build the (keyword, edition) list with per-keyword edition routing."""
    tasks = []
    for kw in ALL_KEYWORDS:
        for ed in keyword_editions(kw):
            tasks.append((kw, ed))
    return tasks


# ── Direct sources (the 22 you listed + Valor health/education sub-feeds) ────
# rss: tried first (RSS/Atom are far more reliable than HTML scraping)
# url: HTML fallback if rss is empty or fails

DIRECT_SOURCES = [
    # ── General BR financial / business press ─────────────────────────────────
    {
        "name": "O Globo Últimas",
        "url":  "https://oglobo.globo.com/ultimas-noticias/",
        "rss":  "https://oglobo.globo.com/rss/oglobo",
        "sector": "General",
    },
    {
        # 2026-06-02: O Globo's dedicated education section feed (pox.globo.com)
        # — 100 items. Strong education-volume source.
        "name": "O Globo Educação",
        "url":  "https://oglobo.globo.com/brasil/educacao/",
        "rss":  "https://pox.globo.com/rss/oglobo/brasil/educacao",
        "sector": "Education",
    },
    {
        "name": "Brazil Journal",
        "url":  "https://braziljournal.com/",
        "rss":  "https://braziljournal.com/feed/",
        "sector": "General",
    },
    {
        # 2026-05-22: fixed dead /arc/outboundfeeds/rss/ URL (404).
        # Working feed is /rss/pipelinevalor (pox.globo.com-style).
        "name": "Pipeline Valor",
        "url":  "https://pipelinevalor.globo.com/",
        "rss":  "https://pipelinevalor.globo.com/rss/pipelinevalor",
        "sector": "General",
    },
    {
        "name": "NeoFeed",
        "url":  "https://neofeed.com.br/",
        "rss":  "https://neofeed.com.br/feed/",
        "sector": "General",
    },
    {
        # 2026-05-21: was using /feed/ (404). Real Arc-CMS feed lives at
        # /arc/outboundfeeds/rss.xml — fixed. Returns 100 items per fetch.
        "name": "Bloomberg Línea Brasil",
        "url":  "https://www.bloomberglinea.com.br/",
        "rss":  "https://www.bloomberglinea.com.br/arc/outboundfeeds/rss.xml",
        "sector": "General",
    },
    {
        "name": "Bloomberg Línea",
        "url":  "https://www.bloomberglinea.com/",
        "rss":  "https://www.bloomberglinea.com/arc/outboundfeeds/rss.xml",
        "sector": "General",
    },
    {
        "name": "Bloomberg Línea México",
        "url":  "https://www.bloomberglinea.com.mx/",
        "rss":  "https://www.bloomberglinea.com/arc/outboundfeeds/rss/latinoamerica/mexico.xml",
        "sector": "General",
    },
    {
        # 2026-06-01: arc/outboundfeeds RSS now 404s. Switched to the live
        # canonical Valor feed (advertised on the section pages) — 100 items.
        "name": "Valor Econômico Últimas",
        "url":  "https://valor.globo.com/ultimas-noticias/",
        "rss":  "https://valor.globo.com/rss/valor",
        "sector": "General",
    },
    {
        # 2026-06-01: Valor PRINT edition feed (pox.globo.com) — 100 items,
        # carries the high-value print pieces (education/health/business deep
        # dives) that don't appear in the general web feed. Added after the
        # "Mensalidade cai 33% em universidades" education story was missed.
        "name": "Valor Impresso",
        "url":  "https://valor.globo.com/impresso/",
        "rss":  "https://pox.globo.com/rss/valor/impresso",
        "sector": "General",
    },
    {
        "name": "Estadão",
        "url":  "https://www.estadao.com.br/ultimas/",
        "rss":  "https://www.estadao.com.br/arc/outboundfeeds/rss/",
        "sector": "General",
    },
    {
        "name": "Veja",
        "url":  "https://veja.abril.com.br/ultimas-noticias/",
        "rss":  "https://veja.abril.com.br/feed/",
        "sector": "General",
    },
    {
        "name": "Folha Últimas",
        "url":  "https://www1.folha.uol.com.br/ultimas-noticias/",
        "rss":  "https://www1.folha.uol.com.br/feed/",
        "sector": "General",
    },

    # ── Health-specific ───────────────────────────────────────────────────────
    {
        # 2026-06-02: pointed at Valor's dedicated HEALTH section feed on
        # pox.globo.com (the arc/outboundfeeds one 404s; the general rss/valor
        # was injecting only general noise into the Health bucket). Low-volume
        # but on-target; Valor Impresso above carries the bigger print pieces.
        "name": "Valor Saúde",
        "url":  "https://valor.globo.com/empresas/saude/",
        "rss":  "https://pox.globo.com/rss/valor/empresas/saude",
        "sector": "Health",
    },
    {
        "name": "Folha Equilíbrio e Saúde",
        "url":  "https://www1.folha.uol.com.br/equilibrioesaude/",
        "rss":  "https://www1.folha.uol.com.br/equilibrioesaude/rss091.xml",
        "sector": "Health",
    },
    {
        # Veja Saúde — dedicated health-section RSS (separate from Veja main feed
        # which is capped at 10 items and rarely surfaces health pieces).
        # Caught: "7 a 1 das canetas emagrecedoras diante da cirurgia bariátrica" class.
        "name": "Veja Saúde",
        "url":  "https://veja.abril.com.br/saude/",
        "rss":  "https://veja.abril.com.br/saude/feed",
        "sector": "Health",
    },
    {
        "name": "MedicinaS/A",
        "url":  "https://medicinasa.com.br/ultimas-noticias/",
        "rss":  "https://medicinasa.com.br/feed/",
        "sector": "Health",
    },
    {
        "name": "Futuro da Saúde",
        "url":  "https://futurodasaude.com.br/",
        "rss":  "https://futurodasaude.com.br/feed/",
        "sector": "Health",
    },
    {
        "name": "Saúde Business",
        "url":  "https://www.saudebusiness.com/",
        "rss":  "https://www.saudebusiness.com/feed/",
        "sector": "Health",
    },
    {
        "name": "ANS Notícias",
        "url":  "https://www.gov.br/ans/pt-br/assuntos/noticias",
        "rss":  "",   # gov.br portals are JS-rendered; HTML fallback
        "sector": "Health Regulatory",
    },
    {
        "name": "Ministério da Saúde Notícias",
        "url":  "https://www.gov.br/saude/pt-br/assuntos/noticias",
        "rss":  "",   # gov.br — HTML fallback
        "sector": "Health Regulatory",
    },

    # ── Education-specific ────────────────────────────────────────────────────
    {
        # 2026-06-02: pointed at Valor's dedicated EDUCATION section feed on
        # pox.globo.com (the arc/outboundfeeds one 404s; the general rss/valor
        # was injecting only general noise into the Education bucket). Low-volume
        # but on-target; Valor Impresso above carries the bigger print education
        # deep-dives (e.g. "Mensalidade cai 33% em universidades").
        "name": "Valor Educação",
        "url":  "https://valor.globo.com/empresas/educacao/",
        "rss":  "https://pox.globo.com/rss/valor/empresas/educacao",
        "sector": "Education",
    },
    {
        "name": "Folha Educação",
        "url":  "https://www1.folha.uol.com.br/educacao/",
        "rss":  "https://www1.folha.uol.com.br/educacao/rss091.xml",
        "sector": "Education",
    },
    {
        # Veja Educação — dedicated education-section RSS
        "name": "Veja Educação",
        "url":  "https://veja.abril.com.br/educacao/",
        "rss":  "https://veja.abril.com.br/educacao/feed",
        "sector": "Education",
    },
    {
        # 2026-06-02: higher-ed sector trade press — regulation, EAD, avaliação,
        # jurídico. Directly relevant to the covered private-education names
        # (YDUQ/COGN/ANIM/AFYA). ~13 items via RSS.
        "name": "Revista Ensino Superior",
        "url":  "https://revistaensinosuperior.com.br/",
        "rss":  "https://revistaensinosuperior.com.br/feed/",
        "sector": "Education",
    },
    {
        # 2026-06-02: official news agency, education desk — reliable, clean
        # (Enem, MEC, public-university news). Low volume but high signal.
        "name": "Agência Brasil Educação",
        "url":  "https://agenciabrasil.ebc.com.br/educacao",
        "rss":  "https://agenciabrasil.ebc.com.br/rss/educacao/feed.xml",
        "sector": "Education",
    },
    {
        # MEC Notícias (gov.br) — works because gov.br portals server-render
        # their news lists (unlike the in.gov.br Diário Oficial reader, which
        # is JS-rendered and only returned page-chrome navigation).
        "name": "MEC Notícias",
        "url":  "https://www.gov.br/mec/pt-br/assuntos/noticias",
        "rss":  "",   # gov.br — HTML fallback
        "sector": "Education Regulatory",
    },
    {
        # 2026-06-02: upgraded from HTML scrape (~9 items) to the pox.globo.com
        # RSS feed (100 items) — big education-volume gain.
        "name": "G1 Educação",
        "url":  "https://g1.globo.com/educacao/",
        "rss":  "https://pox.globo.com/rss/g1/educacao",
        "sector": "Education",
    },

    # ── Health-specific (additional) ──────────────────────────────────────────
    {
        "name": "G1 Ciência e Saúde",
        "url":  "https://g1.globo.com/ciencia-e-saude/",
        "rss":  "",   # HTML scrape
        "sector": "Health",
    },
    {
        # G1 root firehose — broad coverage, relies on keyword filter + curator
        # triage to surface H&E-relevant pieces (politics/sports/entertainment
        # noise dropped at curation stage). User-requested 2026-05-20.
        "name": "G1",
        "url":  "https://g1.globo.com/",
        "rss":  "https://g1.globo.com/rss/g1/",
        "sector": "General",
    },

    # ── Legal / regulatory ────────────────────────────────────────────────────
    {
        "name": "JOTA",
        "url":  "https://www.jota.info/",
        "rss":  "https://www.jota.info/feed",
        "sector": "Regulatory",
    },

    # NOTE (2026-05-21): WSJ cannot be added as a direct source.
    # - All public RSS feeds deprecated Jan 2025 (last build 16+ months stale).
    # - HTML scrape returns HTTP 401 Forbidden (paywall + bot detection).
    # WSJ articles still surface via Google News — see SOURCES_ALLOWLIST below
    # where we boost WSJ-attributed items for dedup priority.

    # ── Health & education regulators / industry (added 2026-05-21) ───────────
    {
        "name": "Anvisa Notícias",
        "url":  "https://www.gov.br/anvisa/pt-br",
        "rss":  "",   # gov.br — HTML scrape; root URL works (subpaths 404)
        "sector": "Health Regulatory",
    },
    {
        "name": "Inep Assuntos",
        "url":  "https://www.gov.br/inep/pt-br/assuntos",
        "rss":  "",
        "sector": "Education Regulatory",
    },
    {
        "name": "CADE Notícias",
        "url":  "https://www.gov.br/cade/pt-br/assuntos/noticias",
        "rss":  "",
        "sector": "Health Regulatory",  # antitrust — hospital/pharma M&A
    },
    {
        # Private-hospitals association — direct industry data on HAPV/RDOR/
        # FLRY/ONCO operating environment, payer-provider dynamics.
        "name": "Anahp",
        "url":  "https://anahp.com.br/noticias/",
        "rss":  "https://anahp.com.br/feed/",
        "sector": "Health",
    },
    {
        # Biopharma deal-flow newsletter — FDA approvals, LLY/NVO/AbbVie
        # pipeline, material for cross-cutting GLP-1 + pharma sector tags.
        "name": "Endpoints News",
        "url":  "https://endpts.com/",
        "rss":  "https://endpts.com/feed/",
        "sector": "Pharma",
    },
    # NOTE: Reuters Healthcare (reuters.com/business/healthcare-pharmaceuticals)
    # returns HTTP 401 Forbidden (same paywall situation as WSJ). Stories surface
    # via Google News — see SOURCES_ALLOWLIST for dedup-priority boost.

    # ── Specialist additions (2026-05-22) — user-approved batch ───────────────
    {
        # National Commission for Health Technology Incorporation. Drug/device
        # approval for SUS — direct read on what gets covered (oncology, GLP-1,
        # rare-disease). Critical regulatory source for pharma + payer impact.
        "name": "CONITEC Notícias",
        "url":  "https://www.gov.br/conitec/pt-br/assuntos/noticias",
        "rss":  "",   # gov.br HTML scrape
        "sector": "Health Regulatory",
    },
    {
        # Conselho Federal de Medicina — doctor regulator. Pricing/scope rules
        # that affect hospital networks (RDOR/HAPV/ONCO).
        "name": "CFM Portal",
        "url":  "https://portal.cfm.org.br/",
        "rss":  "",
        "sector": "Health Regulatory",
    },
    {
        # Câmara dos Deputados — Comissão de Seguridade Social e Família.
        # Health-related bill tracking.
        "name": "Câmara Saúde",
        "url":  "https://www2.camara.leg.br/atividade-legislativa/comissoes/comissoes-permanentes/cssf",
        "rss":  "",
        "sector": "Health Regulatory",
    },
    {
        # US biopharma trade. FDA approvals, clinical trials, M&A —
        # complements Endpoints News for LLY/NVO/AbbVie pipeline visibility.
        "name": "STAT News",
        "url":  "https://www.statnews.com/",
        "rss":  "https://www.statnews.com/feed/",
        "sector": "Pharma",
    },
    {
        # Pharma industry trade. Drug launches, M&A, regulatory.
        "name": "FiercePharma",
        "url":  "https://www.fiercepharma.com/",
        "rss":  "https://www.fiercepharma.com/rss/xml",
        "sector": "Pharma",
    },

    # ── Brazilian financial portals (added 2026-05-22) — sell-side coverage ──
    # User flagged noise from non-reliable outlets on 2026-05-22; tightened EXT
    # cap to 2 AND adding these as DIRECT so sell-side coverage of HAPV/RDOR/
    # ONCO/FLRY/YDUQ/COGN/ANIM (BTG/Itaú/XP/Bradesco views, ratings, target
    # prices, earnings recaps) flows in without burning EXT slots.
    {
        "name": "InfoMoney",
        "url":  "https://www.infomoney.com.br/",
        "rss":  "https://www.infomoney.com.br/feed/",
        "sector": "Sell-side",
    },
    {
        "name": "Money Times",
        "url":  "https://www.moneytimes.com.br/",
        "rss":  "https://www.moneytimes.com.br/feed/",
        "sector": "Sell-side",
    },
    {
        "name": "Seu Dinheiro",
        "url":  "https://www.seudinheiro.com/",
        "rss":  "https://www.seudinheiro.com/feed/",
        "sector": "Sell-side",
    },
    {
        "name": "Suno",
        "url":  "https://www.suno.com.br/noticias/",
        "rss":  "https://www.suno.com.br/noticias/feed/",
        "sector": "Sell-side",
    },

    # ── Terra Saúde + Educação (added 2026-05-25, user-approved) ─────────────
    # Terra has no working RSS (all paths 404), but its Saúde and Educação
    # sub-sections have 300-400 article links per scrape. Caveat: mostly
    # wire-service reposts (AFP/Reuters via Terra) — adds breadth, may
    # duplicate stories already caught by Valor/Folha/O Globo direct sources.
    # Sub-sections only (not the root) to keep political/sports noise out.
    {
        "name": "Terra Saúde",
        "url":  "https://www.terra.com.br/vida-e-estilo/saude/",
        "rss":  "",
        "sector": "Health",
    },
    {
        "name": "Terra Educação",
        "url":  "https://www.terra.com.br/noticias/educacao/",
        "rss":  "",
        "sector": "Education",
    },

    # NOTE: CVM RAD (https://www.rad.cvm.gov.br/ENET/frmConsultaExternaCVM.aspx)
    # is intentionally NOT scraped here — it's a JS-rendered ASP.NET portal that
    # requires session-based interaction. Per planning Q5 decision, defer to v2.
]


# ── Source allowlist (used by Google News priority ranking, not as filter) ────
SOURCES_ALLOWLIST = [
    # H&E-specific outlets
    "MedicinaS/A", "Futuro da Saúde", "Saúde Business", "Saude Business",
    "Valor", "Valor Econômico", "Pipeline", "Brazil Journal",
    "NeoFeed", "Bloomberg Línea", "Bloomberg Linea",
    "Estadão", "Folha", "Folha de S.Paulo",
    "JOTA", "ANS", "Ministério da Saúde", "MEC", "ANVISA",
    "Reuters", "Bloomberg", "Financial Times", "FT",
    "WSJ", "Wall Street Journal", "wsj.com",  # surfaced via Google News only
    "Reuters Healthcare", "Reuters Pharma", "Reuters Brasil",  # paywalled — gnews-only
    "Bloomberg Technology", "Bloomberg.com",  # main Bloomberg paywalled — gnews-only
    "Bloomberg Línea", "Bloomberg Linea",     # already direct — boost dedup priority
    "Anvisa", "Inep", "Anahp", "CADE",        # also in direct sources — allowlist ensures dedup priority
    "Endpoints", "Endpoints News",
    "Veja",
    # Sell-side / market wire
    "Money Times", "InfoMoney", "Suno", "Genial Investimentos",
    "XP Investimentos", "BTG Pactual", "Itaú BBA", "Bradesco BBI", "Safra",
]


# ── Pre-filter caps (input to Claude; Claude does the final 50-item curation) ─
MAX_HEADLINES_PER_SECTOR = 80
MAX_TOTAL_HEADLINES      = 400

# Final Claude-curated digest cap.
# 2026-05-25: set to 60. 60 material items across 2-3 daily runs without
# repetition is already very high; cap should be a safety, not a target.
MAX_DIGEST_ITEMS = 60


# ── Sector display order (used by email + markdown renderers) ────────────────
SECTOR_ORDER = [
    "Health - Providers",
    "Health - Payers & Pharma",
    "Cross-cutting (GLP-1)",
    "Public Health & Regulation",
    "Education - Companies",
    "Education - Policy & Medicine",
    "General",
    "Sell-side",   # broker rating changes — appears last before events
]


# ── Email recipients ──────────────────────────────────────────────────────────
# H&E-specific distribution list. Goes to Rafael + Eduardo + Leonardo on the
# UBS LatAm H&E team. (Eduardo + Leonardo were briefly removed earlier today
# during link-resolver testing — re-added at user request 2026-05-21.)
EMAIL_RECIPIENTS = [
    # 2026-05-26: restored after the "today-only" investigation test that
    # confirmed today (May 26) genuinely has only 1 material covered-name
    # story (COGN dividends from Suno), which the system caught. Code is
    # working correctly — today's flow is genuinely thin.
    "rafael.oliveira@ubs.com",
    "eduardo.resende@ubs.com",
    "leonardo.olmos@ubs.com",
    "bruno.gomez@ubs.com",   # added 2026-06-05
    "olavo.arthuzo@ubs.com",   # added 2026-06-11
]
