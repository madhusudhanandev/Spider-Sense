"""
URLAnalysisService (section 8).

Deliberately NOT "ask the LLM if this URL is malicious". Computes technical
signals directly from the URL string (and, where a reputation/domain-age API
key is configured, from that provider) and returns a structured result the
AI service can *interpret* but never override with invented facts.

Security note (section 35): this service must never fetch the URL's content
server-side without SSRF protections. The current implementation only
parses the URL string and does keyword/heuristic checks -- it does not make
outbound requests. A future `follow_redirects` capability must validate
against private/link-local IP ranges before fetching.
"""
import logging
import re
from urllib.parse import urlparse

from app.core.config import get_settings
from app.schemas.common import URLAnalysisResult, URLSignal

logger = logging.getLogger("spidersense.url_analysis")

# Brands commonly impersonated in the scam categories this product targets.
# Extensible taxonomy -- add more as real-world data comes in.
_IMPERSONATION_BRANDS = [
    "paypal", "amazon", "google", "microsoft", "apple", "netflix",
    "sbi", "hdfc", "icici", "axis", "rbi", "irctc", "indiapost",
    "whatsapp", "facebook", "instagram",
]

_SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "update", "confirm", "account",
    "kyc", "otp", "reward", "prize", "free", "urgent", "suspended",
]

_URL_SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "cutt.ly", "rb.gy"}

_IP_HOST_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


class URLAnalysisService:
    def __init__(self) -> None:
        settings = get_settings()
        self._reputation_provider = settings.URL_REPUTATION_PROVIDER
        self._reputation_api_key = settings.URL_REPUTATION_API_KEY

    def analyze(self, raw_url: str) -> URLAnalysisResult:
        parsed = self._safe_parse(raw_url)
        signals: list[URLSignal] = []
        score = 0

        domain = (parsed.hostname or "").lower() if parsed else None
        is_https = parsed.scheme == "https" if parsed else None

        if parsed is None:
            signals.append(URLSignal(type="malformed_url", severity="high", description="The URL could not be parsed."))
            return URLAnalysisResult(url=raw_url, domain=None, is_https=None, risk_score=70, signals=signals, provider="heuristic")

        if not is_https:
            signals.append(URLSignal(type="no_https", severity="medium", description="The link does not use HTTPS."))
            score += 15

        if domain and _IP_HOST_RE.match(domain):
            signals.append(URLSignal(type="ip_address_host", severity="high", description="The link uses a raw IP address instead of a domain name."))
            score += 25

        if domain in _URL_SHORTENERS:
            signals.append(URLSignal(type="url_shortener", severity="medium", description="The link uses a URL shortener, which can hide the real destination."))
            score += 15

        if domain:
            for brand in _IMPERSONATION_BRANDS:
                if brand in domain and not self._is_official_domain(domain, brand):
                    signals.append(URLSignal(
                        type="brand_impersonation",
                        severity="high",
                        description=f"Domain appears to imitate '{brand}' but is not that organization's official domain.",
                    ))
                    score += 35
                    break

        full_lower = raw_url.lower()
        matched_keywords = [kw for kw in _SUSPICIOUS_KEYWORDS if kw in full_lower]
        if len(matched_keywords) >= 2:
            signals.append(URLSignal(
                type="suspicious_keywords",
                severity="medium",
                description=f"URL contains multiple suspicious keywords: {', '.join(matched_keywords[:5])}.",
            ))
            score += 15

        if domain and domain.count("-") >= 3:
            signals.append(URLSignal(type="excessive_hyphens", severity="low", description="Domain contains an unusually high number of hyphens, common in disposable phishing domains."))
            score += 10

        if domain and len(domain.split(".")) >= 4:
            signals.append(URLSignal(type="deep_subdomain", severity="low", description="Domain uses multiple subdomain levels, sometimes used to obscure the true domain."))
            score += 5

        # Reputation / domain-age providers (mocked unless a real key + provider are configured).
        reputation_signals, reputation_score = self._check_reputation(domain)
        signals.extend(reputation_signals)
        score += reputation_score

        score = max(0, min(score, 100))

        return URLAnalysisResult(
            url=raw_url,
            domain=domain,
            is_https=is_https,
            risk_score=score,
            signals=signals,
            provider="heuristic" if self._reputation_provider == "mock" else self._reputation_provider,
        )

    @staticmethod
    def _safe_parse(raw_url: str):
        try:
            candidate = raw_url if "://" in raw_url else f"http://{raw_url}"
            parsed = urlparse(candidate)
            if not parsed.hostname:
                return None
            return parsed
        except Exception:
            return None

    @staticmethod
    def _is_official_domain(domain: str, brand: str) -> bool:
        # Very small allowlist heuristic: exact match or "brand.com"-style root domain.
        return domain == f"{brand}.com" or domain.endswith(f".{brand}.com") or domain == brand

    def _check_reputation(self, domain: str | None) -> tuple[list[URLSignal], int]:
        """
        Placeholder for a real reputation/domain-age lookup (e.g. Google Safe
        Browsing, VirusTotal, WHOIS-based domain age). Returns a clean mock
        result when no provider/key is configured, so the app still runs
        without external API keys (section 8, section 35).
        """
        if self._reputation_provider == "mock" or not self._reputation_api_key or not domain:
            return [], 0

        # Real implementations would call the configured provider here and
        # translate its response into URLSignal entries + a score delta.
        logger.info("Reputation provider '%s' configured but not yet implemented; skipping.", self._reputation_provider)
        return [], 0


_instance: URLAnalysisService | None = None


def get_url_analysis_service() -> URLAnalysisService:
    global _instance
    if _instance is None:
        _instance = URLAnalysisService()
    return _instance
