"""Sitemap parser: vindt en parseert sitemap.xml (inclusief sitemap-indexes)."""

from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.config import settings
from app.models import SitemapEntry, SitemapResponse


async def _fetch_sitemap(client: httpx.AsyncClient, url: str) -> str | None:
    """Haal sitemap-XML op. Returns None bij fout."""
    try:
        resp = await client.get(url, timeout=settings.request_timeout)
        if resp.status_code == 200:
            return resp.text
    except httpx.HTTPError:
        pass
    return None


def _parse_xml(xml_text: str) -> tuple[list[str], list[SitemapEntry]]:
    """Returns (nested_sitemaps, url_entries)."""
    soup = BeautifulSoup(xml_text, "xml")
    nested = []
    entries = []

    # Sitemap-index: <sitemap><loc>...</loc></sitemap>
    for sitemap in soup.find_all("sitemap"):
        loc = sitemap.find("loc")
        if loc and loc.text:
            nested.append(loc.text.strip())

    # URL entries: <url><loc>...</loc>...</url>
    for url_el in soup.find_all("url"):
        loc = url_el.find("loc")
        if not loc or not loc.text:
            continue
        lastmod = url_el.find("lastmod")
        priority = url_el.find("priority")
        entries.append(SitemapEntry(
            loc=loc.text.strip(),
            lastmod=lastmod.text.strip() if lastmod else None,
            priority=float(priority.text) if priority and priority.text else None,
        ))

    return nested, entries


async def parse_sitemap(domain: str) -> SitemapResponse:
    """Vind en parseer alle sitemaps voor een domein."""
    domain = domain.rstrip("/")
    candidates = [
        urljoin(domain + "/", "sitemap.xml"),
        urljoin(domain + "/", "sitemap_index.xml"),
        urljoin(domain + "/", "sitemap-index.xml"),
    ]

    sitemaps_found: list[str] = []
    all_entries: list[SitemapEntry] = []

    async with httpx.AsyncClient(
        timeout=settings.request_timeout,
        headers={"User-Agent": settings.user_agent},
        follow_redirects=True,
    ) as client:
        # Probeer eerst robots.txt voor sitemap-locatie
        try:
            robots = await client.get(urljoin(domain + "/", "robots.txt"))
            if robots.status_code == 200:
                for line in robots.text.splitlines():
                    if line.lower().startswith("sitemap:"):
                        url = line.split(":", 1)[1].strip()
                        candidates.insert(0, url)
        except httpx.HTTPError:
            pass

        # Doorloop kandidaten en hun nested sitemaps
        to_process = list(dict.fromkeys(candidates))  # dedupe, behoud volgorde
        processed: set[str] = set()
        max_iterations = 50  # safety cap

        while to_process and len(processed) < max_iterations:
            current = to_process.pop(0)
            if current in processed:
                continue
            processed.add(current)

            xml = await _fetch_sitemap(client, current)
            if not xml:
                continue

            sitemaps_found.append(current)
            nested, entries = _parse_xml(xml)
            all_entries.extend(entries)
            for n in nested:
                if n not in processed:
                    to_process.append(n)

    return SitemapResponse(
        domain=domain,
        sitemaps_found=sitemaps_found,
        urls=all_entries,
        total_urls=len(all_entries),
    )
