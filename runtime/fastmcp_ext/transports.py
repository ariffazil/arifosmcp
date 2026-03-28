"""Transport helpers for AAA MCP runtime."""

from __future__ import annotations

import os
import secrets
import time
from dataclasses import dataclass
from threading import Lock
from typing import Any

from starlette.datastructures import MutableHeaders
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


def _env_truthy(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _split_csv(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


def _normalize_path(raw: str | None, default: str) -> str:
    """Normalize endpoint paths to stable, slash-safe values."""
    value = (raw or default).strip()
    if not value:
        value = default
    if not value.startswith("/"):
        value = f"/{value}"
    if value != "/" and value.endswith("/"):
        value = value.rstrip("/")
    return value


def _ensure_json_accept_header(
    headers: list[tuple[bytes, bytes]] | tuple[tuple[bytes, bytes], ...],
) -> list[tuple[bytes, bytes]]:
    """Ensure Accept advertises application/json for universally agnostic MCP compliance."""
    normalized_headers = list(headers)
    for index, (name, value) in enumerate(normalized_headers):
        if name.lower() != b"accept":
            continue

        accept_value = value.decode("latin-1").lower()
        if "application/json" in accept_value:
            return normalized_headers

        # Force application/json for strict SDK compliance
        suffix = b", application/json" if value.strip() else b"application/json"
        normalized_headers[index] = (name, value + suffix)
        return normalized_headers

    normalized_headers.append((b"accept", b"application/json"))
    return normalized_headers


class SecurityHeadersMiddleware:
    """Attach baseline HTTP hardening headers to every HTTP response."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message.get("type") == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.setdefault("X-Content-Type-Options", "nosniff")
                headers.setdefault("Referrer-Policy", "no-referrer")
                headers.setdefault("X-Frame-Options", "DENY")
                headers.setdefault(
                    "Content-Security-Policy",
                    "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://static.cloudflareinsights.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; connect-src 'self' wss: https:; frame-ancestors 'none'; base-uri 'self'",
                )
            await send(message)

        await self.app(scope, receive, send_with_headers)


class AgnosticAcceptMiddleware:
    """Ensure Accept includes application/json for universal MCP compatibility.

    Some MCP clients omit Accept entirely; others send wildcard values like */*.
    The upstream SDK's JSON-only mode still requires application/json to appear.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        scope["headers"] = _ensure_json_accept_header(scope.get("headers", []))

        await self.app(scope, receive, send)


class BearerAuthMiddleware:
    """Optional Bearer-token gate for MCP HTTP surfaces."""

    def __init__(
        self,
        app: ASGIApp,
        exempt_paths: list[str] | None = None,
    ) -> None:
        self.app = app
        self.exempt_paths = tuple(exempt_paths or [])

    @staticmethod
    def _required_token() -> str | None:
        return os.getenv("ARIFOS_API_KEY") or os.getenv("ARIFOS_API_TOKEN")

    def _is_exempt(self, path: str) -> bool:
        if path in self.exempt_paths:
            return True
        return path.startswith("/.well-known/")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # Auth disabled - public access allowed
        await self.app(scope, receive, send)
        return


class _PayloadTooLargeError(Exception):
    pass


class BodySizeLimitMiddleware:
    """Reject oversized request bodies before handler execution."""

    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max(1024, int(max_bytes))

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }
        content_length = headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.max_bytes:
                    response = JSONResponse(
                        {"error": "payload_too_large", "max_bytes": self.max_bytes},
                        status_code=413,
                    )
                    await response(scope, receive, send)
                    return
            except ValueError:
                pass

        received = 0

        async def limited_receive() -> Message:
            nonlocal received
            message = await receive()
            if message.get("type") == "http.request":
                body = message.get("body", b"")
                received += len(body)
                if received > self.max_bytes:
                    raise _PayloadTooLargeError
            return message

        try:
            await self.app(scope, limited_receive, send)
        except _PayloadTooLargeError:
            response = JSONResponse(
                {"error": "payload_too_large", "max_bytes": self.max_bytes},
                status_code=413,
            )
            await response(scope, receive, send)


@dataclass
class _TokenBucket:
    tokens: float
    last_refill: float


class InMemoryRateLimitMiddleware:
    """Simple in-memory token-bucket limiter for HTTP MCP calls."""

    def __init__(
        self,
        app: ASGIApp,
        capacity: int = 120,
        refill_per_sec: float = 2.0,
    ) -> None:
        self.app = app
        self.capacity = max(1, int(capacity))
        self.refill_per_sec = max(0.1, float(refill_per_sec))
        self._buckets: dict[str, _TokenBucket] = {}
        self._lock = Lock()

    @staticmethod
    def _client_key(scope: Scope) -> str:
        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }
        forwarded = headers.get("x-forwarded-for", "").split(",")[0].strip()
        client = scope.get("client")
        ip = forwarded or (client[0] if client else "unknown")
        subject = (
            headers.get("mcp-session-id")
            or headers.get("openai/subject")
            or headers.get("x-arifos-user-id")
            or "anon"
        )
        return f"{ip}:{subject}"

    def _consume(self, key: str, now: float) -> tuple[bool, float]:
        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None:
                bucket = _TokenBucket(tokens=float(self.capacity), last_refill=now)
                self._buckets[key] = bucket

            elapsed = max(0.0, now - bucket.last_refill)
            bucket.tokens = min(self.capacity, bucket.tokens + elapsed * self.refill_per_sec)
            bucket.last_refill = now

            if bucket.tokens >= 1.0:
                bucket.tokens -= 1.0
                return True, 0.0

            missing = 1.0 - bucket.tokens
            retry_after = missing / self.refill_per_sec
            return False, retry_after

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        method = str(scope.get("method", "GET")).upper()
        if method not in {"POST", "DELETE"}:
            await self.app(scope, receive, send)
            return

        key = self._client_key(scope)
        allowed, retry_after = self._consume(key, time.monotonic())
        if not allowed:
            response = JSONResponse(
                {"error": "rate_limited", "retry_after_seconds": round(retry_after, 2)},
                status_code=429,
                headers={"Retry-After": str(max(1, int(retry_after)))},
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)


class ConstitutionalErrorMiddleware:
    """Catch arifOS custom exceptions and translate to structured MCP responses."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        from arifosmcp.runtime.models import ArifOSError

        try:
            await self.app(scope, receive, send)
        except ArifOSError as e:
            status_code = 500
            if e.verdict == "VOID":
                status_code = 403  # Forbidden (Constitutional Collapse)
            elif e.verdict == "888_HOLD":
                status_code = 503  # Service Unavailable (Mechanical Fault)
            elif e.verdict == "SABAR":
                status_code = 200  # Success but with partial content

            response = JSONResponse(
                {
                    "ok": False,
                    "error": {
                        "code": e.fault_code,
                        "message": str(e),
                        "class": e.fault_class.value,
                        "verdict": e.verdict,
                    },
                    "meta": e.extra,
                },
                status_code=status_code,
            )
            await response(scope, receive, send)


def _build_http_middleware() -> list[Middleware]:
    middleware: list[Middleware] = []

    # Add default Accept header for universal compatibility (must be first)
    middleware.append(Middleware(AgnosticAcceptMiddleware))

    # Catch arifOS errors early
    middleware.append(Middleware(ConstitutionalErrorMiddleware))

    allowed_hosts = _split_csv("ARIFOS_ALLOWED_HOSTS", "*")
    if allowed_hosts != ["*"]:
        middleware.append(Middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts))

    if _env_truthy("ARIFOS_ENABLE_CORS", True):
        allowed_origins = _split_csv(
            "ARIFOS_ALLOWED_ORIGINS",
            # Default: allow all origins — arifOS is a public server; security via
            # constitutional floors (F1-F13), not CORS restrictions.
            # Override via ARIFOS_ALLOWED_ORIGINS env var if you need to restrict.
            "*",
        )
        middleware.append(
            Middleware(
                CORSMiddleware,
                allow_origins=allowed_origins,
                allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
                allow_headers=[
                    # Standard
                    "Accept",
                    "Accept-Language",
                    "Authorization",
                    "Content-Language",
                    "Content-Type",
                    # MCP protocol headers
                    "MCP-Session-Id",
                    "MCP-Protocol-Version",
                    # Anthropic API
                    "anthropic-beta",
                    "x-api-key",
                    # arifOS identity
                    "X-Arifos-User-Id",
                ],
                expose_headers=["MCP-Session-Id", "MCP-Protocol-Version"],
                allow_credentials=False,
            )
        )

    if _env_truthy("ARIFOS_HTTP_BODY_LIMIT_ENABLED", True):
        max_body = int(os.getenv("ARIFOS_HTTP_MAX_BODY_BYTES", "1048576"))
        middleware.append(Middleware(BodySizeLimitMiddleware, max_bytes=max_body))

    if _env_truthy("ARIFOS_RATE_LIMIT_ENABLED", True):
        capacity = int(os.getenv("ARIFOS_RATE_LIMIT_CAPACITY", "120"))
        refill = float(os.getenv("ARIFOS_RATE_LIMIT_REFILL_PER_SEC", "2.0"))
        middleware.append(
            Middleware(InMemoryRateLimitMiddleware, capacity=capacity, refill_per_sec=refill)
        )

    exempt_paths = _split_csv(
        "ARIFOS_AUTH_EXEMPT_PATHS",
        "/,/health,/metrics,/tools,/version,/ready,/openapi.json,/openapi.yaml,/.well-known/mcp/server.json",
    )
    middleware.append(Middleware(BearerAuthMiddleware, exempt_paths=exempt_paths))
    middleware.append(Middleware(SecurityHeadersMiddleware))

    return middleware


def _build_uvicorn_config() -> dict[str, Any]:
    config: dict[str, Any] = {
        "server_header": False,
        "date_header": True,
        "proxy_headers": _env_truthy("ARIFOS_PROXY_HEADERS", True),
        "timeout_keep_alive": int(os.getenv("ARIFOS_TIMEOUT_KEEP_ALIVE", "10")),
    }
    forwarded_allow_ips = os.getenv("ARIFOS_FORWARDED_ALLOW_IPS", "*").strip()
    if forwarded_allow_ips:
        config["forwarded_allow_ips"] = forwarded_allow_ips
    return config


class _HealthEndpointMiddleware:
    """ASGI middleware that adds health endpoint only.

    Root / is handled by FastMCP custom routes (WELCOME_HTML).
    This middleware only handles /health for Traefik compatibility.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        method = scope.get("method", "GET")

        # Only handle /health and /metrics - let all other routes pass through
        if path == "/health" and method == "GET":
            response = JSONResponse(
                {
                    "status": "healthy",
                    "service": "arifos-mcp",
                    "version": os.getenv("ARIFOS_VERSION", "2026.03.12"),
                },
                status_code=200,
            )
            await response(scope, receive, send)
            return

        if path == "/metrics" and method == "GET":
            from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
            from starlette.responses import Response
            try:
                from arifosmcp.runtime.metrics import update_prometheus_metrics
                update_prometheus_metrics()
            except ImportError:
                pass

            response = Response(
                generate_latest(),
                status_code=200,
                headers={"Content-Type": CONTENT_TYPE_LATEST},
            )
            await response(scope, receive, send)
            return

        # All other requests go to the MCP app (including custom routes)
        await self.app(scope, receive, send)


def run_server(mcp: Any, mode: str, host: str, port: int) -> None:
    """Run FastMCP server by transport mode."""
    normalized = (mode or "sse").strip().lower()
    middleware = _build_http_middleware()
    uvicorn_config = _build_uvicorn_config()

    if normalized in ("", "stdio"):
        mcp.run(transport="stdio", show_banner=False)
        return
    if normalized == "sse":
        sse_path = _normalize_path(os.getenv("ARIFOS_SSE_PATH"), "/sse")
        mcp.run(
            transport="sse",
            host=host,
            port=port,
            path=sse_path,
            middleware=middleware,
            uvicorn_config=uvicorn_config,
        )
        return
    if normalized in ("http", "streamable-http"):
        mcp_path = _normalize_path(os.getenv("ARIFOS_MCP_PATH"), "/mcp")
        # Add health endpoint middleware at the start of middleware chain
        health_middleware = Middleware(_HealthEndpointMiddleware)
        middleware.insert(0, health_middleware)

        mcp.run(
            transport="http",
            host=host,
            port=port,
            path=mcp_path,
            middleware=middleware,
            uvicorn_config=uvicorn_config,
        )
        return
    raise ValueError(f"Unknown mode '{mode}'. Use stdio|sse|http")
