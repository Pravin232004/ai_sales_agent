import os

from dotenv import load_dotenv
from google import genai

from app.rag.retriever import search_knowledge


# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in the .env file.")


# Create Gemini client
client = genai.Client(api_key=api_key)


def answer_with_rag(question: str) -> str:
    """
    Answer a user question using retrieved knowledge
    from the FAISS vector database.
    """

    # Step 1: Retrieve relevant knowledge
    results = search_knowledge(question, top_k=3)

    if not results:
        return "I could not find relevant information in the knowledge base."

    # Step 2: Build context from retrieved chunks
    context_parts = []

    for result in results:
        context_parts.append(
            f"Source: {result['source']}\n"
            f"{result['text']}"
        )

    context = "\n\n---\n\n".join(context_parts)

    # Step 3: Build the prompt
    prompt = f"""
You are an AI sales assistant.

Answer the customer's question using ONLY the
information provided in the knowledge base below.

If the answer cannot be found in the knowledge base,
say that you do not have enough information.

Knowledge base:
----------------
{context}
----------------

Customer question:
{question}

Give a clear and concise answer.
"""

    # Step 4: Ask Gemini to generate the answer
    interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=prompt,
    )

    return interaction.output_text


def main():

    question = "What products do you offer?"

    print("\nCustomer question:")
    print(question)

    print("\nGenerating RAG answer...\n")

    answer = answer_with_rag(question)

    print("AI Sales Agent:")
    print(answer)


if __name__ == "__main__":
    main()