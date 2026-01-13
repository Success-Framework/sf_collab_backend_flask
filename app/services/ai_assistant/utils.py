from pypdf import PdfReader
from docx import Document
import os
import logging
import re

def extract_text(file_path: str) -> str:
    if file_path.lower().endswith(".pdf"):
        reader = PdfReader(file_path)
        texts = []

        for i, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                if text:
                    texts.append(text)
            except Exception as e:
                logging.warning(
                    f"Skipping page {i} due to PDF error: {e}"
                )

        return "\n".join(texts)

    if file_path.lower().endswith((".doc", ".docx")):
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    raise ValueError("Unsupported file type")


def chunk_text(text, max_chars=1200, overlap=200):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) <= max_chars:
            current += " " + sentence
        else:
            chunks.append(current.strip())
            current = current[-overlap:] + " " + sentence

    if current.strip():
        chunks.append(current.strip())

    return chunks