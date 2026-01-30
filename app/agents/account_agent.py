import re
from datetime import datetime
from app.services.account_service import (
    get_account,
    update_phone,
    update_dob
)

PHONE_REGEX = r"\+?\d{8,15}"
DOB_REGEX = r"\b\d{4}-\d{2}-\d{2}\b"  # YYYY-MM-DD


def extract_phone_number(message: str):
    match = re.search(PHONE_REGEX, message)
    return match.group(0) if match else None


def extract_dob(message: str):
    match = re.search(DOB_REGEX, message)
    return match.group(0) if match else None


def is_valid_dob(dob: str) -> bool:
    try:
        parsed = datetime.strptime(dob, "%Y-%m-%d")
        return parsed.date() < datetime.utcnow().date()
    except ValueError:
        return False


def generate_account_response(customer_id: str, message: str) -> str:
    message_lower = message.lower()

    # 🚫 Block forbidden updates
    forbidden_keywords = ["email", "name", "status", "username"]
    if any(word in message_lower for word in forbidden_keywords):
        return (
            "For security reasons, only phone number and date of birth updates "
            "are allowed via chat.\n\n"
            "Please contact support for other account changes."
        )

    # 🎂 DOB update — FIRST (important)
    new_dob = extract_dob(message)
    if new_dob:
        if not is_valid_dob(new_dob):
            return "Please provide a valid past date of birth in YYYY-MM-DD format."

        update_dob(customer_id, new_dob)
        return f"✅ Your date of birth has been updated to {new_dob}."

    if "dob" in message_lower or "date of birth" in message_lower:
        return (
            "Please provide your date of birth in YYYY-MM-DD format.\n"
            "Example: 1995-08-21"
        )

    # 📞 Phone update — SECOND
    new_phone = extract_phone_number(message)
    if new_phone:
        update_phone(customer_id, new_phone)
        return f"✅ Your phone number has been updated to {new_phone}."

    if "phone" in message_lower:
        return (
            "Please provide the new phone number.\n"
            "Example: +1234567890"
        )

    # 🔁 Fallback
    return (
        "I can help you update the following account details:\n"
        "- Phone number\n"
        "- Date of birth (DOB)\n\n"
        "Please tell me what you’d like to update."
    )
