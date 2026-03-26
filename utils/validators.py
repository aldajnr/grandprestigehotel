# Input validators

def is_zetech_email(email: str) -> bool:
    # Username must end with @zetech.ac.ke (no Gmail)
    return bool(email) and email.strip().lower().endswith("@zetech.ac.ke")
