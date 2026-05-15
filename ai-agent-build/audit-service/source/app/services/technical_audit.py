"""Technische audit van één URL: status, HTTPS, canonical, robots, schema, alt-tags, broken links."""

import asyncio
import json
import time
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.config import settings
from app.models import Issue, TechnicalAuditResponse


async def _check_link(client: httpx.AsyncClient, url: str) -> bool:
    """Return True als link OK is (2xx/3xx), False bij 4xx/5xx of fout."""
    try:
        resp = await client.head(url, follow_redirects=True, timeout=10)
        return resp.status_code < 400
    except Exception:
        return False


async def _check_robots_txt(client: httpx.AsyncClient, base_url: str, path: str) -> bool | None:
    """Check of robots.txt deze path toestaat. Returns None bij fout."""
    try:
        robots_url = urljoin(base_url, "/robots.txt")
        resp = await client.get(robots_url, timeout=10)
        if resp.status_code != 200:
            return True  # geen robots.txt = alles toegestaan
        # Simpele check: zoek naar Disallow regels voor de path
        # Een productie-implementatie zou urllib.robotparser gebruiken
        from urllib import robotparser
        rp = robotparser.RobotFileParser()
        rp.parse(resp.text.splitlines())
        return rp.can_fetch(settings.user_agent, path)
    except Exception:
        return None


def _extract_schemas(soup: BeautifulSoup) -> list[str]:
    """Extract @type values uit alle JSON-LD scripts."""
    schemas = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "@type" in item:
                        schemas.append(item["@type"])
            elif isinstance(data, dict):
                t = data.get("@type")
                if t:
                    if isinstance(t, list):
                        schemas.extend(t)
                    else:
                        schemas.append(t)
        except (json.JSONDecodeError, TypeError):
            continue
    return schemas


async def run_technical_audit(url: str) -> TechnicalAuditResponse:
    """Voer een complete technische audit uit op één URL."""
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    issues: list[Issue] = []
    redirect_chain: list[str] = []

    async with httpx.AsyncClient(
        timeout=settings.request_timeout,
        headers={"User-Agent": settings.user_agent},
        follow_redirects=False,  # we tracken zelf de chain
    ) as client:
        # Initial fetch + track redirects
        start = time.perf_counter()
        try:
            current = url
            response = None
            for _ in range(10):
                response = await client.get(current, timeout=settings.request_timeout)
                if 300 <= response.status_code < 400 and "location" in response.headers:
                    redirect_chain.append(current)
                    current = urljoin(current, response.headers["location"])
                else:
                    break
            response_time_ms = int((time.perf_counter() - start) * 1000)
        except httpx.HTTPError as e:
            return TechnicalAuditResponse(
                url=url,
                status_code=None,
                response_time_ms=None,
                https=parsed.scheme == "https",
                issues=[Issue(severity="critical", type="fetch_error", detail=f"Kon URL niet ophalen: {e}")],
            )

        status_code = response.status_code
        final_url = str(response.url) if response else url
        html = response.text if response else ""

        if status_code >= 400:
            issues.append(Issue(severity="critical", type="bad_status", detail=f"HTTP {status_code}"))

        if response_time_ms > 3000:
            issues.append(Issue(severity="warning", type="slow_response", detail=f"Response time {response_time_ms}ms (>3s)"))

        # HTTPS check
        https = parsed.scheme == "https"
        if not https:
            issues.append(Issue(severity="warning", type="no_https", detail="URL gebruikt geen HTTPS"))

        # Parse HTML
        soup = BeautifulSoup(html, "lxml")

        # Canonical
        canonical_tag = soup.find("link", rel="canonical")
        canonical = canonical_tag.get("href") if canonical_tag else None

        # Robots meta
        robots_meta_tag = soup.find("meta", attrs={"name": "robots"})
        robots_meta = robots_meta_tag.get("content") if robots_meta_tag else None
        if robots_meta and "noindex" in robots_meta.lower():
            issues.append(Issue(severity="warning", type="noindex", detail=f"Pagina heeft robots meta: {robots_meta}"))

        # Robots.txt
        robots_txt_allows = await _check_robots_txt(client, base_url, parsed.path)
        if robots_txt_allows is False:
            issues.append(Issue(severity="critical", type="robots_blocked", detail="robots.txt blokkeert deze URL"))

        # Schema.org
        schemas_found = _extract_schemas(soup)

        # Images alt-tags
        images = soup.find_all("img")
        images_total = len(images)
        alt_missing = sum(1 for img in images if not img.get("alt"))
        if alt_missing > 0:
            issues.append(Issue(
                severity="warning",
                type="alt_missing",
                detail=f"{alt_missing} van {images_total} afbeeldingen zonder alt-tag",
            ))

        # Links splitsen in intern/extern
        internal_links = []
        external_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
                continue
            absolute = urljoin(final_url, href)
            target_host = urlparse(absolute).netloc
            if target_host == parsed.netloc or not target_host:
                internal_links.append(absolute)
            else:
                external_links.append(absolute)

        # Broken links sample (check eerste 10 om snel te blijven)
        sample_links = list(set(internal_links + external_links))[:10]
        check_results = await asyncio.gather(*[_check_link(client, link) for link in sample_links])
        broken = [link for link, ok in zip(sample_links, check_results) if not ok]
        if broken:
            issues.append(Issue(
                severity="warning",
                type="broken_links",
                detail=f"{len(broken)} kapotte link(s) in eerste 10 checks",
            ))

        return TechnicalAuditResponse(
            url=url,
            status_code=status_code,
            response_time_ms=response_time_ms,
            https=https,
            redirect_chain=redirect_chain,
            canonical=canonical,
            robots_meta=robots_meta,
            robots_txt_allows=robots_txt_allows,
            schemas_found=schemas_found,
            images_total=images_total,
            alt_tags_missing=alt_missing,
            internal_links_count=len(internal_links),
            external_links_count=len(external_links),
            broken_links=broken,
            issues=issues,
        )
