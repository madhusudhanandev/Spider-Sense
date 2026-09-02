"""
Demo data seed script.

Runs a set of realistic (but synthetic -- not from real victims) scam
messages through the REAL analysis pipeline and REAL community-sharing +
campaign-clustering flow, exactly as if a user had submitted them one at a
time through the app. Nothing about the detection or clustering logic is
faked or shortcut here -- this just gives the demo enough data volume to
actually show what the system does, instead of 2-3 test messages.

Run from backend/ with the venv active:
    python scripts/seed_demo_data.py

Safe to re-run: each run creates NEW incidents (no dedup), so if you want a
clean slate, drop and recreate the database first.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal  # noqa: E402
from app.models.enums import InputType  # noqa: E402
from app.schemas.community import CommunityReportRequest  # noqa: E402
from app.services.pipeline import run_pipeline  # noqa: E402
from app.api.routes.incidents import create_community_report  # noqa: E402


# Each storyline is a list of (text, platform, language_hint) tuples, in the
# order they'd realistically appear -- this order is what creates the
# platform/language "mutation" events campaign clustering will detect.
STORYLINES: list[list[tuple[str, str, str]]] = [
    # --- 1. HDFC KYC fraud: SMS -> WhatsApp -> Email -> Tamil WhatsApp ---
    [
        ("Your HDFC Bank account KYC has expired. Verify now to avoid suspension: http://hdfc-kyc-secure.example/verify", "SMS", "en"),
        ("HDFC KYC Alert: Your account access will be restricted. Click to re-verify: http://hdfc-kyc-secure.example/reverify", "WhatsApp", "en"),
        ("Final notice: HDFC KYC re-verification required immediately to avoid account freeze: http://hdfc-kyc-secure.example/final-notice", "Email", "en"),
        ("\u0b89\u0b99\u0bcd\u0b95\u0bb3\u0bcd HDFC \u0b95\u0ba3\u0b95\u0bcd\u0b95\u0bc1 KYC \u0bae\u0bc1\u0b9f\u0bbf\u0ba8\u0bcd\u0ba4\u0bc1\u0bb5\u0bbf\u0b9f\u0bcd\u0b9f\u0ba4\u0bc1. \u0b87\u0baa\u0bcd\u0baa\u0bcb\u0ba4\u0bc1 \u0b9a\u0bb0\u0bbf\u0baa\u0bbe\u0bb0\u0bcd\u0b95\u0bcd\u0b95\u0bb5\u0bc1\u0bae\u0bcd: http://hdfc-kyc-secure.example/ta-verify", "WhatsApp", "ta"),
    ],
    # --- 2. Amazon anniversary lottery: SMS -> WhatsApp ---
    [
        ("Congratulations! You have WON Rs. 25,00,000 in the Amazon Anniversary Lottery. Share your bank details and pay a small processing fee of Rs. 500 to claim your prize now.", "SMS", "en"),
        ("AMAZON LUCKY WINNER: Your prize of Rs 25,00,000 is still pending. Reply with your account number and IFSC code to claim before it expires today.", "WhatsApp", "en"),
    ],
    # --- 3. Courier/customs fee scam: Email -> WhatsApp -> SMS ---
    [
        ("Your package could not be delivered due to unpaid customs duty of $2.99. Pay now at http://courier-track-pay.example to avoid return to sender within 24 hours.", "Email", "en"),
        ("DELIVERY ALERT: Your parcel is on hold at customs. Pay the pending fee immediately to release it: http://courier-track-pay.example/release", "WhatsApp", "en"),
        ("Final reminder: your package will be destroyed if customs fee is not paid today. Pay here: http://courier-track-pay.example/final", "SMS", "en"),
    ],
    # --- 4. Work-from-home job scam: LinkedIn -> WhatsApp ---
    [
        ("We reviewed your profile and would like to offer you a Work From Home job paying $500/day. No experience needed. To proceed, install our task app and pay a $50 refundable registration fee.", "LinkedIn", "en"),
        ("Hi, following up on the work from home job offer -- spots are limited, please install the app and complete registration today to secure your position.", "WhatsApp", "en"),
    ],
    # --- 5. Government/tax impersonation: SMS -> phone call transcript ---
    [
        ("IRS Notice: You owe $1,289 in unpaid taxes. Failure to respond within 24 hours will result in legal action. Call +1-800-555-0199 immediately to resolve.", "SMS", "en"),
        ("This is an automated message from the tax department. Your case number requires immediate verification of your social security number to avoid arrest warrant issuance. Press 1 to speak to an officer now.", "Voice", "en"),
    ],
    # --- 6. Tech support scam: Email -> Voice ---
    [
        ("URGENT SECURITY ALERT: Your computer has been infected with a virus. Call Microsoft Support immediately at +1-800-555-0142 to prevent data loss.", "Email", "en"),
        ("Hello, this is Microsoft technical support calling about the virus alert on your computer. Please allow remote access so we can fix this for you right away.", "Voice", "en"),
    ],
    # --- 7. Romance scam: Instagram -> WhatsApp ---
    [
        ("Hi dear, I saw your profile and felt an instant connection. I am currently deployed overseas but would love to get to know you better. Can we chat on WhatsApp?", "Instagram", "en"),
        ("My love, I need your help. I'm stuck at customs and need $800 to release my belongings. I will pay you back as soon as I'm home, I promise.", "WhatsApp", "en"),
    ],
    # --- 8. Crypto/investment scam: Telegram -> WhatsApp ---
    [
        ("Join our exclusive crypto trading group! Our AI trading bot guarantees 30% weekly returns. Limited spots, deposit now to start earning.", "Telegram", "en"),
        ("Your investment account is showing amazing returns! Deposit a bit more now to unlock withdrawal and double your profits before the offer ends.", "WhatsApp", "en"),
    ],
]


async def seed() -> list[str]:
    db = SessionLocal()
    incident_ids: list[str] = []

    total_messages = sum(len(s) for s in STORYLINES)
    done = 0

    try:
        for storyline in STORYLINES:
            for text, platform, language_hint in storyline:
                result = await run_pipeline(
                    db,
                    input_type=InputType.TEXT,
                    text=text,
                    platform=platform,
                    language_hint=language_hint,
                )
                await create_community_report(
                    incident_id=result.incident_id,
                    payload=CommunityReportRequest(consent=True),
                    db=db,
                )
                incident_ids.append(str(result.incident_id))
                done += 1
                print(f"[{done}/{total_messages}] {platform:10s} -> {result.scam_category:25s} risk={result.risk_score}")
    finally:
        db.close()

    return incident_ids


if __name__ == "__main__":
    ids = asyncio.run(seed())
    print(f"\nSeeded {len(ids)} incidents across {len(STORYLINES)} storylines.")
    print("Next: run scripts/backdate_demo_timestamps.py to spread these out over the past two weeks.")