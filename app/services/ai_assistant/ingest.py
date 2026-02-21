import os
import uuid
from sentence_transformers import SentenceTransformer
from .vector_store import get_collection
from .utils import extract_text, chunk_text

import os
from sentence_transformers import SentenceTransformer

_embedding_model = None

def get_embedding_model():
    """
    Lazy-load the embedding model so Flask can import the app
    (and run migrations) without allocating huge memory.
    """
    global _embedding_model
    if _embedding_model is None:
        model_name = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
        _embedding_model = SentenceTransformer(model_name)
    return _embedding_model


UPLOAD_BASE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../uploads')
)

def ingest_document(file_path: str):
    filename = os.path.basename(file_path)
    collection = get_collection()
    print("COUNT:", collection.count())

    # 🔥 Remove existing chunks of same file
    collection.delete(where={"filename": filename})
    text = extract_text(file_path)
    chunks = chunk_text(text)

    embeddings = embedding_model.encode(chunks).tolist()

    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [{"filename": filename} for _ in chunks]

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )


    return {
        "filename": filename,
        "chunks_added": len(chunks)
    }