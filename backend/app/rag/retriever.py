import os
import json
from pathlib import Path

import faiss
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# Load environment variables
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in the .env file.")


# ============================================================
# Create Gemini client
# ============================================================

# Disable automatic retries.
# This allows quota/rate-limit errors to reach our application
# immediately instead of waiting through multiple retries.

http_options = types.HttpOptions(
    timeout=10000,
    retry_options=types.HttpRetryOptions(
        attempts=1
    )
)

client = genai.Client(
    api_key=api_key,
    http_options=http_options
)


# ============================================================
# Project paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

RAG_DIR = BASE_DIR / "data" / "rag"

INDEX_PATH = RAG_DIR / "knowledge.index"
CHUNKS_PATH = RAG_DIR / "chunks.json"


# ============================================================
# Load RAG data
# ============================================================

def load_rag_data():
    """
    Load the FAISS index and stored knowledge chunks.
    """

    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            f"FAISS index not found: {INDEX_PATH}"
        )

    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"Chunks file not found: {CHUNKS_PATH}"
        )

    index = faiss.read_index(str(INDEX_PATH))

    with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    return index, chunks


# ============================================================
# Generate query embedding
# ============================================================

def generate_query_embedding(query: str):
    """
    Generate a Gemini embedding for the user's question.
    """

    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=query
    )

    embedding = np.array(
        [response.embeddings[0].values],
        dtype="float32"
    )

    return embedding


# ============================================================
# Search knowledge base
# ============================================================

def search_knowledge(query: str, top_k: int = 3):
    """
    Search the FAISS knowledge base for relevant chunks.
    """

    index, chunks = load_rag_data()

    query_embedding = generate_query_embedding(query)

    # Normalize the query vector because the FAISS index
    # uses inner product as cosine similarity.
    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, index_position in zip(
        scores[0],
        indices[0]
    ):

        if index_position == -1:
            continue

        result = {
            "score": float(score),
            "source": chunks[index_position]["source"],
            "text": chunks[index_position]["text"]
        }

        results.append(result)

    return results


# ============================================================
# Local test
# ============================================================

def main():

    query = "What products do you offer?"

    print("\nSearching knowledge base...")
    print(f"Question: {query}\n")

    results = search_knowledge(
        query,
        top_k=3
    )

    print("Retrieved results:\n")

    for i, result in enumerate(
        results,
        start=1
    ):

        print(f"Result {i}")
        print(f"Source: {result['source']}")
        print(
            f"Similarity score: "
            f"{result['score']:.4f}"
        )
        print(
            f"Content: "
            f"{result['text']}"
        )
        print("-" * 60)


if __name__ == "__main__":
    main()