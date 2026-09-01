"""
Shared taxonomies.

These are intentionally plain Python (str, Enum) rather than native Postgres
ENUM types so that new values (e.g. a new scam_category or tactic) can be
added later via a simple migration instead of an `ALTER TYPE`. Every taxonomy
here is explicitly documented as extensible in the product spec.
"""
from enum import Enum


class InputType(str, Enum):
    TEXT = "text"
    URL = "url"
    IMAGE = "image"
    SCREENSHOT = "screenshot"
    AUDIO = "audio"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ScamCategory(str, Enum):
    PHISHING = "phishing"
    BANK_IMPERSONATION = "bank_impersonation"
    KYC_FRAUD = "kyc_fraud"
    PAYMENT_FRAUD = "payment_fraud"  # UPI / payment fraud
    GOVERNMENT_IMPERSONATION = "government_impersonation"
    COURIER_DELIVERY_SCAM = "courier_delivery_scam"
    JOB_SCAM = "job_scam"
    INVESTMENT_SCAM = "investment_scam"
    LOTTERY_PRIZE_SCAM = "lottery_prize_scam"
    ROMANCE_SCAM = "romance_scam"
    ACCOUNT_TAKEOVER = "account_takeover"
    TECH_SUPPORT_SCAM = "tech_support_scam"
    IDENTITY_THEFT = "identity_theft"
    CREDENTIAL_HARVESTING = "credential_harvesting"
    OTHER = "other"
    UNKNOWN = "unknown"


class TacticName(str, Enum):
    URGENCY = "urgency"
    FEAR = "fear"
    AUTHORITY_IMPERSONATION = "authority_impersonation"
    REWARD_GREED = "reward_greed"
    SCARCITY = "scarcity"
    THREAT = "threat"
    SOCIAL_PRESSURE = "social_pressure"
    TRUST_EXPLOITATION = "trust_exploitation"
    CREDENTIAL_HARVESTING = "credential_harvesting"
    FINANCIAL_PRESSURE = "financial_pressure"
    CURIOSITY = "curiosity"
    EMOTIONAL_MANIPULATION = "emotional_manipulation"


class IndicatorType(str, Enum):
    URL = "URL"
    DOMAIN = "DOMAIN"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    ORGANIZATION = "ORGANIZATION"
    PERSON = "PERSON"
    PAYMENT_ID = "PAYMENT_ID"
    ACCOUNT_REFERENCE = "ACCOUNT_REFERENCE"
    LOCATION = "LOCATION"
    PLATFORM = "PLATFORM"


class RequestedActionType(str, Enum):
    CLICK_URL = "click_url"
    PROVIDE_CREDENTIALS = "provide_credentials"
    PROVIDE_OTP = "provide_otp"
    TRANSFER_MONEY = "transfer_money"
    INSTALL_SOFTWARE = "install_software"
    CALL_NUMBER = "call_number"
    SHARE_PERSONAL_INFO = "share_personal_info"
    SCAN_QR_CODE = "scan_qr_code"
    DOWNLOAD_ATTACHMENT = "download_attachment"
    CONTACT_SCAMMER = "contact_scammer"
    OTHER = "other"


class EvidenceType(str, Enum):
    ORIGINAL_TEXT = "original_text"
    SCREENSHOT = "screenshot"
    IMAGE = "image"
    AUDIO = "audio"
    OCR_TEXT = "ocr_text"
    TRANSCRIPTION = "transcription"
    URL_ANALYSIS = "url_analysis"
    AI_ANALYSIS = "ai_analysis"
