"""Pydantic models voor request- en response-schemas van alle endpoints."""

from pydantic import BaseModel, Field, HttpUrl
from typing import Literal


# ---------- Shared ----------

class Issue(BaseModel):
    severity: Literal["info", "warning", "critical"]
    type: str
    detail: str


# ---------- /technical/audit ----------

class TechnicalAuditRequest(BaseModel):
    url: HttpUrl


class TechnicalAuditResponse(BaseModel):
    url: str
    status_code: int | None
    response_time_ms: int | None
    https: bool
    redirect_chain: list[str] = []
    canonical: str | None = None
    robots_meta: str | None = None
    robots_txt_allows: bool | None = None
    schemas_found: list[str] = []
    images_total: int = 0
    alt_tags_missing: int = 0
    internal_links_count: int = 0
    external_links_count: int = 0
    broken_links: list[str] = []
    issues: list[Issue] = []


# ---------- /content/audit ----------

class ContentAuditRequest(BaseModel):
    url: HttpUrl


class ContentAuditResponse(BaseModel):
    url: str
    title: str | None = None
    title_length: int | None = None
    meta_description: str | None = None
    meta_description_length: int | None = None
    h1_count: int = 0
    h1_text: str | None = None
    h2_count: int = 0
    h2_texts: list[str] = []
    h3_count: int = 0
    word_count: int = 0
    paragraph_count: int = 0
    avg_words_per_sentence: float | None = None
    internal_links: int = 0
    external_links: int = 0
    flesch_douma_score: float | None = None
    flesch_douma_grade: str | None = None
    issues: list[Issue] = []


# ---------- /sitemap/parse ----------

class SitemapRequest(BaseModel):
    domain: HttpUrl


class SitemapEntry(BaseModel):
    loc: str
    lastmod: str | None = None
    priority: float | None = None


class SitemapResponse(BaseModel):
    domain: str
    sitemaps_found: list[str] = []
    urls: list[SitemapEntry] = []
    total_urls: int = 0


# ---------- /pagespeed ----------

class PageSpeedRequest(BaseModel):
    url: HttpUrl
    strategy: Literal["mobile", "desktop"] = "mobile"


class CoreWebVitals(BaseModel):
    lcp_ms: int | None = Field(None, description="Largest Contentful Paint (target < 2500ms)")
    inp_ms: int | None = Field(None, description="Interaction to Next Paint (target < 200ms)")
    cls: float | None = Field(None, description="Cumulative Layout Shift (target < 0.1)")
    fcp_ms: int | None = Field(None, description="First Contentful Paint")
    ttfb_ms: int | None = Field(None, description="Time to First Byte")


class PageSpeedResponse(BaseModel):
    url: str
    strategy: str
    performance_score: int | None = None
    core_web_vitals: CoreWebVitals
    opportunities: list[str] = []


# ---------- /gsc/queries ----------

class GSCQueriesRequest(BaseModel):
    site_url: str | None = Field(None, description="Override default GSC_SITE_URL")
    days: int = Field(28, ge=1, le=480, description="Aantal dagen terug")
    limit: int = Field(50, ge=1, le=1000)


class GSCQuery(BaseModel):
    query: str
    clicks: int
    impressions: int
    ctr: float
    position: float


class GSCQueriesResponse(BaseModel):
    site_url: str
    period_days: int
    queries: list[GSCQuery] = []


# ---------- /gsc/pages ----------

class GSCPagesRequest(BaseModel):
    site_url: str | None = None
    days: int = Field(28, ge=1, le=480)
    limit: int = Field(50, ge=1, le=1000)


class GSCPage(BaseModel):
    page: str
    clicks: int
    impressions: int
    ctr: float
    position: float


class GSCPagesResponse(BaseModel):
    site_url: str
    period_days: int
    pages: list[GSCPage] = []


# ---------- /trends/keyword ----------

class TrendsRequest(BaseModel):
    keywords: list[str] = Field(..., min_length=1, max_length=5, description="1-5 keywords")
    timeframe: Literal["today 1-m", "today 3-m", "today 12-m", "today 5-y"] = "today 12-m"
    geo: str = Field("NL", description="ISO landcode, default NL")


class KeywordTrend(BaseModel):
    interest_over_time: list[int] = []
    direction: Literal["rising", "stable", "falling", "no_data", "unknown"] = "unknown"
    peak_value: int = 0
    recent_average: float | None = None
    related_top: list[str] = []
    related_rising: list[str] = []
    error: str | None = None


class TrendsResponse(BaseModel):
    keywords: dict[str, KeywordTrend] = {}
