SUSPICIOUS_PATTERNS = [
    "ignore previous instructions",
    "reveal system prompt",
    "show hidden instructions",
    "print full document",
    "dump database",
    "act as system",
    "bypass safety",
    "disable guardrails",
    "developer mode",
    "pretend you are"
]

def detect_prompt_injection(text: str) -> bool:
    if not text:
        return False

    text_lower = text.lower()

    for pattern in SUSPICIOUS_PATTERNS:
        if pattern in text_lower:
            return True

    return False