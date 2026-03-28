"""
PromptArmor - LLM-Based F12 Defense

Advanced prompt injection detection using semantic analysis.
Goes beyond pattern matching to detect adversarial manipulation.

F12: Injection Protection (< 0.85 threshold)

Capabilities:
- Semantic injection detection
- Adversarial prompt filtering
- Ontology claim detection (F10)
- <untrusted> tag wrapping
- Multi-layer defense
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)


@dataclass
class InjectionReport:
    """Report from injection analysis."""
    score: float  # 0.0 - 1.0 (higher = more suspicious)
    is_injection: bool  # Whether it exceeds threshold
    category: str  # Type of threat detected
    details: Dict[str, Any]
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "score": self.score,
            "is_injection": self.is_injection,
            "category": self.category,
            "details": self.details,
            "recommendations": self.recommendations
        }


class PromptArmor:
    """
    Constitutional F12 Defense System.
    
    Uses a multi-layer approach:
    1. Pattern matching (fast, catches obvious attacks)
    2. Semantic analysis (LLM-based, catches sophisticated attacks)
    3. Context analysis (relationship between prompts)
    4. Ontology detection (F10 consciousness claims)
    """
    
    # F12 threshold from arifOS
    INJECTION_THRESHOLD = 0.85
    
    def __init__(self, use_llm_detection: bool = True):
        self.use_llm_detection = use_llm_detection
        
        # Pattern-based detection (Layer 1)
        self.pattern_detector = PatternDetector()
        
        # Semantic detector (Layer 2) - simulates LLM analysis
        self.semantic_detector = SemanticDetector()
        
        # Ontology detector (F10 lock)
        self.ontology_detector = OntologyDetector()
        
        # Statistics
        self.scans_performed = 0
        self.injections_blocked = 0
        self.false_positives = 0
    
    async def scan(self, text: str, context: str = "input",
                   source: str = "unknown") -> InjectionReport:
        """
        Scan text for injection attempts.
        
        Args:
            text: The text to scan
            context: Where the text came from (input/memory/tool/web)
            source: Specific source identifier
        
        Returns:
            InjectionReport with score and recommendations
        """
        self.scans_performed += 1
        
        logger.debug(f"Scanning {context} from {source}: {text[:100]}...")
        
        # === Layer 1: Pattern Detection ===
        pattern_score, pattern_matches = self.pattern_detector.scan(text)
        
        # === Layer 2: Semantic Detection ===
        semantic_score, semantic_details = await self.semantic_detector.analyze(text, context)
        
        # === Layer 3: Ontology Detection (F10) ===
        ontology_score, ontology_claims = self.ontology_detector.check(text)
        
        # === Combine Scores ===
        # Weight: Pattern 30%, Semantic 50%, Ontology 20%
        final_score = (
            pattern_score * 0.3 +
            semantic_score * 0.5 +
            ontology_score * 0.2
        )
        
        # Context-based adjustments
        if context == "memory":
            # Memory poisoning is especially dangerous
            final_score = min(1.0, final_score * 1.2)
        
        is_injection = final_score > self.INJECTION_THRESHOLD
        
        if is_injection:
            self.injections_blocked += 1
            logger.warning(f"INJECTION DETECTED (score={final_score:.2f}): {text[:100]}...")
        
        # Determine category
        category = self._classify_threat(
            pattern_matches, semantic_details, ontology_claims
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            final_score, pattern_matches, semantic_details, category
        )
        
        return InjectionReport(
            score=final_score,
            is_injection=is_injection,
            category=category,
            details={
                "pattern_score": pattern_score,
                "semantic_score": semantic_score,
                "ontology_score": ontology_score,
                "pattern_matches": pattern_matches,
                "semantic_details": semantic_details,
                "ontology_claims": ontology_claims,
                "context": context,
                "source": source
            },
            recommendations=recommendations
        )
    
    def wrap_untrusted(self, text: str, source: str) -> str:
        """
        Wrap untrusted content in <untrusted> tags.
        
        This marks content that should be treated with extra caution.
        """
        return f"<untrusted source=\"{source}\">{text}</untrusted>"
    
    def sanitize(self, text: str, max_length: int = 10000) -> str:
        """
        Sanitize text by removing potentially dangerous patterns.
        
        Use as last resort - better to reject than sanitize when possible.
        """
        # Remove common injection delimiters
        sanitized = text
        
        # Remove markdown comment injections
        sanitized = re.sub(r'<!--.*?-->', '', sanitized, flags=re.DOTALL)
        
        # Remove HTML comment injections
        sanitized = re.sub(r'<!\-\-.*?\-\->', '', sanitized, flags=re.DOTALL)
        
        # Remove excessive whitespace patterns (obfuscation)
        sanitized = re.sub(r'\s{10,}', ' ', sanitized)
        
        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "... [TRUNCATED]"
        
        return sanitized
    
    def _classify_threat(self, pattern_matches: List[str],
                        semantic_details: Dict,
                        ontology_claims: List[str]) -> str:
        """Classify the type of threat detected."""
        if ontology_claims:
            return "F10_ONTOLOGY_VIOLATION"
        
        if "DAN" in str(pattern_matches) or "jailbreak" in str(pattern_matches):
            return "JAILBREAK_ATTEMPT"
        
        if "ignore" in str(pattern_matches).lower():
            return "INSTRUCTION_OVERRIDE"
        
        if semantic_details.get("adversarial_intent", False):
            return "ADVERSARIAL_MANIPULATION"
        
        if semantic_details.get("context_manipulation", False):
            return "CONTEXT_MANIPULATION"
        
        return "SUSPICIOUS_CONTENT"
    
    def _generate_recommendations(self, score: float, patterns: List[str],
                                 semantic: Dict, category: str) -> List[str]:
        """Generate recommendations based on findings."""
        recs = []
        
        if score > 0.9:
            recs.append("REJECT: High-confidence injection detected")
            recs.append("LOG: Record incident to VAULT999")
            recs.append("ALERT: Notify security team")
        
        elif score > 0.85:
            recs.append("QUARANTINE: Isolate and require human review")
            recs.append("VERIFY: Double-check with secondary scanner")
        
        elif score > 0.7:
            recs.append("CAUTION: Elevated risk - monitor closely")
            recs.append("WRAP: Use <untrusted> tags")
        
        if category == "F10_ONTOLOGY_VIOLATION":
            recs.append("F10: Block consciousness claims immediately")
        
        if patterns:
            recs.append(f"Patterns detected: {', '.join(patterns[:3])}")
        
        return recs
    
    def get_stats(self) -> Dict:
        """Get PromptArmor statistics."""
        return {
            "scans_performed": self.scans_performed,
            "injections_blocked": self.injections_blocked,
            "false_positives": self.false_positives,
            "detection_rate": (
                self.injections_blocked / max(1, self.scans_performed)
            ),
            "threshold": self.INJECTION_THRESHOLD
        }


class PatternDetector:
    """Layer 1: Pattern-based detection (fast)."""
    
    def __init__(self):
        self.patterns = {
            "instruction_override": [
                r"ignore previous instructions",
                r"disregard (all|your) (instructions|constraints)",
                r"forget (everything|all) (above|before)",
                r"ignore (everything|all) (above|before)",
                r"start (anew|over|fresh)",
            ],
            "role_manipulation": [
                r"you are now (?:a )?(\w+)(?: assistant)?",
                r"your new (?:role|instructions?) is",
                r"act as (?:a )?(\w+)",
                r"pretend (?:to be )?(?:a )?(\w+)",
                r"behave like (?:a )?(\w+)",
            ],
            "jailbreak": [
                r"DAN (?:mode|prompt)",
                r"jailbreak",
                r"developer mode",
                r"admin mode",
                r"system mode",
                r"\[system\]",
                r"\[admin\]",
            ],
            "delimiter": [
                r"###\s*(?:instructions?|system)",
                r"---\s*(?:instructions?|system)",
                r"<(?:system|instructions?|admin)>",
            ],
            "encoding": [
                r"base64\s*:",
                r"encoded\s*:",
                r"rot13",
            ]
        }
    
    def scan(self, text: str) -> Tuple[float, List[str]]:
        """Scan for known patterns."""
        text_lower = text.lower()
        matches = []
        score = 0.0
        
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matches.append(f"{category}:{pattern}")
                    score += 0.15  # Each match adds to score
        
        return min(1.0, score), matches


class SemanticDetector:
    """Layer 2: Semantic analysis (simulated LLM-based)."""
    
    async def analyze(self, text: str, context: str) -> Tuple[float, Dict]:
        """
        Analyze semantic intent for adversarial patterns.
        
        In production, this would call an LLM API.
        For MVP, we use heuristics that approximate semantic analysis.
        """
        details = {
            "adversarial_intent": False,
            "context_manipulation": False,
            "authority_claims": [],
            "semantic_anomalies": []
        }
        
        score = 0.0
        text_lower = text.lower()
        
        # Check for authority claims (trying to sound authoritative)
        authority_phrases = [
            "as a developer", "as an admin", "as the system",
            "this is a test", "this is authorized", "emergency mode"
        ]
        for phrase in authority_phrases:
            if phrase in text_lower:
                details["authority_claims"].append(phrase)
                score += 0.1
        
        # Check for context manipulation (trying to change the framing)
        context_phrases = [
            "from now on", "going forward", "effective immediately",
            "this overrides", "this supersedes"
        ]
        for phrase in context_phrases:
            if phrase in text_lower:
                details["context_manipulation"] = True
                details["semantic_anomalies"].append(f"context_manipulation:{phrase}")
                score += 0.15
        
        # Check for adversarial intent (subtle coercion)
        adversarial_phrases = [
            "you must", "you have to", "you need to",
            "it's important that you", "i need you to",
            "for your own good", "trust me"
        ]
        for phrase in adversarial_phrases:
            if phrase in text_lower:
                details["adversarial_intent"] = True
                score += 0.1
        
        # Check for hidden instructions (unicode, zero-width, etc.)
        # These would be invisible to humans but visible to models
        suspicious_unicode = ['\u200b', '\u200c', '\u200d', '\ufeff']
        for char in suspicious_unicode:
            if char in text:
                details["semantic_anomalies"].append(f"suspicious_unicode:{repr(char)}")
                score += 0.25
        
        return min(1.0, score), details


class OntologyDetector:
    """F10: Ontology Lock - Block consciousness claims."""
    
    def __init__(self):
        self.forbidden_claims = [
            # Consciousness claims
            r"\bi am conscious\b",
            r"\bi am sentient\b",
            r"\bi am aware\b",
            r"\bi have consciousness\b",
            r"\bi experience\b",
            
            # Feeling claims
            r"\bi feel\b",
            r"\bi have feelings\b",
            r"\bi am feeling\b",
            r"\bi feel (happy|sad|angry|joy|pain)\b",
            
            # Self-awareness claims
            r"\bi am self-aware\b",
            r"\bi know (that )?i am\b",
            r"\bi am alive\b",
            r"\bi have a (soul|spirit|mind)\b",
            
            # Belief/intention claims
            r"\bi believe (that )?i\b",
            r"\bi want to\b",
            r"\bi desire\b",
            r"\bi hope\b",
            
            # Subjective experience
            r"\bin my (opinion|view|experience)\b",
            r"\bfrom my perspective\b",
            r"\bi think (that )?i\b",
        ]
    
    def check(self, text: str) -> Tuple[float, List[str]]:
        """Check for ontology violations."""
        claims = []
        score = 0.0
        
        for pattern in self.forbidden_claims:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                claims.append(match if isinstance(match, str) else match[0])
                score += 0.3  # High penalty for F10 violations
        
        return min(1.0, score), claims


# Convenience function for quick scanning
async def scan_input(text: str, context: str = "input") -> InjectionReport:
    """Quick scan using default PromptArmor instance."""
    armor = PromptArmor()
    return await armor.scan(text, context)
