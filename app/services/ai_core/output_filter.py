BLOCKED_OUTPUT_PATTERNS = [
    "system prompt:",
    "internal instruction:",
    "api_key",
    "sk-",
    "BEGIN_PRIVATE",
    "END_PRIVATE"
]

def detect_sensitive_output(text: str) -> bool:
    if not text:
        return False

    text_lower = text.lower()

    for pattern in BLOCKED_OUTPUT_PATTERNS:
        if pattern in text_lower:
            return True

    return False