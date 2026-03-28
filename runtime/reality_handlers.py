from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any

import httpx

from .reality_models import (
    Actor,
    BundleInput,
    BundleStatus,
    ErrorCode,
    EvidenceBundle,
    FetchResult,
    SearchResult,
    StatusError,
)

# Vector auto-sync bridge (SEALTRIWITNESS Phase 2)
try:
    from ..intelligence.tools.vector_bridge import auto_sync_bundle

    VECTOR_SYNC_AVAILABLE = True
except ImportError:
    VECTOR_SYNC_AVAILABLE = False

    async def auto_sync_bundle(*args, **kwargs):
        """No-op when vector bridge not available."""
        pass


logger = logging.getLogger(__name__)

# Constants from server.py / tools.py
BROWSERLESS_URL = os.getenv("BROWSERLESS_URL", "http://headless_browser:3000")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
JINA_API_KEY = os.getenv("JINA_API_KEY", "")
PPLX_API_KEY = os.getenv("PPLX_API_KEY", "")

try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False


class RealityHandler:
    def __init__(self):
        pass

    def _map_exception(self, e: Exception) -> ErrorCode:
        err_str = str(e).lower()
        if (
            isinstance(e, httpx.ConnectError)
            or "dns" in err_str
            or "name or service not known" in err_str
        ):
            return "DNS_FAIL"
        if isinstance(e, httpx.TimeoutException) or "timed out" in err_str:
            return "TIMEOUT"
        if "ssl" in err_str or "certificate" in err_str:
            return "TLS_FAIL"
        if isinstance(e, httpx.HTTPStatusError):
            code = e.response.status_code
            if code == 403 or code == 429:
                return "WAF_BLOCK"
            if 400 <= code < 500:
                return "HTTP_4XX"
            return "HTTP_5XX"
        return "PARSE_FAIL"

    def _map_http_error(self, status_code: int) -> ErrorCode:
        if status_code == 403 or status_code == 429:
            return "WAF_BLOCK"
        if 400 <= status_code < 500:
            return "HTTP_4XX"
        return "HTTP_5XX"

    async def fetch_url(self, url: str, render: str = "auto", policy: Any = None) -> FetchResult:
        start_time = time.time()
        timings = {"dns": 0.0, "connect": 0.0, "ttfb": 0.0, "total": 0.0}

        res = FetchResult(url=url)
        use_render = render == "always"

        try:
            if render != "always":
                async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                    h_start = time.time()
                    try:
                        response = await client.get(
                            url,
                            headers={
                                "User-Agent": "Mozilla/5.0 arifOS/2026.03.13 (RealityCompass/v1)",
                                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                                "Cache-Control": "no-cache",
                            },
                        )
                        timings["total"] = (time.time() - h_start) * 1000

                        res.status_code = response.status_code
                        res.content_type = response.headers.get("content-type")
                        res.headers_subset = {
                            k: v
                            for k, v in response.headers.items()
                            if k.lower()
                            in ["server", "cache-control", "x-cache", "cf-ray", "content-encoding"]
                        }
                        res.final_url = str(response.url)
                        res.redirects = len(response.history)

                        if response.status_code >= 400:
                            if response.status_code in [403, 429] and render == "auto":
                                use_render = True
                                res.error_message = (
                                    f"HTTP {response.status_code} -> triggering render fallback"
                                )
                            else:
                                res.error_message = (
                                    f"HTTP {response.status_code}: {response.text[:200]}"
                                )
                                res.status_code = response.status_code
                        else:
                            res.raw_content = response.text
                            res.content_length = len(response.text)
                    except Exception as inner_e:
                        res.exception_class = inner_e.__class__.__name__
                        res.error_message = str(inner_e)
                        if render == "auto":
                            use_render = True

            if use_render:
                r_start = time.time()
                async with httpx.AsyncClient(timeout=30.0) as b_client:
                    try:
                        token = os.getenv("BROWSERLESS_TOKEN", "").strip()
                        endpoint = (
                            f"{BROWSERLESS_URL}/content?token={token}"
                            if token
                            else f"{BROWSERLESS_URL}/content"
                        )
                        b_res = await b_client.post(
                            endpoint,
                            json={"url": url},
                            headers={"Content-Type": "application/json"},
                        )
                        if b_res.status_code == 200:
                            res.raw_content = b_res.text
                            res.content_length = len(b_res.text)
                            res.render_fallback_used = True
                            res.status_code = 200
                            res.error_message = None
                            timings["total"] = (time.time() - r_start) * 1000
                        else:
                            res.error_message = (
                                f"Browserless Fail {b_res.status_code}: {b_res.text[:200]}"
                            )
                            res.status_code = b_res.status_code
                    except Exception as b_e:
                        res.error_message = f"Browserless Exception: {str(b_e)}"
                        res.exception_class = b_e.__class__.__name__

        except Exception as e:
            res.exception_class = e.__class__.__name__
            res.error_message = str(e)
            res.status_code = res.status_code or 0

        res.latency_ms = timings
        return res

    async def search_brave(
        self, query: str, top_k: int = 5, region: str = "MY", locale: str = "en-MY"
    ) -> SearchResult:
        start_time = time.time()
        res = SearchResult(engine="brave", query=query)

        if not BRAVE_API_KEY:
            if DDGS_AVAILABLE:
                logger.info("Brave key missing, falling back to DDGS")
                return await self.search_ddgs(query, top_k)
            res.error = "BRAVE_API_KEY not set and DDGS not available"
            res.status_code = 401
            return res

        # Brave V1 implementation...
        search_lang = locale.split("-")[0] if "-" in locale else "en"
        params = {
            "q": query,
            "count": min(max(1, top_k), 20),
            "search_lang": search_lang,
            "ui_lang": locale,
            "country": region,
            "text_decorations": 0,
            "spellcheck": 1,
        }
        res.request_params = params

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    params=params,
                    headers={
                        "Accept": "application/json",
                        "X-Subscription-Token": BRAVE_API_KEY,
                        "Cache-Control": "no-cache",
                        "Accept-Encoding": "gzip",
                    },
                )
                res.status_code = response.status_code
                if response.status_code == 200:
                    data = response.json()
                    web_results = data.get("web", {}) or {}
                    res.results = web_results.get("results", []) if web_results else []
                    if not res.results and DDGS_AVAILABLE:
                         logger.info("Brave returned no results, trying DDGS fallback")
                         return await self.search_ddgs(query, top_k)
                elif DDGS_AVAILABLE:
                      logger.warning(f"Brave error {response.status_code}, trying DDGS fallback")
                      return await self.search_ddgs(query, top_k)
                else:
                    res.error = f"Brave API Error {response.status_code}: {response.text[:500]}"
        except Exception as e:
            if DDGS_AVAILABLE:
                logger.warning(f"Brave exception ({type(e).__name__}), trying DDGS fallback")
                return await self.search_ddgs(query, top_k)
            res.error = f"{e.__class__.__name__}: {str(e)}"
            res.status_code = 0

        res.latency_ms = (time.time() - start_time) * 1000
        return res

    async def search_ddgs(self, query: str, top_k: int = 5) -> SearchResult:
        """Search DuckDuckGo."""
        start_time = time.time()
        res = SearchResult(engine="ddgs", query=query)
        if not DDGS_AVAILABLE:
            res.error = "ddgs library not installed"
            return res
        
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=top_k))
                res.results = [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "description": r.get("body", "")
                    }
                    for r in results
                ]
                res.status_code = 200
        except Exception as e:
            res.error = f"DDGS error: {str(e)}"
            res.status_code = 500
        
        res.latency_ms = (time.time() - start_time) * 1000
        return res

    async def handle_compass(
        self, bundle_input: BundleInput, auth_context: dict[str, Any]
    ) -> EvidenceBundle:
        # P0 Invariant: Never Blank
        actor = Actor(
            actor_id=auth_context.get("actor_id", "anonymous"),
            authority_level=auth_context.get("authority_level", "anonymous"),
            token_fingerprint=auth_context.get("token_fingerprint"),
        )

        bundle = EvidenceBundle(
            status=BundleStatus(
                state="PARTIAL",
                stage="111_SENSE",
                verdict="SABAR",
                message="Reality acquisition initiated.",
            ),
            input=bundle_input,
            actor=actor,
        )

        is_url = bundle_input.value.startswith(("http://", "https://"))
        mode = bundle_input.mode
        if mode == "auto":
            mode = "fetch" if is_url else "search"

        try:
            if mode == "fetch":
                f_res = await self.fetch_url(bundle_input.value, render=bundle_input.render)
                bundle.results.append(f_res)
                if f_res.status_code == 200 and f_res.content_length > 0:
                    bundle.status.state = "SUCCESS"
                    bundle.status.verdict = "SEAL"
                    bundle.status.message = "Successfully fetched evidence."
                else:
                    bundle.status.state = "SABAR"
                    err_code = (
                        self._map_exception(Exception(f_res.error_message))
                        if f_res.error_message
                        else "NO_RESULTS"
                    )
                    bundle.status.errors.append(
                        StatusError(
                            code=err_code,
                            detail=f_res.error_message or "Empty content",
                            hint="Try render='always' if site is dynamic.",
                        )
                    )

            elif mode == "search":
                s_res = await self.search_brave(bundle_input.value, top_k=bundle_input.top_k)
                bundle.results.append(s_res)

                if s_res.status_code == 200 and s_res.results:
                    bundle.status.state = "SUCCESS"
                    bundle.status.verdict = "SEAL"
                    bundle.status.message = f"Found {len(s_res.results)} search candidates."

                    if bundle_input.fetch_top_k > 0:
                        bundle.status.message += (
                            f" Initiating fetch for top {bundle_input.fetch_top_k}."
                        )
                        fetch_tasks = [
                            self.fetch_url(r["url"], render=bundle_input.render)
                            for r in s_res.results[: bundle_input.fetch_top_k]
                        ]
                        f_results = await asyncio.gather(*fetch_tasks)
                        bundle.results.extend(f_results)
                else:
                    bundle.status.state = "SABAR"
                    err_code = (
                        "ENGINE_422"
                        if s_res.status_code == 422
                        else ("NO_RESULTS" if s_res.status_code == 200 else "HTTP_5XX")
                    )
                    bundle.status.errors.append(
                        StatusError(
                            code=err_code,
                            detail=s_res.error or "No results found.",
                            hint="Check query syntax or API status.",
                        )
                    )

        except Exception as e:
            bundle.status.state = "ERROR"
            bundle.status.message = f"Critical handler failure: {str(e)}"
            bundle.status.errors.append(StatusError(code="SCHEMA_FAIL", detail=str(e)))

        # SEALTRIWITNESS Phase 2: Auto-sync to vector memory (fire-and-forget)
        if VECTOR_SYNC_AVAILABLE and bundle.status.state == "SUCCESS":
            try:
                # Run async without blocking response
                asyncio.create_task(
                    auto_sync_bundle(
                        bundle=bundle,
                        session_id=auth_context.get("session_id", "global"),
                        actor_id=auth_context.get("actor_id", "anonymous"),
                    )
                )
            except Exception as sync_e:
                logger.warning(f"Vector auto-sync failed (non-blocking): {sync_e}")

        return bundle


handler = RealityHandler()
