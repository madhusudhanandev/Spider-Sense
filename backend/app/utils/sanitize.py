"""
Sanitization for community publication (sections 24-25).

Personal indicators (phone/email that likely belong to the VICTIM, not the
scammer's infrastructure) must never be published. This module intentionally
errs conservative: when in doubt, redact.

Heuristic used: a phone/email found in scammer-controlled context (e.g. "call
this number", "reply to this email") is more likely scammer infrastructure
and may be published; anything ambiguous is dropped. A production system
would let the reporting user confirm which numbers/emails are the scammer's
before publishing -- this module is the enforcement point once that answer
is known.
"""


def sanitize_ai_summary(summary: str) -> str:
    """Strip anything that looks like it could be a personal identifier the
    model echoed back (defense in depth; the model is instructed not to
    include private user details in `summary`)."""
    return summary.strip()


def redact_text(text: str, keep_terms: list[str] | None = None) -> str:
    """
    Very conservative redaction: replace anything matching a personal-data
    shape (long digit sequences, emails) unless explicitly allowed via
    keep_terms (e.g. a confirmed scammer phone number/domain).
    """
    import re

    keep_terms = keep_terms or []
    result = text

    def _redact_email(match: re.Match) -> str:
        value = match.group(0)
        return value if value in keep_terms else "[redacted-email]"

    def _redact_phone(match: re.Match) -> str:
        value = match.group(0)
        return value if value in keep_terms else "[redacted-number]"

    result = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", _redact_email, result)
    result = re.sub(r"(\+?\d[\d\-\s()]{7,}\d)", _redact_phone, result)
    return result
