import os
import uuid
from sentence_transformers import SentenceTransformer
from .vector_store import get_collection
from .utils import extract_text, chunk_text

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

UPLOAD_BASE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../uploads')
)

def ingest_document(file_path: str):
    filename = os.path.basename(file_path)
    collection = get_collection()

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