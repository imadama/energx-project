# Energx SEO Master Agent — Roadmap v1.1

**Project:** AI-gedreven SEO platform voor Energx
**Lead:** Imad
**Status:** Voorbereiding + groot deel weekend 1+2 al voltooid in versnelde sessie (mei 2026)
**Volgende milestones:** Workflow A+B importeren in Dify, FastAPI service deployen, GSC live

---

## Wat al draait (status mei 2026)

### Productie

- ✅ **Dify self-hosted** — Docker op VPS (`100.117.6.53`)
- ✅ **Ollama** met `qwen3:32b` (LLM) + `nomic-embed-text` (embeddings) op P40 GPU
- ✅ **Serper.dev** SERP API gekoppeld
- ✅ **Google AI Studio / Gemini** key actief (Gemini 2.5 Flash voor brief generator)
- ✅ **Energx KB** in Dify met 4 documenten (Tone-of-Voice, Bedrijfsprofiel, Energie-feiten, SEO-richtlijnen) — geïndexeerd via lokale nomic-embed-text
- ✅ **Brief Generator v2** in productie — KB-aware, 14-secties output, hallucination-checks
- ✅ Hit testing op KB gevalideerd (3/3 tests positief)
- ✅ Dify backup gemaakt
- ✅ Google Search Console: dev.energx.nl property + Service Account aangemaakt

### Code klaar (nog te deployen)

- ✅ **FastAPI audit-service** — 7 endpoints (health, technical/audit, content/audit, sitemap/parse, pagespeed, gsc/queries, gsc/pages), Flesch-Douma NL ingebouwd, smoke tests groen
- ✅ **Dify Workflow A DSL** (Tech Audit) — klaar voor import
- ✅ **Dify Workflow B DSL** (Content Audit) — klaar voor import

### Documenten / specs

- ✅ Knowledge Base docs A/B/C/D in `kb-doc-*-FINAL.md`
- ✅ Brief Generator system prompt v2
- ✅ Admin-checklist
- ✅ Review-feedback C en D

---

## Versnelde planning vanaf nu

We laten de weekend-cadans los — we werken door tot iets blokkeert.

### Direct (jouw handen, ~60 min)

1. **FastAPI service deployen op je VPS**
   - Kopieer `outputs/energx-audit-service/` naar je VPS (`scp -r ...` of via git)
   - Op de VPS: `cp .env.example .env`, vul `API_KEY`, `PAGESPEED_API_KEY`, `GSC_SITE_URL` in
   - Plaats GSC service-account JSON in `./credentials/gsc-service-account.json`
   - `docker compose up -d`
   - Test: `curl http://localhost:8080/health`

2. **Custom tool registreren in Dify**
   - Dify → Tools → Custom Tools → "Add via OpenAPI"
   - Schema URL: `http://<vps-tailscale-ip>:8080/openapi.json`
   - Authentication: API Key in header `Authorization: Bearer <API_KEY>`
   - Naam: `energx_audit`

3. **Workflow A en B importeren in Dify**
   - Studio → Create from Blank → Import DSL file
   - Import `workflow-a-tech-audit.yml`
   - Import `workflow-b-content-audit.yml`
   - In Workflow B: voeg handmatig de Energx KB dataset-id toe in de `kb_retrieval` node
   - Test runs uitvoeren

### Daarna (ik kan parallel doorbouwen)

4. **Workflow C DSL** — Keyword Gap Analyse (3-4 uur werk voor mij)
5. **Workflow D DSL** — Keyword Researcher (proactief, nieuw uit pauze-discussie)
6. **Master Workflow DSL** — combineert A+B+C → één rapport
7. **Frontend skeleton** — Next.js met form + status-page voor de Master Workflow

---

## Originele weekend-planning vs werkelijkheid

| Originele plan | Status | Werkelijkheid |
|---|---|---|
| Weekend 1 — Foundation & KB | ✅ Klaar | KB live, Brief Generator v2 in productie. GSC verificatie + Service Account klaar. |
| Weekend 2 — FastAPI service | 🟡 Code klaar | Service geschreven en getest, alleen nog deployment naar VPS |
| Weekend 3 — Workflow A + B | 🟡 DSLs klaar | YAMLs geschreven, nog te importeren in Dify |
| Weekend 4 — Workflow C (Keyword Gap) | ⏳ Open | Wordt uitgebreid naar Workflow C+D (zie sectie hieronder) |
| Weekend 5 — Master Workflow | ⏳ Open | Hangt af van A, B, C |
| Weekend 6 — UI / Dashboard | ⏳ Open | Voor non-technische gebruiker |

