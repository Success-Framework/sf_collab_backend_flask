def build_refusal(message: str):
    return {
        "response": f"⚠️ I cannot assist with that request.\n\nReason: {message}",
        "guardrail_triggered": True
    }