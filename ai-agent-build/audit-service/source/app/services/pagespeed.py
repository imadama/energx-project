"""PageSpeed Insights API integratie: Core Web Vitals voor een URL."""

import httpx

from app.config import settings
from app.models import CoreWebVitals, PageSpeedResponse

_PSI_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


async def run_pagespeed(url: str, strategy: str = "mobile") -> PageSpeedResponse:
    """Haal PageSpeed Insights metrics op voor een URL."""
    if not settings.pagespeed_api_key:
        return PageSpeedResponse(
            url=url,
            strategy=strategy,
            performance_score=None,
            core_web_vitals=CoreWebVitals(),
            opportunities=["FOUT: PAGESPEED_API_KEY niet geconfigureerd"],
        )

    params = {
        "url": url,
        "strategy": strategy,
        "key": settings.pagespeed_api_key,
        "category": ["PERFORMANCE"],
    }

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            resp = await client.get(_PSI_ENDPOINT, params=params)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as e:
            return PageSpeedResponse(
                url=url,
                strategy=strategy,
                performance_score=None,
                core_web_vitals=CoreWebVitals(),
                opportunities=[f"PageSpeed API error: {e}"],
            )

    # Lighthouse Result voor performance score
    lighthouse = data.get("lighthouseResult", {})
    perf_score = None
    perf_cat = lighthouse.get("categories", {}).get("performance", {})
    if "score" in perf_cat and perf_cat["score"] is not None:
        perf_score = int(perf_cat["score"] * 100)

    audits = lighthouse.get("audits", {})

    def _audit_ms(key: str) -> int | None:
        v = audits.get(key, {}).get("numericValue")
        return int(v) if v is not None else None

    def _audit_unitless(key: str) -> float | None:
        v = audits.get(key, {}).get("numericValue")
        return round(float(v), 3) if v is not None else None

    cwv = CoreWebVitals(
        lcp_ms=_audit_ms("largest-contentful-paint"),
        inp_ms=_audit_ms("interactive"),  # PSI heeft INP nog niet altijd, fallback op interactive
        cls=_audit_unitless("cumulative-layout-shift"),
        fcp_ms=_audit_ms("first-contentful-paint"),
        ttfb_ms=_audit_ms("server-response-time"),
    )

    # Top opportunities (lighthouse audits met savings)
    opportunities: list[str] = []
    for key, audit in audits.items():
        details = audit.get("details", {})
        savings_ms = details.get("overallSavingsMs")
        if savings_ms and savings_ms > 200:
            title = audit.get("title", key)
            opportunities.append(f"{title}: bespaar ~{int(savings_ms)}ms")
    opportunities = sorted(opportunities, key=lambda s: -int(s.split("~")[-1].split("ms")[0]))[:5]

    return PageSpeedResponse(
        url=url,
        strategy=strategy,
        performance_score=perf_score,
        core_web_vitals=cwv,
        opportunities=opportunities,
    )
