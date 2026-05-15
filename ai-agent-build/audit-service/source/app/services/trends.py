"""Google Trends integratie via pytrends. Geen API key nodig, maar Google kan rate-limiten."""

import asyncio
from concurrent.futures import ThreadPoolExecutor

from pytrends.request import TrendReq


_executor = ThreadPoolExecutor(max_workers=2)  # pytrends is niet thread-safe bij hoge concurrency


def _classify_direction(values: list[int]) -> str:
    """Bepaal trend-richting uit time-series."""
    if not values or len(values) < 4:
        return "unknown"
    first_quarter_avg = sum(values[: len(values) // 4]) / max(len(values) // 4, 1)
    last_quarter_avg = sum(values[-len(values) // 4 :]) / max(len(values) // 4, 1)
    if last_quarter_avg > first_quarter_avg * 1.3:
        return "rising"
    if last_quarter_avg < first_quarter_avg * 0.7:
        return "falling"
    return "stable"


def _trends_sync(keywords: list[str], timeframe: str, geo: str) -> dict:
    """Sync pytrends call. Returns dict met data per keyword."""
    pytrends = TrendReq(hl="nl-NL", tz=60, retries=2, backoff_factor=0.5)

    # Pytrends accepteert max 5 keywords per build_payload
    keywords = keywords[:5]
    pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo, gprop="")

    result: dict = {"keywords": {}}

    # Interest over time
    iot = pytrends.interest_over_time()
    for kw in keywords:
        if iot is not None and kw in iot.columns:
            values = iot[kw].tolist()
            result["keywords"][kw] = {
                "interest_over_time": values,
                "direction": _classify_direction(values),
                "peak_value": max(values) if values else 0,
                "recent_average": sum(values[-4:]) / 4 if len(values) >= 4 else None,
            }
        else:
            result["keywords"][kw] = {
                "interest_over_time": [],
                "direction": "no_data",
                "peak_value": 0,
                "recent_average": None,
            }

    # Related queries (top + rising) — per keyword
    try:
        related = pytrends.related_queries()
        for kw in keywords:
            if kw in related:
                top_df = related[kw].get("top")
                rising_df = related[kw].get("rising")
                result["keywords"][kw]["related_top"] = (
                    top_df["query"].head(10).tolist() if top_df is not None else []
                )
                result["keywords"][kw]["related_rising"] = (
                    rising_df["query"].head(10).tolist() if rising_df is not None else []
                )
    except Exception:
        # Related queries is optioneel; faal niet de hele call
        for kw in keywords:
            result["keywords"][kw].setdefault("related_top", [])
            result["keywords"][kw].setdefault("related_rising", [])

    return result


async def get_keyword_trends(
    keywords: list[str],
    timeframe: str = "today 12-m",
    geo: str = "NL",
) -> dict:
    """
    Haal Google Trends data op voor 1-5 keywords.

    timeframe opties: 'today 1-m', 'today 3-m', 'today 12-m', 'today 5-y'
    geo: ISO landcode, default NL
    """
    if not keywords:
        return {"keywords": {}}

    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(_executor, _trends_sync, keywords, timeframe, geo)
    except Exception as e:
        return {
            "keywords": {kw: {"error": str(e)} for kw in keywords[:5]},
        }
