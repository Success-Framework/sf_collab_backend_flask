# app/services/ai_assistant/rag.py

from sentence_transformers import SentenceTransformer
from groq import Groq
from flask import current_app

from app.services.ai_assistant.vector_store import get_collection
from app.services.ai_assistant.prompts import ASSISTANT_SYSTEM_PROMPT
import re

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# SIMILARITY_THRESHOLD = 0.25
MAX_DISTANCE_THRESHOLD = 2.0
TOP_K = 5
FALLBACK = "Sorry, I don't know. Please ask something else."
FALLBACK2 = "Something is wrong."


def clean_llm_output(text: str) -> str:
    # Remove <think>...</think> blocks completely
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()
def ask_assistant(question: str) -> str:
    """
    Returns assistant answer or exactly 'I don't know.'
    """
    question = question.lower().strip()
    # 1. Embed query
    query_embedding = embedding_model.encode([question])[0].tolist()

    # 2. Vector search
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
        include=["documents", "distances"]
    )

    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents or not distances:
        return FALLBACK2



    # 3. Similarity gate
    best_distance = distances[0]
    if best_distance > MAX_DISTANCE_THRESHOLD:
        return FALLBACK2
    # 4. Build context
    context = "\n\n".join(documents)

    # 5. Call Groq
    groq_client = Groq(api_key=current_app.config.get("GROQ_API_KEY"))

    completion = groq_client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {"role": "system", "content": ASSISTANT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{question}"
            }
        ],
        temperature=0,
        max_tokens=512
    )

    answer = completion.choices[0].message.content.strip()

    if not answer:
        return "Sorry, I don't know."
    raw_answer = completion.choices[0].message.content or ""
    answer = clean_llm_output(raw_answer)

    return answer if answer else FALLBACK
