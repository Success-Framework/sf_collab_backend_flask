import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TARGET_CTA = {
    "clients": "Would you be open to a quick conversation?",
    "investors": "Would you be open to a short intro call?",
    "partners": "Would you be interested in exploring a partnership?",
    "employees": "Would you be interested in learning more?"
}

def generate_outreach_draft(campaign, user):
    prompt = f"""
Write a short, human outreach email.

Context:
- Sender: {user.first_name} {user.last_name}
- Target type: {campaign.target_type}
- Campaign description: {campaign.description}

Rules:
- Keep it short and natural
- No fake personalization
- No emojis
- Plain text
- Clear CTA
- Friendly but professional

Output format:
Subject:
<subject>

Body:
<body>
"""

    response = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    text = response.choices[0].message.content.strip()

    subject = ""
    body = ""

    if "Subject:" in text and "Body:" in text:
        subject = text.split("Subject:")[1].split("Body:")[0].strip()
        body = text.split("Body:")[1].strip()
    else:
        subject = "Quick introduction"
        body = text

    return subject, body
