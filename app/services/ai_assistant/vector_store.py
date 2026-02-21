# app/services/ai_assistant/vector_store.py

import os
import chromadb
from chromadb.config import Settings

VECTOR_STORE_PATH = os.getenv(
    "VECTOR_STORE_PATH",
    "/app/vector_store"   # shared directory inside container
)

os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

_client = None
_collection = None

def get_collection():
    global _client, _collection

    if _client is None:
        _client = chromadb.Client(
            Settings(
                persist_directory=VECTOR_DB_DIR,
                anonymized_telemetry=False
            )
        )

    if _collection is None:
        _collection = _client.get_or_create_collection(
            name="website_docs"
        )

    return _collection
