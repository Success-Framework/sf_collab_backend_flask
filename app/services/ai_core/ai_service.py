import requests
from flask import current_app

from .injection import detect_prompt_injection
from .output_filter import detect_sensitive_output
from .system_prompts import get_system_prompt
from .response_builder import build_refusal


class AIService:

    @staticmethod
    def preprocess_input(feature: str, user_input: str):
        if detect_prompt_injection(user_input):
            return build_refusal("Prompt injection attempt detected.")
        return None

    @staticmethod
    def postprocess_output(response_text: str):
        if detect_sensitive_output(response_text):
            return build_refusal("Sensitive output blocked.")
        return None

    @staticmethod
    def build_messages(feature: str, user_input: str, context: str = None):
        system_prompt = get_system_prompt(feature)

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        if context:
            messages.append({
                "role": "system",
                "content": f"Context:\n{context}"
            })

        messages.append({
            "role": "user",
            "content": user_input
        })

        return messages

    @staticmethod
    def call_model(messages, temperature=0.7, max_tokens=2048):

        HF_URL = current_app.config.get("HF_PROXY_URL")
        HF_API_KEY = current_app.config.get("HF_PROXY_KEY")

        headers = {
            "Authorization": f"Bearer {HF_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "advisor-model",  # matches HF config.yaml
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(
            f"{HF_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            raise Exception(f"HF Proxy Error: {response.text}")

        data = response.json()

        return data["choices"][0]["message"]["content"]

    @staticmethod
    def generate(feature: str, user_input: str, context: str = None,
                 temperature=0.7, max_tokens=2048):

        # Pre-guardrail
        guardrail_check = AIService.preprocess_input(feature, user_input)
        if guardrail_check:
            return guardrail_check

        messages = AIService.build_messages(feature, user_input, context)

        response_text = AIService.call_model(
            messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Post-guardrail
        post_guardrail = AIService.postprocess_output(response_text)
        if post_guardrail:
            return post_guardrail

        return {
            "response": response_text,
            "guardrail_triggered": False
        }