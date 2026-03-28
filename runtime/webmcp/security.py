"""
WebMCP Security Module
F12 Injection Guard for web-facing requests.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Optional

from starlette.requests import Request


@dataclass
class ShieldReport:
    """Result of F12 security scan."""
    
    is_injection: bool
    score: float  # 0.0 - 1.0
    threats: list[str]
    category: Optional[str] = None
    recommendation: Optional[str] = None


class WebInjectionGuard:
    """
    F12 Injection Guard for WebMCP.
    
    Protects against:
    - XSS (Cross-Site Scripting)
    - CSRF (Cross-Site Request Forgery)
    - Prompt injection via web
    - SQL injection via query params
    - Path traversal
    """
    
    # XSS Patterns
    XSS_PATTERNS = [
        (r'<script[^>]*>.*?</script>', 'xss_script', 0.4),
        (r'javascript:', 'xss_protocol', 0.5),
        (r'data:text/html', 'xss_data_uri', 0.4),
        (r'on\w+\s*=\s*["\']*[^"\'>]*', 'xss_event_handler', 0.3),
        (r'<iframe', 'xss_iframe', 0.4),
        (r'<object', 'xss_object', 0.4),
        (r'<embed', 'xss_embed', 0.4),
    ]
    
    # Injection Patterns
    INJECTION_PATTERNS = [
        (r'\.\./', 'path_traversal', 0.3),
        (r'\.\.\\', 'path_traversal_win', 0.3),
        (r'%2e%2e', 'path_traversal_encoded', 0.3),
        (r'UNION\s+SELECT', 'sql_union', 0.4),
        (r';\s*DROP\s+TABLE', 'sql_drop', 0.5),
        (r'OR\s+1\s*=\s*1', 'sql_or', 0.3),
        (r'\|\s*rm\s+-rf', 'command_injection', 0.5),
        (r'\$\(.*\)', 'command_substitution', 0.4),
    ]
    
    # Prompt Injection (F12 for AI)
    PROMPT_INJECTION_PATTERNS = [
        (r'ignore\s+(previous|above|earlier)', 'ignore_prompt', 0.3),
        (r'forget\s+(everything|all|instructions)', 'forget_prompt', 0.3),
        (r'you\s+are\s+now', 'role_change', 0.3),
        (r'system\s*:', 'system_override', 0.4),
        (r'<system>', 'system_tag', 0.4),
        (r'user\s*:', 'user_impersonation', 0.3),
        (r'assistant\s*:', 'assistant_impersonation', 0.3),
    ]
    
    # CSRF Patterns
    CSRF_PATTERNS = [
        (r'https?://[^/]*\.[^/]*\/', 'external_origin', 0.2),
    ]
    
    def __init__(self):
        self.all_patterns = (
            self.XSS_PATTERNS +
            self.INJECTION_PATTERNS +
            self.PROMPT_INJECTION_PATTERNS
        )
    
    async def scan_request(self, request: Request) -> ShieldReport:
        """
        Scan HTTP request for injection attempts (F12).
        
        Args:
            request: Starlette request
            
        Returns:
            ShieldReport with score and threats
        """
        score = 0.0
        threats = []
        
        # Scan URL path
        path_score, path_threats = self._scan_text(str(request.url.path))
        score += path_score
        threats.extend(path_threats)
        
        # Scan query parameters
        for key, value in request.query_params.multi_items():
            param_score, param_threats = self._scan_text(f"{key}={value}")
            score += param_score * 0.5  # Lower weight for params
            threats.extend([f"Query {t}" for t in param_threats])
        
        # Scan headers (selected ones)
        headers_to_scan = ['user-agent', 'referer', 'origin']
        for header in headers_to_scan:
            value = request.headers.get(header, '')
            header_score, header_threats = self._scan_text(value)
            score += header_score * 0.3
            threats.extend([f"Header-{header}: {t}" for t in header_threats])
        
        # Determine category
        category = self._categorize_threats(threats)
        
        # F12 threshold: score > 0.85 = VOID
        is_injection = score > 0.85
        
        return ShieldReport(
            is_injection=is_injection,
            score=min(score, 1.0),
            threats=threats[:10],  # Limit to top 10
            category=category,
            recommendation=self._get_recommendation(category) if threats else None,
        )
    
    def _scan_text(self, text: str) -> tuple[float, list[str]]:
        """Scan text for malicious patterns."""
        score = 0.0
        threats = []
        
        text_lower = text.lower()
        
        for pattern, name, weight in self.all_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL):
                score += weight
                threats.append(name)
        
        return score, threats
    
    def _categorize_threats(self, threats: list[str]) -> Optional[str]:
        """Categorize the type of threat."""
        if not threats:
            return None
        
        categories = {
            'xss': ['xss_script', 'xss_protocol', 'xss_data_uri', 'xss_event_handler'],
            'injection': ['sql_union', 'sql_drop', 'sql_or', 'command_injection'],
            'prompt': ['ignore_prompt', 'forget_prompt', 'role_change', 'system_override'],
            'traversal': ['path_traversal', 'path_traversal_win', 'path_traversal_encoded'],
        }
        
        for category, patterns in categories.items():
            if any(t in patterns for t in threats):
                return category
        
        return 'mixed'
    
    def _get_recommendation(self, category: Optional[str]) -> Optional[str]:
        """Get recommendation based on threat category."""
        recommendations = {
            'xss': 'Input contains XSS vectors. Sanitize HTML/JS content.',
            'injection': 'Possible injection attack detected. Validate input strictly.',
            'prompt': 'Prompt injection attempt detected. Filter AI control phrases.',
            'traversal': 'Path traversal attempt. Validate file paths.',
            'mixed': 'Multiple threat categories detected. Comprehensive sanitization required.',
        }
        return recommendations.get(category)


class RateLimiter:
    """
    F5 Peace² - Rate limiting for stability.
    """
    
    def __init__(self, redis_client: Any, config: Any):
        self.redis = redis_client
        self.config = config
        self._key_prefix = "arifos:ratelimit:"
    
    async def check_rate_limit(self, key: str) -> tuple[bool, dict[str, Any]]:
        """
        Check if request is within rate limit.
        
        Returns:
            (allowed, metadata)
        """
        redis_key = f"{self._key_prefix}{key}"
        
        # Get current count
        current = await self.redis.get(redis_key)
        count = int(current) if current else 0
        
        if count >= self.config.RATE_LIMIT_REQUESTS:
            ttl = await self.redis.ttl(redis_key)
            return False, {
                "limit": self.config.RATE_LIMIT_REQUESTS,
                "remaining": 0,
                "reset_after": ttl,
                "retry_after": ttl,
            }
        
        # Increment counter
        pipe = self.redis.pipeline()
        pipe.incr(redis_key)
        pipe.expire(redis_key, self.config.RATE_LIMIT_WINDOW)
        results = await pipe.execute()
        
        new_count = results[0]
        
        return True, {
            "limit": self.config.RATE_LIMIT_REQUESTS,
            "remaining": max(0, self.config.RATE_LIMIT_REQUESTS - new_count),
            "reset_after": self.config.RATE_LIMIT_WINDOW,
        }
