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
    """
    Lazily initialize Chroma client & collection.
    This ensures every Gunicorn worker loads from disk.
    """
    global _client, _collection

    if _collection is not None:
        return _collection

    _client = chromadb.Client(
        Settings(
            persist_directory=VECTOR_STORE_PATH,
            anonymized_telemetry=False
        )
    )

    _collection = _client.get_or_create_collection(
        name="ai_assistant_docs"
    )

    return _collection
