# Energx Audit Service

FastAPI microservice voor de Energx SEO Master Agent. Levert technische SEO-audits, on-page audits, sitemap parsing, PageSpeed-data en Google Search Console-data als REST API. Wordt aangeroepen door Dify-workflows.

## Endpoints

| Endpoint | Methode | Doel |
|---|---|---|
| `GET /health` | GET | Healthcheck |
| `POST /technical/audit` | POST | Technische audit van één URL (status code, HTTPS, canonical, robots, schema, alt-tags, broken links) |
| `POST /content/audit` | POST | On-page content audit (title/meta lengths, H-structuur, word count, internal links, Flesch-Douma NL) |
| `POST /sitemap/parse` | POST | Parse `sitemap.xml` van een domein, return lijst van URLs |
| `POST /pagespeed` | POST | Core Web Vitals via PageSpeed Insights API |
| `POST /gsc/queries` | POST | Top zoekopdrachten + positie + clicks uit Google Search Console |
| `POST /gsc/pages` | POST | Top pagina's met impressions/clicks uit GSC |

## Quick start

### 1. Lokaal draaien (development)

```bash
cd energx-audit-service
cp .env.example .env
# Vul je API keys in .env

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

Test: `curl http://localhost:8080/health` → `{"status": "ok"}`

API-docs (Swagger): `http://localhost:8080/docs`

### 2. Docker (productie)

```bash
docker compose up -d
docker compose logs -f
```

De service draait dan op `http://localhost:8080`. Voor Dify in dezelfde Docker-netwerk: `http://energx-audit:8080`.

### 3. Op je Dify-VPS deployen

```bash
# Op je VPS:
git clone <repo-url> energx-audit-service
cd energx-audit-service
cp .env.example .env
nano .env  # vul keys in
docker compose up -d
```

Reverse proxy via Nginx of Tailscale-IP voor toegang vanuit Dify.

## Configuratie (.env)

| Variabele | Verplicht | Doel |
|---|---|---|
| `PAGESPEED_API_KEY` | optioneel | Voor PageSpeed Insights endpoint. Gratis via [Google Cloud Console](https://console.cloud.google.com/) |
| `GSC_SERVICE_ACCOUNT_JSON` | voor /gsc/* | Pad naar de Service Account JSON voor Search Console toegang |
| `GSC_SITE_URL` | voor /gsc/* | Default site URL (bijv. `sc-domain:energx.nl` of `https://dev.energx.nl/`) |
| `API_KEY` | aanbevolen | Simpele Bearer-token om je API te beschermen tegen public access |
| `LOG_LEVEL` | optioneel | `DEBUG`, `INFO` (default), `WARNING`, `ERROR` |
| `REQUEST_TIMEOUT` | optioneel | Timeout voor externe calls in seconden (default: 30) |

## Authenticatie

Als `API_KEY` is gezet, vereist elke request een header:

```
Authorization: Bearer <jouw-key>
```

## Integratie met Dify

In Dify → Tools → Custom Tools → "Add custom tool":

1. **Schema type:** OpenAPI
2. **Schema URL:** `http://<jouw-host>:8080/openapi.json`
3. **Authentication:** API Key in header `Authorization: Bearer <key>`
4. **Save** — Dify importeert alle endpoints als losse tools.

Daarna kun je in elke workflow (zoals Tech Audit, Content Audit, Master Workflow) deze tools selecteren.

## Voorbeelden

### Technische audit

```bash
curl -X POST http://localhost:8080/technical/audit \
  -H "Authorization: Bearer <key>" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://dev.energx.nl/energx-thuisbatterij.html"}'
```

Response (verkort):
```json
{
  "url": "https://dev.energx.nl/energx-thuisbatterij.html",
  "status_code": 200,
  "response_time_ms": 412,
  "https": true,
  "canonical": "https://dev.energx.nl/energx-thuisbatterij.html",
  "robots_meta": "index, follow",
  "robots_txt_allows": true,
  "schemas_found": ["Organization", "LocalBusiness"],
  "alt_tags_missing": 2,
  "broken_links": [],
  "issues": [
    {"severity": "warning", "type": "alt_missing", "detail": "2 afbeeldingen zonder alt-tag"}
  ]
}
```

### Content audit

```bash
curl -X POST http://localhost:8080/content/audit \
  -H "Content-Type: application/json" \
  -d '{"url": "https://dev.energx.nl/blog-thuisbatterij-kopen.html"}'
```

Response (verkort):
```json
{
  "url": "...",
  "title": "Thuisbatterij kopen in 2026 | Energx",
  "title_length": 38,
  "meta_description": "...",
  "meta_description_length": 152,
  "h1_count": 1,
  "h1_text": "Thuisbatterij kopen: alles wat je moet weten",
  "h2_count": 7,
  "h3_count": 12,
  "word_count": 1842,
  "internal_links": 5,
  "external_links": 3,
  "flesch_douma_score": 64.2,
  "flesch_douma_grade": "Makkelijk leesbaar (mavo/havo)",
  "issues": []
}
```

### Sitemap parser

```bash
curl -X POST http://localhost:8080/sitemap/parse \
  -d '{"domain": "https://dev.energx.nl"}'
```

### GSC top queries

```bash
curl -X POST http://localhost:8080/gsc/queries \
  -d '{"site_url": "sc-domain:energx.nl", "days": 28, "limit": 50}'
```

## Onderhoud

- **Update dependencies:** `pip install -U -r requirements.txt`
- **Logs:** `docker compose logs -f energx-audit`
- **Restart:** `docker compose restart`
- **Backup:** geen state in deze service — alles is stateless, geen DB nodig

## Volgende stappen na deployment

1. Test alle endpoints via Swagger (`/docs`)
2. Voeg toe als custom tool in Dify
3. Bouw Workflow A (Technische Site Audit) die de endpoints achter elkaar aanroept
4. Bouw Workflow B (Content Audit) idem

Versie: 1.0 (mei 2026)
