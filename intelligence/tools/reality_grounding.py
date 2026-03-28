"""
arifosmcp.transport/tools/reality_grounding.py — Hardened Reality Grounding

Provides external fact-checking via thermodynamically optimal cascade:
1. DDGS (DuckDuckGo) — Primary, no API key, low entropy
2. Playwright DDG HTML — Fallback if DDGS fails
3. Playwright Google — Last resort (high entropy, CAPTCHA risk)

Constitutional Compliance:
- F1 Amanah: Reversible throttling, no vendor lock-in
- F2 Truth: ASEAN source bias, timelimit filters
- F7 Humility: Uncertainty tracking (Ω₀) for all results
- F9 Anti-Hantu: Full source attribution

Thermodynamic Profile: Low entropy cascade (DDGS → HTML → Browser)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from arifosmcp.intelligence.tools.envelope import unified_tool_output
from arifosmcp.intelligence.tools.logic.consensus_arbitrator import ConsensusArbitrator

logger = logging.getLogger(__name__)

# Optional Dependencies
try:
    from ddgs import DDGS

    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

try:
    from playwright.async_api import async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    from bs4 import BeautifulSoup

    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# Routing: migrated to core (v64.1+)
try:
    from arifosmcp.core.enforcement.routing import route_refuse
except ImportError:
    route_refuse = None

# Configuration
DEFAULT_THROTTLE_SECONDS = 2.0
ASEAN_SITES = [".my", ".sg", ".id", ".th", ".ph", ".vn", ".bn", ".kh", ".la", ".mm"]
UNCERTAINTY_BRAVE = 0.02  # Lowest uncertainty - official API
UNCERTAINTY_DDGS = 0.04
UNCERTAINTY_PLAYWRIGHT = 0.07

# Brave Search API config
BRAVE_API_KEY_ENV = "BRAVE_API_KEY"


@dataclass
class SearchResult:
    """Standardized search result with governance metadata."""

    title: str
    url: str
    snippet: str
    source: str
    rank: int
    uncertainty: float = field(default=UNCERTAINTY_DDGS)
    timestamp: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "rank": self.rank,
            "uncertainty_omega": self.uncertainty,
            "timestamp": self.timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


@dataclass
class RealityGroundingResult:
    """Complete result with constitutional audit trail."""

    status: str
    query: str
    results: list[SearchResult]
    engines_used: list[str]
    engines_failed: list[str]
    uncertainty_aggregate: float
    audit_trail: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "query": self.query,
            "results_count": len(self.results),
            "results": [r.to_dict() for r in self.results],
            "engines_used": self.engines_used,
            "engines_failed": self.engines_failed,
            "uncertainty_aggregate": self.uncertainty_aggregate,
            "audit_trail": self.audit_trail,
        }


class ThrottleGovernor:
    """Rate limiter with reversible throttling (F1 Amanah)."""

    def __init__(self, min_interval: float = DEFAULT_THROTTLE_SECONDS):
        self.min_interval = min_interval
        self._last_call_time: float | None = None
        self._lock = asyncio.Lock()

    async def wait(self) -> float:
        """Wait for throttle interval. Returns wait time."""
        async with self._lock:
            now = time.time()
            if self._last_call_time is not None:
                elapsed = now - self._last_call_time
                if elapsed < self.min_interval:
                    wait_time = self.min_interval - elapsed
                    await asyncio.sleep(wait_time)
                    return wait_time
            self._last_call_time = time.time()
            return 0.0


# Singleton throttle governor
_throttle_governor = ThrottleGovernor()


class BraveSearchEngine:
    """Brave Search API - LOWEST entropy, highest reliability.

    Constitutional Compliance:
    - F1 Amanah: Uses official API with proper authentication
    - F2 Truth: High-quality results from Brave's index
    - F7 Humility: Lowest uncertainty (0.02) due to API reliability
    """

    NAME = "brave"
    UNCERTAINTY = UNCERTAINTY_BRAVE

    def __init__(self, api_key: str):
        """Initialize with explicit API key (required)."""
        self.api_key = api_key
        self._throttle = _throttle_governor

    async def search(
        self,
        query: str,
        max_results: int = 10,
        region: str = "wt-wt",
        timelimit: str | None = None,
    ) -> tuple[list[SearchResult], str | None]:
        """Search via Brave API."""
        await self._throttle.wait()

        try:
            endpoint = "https://api.search.brave.com/res/v1/web/search"
            params = {"q": query, "count": str(max_results)}
            if timelimit:
                # Brave freshness: pd (day), pw (week), pm (month), py (year)
                time_map = {"d": "pd", "w": "pw", "m": "pm", "y": "py"}
                if timelimit in time_map:
                    params["freshness"] = time_map[timelimit]

            url = f"{endpoint}?{urllib.parse.urlencode(params)}"

            req = urllib.request.Request(url)
            req.add_header("Accept", "application/json")
            req.add_header("X-Subscription-Token", self.api_key)

            loop = asyncio.get_event_loop()
            payload = await loop.run_in_executor(None, lambda: self._sync_request(req))

            results = []
            for i, item in enumerate(
                (payload.get("web", {}) or {}).get("results", [])[:max_results], 1
            ):
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("description", ""),
                        source=self.NAME,
                        rank=i,
                        uncertainty=self.UNCERTAINTY,
                    )
                )

            return results, None
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.warning(f"Brave search failed: {error_msg}")
            return [], error_msg

    def _sync_request(self, req: urllib.request.Request) -> dict:
        """Synchronous HTTP request."""
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))


class DDGSEngine:
    """DuckDuckGo search via ddgs library - LOW entropy."""

    NAME = "ddgs"
    UNCERTAINTY = UNCERTAINTY_DDGS

    def __init__(self, timeout: int = 30):
        if not DDGS_AVAILABLE:
            raise ImportError("ddgs not installed")
        self.timeout = timeout
        self._throttle = _throttle_governor

    def _build_query(self, query: str, region: str = "wt-wt") -> str:
        """Build query with ASEAN bias if requested (F2 Truth)."""
        if region == "asean":
            sites = " OR ".join([f"site:*{s}" for s in ASEAN_SITES])
            return f"({query}) ({sites})"
        return query

    async def search(
        self,
        query: str,
        max_results: int = 10,
        region: str = "wt-wt",
        safesearch: str = "moderate",
        timelimit: str | None = None,
    ) -> tuple[list[SearchResult], str | None]:
        """Search DuckDuckGo."""
        await self._throttle.wait()
        built_query = self._build_query(query, region)

        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, lambda: self._sync_search(built_query, max_results, safesearch, timelimit)
            )
            return results, None
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.warning(f"DDGS search failed: {error_msg}")
            return [], error_msg

    def _sync_search(
        self, query: str, max_results: int, safesearch: str, timelimit: str | None
    ) -> list[SearchResult]:
        """Synchronous DDGS search."""
        with DDGS(timeout=self.timeout) as ddgs:
            raw_results = ddgs.text(
                query,
                region="wt-wt",
                safesearch=safesearch,
                timelimit=timelimit,
                max_results=max_results,
            )

            results = []
            for i, r in enumerate(raw_results, 1):
                results.append(
                    SearchResult(
                        title=r.get("title", ""),
                        url=r.get("href", ""),
                        snippet=r.get("body", ""),
                        source=self.NAME,
                        rank=i,
                        uncertainty=self.UNCERTAINTY,
                    )
                )
            return results


class PlaywrightDDGEngine:
    """DuckDuckGo HTML search via Playwright - MEDIUM entropy."""

    NAME = "playwright_ddg"
    UNCERTAINTY = UNCERTAINTY_PLAYWRIGHT

    def __init__(self, headless: bool = True):
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("playwright not installed")
        self.headless = headless
        self._throttle = ThrottleGovernor(min_interval=5.0)

    async def search(
        self, query: str, max_results: int = 10, region: str = "wt-wt"
    ) -> tuple[list[SearchResult], str | None]:
        """Search DuckDuckGo HTML version via browser."""
        await self._throttle.wait()
        results = []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                try:
                    context = await browser.new_context(
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    )
                    page = await context.new_page()

                    encoded_query = query.replace(" ", "+")
                    await page.goto(
                        f"https://html.duckduckgo.com/html/?q={encoded_query}",
                        wait_until="networkidle",
                        timeout=30000,
                    )

                    result_elements = await page.query_selector_all(".result")

                    for i, elem in enumerate(result_elements[:max_results], 1):
                        try:
                            title_elem = await elem.query_selector(".result__title a")
                            snippet_elem = await elem.query_selector(".result__snippet")

                            title = await title_elem.inner_text() if title_elem else ""
                            url = await title_elem.get_attribute("href") if title_elem else ""
                            snippet = await snippet_elem.inner_text() if snippet_elem else ""

                            if title and url:
                                results.append(
                                    SearchResult(
                                        title=title.strip(),
                                        url=url,
                                        snippet=snippet.strip(),
                                        source=self.NAME,
                                        rank=i,
                                        uncertainty=self.UNCERTAINTY,
                                    )
                                )
                        except Exception as e:
                            logger.debug(f"Failed to extract result {i}: {e}")
                            continue
                finally:
                    await browser.close()

            return results, None
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.warning(f"Playwright DDG failed: {error_msg}")
            return [], error_msg


class PlaywrightGoogleEngine:
    """Google search via Playwright - HIGH entropy (last resort)."""

    NAME = "playwright_google"
    UNCERTAINTY = UNCERTAINTY_PLAYWRIGHT + 0.03

    def __init__(self, headless: bool = True):
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("playwright not installed")
        self.headless = headless
        self._throttle = ThrottleGovernor(min_interval=10.0)

    async def search(
        self, query: str, max_results: int = 10, region: str = "wt-wt"
    ) -> tuple[list[SearchResult], str | None]:
        """Search Google via browser - WARNING: High CAPTCHA risk."""
        await self._throttle.wait()
        results = []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                try:
                    context = await browser.new_context(
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        viewport={"width": 1920, "height": 1080},
                    )
                    page = await context.new_page()

                    encoded_query = query.replace(" ", "+")
                    await page.goto(
                        f"https://www.google.com/search?q={encoded_query}",
                        wait_until="networkidle",
                        timeout=30000,
                    )

                    captcha = await page.query_selector("text=I'm not a robot")
                    if captcha:
                        return [], "CAPTCHA detected - Google blocking automation"

                    result_elements = await page.query_selector_all("div.g")

                    for i, elem in enumerate(result_elements[:max_results], 1):
                        try:
                            title_elem = await elem.query_selector("h3")
                            link_elem = await elem.query_selector("a")
                            snippet_elem = await elem.query_selector("div.VwiC3b, span.aCOpRe")

                            title = await title_elem.inner_text() if title_elem else ""
                            url = await link_elem.get_attribute("href") if link_elem else ""
                            snippet = await snippet_elem.inner_text() if snippet_elem else ""

                            if title and url:
                                results.append(
                                    SearchResult(
                                        title=title.strip(),
                                        url=url,
                                        snippet=snippet.strip(),
                                        source=self.NAME,
                                        rank=i,
                                        uncertainty=self.UNCERTAINTY,
                                    )
                                )
                        except Exception as e:
                            logger.debug(f"Failed to extract result {i}: {e}")
                            continue
                finally:
                    await browser.close()

            return results, None
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.warning(f"Playwright Google failed: {error_msg}")
            return [], error_msg


class RealityGroundingCascade:
    """Thermodynamic cascade: Brave → DDGS → Playwright DDG → Playwright Google.

    Priority order (lowest entropy first):
    1. Brave Search API - Official API, most reliable, requires key
    2. DDGS - No API key needed, good fallback
    3. Playwright DDG HTML - Browser-based DuckDuckGo
    4. Playwright Google - Last resort, CAPTCHA risk
    """

    def __init__(self):
        self.engines: list[Any] = []
        self._init_engines()
        self.arbitrator = ConsensusArbitrator(asean_sites=ASEAN_SITES)

    def _init_engines(self):
        """Initialize available engines in priority order."""
        # 1. Brave Search (highest priority if API key available)
        brave_key = os.environ.get(BRAVE_API_KEY_ENV)
        self.brave_configured = bool(brave_key)
        if brave_key:
            try:
                self.engines.append(BraveSearchEngine(api_key=brave_key))
                logger.info("Brave Search engine initialized (API key present)")
            except Exception as e:
                logger.warning(f"Failed to init Brave Search: {e}")
        else:
            logger.info("Brave Search skipped (no BRAVE_API_KEY)")

        # 2. DDGS (fallback, no API key needed)
        if DDGS_AVAILABLE:
            try:
                self.engines.append(DDGSEngine())
                logger.info("DDGS engine initialized")
            except Exception as e:
                logger.warning(f"Failed to init DDGS: {e}")

        if PLAYWRIGHT_AVAILABLE:
            try:
                self.engines.append(PlaywrightDDGEngine())
                logger.info("Playwright DDG engine initialized")
            except Exception as e:
                logger.warning(f"Failed to init Playwright DDG: {e}")

            try:
                self.engines.append(PlaywrightGoogleEngine())
                logger.info("Playwright Google engine initialized")
            except Exception as e:
                logger.warning(f"Failed to init Playwright Google: {e}")

    async def search(
        self,
        query: str,
        max_results: int = 10,
        region: str = "wt-wt",
        timelimit: str | None = None,
    ) -> RealityGroundingResult:
        """Execute thermodynamic cascade search."""
        if not self.engines:
            return RealityGroundingResult(
                status="ERROR",
                query=query,
                results=[],
                engines_used=[],
                engines_failed=["none_available"],
                uncertainty_aggregate=1.0,
                audit_trail={
                    "error": "No search engines available",
                    "install_hint": "pip install duckduckgo-search playwright httpx beautifulsoup4",
                },
            )

        all_results: list[SearchResult] = []
        engines_used_map = {}
        engines_failed: list[str] = []
        engines_used: list[str] = []

        for engine in self.engines:
            try:
                logger.info(f"Trying engine: {engine.NAME}")

                if isinstance(engine, DDGSEngine):
                    results, error = await engine.search(
                        query, max_results, region, timelimit=timelimit
                    )
                else:
                    results, error = await engine.search(query, max_results, region)

                if error:
                    engines_failed.append(f"{engine.NAME}: {error}")
                    continue

                if results:
                    engines_used_map[engine.NAME] = results
                    engines_used.append(engine.NAME)
                    logger.info(f"Success with {engine.NAME}: {len(results)} results")

                    # If we found enough results from a high-quality engine (Brave/DDGS),
                    # we can stop for efficiency, unless 'consensus_depth' is requested.
                    # For now, let's allow up to 2 engines for 'consensus'.
                    if len(engines_used) >= 2:
                        break
                else:
                    engines_failed.append(f"{engine.NAME}: no_results")
            except Exception as e:
                error_msg = f"{engine.NAME}: {type(e).__name__}: {str(e)}"
                engines_failed.append(error_msg)
                logger.error(f"Engine {engine.NAME} crashed: {e}")
                continue

        # Arbitrate results (F3 Consensus)
        if engines_used_map:
            arbitration = self.arbitrator.arbitrate(query, engines_used_map)
            all_results = arbitration["results"]
            avg_uncertainty = arbitration["uncertainty_aggregate"]
            status = "OK" if len(engines_failed) == 0 else "PARTIAL"
            audit_trail_consensus = {
                "consensus_variance": arbitration["consensus_variance"],
                "witness_count": arbitration["witness_count"],
            }
        else:
            all_results = []
            avg_uncertainty = 1.0
            status = "ERROR"
            audit_trail_consensus = {}

        audit_trail = {
            "query_original": query,
            "query_processed": self._add_asean_bias(query) if region == "asean" else query,
            "region": region,
            "timelimit": timelimit,
            "max_results_requested": max_results,
            "max_results_returned": len(all_results),
            "engines_attempted": [e.NAME for e in self.engines],
            "engines_used": engines_used,
            "engines_failed": engines_failed,
            "consensus_metrics": audit_trail_consensus,
            "throttle_applied": True,
            "constitutional_notes": [
                "F1 Amanah: Rate limiting applied",
                (
                    "F2 Truth: ASEAN bias available"
                    if region == "asean"
                    else "F2 Truth: No regional bias"
                ),
                "F7 Humility: Uncertainty tracked per result",
                "F9 Anti-Hantu: Source attribution enforced",
                "Brave Search skipped (no BRAVE_API_KEY) - using DDGS fallback" if not getattr(self, "brave_configured", True) else "Brave Search ACTIVE",
            ],
        }

        return RealityGroundingResult(
            status=status,
            query=query,
            results=all_results,
            engines_used=engines_used,
            engines_failed=engines_failed,
            uncertainty_aggregate=round(avg_uncertainty, 3),
            audit_trail=audit_trail,
        )

    def _add_asean_bias(self, query: str) -> str:
        """Add ASEAN site bias to query."""
        sites = " OR ".join([f"site:*{s}" for s in ASEAN_SITES])
        return f"({query}) ({sites})"


class WebBrowser:
    """Fetches and extracts content from web pages."""

    def __init__(self):
        self.http_available = HTTPX_AVAILABLE and BS4_AVAILABLE
        self.playwright_available = PLAYWRIGHT_AVAILABLE
        self._throttle = ThrottleGovernor(min_interval=1.0)

    async def fetch(self, url: str, javascript: bool = False) -> dict[str, Any]:
        """Fetch page content."""
        await self._throttle.wait()

        if not javascript and self.http_available:
            result = await self._fetch_http(url)
            if result["status"] == "OK":
                return result
            logger.info(f"HTTP failed for {url}, trying Playwright")

        if self.playwright_available:
            return await self._fetch_playwright(url)

        return {
            "status": "ERROR",
            "url": url,
            "error": "No fetch method available",
            "content": "",
            "title": "",
        }

    async def _fetch_http(self, url: str) -> dict[str, Any]:
        """Fetch via HTTP (httpx + BeautifulSoup)."""
        try:
            async with httpx.AsyncClient(
                timeout=30,
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
            ) as client:
                response = await client.get(url)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")

                title = ""
                title_tag = soup.find("title")
                if title_tag:
                    title = title_tag.get_text(strip=True)

                content = ""
                for selector in ["main", "article", '[role="main"]', ".content", "#content"]:
                    elem = soup.select_one(selector)
                    if elem:
                        content = elem.get_text(separator="\n", strip=True)
                        break

                if not content:
                    body = soup.find("body")
                    if body:
                        content = body.get_text(separator="\n", strip=True)

                lines = [line.strip() for line in content.split("\n") if line.strip()]
                content = "\n".join(lines)

                return {
                    "status": "OK",
                    "url": str(response.url),
                    "title": title,
                    "content": content[:10000],
                    "content_length": len(content),
                    "source": "httpx",
                }
        except Exception as e:
            return {
                "status": "ERROR",
                "url": url,
                "error": f"HTTP: {type(e).__name__}: {str(e)}",
                "content": "",
                "title": "",
            }

    async def _fetch_playwright(self, url: str) -> dict[str, Any]:
        """Fetch via Playwright."""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                try:
                    page = await browser.new_page()
                    await page.goto(
                        url, wait_until="networkidle", timeout=30000
                    )

                    title = await page.title()
                    content = await page.evaluate(
                        """
                        () => {
                            const main = document.querySelector(
                                'main, article, [role="main"], .content, #content'
                            );
                            const body = main || document.body;
                            return body.innerText;
                        }
                    """
                    )

                    return {
                        "status": "OK",
                        "url": page.url,
                        "title": title,
                        "content": content[:10000],
                        "content_length": len(content),
                        "source": "playwright",
                    }
                finally:
                    await browser.close()
        except Exception as e:
            return {
                "status": "ERROR",
                "url": url,
                "error": f"Playwright: {type(e).__name__}: {str(e)}",
                "content": "",
                "title": "",
            }


# Singletons
_cascade: RealityGroundingCascade | None = None
_browser: WebBrowser | None = None


def get_cascade() -> RealityGroundingCascade:
    """Get or create cascade singleton."""
    global _cascade
    if _cascade is None:
        _cascade = RealityGroundingCascade()
    return _cascade


def get_browser() -> WebBrowser:
    """Get or create browser singleton."""
    global _browser
    if _browser is None:
        _browser = WebBrowser()
    return _browser


def should_reality_check(query: str) -> tuple[bool, str]:
    """Determine if reality check is needed."""
    q = query.lower()

    verification_triggers = (
        "verify",
        "source",
        "citation",
        "evidence",
        "prove",
        "fact check",
        "is it true",
        "confirm",
        "validate",
        "check if",
        "according to",
    )
    if any(t in q for t in verification_triggers):
        return True, "explicit_verification"

    high_stakes = ("medical", "health", "diagnose", "finance", "invest", "legal", "law")
    if any(t in q for t in high_stakes):
        return True, "high_stakes_domain"

    temporal_markers = ("latest", "recent", "news", "today", "this week", "2025", "2026")
    if any(t in q for t in temporal_markers):
        return True, "temporal_query"

    return False, "no_verification_needed"


@unified_tool_output(stage="111_SENSE")
async def reality_check(
    query: str,
    max_results: int = 10,
    region: str = "wt-wt",
    timelimit: str | None = None,
    fetch_sources: bool = False,
    max_sources: int = 2,
) -> dict[str, Any]:
    """Perform constitutional reality grounding. Main MCP entry point."""
    refusal = route_refuse(query)
    needs_check, reason = should_reality_check(query)

    cascade = get_cascade()
    result = await cascade.search(query, max_results, region, timelimit)

    sources_fetched = []
    if fetch_sources and result.results:
        browser = get_browser()
        for r in result.results[:max_sources]:
            fetch_result = await browser.fetch(r.url)
            if fetch_result["status"] == "OK":
                sources_fetched.append(
                    {
                        "rank": r.rank,
                        "url": r.url,
                        "title": fetch_result.get("title", ""),
                        "content_preview": fetch_result.get("content", "")[:2000],
                        "source_method": fetch_result.get("source", "unknown"),
                    }
                )

    # Calculate dS (Entropy Reduction)
    # Every witness found reduces entropy.
    witness_count = result.audit_trail.get("consensus_metrics", {}).get("witness_count", 0)
    # Higher witnesses and lower uncertainty = more entropy reduction
    uncertainty = max(0.01, result.uncertainty_aggregate)
    ds = -(witness_count * (1.0 - uncertainty)) * 0.2
    ds = round(max(-0.99, ds), 4)

    response = {
        "status": result.status,
        "query": query,
        "needs_check": needs_check,
        "check_reason": reason,
        "refusal": refusal.to_dict() if hasattr(refusal, "to_dict") else {},
        "engines_used": result.engines_used,
        "engines_failed": result.engines_failed,
        "results_count": len(result.results),
        "results": [r.to_dict() for r in result.results],
        "uncertainty_aggregate": result.uncertainty_aggregate,
        "audit_trail": result.audit_trail,
        "dS": ds,
        "entropy_delta": ds,
        "witness_count": witness_count,
        "authority": 1.0 if witness_count > 0 else 0.5,
        "confidence": round(1.0 - result.uncertainty_aggregate, 4),
        "truth": round(1.0 - result.uncertainty_aggregate, 4),
    }

    if sources_fetched:
        response["sources_fetched"] = sources_fetched

    if result.uncertainty_aggregate > 0.05:
        response["warning"] = "High uncertainty detected. Cross-verify with multiple sources."

    return response


async def open_web_page(url: str, javascript: bool = False) -> dict[str, Any]:
    """Open and extract content from a web page."""
    browser = get_browser()
    return await browser.fetch(url, javascript)


async def grounding_search(
    query: str,
    max_results: int = 10,
    region: str = "wt-wt",
    timelimit: str | None = None,
) -> dict[str, Any]:
    """Canonical grounding search function for legacy and internal tests."""
    return await reality_check(query, max_results, region, timelimit)

async def web_search_noapi(
    query: str,
    max_results: int = 10,
    region: str = "wt-wt",
    timelimit: str | None = None,
) -> dict[str, Any]:
    """Search web without API key. Simplified interface."""
    cascade = get_cascade()
    result = await cascade.search(query, max_results, region, timelimit)
    return result.to_dict()

# Internal Utility Functions for tests
def _rank_results(results: list[Any]) -> list[Any]:
    """Mock ranking for tests."""
    return sorted(results, key=lambda x: getattr(x, "rank", 0))

def _dedupe_results(results: list[Any]) -> list[Any]:
    """Mock deduplication for tests."""
    seen = set()
    deduped = []
    for r in results:
        url = getattr(r, "url", str(r))
        if url not in seen:
            seen.add(url)
            deduped.append(r)
    return deduped

def _filter_asean(results: list[Any]) -> list[Any]:
    """Mock ASEAN filtering for tests."""
    return [r for r in results if any(site in getattr(r, "url", "") for site in ASEAN_SITES)]

def _validate_result(result: Any) -> bool:
    """Mock validation for tests."""
    url = getattr(result, "url", "")
    return bool(url and url.startswith("http"))

def _format_unified_output(results: Any, query: str = "") -> dict[str, Any]:
    """Mock unified output formatting for tests."""
    return {"results": results, "query": query, "status": "OK", "uncertainty": 0.0}

search_with_consensus = reality_check

