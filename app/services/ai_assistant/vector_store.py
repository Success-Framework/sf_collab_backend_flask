import os
import chromadb
from chromadb.config import Settings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
VECTOR_DB_DIR = os.path.join(BASE_DIR, 'vector_store')

os.makedirs(VECTOR_DB_DIR, exist_ok=True)

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