---

## Nieuwe component: Workflow D — Keyword Researcher

Proactief in plaats van reactief. Was in originele roadmap niet expliciet maar
ontdekt tijdens implementatie.

### Doel

Eén Dify-workflow die op input "thuisbatterij" (seed-thema) automatisch
ontdekt welke keywords nu hot zijn, waar Energx kansen heeft, en welke
content gemaakt moet worden.

### Architectuur

```
INPUT: seed-thema (bijv. "thuisbatterij")
  ↓
[1] Serper → top 10 SERP + related_searches + PAA per seed
  ↓
[2] Voor elke gerelateerde keyword: 2e Serper-call → diepte
  ↓
[3] FastAPI /gsc/queries → jouw eigen rankings, focus op pos 11-30 (quick wins)
  ↓
[4] Optioneel: pytrends (extra FastAPI endpoint) → trend-direction per keyword
  ↓
[5] Claude/Gemini synthese: cluster per intent, rang op kans, markeer trending
  ↓
OUTPUT: kansenlijst met prioritering (gereed voor Brief Generator)
```

### Implementatie-stappen

1. **FastAPI uitbreiden** met `/trends/keyword` endpoint (pytrends-wrapper, gratis)
2. **Dify Workflow D DSL** schrijven die bovenstaande architectuur implementeert
3. **Test op zaai-thema's:** `thuisbatterij`, `warmtepomp`, `laadpaal`, `salderingsregeling`
4. **Output validatie:** klopt de prioritering met handmatig gevoel?

### Tijdsinvestering

~6-8 uur development. Levert dagelijks/wekelijks een lijst met "hier moet je
nu content over schrijven".

---

## Master Workflow (Workflow E in v1.1)

Zelfde architectuur als origineel, maar nu met expliciete koppeling naar
nieuwe Workflow D voor proactief identificeren van content-opportunities.

```
Input: domein
  ↓
Roep parallel:
   - Workflow A (Tech Audit)
   - Workflow B (Content Audit)
   - Workflow C (Keyword Gap)
   - Workflow D (Keyword Researcher) ← NIEUW
  ↓
Aggregator-node: combineer alle outputs
  ↓
Claude/Gemini (groot context): master synthese
   • Quick wins (deze week)
   • Medium-term (komende maand)
   • Strategic (komend kwartaal)
   • Trending opportunities (deze maand, uit Workflow D)
  ↓
Voor top 10 prioriteiten: Brief Generator
  ↓
PDF-rapport + email-trigger
```

---

## Beslissingen die nog open staan

Onveranderd t.o.v. v1.0, plus:

1. **Frontend framework** — Next.js (best practice) of Laravel-stack (bestaande expertise)
2. **Workflow D - pytrends als endpoint of als losse Dify-tool?** Voorkeur: endpoint in FastAPI (consistent met andere data-tools)
3. **Concurrentieanalyse versnellen** — qwen3:32b duurt 4 min, Gemini Flash zou ~30s zijn. Migratie?

---

## Kosten-update

Niets significants veranderd. Free tier dekt nog steeds alles:
- Gemini API: free tier toereikend (1500 requests/dag op Flash)
- Ollama lokaal: €0
- Serper.dev: gebruik blijft binnen gratis 2500 queries/maand
- PageSpeed Insights: gratis API
- GSC API: gratis

Eerste betaalde upgrade waarschijnlijk pas bij Workflow D op grote schaal,
of bij Master Workflow productie-runs >100x/maand.

---

## Versie-info

Versie: 1.1 (mei 2026)
Wijzigingen t.o.v. 1.0:
- Voorbereidingsfase en grote delen weekend 1+2 toegevoegd als ✅
- Workflow D (Keyword Researcher) toegevoegd
- Accelerated planning ipv weekend-cadans
- Werkelijke vs originele planning vergelijking

Volgende review: zodra Workflow A+B draaien in productie
