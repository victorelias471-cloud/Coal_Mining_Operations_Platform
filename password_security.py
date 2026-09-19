import re


def analyze_password(password: str) -> dict:
    """
    Analyze password strength and return security requirements.
    """

    score = 0
    checks = {}

    # Length
    checks["minimum_length"] = len(password) >= 12
    if len(password) >= 12:
        score += 25

    # Uppercase
    checks["uppercase"] = bool(re.search(r"[A-Z]", password))
    if checks["uppercase"]:
        score += 15

    # Lowercase
    checks["lowercase"] = bool(re.search(r"[a-z]", password))
    if checks["lowercase"]:
        score += 15

    # Number
    checks["number"] = bool(re.search(r"\d", password))
    if checks["number"]:
        score += 15

    # Special character
    checks["special_character"] = bool(
        re.search(r"[^A-Za-z0-9]", password)
    )
    if checks["special_character"]:
        score += 15

    # Extra length bonus
    if len(password) >= 16:
        score += 15

    if score >= 85:
        strength = "Very Strong"
    elif score >= 70:
        strength = "Strong"
    elif score >= 50:
        strength = "Moderate"
    else:
        strength = "Weak"

    compliant = all(checks.values())

    return {
        "score": min(score, 100),
        "strength": strength,
        "policy_compliant": compliant,
        "checks": checks,
    }
