"""
Lightweight regex-based extraction used as a deterministic backstop
alongside (not instead of) the AI's own entity extraction -- so URLs and
phone numbers are never missed just because the model didn't surface them.
"""
import re

URL_RE = re.compile(r"https?://[^\s<>\"']+")
# Loose international-friendly phone matcher; over-matching is filtered by
# a minimum digit count.
PHONE_RE = re.compile(r"(\+?\d[\d\-\s()]{7,}\d)")
EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


def extract_urls(text: str) -> list[str]:
    return list(dict.fromkeys(URL_RE.findall(text or "")))


def extract_phone_numbers(text: str) -> list[str]:
    candidates = PHONE_RE.findall(text or "")
    cleaned = []
    for c in candidates:
        digits = re.sub(r"\D", "", c)
        if 8 <= len(digits) <= 15:
            cleaned.append(c.strip())
    return list(dict.fromkeys(cleaned))


def extract_emails(text: str) -> list[str]:
    return list(dict.fromkeys(EMAIL_RE.findall(text or "")))


def normalize_domain(url: str) -> str | None:
    from urllib.parse import urlparse

    candidate = url if "://" in url else f"http://{url}"
    try:
        return (urlparse(candidate).hostname or "").lower() or None
    except Exception:
        return None


def normalize_phone(phone: str) -> str:
    return re.sub(r"[\s\-()]", "", phone)
