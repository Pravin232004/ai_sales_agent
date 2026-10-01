import os
import json
from pathlib import Path

import faiss
import numpy as np
from dotenv import load_dotenv
from google import genai


# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in the .env file.")


# Create Gemini client
client = genai.Client(api_key=api_key)


# Project paths
BASE_DIR = Path(__file__).resolve().parents[3]

KNOWLEDGE_DIR = BASE_DIR / "data" / "knowledge"
RAG_DIR = BASE_DIR / "data" / "rag"

INDEX_PATH = RAG_DIR / "knowledge.index"
CHUNKS_PATH = RAG_DIR / "chunks.json"


def load_documents():
    """
    Load all text files from the knowledge directory.
    """

    documents = []

    for file_path in KNOWLEDGE_DIR.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        documents.append({
            "source": file_path.name,
            "text": text
        })

    return documents


def chunk_text(text, chunk_size=500, overlap=100):
    """
    Split text into overlapping chunks.
    """

    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def create_chunks(documents):
    """
    Create chunks while preserving the source filename.
    """

    chunks = []

    for document in documents:

        text_chunks = chunk_text(document["text"])

        for chunk in text_chunks:
            chunks.append({
                "source": document["source"],
                "text": chunk
            })

    return chunks


def generate_embeddings(chunks):
    """
    Generate one Gemini embedding for each chunk.
    """

    embeddings = []

    for i, chunk in enumerate(chunks, start=1):

        print(f"Generating embedding {i}/{len(chunks)}...")

        response = client.models.embed_content(
            model="gemini-embedding-2",
            contents=chunk["text"]
        )

        embedding = response.embeddings[0].values

        embeddings.append(embedding)

    return np.array(embeddings, dtype="float32")


def build_faiss_index(embeddings):
    """
    Create a FAISS index using cosine similarity.

    Cosine similarity can be implemented using
    normalized vectors with inner product.
    """

    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    return index


def save_rag_data(index, chunks):
    """
    Save FAISS index and chunk metadata.
    """

    RAG_DIR.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(INDEX_PATH))

    with open(CHUNKS_PATH, "w", encoding="utf-8") as file:
        json.dump(chunks, file, indent=2, ensure_ascii=False)


def main():

    print("Loading knowledge documents...")

    documents = load_documents()

    print(f"Loaded {len(documents)} documents.")

    if not documents:
        raise ValueError("No knowledge files found.")

    print("Creating text chunks...")

    chunks = create_chunks(documents)

    print(f"Created {len(chunks)} chunks.")

    print("Generating embeddings...")

    embeddings = generate_embeddings(chunks)

    print(f"Embedding shape: {embeddings.shape}")

    print("Building FAISS index...")

    index = build_faiss_index(embeddings)

    print("Saving RAG data...")

    save_rag_data(index, chunks)

    print("\nRAG knowledge base created successfully!")

    print(f"FAISS index: {INDEX_PATH}")
    print(f"Chunks file: {CHUNKS_PATH}")


if __name__ == "__main__":
    main()