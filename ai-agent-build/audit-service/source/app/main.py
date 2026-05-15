"""
Energx Audit Service — FastAPI app.

Endpoints:
- GET  /health
- POST /technical/audit
- POST /content/audit
- POST /sitemap/parse
- POST /pagespeed
- POST /gsc/queries
- POST /gsc/pages

Authenticatie: Bearer token via API_KEY env var (optioneel).
"""

import logging

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import (
    ContentAuditRequest,
    ContentAuditResponse,
    GSCPagesRequest,
    GSCPagesResponse,
    GSCQueriesRequest,
    GSCQueriesResponse,
    PageSpeedRequest,
    PageSpeedResponse,
    SitemapRequest,
    SitemapResponse,
    TechnicalAuditRequest,
    TechnicalAuditResponse,
    TrendsRequest,
    TrendsResponse,
)
from app.services.content_audit import run_content_audit
from app.services.gsc import get_top_pages, get_top_queries
from app.services.pagespeed import run_pagespeed
from app.services.sitemap_parser import parse_sitemap
from app.services.technical_audit import run_technical_audit
from app.services.trends import get_keyword_trends


# ---------- Logging ----------
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("energx-audit")

# ---------- App ----------
app = FastAPI(
    title="Energx Audit Service",
    description=(
        "FastAPI microservice voor SEO-audits, ingeplugd in Dify-workflows. "
        "Levert technische audits, content audits, sitemap parsing, PageSpeed en GSC-data."
    ),
    version="1.0.0",
)

# CORS — alleen lokale Dify mag deze service aanroepen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in productie naar Dify-origin beperken
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---------- Auth dependency ----------

async def verify_api_key(authorization: str | None = Header(default=None)):
    """Simpele Bearer-token check. Skip als API_KEY niet is gezet (development mode)."""
    if not settings.api_key:
        return  # auth disabled
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
        )
    token = authorization.split(" ", 1)[1]
    if token != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )


# ---------- Health ----------

@app.get("/health", tags=["meta"])
async def health():
    """Healthcheck voor Docker en monitoring."""
    return {"status": "ok", "service": "energx-audit", "version": "1.0.0"}


# ---------- Technical audit ----------

@app.post(
    "/technical/audit",
    response_model=TechnicalAuditResponse,
    tags=["audit"],
    summary="Technische SEO-audit van één URL",
)
async def technical_audit(
    request: TechnicalAuditRequest,
    _: None = Depends(verify_api_key),
):
    """Status code, HTTPS, canonical, robots, schema, alt-tags, broken links."""
    logger.info(f"Technical audit: {request.url}")
    return await run_technical_audit(str(request.url))


# ---------- Content audit ----------

@app.post(
    "/content/audit",
    response_model=ContentAuditResponse,
    tags=["audit"],
    summary="On-page content audit met NL readability (Flesch-Douma)",
)
async def content_audit(
    request: ContentAuditRequest,
    _: None = Depends(verify_api_key),
):
    """Title/meta lengths, H-structuur, word count, internal links, Flesch-Douma score."""
    logger.info(f"Content audit: {request.url}")
    return await run_content_audit(str(request.url))


# ---------- Sitemap parser ----------

@app.post(
    "/sitemap/parse",
    response_model=SitemapResponse,
    tags=["sitemap"],
    summary="Parse alle sitemaps voor een domein",
)
async def sitemap_parse(
    request: SitemapRequest,
    _: None = Depends(verify_api_key),
):
    """Vindt sitemap.xml + nested sitemap-indexes via /robots.txt en standaard-paden."""
    logger.info(f"Sitemap parse: {request.domain}")
    return await parse_sitemap(str(request.domain))


# ---------- PageSpeed ----------

@app.post(
    "/pagespeed",
    response_model=PageSpeedResponse,
    tags=["pagespeed"],
    summary="Core Web Vitals via PageSpeed Insights API",
)
async def pagespeed(
    request: PageSpeedRequest,
    _: None = Depends(verify_api_key),
):
    """LCP, INP, CLS + top opportunities. Vereist PAGESPEED_API_KEY in .env."""
    logger.info(f"PageSpeed: {request.url} ({request.strategy})")
    return await run_pagespeed(str(request.url), request.strategy)


# ---------- GSC ----------

@app.post(
    "/gsc/queries",
    response_model=GSCQueriesResponse,
    tags=["gsc"],
    summary="Top zoekopdrachten uit Google Search Console",
)
async def gsc_queries(
    request: GSCQueriesRequest,
    _: None = Depends(verify_api_key),
):
    """Vereist GSC_SERVICE_ACCOUNT_JSON in .env."""
    logger.info(f"GSC queries: site={request.site_url or 'default'} days={request.days}")
    try:
        return await get_top_queries(request.site_url, request.days, request.limit)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/gsc/pages",
    response_model=GSCPagesResponse,
    tags=["gsc"],
    summary="Top pagina's met impressions/clicks uit GSC",
)
async def gsc_pages(
    request: GSCPagesRequest,
    _: None = Depends(verify_api_key),
):
    """Vereist GSC_SERVICE_ACCOUNT_JSON in .env."""
    logger.info(f"GSC pages: site={request.site_url or 'default'} days={request.days}")
    try:
        return await get_top_pages(request.site_url, request.days, request.limit)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------- Trends ----------

@app.post(
    "/trends/keyword",
    response_model=TrendsResponse,
    tags=["trends"],
    summary="Google Trends data per keyword (interest over time, related queries)",
)
async def trends_keyword(
    request: TrendsRequest,
    _: None = Depends(verify_api_key),
):
    """
    Google Trends voor 1-5 keywords. Geen API key nodig.

    Output per keyword:
    - interest_over_time: relatieve volumes over de periode
    - direction: rising/stable/falling/no_data
    - related_top: top 10 gerelateerde zoekopdrachten
    - related_rising: top 10 stijgende zoekopdrachten

    Let op: Google kan onaangekondigd rate-limiten op pytrends. Cache de resultaten.
    """
    logger.info(f"Trends: keywords={request.keywords} timeframe={request.timeframe} geo={request.geo}")
    return await get_keyword_trends(request.keywords, request.timeframe, request.geo)
