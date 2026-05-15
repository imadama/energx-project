"""On-page content audit: title/meta, H-structuur, word count, readability NL."""

from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.config import settings
from app.models import ContentAuditResponse, Issue
from app.services.readability import flesch_douma, count_sentences, count_words


def _extract_visible_text(soup: BeautifulSoup) -> str:
    """Strip nav, footer, scripts, en haal alleen body-content."""
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


async def run_content_audit(url: str) -> ContentAuditResponse:
    """Voer een complete content audit uit op één URL."""
    parsed = urlparse(url)
    issues: list[Issue] = []

    async with httpx.AsyncClient(
        timeout=settings.request_timeout,
        headers={"User-Agent": settings.user_agent},
        follow_redirects=True,
    ) as client:
        try:
            response = await client.get(url)
        except httpx.HTTPError as e:
            return ContentAuditResponse(
                url=url,
                issues=[Issue(severity="critical", type="fetch_error", detail=f"Kon URL niet ophalen: {e}")],
            )

        if response.status_code >= 400:
            return ContentAuditResponse(
                url=url,
                issues=[Issue(severity="critical", type="bad_status", detail=f"HTTP {response.status_code}")],
            )

        soup = BeautifulSoup(response.text, "lxml")

        # Title
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else None
        title_length = len(title) if title else 0
        if not title:
            issues.append(Issue(severity="critical", type="no_title", detail="Geen <title> tag gevonden"))
        elif title_length < 30:
            issues.append(Issue(severity="warning", type="title_short", detail=f"Title is {title_length} tekens (<30)"))
        elif title_length > 65:
            issues.append(Issue(severity="warning", type="title_long", detail=f"Title is {title_length} tekens (>65, wordt afgekapt)"))

        # Meta description
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        meta_description = meta_desc_tag.get("content", "").strip() if meta_desc_tag else None
        meta_description_length = len(meta_description) if meta_description else 0
        if not meta_description:
            issues.append(Issue(severity="warning", type="no_meta_description", detail="Geen meta description"))
        elif meta_description_length > 160:
            issues.append(Issue(severity="warning", type="meta_long", detail=f"Meta description {meta_description_length} tekens (>160)"))
        elif meta_description_length < 120:
            issues.append(Issue(severity="info", type="meta_short", detail=f"Meta description {meta_description_length} tekens (<120)"))

        # Headings
        h1_tags = soup.find_all("h1")
        h1_count = len(h1_tags)
        h1_text = h1_tags[0].get_text(strip=True) if h1_tags else None
        if h1_count == 0:
            issues.append(Issue(severity="critical", type="no_h1", detail="Geen H1 op de pagina"))
        elif h1_count > 1:
            issues.append(Issue(severity="warning", type="multiple_h1", detail=f"{h1_count} H1's gevonden (1 aanbevolen)"))

        h2_tags = soup.find_all("h2")
        h2_texts = [h.get_text(strip=True) for h in h2_tags]
        h3_tags = soup.find_all("h3")

        # Content text
        visible_text = _extract_visible_text(soup)
        word_count = count_words(visible_text)
        sentence_count = count_sentences(visible_text)
        avg_words_per_sentence = round(word_count / sentence_count, 1) if sentence_count else None

        paragraphs = soup.find_all("p")
        paragraph_count = len([p for p in paragraphs if p.get_text(strip=True)])

        if word_count < 300:
            issues.append(Issue(severity="warning", type="thin_content", detail=f"Slechts {word_count} woorden (dunne content)"))

        # Links
        internal_links = 0
        external_links = 0
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
                continue
            absolute = urljoin(url, href)
            target_host = urlparse(absolute).netloc
            if target_host == parsed.netloc or not target_host:
                internal_links += 1
            else:
                external_links += 1

        # Readability
        score, grade = flesch_douma(visible_text)
        if score is not None and score < 50:
            issues.append(Issue(
                severity="warning",
                type="readability_low",
                detail=f"Flesch-Douma score {score} (te complex voor consumer-content)",
            ))

        return ContentAuditResponse(
            url=url,
            title=title,
            title_length=title_length if title else None,
            meta_description=meta_description,
            meta_description_length=meta_description_length if meta_description else None,
            h1_count=h1_count,
            h1_text=h1_text,
            h2_count=len(h2_tags),
            h2_texts=h2_texts,
            h3_count=len(h3_tags),
            word_count=word_count,
            paragraph_count=paragraph_count,
            avg_words_per_sentence=avg_words_per_sentence,
            internal_links=internal_links,
            external_links=external_links,
            flesch_douma_score=score,
            flesch_douma_grade=grade,
            issues=issues,
        )
