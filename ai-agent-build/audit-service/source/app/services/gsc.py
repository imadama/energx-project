"""Google Search Console API integratie via Service Account.

Vereist:
- GSC_SERVICE_ACCOUNT_JSON pad naar de JSON-credentials
- GSC_SITE_URL als default site (kan per request worden overschreven)
- Service Account email moet als gebruiker zijn toegevoegd aan de GSC property
"""

from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor
import asyncio
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import settings
from app.models import GSCPage, GSCPagesResponse, GSCQuery, GSCQueriesResponse


_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
_executor = ThreadPoolExecutor(max_workers=4)


def _get_service():
    """Build de Search Console API client. Raises als credentials ontbreken."""
    if not settings.gsc_service_account_json:
        raise RuntimeError("GSC_SERVICE_ACCOUNT_JSON niet geconfigureerd in .env")
    if not os.path.exists(settings.gsc_service_account_json):
        raise RuntimeError(f"Service account JSON niet gevonden op: {settings.gsc_service_account_json}")

    creds = service_account.Credentials.from_service_account_file(
        settings.gsc_service_account_json,
        scopes=_SCOPES,
    )
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def _query_sync(site_url: str, days: int, limit: int, dimension: str) -> list[dict]:
    """Sync GSC query; we wrappen 'm in async via run_in_executor."""
    service = _get_service()
    end_date = date.today() - timedelta(days=2)  # GSC heeft 2-3 dagen vertraging
    start_date = end_date - timedelta(days=days)

    body = {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "dimensions": [dimension],
        "rowLimit": limit,
        "startRow": 0,
    }
    try:
        response = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
    except HttpError as e:
        raise RuntimeError(f"GSC API error: {e}") from e

    return response.get("rows", [])


async def get_top_queries(site_url: str | None, days: int, limit: int) -> GSCQueriesResponse:
    """Haal top zoekopdrachten uit GSC."""
    target_site = site_url or settings.gsc_site_url
    if not target_site:
        raise RuntimeError("Geen site_url opgegeven en GSC_SITE_URL niet gezet in .env")

    loop = asyncio.get_event_loop()
    rows = await loop.run_in_executor(_executor, _query_sync, target_site, days, limit, "query")

    queries = [
        GSCQuery(
            query=row["keys"][0],
            clicks=int(row.get("clicks", 0)),
            impressions=int(row.get("impressions", 0)),
            ctr=round(float(row.get("ctr", 0)), 4),
            position=round(float(row.get("position", 0)), 2),
        )
        for row in rows
    ]
    return GSCQueriesResponse(site_url=target_site, period_days=days, queries=queries)


async def get_top_pages(site_url: str | None, days: int, limit: int) -> GSCPagesResponse:
    """Haal top pagina's uit GSC."""
    target_site = site_url or settings.gsc_site_url
    if not target_site:
        raise RuntimeError("Geen site_url opgegeven en GSC_SITE_URL niet gezet in .env")

    loop = asyncio.get_event_loop()
    rows = await loop.run_in_executor(_executor, _query_sync, target_site, days, limit, "page")

    pages = [
        GSCPage(
            page=row["keys"][0],
            clicks=int(row.get("clicks", 0)),
            impressions=int(row.get("impressions", 0)),
            ctr=round(float(row.get("ctr", 0)), 4),
            position=round(float(row.get("position", 0)), 2),
        )
        for row in rows
    ]
    return GSCPagesResponse(site_url=target_site, period_days=days, pages=pages)
